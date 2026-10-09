#!/usr/bin/env bash
# Test the existing dist; this script deliberately performs no build.
set -euo pipefail
browser=${1:?browser required}
output=${2:?output directory required}
mkdir -p "$output"
preview_path=$(node -p "JSON.parse(require('node:fs').readFileSync('dist/build-config.json','utf8')).BASE_PATH")
preview_url="http://127.0.0.1:8000${preview_path}"
npm run preview -- --host 127.0.0.1 --port 8000 > "$output/preview.log" 2>&1 &
preview_pid=$!
trap 'kill "$preview_pid" 2>/dev/null || true' EXIT
for attempt in {1..50}; do
  if curl --fail --silent --output /dev/null "$preview_url"; then break; fi
  sleep 0.2
done
curl --fail --silent --output /dev/null "$preview_url"
browser_args=()
if [ -f dist/demo.html ]; then browser_args+=(--demo-path demo.html); fi
if [ "$browser" = chromium ] && command -v google-chrome >/dev/null; then
  browser_args+=(--executable "$(command -v google-chrome)")
fi
browser_status=0
python scripts/browser-regression.py --url "$preview_url" --browser "$browser" --output "$output" "${browser_args[@]}" || browser_status=$?
python scripts/browser-cases.py --url "$preview_url" --browser "$browser" --output "$output/cases" "${browser_args[@]}" || browser_status=$?
exit "$browser_status"
