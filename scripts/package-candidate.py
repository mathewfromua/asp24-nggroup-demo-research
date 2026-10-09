#!/usr/bin/env python3
"""Assemble a reviewed-source bundle around the one already-tested dist artifact."""
import argparse, hashlib, io, json, os, platform, shutil, subprocess, tarfile, zipfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
p=argparse.ArgumentParser(description=__doc__)
p.add_argument('--evidence',type=Path,required=True)
p.add_argument('--output',type=Path,default=ROOT/'output/candidate')
a=p.parse_args()
sha=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip()
assert not subprocess.check_output(['git','status','--porcelain','--untracked-files=no'],cwd=ROOT), 'Commit candidate inputs before packaging'
read=lambda path:json.loads(path.read_text())
hashfile=lambda path:hashlib.sha256(path.read_bytes()).hexdigest()
registry=read(ROOT/'publication.json');included=read(ROOT/'docs/included-heads.json')
for record in included['branches']:
 subprocess.run(['git','merge-base','--is-ancestor',record['head'],sha],cwd=ROOT,check=True)
build=read(a.evidence/'build/build-result.json');assert build['commit']==sha and build['status']=='PASS'
actual={p.relative_to(ROOT/'dist').as_posix():hashfile(p) for p in sorted((ROOT/'dist').rglob('*')) if p.is_file()}
assert actual==read(a.evidence/'build/dist-sha256.json'), 'Downloaded dist differs from tested build'
browsers={}
for browser in ['chromium','firefox','webkit']:
 regression=read(a.evidence/browser/'results.json');cases=read(a.evidence/browser/'cases/results.json')
 for result in [regression,cases]:
  assert result['commit']==sha and result['status']=='PASS',(browser,result)
 browsers[browser]={'regression':regression,'cases':cases}
# Standalone generation only embeds existing local images; never rebuilds dist or PDFs.
subprocess.run(['python','reports/export_standalone.py'],cwd=ROOT,check=True)
assert not subprocess.check_output(['git','diff','--name-only'],cwd=ROOT), 'Standalone manifest unexpectedly changed'
bundle=a.output/f'asp24-nggroup-{sha}';bundle.mkdir(parents=True,exist_ok=False)
source=bundle/'source';source.mkdir()
archive=subprocess.check_output(['git','archive',sha],cwd=ROOT)
with tarfile.open(fileobj=io.BytesIO(archive)) as tar:tar.extractall(source,filter='data')
shutil.copytree(ROOT/'dist',bundle/'dist')
shutil.copytree(ROOT/'output/standalone',bundle/'reports')
shutil.copytree(a.evidence,bundle/'evidence')
for name in ['reports/editorial-validation.json','research/editorial-decisions.json','research/editorial-source-register.json','docs/included-heads.json','docs/RELEASE_NOTES.md','docs/REVIEW_CANDIDATE.md']:
 shutil.copy2(ROOT/name,bundle/'evidence'/Path(name).name)
(bundle/'START_HERE.md').write_text(f'''# ASP24 / NG Group — {registry['reportVersion']}

Preview with limitations. Commit `{sha}`. Main / Pages unchanged.

Read `reports/ASP24_Review.pdf`, `reports/NGGroup_Review.pdf` or the two standalone HTML files. For interactive cases: install Node 24, run `cd source && node scripts/serve.mjs` after copying the sibling `dist` into `source/dist`; open the localhost URL printed by the server. No npm install needed. Never open ES modules with file://.

The immutable `dist` was built once, then downloaded and tested by Chromium, Firefox and WebKit. `evidence` records actual results. `source` is git archive of the exact commit. Report control regeneration used a separate temporary tree. Fonts are fetched separately with checked hashes; font files and caches are not bundled.

PDF and standalone HTML case links point to the configured future HTTPS publication. Before deployment, use the served hub and its HTML reports for working same-origin cases. No candidate HTTPS publication is claimed.

Untagged final PDFs (R42 / #4); stable Safari, physical iPhone, native zoom and VoiceOver NOT_RUN (#1). Broad research and independent final review pending. See evidence/REVIEW_CANDIDATE.md. No PDF/UA or WCAG certification.
''')
files={}
for path in sorted(bundle.rglob('*')):
 if not path.is_file():continue
 relative=path.relative_to(bundle).as_posix()
 assert path.suffix.lower() not in {'.ttf','.otf','.woff','.woff2','.pyc'},relative
 assert not any(part in {'node_modules','__pycache__','.venv','.git'} for part in path.parts),relative
 files[relative]={'sha256':hashfile(path),'bytes':path.stat().st_size}
manifest={'schema':1,'status':'preview with limitations','commit':sha,'included_heads':included,'reportVersion':registry['reportVersion'],'caseVersions':{c['caseId']:c['caseVersion'] for c in registry['cases']},'storage_schema':4,'import_version':1,'build':build,'browsers':browsers,'report_input_digest':read(ROOT/'reports/input-manifest.json')['digest'],'source_authenticity':'Not established by integrity checks; see source register and editorial decisions','independent_review':'PENDING_READ_ONLY_REVIEW','publication':'NOT_DEPLOYED','limits':['R34 service time origin needs company evidence','R42 final PDFs untagged; HTML alternative; issue #4','Stable Safari/physical iPhone/native zoom/VoiceOver NOT_RUN; issue #1','Broad research remains pending; issue #2','Ruleset/security settings proposal not applied; secret scanning and push protection not confirmed'],'file_hash_scope':'All bundle files except this manifest; no self-referential checksum','files':files}
(bundle/'candidate-manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n')
archive_path=a.output/f'{bundle.name}.zip'
with zipfile.ZipFile(archive_path,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=9) as archive:
 for path in sorted(bundle.rglob('*')):
  if path.is_file():archive.write(path,path.relative_to(bundle.parent))
(a.output/'bundle-sha256.txt').write_text(f'{hashfile(archive_path)}  {archive_path.name}\n')
shutil.copy2(bundle/'candidate-manifest.json',a.output/'candidate-manifest.json')
print(archive_path)
