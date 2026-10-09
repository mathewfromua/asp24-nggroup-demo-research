#!/usr/bin/env python3
"""Focused checks for deferred project UI and safe failure/navigation recovery.
Uses an existing HTTP build; no rebuild or native-device support claim.
"""
import argparse,json,platform,subprocess,traceback,threading
from http.server import BaseHTTPRequestHandler,ThreadingHTTPServer
from urllib.request import urlopen
from urllib.error import HTTPError
from datetime import datetime,timezone
from pathlib import Path
from urllib.parse import urlsplit,parse_qs
from playwright.sync_api import sync_playwright,expect
parser=argparse.ArgumentParser(description=__doc__)
parser.add_argument('--url',required=True);parser.add_argument('--browser',choices=['chromium','firefox','webkit'],default='chromium');parser.add_argument('--executable');parser.add_argument('--output',type=Path,required=True);parser.add_argument('--only')
a=parser.parse_args();a.output.mkdir(parents=True,exist_ok=True);base=a.url.rstrip('/')+'/';root=Path(__file__).resolve().parents[1]
allowed_hosts={urlsplit(base).netloc}
results={'schema':1,'commit':subprocess.check_output(['git','rev-parse','HEAD'],cwd=root,text=True).strip(),'browser':a.browser,'url':base,'started_at_utc':datetime.now(timezone.utc).isoformat(),'environment':{'platform':platform.platform()},'checks':[],'not_run':['Native Safari, physical iPhone/Android, Telegram and VoiceOver']}
def go(p,path,wait='networkidle'):
 response=p.goto(base+path,wait_until=wait)
 if response:assert response.status==200
def first_save(p):
 requested=[];p.on('request',lambda r:requested.append(r.url))
 go(p,'demo.html?case=six-candidates&v=1#/asp/compare?experience=modern');expect(p.get_by_test_id('comparison-workbench')).to_be_visible()
 assert not any('science-entry-' in u for u in requested),requested
 p.get_by_test_id('wb-shortlist').click();expect(p.locator('#modal')).to_be_visible();assert any('science-entry-' in u for u in requested)
 p.locator('#modal [data-target=new]').click();expect(p.locator('.science-project-line')).to_have_count(6)
 p.locator('[data-science-form=project] [name=name]').fill('Збережений контрольний проєкт P3')
 p.locator('[data-science-form=project] [name=note]').fill('Контрольна чернетка без втрати даних')
 p.locator('[data-science-form=project] button[type=submit]').click();p.reload(wait_until='networkidle')
 expect(p.locator('[data-science-form=project] [name=name]')).to_have_value('Збережений контрольний проєкт P3');expect(p.locator('[data-science-form=project] [name=note]')).to_have_value('Контрольна чернетка без втрати даних');expect(p.locator('.science-project-line')).to_have_count(6)
 stored=p.evaluate("JSON.parse(sessionStorage.getItem('asp24-nggroup-case:six-candidates:v1'))")
 assert stored['science']['projects'][-1]['candidates']==['u01','u02','u03','u04','u05','u06'];assert stored['view']['pairs']['ups']==['u05','u06']
 p.screenshot(path=str(a.output/'lazy-project-saved.png'))
def import_failure(p):
 # Real HTTP errors exercise the browser module cache without request-interception
 # side effects. The proxy forwards only this preview's own path/origin.
 blocked=[True];requests=[];source=urlsplit(base)
 class Handler(BaseHTTPRequestHandler):
  def do_GET(self):
   path=urlsplit(self.path).path
   if not path.startswith(source.path):body=b'Not found';ctype='text/plain';status=404
   elif '/assets/science-entry-' in path and path.endswith('.js') and blocked[0]:body=b'Temporary project asset failure';ctype='text/plain';status=503
   else:
    try:
     with urlopen(source.scheme+'://'+source.netloc+self.path,timeout=15) as response:body=response.read();ctype=response.headers['Content-Type'];status=response.status
    except HTTPError as error:body=error.read();ctype=error.headers['Content-Type'];status=error.code
   requests.append({'path':self.path,'status':status});self.send_response(status);self.send_header('Content-Type',ctype);self.send_header('Cache-Control','no-store');self.send_header('Content-Length',str(len(body)));self.end_headers();self.wfile.write(body)
  def log_message(self,*args):pass
 server=ThreadingHTTPServer(('127.0.0.1',0),Handler);threading.Thread(target=server.serve_forever,daemon=True).start()
 host=f'127.0.0.1:{server.server_port}';allowed_hosts.add(host);fault_base='http://'+host+source.path
 case_url=fault_base+'demo.html?case=six-candidates&v=1&keep=receipt#/asp/projects?q=U02'
 try:
  assert p.goto(case_url,wait_until='networkidle').status==200
  expect(p.locator('[data-science-loading]')).to_contain_text('Не вдалося');expect(p.locator('[data-science-loading] a[href="#/ng/documents"]')).to_be_visible()
  p.locator('#case-export').click();before=json.loads(p.locator('.case-context-details .export-fallback textarea').input_value())['state']
  personal=json.loads(json.dumps(before));personal.update(cart={'u02':2},drafts={'u02':{'purpose':'Сумісність','quantity':'7','question':'Особиста контрольна чернетка'}})
  p.evaluate("value=>localStorage.setItem('perspective-demo-v1',value)",json.dumps(personal));personal_before=p.evaluate('JSON.stringify({...localStorage})')
  origin=p.evaluate('performance.timeOrigin');blocked[0]=False;p.locator('[data-action=load-science]').click()
  expect(p.locator('[data-action=science-create]')).to_be_visible();assert p.evaluate('performance.timeOrigin')!=origin
  retry_token=parse_qs(urlsplit(p.url).query)['retry-science'];assert len(retry_token)==1
  p.reload(wait_until='networkidle');expect(p.locator('[data-action=science-create]')).to_be_visible();assert not p.locator('[data-science-loading]').count()
  query=parse_qs(urlsplit(p.url).query);assert query=={'case':['six-candidates'],'v':['1'],'keep':['receipt'],'retry-science':retry_token},query
  assert urlsplit(p.url).fragment=='/asp/projects?q=U02';assert p.evaluate('JSON.stringify({...localStorage})')==personal_before
  after=p.evaluate("JSON.parse(sessionStorage.getItem('asp24-nggroup-case:six-candidates:v1'))")
  for key in ['compareByGroup','science','cart','drafts']:assert after[key]==before[key],key
  assert after['view']['pairs']==before['view']['pairs']
  p.screenshot(path=str(a.output/'lazy-project-retry.png'))
  # A fresh explicit retry during a continuing outage must still fail visibly.
  blocked[0]=True;p.goto(case_url,wait_until='networkidle');expect(p.locator('[data-science-loading]')).to_contain_text('Не вдалося')
  origin=p.evaluate('performance.timeOrigin');p.locator('[data-action=load-science]').click();expect(p.locator('[data-science-loading]')).to_contain_text('Не вдалося')
  assert p.evaluate('performance.timeOrigin')!=origin;expect(p.locator('[data-action=load-science]')).to_be_visible()
  p.locator('[data-science-loading] a[href="#/ng/documents"]').click();expect(p.locator('.document-list')).to_be_visible();assert p.evaluate('JSON.stringify({...localStorage})')==personal_before
  js=[r for r in requests if '/assets/science-entry-' in urlsplit(r['path']).path and urlsplit(r['path']).path.endswith('.js')]
  assert any(r['status']==503 and not urlsplit(r['path']).query for r in js),js
  assert any(r['status']==200 and urlsplit(r['path']).query.startswith('retry=') for r in js),js
  assert any(r['status']==503 and urlsplit(r['path']).query.startswith('retry=') for r in js),js
 finally:
  (a.output/'lazy-project-http-recovery-requests.json').write_text(json.dumps(requests,ensure_ascii=False,indent=2)+'\n')
  server.shutdown();server.server_close();allowed_hosts.discard(host)
def denied_retry(p):
 go(p,'demo.html#/asp/catalog');p.locator('[data-action=cart][data-id=u02]').click()
 p.context.route('**/assets/science-entry-*.js*',lambda r:r.abort())
 go(p,'demo.html#/asp/projects');expect(p.locator('[data-science-loading]')).to_contain_text('Не вдалося')
 p.evaluate("()=>{Storage.prototype.setItem=function(){throw new DOMException('Intentional storage denial','QuotaExceededError')};}")
 origin=p.evaluate('performance.timeOrigin');p.locator('[data-action=load-science]').click()
 expect(p.locator('#toast')).to_contain_text('Перезавантаження зупинено');assert p.evaluate('performance.timeOrigin')==origin
 p.locator('[data-action=export-live-state]').click();state=json.loads(p.locator('#modal .export-fallback textarea').input_value())
 assert state['cart']=={'u02':1};assert state['version']==4
 p.locator('#modal [data-action=close]').first.click()
 p.locator('[data-science-loading] a[href="#/ng/documents"]').click();expect(p.locator('.document-list')).to_be_visible()
def stale_navigation(p):
 pending=[];p.context.route('**/assets/science-entry-*.js*',lambda r:pending.append(r))
 go(p,'demo.html#/asp/projects',wait='domcontentloaded');expect(p.locator('[data-science-loading]')).to_be_visible()
 p.locator('[data-science-loading] a[href="#/ng/documents"]').click();expect(p.locator('.document-list')).to_be_visible()
 for route in pending:route.continue_()
 p.wait_for_load_state('networkidle');expect(p.locator('.document-list')).to_be_visible();assert p.url.endswith('#/ng/documents')
 assert not p.locator('#modal').is_visible()
def newer_modal(p):
 pending=[];released=[False]
 p.context.route('**/assets/science-entry-*.js*',lambda r:r.continue_() if released[0] else pending.append(r))
 go(p,'demo.html?case=six-candidates&v=1#/asp/compare?experience=modern');expect(p.get_by_test_id('comparison-workbench')).to_be_visible()
 p.get_by_test_id('wb-shortlist').click();p.wait_for_timeout(100);assert pending
 # A normal pointer press can span a frame; focus handling must not move its target.
 p.locator('.wb-full .wb-model-title').first.click(delay=80);expect(p.locator('#modal')).to_be_visible()
 title=p.locator('#dialog-title').inner_text();assert 'VOLTYN N18' in title
 stored="JSON.parse(sessionStorage.getItem('asp24-nggroup-case:six-candidates:v1'))"
 before=p.evaluate(stored)
 released[0]=True
 for request in pending:request.continue_()
 p.wait_for_load_state('networkidle');expect(p.locator('#dialog-title')).to_have_text(title)
 after=p.evaluate(stored)
 for field in ['science','cart','drafts','compareByGroup']:
  assert after[field]==before[field],field
 assert after['view']['pairs']==before['view']['pairs']
 p.screenshot(path=str(a.output/'late-project-import-newer-model-modal.png'))
checks=[('deferred-first-click-project-save-draft-reload',first_save),('failed-project-import-explicit-safe-reload-retry',import_failure),('denied-storage-blocks-reload-export-retains-state',denied_retry),('late-project-import-preserves-document-navigation',stale_navigation),('late-project-import-preserves-newer-model-modal-and-state',newer_modal)]
if a.only:checks=[c for c in checks if c[0] in a.only.split(',')];assert checks
try:
 with sync_playwright() as pw:
  options={}
  if a.browser=='chromium':options['chromium_sandbox']=True
  if a.executable:options['executable_path']=a.executable
  browser=getattr(pw,a.browser).launch(**options);results['environment']['browser_version']=browser.version
  for name,fn in checks:
   context=browser.new_context(viewport={'width':1440,'height':900},accept_downloads=True);context.route('**/*',lambda r:r.continue_() if urlsplit(r.request.url).netloc in allowed_hosts else r.abort());context.tracing.start(screenshots=True,snapshots=True);page=context.new_page();errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
   try:fn(page);assert not errors,errors
   except Exception as e:
    page.screenshot(path=str(a.output/(name+'-failure.png')),full_page=True);context.tracing.stop(path=str(a.output/(name+'.zip')));results['checks'].append({'name':name,'status':'FAIL','error':str(e),'traceback':traceback.format_exc()});print('FAIL',name,str(e),flush=True)
   else:context.tracing.stop();results['checks'].append({'name':name,'status':'PASS'});print('PASS',name,flush=True)
   finally:context.close()
  browser.close();results['status']='FAIL' if any(c['status']=='FAIL' for c in results['checks']) else 'PASS'
except Exception as e:results['status']='BLOCKED' if not results['checks'] else 'FAIL';results['error']=str(e)
results['completed_at_utc']=datetime.now(timezone.utc).isoformat();(a.output/'results.json').write_text(json.dumps(results,ensure_ascii=False,indent=2)+'\n');print(results['status'],flush=True)
raise SystemExit(0 if results['status']=='PASS' else 2 if results['status']=='BLOCKED' else 1)
