"""Install the pinned renderer only inside the explicitly selected CI container."""
import argparse
import json
import os
from pathlib import Path
import platform
import subprocess

ROOT = Path(__file__).resolve().parents[1]
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--output', type=Path, required=True)
args = parser.parse_args()
assert os.environ.get('REPORT_RENDER_CONTAINER') == '1', 'Use the pinned report build container; do not run on the host'
profile = json.loads((ROOT / 'reports/native-runtime.json').read_text())
assert subprocess.check_output(['dpkg', '--print-architecture'], text=True).strip() == profile['architecture']
assert 'VERSION_CODENAME=trixie' in Path('/etc/os-release').read_text()
assert platform.python_version() == '3.12.14'
environment = dict(os.environ, DEBIAN_FRONTEND='noninteractive')
subprocess.run(['apt-get', 'update'], check=True, env=environment)
subprocess.run(['apt-get', 'install', '-y', '--no-install-recommends',
                *[f'{name}={version}' for name, version in profile['packages'].items()]],
               check=True, env=environment)
versions = subprocess.check_output(['dpkg-query', '-W', '-f=${binary:Package}\t${Version}\n',
                                    *profile['packages']], text=True)
observed = {name.split(':')[0]: version for name, version in
            (line.split('\t') for line in versions.splitlines())}
assert observed == profile['packages'], 'Installed native versions differ from the pinned profile'
args.output.parent.mkdir(parents=True, exist_ok=True)
args.output.write_text(json.dumps({'status': 'PASS', 'python': platform.python_version(),
                                  'base_image': profile['base_image'], 'packages': observed}, indent=2) + '\n')
print('PASS pinned native renderer packages')
