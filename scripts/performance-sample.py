#!/usr/bin/env python3
"""Repeat cold-cache RC2/current measurements against identical local gzip HTTP.

This is a laboratory comparison, not a field performance or conversion claim.
The server sends deterministic gzip bytes, disables cache, and has no SPA fallback.
"""
import argparse
from datetime import datetime, timezone
import gzip
import hashlib
import importlib.metadata
import json
import mimetypes
import os
from pathlib import Path
import platform
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import statistics
import subprocess
import sys
import threading
import time
from urllib.parse import unquote, urlsplit
from playwright.sync_api import sync_playwright

p = argparse.ArgumentParser(description=__doc__)
p.add_argument('--baseline-dist', type=Path, required=True)
p.add_argument('--modern-dist', type=Path, required=True)
p.add_argument('--baseline-sha', default='0034b000bd1bad42f0c3ffb222a0ec58308a42bc')
p.add_argument('--output', type=Path, required=True)
p.add_argument('--repeats', type=int, default=5)
p.add_argument('--executable')
a = p.parse_args()
assert a.repeats >= 3, 'At least three runs are required'
a.output.mkdir(parents=True, exist_ok=True)
root = Path(__file__).resolve().parents[1]
sha = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=root, text=True).strip()
fixture = json.loads(subprocess.check_output(['node', '--input-type=module', '-e', "import {products} from './data.js';import {initialState} from './logic.js';let state=initialState();const ids=products.filter(p=>p.group==='ups').slice(0,6).map(p=>p.id);state.compareByGroup.ups=ids;state.view.group='ups';state.view.pairs.ups=ids.slice(0,2);console.log(JSON.stringify(state));"], cwd=root, text=True))


def serve(directory):
    directory = directory.resolve()
    class Handler(BaseHTTPRequestHandler):
        def do_GET(self):
            path = (directory / unquote(urlsplit(self.path).path).lstrip('/')).resolve()
            if not path.is_relative_to(directory):
                self.send_error(403); return
            if path.is_dir(): path = path / 'index.html'
            if not path.is_file():
                self.send_error(404); return
            raw = path.read_bytes()
            mime = mimetypes.guess_type(str(path))[0] or 'application/octet-stream'
            compress = mime.startswith('text/') or path.suffix in ('.js', '.mjs', '.json', '.svg')
            body = gzip.compress(raw, compresslevel=9, mtime=0) if compress else raw
            self.send_response(200)
            self.send_header('Content-Type', mime)
            self.send_header('Cache-Control', 'no-store')
            self.send_header('Content-Length', str(len(body)))
            if compress: self.send_header('Content-Encoding', 'gzip')
            self.end_headers(); self.wfile.write(body)
        def log_message(self, *args): pass
    server = ThreadingHTTPServer(('127.0.0.1', 0), Handler)
    threading.Thread(target=server.serve_forever, daemon=True).start()
    return server, 'http://127.0.0.1:' + str(server.server_port) + '/'


observer = """(() => {
  window.__perf = {lcp: null, cls: 0, longTasks: [], events: []};
  for (const [type, collect] of [
    ['largest-contentful-paint', entries => {for(const e of entries) window.__perf.lcp=e.startTime;}],
    ['layout-shift', entries => {for(const e of entries) if(!e.hadRecentInput) window.__perf.cls+=e.value;}],
    ['longtask', entries => {for(const e of entries) window.__perf.longTasks.push({start:e.startTime,duration:e.duration});}],
    ['event', entries => {for(const e of entries) if(e.interactionId)window.__perf.events.push({name:e.name,duration:e.duration,interactionId:e.interactionId});}]
  ]) {try {new PerformanceObserver(list=>collect(list.getEntries())).observe({type, buffered:true, ...(type==='event'?{durationThreshold:16}:{})});} catch {}}
})();"""


def sample(browser, base, version, scenario, repeat):
    context = browser.new_context(viewport={'width':1440, 'height':900}, service_workers='block', reduced_motion='reduce')
    context.add_init_script(observer)
    if scenario == 'comparison':
        context.add_init_script('localStorage.setItem("perspective-demo-v1",' + json.dumps(json.dumps(fixture, ensure_ascii=False)) + ')')
    page = context.new_page()
    errors = []
    page.on('pageerror', lambda e: errors.append(str(e)))
    page.on('response', lambda r: errors.append(f'HTTP {r.status}: {r.url}') if r.status >= 400 else None)
    route = {'hub':'', 'demo':'demo.html#/asp/catalog', 'comparison':'demo.html#/asp/compare' + ('?experience=modern' if version == 'modern' else '')}[scenario]
    response = page.goto(base + route, wait_until='networkidle')
    assert response.status == 200
    selector = '[data-testid=wb-differences]' if version == 'modern' else '#differences'
    if scenario == 'comparison': page.locator(selector).wait_for(state='visible')
    page.evaluate('() => new Promise(resolve=>requestAnimationFrame(()=>requestAnimationFrame(resolve)))')
    page.wait_for_timeout(250)
    before = page.evaluate('''() => ({...window.__perf, fcp:performance.getEntriesByName('first-contentful-paint')[0]?.startTime??null,
      navigation:performance.getEntriesByType('navigation')[0].toJSON(), resources:performance.getEntriesByType('resource').map(e=>e.toJSON())})''')
    interaction = None
    if scenario == 'comparison':
        # The same user operation and seeded six models: toggle differences and
        # wait until the browser has had two animation frames to paint it.
        interaction = page.locator(selector).evaluate('''el => new Promise(resolve=>{
          const started=performance.now();el.click();requestAnimationFrame(()=>requestAnimationFrame(()=>resolve(performance.now()-started)));
        })''')
        assert page.locator(selector).is_checked()
    final = page.evaluate('window.__perf')
    assert not errors, errors
    resources = before['resources']
    js_css = [r for r in resources if urlsplit(r['name']).path.endswith(('.js', '.css'))]
    metrics = {
        'request_count': len(resources) + 1,
        'total_encoded_body_bytes': sum(r['encodedBodySize'] for r in resources) + before['navigation']['encodedBodySize'],
        'js_css_decoded_bytes': sum(r['decodedBodySize'] for r in js_css),
        'js_css_transferred_body_bytes': sum(r['encodedBodySize'] for r in js_css),
        'initial_js_decoded_bytes': sum(r['decodedBodySize'] for r in js_css if urlsplit(r['name']).path.endswith('.js')),
        'initial_js_encoded_bytes': sum(r['encodedBodySize'] for r in js_css if urlsplit(r['name']).path.endswith('.js')),
        'lcp_ms': before['lcp'], 'cls': before['cls'], 'fcp_ms': before['fcp'],
        'dom_content_loaded_ms': before['navigation']['domContentLoadedEventEnd'],
        'load_ms': before['navigation']['loadEventEnd'],
        'total_blocking_time_proxy_ms': sum(max(0, entry['duration']-50) for entry in before['longTasks']),
        'comparison_click_to_two_frames_ms': interaction,
    }
    assert metrics['lcp_ms'] is not None, 'No LCP observation'
    if scenario == 'hub': assert metrics['initial_js_decoded_bytes'] < 5000, 'Hub unexpectedly loads a large JS/catalog graph'
    result = {'version':version, 'scenario':scenario, 'repeat':repeat, 'url':base+route, 'metrics':metrics, 'resources':resources,
              'navigation':before['navigation'], 'long_tasks':before['longTasks'], 'interaction_events':final['events']}
    if repeat == 1: page.screenshot(path=str(a.output / f'{version}-{scenario}-1440.png'), full_page=True)
    context.close()
    return result


def assets(directory):
    result = {}
    for path in sorted(directory.rglob('*')):
        if path.is_file() and path.suffix in ('.js', '.css'):
            data = path.read_bytes()
            result[path.relative_to(directory).as_posix()] = {'raw_bytes':len(data), 'gzip_bytes':len(gzip.compress(data, compresslevel=9, mtime=0)), 'sha256':hashlib.sha256(data).hexdigest()}
    return result


def lighthouse_samples(bases):
    binary=root/'node_modules/.bin/lighthouse'
    info={'status':'NOT_RUN','repeats':3,'scenarios':['hub','demo'],'method':'Desktop preset, provided unthrottled CPU/network, same gzip servers; cold Chrome process each run; no sandbox bypass','samples':[]}
    if not binary.exists():
        info['reason']='Locked Lighthouse executable unavailable'
        return info
    info['version']=subprocess.check_output([str(binary),'--version'],text=True).strip()
    directory=a.output/'lighthouse';directory.mkdir()
    env=dict(os.environ)
    if a.executable:env['CHROME_PATH']=a.executable
    for repeat in range(1,4):
        for scenario in ['hub','demo']:
            for version in (['baseline','modern'] if repeat%2 else ['modern','baseline']):
                name=f'{version}-{scenario}-{repeat}'
                target=directory/(name+'.json')
                command=[str(binary),bases[version]+('demo.html#/asp/catalog' if scenario=='demo' else ''),'--only-categories=performance','--preset=desktop','--throttling-method=provided','--chrome-flags=--headless=new','--output=json','--output-path='+str(target),'--quiet']
                try:
                    result=subprocess.run(command,cwd=root,env=env,text=True,capture_output=True,timeout=150)
                    (directory/(name+'.log')).write_text(result.stdout+'\n'+result.stderr)
                    if result.returncode:raise RuntimeError('Lighthouse exited '+str(result.returncode)+'; see '+name+'.log')
                    data=json.loads(target.read_text());assert not data.get('runtimeError'),data.get('runtimeError')
                    metrics={metric:data['audits'][metric].get('numericValue') for metric in ['first-contentful-paint','largest-contentful-paint','cumulative-layout-shift','total-blocking-time','speed-index']}
                    info['samples'].append({'version':version,'scenario':scenario,'repeat':repeat,'metrics':metrics,'score':data['categories']['performance']['score'],'path':'lighthouse/'+name+'.json','status':'PASS'})
                    print('LIGHTHOUSE',name,json.dumps(metrics),flush=True)
                except Exception as error:
                    info['status']='BLOCKED';info['reason']=str(error)
                    return info
    info['status']='PASS'
    info['summary']={}
    for scenario in ['hub','demo']:
        info['summary'][scenario]={}
        for version in ['baseline','modern']:
            rows=[x for x in info['samples'] if x['version']==version and x['scenario']==scenario]
            info['summary'][scenario][version]={key:statistics.median(x['metrics'][key] for x in rows) for key in rows[0]['metrics']}
    return info


report = {'schema':1, 'commit':sha, 'candidate_sha':sha, 'baseline_sha':a.baseline_sha, 'status':'BLOCKED', 'command':['python',*sys.argv], 'started_at_utc':datetime.now(timezone.utc).isoformat(),
          'environment':{'platform':platform.platform(), 'python':platform.python_version(), 'node':subprocess.check_output(['node','--version'], text=True).strip(), 'playwright':importlib.metadata.version('playwright')},
          'method':{'repeats':a.repeats, 'viewport':{'width':1440,'height':900}, 'cold_cache':True, 'server':'Python HTTP, gzip level 9, cache-control no-store',
                    'network':'unthrottled loopback, sequential alternating versions', 'cpu':'unthrottled same runner', 'reduced_motion':'reduce',
                    'interaction':'Same six ups models; differences toggle click to two animation frames', 'total_blocking_time':'long-task excess over 50ms during navigation observation; lab proxy, not Lighthouse TBT',
                    'not_measured':['field INP','real network performance','native zoom','Safari','iPhone','VoiceOver']},
          'assets':{'baseline':assets(a.baseline_dist), 'modern':assets(a.modern_dist)}, 'samples':[]}
servers = []
try:
    bases = {}
    for version, directory in [('baseline',a.baseline_dist),('modern',a.modern_dist)]:
        server, bases[version] = serve(directory); servers.append(server)
    with sync_playwright() as playwright:
        options = {'chromium_sandbox':True}
        if a.executable: options['executable_path'] = a.executable
        browser = playwright.chromium.launch(timeout=30000, **options)
        report['environment']['browser'] = browser.version
        for repeat in range(1, a.repeats+1):
            for scenario in ['hub','demo','comparison']:
                # Reverse order every other repetition to reduce systematic order bias.
                for version in (['baseline','modern'] if repeat % 2 else ['modern','baseline']):
                    result = sample(browser,bases[version],version,scenario,repeat)
                    report['samples'].append(result)
                    print(version, scenario, repeat, json.dumps(result['metrics']), flush=True)
        browser.close()
    report['summary'] = {}
    for scenario in ['hub','demo','comparison']:
        report['summary'][scenario] = {}
        for version in ['baseline','modern']:
            rows = [s['metrics'] for s in report['samples'] if s['scenario']==scenario and s['version']==version]
            report['summary'][scenario][version] = {key:{'median':statistics.median(values),'min':min(values),'max':max(values)} for key in rows[0] if (values:=[row[key] for row in rows if row[key] is not None])}
        before, after = report['summary'][scenario]['baseline'], report['summary'][scenario]['modern']
        report['summary'][scenario]['delta_modern_minus_baseline'] = {key:after[key]['median']-before[key]['median'] for key in before if key in after}
    report['lighthouse'] = lighthouse_samples(bases)
    report['status'] = 'PASS'
except Exception as error:
    import traceback
    report['error'] = str(error); report['traceback'] = traceback.format_exc()
    report['status'] = 'FAIL' if report['samples'] else 'BLOCKED'
    print(report['status'], error, flush=True)
finally:
    for server in servers: server.shutdown()
    report['completed_at_utc'] = datetime.now(timezone.utc).isoformat()
    (a.output/'performance.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
raise SystemExit(0 if report['status']=='PASS' else 2 if report['status']=='BLOCKED' else 1)
