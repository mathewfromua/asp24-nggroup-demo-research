"""Comparable RC3/hardening cold samples, derived from performance-sample.py and rc3-performance.py.
Both variants run the same modern case. No field Web Vitals or general speed claim.
"""
import argparse,gzip,hashlib,importlib.metadata,json,mimetypes,platform,statistics,subprocess,threading
from datetime import datetime,timezone
from pathlib import Path
from http.server import BaseHTTPRequestHandler,ThreadingHTTPServer
from urllib.parse import urlsplit,unquote
from playwright.sync_api import sync_playwright
p=argparse.ArgumentParser();p.add_argument('--baseline-dist',type=Path,required=True);p.add_argument('--candidate-dist',type=Path,required=True);p.add_argument('--output',type=Path,required=True);p.add_argument('--repeats',type=int,default=5);p.add_argument('--executable');a=p.parse_args();assert a.repeats>=3;a.output.mkdir(parents=True,exist_ok=True)
ROOT=Path(__file__).resolve().parents[1]
COMMIT=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip()
SHA='b320abc302ed895704db2437ce7dbe3a6964e603'
def serve(root):
 prefix=json.loads((root/'build-config.json').read_text())['BASE_PATH']
 class Handler(BaseHTTPRequestHandler):
  def do_GET(self):
   pathname=unquote(urlsplit(self.path).path)
   if not pathname.startswith(prefix):self.send_error(404);return
   path=(root/pathname[len(prefix):]).resolve()
   if not path.is_relative_to(root.resolve()):self.send_error(403);return
   if path.is_dir():path=path/'index.html'
   if not path.is_file():self.send_error(404);return
   raw=path.read_bytes();mime=mimetypes.guess_type(str(path))[0] or 'application/octet-stream';compressed=mime.startswith('text/') or path.suffix in ['.js','.mjs','.json','.svg'];body=gzip.compress(raw,compresslevel=9,mtime=0) if compressed else raw
   self.send_response(200);self.send_header('Content-Type',mime);self.send_header('Cache-Control','no-store');self.send_header('Content-Length',str(len(body)))
   if compressed:self.send_header('Content-Encoding','gzip')
   self.end_headers();self.wfile.write(body)
  def log_message(self,*args):pass
 server=ThreadingHTTPServer(('127.0.0.1',0),Handler);threading.Thread(target=server.serve_forever,daemon=True).start();return server,'http://127.0.0.1:'+str(server.server_port)+prefix
observer="""(()=>{window.__perf={lcp:null,cls:0,longTasks:[]};for(const [type,collect] of [['largest-contentful-paint',es=>{for(const e of es)window.__perf.lcp=e.startTime}],['layout-shift',es=>{for(const e of es)if(!e.hadRecentInput)window.__perf.cls+=e.value}],['longtask',es=>{for(const e of es)window.__perf.longTasks.push({start:e.startTime,duration:e.duration})}]])new PerformanceObserver(l=>collect(l.getEntries())).observe({type,buffered:true});})();"""
def sample(browser,base,version,scenario,repeat):
 width,height=(390,844) if scenario=='comparison-mobile' else (1440,900)
 context=browser.new_context(viewport={'width':width,'height':height},service_workers='block',reduced_motion='reduce');context.add_init_script(observer);page=context.new_page();errors=[];page.on('pageerror',lambda e:errors.append(str(e)));page.on('response',lambda r:errors.append(str(r.status)+' '+r.url) if r.status>=400 else None)
 context.route('**/*',lambda r:r.continue_() if urlsplit(r.request.url).netloc==urlsplit(base).netloc else r.abort())
 comparison=scenario.startswith('comparison');path='demo.html?case=six-candidates&v=1#/asp/compare?experience=modern' if comparison else ''
 response=page.goto(base+path,wait_until='networkidle');assert response.status==200
 if comparison:page.get_by_test_id('comparison-workbench').wait_for(state='visible')
 page.evaluate('()=>new Promise(r=>requestAnimationFrame(()=>requestAnimationFrame(r)))');page.wait_for_timeout(250)
 before=page.evaluate("()=>({...window.__perf,fcp:performance.getEntriesByName('first-contentful-paint')[0]?.startTime??null,navigation:performance.getEntriesByType('navigation')[0].toJSON(),resources:performance.getEntriesByType('resource').map(e=>e.toJSON())})")
 latency=None
 if comparison:
  el=page.get_by_test_id('wb-differences');latency=el.evaluate('el=>new Promise(resolve=>{const start=performance.now();el.click();requestAnimationFrame(()=>requestAnimationFrame(()=>resolve(performance.now()-start)))})');assert el.is_checked()
 resources=before['resources'];assets=[r for r in resources if urlsplit(r['name']).path.endswith(('.js','.css'))]
 metrics={'request_count':len(resources)+1,'js_css_gzip_bytes':sum(r['encodedBodySize'] for r in assets),'js_css_raw_bytes':sum(r['decodedBodySize'] for r in assets),'lcp_ms':before['lcp'],'fcp_ms':before['fcp'],'cls':before['cls'],'click_to_two_frames_ms':latency,'long_task_excess_50ms':sum(max(0,t['duration']-50) for t in before['longTasks'])}
 assert not errors,errors;assert metrics['lcp_ms'] is not None
 if repeat==1:page.screenshot(path=str(a.output/(version+'-'+scenario+'.png')))
 context.close();return {'version':version,'scenario':scenario,'repeat':repeat,'metrics':metrics,'resources':resources,'navigation':before['navigation'],'long_tasks':before['longTasks']}
def inventory(root):
 return {str(p.relative_to(root)):{'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()} for p in sorted(root.rglob('*')) if p.is_file()}
def assets(root):
 return {str(p.relative_to(root)):{'raw':p.stat().st_size,'gzip':len(gzip.compress(p.read_bytes(),compresslevel=9,mtime=0)),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()} for p in root.rglob('*') if p.suffix in ['.js','.css']}
result={'baseline_sha':SHA,'commit':COMMIT,'candidate_sha':COMMIT,'working_tree_changes':subprocess.check_output(['git','status','--porcelain'],cwd=ROOT,text=True).splitlines(),'started_utc':datetime.now(timezone.utc).isoformat(),'method':{'derived_from':['scripts/performance-sample.py','scripts/rc3-performance.py'],'repeats':a.repeats,'fresh_context_per_sample':True,'alternating_versions':True,'server':'same process Python HTTP gzip9 mtime0 Cache-Control:no-store','network_cpu':'unthrottled loopback same Linux runner','interaction':'six-candidates modern; differences toggle click to two animation frames','viewport':{'desktop':[1440,900],'mobile':[390,844]},'not_field_metrics':True},'environment':{'platform':platform.platform(),'python':platform.python_version(),'playwright':importlib.metadata.version('playwright'),'node':subprocess.check_output(['node','--version'],text=True).strip()},'assets':{'baseline':assets(a.baseline_dist),'candidate':assets(a.candidate_dist)},'dist_files':{'baseline':inventory(a.baseline_dist),'candidate':inventory(a.candidate_dist)},'limitations':['Laboratory loopback data; not field Web Vitals, INP, mobile network or native-device evidence','LCP last observed after networkidle, two animation frames and250ms','Project/lab bytes move to first project action; that deferred action must pass the separate lazy-science smoke'],'samples':[]}
servers=[];bases={}
try:
 for version,root in [('baseline',a.baseline_dist),('candidate',a.candidate_dist)]:
  server,bases[version]=serve(root);servers.append(server)
 with sync_playwright() as pw:
  options={'chromium_sandbox':True}
  if a.executable:options['executable_path']=a.executable
  browser=pw.chromium.launch(**options);result['environment']['chromium']=browser.version
  for scenario in ['comparison-desktop','comparison-mobile','hub']:
   for repeat in range(1,a.repeats+1):
    for version in (['baseline','candidate'] if repeat%2 else ['candidate','baseline']):
     row=sample(browser,bases[version],version,scenario,repeat);result['samples'].append(row);print(version,scenario,repeat,row['metrics'],flush=True)
  browser.close()
 result['medians']={}
 for scenario in ['comparison-desktop','comparison-mobile','hub']:
  result['medians'][scenario]={}
  for version in ['baseline','candidate']:
   rows=[r['metrics'] for r in result['samples'] if r['version']==version and r['scenario']==scenario]
   result['medians'][scenario][version]={key:statistics.median(r[key] for r in rows) if rows[0][key] is not None else None for key in rows[0]}
 result['status']='PASS'
except Exception as e:result['status']='FAIL';result['error']=str(e)
finally:
 (a.output/'hardening-comparison.json').write_text(json.dumps(result,ensure_ascii=False,indent=2));print(result['status'],flush=True)
 for server in servers:server.shutdown()

raise SystemExit(0 if result['status']=='PASS' else 1)
