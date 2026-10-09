"""Full report-generator input contract; deterministic paths and SHA-256, no clock."""
from pathlib import Path
import hashlib,json,platform,importlib.metadata,os
ROOT=Path(__file__).resolve().parent.parent

def inventory():
    paths=['deployment.config.json','reports/content.json','reports/content.py','reports/build_editorial.py','reports/build_html.py','reports/export_standalone.py','reports/build_inputs.py','reports/requirements.txt','reports/fonts/provenance.json','reports/fonts/downloads.json']
    if (ROOT/'publication.json').exists(): paths.append('publication.json')
    for directory in ['reports/assets','reports/covers','evidence/figure_data']:
        paths += [p.relative_to(ROOT).as_posix() for p in (ROOT/directory).rglob('*') if p.is_file() and '__pycache__' not in p.parts]
    files={p:hashlib.sha256((ROOT/p).read_bytes()).hexdigest() for p in sorted(paths)}
    return {'schema':1,'files':files,'digest':hashlib.sha256(json.dumps(files,sort_keys=True,separators=(',',':')).encode()).hexdigest()}

def verify_environment():
    assert platform.python_version()=='3.12.14', 'Pinned Python 3.12.14 required for control generation'
    for line in (ROOT/'reports/requirements.txt').read_text().splitlines():
        if line and not line.startswith('#'):
            name,version=line.split('==');assert importlib.metadata.version(name)==version,(name,version)
    directory=Path(os.environ.get('REPORT_FONT_DIR',os.environ.get('PERSPEKTYVA_FONT_DIR',ROOT/'reports/fonts')))
    for font in json.loads((ROOT/'reports/fonts/provenance.json').read_text())['fonts']:
        assert hashlib.sha256((directory/font['file']).read_bytes()).hexdigest()==font['sha256'],font['file']

if __name__=='__main__':
    import argparse
    p=argparse.ArgumentParser();p.add_argument('--write',action='store_true');a=p.parse_args()
    current=inventory();path=ROOT/'reports/input-manifest.json'
    if a.write:verify_environment();path.write_text(json.dumps(current,indent=2)+'\n')
    else:assert json.loads(path.read_text())==current,'Outdated generator inputs; regenerate PDF/HTML'
    print('PASS report input digest',current['digest'])
