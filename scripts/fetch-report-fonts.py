"""Retrieve pinned official LibreOffice source archives into an external directory."""
from pathlib import Path
import argparse,hashlib,io,json,urllib.request,zipfile
R=Path(__file__).resolve().parent.parent
p=argparse.ArgumentParser();p.add_argument('directory',type=Path);a=p.parse_args();a.directory.mkdir(parents=True,exist_ok=True)
expected={f['file']:f['sha256'] for f in json.loads((R/'reports/fonts/provenance.json').read_text())['fonts']}
for archive in json.loads((R/'reports/fonts/downloads.json').read_text())['archives']:
    if all((a.directory/f).exists() and hashlib.sha256((a.directory/f).read_bytes()).hexdigest()==expected[f] for f in archive['files']):continue
    raw=urllib.request.urlopen(archive['url'],timeout=60).read();assert hashlib.sha256(raw).hexdigest()==archive['sha256'],'Archive hash mismatch'
    z=zipfile.ZipFile(io.BytesIO(raw))
    for name in archive['files']:
        matches=[n for n in z.namelist() if Path(n).name==name and hashlib.sha256(z.read(n)).hexdigest()==expected[name]]
        assert matches, 'Exact font not found: '+name
        (a.directory/name).write_bytes(z.read(matches[0]))
print('PASS exact external report fonts; no binaries copied into repository')
