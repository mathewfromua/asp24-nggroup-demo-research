#!/usr/bin/env python3
"""Observe RC3 hub/case bytes and LCP on local HTTP, without a speedup claim."""
import argparse
from datetime import datetime, timezone
import hashlib
import importlib.metadata
import json
from pathlib import Path
import platform
import statistics
import subprocess
from urllib.parse import urlsplit

from playwright.sync_api import sync_playwright


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--url', required=True)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--executable')
    args = parser.parse_args()
    base = args.url.rstrip('/') + '/'
    parsed = urlsplit(base)
    assert parsed.scheme == 'http' and parsed.hostname in {'127.0.0.1', 'localhost'}, 'Local preview only'
    root = Path(__file__).resolve().parents[1]
    sha = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=root, text=True).strip()
    args.output.mkdir(parents=True, exist_ok=True)
    dist = root / 'dist'
    files = {p.relative_to(dist).as_posix(): {'bytes': p.stat().st_size, 'sha256': hashlib.sha256(p.read_bytes()).hexdigest()}
             for p in sorted(dist.rglob('*')) if p.is_file()}
    result = {
        'schema': 1, 'status': 'NOT_RUN', 'commit': sha,
        'started_at_utc': datetime.now(timezone.utc).isoformat(),
        'environment': {'platform': platform.platform(), 'python': platform.python_version(),
                        'playwright': importlib.metadata.version('playwright')},
        'method': 'Three fresh browser contexts per route/viewport; local HTTP with Cache-Control: no-store; no throttling or compression',
        'interpretation': 'Completed measurement only; no comparative performance, field INP or conversion claim',
        'limitations': ['Loopback and desktop runner are not a mobile network or physical device',
                       'LCP is the last observed entry after networkidle and two animation frames',
                       'No baseline comparison; transferred bytes depend on this preview server'],
        'dist_files': files, 'dist_total_bytes': sum(f['bytes'] for f in files.values()),
        'samples': [], 'medians': {},
    }
    observer = """() => {window.__rc3Lcp=null;new PerformanceObserver(list=>{
      for(const entry of list.getEntries())window.__rc3Lcp=entry.startTime;
    }).observe({type:'largest-contentful-paint',buffered:true});}"""
    launched = False
    try:
        with sync_playwright() as pw:
            launch = {'chromium_sandbox': True}
            if args.executable:
                launch['executable_path'] = args.executable
            browser = pw.chromium.launch(**launch)
            launched = True
            result['environment']['browser_version'] = browser.version
            for label, path, viewport in [
                ('hub-desktop', '', {'width': 1440, 'height': 900}),
                ('case-modern-desktop', 'demo.html?case=six-candidates&v=1#/asp/compare?experience=modern', {'width': 1440, 'height': 900}),
                ('case-modern-mobile', 'demo.html?case=six-candidates&v=1#/asp/compare?experience=modern', {'width': 390, 'height': 844}),
            ]:
                for repeat in range(3):
                    context = browser.new_context(viewport=viewport, reduced_motion='reduce', service_workers='block')
                    context.add_init_script('(' + observer + ')()')
                    page = context.new_page()
                    errors = []
                    page.on('pageerror', lambda error: errors.append(str(error)))
                    page.on('response', lambda response: errors.append(f'HTTP {response.status}: {response.url}') if response.status >= 400 else None)
                    def local_only(route):
                        if urlsplit(route.request.url).netloc == parsed.netloc:
                            route.continue_()
                        else:
                            errors.append('Unexpected outbound request: ' + route.request.url)
                            route.abort()
                    context.route('**/*', local_only)
                    response = page.goto(base + path, wait_until='networkidle')
                    assert response.status == 200
                    if label.startswith('case-'):
                        page.get_by_test_id('comparison-workbench').wait_for(state='visible')
                    page.evaluate('() => new Promise(resolve=>requestAnimationFrame(()=>requestAnimationFrame(resolve)))')
                    sample = page.evaluate('''() => {
                      const navigation=performance.getEntriesByType('navigation')[0].toJSON();
                      const resources=performance.getEntriesByType('resource').map(entry=>entry.toJSON());
                      const all=[navigation,...resources];
                      return {lcp_ms:window.__rc3Lcp, request_count:all.length,
                        transferred_bytes:all.reduce((sum,entry)=>sum+entry.transferSize,0),
                        encoded_body_bytes:all.reduce((sum,entry)=>sum+entry.encodedBodySize,0),
                        decoded_body_bytes:all.reduce((sum,entry)=>sum+entry.decodedBodySize,0),
                        navigation,resources};
                    }''')
                    assert not errors, errors
                    assert isinstance(sample['lcp_ms'], (float, int)) and sample['lcp_ms'] > 0, 'LCP unavailable'
                    result['samples'].append({'scenario': label, 'repeat': repeat + 1, 'viewport': viewport, **sample})
                    context.close()
                samples = [sample for sample in result['samples'] if sample['scenario'] == label]
                result['medians'][label] = {metric: statistics.median(sample[metric] for sample in samples)
                                           for metric in ['lcp_ms', 'request_count', 'transferred_bytes', 'encoded_body_bytes', 'decoded_body_bytes']}
            browser.close()
            result['status'] = 'PASS'
    except Exception as error:
        result['status'] = 'FAIL' if launched else 'BLOCKED'
        result['error'] = str(error)
    result['completed_at_utc'] = datetime.now(timezone.utc).isoformat()
    (args.output / 'performance.json').write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n')
    print(result['status'], args.output / 'performance.json')
    return 0 if result['status'] == 'PASS' else 2 if result['status'] == 'BLOCKED' else 1


if __name__ == '__main__':
    raise SystemExit(main())
