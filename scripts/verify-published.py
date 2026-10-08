#!/usr/bin/env python3
"""Verify exact deployed public bytes after deployment; never publish or bypass redirects."""
from pathlib import Path
import argparse
import hashlib
import json
import sys
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parent.parent
# Explicit authorized origins AND deployment prefixes. No wildcard hosts.
ALLOWED = {
    ('https', 'mathewfromua.github.io', '/asp24-nggroup-demo-research/'),
    ('https', 'perspektyva.mathew-from-ua.chatgpt.site', '/'),
    ('https', 'asp24-perspective.mathew-from-ua.chatgpt.site', '/'),
}


def allowed_url(value, prefix):
    url = urllib.parse.urlsplit(value)
    if url.username or url.password or url.query or url.fragment:
        return False
    try:
        decoded = urllib.parse.unquote(url.path, errors='strict')
    except UnicodeError:
        return False
    if any(part in ('.', '..') for part in decoded.split('/')) or '\\' in decoded:
        return False
    return ((url.scheme, url.netloc, prefix) in ALLOWED and decoded.startswith(prefix))


class AuthorizedRedirect(urllib.request.HTTPRedirectHandler):
    def __init__(self, base_url):
        super().__init__()
        self.origin = urllib.parse.urlsplit(base_url)[:2]
        self.prefix = urllib.parse.urlsplit(base_url).path

    def redirect_request(self, req, fp, code, msg, headers, newurl):
        if urllib.parse.urlsplit(newurl)[:2] != self.origin or not allowed_url(newurl, self.prefix):
            raise urllib.error.URLError('Redirect left the authorized origin or deployment prefix')
        return super().redirect_request(req, fp, code, msg, headers, newurl)


def main():
    defaults = json.loads((ROOT / 'deployment.config.json').read_text())
    parser = argparse.ArgumentParser()
    parser.add_argument('--base-url', default=defaults['PUBLIC_BASE_URL'])
    parser.add_argument('--out', default=str(ROOT / 'qa-results/published-byte-check.json'))
    args = parser.parse_args()
    base = args.base_url.rstrip('/') + '/'
    parsed = urllib.parse.urlsplit(base)
    if (parsed.scheme, parsed.netloc, parsed.path) not in ALLOWED or not allowed_url(base, parsed.path):
        raise SystemExit('Only the exact authorized HTTPS project origins and paths are allowed.')
    dist = ROOT / 'dist'
    if not (dist / 'index.html').is_file():
        raise SystemExit('Build dist before checking publication.')
    built = json.loads((dist / 'build-config.json').read_text())
    if built['PUBLIC_BASE_URL'] != base:
        raise SystemExit('The requested URL differs from dist/build-config.json; rebuild for this target.')
    opener = urllib.request.build_opener(AuthorizedRedirect(base))
    items = []
    for path in sorted(dist.rglob('*')):
        if not path.is_file():
            continue
        rel = path.relative_to(dist).as_posix()
        expected = hashlib.sha256(path.read_bytes()).hexdigest()
        row = {'path': rel, 'expected_sha256': expected}
        try:
            url = urllib.parse.urljoin(base, urllib.parse.quote(rel))
            req = urllib.request.Request(url, headers={'Cache-Control': 'no-cache', 'User-Agent': 'ASP24-NGGroup-release-verifier/3.1'})
            with opener.open(req, timeout=30) as response:
                body = response.read()
                row.update(status=response.status, resolved_url=response.url, content_type=response.headers.get_content_type())
            if not allowed_url(row['resolved_url'], parsed.path) or urllib.parse.urlsplit(row['resolved_url'])[:2] != parsed[:2]:
                raise ValueError('Final URL left the authorized origin or deployment prefix')
            row.update(actual_sha256=hashlib.sha256(body).hexdigest(), bytes=len(body))
            row['match'] = row['status'] == 200 and row['actual_sha256'] == expected
            if rel.endswith('.pdf'):
                row['pdf_signature'] = body.startswith(b'%PDF-')
                row['match'] = row['match'] and row['pdf_signature'] and row['content_type'] == 'application/pdf'
            if rel.endswith('.html'):
                row['match'] = row['match'] and row['content_type'] == 'text/html'
        except Exception as error:
            row.update(match=False, error=str(error))
        items.append(row)
    result = {'at': datetime.now(timezone.utc).isoformat(), 'base_url': base, 'files': items, 'passed': bool(items) and all(x['match'] for x in items)}
    output = Path(args.out)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result['passed'] else 1


if __name__ == '__main__':
    sys.exit(main())
