"""Regenerate in a temporary clean tree; byte comparison and meaningful stale-input failures."""
from pathlib import Path
import json,subprocess,tempfile,shutil,os,sys,hashlib
R=Path(__file__).resolve().parent.parent
sys.path.insert(0,str(R/'reports'))
from build_inputs import inventory,verify_environment
verify_environment()
assert json.loads((R/'reports/input-manifest.json').read_text())==inventory()
with tempfile.TemporaryDirectory(prefix='report-control-') as temp:
    target=Path(temp)
    # Includes current tracked modifications; CI checks out the immutable reviewed SHA.
    files=subprocess.check_output(['git','ls-files','-z'],cwd=R).decode().split('\0')
    files+=list(inventory()['files'])+['reports/input-manifest.json']
    for name in set(filter(None,files)):
        src=R/name
        if src.is_file():dst=target/name;dst.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(src,dst)
    # Build verification uses the same npm-ci toolchain, without network or a mutable
    # install in the temporary control tree. Source and generated reports stay isolated.
    assert (R/'node_modules/vite').is_dir(), 'Run npm ci before report reproduction'
    (target/'node_modules').symlink_to(R/'node_modules',target_is_directory=True)
    def run(args,ok=True):
        r=subprocess.run(args,cwd=target,text=True,capture_output=True)
        assert (r.returncode==0)==ok, r.stdout[-2000:]+r.stderr[-2000:]
    for script in ['build_editorial.py','build_html.py','export_standalone.py']:run([sys.executable,'reports/'+script])
    compared=[]
    for path in sorted((R/'public/reports').rglob('*')):
        if path.is_file():
            name=path.relative_to(R);assert path.read_bytes()==(target/name).read_bytes(),f'Control generation differs: {name}'
            compared.append(str(name))
    run(['node','scripts/build-static.mjs']);run(['node','scripts/verify-build.mjs'])
    for name in ['reports/content.json','reports/build_html.py']:
        p=target/name;original=p.read_bytes();p.write_bytes(original+b'\n');run(['node','scripts/verify-build.mjs'],ok=False);p.write_bytes(original)
    result={'status':'PASS','control_generation':'byte-identical with pinned Python/packages/fonts','compared':compared,'negative_checks':['content change rejected','template change rejected'],'normalization':'No output byte normalization. ReportLab invariant=1 fixes timestamps/IDs; paths are relative. Different renderer/font bytes are not equivalent.','source_authenticity':'NOT_TESTED_BY_INTEGRITY'}
    out=R/'output/verification';out.mkdir(parents=True,exist_ok=True);(out/'report-reproduction.json').write_text(json.dumps(result,indent=2)+'\n')
print('PASS independent control generation and two negative stale-output checks')
