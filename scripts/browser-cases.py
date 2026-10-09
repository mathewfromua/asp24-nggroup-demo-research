#!/usr/bin/env python3
"""Exercise the report/case contract against a built candidate over HTTP.

Requires publication.json from the report-demo-paths branch. Uses only synthetic
personal fixtures; no real records, outbound requests, or disabled sandbox.
"""
import argparse
from datetime import datetime, timezone
import importlib.metadata
import json
from pathlib import Path
import re
import subprocess
import traceback
from urllib.parse import urljoin, urlsplit
from playwright.sync_api import sync_playwright, expect

parser=argparse.ArgumentParser(description=__doc__)
parser.add_argument('--url',required=True)
parser.add_argument('--demo-path',default='demo.html')
parser.add_argument('--browser',choices=['chromium','firefox','webkit'],default='chromium')
parser.add_argument('--executable')
parser.add_argument('--output',type=Path,default=Path('/tmp/asp24-case-results'))
args=parser.parse_args()
root=Path(__file__).resolve().parents[1]
registry=json.loads((root/'publication.json').read_text())
base=args.url.rstrip('/')+'/'
demo=urljoin(base,args.demo_path)
origin=urlsplit(base).netloc
args.output.mkdir(parents=True,exist_ok=True)
key='perspective-demo-v1'
fixture=json.loads(subprocess.check_output(['node','--input-type=module','-e',"import {initialState} from './logic.js';import {normalizeScience,createProject} from './science.js';const s=initialState();s.cart={c02:4};s.favorites=['o01'];s.compareByGroup.optics=['o01','o03'];s.view.pairs.optics=['o03','o01'];s.drafts.u04={purpose:'Тест',quantity:'3',question:'Особиста синтетична чернетка'};s.listName='Особистий синтетичний список';s.note='Не змінювати під час прикладу';s.science=normalizeScience();createProject(s.science,{name:'Мій синтетичний проєкт',candidates:['c02','u04']},undefined,'2026-10-09T00:00:00.000Z');console.log(JSON.stringify(s));"],cwd=root,text=True))
results={'started_at_utc':datetime.now(timezone.utc).isoformat(),'commit':subprocess.check_output(['git','rev-parse','HEAD'],cwd=root,text=True).strip(),'browser':args.browser,'playwright':importlib.metadata.version('playwright'),'url':base,'checks':[],'not_run':['native browser zoom','physical Safari/iPhone/VoiceOver']}


def personal(page):
    return page.evaluate('(key)=>localStorage.getItem(key)',key)


def assert_personal(page,expected):
    assert personal(page)==expected, 'Opening or changing a case changed personal storage bytes'


def overflow(page):
    geometry=page.evaluate('({width:innerWidth,scroll:document.documentElement.scrollWidth})')
    assert geometry['scroll']<=geometry['width']+1,geometry


def assert_case(page,case,changed=False):
    expect(page.locator('.case-banner')).to_contain_text(case['title'])
    if case['caseId']=='six-candidates':
        ids=page.locator('.research-desktop [data-compare-id]').evaluate_all('(els)=>els.map(el=>el.dataset.compareId)')
        expected=['u01','u02','u03','u04','u05'] if changed else case['seed']['candidates']
        assert ids==expected
    elif case['caseId']=='unknown-and-difference':
        row=page.locator('.research-desktop [data-row="Маса"]')
        expect(row.locator('.difference-label')).to_have_text('Відмінність')
        expect(row.locator('.incomplete-label')).to_have_text('Неповні дані')
        expect(page.locator('.research-mobile [data-row="Маса"] .incomplete-label')).to_have_text('Неповні дані')
    elif case['caseId']=='two-reels':
        expect(page.locator('[data-quantity=c04]')).to_have_value('2')
        expect(page.locator('[data-cart-id=c04]')).to_contain_text('610 м')
        assert '16 950' in page.locator('.total strong').inner_text().replace('\xa0',' ')
    elif case['caseId']=='model-document':
        expect(page.locator('.document-page')).to_contain_text('DEMO-U02')
        expect(page.locator('a[href="#/ng/product/u02"]').first).to_be_visible()


def hub(page):
    requested=[];page.on('request',lambda request:requested.append(urlsplit(request.url).path))
    response=page.goto(base,wait_until='networkidle');assert response.status==200
    expect(page.locator('h1')).to_contain_text('ASP24 / NG Group')
    for report in ['ASP24','NGGroup']:
        expect(page.locator(f'a[href$="reports/{report}_Review.html"]')).to_be_visible()
        expect(page.locator(f'a[href$="reports/{report}_Review.pdf"]')).to_be_visible()
    assert not any(re.search(r'/assets/(app|data|catalog-expanded)-',path) for path in requested),requested
    for width in [320,390,430,1440]:
        page.set_viewport_size({'width':width,'height':900});overflow(page)
    page.set_viewport_size({'width':390,'height':844})
    page.add_style_tag(content='html{font-size:200% !important}body{font-size:200% !important}')
    overflow(page)
    # All historical hash URLs remain a real navigation to the same stable model.
    page.goto(base+'#/asp/product/u02',wait_until='networkidle')
    expect(page.locator('h1')).to_have_text('VOLTYN N36')
    assert urlsplit(page.url).path.endswith('demo.html') and urlsplit(page.url).fragment=='/asp/product/u02'


def make_case_check(case,filled):
    def check(page):
        report=base+f'reports/{case["reportId"]}_Review.html#{case["sectionId"]}'
        page.goto(report,wait_until='networkidle')
        if filled:page.evaluate('([key,state])=>localStorage.setItem(key,JSON.stringify(state))',[key,fixture])
        original=personal(page)
        section=page.locator('#'+case['sectionId']);expect(section).to_be_visible()
        entry=section.locator(f'a[href*="cases/{case["caseId"]}/"]').first
        expect(entry).to_be_visible();entry.click();page.wait_for_load_state('networkidle')
        expect(page.locator('h1')).to_have_text(case['title'])
        assert_personal(page,original)
        for width in [320,390,430,1440]:
            page.set_viewport_size({'width':width,'height':900});overflow(page)
        page.set_viewport_size({'width':390,'height':844})
        page.get_by_role('link',name='Відкрити приклад',exact=True).click();page.wait_for_load_state('networkidle')
        assert_case(page,case);assert_personal(page,original)
        # A storage event from the personal workspace must not replace case state.
        page.evaluate('([key,fixture])=>window.dispatchEvent(new StorageEvent("storage",{key,newValue:JSON.stringify(fixture),storageArea:localStorage}))',[key,fixture])
        assert_case(page,case);assert_personal(page,original)
        changed=case['caseId']=='six-candidates'
        if changed:page.locator('.research-mobile [data-action=remove-compare][data-id=u06]').click()
        assert_case(page,case,changed)
        page.reload(wait_until='networkidle');assert_case(page,case,changed);assert_personal(page,original)
        stored=page.evaluate('(key)=>sessionStorage.getItem(key)',f'asp24-nggroup-case:{case["caseId"]}:v{case["caseVersion"]}')
        assert stored is not None and json.loads(stored)['version']==4
        return_link=page.locator('.case-banner').get_by_role('link',name='Повернутися до розділу огляду',exact=True)
        assert return_link.get_attribute('href').endswith(f'reports/{case["reportId"]}_Review.html#{case["sectionId"]}')
        return_link.click();page.wait_for_load_state('networkidle')
        assert page.url==report;expect(page.locator('#'+case['sectionId'])).to_be_visible();assert_personal(page,original)
        page.go_back(wait_until='networkidle');assert_case(page,case,changed);assert_personal(page,original)
        page.go_forward(wait_until='networkidle');assert page.url==report;assert_personal(page,original)
        page.goto(demo+f'?case={case["caseId"]}&v={case["caseVersion"]}'+case['route'],wait_until='networkidle')
        assert_case(page,case,changed);assert_personal(page,original)
        page.locator('.case-banner').get_by_role('button',name='Почати приклад спочатку').click();page.wait_for_load_state('networkidle')
        assert_case(page,case);assert_personal(page,original)
    return check


def invalid_versions(page):
    page.goto(base+'reports/ASP24_Review.html',wait_until='networkidle')
    page.evaluate('([key,state])=>localStorage.setItem(key,JSON.stringify(state))',[key,fixture]);original=personal(page)
    for case_id,version in [('not-a-case','1'),('six-candidates','0'),('six-candidates','999')]:
        requested=[]
        listener=lambda request:requested.append(urlsplit(request.url).path)
        page.on('request',listener)
        page.goto(demo+f'?case={case_id}&v={version}',wait_until='networkidle')
        expect(page.locator('h1')).to_have_text('Ця версія прикладу недоступна')
        expect(page.get_by_role('link',name='Повернутися до огляду')).to_be_visible()
        assert page.locator('#app').inner_html()==''
        assert not any(re.search(r'/assets/app-',path) for path in requested),requested
        assert_personal(page,original);page.remove_listener('request',listener)


checks=[('static-hub-without-catalog-legacy-hash-reflow',hub)]
checks += [(f'{c["caseId"]}-read-case-return-'+('filled' if filled else 'clean'),make_case_check(c,filled)) for c in registry['cases'] for filled in [False,True]]
checks += [('invalid-id-old-unknown-version-no-app-no-personal-mutation',invalid_versions)]
with sync_playwright() as p:
    try:
        options={'chromium_sandbox':True} if args.browser=='chromium' else {}
        if args.executable:options['executable_path']=args.executable
        browser=getattr(p,args.browser).launch(timeout=30000,**options)
    except Exception as error:results.update(status='BLOCKED',launch_error=str(error))
    else:
        results['browser_version']=browser.version
        for name,check in checks:
            context=browser.new_context(viewport={'width':390,'height':844});context.set_default_timeout(12000)
            context.tracing.start(screenshots=True,snapshots=True,sources=True)
            errors=[]
            def local_only(route):
                if urlsplit(route.request.url).netloc==origin:route.continue_()
                else:errors.append('Unexpected outbound request: '+route.request.url);route.abort()
            context.route('**/*',local_only)
            page=context.new_page();page.on('pageerror',lambda error:errors.append(str(error)))
            try:
                check(page);assert not errors,errors
            except Exception as error:
                page.screenshot(path=str(args.output/(name+'.png')),full_page=True)
                context.tracing.stop(path=str(args.output/(name+'.zip')))
                results['checks'].append({'name':name,'status':'FAIL','error':str(error),'traceback':traceback.format_exc(),'console_errors':errors});print('FAIL',name,str(error),flush=True)
            else:
                context.tracing.stop();results['checks'].append({'name':name,'status':'PASS'});print('PASS',name,flush=True)
            finally:context.close()
        browser.close();results['status']='FAIL' if any(c['status']=='FAIL' for c in results['checks']) else 'PASS'
results['completed_at_utc']=datetime.now(timezone.utc).isoformat()
(args.output/'results.json').write_text(json.dumps(results,ensure_ascii=False,indent=2)+'\n')
print(results['status'],args.output/'results.json',flush=True)
raise SystemExit(0 if results['status']=='PASS' else 2 if results['status']=='BLOCKED' else 1)
