#!/usr/bin/env bash
# Six suites, one existing dist and one local HTTP server. Never rebuild here.
set -euo pipefail
browser=${1:?browser required}
output=${2:?output directory required}
mkdir -p "$output"
preview_path=$(node -p "JSON.parse(require('node:fs').readFileSync('dist/build-config.json','utf8')).BASE_PATH")
preview_port=${RC3_PREVIEW_PORT:-8000}
preview_url="http://127.0.0.1:${preview_port}${preview_path}"
: > "$output/preview.log"
node scripts/serve.mjs --host 127.0.0.1 --port "$preview_port" > "$output/preview.log" 2>&1 &
preview_pid=$!
trap 'kill "$preview_pid" 2>/dev/null || true' EXIT
preview_ready=0
for attempt in {1..50}; do
  if ! kill -0 "$preview_pid" 2>/dev/null; then cat "$output/preview.log"; exit 1; fi
  if [[ "$(< "$output/preview.log")" == *"Preview: $preview_url"* ]] && curl --fail --silent --output /dev/null "$preview_url"; then
    preview_ready=1
    break
  fi
  sleep 0.2
done
if [ "$preview_ready" != 1 ] || ! kill -0 "$preview_pid" 2>/dev/null; then cat "$output/preview.log"; exit 1; fi
# Bind observations to bytes actually delivered by our child server. A stale
# service on the same port must never be mistaken for this candidate.
RC3_PREVIEW_URL="$preview_url" RC3_OUTPUT="$output" python - <<'PY'
import hashlib,json,os,urllib.parse,urllib.request
from pathlib import Path
class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self,*args,**kwargs):
        raise RuntimeError('Candidate byte verification must not follow redirects')
opener=urllib.request.build_opener(NoRedirect)
dist=Path('dist');served={}
for path in sorted(dist.rglob('*')):
    if not path.is_file():continue
    relative=path.relative_to(dist).as_posix()
    url=os.environ['RC3_PREVIEW_URL']+urllib.parse.quote(relative)
    with opener.open(url,timeout=10) as response:
        assert response.status==200,(relative,response.status)
        served[relative]=hashlib.sha256(response.read()).hexdigest()
    assert served[relative]==hashlib.sha256(path.read_bytes()).hexdigest(),f'Served bytes differ: {relative}'
(Path(os.environ['RC3_OUTPUT'])/'served-dist-sha256.json').write_text(json.dumps(served,indent=2)+'\n')
print('PASS local HTTP delivered bytes:',len(served),'files')
PY
kill -0 "$preview_pid"
browser_args=()
if [ "$browser" = chromium ] && command -v google-chrome >/dev/null; then
  browser_args+=(--executable "$(command -v google-chrome)")
fi
status=0
python scripts/browser-regression.py --url "$preview_url" --demo-path demo.html --browser "$browser" --output "$output" "${browser_args[@]}" || status=$?
python scripts/browser-cases.py --url "$preview_url" --browser "$browser" --output "$output/cases" "${browser_args[@]}" || status=$?
python scripts/browser-case-storage.py --url "$preview_url" --browser "$browser" --output "$output/case-storage" "${browser_args[@]}" || status=$?
python scripts/browser-modern.py --url "$preview_url" --browser "$browser" --output "$output/modern" "${browser_args[@]}" || status=$?
python scripts/browser-rc3.py --url "$preview_url" --browser "$browser" --output "$output/rc3" "${browser_args[@]}" || status=$?
python scripts/browser-reports-rc3.py --url "$preview_url" --browser "$browser" --output "$output/reports-rc3" "${browser_args[@]}" || status=$?
# The changed entry/case views warrant scoped observations, not another full
# Lighthouse/baseline campaign. These lab observations make no speedup claim.
if [ "$browser" = chromium ]; then
  python scripts/rc3-performance.py --url "$preview_url" --output "$output/performance" "${browser_args[@]}" || status=$?
fi
RC3_BROWSER="$browser" RC3_OUTPUT="$output" RC3_STATUS="$status" python - <<'PY'
import hashlib,json,os,subprocess
from pathlib import Path
dist=Path('dist')
result={'commit':subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),
        'browser':os.environ['RC3_BROWSER'],
        'status':'PASS' if os.environ['RC3_STATUS']=='0' else 'BLOCKED' if os.environ['RC3_STATUS']=='2' else 'FAIL',
        'working_tree_dirty':bool(subprocess.check_output(['git','diff','--name-only','HEAD'],text=True).strip()),
        'dist_sha256':{path.relative_to(dist).as_posix():hashlib.sha256(path.read_bytes()).hexdigest() for path in sorted(dist.rglob('*')) if path.is_file()}}
(Path(os.environ['RC3_OUTPUT'])/'browser-run.json').write_text(json.dumps(result,indent=2)+'\n')
PY
exit "$status"
