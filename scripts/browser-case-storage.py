#!/usr/bin/env python3
"""Observe case storage failures in the actual HTTP application and downloaded JSON.

Faults are injected at the browser Storage boundary, before application startup.
The DOM, inputs, navigation, reload, downloads and personal bytes are real. No
application state is replaced by a mock and no sandbox bypass flags are used.
"""
import argparse
from datetime import datetime, timezone
import importlib.metadata
import json
from pathlib import Path
import platform
import re
import subprocess
import sys
import traceback
from urllib.parse import urljoin, urlsplit

from playwright.sync_api import sync_playwright, expect

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--url', required=True)
parser.add_argument('--demo-path', default='demo.html')
parser.add_argument('--browser', choices=['chromium', 'firefox', 'webkit'], default='chromium')
parser.add_argument('--executable')
parser.add_argument('--output', type=Path, default=Path('/tmp/asp24-case-storage-results'))
args = parser.parse_args()
args.output.mkdir(parents=True, exist_ok=True)
root = Path(__file__).resolve().parents[1]
base = args.url.rstrip('/') + '/'
demo = urljoin(base, args.demo_path)
origin = urlsplit(base).netloc
registry = json.loads((root / 'publication.json').read_text())
case = next(c for c in registry['cases'] if c['caseId'] == 'model-document')
case_url = demo + f'?case={case["caseId"]}&v={case["caseVersion"]}' + case['route']
report_url = base + f'reports/{case["reportId"]}_Review.html#{case["sectionId"]}'
personal_key = 'perspective-demo-v1'
case_key = f'asp24-nggroup-case:{case["caseId"]}:v{case["caseVersion"]}'
seed_question = case['seed']['drafts']['u02']['question']
draft_a = 'Синтетичне питання: порт A/B, виконання D1; кількість 2.\nЗберегти «точний текст», 0 і 24 В.'
draft_b = draft_a + '\nДодано після відмови запису — не втратити № 7.'
fixture = json.loads(subprocess.check_output([
    'node', '--input-type=module', '-e', """
import {initialState} from './logic.js';
import {normalizeScience,createProject} from './science.js';
const s=initialState();s.cart={c02:4};s.favorites=['o01'];
s.compareByGroup.optics=['o01','o03'];s.view.pairs.optics=['o03','o01'];
s.drafts.u04={purpose:'Тест',quantity:'3',question:'Особиста синтетична чернетка — не змінювати'};
s.listName='Особистий синтетичний список';s.note='Не змінювати під час прикладу';
s.science=normalizeScience();
createProject(s.science,{name:'Мій синтетичний проєкт',candidates:['c02','u04']},undefined,'2026-10-09T00:00:00.000Z');
console.log(JSON.stringify(s));
"""], cwd=root, text=True))
results = {
    'started_at_utc': datetime.now(timezone.utc).isoformat(),
    'commit': subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=root, text=True).strip(),
    'working_tree_dirty': bool(subprocess.check_output(['git', 'status', '--porcelain', '--untracked-files=no'], cwd=root, text=True).strip()),
    'browser': args.browser, 'playwright': importlib.metadata.version('playwright'),
    'environment': {'platform': platform.platform(), 'python': platform.python_version()},
    'command': ['python', *sys.argv], 'url': base, 'checks': [],
    'not_run': ['stable Safari', 'physical iPhone', 'native zoom', 'VoiceOver'],
}


def open_case(page, faults=None):
    """Seed personal data outside the app, then instrument only case boundaries."""
    page.goto(report_url, wait_until='networkidle')
    original = page.evaluate('([key,state])=>{const value=JSON.stringify(state);localStorage.setItem(key,value);return value}', [personal_key, fixture])
    config = json.dumps({'faults': faults or {}, 'caseKey': case_key, 'personalKey': personal_key}, ensure_ascii=False)
    page.add_init_script(script='''(() => {
      const config = CONFIG;
      const local = window.localStorage, session = window.sessionStorage;
      const native = {get:Storage.prototype.getItem,set:Storage.prototype.setItem,remove:Storage.prototype.removeItem};
      const probe = window.__caseStorageProbe = {
        faults: JSON.parse(native.get.call(session,'asp24-nggroup-test-faults') || JSON.stringify(config.faults)), personalAccesses: [],
        faultsForReload: next => native.set.call(session,'asp24-nggroup-test-faults',JSON.stringify(next)),
        personalBytes: () => native.get.call(local,config.personalKey),
        caseBytes: () => native.get.call(session,config.caseKey),
      };
      for (const [method,kind] of [['getItem','get'],['setItem','set'],['removeItem','remove']]) {
        Storage.prototype[method] = function(key,...rest) {
          if(this===local && key===config.personalKey)probe.personalAccesses.push(method);
          if(this===session && key===config.caseKey && probe.faults[kind]) {
            throw new DOMException('Intentional case '+kind+' failure',kind==='set'?'QuotaExceededError':'SecurityError');
          }
          return native[kind].call(this,key,...rest);
        };
      }
      if(probe.faults.unavailable)Object.defineProperty(window,'sessionStorage',{
        configurable:true,get(){throw new DOMException('Intentional unavailable sessionStorage','SecurityError');}
      });
    })();'''.replace('CONFIG', config))
    response = page.goto(case_url, wait_until='networkidle')
    assert response.status == 200
    expect(page.locator('.document-page')).to_contain_text('DEMO-U02')
    expect(page.locator('#case-export')).to_be_visible()
    assert_personal(page, original)
    return original


def assert_personal(page, original):
    probe = page.evaluate('({bytes:window.__caseStorageProbe.personalBytes(),accesses:window.__caseStorageProbe.personalAccesses})')
    assert probe['bytes'] == original, 'Case operation mutated personal projects/cart/candidates/drafts'
    assert probe['accesses'] == [], 'Case application accessed the personal localStorage key: ' + str(probe['accesses'])


def backing(page):
    raw = page.evaluate('window.__caseStorageProbe.caseBytes()')
    return json.loads(raw) if raw else None


def consult(page, text=None):
    page.locator('[data-action=consult][data-id=u02]').click()
    field = page.locator('#consult-form [name=question]')
    expect(field).to_be_visible()
    if text is not None:
        field.fill(text)
        expect(field).to_have_value(text)
    return field


def close_consult(page):
    page.locator('#modal [data-action=close]').click()
    expect(page.locator('#modal')).not_to_be_visible()


def warning(page, kind):
    status = page.locator('#case-storage-status')
    expect(status).to_be_visible()
    expect(status).to_have_attribute('role', 'status')
    expect(status).to_have_attribute('aria-live', 'polite')
    expect(status).to_have_attribute('data-storage-kind', kind)
    expect(status).to_contain_text(re.compile('перезавантаж', re.I))
    expect(status).to_contain_text(re.compile('експорт', re.I))
    for label in page.locator('[data-save-status]').all():
        # Closed <dialog> content remains in DOM but is hidden from users and AT.
        # Its label describes the last draft write, before the later reset action.
        if label.is_visible():
            expect(label).to_contain_text('Лише в пам’яті')
            message = label.inner_text()
            assert not re.search(r'(?:^|\s)(?:збережено|зберігається|зберігаються)\s+(?:в|у)\s+', message, re.I), message


def export_case(page, expected, filename):
    with page.expect_download() as download_info:
        page.locator('#case-export').click()
    download = download_info.value
    assert download.failure() is None
    path = args.output / filename
    download.save_as(path)
    payload = json.loads(path.read_text())
    assert payload['format'] == 'asp24-nggroup-case-state'
    assert payload['exportVersion'] == 1
    assert payload['caseId'] == case['caseId'] and payload['caseVersion'] == case['caseVersion']
    assert payload['stateSchemaVersion'] == 4 and payload['state']['version'] == 4
    assert payload['state']['drafts']['u02']['question'] == expected
    assert payload['state']['drafts'].get('u04') != fixture['drafts']['u04']
    assert payload['state']['cart'] != fixture['cart']
    # Validate the bytes actually downloaded, using the public export validator.
    validated = subprocess.check_output([
        'node', '--input-type=module', '-e',
        "import {validateCaseExport} from './case-context.js';const chunks=[];for await(const c of process.stdin)chunks.push(c);if(validateCaseExport(JSON.parse(Buffer.concat(chunks).toString())))process.exit(1);console.log('VALID');",
    ], input=path.read_text(), cwd=root, text=True)
    assert validated.strip() == 'VALID'
    return payload


def persist_history(page):
    original = open_case(page)
    consult(page, draft_a)
    expect(page.locator('#consult-form [data-save-status]')).to_contain_text('Збережено')
    assert backing(page)['drafts']['u02']['question'] == draft_a
    close_consult(page)
    export_case(page, draft_a, 'persisted-export.json')
    page.reload(wait_until='networkidle')
    expect(consult(page)).to_have_value(draft_a)
    close_consult(page)
    page.locator('.case-banner').get_by_role('link', name='Повернутися до розділу огляду', exact=True).click()
    page.wait_for_load_state('networkidle')
    assert page.url == report_url
    assert_personal(page, original)
    page.go_back(wait_until='networkidle')
    expect(consult(page)).to_have_value(draft_a)
    close_consult(page)
    page.go_forward(wait_until='networkidle')
    assert page.url == report_url
    assert_personal(page, original)
    page.goto(case_url, wait_until='networkidle')
    expect(consult(page)).to_have_value(draft_a)
    close_consult(page)
    assert_personal(page, original)


def write_failure(page):
    original = open_case(page, {'set': True})
    consult(page, draft_a)
    warning(page, 'write-error')
    page.locator('#consult-form [name=question]').fill(draft_b)
    warning(page, 'write-error')
    close_consult(page)
    expect(consult(page)).to_have_value(draft_b)
    close_consult(page)
    export_case(page, draft_b, 'quota-export.json')
    assert backing(page) is None, 'Failed writes unexpectedly persisted data'
    assert_personal(page, original)
    page.reload(wait_until='networkidle')
    expect(consult(page)).to_have_value(seed_question)
    warning(page, 'write-error')
    close_consult(page)
    assert_personal(page, original)


def unavailable_storage(page):
    original = open_case(page, {'unavailable': True})
    warning(page, 'memory-only')
    consult(page, draft_b)
    warning(page, 'memory-only')
    close_consult(page)
    export_case(page, draft_b, 'unavailable-export.json')
    assert_personal(page, original)
    page.reload(wait_until='networkidle')
    warning(page, 'memory-only')
    expect(consult(page)).to_have_value(seed_question)
    close_consult(page)
    assert_personal(page, original)


def read_failure(page):
    original = open_case(page)
    consult(page, draft_a)
    close_consult(page)
    # One init script owns ordering; the next navigation enables the read fault.
    page.evaluate('window.__caseStorageProbe.faultsForReload({get:true})')
    page.reload(wait_until='networkidle')
    warning(page, 'read-error')
    previous = backing(page)
    assert previous['drafts']['u02']['question'] == draft_a
    consult(page, draft_b)
    warning(page, 'read-error')
    close_consult(page)
    export_case(page, draft_b, 'read-failure-export.json')
    assert backing(page) == previous, 'Unreadable existing case bytes were overwritten'
    assert_personal(page, original)
    page.reload(wait_until='networkidle')
    warning(page, 'read-error')
    assert backing(page) == previous
    assert_personal(page, original)


def clear_failure(page):
    original = open_case(page, {'remove': True})
    consult(page, draft_b)
    close_consult(page)
    before = backing(page)
    page.evaluate("window.__sameCaseDocument='no-reload-on-clear-failure'")
    page.locator('.case-banner').get_by_role('button', name='Почати приклад спочатку', exact=True).click()
    warning(page, 'clear-error')
    expect(page.locator('#case-reset-status')).to_be_visible()
    expect(page.locator('#case-reset-status')).to_have_attribute('role', 'status')
    expect(page.locator('#case-reset-status')).to_contain_text('Приклад не скинуто')
    assert page.evaluate('window.__sameCaseDocument') == 'no-reload-on-clear-failure'
    assert backing(page) == before
    export_case(page, draft_b, 'clear-failure-export.json')
    assert_personal(page, original)
    # A subsequent successful reset really reloads and restores the declared seed.
    page.evaluate('window.__caseStorageProbe.faults.remove=false')
    with page.expect_navigation(wait_until='networkidle'):
        page.locator('.case-banner').get_by_role('button', name='Почати приклад спочатку', exact=True).click()
    assert page.evaluate("typeof window.__sameCaseDocument") == 'undefined'
    expect(consult(page)).to_have_value(seed_question)
    close_consult(page)
    assert_personal(page, original)


def late_failure_and_same_document_history(page):
    original = open_case(page)
    consult(page, draft_a)
    previous = backing(page)['drafts']['u02']['question']
    page.evaluate('window.__caseStorageProbe.faults.set=true')
    page.locator('#consult-form [name=question]').fill(draft_b)
    warning(page, 'write-error')
    close_consult(page)
    page.locator('a.back[href="#/ng/product/u02"]').click()
    expect(page.locator('h1')).to_have_text('VOLTYN N36')
    page.go_back()
    expect(page.locator('.document-page')).to_contain_text('DEMO-U02')
    expect(consult(page)).to_have_value(draft_b)
    warning(page, 'write-error')
    close_consult(page)
    page.go_forward()
    expect(page.locator('h1')).to_have_text('VOLTYN N36')
    export_case(page, draft_b, 'late-failure-history-export.json')
    assert backing(page)['drafts']['u02']['question'] == previous
    assert_personal(page, original)


checks = [
    ('successful-write-exact-export-reload-reinitialization-back-forward-personal-isolation', persist_history),
    ('quota-error-further-draft-edits-export-memory-reload-warning-no-false-success', write_failure),
    ('unavailable-session-storage-memory-export-reload-visible-accessible-warning', unavailable_storage),
    ('getItem-exception-protects-unreadable-bytes-export-reinitialization', read_failure),
    ('removeItem-exception-no-reload-keeps-current-export-retry-reset', clear_failure),
    ('late-write-failure-preserves-latest-draft-through-hash-back-forward', late_failure_and_same_document_history),
]

with sync_playwright() as playwright:
    try:
        options = {'chromium_sandbox': True} if args.browser == 'chromium' else {}
        if args.executable:
            options['executable_path'] = args.executable
        browser = getattr(playwright, args.browser).launch(timeout=30000, **options)
    except Exception as error:
        results.update(status='BLOCKED', launch_error=str(error))
    else:
        results['browser_version'] = browser.version
        for name, check in checks:
            context = browser.new_context(viewport={'width':390, 'height':844}, accept_downloads=True)
            context.set_default_timeout(12000)
            context.tracing.start(screenshots=True, snapshots=True, sources=True)
            errors = []
            def local_only(route):
                if urlsplit(route.request.url).netloc == origin:
                    route.continue_()
                else:
                    errors.append('Unexpected outbound request: ' + route.request.url)
                    route.abort()
            context.route('**/*', local_only)
            page = context.new_page()
            page.on('pageerror', lambda error: errors.append(str(error)))
            try:
                check(page)
                assert not errors, errors
            except Exception as error:
                try:
                    page.screenshot(path=str(args.output / (name + '.png')), full_page=True)
                except Exception:
                    pass
                context.tracing.stop(path=str(args.output / (name + '.zip')))
                results['checks'].append({'name':name, 'status':'FAIL', 'error':str(error), 'traceback':traceback.format_exc(), 'console_errors':errors})
                print('FAIL', name, str(error), flush=True)
            else:
                context.tracing.stop()
                results['checks'].append({'name':name, 'status':'PASS'})
                print('PASS', name, flush=True)
            finally:
                context.close()
        browser.close()
        results['status'] = 'FAIL' if any(c['status'] == 'FAIL' for c in results['checks']) else 'PASS'

results['completed_at_utc'] = datetime.now(timezone.utc).isoformat()
(args.output / 'results.json').write_text(json.dumps(results, ensure_ascii=False, indent=2) + '\n')
print(results['status'], args.output / 'results.json', flush=True)
raise SystemExit(0 if results['status'] == 'PASS' else 2 if results['status'] == 'BLOCKED' else 1)
