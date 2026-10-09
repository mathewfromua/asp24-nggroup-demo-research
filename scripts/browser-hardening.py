#!/usr/bin/env python3
"""Focused P1 fault checks on an existing HTTP build, with browser sandbox on.

Fault injection verifies same-page recovery, not native Safari/Telegram support.
No app build, full suite, external requests, or real user records are involved.
"""
import argparse
from datetime import datetime, timezone
import importlib.metadata
import json
from pathlib import Path
import platform
import subprocess
import traceback
from urllib.parse import urljoin, urlsplit
from playwright.sync_api import expect, sync_playwright

parser=argparse.ArgumentParser(description=__doc__)
parser.add_argument('--url',required=True)
parser.add_argument('--browser',choices=['chromium','firefox','webkit'],default='chromium')
parser.add_argument('--executable')
parser.add_argument('--output',type=Path,required=True)
parser.add_argument('--only',help='Comma-separated exact check names for an addressed rerun; omitted in the full gate')
args=parser.parse_args();args.output.mkdir(parents=True,exist_ok=True)
root=Path(__file__).resolve().parents[1];base=args.url.rstrip('/')+'/'
key='perspective-demo-v1';casekey='asp24-nggroup-case:model-document:v1'
question='  DEMO-U02 · D1 — 24 В\nКількість 2, «точний текст» <tag> & № 7.  '
fixture=json.loads(subprocess.check_output(['node','--input-type=module','-e',"import {initialState} from './logic.js';console.log(JSON.stringify(initialState()))"],cwd=root,text=True))
results={'schema':1,'commit':subprocess.check_output(['git','rev-parse','HEAD'],cwd=root,text=True).strip(),
 'working_tree_dirty':bool(subprocess.check_output(['git','status','--porcelain'],cwd=root,text=True).strip()),
 'started_at_utc':datetime.now(timezone.utc).isoformat(),'browser':args.browser,'url':base,
 'environment':{'platform':platform.platform(),'python':platform.python_version(),'playwright':importlib.metadata.version('playwright')},
 'checks':[],'not_run':['native Safari/macOS','Safari/iOS','Chrome/Android','Telegram iOS/Android','WKWebView/Android WebView devices','physical screen keyboard','VoiceOver']}

def go(page,path):
    response=page.goto(base+path,wait_until='networkidle')
    if response:assert response.status==200,(path,response.status)

def draft(page,case=False):
    go(page,'demo.html'+('?case=model-document&v=1' if case else '')+'#/ng/document/u02')
    page.locator('.document-page [data-action=consult][data-id=u02]').click()
    page.locator('#consult-form [name=question]').fill(question)
    page.locator('#consult-form [name=quantity]').fill('2')
    return page.locator('#consult-form [name=question]')

def summary(page):
    page.locator('#consult-form button[type=submit]').click()
    expect(page.locator('.summary-text')).to_contain_text(question.strip())
    return page.locator('.summary-text').inner_text()

def no_overflow(page):
    sizes=page.evaluate('({width:innerWidth,document:document.documentElement.scrollWidth})')
    assert sizes['document']<=sizes['width']+1,sizes

def normal_exports(page):
    draft(page);text=summary(page)
    with page.expect_download() as event:page.locator('[data-action=download-consult]').click()
    file=args.output/'normal-question.txt';event.value.save_as(file)
    assert file.read_text(encoding='utf-8-sig')==text
    expect(page.locator('#modal .export-fallback textarea')).to_have_value(text)
    expect(page.locator('#modal .export-fallback')).to_contain_text('Перевірте завантаження')
    go(page,'demo.html?case=model-document&v=1#/ng/document/u02')
    with page.expect_download() as event:page.locator('#case-export').click()
    file=args.output/'normal-case.json';event.value.save_as(file)
    payload=json.loads(file.read_text());assert payload['caseId']=='model-document' and payload['stateSchemaVersion']==4
    assert json.loads(page.locator('.case-context-details .export-fallback textarea').input_value())==payload

def missing_download_clipboard(page):
    page.set_viewport_size({'width':390,'height':844})
    page.add_init_script("Object.defineProperty(URL,'createObjectURL',{configurable:true,value:undefined});Object.defineProperty(navigator,'clipboard',{configurable:true,value:undefined});")
    draft(page);text=summary(page)
    page.locator('[data-action=copy-consult]').click()
    expect(page.locator('#copy-fallback textarea')).to_have_value(text)
    expect(page.locator('#copy-fallback')).to_contain_text('Автокопіювання недоступне')
    page.locator('[data-action=download-consult]').click()
    area=page.locator('#modal .export-fallback textarea')
    expect(area).to_have_value(text);expect(area).to_be_visible()
    expect(page.locator('#modal .export-fallback')).to_contain_text('Завантаження недоступне')
    page.locator('#modal .export-fallback').get_by_role('button',name='Виділити весь текст',exact=True).click()
    assert area.evaluate('(e)=>e.selectionStart===0&&e.selectionEnd===e.value.length')
    no_overflow(page);page.screenshot(path=str(args.output/'missing-apis-390.png'))
    page.locator('#modal [data-action=close]').first.click()
    page.locator('.document-page [data-action=consult][data-id=u02]').click()
    expect(page.locator('#consult-form [name=question]')).to_have_value(question)

def silent_download_and_denied_copy(page):
    page.set_viewport_size({'width':390,'height':844})
    page.add_init_script('''const click=HTMLAnchorElement.prototype.click;
      HTMLAnchorElement.prototype.click=function(){if(this.download)return;return click.call(this);};
      Object.defineProperty(navigator,'clipboard',{configurable:true,value:{writeText:async()=>{throw new DOMException('Intentional denied copy','NotAllowedError');}}});''')
    go(page,'index.html')
    personal=json.dumps(fixture,ensure_ascii=False)
    page.evaluate('([k,v])=>localStorage.setItem(k,v)',[key,personal])
    draft(page,case=True)
    page.locator('#modal [data-action=close]').click()
    page.locator('#case-export').click()
    panel=page.locator('.case-context-details .export-fallback')
    expect(panel).to_contain_text('якщо файл не з’явився')
    panel.locator('summary').click()
    area=panel.locator('textarea');expect(area).to_be_visible()
    payload=json.loads(area.input_value())
    assert payload['state']['drafts']['u02']['question']==question
    assert payload['state']['drafts']['u02']['quantity']=='2'
    assert page.evaluate('(k)=>localStorage.getItem(k)',key)==personal
    panel.get_by_role('button',name='Копіювати текст',exact=True).click()
    expect(panel).to_contain_text('Автокопіювання недоступне')
    assert area.evaluate('(e)=>e.selectionEnd===e.value.length')
    for width in [320,390,430]:
        page.set_viewport_size({'width':width,'height':844});no_overflow(page)
    page.set_viewport_size({'width':390,'height':844});page.screenshot(path=str(args.output/'silent-download-copy-denied-390.png'))
    (args.output/'silent-download-case.json').write_text(area.input_value())

def denied_storage_preserves_live_draft(page):
    page.add_init_script('''const set=Storage.prototype.setItem;
      Storage.prototype.setItem=function(k,v){if(k==='perspective-demo-v1')throw new DOMException('Intentional quota fault','QuotaExceededError');return set.call(this,k,v);};
      Object.defineProperty(URL,'createObjectURL',{configurable:true,value:undefined});''')
    draft(page)
    expect(page.locator('#consult-form [data-save-status]')).to_contain_text('Лише в пам’яті')
    # A different tab must not replace this tab's unsaved question with older data.
    page.evaluate('([k,s])=>window.dispatchEvent(new StorageEvent("storage",{key:k,newValue:JSON.stringify(s),storageArea:localStorage}))',[key,fixture])
    expect(page.locator('#consult-form [name=question]')).to_have_value(question)
    page.locator('#modal [data-action=close]').click()
    expect(page.locator('#storage-warning')).to_be_visible()
    page.locator('#storage-warning [data-action=export-live-state]').click()
    raw=page.locator('#modal .export-fallback textarea').input_value();payload=json.loads(raw)
    assert payload['version']==4 and payload['drafts']['u02']['question']==question and payload['drafts']['u02']['quantity']=='2'
    assert page.evaluate('(k)=>localStorage.getItem(k)',key) is None
    (args.output/'memory-only-personal-state.json').write_text(raw)
    page.locator('#modal [data-action=close]').click()
    page.locator('a.back[href="#/ng/product/u02"]').click()
    page.go_back(wait_until='networkidle')
    page.locator('.document-page [data-action=consult][data-id=u02]').click()
    expect(page.locator('#consult-form [name=question]')).to_have_value(question)
    expect(page.locator('#consult-form [data-save-status]')).to_contain_text('Лише в пам’яті')

def react_failure_keeps_navigation(page):
    blocked=[]
    def block(route):
        if 'comparison-workbench-' in route.request.url and urlsplit(route.request.url).path.endswith('.js'):
            blocked.append(route.request.url);route.abort()
        else:route.continue_()
    page.route('**/assets/*',block)
    go(page,'demo.html?case=six-candidates&v=1#/asp/compare?experience=modern')
    expect(page.locator('#modern-comparison [role=alert]')).to_contain_text('Поточний добір не змінено')
    assert blocked,'The intended React chunk was not blocked'
    links=page.locator('#modern-comparison nav');expect(links.get_by_role('link',name='До каталогу',exact=True)).to_be_visible()
    expect(links.get_by_role('link',name='HTML-огляди та PDF',exact=True)).to_be_visible()
    links.get_by_role('link',name='Класичне порівняння',exact=True).click()
    expect(page.locator('.research-workspace')).to_be_visible()
    assert page.locator('.research-desktop [data-compare-id]').count()==6
    page.go_back(wait_until='networkidle')
    page.get_by_role('link',name='Документи моделей',exact=True).click()
    expect(page.locator('h1')).to_have_text('Документи за моделями')
    page.locator('#search').fill('DEMO-U02');page.locator('#search').press('Enter')
    expect(page.locator('.document-row')).to_have_count(1);page.locator('.document-row').click()
    expect(page.locator('.document-page')).to_contain_text('DEMO-U02')
    page.locator('[data-action=reports]').click()
    html=page.locator('#modal a[href$="reports/ASP24_Review.html"]')
    assert html.get_attribute('target') is None
    pdf=page.locator('#modal a[href$="reports/ASP24_Review.pdf"]')
    assert pdf.get_attribute('target') is None
    response=page.request.get(urljoin(page.url,pdf.get_attribute('href')));assert response.status==200 and response.body().startswith(b'%PDF-')
    html.click();expect(page.locator('h1')).to_contain_text('ASP24 —')
    page.go_back(wait_until='networkidle');expect(page.locator('.document-page')).to_contain_text('DEMO-U02')
    assert len(page.context.pages)==1

checks=[('normal-TXT-JSON-downloads-with-same-page-copy',normal_exports),
 ('missing-download-and-clipboard-APIs-mobile',missing_download_clipboard),
 ('silently-blocked-download-denied-clipboard-case-isolation',silent_download_and_denied_copy),
 ('personal-storage-denied-live-draft-export-history-cross-tab',denied_storage_preserves_live_draft),
 ('React-load-failure-classic-catalog-documents-reports-same-tab',react_failure_keeps_navigation)]
if args.only:
    selected=set(args.only.split(','));assert selected<={name for name,_ in checks},selected
    checks=[entry for entry in checks if entry[0] in selected];results['selected_checks']=sorted(selected)
with sync_playwright() as pw:
    try:
        options={'chromium_sandbox':True} if args.browser=='chromium' else {}
        if args.executable:options['executable_path']=args.executable
        browser=getattr(pw,args.browser).launch(timeout=30000,**options)
    except Exception as error:results.update(status='BLOCKED',launch_error=str(error))
    else:
        results['browser_version']=browser.version
        for name,check in checks:
            context=browser.new_context(viewport={'width':1440,'height':900},accept_downloads=True,reduced_motion='reduce')
            context.set_default_timeout(12000);context.tracing.start(screenshots=True,snapshots=True,sources=True)
            errors=[]
            def local_only(route):
                if urlsplit(route.request.url).netloc==urlsplit(base).netloc:route.continue_()
                else:errors.append('Unexpected outbound request: '+route.request.url);route.abort()
            context.route('**/*',local_only);page=context.new_page();page.on('pageerror',lambda error:errors.append(str(error)))
            try:check(page);assert not errors,errors
            except Exception as error:
                page.screenshot(path=str(args.output/(name+'-failure.png')),full_page=True)
                context.tracing.stop(path=str(args.output/(name+'.zip')))
                results['checks'].append({'name':name,'status':'FAIL','error':str(error),'traceback':traceback.format_exc(),'console_errors':errors})
                print('FAIL',name,error,flush=True)
            else:
                context.tracing.stop();results['checks'].append({'name':name,'status':'PASS'});print('PASS',name,flush=True)
            finally:context.close()
        browser.close();results['status']='FAIL' if any(c['status']=='FAIL' for c in results['checks']) else 'PASS'
results['completed_at_utc']=datetime.now(timezone.utc).isoformat()
(args.output/'results.json').write_text(json.dumps(results,ensure_ascii=False,indent=2)+'\n')
print(results['status'],args.output/'results.json',flush=True)
raise SystemExit(0 if results['status']=='PASS' else 2 if results['status']=='BLOCKED' else 1)
