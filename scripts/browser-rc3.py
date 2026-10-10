#!/usr/bin/env python3
"""RC3 case-route regressions: first technical row, Modern return, isolated replacement undo."""
import argparse
from datetime import datetime, timezone
import importlib.metadata
import json
from pathlib import Path
import platform
import subprocess
import sys
import traceback
from urllib.parse import urlsplit
from playwright.sync_api import sync_playwright, expect

parser=argparse.ArgumentParser(description=__doc__)
parser.add_argument('--url',required=True)
parser.add_argument('--browser',choices=['chromium','firefox','webkit'],default='chromium')
parser.add_argument('--executable')
parser.add_argument('--output',type=Path,required=True)
args=parser.parse_args();args.output.mkdir(parents=True,exist_ok=True)
root=Path(__file__).resolve().parents[1]
base=args.url.rstrip('/')+'/'
case_key='asp24-nggroup-case:six-candidates:v1'
personal_key='perspective-demo-v1'
fixture=json.loads(subprocess.check_output(['node','--input-type=module','-e',"import {initialState} from './logic.js';import {products} from './data.js';console.log(JSON.stringify({state:initialState(),products}))"],cwd=root,text=True))
products={p['id']:p for p in fixture['products']}
results={'schema':1,'commit':subprocess.check_output(['git','rev-parse','HEAD'],cwd=root,text=True).strip(),
 'started_at_utc':datetime.now(timezone.utc).isoformat(),'browser':args.browser,'url':base,'command':['python',*sys.argv],
 'environment':{'platform':platform.platform(),'python':platform.python_version(),'playwright':importlib.metadata.version('playwright')},
 'checks':[],'not_run':['stable Safari','physical iPhone','native zoom','VoiceOver','public deployment']}


def stored(page):
    return page.evaluate('(key)=>JSON.parse(sessionStorage.getItem(key))',case_key)


def selection(page):
    s=stored(page)
    return {key:s[key] for key in ['compareByGroup','cart','drafts']} | {'view':{key:s['view'][key] for key in ['group','pairs','differences']}}


def enter_case(page,brand='asp'):
    # Start at the physical versioned case URL, then follow real links into its isolated state.
    response=page.goto(base+'cases/six-candidates/v1/',wait_until='networkidle')
    assert response.status==200
    page.get_by_role('link',name='Відкрити приклад',exact=True).click()
    expect(page.locator('.research-workspace')).to_be_visible()
    page.get_by_role('link',name='Новий робочий простір →',exact=True).click()
    expect(page.get_by_test_id('comparison-workbench')).to_be_visible()
    if brand=='ng':
        page.goto(base+'demo.html?case=six-candidates&v=1#/ng/compare?experience=modern',wait_until='networkidle')
        expect(page.get_by_test_id('comparison-workbench')).to_be_visible()
    assert '?case=six-candidates&v=1' in page.url and 'experience=modern' in page.url


def initial_geometry(page):
    for width,height in [(1440,900),(390,844)]:
        page.set_viewport_size({'width':width,'height':height})
        page.goto(base+'index.html',wait_until='networkidle')
        page.evaluate('(key)=>sessionStorage.removeItem(key)',case_key)
        enter_case(page)
        page.evaluate('() => document.fonts.ready')
        # Navigation itself must present the table; no scroll correction before measuring.
        measure=page.evaluate('''() => {
          const wrap=document.querySelector(innerWidth>700?'.wb-full':'.wb-pair');
          const box=e=>{const r=e.getBoundingClientRect();return {top:r.top,bottom:r.bottom,left:r.left,right:r.right,width:r.width,height:r.height};};
          const row=wrap.querySelector('tbody tr[data-row]');
          const titles=[...wrap.querySelectorAll('.wb-model-title')].map(e=>({text:e.textContent,...box(e)}));
          const cells=[...row.children].map(e=>({text:e.textContent,...box(e)}));
          return {url:location.href,viewport:{width:innerWidth,height:innerHeight},scrollY,documentWidth:document.documentElement.scrollWidth,
            row:{key:row.dataset.row,...box(row)},cells,titles,banner:box(document.querySelector('.case-banner')),
            contextOpen:document.querySelector('.case-context-details').open,candidatesOpen:document.querySelector('.wb-candidates').open};
        }''')
        (args.output/f'case-{width}x{height}-geometry.json').write_text(json.dumps(measure,ensure_ascii=False,indent=2)+'\n')
        page.screenshot(path=str(args.output/f'case-{width}x{height}-first-technical-row.png'),full_page=False)
        assert measure['scrollY']==0,measure
        assert measure['documentWidth']<=width+1,measure
        assert not measure['contextOpen'] and not measure['candidatesOpen'],measure
        assert measure['row']['top']>=0 and measure['row']['bottom']<=height,measure
        assert len(measure['titles'])==(6 if width>700 else 2),measure
        for item in measure['titles']+measure['cells']:
            assert item['text'].strip() and item['top']>=0 and item['bottom']<=height and item['left']>=0 and item['right']<=width+1,item
        expect(page.locator('.case-demo-notice')).to_be_visible()
        expect(page.locator('#case-storage-status')).to_be_visible()
        expect(page.locator('.case-demo-notice')).to_contain_text('умовні')
        summary=page.locator('.case-context-details > summary');summary.focus();page.keyboard.press('Enter')
        expect(page.locator('#case-export')).to_be_visible();expect(page.locator('#case-reset')).to_be_visible()
        assert page.locator('.case-context-details').evaluate('e=>e.open')
        with page.expect_download() as event:page.locator('#case-export').click()
        destination=args.output/f'case-{width}-export.json';event.value.save_as(destination)
        payload=json.loads(destination.read_text());assert payload['caseId']=='six-candidates' and payload['stateSchemaVersion']==4
        page.locator('#case-reset').click();page.wait_for_load_state('networkidle')
        expect(page.get_by_test_id('comparison-workbench')).to_be_visible()
        assert 'experience=modern' in page.url


def modern_return(page):
    enter_case(page)
    # A non-default category makes an accidental default-to-UPS return observable.
    state=stored(page)
    state['compareByGroup']['cable']=[f'c{i:02}' for i in range(1,7)]
    state['view']['pairs']['cable']=['c05','c06']
    state['cart']={'u02':3,'c04':2}
    state['drafts']['u02']={'purpose':'Тест','quantity':'2','question':'  D1\nНе втратити чернетку  '}
    modern_url=page.url
    # Seed away from the app so its pagehide save cannot replace the fixture.
    page.goto(base+'index.html',wait_until='networkidle')
    page.evaluate('([key,s])=>sessionStorage.setItem(key,JSON.stringify(s))',[case_key,state])
    page.goto(modern_url,wait_until='networkidle')
    expect(page.get_by_test_id('comparison-workbench')).to_be_visible()
    page.get_by_test_id('wb-group').select_option('cable')
    page.get_by_test_id('wb-differences').check()
    before=selection(page)
    pid=next(pid for pid in state['compareByGroup']['cable'] if products[pid]['ng'])
    page.locator('.wb-full .wb-model-title').filter(has_text=products[pid]['name']).click()
    page.locator('#modal').get_by_role('link',name='Картка NG Group',exact=True).click()
    expect(page.locator('.detail-head')).to_contain_text(products[pid]['sku'])
    page.get_by_role('link',name='Приклад технічного опису',exact=True).click()
    expect(page.locator('.document-page')).to_contain_text(products[pid]['sku'])
    page.reload(wait_until='networkidle')
    expect(page.locator('.return-comparison')).to_have_attribute('href','#/asp/compare?experience=modern')
    page.locator('.return-comparison').click()
    expect(page.get_by_test_id('comparison-workbench')).to_be_visible()
    assert selection(page)==before
    page.go_back(wait_until='networkidle');expect(page.locator('.document-page')).to_contain_text(products[pid]['sku'])
    page.go_forward(wait_until='networkidle');expect(page.get_by_test_id('comparison-workbench')).to_be_visible()
    assert selection(page)==before
    # Classic explicitly selected by the user must keep its own return route.
    page.get_by_role('link',name='Класичне порівняння',exact=True).click()
    page.locator(f'[data-action="compare-details"][data-id="{pid}"]').first.click()
    page.locator('#modal').get_by_role('link',name='Документ D1',exact=True).click()
    expect(page.locator('.return-comparison')).to_have_attribute('href','#/asp/compare')
    page.locator('.return-comparison').click();expect(page.locator('.research-workspace')).to_be_visible()
    assert selection(page)==before
    page.get_by_role('link',name='Новий робочий простір →',exact=True).click()
    page.locator('.case-banner').get_by_role('link',name='Повернутися до розділу огляду',exact=True).click()
    page.wait_for_load_state('networkidle');assert page.url==base+'reports/ASP24_Review.html#asp24-09'
    expect(page.locator('#asp24-09')).to_be_visible()


def replacement_undo(page):
    enter_case(page)
    state=stored(page)
    state['compareByGroup']['cable']=['c04','c05'];state['view']['pairs']['cable']=['c05','c04']
    state['cart']={'u02':3,'c04':2};state['drafts']['u02']={'purpose':'Тест','quantity':'2','question':'  Текст\nD1  '}
    personal=json.dumps(fixture['state'],ensure_ascii=False)
    other=json.dumps(state,ensure_ascii=False)
    modern_url=page.url
    page.goto(base+'index.html',wait_until='networkidle')
    page.evaluate('([key,s,pk,personal,other])=>{sessionStorage.setItem(key,JSON.stringify(s));localStorage.setItem(pk,personal);sessionStorage.setItem("asp24-nggroup-case:two-reels:v1",other);}',[case_key,state,personal_key,personal,other])
    page.goto(modern_url,wait_until='networkidle');expect(page.get_by_test_id('comparison-workbench')).to_be_visible();before=selection(page)
    page.locator('.wb-candidates > summary').click()
    page.get_by_test_id('wb-replace-u05').click()
    page.get_by_test_id('wb-search').fill('DEMO-U07')
    page.get_by_test_id('wb-add-u07').click()
    expect(page.get_by_test_id('wb-search')).to_have_count(0)
    expect(page.get_by_test_id('wb-undo')).to_be_focused()
    expect(page.get_by_test_id('wb-undo')).to_contain_text('Скасувати заміну')
    changed=stored(page);assert changed['compareByGroup']['ups']==['u01','u02','u03','u04','u07','u06']
    assert changed['view']['pairs']['ups']==['u07','u06']
    page.keyboard.press('Enter')
    expect(page.get_by_test_id('wb-undo')).to_be_disabled()
    expect(page.locator('.wb-action-status')).to_contain_text('кандидата й пару відновлено')
    assert selection(page)==before
    assert page.evaluate('(key)=>localStorage.getItem(key)',personal_key)==personal
    assert page.evaluate('() => sessionStorage.getItem("asp24-nggroup-case:two-reels:v1")')==other
    page.reload(wait_until='networkidle');assert selection(page)==before
    # The alternative replacement entry through model details uses the same snapshot.
    page.locator('.wb-full .wb-model-title').filter(has_text=products['u05']['name']).click()
    page.locator('#modal [data-action="replace-model"]').click()
    page.locator('#modal [data-action="pick-candidate"][data-id="u07"]').click()
    expect(page.get_by_test_id('wb-undo')).to_be_focused()
    assert stored(page)['view']['pairs']['ups']==['u07','u06']
    page.get_by_test_id('wb-undo').click();assert selection(page)==before
    page.screenshot(path=str(args.output/'case-replacement-undone.png'),full_page=False)


def storage_warning(page):
    page.add_init_script('''(() => {const save=Storage.prototype.setItem;Storage.prototype.setItem=function(key,value){if(this===sessionStorage&&key==='asp24-nggroup-case:six-candidates:v1')throw new DOMException('RC3 intentional quota probe','QuotaExceededError');return save.call(this,key,value);};})();''')
    enter_case(page)
    expect(page.locator('#case-storage-status')).to_contain_text('лише в пам’яті')
    expect(page.locator('#case-storage-status')).to_be_visible()
    assert page.locator('.case-context-details').evaluate('e=>!e.open')
    assert not page.locator('#case-storage-status').evaluate('e=>!!e.closest("details")')
    expect(page.locator('#storage-warning')).to_be_visible()
    page.locator('.case-context-details > summary').click()
    with page.expect_download() as event:page.locator('#case-export').click()
    event.value.save_as(args.output/'case-memory-only-export.json')


checks=[('case-first-technical-row-1440x900-and-390x844',initial_geometry),
 ('modern-card-document-return-history-classic-category-pair-differences',modern_return),
 ('case-last-replacement-undo-slot-pair-personal-other-case-isolation',replacement_undo),
 ('case-storage-failure-remains-visible-and-exportable',storage_warning)]
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
            try:
                check(page);assert not errors,errors
            except Exception as error:
                try:page.screenshot(path=str(args.output/(name+'-failure.png')),full_page=True)
                except Exception:pass
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
