#!/usr/bin/env python3
"""Package the exact tested Modern Experience dist and evidence; never rebuild it."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess

ROOT = Path(__file__).resolve().parents[1]
BASELINE = '0034b000bd1bad42f0c3ffb222a0ec58308a42bc'
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--evidence', type=Path, required=True)
parser.add_argument('--output', type=Path, default=ROOT / 'output/modern-preview')
args = parser.parse_args()
read = lambda path: json.loads(path.read_text())
digest = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()
sha = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()
assert not subprocess.check_output(['git', 'diff', '--name-only', 'HEAD'], cwd=ROOT), 'Commit source changes before packaging'
subprocess.run(['git', 'merge-base', '--is-ancestor', BASELINE, sha], cwd=ROOT, check=True)
build = read(args.evidence / 'build/build-result.json')
assert build['commit'] == sha and build['status'] == 'PASS', 'Build evidence does not identify this successful commit'
files = {p.relative_to(ROOT / 'dist').as_posix(): digest(p) for p in sorted((ROOT / 'dist').rglob('*')) if p.is_file()}
assert files == read(args.evidence / 'build/pages-sha256.json'), 'Dist differs from the tested Pages build'
browsers = {}
for browser in ['chromium', 'firefox', 'webkit']:
    suites = {}
    for name, relative in [('regression', 'results.json'), ('cases', 'cases/results.json'), ('case_storage', 'case-storage/results.json'), ('modern', 'modern/results.json')]:
        result = read(args.evidence / browser / relative)
        assert result['commit'] == sha and result['status'] == 'PASS', (browser, name, result)
        assert result['checks'] and all(check['status'] == 'PASS' for check in result['checks']), (browser, name)
        suites[name] = result
    browsers[browser] = suites
performance = read(args.evidence / 'performance/performance.json')
assert performance['baseline_sha'] == BASELINE and performance['candidate_sha'] == sha
assert performance['status'] == 'PASS', 'Performance measurement must actually complete; no speedup assertion is inferred'
args.output.mkdir(parents=True, exist_ok=False)
shutil.copytree(ROOT / 'dist', args.output / 'dist')
shutil.copytree(args.evidence, args.output / 'evidence')
(args.output / 'scripts').mkdir()
for name in ['serve.mjs', 'deployment-config.mjs']:
    shutil.copy2(ROOT / 'scripts' / name, args.output / 'scripts' / name)
shutil.copy2(ROOT / 'deployment.config.json', args.output / 'deployment.config.json')
shutil.copy2(ROOT / 'THIRD_PARTY_NOTICES.md', args.output / 'THIRD_PARTY_NOTICES.md')
(args.output / 'START_HERE.md').write_text(f'''# Modern Experience — HTTP preview

Exact source: https://github.com/mathewfromua/asp24-nggroup-demo-research/tree/{sha}
Base RC2: `{BASELINE}`. This artifact is separate from the release candidate.
No public deployment, merge or independent acceptance is claimed.

With Node 24, from this extracted directory run:

```sh
node scripts/serve.mjs --host 127.0.0.1 --port 8000
```

Open http://127.0.0.1:8000/asp24-nggroup-demo-research/ .
The reports remain the initial product; demo.html opens the synthetic catalogue.
The comparison page links to the React workbench. Its direct route is
`demo.html#/asp/compare?experience=modern` (or `ng` for NG Group).
No npm install or server fallback is needed for this already built preview.
Do not use file:// for interactive routes. All data in browser evidence are synthetic.

`modern-manifest.json` identifies every packaged byte, build checks, browser suites
and measurements. Performance PASS means successful measurement, not a speedup.
`evidence/performance` holds raw repetitions and environment details.
The root-domain build is independently checked in build evidence; this dist uses
its recorded Pages subpath. Rebuilding source requires npm ci and the lockfile.

Final reports are the RC2 14/16-page PDFs and matching HTML. R34 remains open;
R42 remains open (untagged current PDFs). Any tagged export experiment is separate.
Native Safari, physical iPhone, native zoom and VoiceOver are NOT_RUN.
WebKit and CSS text stress do not stand for those native checks.
''')
packaged = {}
for path in sorted(args.output.rglob('*')):
    if not path.is_file():
        continue
    relative = path.relative_to(args.output).as_posix()
    assert path.suffix.lower() not in {'.ttf', '.otf', '.woff', '.woff2', '.pyc', '.pem', '.key'}, relative
    assert not any(part in {'node_modules', '__pycache__', '.venv', '.git', '.auth'} for part in path.parts), relative
    packaged[relative] = {'sha256': digest(path), 'bytes': path.stat().st_size}
manifest = {
    'schema': 1, 'kind': 'modern-experience-http-preview', 'commit': sha,
    'baseline_sha': BASELINE, 'publication': 'NOT_DEPLOYED',
    'independent_review': 'PENDING', 'build': build, 'browsers': browsers,
    'performance': {'status': performance['status'], 'path': 'evidence/performance/performance.json',
                    'interpretation': 'Completed comparable measurements; see results, not an assumed improvement'},
    'reports': {'version': read(ROOT / 'publication.json')['reportVersion'],
                'input_digest': read(ROOT / 'reports/input-manifest.json')['digest']},
    'contracts': {'state_schema': 4, 'project_import_version': 1, 'personal_key': 'perspective-demo-v1',
                  'max_candidates': 6, 'project_limit': 64},
    'limitations': ['R34 service time origin unresolved', 'R42 final PDFs untagged; HTML alternative',
                    'Stable Safari / physical iPhone / native zoom / VoiceOver NOT_RUN',
                    'Synthetic catalogue; no real commerce or business-effect claim'],
    'file_hash_scope': 'All package files except this manifest; no self-referential checksum',
    'files': packaged,
}
(args.output / 'modern-manifest.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + '\n')
print(json.dumps({'commit': sha, 'files': len(packaged), 'output': str(args.output)}, ensure_ascii=False))
