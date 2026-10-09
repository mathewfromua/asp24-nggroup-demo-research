#!/usr/bin/env python3
"""Focused P2 HTTP checks: pair focus, sticky context and readable compact cases."""
import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
import subprocess
import sys
import traceback
from urllib.parse import urlsplit
from playwright.sync_api import sync_playwright, expect

p = argparse.ArgumentParser(description=__doc__)
p.add_argument('--url', required=True)
p.add_argument('--browser', choices=['chromium', 'firefox', 'webkit'], default='chromium')
p.add_argument('--executable')
p.add_argument('--output', type=Path, required=True)
p.add_argument('--check', help='Run one named check during a focused local repair; omitted by the release gate')
a = p.parse_args(); a.output.mkdir(parents=True, exist_ok=True)
root = Path(__file__).resolve().parents[1]
base = a.url.rstrip('/') + '/'
case_key = 'asp24-nggroup-case:six-candidates:v1'
personal_key = 'perspective-demo-v1'
results = {'schema': 1, 'commit': subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=root, text=True).strip(),
           'working_tree_dirty': bool(subprocess.check_output(['git', 'status', '--porcelain'], cwd=root, text=True).strip()),
           'browser': a.browser, 'url': base, 'command': [sys.executable, *sys.argv], 'checks': [],
           'started_at_utc': datetime.now(timezone.utc).isoformat(),
           'not_run': ['native Safari', 'physical iPhone', 'VoiceOver', 'native browser zoom']}


def enter(page):
    page.goto(base + 'cases/six-candidates/v1/', wait_until='networkidle')
    page.get_by_role('link', name='Відкрити приклад', exact=True).click()
    page.get_by_role('link', name='Новий робочий простір →', exact=True).click()
    expect(page.get_by_test_id('comparison-workbench')).to_be_visible()
    page.evaluate('() => document.fonts.ready')


def state(page):
    return page.evaluate('(key)=>JSON.parse(sessionStorage.getItem(key))', case_key)


def selection(page):
    current = state(page)
    return {key: current[key] for key in ['compareByGroup', 'cart', 'drafts']} | {'pair': current['view']['pairs']}


def no_overflow(page):
    size = page.evaluate('({width:innerWidth,scroll:document.documentElement.scrollWidth})')
    assert size['scroll'] <= size['width'] + 1, size


def compact_readability(page):
    observations = []
    for width, height in [(1440, 900), (320, 844), (390, 844), (430, 844)]:
        page.set_viewport_size({'width': width, 'height': height})
        page.goto(base, wait_until='networkidle')
        page.evaluate('(key)=>sessionStorage.removeItem(key)', case_key)
        enter(page)
        metric = page.evaluate('''() => {
          const table=document.querySelector(innerWidth>700?'.wb-full':'.wb-pair');
          const box=e=>{const r=e.getBoundingClientRect();return {top:r.top,bottom:r.bottom,left:r.left,right:r.right};};
          const row=table.querySelector('tbody tr[data-row]');
          const helpers=[...document.querySelectorAll('.wb-heading-side,.wb-count small,.wb-parameter-heading span,.wb-sku,.wb-pair-marker,.wb-row-note,.wb-offers td>span,[data-testid=wb-undo]')].filter(e=>e.getClientRects().length);
          return {width:innerWidth,scrollY,row:{key:row.dataset.row,...box(row)},cells:[...row.children].map(box),
            helpers:helpers.map(e=>({class:e.className,text:e.textContent,size:parseFloat(getComputedStyle(e).fontSize)}))};
        }''')
        no_overflow(page)
        assert metric['scrollY'] == 0, metric
        assert metric['row']['key'] == 'Потужність', metric
        if width in [1440, 390]:
            assert all(cell['top'] >= 0 and cell['bottom'] <= height and cell['left'] >= 0 and cell['right'] <= width + 1 for cell in metric['cells']), metric
        assert metric['helpers'] and all(item['size'] >= 11 for item in metric['helpers']), metric
        page.screenshot(path=str(a.output / f'case-readable-{width}.png'))
        observations.append(metric)
    return observations


def desktop_pair(page):
    page.goto(base, wait_until='networkidle')
    personal = '{"reviewer":"untouched personal bytes","cart":{"u02":3},"drafts":{"u02":{"question":"Точна чернетка D1"}}}'
    page.evaluate('([key,value])=>localStorage.setItem(key,value)', [personal_key, personal])
    enter(page); before = selection(page)
    toggle = page.get_by_test_id('wb-pair-focus')
    toggle.focus(); page.keyboard.press('Space'); expect(toggle).to_have_attribute('aria-pressed', 'true')
    expect(page.locator('.wb-full')).not_to_be_visible(); expect(page.locator('.wb-pair')).to_be_visible()
    expect(page.locator('.wb-pair .wb-model-title')).to_have_count(2)
    assert selection(page) == before
    page.get_by_test_id('wb-pair-a').select_option('u02'); page.get_by_test_id('wb-pair-b').select_option('u04')
    assert state(page)['view']['pairs']['ups'] == ['u02', 'u04']
    expect(page.locator('.wb-pair')).to_contain_text('DEMO-U02'); expect(page.locator('.wb-pair')).to_contain_text('DEMO-U04')
    assert state(page)['compareByGroup']['ups'] == before['compareByGroup']['ups']
    page.screenshot(path=str(a.output / 'desktop-active-pair.png'))
    toggle.click(); expect(toggle).to_have_attribute('aria-pressed', 'false')
    expect(page.locator('.wb-full .wb-model-title')).to_have_count(6)
    page.get_by_test_id('wb-save').click(); page.reload(wait_until='networkidle')
    expect(page.get_by_test_id('comparison-workbench')).to_be_visible()
    assert state(page)['view']['pairs']['ups'] == ['u02', 'u04']
    assert state(page)['compareByGroup']['ups'] == before['compareByGroup']['ups']
    page.get_by_test_id('wb-pair-a').select_option('u05'); page.get_by_test_id('wb-pair-b').select_option('u06')
    before_replace = selection(page)
    page.get_by_test_id('wb-pair-focus').click()
    page.locator('.wb-candidates > summary').click(); page.get_by_test_id('wb-replace-u05').click()
    page.get_by_test_id('wb-search').fill('DEMO-U07'); page.get_by_test_id('wb-add-u07').click()
    assert state(page)['view']['pairs']['ups'] == ['u07', 'u06']
    expect(page.locator('.wb-pair')).to_contain_text('DEMO-U07')
    expect(page.get_by_test_id('wb-undo')).to_be_focused(); page.keyboard.press('Enter')
    assert selection(page) == before_replace
    assert page.evaluate('(key)=>localStorage.getItem(key)', personal_key) == personal
    return {'candidates': state(page)['compareByGroup']['ups'], 'pair_after_undo': state(page)['view']['pairs']['ups'], 'personal_bytes_unchanged': True}


def sticky_keyboard(page):
    observations = []
    for width, enlarged in [(1440, False), (1000, False), (390, False), (320, False), (390, True)]:
        page.set_viewport_size({'width': width, 'height': 900 if width > 700 else 844})
        enter(page)
        # The switches category has ten real parameter rows: use existing catalog IDs,
        # not duplicated markup or fabricated rows, for a genuinely long table.
        saved = state(page)
        switch_ids = json.loads(subprocess.check_output(['node', '--input-type=module', '-e', "import {products} from './data.js';console.log(JSON.stringify(products.filter(p=>p.group==='switches').slice(0,6).map(p=>p.id)))"], cwd=root, text=True))
        saved['compareByGroup']['switches'] = switch_ids
        saved['view']['pairs']['switches'] = switch_ids[-2:]
        page.goto(base, wait_until='networkidle')
        page.evaluate('([key,value])=>sessionStorage.setItem(key,JSON.stringify(value))', [case_key, saved])
        page.goto(base + 'demo.html?case=six-candidates&v=1#/asp/compare?experience=modern', wait_until='networkidle')
        page.get_by_test_id('wb-group').select_option('switches')
        if enlarged:
            page.evaluate('''() => {const nodes=[...document.querySelectorAll('body,body *')],sizes=nodes.map(e=>getComputedStyle(e).fontSize);nodes.forEach((e,i)=>e.style.setProperty('font-size',parseFloat(sizes[i])*2+'px','important'));}''')
        table = page.locator('.wb-full' if width > 700 else '.wb-pair')
        table.evaluate('e=>e.scrollIntoView({block:"start"})'); table.focus()
        expect(table).to_be_focused()
        # Arrow keys exercise the real scrollable region; no scrollTop fixture substitutes for them.
        for _ in range(8): page.keyboard.press('ArrowDown')
        page.wait_for_function('e=>e.scrollTop>50', arg=table.element_handle())
        table.press('ArrowRight'); page.wait_for_timeout(100)
        geometry = table.evaluate('''e=>{const box=n=>{const r=n.getBoundingClientRect();return {top:r.top,bottom:r.bottom,left:r.left,right:r.right};};return {scrollTop:e.scrollTop,scrollLeft:e.scrollLeft,client:e.clientWidth,scroll:e.scrollWidth,box:box(e),heads:[...e.querySelectorAll('thead th')].map(box),labels:[...e.querySelectorAll('tbody th')].map(box)};}''')
        assert all(abs(head['top'] - geometry['box']['top'] - 1) <= 1 for head in geometry['heads']), geometry
        assert all(abs(label['left'] - geometry['box']['left'] - 1) <= 1 for label in geometry['labels']), geometry
        if geometry['scroll'] > geometry['client'] + 1: assert geometry['scrollLeft'] > 0, geometry
        assert table.get_attribute('role') == 'region' and table.get_attribute('aria-describedby')
        # Tab into actions and verify focus is never hidden behind the sticky headings.
        footer = table.locator('tfoot button:not(:disabled)').first
        footer.focus(); expect(footer).to_be_focused()
        page.wait_for_function('''e=>{const r=e.closest('.wb-table-wrap'),b=e.getBoundingClientRect(),h=[...r.querySelectorAll('thead th')].map(x=>x.getBoundingClientRect());return h.every(x=>x.top>=-1)&&b.left>=h[0].right-1&&b.top>=Math.max(...h.map(x=>x.bottom))-1;}''', arg=footer.element_handle())
        focus = footer.evaluate('''e=>{const region=e.closest('.wb-table-wrap'),b=e.getBoundingClientRect(),r=region.getBoundingClientRect(),heads=[...region.querySelectorAll('thead th')].map(h=>h.getBoundingClientRect());return {top:b.top,bottom:b.bottom,left:b.left,right:b.right,regionBottom:r.bottom,regionRight:r.right,parameterRight:heads[0].right,headingTop:Math.min(...heads.map(h=>h.top)),headingBottom:Math.max(...heads.map(h=>h.bottom)),outline:getComputedStyle(e).outlineStyle};}''')
        assert focus['top'] >= focus['headingBottom'] - 1 and focus['bottom'] <= focus['regionBottom'] + 1, focus
        assert focus['headingTop'] >= -1 and focus['left'] >= focus['parameterRight'] - 1 and focus['right'] <= focus['regionRight'] + 1, focus
        assert focus['outline'] != 'none', focus
        page.keyboard.press('Tab'); assert page.evaluate('document.activeElement.tagName') != 'BODY'
        no_overflow(page); page.screenshot(path=str(a.output / f'sticky-context-{width}{"-text200" if enlarged else ""}.png'))
        observations.append({'width': width, 'text200': enlarged, 'geometry': geometry, 'footer_focus': focus})
    return observations


def reading_return(page):
    enter(page)
    saved = state(page)
    ids = json.loads(subprocess.check_output(['node', '--input-type=module', '-e', "import {products} from './data.js';console.log(JSON.stringify(products.filter(p=>p.group==='switches').slice(0,6).map(p=>p.id)))"], cwd=root, text=True))
    saved['compareByGroup']['switches'] = ids; saved['view']['pairs']['switches'] = ids[-2:]; saved['view']['group'] = 'switches'
    page.goto(base, wait_until='networkidle')
    page.evaluate('([key,value])=>sessionStorage.setItem(key,JSON.stringify(value))', [case_key, saved])
    compare_url = base + 'demo.html?case=six-candidates&v=1#/asp/compare?experience=modern'
    page.goto(compare_url, wait_until='networkidle')
    page.get_by_test_id('wb-pair-focus').click()
    table = page.locator('.wb-pair'); table.evaluate('e=>e.scrollIntoView({block:"start"})'); table.focus()
    for _ in range(12): page.keyboard.press('ArrowDown')
    page.wait_for_function('e=>e.scrollTop>100', arg=table.element_handle())
    page.wait_for_timeout(250)
    before = table.evaluate('e=>({x:e.scrollLeft,y:e.scrollTop,window:scrollY})'); content = selection(page)
    focus = table.locator('.wb-model-title').first
    focus.evaluate('e=>e.focus({preventScroll:true})'); page.keyboard.press('Enter')
    page.locator('#modal a[href*="/product/"]').click()
    page.locator('.return-comparison').click()
    restored_stages = []
    def restored(stage):
        expect(page.get_by_test_id('wb-pair-focus')).to_have_attribute('aria-pressed', 'true')
        try:
            page.wait_for_function('''expected=>{const root=document.querySelector('.comparison-workbench'),table=root?.querySelector('.wb-pair');return root&&!root.dataset.restoringView&&Math.abs(table.scrollTop-expected.y)<2&&Math.abs(table.scrollLeft-expected.x)<2&&Math.abs(scrollY-expected.window)<2;}''', arg=before)
        except Exception:
            actual = page.evaluate('''() => ({window:scrollY,root:document.querySelector('.comparison-workbench')?.dataset,table:[...document.querySelectorAll('.wb-table-wrap')].map(e=>({class:e.className,x:e.scrollLeft,y:e.scrollTop})),focus:document.activeElement.outerHTML})''')
            raise AssertionError({'stage':stage,'expected':before,'actual':actual,'saved':state(page)['view']['pages'].get('#/asp/compare?experience=modern'),'completed_stages':restored_stages})
        assert selection(page) == content
        expect(page.locator(f'[data-wb-focus="model-pair-{ids[-2]}"]')).to_be_focused()
        restored_stages.append({'stage':stage,'position':table.evaluate('e=>({x:e.scrollLeft,y:e.scrollTop,window:scrollY})')})
    restored('card-return')
    page.locator(f'[data-wb-focus="model-pair-{ids[-2]}"]').press('Enter')
    page.locator('#modal').get_by_role('link', name='Документ D1', exact=True).click()
    expect(page.locator('.document-page')).to_be_visible()
    page.locator('.return-comparison').click(); restored('document-return')
    page.go_back(wait_until='networkidle'); expect(page.locator('.document-page')).to_be_visible()
    page.go_forward(wait_until='networkidle'); restored('history-forward')
    page.reload(wait_until='networkidle'); restored('reload')
    page.screenshot(path=str(a.output / 'pair-reading-context-restored.png'))
    return {'before': before, 'after': table.evaluate('e=>({x:e.scrollLeft,y:e.scrollTop,window:scrollY})'), 'restored_stages':restored_stages,'page_view': state(page)['view']['pages']['#/asp/compare?experience=modern']}


checks = [('compact-case-first-technical-row-readable-helpers', compact_readability),
          ('desktop-pair-focus-six-candidates-save-reload-undo-personal-isolation', desktop_pair),
          ('long-table-sticky-model-parameter-keyboard-context', sticky_keyboard),
          ('pair-focus-reading-position-card-document-history-reload-keyboard', reading_return)]
if a.check:
    checks = [(name, check) for name, check in checks if name == a.check]
    if not checks: p.error('Unknown --check')
with sync_playwright() as pw:
    try:
        options = {'chromium_sandbox': True} if a.browser == 'chromium' else {}
        if a.executable: options['executable_path'] = a.executable
        browser = getattr(pw, a.browser).launch(**options)
    except Exception as error:
        results.update(status='BLOCKED', launch_error=str(error))
    else:
        results['browser_version'] = browser.version
        for title, check in checks:
            context = browser.new_context(viewport={'width': 1440, 'height': 900}, reduced_motion='reduce')
            context.tracing.start(screenshots=True, snapshots=True, sources=True)
            errors = []
            def local_only(route):
                if urlsplit(route.request.url).netloc == urlsplit(base).netloc: route.continue_()
                else: errors.append('Unexpected external request: ' + route.request.url); route.abort()
            context.route('**/*', local_only)
            page = context.new_page(); page.set_default_timeout(12000)
            page.on('pageerror', lambda error: errors.append(str(error)))
            try:
                details = check(page); assert not errors, errors
            except Exception as error:
                page.screenshot(path=str(a.output / (title + '-failure.png')), full_page=True)
                context.tracing.stop(path=str(a.output / (title + '.zip')))
                results['checks'].append({'name': title, 'status': 'FAIL', 'error': str(error), 'traceback': traceback.format_exc(), 'console_errors': errors})
                print('FAIL', title, error, flush=True)
            else:
                context.tracing.stop()
                results['checks'].append({'name': title, 'status': 'PASS', 'details': details}); print('PASS', title, flush=True)
            finally: context.close()
        browser.close()
        results['status'] = 'FAIL' if any(check['status'] == 'FAIL' for check in results['checks']) else 'PASS'
results['completed_at_utc'] = datetime.now(timezone.utc).isoformat()
(a.output / 'results.json').write_text(json.dumps(results, ensure_ascii=False, indent=2) + '\n')
print(results['status'], a.output / 'results.json', flush=True)
raise SystemExit(0 if results['status'] == 'PASS' else 2 if results['status'] == 'BLOCKED' else 1)
