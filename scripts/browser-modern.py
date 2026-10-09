#!/usr/bin/env python3
"""Actual HTTP/DOM parity checks for the optional React comparison workbench."""
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
from urllib.parse import urlsplit
from playwright.sync_api import sync_playwright, expect

p=argparse.ArgumentParser(description=__doc__)
p.add_argument('--url',required=True)
p.add_argument('--browser',choices=['chromium','firefox','webkit'],default='chromium')
p.add_argument('--executable')
p.add_argument('--output',type=Path,required=True)
a=p.parse_args();a.output.mkdir(parents=True,exist_ok=True)
root=Path(__file__).resolve().parents[1]
base=a.url.rstrip('/')+'/'
demo=base+'demo.html'; modern=demo+'#/asp/compare?experience=modern'
key='perspective-demo-v1'
fixture=json.loads(subprocess.check_output(['node','--input-type=module','-e',"import {products} from './data.js';import {initialState} from './logic.js';import {comparisonRows} from './src/domain/comparison.ts';console.log(JSON.stringify({products,state:initialState(),rows:comparisonRows(products.filter(p=>p.group==='ups').slice(0,6))}))"],cwd=root,text=True))
products=fixture['products'];by_id={p['id']:p for p in products};ids=[p['id'] for p in products if p['group']=='ups'][:7]
assert len(ids)==7
results={'schema':1,'commit':subprocess.check_output(['git','rev-parse','HEAD'],cwd=root,text=True).strip(),'started_at_utc':datetime.now(timezone.utc).isoformat(),
 'environment':{'platform':platform.platform(),'python':platform.python_version(),'playwright':importlib.metadata.version('playwright')},
 'browser':a.browser,'command':['python',*sys.argv],'url':base,'checks':[],'not_run':['stable Safari','physical iPhone','native zoom','VoiceOver']}


def state(selected=False):
    s=json.loads(json.dumps(fixture['state']));s['view']['group']='ups'
    s['cart']={'c04':2,'u02':3};s['drafts']['u02']={'purpose':'Сумісність','quantity':'2','question':'Особиста чернетка: 24 В, D1 — не втратити.'}
    if selected:s['compareByGroup']['ups']=ids[:6];s['view']['pairs']['ups']=ids[:2]
    return s


def seed(page,s,route=modern):
    page.goto(base+'reports/ASP24_Review.html',wait_until='networkidle')
    page.evaluate('([key,state])=>localStorage.setItem(key,JSON.stringify(state))',[key,s])
    page.goto(route,wait_until='networkidle');expect(page.get_by_test_id('comparison-workbench')).to_be_visible()


def stored(page):return page.evaluate('(key)=>JSON.parse(localStorage.getItem(key))',key)
def selected(page):return page.locator('[data-testid^="wb-candidate-"]').evaluate_all('(els)=>els.map(el=>el.dataset.testid.slice("wb-candidate-".length))')
def pair(page):return [page.get_by_test_id('wb-pair-a').input_value(),page.get_by_test_id('wb-pair-b').input_value()]
def no_overflow(page):
    bounds=page.evaluate('''() => ({width:innerWidth,scroll:document.documentElement.scrollWidth,
      overflow:[...document.querySelectorAll('body *')].filter(e=>e.getClientRects().length).map(e=>{const r=e.getBoundingClientRect();return {tag:e.tagName,id:e.id,class:e.className,testid:e.dataset.testid,left:r.left,right:r.right,width:r.width,scroll:e.scrollWidth};}).filter(e=>e.right>innerWidth+1||e.left< -1).slice(0,25)})''')
    assert bounds['scroll']<=bounds['width']+1,bounds

def search_add(page,pid):
    field=page.get_by_test_id('wb-search')
    if not field.is_visible():page.get_by_test_id('wb-add').click()
    field.fill(by_id[pid]['sku'])
    expect(page.get_by_test_id('wb-result-'+pid)).to_be_visible()
    page.get_by_test_id('wb-add-'+pid).click()
    expect(page.get_by_test_id('wb-candidate-'+pid)).to_be_visible()


def flow(page):
    initial=state();seed(page,initial)
    expect(page.get_by_test_id('wb-group')).to_have_value('ups')
    for pid in ids[:6]:search_add(page,pid)
    assert selected(page)==ids[:6]
    page.get_by_test_id('wb-pair-a').select_option(ids[4]);page.get_by_test_id('wb-pair-b').select_option(ids[5])
    assert pair(page)==ids[4:6]
    page.get_by_test_id('wb-remove-'+ids[4]).click();expect(page.get_by_test_id('wb-candidate-'+ids[4])).to_have_count(0)
    page.get_by_test_id('wb-undo').click();assert selected(page)==ids[:6] and pair(page)==ids[4:6]
    page.get_by_test_id('wb-replace-'+ids[4]).click();search_add(page,ids[6])
    expected=[ids[6] if x==ids[4] else x for x in ids[:6]]
    assert selected(page)==expected and pair(page)==[ids[6],ids[5]]
    page.get_by_test_id('wb-differences').check()
    page.get_by_test_id('wb-save').click();expect(page.get_by_test_id('wb-save-status')).to_contain_text(re.compile('збереж',re.I))
    before=stored(page);assert before['version']==4 and before['cart']==initial['cart'] and before['drafts']==initial['drafts']
    page.reload(wait_until='networkidle');assert selected(page)==expected and pair(page)==[ids[6],ids[5]]
    expect(page.get_by_test_id('wb-differences')).to_be_checked()
    page.get_by_test_id('wb-shortlist').click()
    page.locator('#modal [data-action="comparison-save-to-project"][data-target="new"]').click()
    expect(page.locator('.science-project-line')).to_have_count(6)
    saved=stored(page);project=saved['science']['projects'][-1]
    assert project['candidates']==expected and saved['cart']==initial['cart'] and saved['drafts']==initial['drafts']
    assert all(project['quantities'][pid]==1 for pid in expected)
    page.goto(modern,wait_until='networkidle');assert selected(page)==expected and pair(page)==[ids[6],ids[5]]
    page.reload(wait_until='networkidle');assert stored(page)['science']['projects'][-1]==project


def legacy_parity(page):
    initial=state(True);seed(page,initial)
    page.get_by_test_id('wb-pair-a').select_option(ids[4]);page.get_by_test_id('wb-pair-b').select_option(ids[5])
    page.get_by_test_id('wb-differences').check()
    expected=stored(page)
    page.goto(demo+'#/asp/compare',wait_until='networkidle')
    assert page.locator('.research-desktop [data-compare-id]').evaluate_all('(els)=>els.map(el=>el.dataset.compareId)')==ids[:6]
    assert page.locator('.research-mobile [data-compare-id]').evaluate_all('(els)=>els.map(el=>el.dataset.compareId)')==ids[4:6]
    expect(page.locator('#differences')).to_be_checked()
    page.locator('#differences').uncheck()
    page.goto(modern,wait_until='networkidle');assert selected(page)==ids[:6] and pair(page)==ids[4:6]
    expect(page.get_by_test_id('wb-differences')).not_to_be_checked()
    actual=stored(page)
    for field in ['cart','drafts','compareByGroup','science']:assert actual[field]==expected[field],field
    # Back/Forward resolves the actual legacy/pilot URL and retains the same state.
    page.go_back(wait_until='networkidle');expect(page.locator('#differences')).to_be_visible()
    page.go_forward(wait_until='networkidle');expect(page.get_by_test_id('comparison-workbench')).to_be_visible()
    assert selected(page)==ids[:6] and pair(page)==ids[4:6]


def responsive_keyboard(page):
    seed(page,state(True))
    for brand in ['asp','ng']:
        page.goto(demo+f'#/{brand}/compare?experience=modern',wait_until='networkidle')
        for width,height in [(320,844),(390,844),(430,844),(1440,900)]:
            page.set_viewport_size({'width':width,'height':height});page.wait_for_timeout(100);no_overflow(page)
            expect(page.get_by_test_id('wb-pair-a')).to_be_visible();expect(page.get_by_test_id('wb-pair-b')).to_be_visible()
            first=page.get_by_test_id('comparison-workbench').locator('tbody tr[data-row]:visible').first
            expect(first).to_be_visible();box=first.bounding_box();assert box['y']<height,{'brand':brand,'width':width,'first_parameter_y':box['y']}
            expected_cells={(row['key'],cell['productId']):cell['text'] for row in fixture['rows'] for cell in row['cells']}
            for row in page.get_by_test_id('comparison-workbench').locator('tbody tr[data-row]:visible').all():
                for cell in row.locator('td[data-product-id]').all():
                    assert cell.inner_text()==expected_cells[(row.get_attribute('data-row'),cell.get_attribute('data-product-id'))]
            page.screenshot(path=str(a.output/f'{brand}-{width}.png'),full_page=True)
            if width in [390,1440]:page.screenshot(path=str(a.output/f'{brand}-{width}-viewport.png'))
        page.set_viewport_size({'width':390,'height':844})
        page.get_by_test_id('wb-pair-a').focus();expect(page.get_by_test_id('wb-pair-a')).to_be_focused()
        page.keyboard.press('ArrowDown');page.keyboard.press('Tab')
        expect(page.get_by_test_id('wb-pair-b')).to_be_focused()
        # Walk the workbench through its explicit final Save control. A fixed Tab
        # count can legitimately leave the document for browser chrome after the
        # footer, especially when an unavailable product disables its cart button.
        visited=[]
        for _ in range(30):
            page.keyboard.press('Tab')
            focus=page.evaluate('''() => {const e=document.activeElement,s=getComputedStyle(e),r=e.getBoundingClientRect();return {testid:e.dataset.testid,insideWorkbench:!!e.closest('[data-testid=comparison-workbench]'),tag:e.tagName,name:e.getAttribute('aria-label')||e.labels?.[0]?.textContent||e.textContent||e.title,outline:s.outlineStyle,outlineWidth:s.outlineWidth,width:r.width,height:r.height};}''')
            assert focus['insideWorkbench'] and focus['tag']!='BODY' and focus['width']>0 and focus['height']>0,focus
            assert focus['name'].strip(),focus
            assert focus['outline']!='none' and float(focus['outlineWidth'].replace('px',''))>0,focus
            visited.append(focus.get('testid'))
            if focus.get('testid')=='wb-save':break
        assert visited[-1]=='wb-save' and 'wb-differences' in visited,visited
        # Double actual computed text, including explicit px sizes. Snapshot all
        # values before applying overrides to avoid inherited compound doubling.
        doubled=page.evaluate('''() => {
          const elements=[...document.querySelectorAll('body, body *')];
          const sizes=elements.map(e=>parseFloat(getComputedStyle(e).fontSize));
          const cell=document.querySelector('.wb-pair tbody td');
          const before=parseFloat(getComputedStyle(cell).fontSize);
          elements.forEach((e,i)=>e.style.setProperty('font-size',sizes[i]*2+'px','important'));
          return {before,after:parseFloat(getComputedStyle(cell).fontSize)};
        }''')
        assert abs(doubled['after']-doubled['before']*2)<0.1,doubled
        for width,height in [(320,844),(390,844),(430,844),(1440,900)]:
            page.set_viewport_size({'width':width,'height':height});page.wait_for_timeout(100);no_overflow(page)
            header_bounds=page.locator('.research-global').evaluate('''header => {
              const h=header.getBoundingClientRect();
              return [...header.querySelectorAll('a,button')].filter(e=>e.getClientRects().length).map(e=>{const r=e.getBoundingClientRect();return {text:e.textContent,top:r.top,bottom:r.bottom,headerTop:h.top,headerBottom:h.bottom};});
            }''')
            for control in header_bounds:
                assert control['top']>=-1 and control['top']>=control['headerTop']-1 and control['bottom']<=control['headerBottom']+1,control
            page.screenshot(path=str(a.output/f'{brand}-{width}-text-200.png'),full_page=True)
        page.reload(wait_until='networkidle')


def undo_full_capacity(page):
    seed(page,state(True))
    page.get_by_test_id('wb-remove-'+ids[4]).click()
    search_add(page,ids[6])
    before=selected(page);assert len(before)==6
    page.get_by_test_id('wb-undo').click()
    assert selected(page)==before
    expect(page.locator('.wb-action-status')).to_contain_text(re.compile('немає місця|не вдалося',re.I))
    assert 'повернуто' not in page.locator('.wb-action-status').inner_text().lower()
    page.reload(wait_until='networkidle');assert selected(page)==before


def case_isolation_failure(page):
    original=state(True);seed(page,original)
    page.goto(base+'reports/ASP24_Review.html#asp24-09',wait_until='networkidle')
    personal=page.evaluate('(key)=>localStorage.getItem(key)',key)
    case_key='asp24-nggroup-case:six-candidates:v1'
    page.add_init_script('''(() => {const original=Storage.prototype.setItem;Storage.prototype.setItem=function(key,value){if(this===sessionStorage&&key==='asp24-nggroup-case:six-candidates:v1')throw new DOMException('Intentional quota probe','QuotaExceededError');return original.call(this,key,value);};})();''')
    route=demo+'?case=six-candidates&v=1#/asp/compare?experience=modern'
    page.goto(route,wait_until='networkidle');expect(page.get_by_test_id('comparison-workbench')).to_be_visible()
    page.get_by_test_id('wb-pair-a').select_option('u03')
    page.get_by_test_id('wb-save').click()
    expect(page.get_by_test_id('wb-save-status')).to_contain_text('Лише в пам’яті')
    expect(page.locator('#case-storage-status')).to_contain_text(re.compile('перезавантаж',re.I))
    with page.expect_download() as event:page.locator('#case-export').click()
    path=a.output/'modern-memory-case-export.json';event.value.save_as(path);payload=json.loads(path.read_text())
    assert payload['state']['view']['pairs']['ups'][0]=='u03' and payload['stateSchemaVersion']==4
    assert page.evaluate('(key)=>localStorage.getItem(key)',key)==personal
    page.locator('.case-banner').get_by_role('link',name='Повернутися до розділу огляду',exact=True).click()
    page.wait_for_load_state('networkidle');assert page.url==base+'reports/ASP24_Review.html#asp24-09'
    page.go_back(wait_until='networkidle');expect(page.get_by_test_id('comparison-workbench')).to_be_visible()
    page.go_forward(wait_until='networkidle');assert page.url==base+'reports/ASP24_Review.html#asp24-09'
    assert page.evaluate('(key)=>localStorage.getItem(key)',key)==personal


checks=[('search-six-pair-replace-remove-undo-shortlist-save-reload',flow),('legacy-pilot-share-schema4-pair-drafts-back-forward',legacy_parity),
 ('both-brands-320-390-430-1440-keyboard-focus-text200',responsive_keyboard),('modern-case-memory-warning-export-isolation-return-history',case_isolation_failure),('full-capacity-undo-is-truthful-and-keeps-current-selection',undo_full_capacity)]
with sync_playwright() as pw:
    try:
        options={'chromium_sandbox':True} if a.browser=='chromium' else {}
        if a.executable:options['executable_path']=a.executable
        browser=getattr(pw,a.browser).launch(timeout=30000,**options)
    except Exception as error:results.update(status='BLOCKED',launch_error=str(error))
    else:
        results['browser_version']=browser.version
        for name,check in checks:
            context=browser.new_context(viewport={'width':1440,'height':900},accept_downloads=True,reduced_motion='reduce');context.set_default_timeout(12000)
            context.tracing.start(screenshots=True,snapshots=True,sources=True)
            errors=[]
            def local_only(route):
                if urlsplit(route.request.url).netloc==urlsplit(base).netloc:route.continue_()
                else:errors.append('Unexpected outbound request: '+route.request.url);route.abort()
            context.route('**/*',local_only);page=context.new_page();page.on('pageerror',lambda error:errors.append(str(error)))
            try:
                check(page);assert not errors,errors
            except Exception as error:
                try:page.screenshot(path=str(a.output/(name+'-failure.png')),full_page=True)
                except Exception:pass
                context.tracing.stop(path=str(a.output/(name+'.zip')))
                results['checks'].append({'name':name,'status':'FAIL','error':str(error),'traceback':traceback.format_exc(),'console_errors':errors})
                print('FAIL',name,error,flush=True)
            else:context.tracing.stop();results['checks'].append({'name':name,'status':'PASS'});print('PASS',name,flush=True)
            finally:context.close()
        browser.close();results['status']='FAIL' if any(c['status']=='FAIL' for c in results['checks']) else 'PASS'
results['completed_at_utc']=datetime.now(timezone.utc).isoformat()
(a.output/'results.json').write_text(json.dumps(results,ensure_ascii=False,indent=2)+'\n')
print(results['status'],a.output/'results.json',flush=True)
raise SystemExit(0 if results['status']=='PASS' else 2 if results['status']=='BLOCKED' else 1)
