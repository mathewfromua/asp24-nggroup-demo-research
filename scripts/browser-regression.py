#!/usr/bin/env python3
"""Deterministic HTTP/DOM regression checks. Browser dependencies stay outside dist.

Run after build and preview. Example:
 python scripts/browser-regression.py --url http://127.0.0.1:8000/asp24-nggroup-demo-research/ --browser firefox
A browser launch failure is BLOCKED, never PASS. No sandbox bypass flags are used.
"""
import argparse
from datetime import datetime, timezone
import importlib.metadata
import json
from pathlib import Path
import subprocess
import traceback
from urllib.parse import urljoin, urlsplit
from playwright.sync_api import sync_playwright, expect

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--url', default='http://127.0.0.1:8000/asp24-nggroup-demo-research/')
parser.add_argument('--demo-path', default='')
parser.add_argument('--browser', choices=['chromium', 'firefox', 'webkit'], default='chromium')
parser.add_argument('--executable')
parser.add_argument('--output', type=Path, default=Path('/tmp/asp24-browser-results'))
args = parser.parse_args()
args.output.mkdir(parents=True, exist_ok=True)
root = Path(__file__).resolve().parents[1]
base = args.url.rstrip('/') + '/'
demo = urljoin(base, args.demo_path)
origin = urlsplit(base).netloc
fixture = json.loads(subprocess.check_output(['node', '--input-type=module', '-e', "import {products} from './data.js';import {initialState} from './logic.js';console.log(JSON.stringify({products,state:initialState()}))"], cwd=root, text=True))
products = fixture['products']
by_id = {p['id']: p for p in products}
key = 'perspective-demo-v1'
results = {'started_at_utc': datetime.now(timezone.utc).isoformat(), 'commit': subprocess.check_output(['git','rev-parse','HEAD'],cwd=root,text=True).strip(), 'working_tree_dirty': bool(subprocess.check_output(['git','status','--porcelain'],cwd=root,text=True).strip()), 'browser': args.browser, 'playwright': importlib.metadata.version('playwright'), 'url': base, 'demo_path': args.demo_path, 'checks': [], 'not_run': ['stable Safari/macOS', 'physical iPhone / native keyboard', 'VoiceOver', 'real browser zoom (CSS text resize is tested separately)', 'PDF viewer accessibility / PDF-UA']}


def fresh_state():
    return json.loads(json.dumps(fixture['state']))


def project(ids, name='Контрольний проєкт'):
    return {'id':'project-1','name':name,'note':'','candidates':ids,'chosen':[], 'quantities':{pid:1 for pid in ids},'references':[], 'createdAt':'2026-10-09T00:00:00.000Z','updatedAt':'2026-10-09T00:00:00.000Z'}


def science(proj):
    return {'version':1,'projects':[proj],'activeProjectId':proj['id'],'nextProjectSeq':2,'quarantine':[]}


def stored(page):
    return page.evaluate('(key)=>JSON.parse(localStorage.getItem(key))',key)


def seed(page, state, route='#/asp/catalog'):
    # Seed on a static document: an existing app writes its live state on pagehide.
    page.goto(base + 'reports/ASP24_Review.html', wait_until='networkidle')
    page.evaluate('([key,state])=>localStorage.setItem(key,JSON.stringify(state))',[key,state])
    page.goto(demo + route, wait_until='networkidle')
    page.reload(wait_until='networkidle')


def candidates(page):
    return page.locator('.research-desktop [data-compare-id]').evaluate_all('(els)=>els.map(el=>el.dataset.compareId)')


def pair(page):
    return page.locator('.research-mobile [data-compare-id]').evaluate_all('(els)=>els.map(el=>el.dataset.compareId)')


def overflow(page):
    dimensions=page.evaluate('({width:innerWidth,scroll:document.documentElement.scrollWidth})')
    assert dimensions['scroll'] <= dimensions['width'] + 1, dimensions


def exact_and_facets(page):
    seed(page,fresh_state())
    page.locator('#search-form input[name=q]').fill('DEMO-U02')
    page.locator('#search-form').evaluate('(form)=>form.requestSubmit()')
    expect(page.locator('.product')).to_have_count(1)
    expect(page.locator('.product')).to_have_attribute('data-product-id','u02')
    expect(page.locator('.exact')).to_have_text('Точний збіг')
    page.goto(demo+'#/asp/catalog?cat=ups&view=list',wait_until='networkidle')
    page.locator('[data-multi-filter=f0][value="18 Вт"]').check()
    page.locator('[data-multi-filter=f0][value="36 Вт"]').check()
    # Assert the displayed quantity matches the actual OR result through the source facet key.
    facet_key=next(k for k,v in by_id['u02']['props'].items() if v=='36 Вт')
    expected=[p['id'] for p in products if p['group']=='ups' and p['props'][facet_key] in ['18 Вт','36 Вт']]
    assert page.locator('.technical-item').evaluate_all('(els)=>els.map(el=>el.dataset.productId)')==expected[:24]
    page.locator('[data-action=remove-filter][data-value="18 Вт"]').click()
    assert page.locator('[data-multi-filter=f0][value="36 Вт"]').is_checked()
    assert not page.locator('[data-multi-filter=f0][value="18 Вт"]').is_checked()
    page.goto(demo+'#/asp/catalog?cat=ups&sort=price-down&view=list&page=2',wait_until='networkidle')
    expected=sorted([p for p in products if p['group']=='ups'],key=lambda p:p['price'],reverse=True)
    assert page.locator('.technical-item').evaluate_all('(els)=>els.map(el=>el.dataset.productId)')==[p['id'] for p in expected[24:48]]


def comparison(page):
    seed(page,fresh_state(),'#/asp/catalog?cat=ups')
    ids=[f'u0{i}' for i in range(1,7)]
    for pid in ids:
        page.locator(f'[data-action=compare][data-id="{pid}"]').click()
    page.goto(demo+'#/asp/compare',wait_until='networkidle')
    assert candidates(page)==ids
    for slot,pid in enumerate(['u05','u06']):
        page.locator(f'.research-mobile [data-action=choose-pair][data-slot="{slot}"]').focus()
        page.keyboard.press('Enter')
        page.locator(f'[data-action=select-pair][data-slot="{slot}"][data-id="{pid}"]').focus()
        page.keyboard.press('Enter')
        assert page.evaluate('document.activeElement.dataset.id')==pid
    assert pair(page)==['u05','u06']
    page.locator('#differences').check()
    page.reload(wait_until='networkidle')
    assert candidates(page)==ids and pair(page)==['u05','u06']
    expect(page.locator('#differences')).to_be_checked()
    page.locator('.research-mobile [data-action=remove-compare][data-id=u05]').click()
    assert len(candidates(page))==5
    page.locator('[data-action=undo-compare]').click()
    assert candidates(page)==ids and pair(page)==['u05','u06']
    page.locator('[data-action=add-compare-models]').click()
    replacement=next(p for p in products if p['group']=='ups' and p['id'] not in ids)
    page.locator('#replace-target').select_option('u05')
    page.locator('#candidate-search').fill(replacement['sku'])
    page.locator(f'[data-action=pick-candidate][data-id="{replacement["id"]}"]').click()
    assert candidates(page)==[replacement['id'] if pid=='u05' else pid for pid in ids]
    assert pair(page)==[replacement['id'],'u06']
    assert page.evaluate('document.activeElement.dataset.id')==replacement['id']
    page.reload(wait_until='networkidle')
    assert len(candidates(page))==6 and pair(page)==[replacement['id'],'u06']
    # Each mobile value includes its model in text available to assistive technology.
    for row in page.locator('.research-pair [data-row]').all():
        labels=row.locator('dd .sr-only').all_text_contents()
        assert labels==[by_id[replacement['id']]['name']+': ',by_id['u06']['name']+': ']
    for width,height in [(320,844),(390,844),(430,844),(1440,900)]:
        page.set_viewport_size({'width':width,'height':height})
        page.wait_for_timeout(160)
        overflow(page)
    page.set_viewport_size({'width':390,'height':844})
    page.add_style_tag(content='html {font-size: 200% !important} body {font-size:200% !important}')
    overflow(page)


def missing_and_scroll(page):
    state=fresh_state();state['compareByGroup']['ups']=['u01','u02','u03','u04','u05','u06'];state['view']['pairs']['ups']=['u02','u04']
    seed(page,state,'#/asp/compare')
    mass=page.locator('.research-desktop [data-row="Маса"]')
    expect(mass.locator('.difference-label')).to_have_text('Відмінність')
    expect(mass.locator('.incomplete-label')).to_have_text('Неповні дані')
    page.locator('#differences').check()
    expect(mass).to_be_visible()
    page.evaluate('''() => { window.__saves=0; const original=Storage.prototype.setItem; Storage.prototype.setItem=function(k,v){if(k==='perspective-demo-v1')window.__saves++;return original.call(this,k,v);}; }''')
    for width in [1200,1190,1210,1220]:
        page.set_viewport_size({'width':width,'height':900});page.wait_for_timeout(180)
    page.evaluate("window.__saves=0;document.querySelector('.research-scroll').scrollLeft=150")
    page.wait_for_timeout(250)
    assert page.evaluate('window.__saves')==1, 'One horizontal scroll must have one active persistence listener after resizes'
    expected_x=page.locator('.research-scroll').evaluate('(el)=>el.scrollLeft')
    page.reload(wait_until='networkidle')
    assert abs(page.locator('.research-scroll').evaluate('(el)=>el.scrollLeft')-expected_x)<2


def drafts_and_import(page):
    state=fresh_state();state['science']=science(project(['u02']))
    seed(page,state,'#/asp/project/project-1')
    page.locator('[data-science-form=project] [name=name]').fill('Незбережена назва')
    page.locator('[data-science-form=project] [name=note]').fill('Чернетка з кількістю 2')
    page.locator('[data-field=quantity]').fill('2');page.locator('[data-field=quantity]').press('Tab')
    expect(page.locator('[name=name]')).to_have_value('Незбережена назва')
    page.locator('[data-field=chosen]').check()
    expect(page.locator('[name=note]')).to_have_value('Чернетка з кількістю 2')
    page.locator('[data-action=science-candidates]').click()
    page.locator('[data-action=science-add-candidate][data-id=c02]').click()
    page.locator('#modal [data-action=close]').click()
    expect(page.locator('[name=name]')).to_have_value('Незбережена назва')
    page.locator('[data-science-form=project] button[type=submit]').click()
    page.reload(wait_until='networkidle')
    expect(page.locator('[name=note]')).to_have_value('Чернетка з кількістю 2')
    saved=stored(page)['science']['projects'][0]
    assert saved['quantities']['u02']==2 and saved['chosen']==['u02'] and saved['candidates']==['u02','c02']
    legacy={'format':'perspektyva-project','version':1,'project':project(['u02','c02'],'Старий формат')}
    legacy['project']['quantities']['c02']=2
    page.goto(demo+'#/asp/projects',wait_until='networkidle')
    payload=json.dumps(legacy,ensure_ascii=False).encode()
    page.locator('[data-science-import]').set_input_files({'name':'legacy-project.json','mimeType':'application/json','buffer':payload})
    expect(page.locator('h1')).to_have_text('Старий формат')
    page.reload(wait_until='networkidle')
    imported=stored(page)['science']['projects'][1]
    assert imported['id']=='project-2' and imported['quantities']['c02']==2


def limit64(page):
    ids=[p['id'] for p in products[:65]]
    state=fresh_state();state['science']=science(project(ids[:63]))
    seed(page,state,'#/asp/project/project-1')
    page.locator('[data-action=science-candidates]').click()
    page.locator(f'[data-action=science-add-candidate][data-id="{ids[63]}"]').click()
    assert len(stored(page)['science']['projects'][0]['candidates'])==64
    before=stored(page)['science']
    page.locator(f'[data-action=science-add-candidate][data-id="{ids[64]}"]').click()
    expect(page.locator('#toast')).to_contain_text('64')
    assert stored(page)['science']==before
    page.locator('#modal [data-action=close]').click()
    page.reload(wait_until='networkidle')
    assert len(stored(page)['science']['projects'][0]['candidates'])==64
    assert not stored(page)['science']['quarantine']
    page.locator('[data-action=science-duplicate]').click()
    expect(page.locator('h1')).to_contain_text('копія')
    assert len(stored(page)['science']['projects'][1]['candidates'])==64
    # Rejected 65-item legacy import cannot mutate either valid project.
    page.goto(demo+'#/asp/projects',wait_until='networkidle')
    before=stored(page)['science']
    payload=json.dumps({'format':'perspektyva-project','version':1,'project':project(ids)}).encode()
    page.locator('[data-science-import]').set_input_files({'name':'over-limit.json','mimeType':'application/json','buffer':payload})
    expect(page.locator('#toast')).to_contain_text('64')
    assert stored(page)['science']==before


def denied_storage(page):
    page.add_init_script("Storage.prototype.setItem=function(){throw new DOMException('Test storage refusal','QuotaExceededError')}")
    page.goto(demo+'#/asp/projects',wait_until='networkidle')
    page.locator('[data-action=science-create]').click()
    expect(page.locator('[data-save-status]').first).not_to_have_text('Збережено в цьому браузері.') if page.locator('[data-save-status]').count() else None
    expect(page.locator('#storage-warning')).to_contain_text('лише в пам’яті')
    expect(page.locator('#toast')).to_contain_text('лише в пам’яті')
    with page.expect_download() as download:
        page.locator('[data-action=science-export][data-format=json]').click()
    exported=json.loads(Path(download.value.path()).read_text())
    assert exported['format']=='perspektyva-project' and exported['project']['id']=='project-1'


def ng_views_and_reports(page):
    seed(page,fresh_state(),'#/ng/catalog?q=DEMO-U02')
    for view in ['cards','list','series']:
        page.locator(f'[data-action=catalog-view][data-key={view}]').click()
        expect(page.locator('.catalog-results')).to_contain_text('Виконання D1 · технічний опис')
        assert page.locator('.catalog-results .price,.catalog-results .stock,.technical-offer strong').count()==0
    for name in ['ASP24_Review','NGGroup_Review']:
        response=page.goto(base+'reports/'+name+'.html',wait_until='networkidle');assert response.status==200
        expect(page.locator('h1').first).to_be_visible()
        for width in [320,390,430,1440]:
            page.set_viewport_size({'width':width,'height':900});overflow(page)
        response=page.context.request.get(base+'reports/'+name+'.pdf')
        assert response.status==200 and response.body().startswith(b'%PDF-')


checks=[('exact-search-or-facets-sort-before-pagination',exact_and_facets,1440),('six-candidates-mobile-pair-replace-remove-undo-reload-keyboard-reflow-text-resize',comparison,390),('independent-missing-difference-and-scroll-listener-lifecycle',missing_and_scroll,1200),('draft-through-auxiliary-render-save-reload-legacy-import',drafts_and_import,390),('64-limit-atomic-add-import-duplicate-reload',limit64,390),('storage-refusal-in-memory-export',denied_storage,390),('ng-presentation-public-html-dom-pdf-http',ng_views_and_reports,390)]
with sync_playwright() as p:
    try:
        options={'chromium_sandbox':True} if args.browser=='chromium' else {}
        if args.executable: options['executable_path']=args.executable
        browser=getattr(p,args.browser).launch(timeout=30000,**options)
    except Exception as error:
        results.update(status='BLOCKED',launch_error=str(error))
    else:
        results['browser_version']=browser.version
        for name,check,width in checks:
            context=browser.new_context(viewport={'width':width,'height':844},accept_downloads=True)
            context.set_default_timeout(12000)
            context.tracing.start(screenshots=True,snapshots=True,sources=True)
            errors=[]
            def local_only(route):
                if urlsplit(route.request.url).netloc==origin:route.continue_()
                else:
                    errors.append('Unexpected off-origin request: '+route.request.url);route.abort()
            context.route('**/*',local_only)
            page=context.new_page();page.on('pageerror',lambda error:errors.append(str(error)))
            try:
                check(page)
                assert not errors,errors
            except Exception as error:
                page.screenshot(path=str(args.output/(name+'.png')),full_page=True)
                context.tracing.stop(path=str(args.output/(name+'.zip')))
                results['checks'].append({'name':name,'status':'FAIL','error':str(error),'traceback':traceback.format_exc(),'console_errors':errors})
                print('FAIL',name,str(error),flush=True)
            else:
                context.tracing.stop()
                results['checks'].append({'name':name,'status':'PASS'})
                print('PASS',name,flush=True)
            finally:context.close()
        browser.close()
        results['status']='FAIL' if any(c['status']=='FAIL' for c in results['checks']) else 'PASS'
results['completed_at_utc']=datetime.now(timezone.utc).isoformat()
(args.output/'results.json').write_text(json.dumps(results,ensure_ascii=False,indent=2)+'\n')
print(results['status'],args.output/'results.json',flush=True)
raise SystemExit(0 if results['status']=='PASS' else 2 if results['status']=='BLOCKED' else 1)
