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
p.add_argument('--probe-only',action='store_true',help='Capture reversible WebKit layout probes only; never substitutes for the regression suite')
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
    if bounds['scroll']>bounds['width']+1:
        # Keep the original failure. Temporary browser-only probes isolate native
        # layout boxes, then restore every style; they never turn overflow PASS.
        bounds['diagnostic']=page.evaluate('''() => {
          const label=e=>e.tagName+(e.id?'#'+e.id:'')+'.'+String(e.className?.baseVal??e.className??'').replaceAll(' ','.');
          const nodes=[...document.querySelectorAll('body *')];
          const widths=nodes.map(e=>{const r=e.getBoundingClientRect(),s=getComputedStyle(e);return {node:label(e),client:e.clientWidth,scroll:e.scrollWidth,left:r.left,right:r.right,width:r.width,display:s.display,overflow:s.overflowX};}).filter(x=>x.scroll>x.client+1).slice(0,35);
          const ranges=[],walker=document.createTreeWalker(document.body,NodeFilter.SHOW_TEXT);
          while(walker.nextNode()){const n=walker.currentNode;if(!n.textContent.trim())continue;const range=document.createRange();range.selectNodeContents(n);const r=range.getBoundingClientRect();if(r.width&&r.height&&(r.right>innerWidth+1||r.left< -1))ranges.push({parent:label(n.parentElement),text:n.textContent.slice(0,160),left:r.left,right:r.right,top:r.top});}
          const pseudo=[];for(const e of nodes)for(const kind of ['::before','::after']){const s=getComputedStyle(e,kind);if(s.content&&!['none','normal','""'].includes(s.content))pseudo.push({node:label(e),kind,content:s.content,width:s.width,position:s.position,left:s.left,right:s.right,transform:s.transform});}
          const probes=[];for(const [name,css] of [
            ['caption-block-clip','caption.sr-only{display:block!important;clip-path:inset(50%)!important;margin:-1px!important}'],
            ['closed-details-grid','.wb-candidates:not([open])>.wb-candidate-grid{display:none!important}'],
            ['native-select-grid','.wb-pair-select{display:grid!important;grid-template-columns:23px minmax(0,1fr)!important}']
          ]){const style=document.createElement('style');style.textContent=css;document.head.append(style);probes.push({name,scroll:document.documentElement.scrollWidth});style.remove();}
          return {widths,ranges:ranges.slice(0,30),pseudo:pseudo.slice(0,20),probes,restoredScroll:document.documentElement.scrollWidth};
        }''')
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
            page.set_viewport_size({'width':width,'height':height});page.wait_for_timeout(100)
            page.evaluate('() => { scrollTo(0,0); return new Promise(resolve=>requestAnimationFrame(()=>requestAnimationFrame(resolve))); }')
            no_overflow(page)
            expect(page.get_by_test_id('wb-pair-a')).to_be_visible();expect(page.get_by_test_id('wb-pair-b')).to_be_visible()
            first=page.get_by_test_id('comparison-workbench').locator('tbody tr[data-row]:visible').first
            expect(first).to_be_visible();box=first.bounding_box();assert 0<=box['y']<height,{'brand':brand,'width':width,'first_parameter_y':box['y']}
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
            page.evaluate('() => { scrollTo(0,0); return new Promise(resolve=>requestAnimationFrame(()=>requestAnimationFrame(resolve))); }')
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


def layout_probe(page):
    seed(page,state(True))
    page.set_viewport_size({'width':320,'height':844})
    settle="() => { scrollTo(0,0); return new Promise(resolve=>requestAnimationFrame(()=>requestAnimationFrame(resolve))); }"
    page.evaluate(settle)
    inspect="""() => {
      const read=e=>{const r=e.getBoundingClientRect(),s=getComputedStyle(e);return {tag:e.tagName,className:e.className,testid:e.dataset.testid,text:e.tagName==='SELECT'?e.selectedOptions[0]?.textContent:e.textContent.slice(0,60),left:r.left,right:r.right,width:r.width,client:e.clientWidth,scroll:e.scrollWidth,css:Object.fromEntries(['display','position','left','right','top','width','minWidth','maxWidth','boxSizing','overflowX','clip','clipPath','appearance','gridTemplateColumns','gap','paddingLeft','paddingRight'].map(k=>[k,s[k]]))};};
      return {viewport:innerWidth,pageScroll:document.documentElement.scrollWidth,controls:read(document.querySelector('.wb-pair-controls')),labels:[...document.querySelectorAll('.wb-pair-select')].map(e=>({self:read(e),children:[...e.children].map(read)}))};
    }"""
    original=page.evaluate(inspect)
    page.reload(wait_until='networkidle');page.evaluate(settle)
    fresh_320=page.evaluate(inspect)
    page.set_viewport_size({'width':1440,'height':900});page.evaluate(settle)
    page.set_viewport_size({'width':320,'height':844});page.evaluate(settle)
    resized_again=page.evaluate(inspect)
    probes=[]
    changes=[
      ('select-display-none','.wb-pair-select select{display:none!important}'),
      ('hidden-label-display-none','.wb-pair-select>.sr-only{display:none!important}'),
      ('hidden-label-explicit-origin','.wb-pair-select{position:relative!important}.wb-pair-select>.sr-only{left:0!important;top:0!important}'),
      ('label-relative-only','.wb-pair-select{position:relative!important}'),
      ('native-appearance-none','.wb-pair-select select{appearance:none!important;-webkit-appearance:none!important}'),
      ('select-fixed-119px','.wb-pair-select select{width:119px!important;min-width:0!important;max-width:119px!important}'),
      ('select-zero-min-percent','.wb-pair-select select{width:0!important;min-width:100%!important}'),
      ('select-auto-grid-stretch','.wb-pair-select select{width:auto!important;justify-self:stretch!important}'),
      ('select-inline-block','.wb-pair-select select{display:block!important}'),
      ('badge-display-none','.wb-pair-select>[aria-hidden]{display:none!important}'),
    ]
    for name,css in changes:
        style=page.add_style_tag(content=css)
        page.evaluate(settle)
        measured=page.evaluate(inspect)
        style.evaluate('(element)=>element.remove()')
        page.evaluate(settle)
        restored=page.evaluate('document.documentElement.scrollWidth')
        probes.append({'name':name,'css':css,'measurement':measured,'restored_page_scroll':restored})
        print('LAYOUT_PROBE',name,'page',measured['pageScroll'],'labels',[x['self']['scroll'] for x in measured['labels']],'restored',restored,flush=True)
    results['layout_probe']={'interpretation':'Diagnostic observations only. Every temporary stylesheet is removed; regression status is reported by the separate full suite.','original':original,'fresh_320':fresh_320,'resized_again':resized_again,'probes':probes}
    page.screenshot(path=str(a.output/'restored-320.png'),full_page=True)
    doubled=page.evaluate('''() => {
      const nodes=[...document.querySelectorAll('body,body *')],sizes=nodes.map(e=>parseFloat(getComputedStyle(e).fontSize));
      const cell=document.querySelector('.wb-pair tbody td'),before=parseFloat(getComputedStyle(cell).fontSize);
      nodes.forEach((e,i)=>e.style.setProperty('font-size',sizes[i]*2+'px','important'));
      return {before,after:parseFloat(getComputedStyle(cell).fontSize)};
    }''')
    assert abs(doubled['after']-doubled['before']*2)<0.1,doubled
    inspect_text200='''() => {
      const report=('''+inspect+''')();
      const read=e=>{const r=e.getBoundingClientRect(),s=getComputedStyle(e);return {tag:e.tagName,className:e.className,testid:e.dataset.testid,text:e.tagName==='SELECT'?e.selectedOptions[0]?.textContent:e.textContent.slice(0,80),left:r.left,right:r.right,top:r.top,width:r.width,height:r.height,client:e.clientWidth,scroll:e.scrollWidth,css:Object.fromEntries(['fontSize','display','position','width','minWidth','maxWidth','overflowX','overflowWrap','whiteSpace','textOverflow','appearance','contain','gridTemplateColumns','justifySelf','paddingLeft','paddingRight'].map(k=>[k,s[k]]))};};
      return {...report,heading:[...document.querySelectorAll('.wb-heading,.wb-heading>div,#wb-title,.wb-heading-side>*')].map(read),nativeControls:[...document.querySelectorAll('.wb-toolbar .wb-field,.comparison-workbench select,.comparison-workbench input')].filter(e=>e.getClientRects().length).map(read)};
    }'''
    page.evaluate(settle);enlarged_original=page.evaluate(inspect_text200);enlarged_probes=[]
    enlarged_changes=[
      ('all-select-appearance-none','.comparison-workbench select{appearance:none!important;-webkit-appearance:none!important}'),
      ('all-select-overflow-ellipsis','.comparison-workbench select{overflow:hidden!important;text-overflow:ellipsis!important}'),
      ('all-select-auto-stretch','.comparison-workbench select{width:auto!important;justify-self:stretch!important}'),
      ('all-select-zero-min-percent','.comparison-workbench select{width:0!important;min-width:100%!important;max-width:100%!important}'),
      ('all-select-inline-size-containment','.comparison-workbench select{contain:inline-size!important}'),
      ('controls-wrapper-clip-diagnostic','.wb-field,.wb-pair-select{overflow:clip!important}'),
      ('heading-wrap-anywhere','.wb-heading h1,.wb-heading-side{overflow-wrap:anywhere!important}'),
      ('appearance-none-and-heading-wrap','.comparison-workbench select{appearance:none!important;-webkit-appearance:none!important}.wb-heading h1,.wb-heading-side{overflow-wrap:anywhere!important}'),
      ('select-overflow-and-heading-wrap','.comparison-workbench select{overflow:hidden!important;text-overflow:ellipsis!important}.wb-heading h1,.wb-heading-side{overflow-wrap:anywhere!important}'),
      ('wrapper-clip-and-heading-wrap-diagnostic','.wb-field,.wb-pair-select{overflow:clip!important}.wb-heading h1,.wb-heading-side{overflow-wrap:anywhere!important}'),
    ]
    print('TEXT200_LAYOUT_PROBE','original','page',enlarged_original['pageScroll'],flush=True)
    for name,css in enlarged_changes:
        style=page.add_style_tag(content=css);page.evaluate(settle);measured=page.evaluate(inspect_text200)
        style.evaluate('(element)=>element.remove()');page.evaluate(settle)
        restored=page.evaluate('document.documentElement.scrollWidth')
        enlarged_probes.append({'name':name,'css':css,'measurement':measured,'restored_page_scroll':restored})
        print('TEXT200_LAYOUT_PROBE',name,'page',measured['pageScroll'],'native',[x['scroll'] for x in measured['nativeControls']],'restored',restored,flush=True)
    results['layout_probe']['text_200']={'actual_doubled_sizes':doubled,'original':enlarged_original,'probes':enlarged_probes}
    page.screenshot(path=str(a.output/'restored-320-text-200.png'),full_page=True)


def interaction_paint(page,element):
    # Exercise the real 150ms transition, then inspect the painted frame.
    page.wait_for_timeout(180)
    page.evaluate('() => new Promise(resolve=>requestAnimationFrame(()=>requestAnimationFrame(resolve)))')
    return element.evaluate('''e => {const s=getComputedStyle(e);return Object.fromEntries(
      ['backgroundColor','color','borderTopColor','boxShadow','filter','outlineStyle','outlineWidth',
       'textDecorationLine','textDecorationColor','opacity','cursor','transitionDuration'].map(k=>[k,s[k]]));}''')


def interaction_bounds(element):
    return element.evaluate('''target => {
      const rect=e=>{const r=e.getBoundingClientRect();return {x:r.x,y:r.y,width:r.width,height:r.height};};
      const landmarks=[...document.querySelectorAll('.product,.wb-heading,.wb-toolbar,.wb-pair-controls,.wb-candidate-grid article,.wb-results article,.wb-table-wrap,.wb-footer,.research-global')].filter(e=>e.getClientRects().length);
      return {target:rect(target),landmarks:landmarks.map((e,i)=>({key:i+':'+e.tagName+':'+e.className+':'+(e.dataset.testid||''),rect:rect(e)})),scrollWidth:document.documentElement.scrollWidth};
    }''')


def stable_interaction_bounds(before,after,label):
    assert before['scrollWidth']==after['scrollWidth'],{'target':label,'before':before,'after':after}
    assert [e['key'] for e in before['landmarks']]==[e['key'] for e in after['landmarks']],label
    pairs=[('target',before['target'],after['target'])]+[(b['key'],b['rect'],c['rect']) for b,c in zip(before['landmarks'],after['landmarks'])]
    for name,b,c in pairs:
        assert all(abs(b[k]-c[k])<=0.5 for k in ['x','y','width','height']),{'interaction':label,'element':name,'before':b,'after':c}


def hover_interaction(page,element,brand,label):
    element.scroll_into_view_if_needed();page.mouse.move(1,1)
    page.evaluate('() => document.activeElement?.blur()')
    before=interaction_paint(page,element);bounds=interaction_bounds(element)
    element.hover();after=interaction_paint(page,element)
    assert element.evaluate('e=>e.matches(":hover")'),label
    changed={k:{'before':before[k],'hover':after[k]} for k in ['backgroundColor','color','borderTopColor','boxShadow','filter','textDecorationLine','textDecorationColor'] if before[k]!=after[k]}
    assert changed,{'brand':brand,'target':label,'before':before,'hover':after}
    stable_interaction_bounds(bounds,interaction_bounds(element),brand+':hover:'+label)
    results.setdefault('interaction_evidence',[]).append({'brand':brand,'device':'desktop','target':label,'hover_changed':changed,'stable_bounds':bounds['target'],'stable_landmarks':len(bounds['landmarks'])})
    return before


def disabled_interaction(page,element,touch=False):
    expect(element).to_be_disabled();element.scroll_into_view_if_needed()
    before={'selection':selected(page),'pair':pair(page),'cart':stored(page)['cart'],'message':page.locator('.wb-action-status').inner_text()}
    box=element.bounding_box();assert box and box['width']>0 and box['height']>0
    if touch:page.touchscreen.tap(box['x']+box['width']/2,box['y']+box['height']/2)
    else:page.mouse.click(box['x']+box['width']/2,box['y']+box['height']/2)
    paint=interaction_paint(page,element)
    assert paint['cursor']=='not-allowed' and paint['boxShadow']=='none' and paint['filter']=='none',paint
    assert {'selection':selected(page),'pair':pair(page),'cart':stored(page)['cart'],'message':page.locator('.wb-action-status').inner_text()}==before


def interaction_feedback(page,brand):
    status=page.locator('.wb-action-status');original=stored(page)
    page.get_by_test_id('wb-add').click();page.get_by_test_id('wb-search').fill(by_id[ids[3]]['sku'])
    page.get_by_test_id('wb-add-'+ids[3]).click()
    expect(status).to_have_text(by_id[ids[3]]['name']+': додано до порівняння.')
    expect(page.get_by_test_id('wb-result-'+ids[3])).to_have_attribute('data-selected','true')
    disabled_interaction(page,page.get_by_test_id('wb-add-'+ids[3]))
    page.mouse.move(1,1);page.evaluate('() => document.activeElement?.blur()')
    chosen=interaction_paint(page,page.get_by_test_id('wb-result-'+ids[3]))
    active=interaction_paint(page,page.get_by_test_id('wb-candidate-'+ids[0]))
    assert chosen['backgroundColor']==active['backgroundColor'],{'result':chosen,'active_pair':active}
    page.locator('.wb-discovery-heading button').click()
    page.get_by_test_id('wb-remove-'+ids[2]).click()
    expect(status).to_have_text(by_id[ids[2]]['name']+': прибрано. Дію можна скасувати.')
    page.get_by_test_id('wb-undo').click();expect(status).to_have_text('Видаленого кандидата повернуто.')
    assert selected(page)==ids[:4] and pair(page)==ids[:2]
    disabled_interaction(page,page.locator('.wb-full').get_by_role('button',name='До кошика: '+by_id[ids[2]]['name'],exact=True))
    page.locator('.wb-full').get_by_role('button',name='До кошика: '+by_id[ids[0]]['name'],exact=True).click()
    expect(status).to_have_text(by_id[ids[0]]['name']+': додано 1 '+by_id[ids[0]]['unit']+' до поточного кошика.')
    cart={**original['cart'],ids[0]:1};assert stored(page)['cart']==cart
    # Block only this test's state write. A changed pair must remain visibly in
    # memory, with exact failure feedback and no false success or stored change.
    persisted=page.evaluate('(key)=>localStorage.getItem(key)',key)
    page.evaluate('''key => {window.__interactionSetItem=Storage.prototype.setItem;Storage.prototype.setItem=function(k,v){if(this===localStorage&&k===key)throw new DOMException('Intentional interaction quota probe','QuotaExceededError');return window.__interactionSetItem.call(this,k,v);};}''',key)
    try:
        page.get_by_test_id('wb-pair-a').select_option(ids[2]);page.get_by_test_id('wb-save').click()
        expect(status).to_have_text('Вибір лише в пам’яті цієї сторінки. Перезавантаження може його втратити; збережіть JSON-експорт.')
        expect(page.get_by_test_id('wb-save-status')).to_have_text('Лише в пам’яті сторінки. Збережіть експорт.')
        assert 'Вибір збережено.' not in status.inner_text()
        assert page.evaluate('(key)=>localStorage.getItem(key)',key)==persisted
        assert pair(page)[0]==ids[2] and stored(page)['view']['pairs']['ups'][0]==ids[0]
        page.screenshot(path=str(a.output/f'{brand}-1440-interaction-save-failure.png'),full_page=True)
    finally:page.evaluate('() => {Storage.prototype.setItem=window.__interactionSetItem;delete window.__interactionSetItem;}')
    page.get_by_test_id('wb-pair-a').select_option(ids[0]);page.get_by_test_id('wb-save').click()
    expect(status).to_have_text('Вибір збережено. Він доступний після перезавантаження.')
    expect(page.get_by_test_id('wb-save-status')).to_have_text('Збережено в цьому браузері.')
    page.get_by_test_id('wb-shortlist').click()
    expect(page.locator('#modal')).to_be_visible()
    page.locator('#modal [data-action="comparison-save-to-project"][data-target="new"]').click()
    expect(page.locator('.science-project-line')).to_have_count(4)
    expect(page.locator('#toast')).to_have_text('Кандидатів збережено в проєкті.')
    project=stored(page)['science']['projects'][-1];assert project['candidates']==ids[:4]
    quantity=page.locator('[data-project-model="'+ids[0]+'"] input[data-field="quantity"]')
    quantity.fill('4');quantity.press('Tab')
    expect(quantity).to_have_value('4');expect(page.locator('#toast')).to_have_text(by_id[ids[0]]['name']+': 4 '+by_id[ids[0]]['unit']+'.')
    assert stored(page)['science']['projects'][-1]['quantities'][ids[0]]==4
    quantity.fill('0');quantity.press('Tab')
    expect(quantity).to_have_value('4');expect(quantity).to_have_attribute('aria-invalid','true')
    expect(page.locator('.quantity-error[role=status]')).to_have_text('Введіть ціле число від 1 до 999. Залишено попередню кількість.')
    assert stored(page)['science']['projects'][-1]['quantities'][ids[0]]==4
    quantity.fill('5');expect(quantity).not_to_have_attribute('aria-invalid','true')
    expect(page.locator('.quantity-error')).to_have_count(0);quantity.press('Tab')
    expect(page.locator('#toast')).to_have_text(by_id[ids[0]]['name']+': 5 '+by_id[ids[0]]['unit']+'.')
    with page.expect_download() as event:page.locator('[data-action="science-export"][data-format="json"]').click()
    export=a.output/f'{brand}-interaction-project.json';event.value.save_as(export);payload=json.loads(export.read_text())
    expect(page.locator('#toast')).to_have_text('Експорт поточного проєкту підготовлено.')
    current=stored(page);assert payload['format']=='perspektyva-project' and payload['version']==1 and payload['project']==current['science']['projects'][-1]
    assert current['cart']==cart and current['drafts']==original['drafts']


def touch_interactions(browser,brand,width):
    context=browser.new_context(viewport={'width':width,'height':844},has_touch=True,accept_downloads=True,reduced_motion='no-preference')
    context.set_default_timeout(12000);context.tracing.start(screenshots=True,snapshots=True,sources=True)
    errors=[]
    def local_only(route):
        if urlsplit(route.request.url).netloc==urlsplit(base).netloc:route.continue_()
        else:errors.append('Unexpected outbound request: '+route.request.url);route.abort()
    context.route('**/*',local_only);page=context.new_page();page.on('pageerror',lambda error:errors.append(str(error)))
    def control(element):
        expect(element).to_be_visible();element.scroll_into_view_if_needed();paint=interaction_paint(page,element);box=element.bounding_box()
        live_media=page.evaluate('() => ({hoverNone:matchMedia("(hover:none)").matches,coarse:matchMedia("(pointer:coarse)").matches})')
        assert live_media['hoverNone'] and live_media['coarse'],{'brand':brand,'width':width,'control':element.inner_text(),'media':live_media}
        assert box and box['height']>=43.5 and float(paint['opacity'])>0,{'brand':brand,'width':width,'control':element.get_attribute('data-testid'),'bounds':box,'paint':paint,'media':live_media}
        assert element.evaluate('e=>{const r=e.getBoundingClientRect(),p=document.elementFromPoint(r.x+r.width/2,r.y+r.height/2);return !!p&&(e===p||e.contains(p));}'),element.inner_text()
    try:
        initial=state(True);initial['compareByGroup']['ups']=ids[:3]
        seed(page,initial,demo+f'#/{brand}/compare?experience=modern')
        media=page.evaluate('() => ({touch:navigator.maxTouchPoints,hoverNone:matchMedia("(hover:none)").matches,coarse:matchMedia("(pointer:coarse)").matches})')
        # Firefox's has_touch emulation changes input/media while preserving the
        # host's maxTouchPoints. Require real touch delivery below in every engine.
        assert media['hoverNone'] and media['coarse'],media
        page.evaluate('() => {window.__interactionTouchStarts=0;document.addEventListener("touchstart",()=>window.__interactionTouchStarts++,{passive:true});}')
        no_overflow(page);expect(page.get_by_test_id('wb-pair-a')).to_be_visible();expect(page.get_by_test_id('wb-pair-b')).to_be_visible()
        summary=page.locator('.wb-candidates > summary');control(summary);summary.tap()
        media['delivered_touchstarts']=page.evaluate('window.__interactionTouchStarts')
        assert media['delivered_touchstarts']>0,media
        for pid in ids[:3]:
            for action in ['replace','remove']:control(page.get_by_test_id('wb-'+action+'-'+pid))
        # Chromium full-page capture changes device metrics and can clear its
        # touch media. Viewport capture preserves the device used by real taps.
        page.evaluate('() => scrollTo(0,0)');page.screenshot(path=str(a.output/f'{brand}-{width}-interaction-touch-candidates.png'))
        page.get_by_test_id('wb-replace-'+ids[0]).tap();expect(page.get_by_test_id('wb-replace-target')).to_have_value(ids[0])
        control(page.locator('.wb-discovery-heading button'));page.locator('.wb-discovery-heading button').tap()
        page.get_by_test_id('wb-remove-'+ids[2]).tap()
        expect(page.locator('.wb-action-status')).to_have_text(by_id[ids[2]]['name']+': прибрано. Дію можна скасувати.')
        control(page.get_by_test_id('wb-undo'));page.get_by_test_id('wb-undo').tap()
        expect(page.locator('.wb-action-status')).to_have_text('Видаленого кандидата повернуто.')
        control(page.get_by_test_id('wb-add'));page.get_by_test_id('wb-add').tap();page.get_by_test_id('wb-search').fill(by_id[ids[3]]['sku'])
        control(page.get_by_test_id('wb-add-'+ids[3]));page.get_by_test_id('wb-add-'+ids[3]).tap()
        expect(page.locator('.wb-action-status')).to_have_text(by_id[ids[3]]['name']+': додано до порівняння.')
        expect(page.get_by_test_id('wb-result-'+ids[3])).to_have_attribute('data-selected','true')
        page.locator('.wb-discovery-heading button').tap()
        assert selected(page)==ids[:4] and pair(page)==ids[:2]
        expect(page.get_by_test_id('wb-candidate-'+ids[0])).to_have_attribute('data-pair','A')
        expect(page.get_by_test_id('wb-candidate-'+ids[0]).locator('.wb-candidate-pair')).to_have_text('A · активна пара')
        page.get_by_test_id('wb-pair-b').select_option(ids[2])
        disabled_interaction(page,page.locator('.wb-pair').get_by_role('button',name='До кошика: '+by_id[ids[2]]['name'],exact=True),touch=True)
        page.get_by_test_id('wb-pair-b').select_option(ids[1])
        control(page.get_by_test_id('wb-save'));page.get_by_test_id('wb-save').tap()
        expect(page.locator('.wb-action-status')).to_have_text('Вибір збережено. Він доступний після перезавантаження.')
        control(page.get_by_test_id('wb-shortlist'));page.get_by_test_id('wb-shortlist').tap();expect(page.locator('#modal')).to_be_visible()
        page.locator('#modal [data-action="close"]').tap()
        summary.tap();page.evaluate('() => scrollTo(0,0)');no_overflow(page)
        first=page.locator('.wb-pair tbody tr[data-row]').first;box=first.bounding_box();assert box and 0<=box['y']<844,{'brand':brand,'width':width,'first_parameter':box}
        page.screenshot(path=str(a.output/f'{brand}-{width}-interaction-touch.png'))
        page.screenshot(path=str(a.output/f'{brand}-{width}-interaction-touch-viewport.png'))
        assert not errors,errors
        results.setdefault('interaction_evidence',[]).append({'brand':brand,'device':'touch','width':width,'media':media,'visible_actions':['replace','remove','undo','add','save','shortlist'],'first_parameter_y':box['y']})
    except Exception:
        page.screenshot(path=str(a.output/f'{brand}-{width}-interaction-touch-failure.png'),full_page=True)
        context.tracing.stop(path=str(a.output/f'{brand}-{width}-interaction-touch.zip'));raise
    else:context.tracing.stop()
    finally:context.close()


def actual_interactions(page):
    page.emulate_media(reduced_motion='no-preference')
    assert page.evaluate('() => matchMedia("(hover:hover) and (pointer:fine)").matches')
    for brand in ['asp','ng']:
        seed(page,state(),demo+f'#/{brand}/compare?experience=modern')
        page.goto(demo+f'#/{brand}/catalog?cat=ups',wait_until='networkidle')
        card=page.locator('.product[data-product-id="'+ids[0]+'"]');expect(card).to_be_visible()
        hover_interaction(page,card,brand,'catalog-card')
        for selector,label in [('.favorite','catalog-favorite'),('.compare-toggle','catalog-compare'),('h3 a','catalog-model-link'),('.card-buttons .btn','catalog-button')]:
            hover_interaction(page,card.locator(selector).first,brand,label)
        compare=card.locator('.compare-toggle');page.mouse.move(1,1);page.evaluate('() => document.activeElement?.blur()')
        unselected=interaction_paint(page,compare);compare.click();expect(compare).to_have_attribute('aria-pressed','true')
        page.mouse.move(1,1);page.evaluate('() => document.activeElement?.blur()');persistent=interaction_paint(page,compare)
        assert persistent['backgroundColor']!=unselected['backgroundColor'] and ids[0] in stored(page)['compareByGroup']['ups']
        expect(compare).to_contain_text('Додано')
        initial=state(True);initial['compareByGroup']['ups']=ids[:3]
        seed(page,initial,demo+f'#/{brand}/compare?experience=modern')
        disabled_interaction(page,page.get_by_test_id('wb-undo'))
        hover_interaction(page,page.get_by_test_id('wb-add'),brand,'primary-button')
        primary=page.get_by_test_id('wb-add');before=interaction_paint(page,primary);bounds=interaction_bounds(primary);box=primary.bounding_box()
        page.mouse.move(box['x']+box['width']/2,box['y']+box['height']/2);page.mouse.down()
        try:
            active=interaction_paint(page,primary);assert primary.evaluate('e=>e.matches(":active")')
            assert active['backgroundColor']!=before['backgroundColor'] or active['boxShadow']!=before['boxShadow'],{'normal':before,'active':active}
            stable_interaction_bounds(bounds,interaction_bounds(primary),brand+':active:primary-button')
        finally:page.mouse.move(1,1);page.mouse.up()
        for element,label in [(page.get_by_test_id('wb-save'),'secondary-button'),(page.get_by_test_id('wb-group'),'category-select'),(page.get_by_test_id('wb-candidate-'+ids[0]),'selected-candidate'),(page.get_by_test_id('wb-candidate-'+ids[2]),'candidate'),(page.get_by_test_id('wb-replace-'+ids[0]),'candidate-action'),(page.locator('.wb-full .wb-model-title').first,'table-model-button')]:
            hover_interaction(page,element,brand,label)
        page.get_by_test_id('wb-add').click();page.get_by_test_id('wb-search').fill(by_id[ids[3]]['sku'])
        for element,label in [(page.get_by_test_id('wb-result-'+ids[3]),'search-result'),(page.get_by_test_id('wb-add-'+ids[3]),'search-add-button'),(page.get_by_test_id('wb-search'),'search-input')]:
            hover_interaction(page,element,brand,label)
        page.evaluate('() => scrollTo(0,0)');page.get_by_test_id('wb-add-'+ids[3]).hover();interaction_paint(page,page.get_by_test_id('wb-add-'+ids[3]))
        page.screenshot(path=str(a.output/f'{brand}-1440-interaction-hover.png'),full_page=True)
        page.locator('.wb-discovery-heading button').click();primary.scroll_into_view_if_needed();page.mouse.move(1,1)
        page.get_by_test_id('wb-group').focus();bounds=interaction_bounds(primary);page.keyboard.press('Tab');expect(primary).to_be_focused()
        focus=interaction_paint(page,primary);assert primary.evaluate('e=>e.matches(":focus-visible")') and focus['outlineStyle']!='none' and float(focus['outlineWidth'].replace('px',''))>=3,focus
        stable_interaction_bounds(bounds,interaction_bounds(primary),brand+':keyboard-focus')
        page.keyboard.press('Enter');expect(page.get_by_test_id('wb-search')).to_be_focused()
        page.keyboard.press('Shift+Tab');expect(page.locator('.wb-discovery-heading button')).to_be_focused()
        page.keyboard.press('Enter');expect(primary).to_be_focused();expect(primary).to_have_attribute('aria-expanded','false')
        page.emulate_media(reduced_motion='reduce');assert interaction_paint(page,primary)['transitionDuration']=='0s'
        page.emulate_media(reduced_motion='no-preference')
        interaction_feedback(page,brand)
    for brand in ['asp','ng']:
        for width in [390,320]:touch_interactions(page.context.browser,brand,width)


checks=[('search-six-pair-replace-remove-undo-shortlist-save-reload',flow),('legacy-pilot-share-schema4-pair-drafts-back-forward',legacy_parity),
 ('both-brands-320-390-430-1440-keyboard-focus-text200',responsive_keyboard),('modern-case-memory-warning-export-isolation-return-history',case_isolation_failure),('full-capacity-undo-is-truthful-and-keeps-current-selection',undo_full_capacity),('actual-hover-active-focus-stable-bounds-feedback-and-fresh-touch-both-brands',actual_interactions)]
if a.probe_only:checks=[('reversible-native-layout-diagnostic',layout_probe)]
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
