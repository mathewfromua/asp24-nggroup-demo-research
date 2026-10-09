#!/usr/bin/env python3
"""Package exact-SHA RC3 outputs and observed evidence without rebuilding dist."""
import argparse
import hashlib
import io
import json
from pathlib import Path
import shutil
import subprocess
import tarfile
import zipfile

ROOT = Path(__file__).resolve().parents[1]
BASELINE = 'a659d2f9e8d923a7bc64a3f91133cfed959e9181'
SUITES = {
    'regression': 'results.json',
    'cases': 'cases/results.json',
    'case_storage': 'case-storage/results.json',
    'modern': 'modern/results.json',
    'rc3': 'rc3/results.json',
    'reports_rc3': 'reports-rc3/results.json',
}


def read(path):
    return json.loads(path.read_text())


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def inventory(directory):
    return {path.relative_to(directory).as_posix(): digest(path)
            for path in sorted(directory.rglob('*')) if path.is_file()}


def safe_file(path, base):
    relative = path.relative_to(base)
    assert not path.is_symlink(), relative
    assert path.suffix.lower() not in {
        '.ttf', '.otf', '.woff', '.woff2', '.pyc', '.pem', '.key', '.p12', '.pfx',
        '.zip', '.tar', '.gz', '.7z', '.har', '.bundle',
    }, relative
    assert not any(part in {'node_modules', '__pycache__', '.venv', '.git', '.auth',
                           'private', 'backups', 'inbox', '.aws', '.openai'} for part in relative.parts), relative
    assert not path.name.startswith(('.env', 'cookies', 'storage-state', 'storageState')), relative


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--build', type=Path, required=True, help='Downloaded rc3-build artifact')
    parser.add_argument('--evidence', type=Path, required=True, help='Browser directories named chromium/firefox/webkit')
    parser.add_argument('--output', type=Path, default=ROOT / 'output/rc3-preview')
    args = parser.parse_args()
    sha = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()
    assert not subprocess.check_output(['git', 'diff', '--name-only', 'HEAD'], cwd=ROOT), 'Commit tracked inputs before packaging'
    subprocess.run(['git', 'merge-base', '--is-ancestor', BASELINE, sha], cwd=ROOT, check=True)
    build = read(args.build / 'build-evidence/build-result.json')
    assert build['commit'] == sha and build['status'] == 'PASS', 'Build evidence must identify the exact successful commit'
    for base in ['pages', 'root']:
        assert inventory(args.build / base / 'dist') == read(args.build / f'build-evidence/{base}-sha256.json'), f'{base} dist differs from tested bytes'
    reproduction = read(args.build / 'build-evidence/verification/report-reproduction.json')
    assert reproduction['status'] == 'PASS' and len(reproduction['compared']) >= 4
    assert set(reproduction['negative_checks']) == {'content change rejected', 'template change rejected'}, 'Both meaningful stale-output checks are required'
    browsers = {}
    for browser in ['chromium', 'firefox', 'webkit']:
        run = read(args.evidence / browser / 'browser-run.json')
        assert run['commit'] == sha and run['browser'] == browser and run['status'] == 'PASS'
        assert not run['working_tree_dirty'], (browser, 'browser run used modified source')
        assert run['dist_sha256'] == inventory(args.build / 'pages/dist'), (browser, 'browser run used different dist bytes')
        assert read(args.evidence / browser / 'served-dist-sha256.json') == run['dist_sha256'], (browser, 'HTTP delivered different dist bytes')
        browsers[browser] = {}
        for name, relative in SUITES.items():
            result = read(args.evidence / browser / relative)
            assert result['commit'] == sha and result['status'] == 'PASS', (browser, name, 'wrong commit or unsuccessful suite')
            assert result['browser'] == browser, (browser, name, 'wrong engine')
            assert not result.get('working_tree_dirty', False), (browser, name, 'suite used modified source')
            assert result['checks'] and all(check['status'] == 'PASS' for check in result['checks']), (browser, name, 'incomplete checks')
            browsers[browser][name] = {'status': result['status'], 'checks': len(result['checks']), 'path': f'evidence/browser/{browser}/{relative}'}
    performance = read(args.evidence / 'chromium/performance/performance.json')
    assert performance['commit'] == sha and performance['status'] == 'PASS', 'Scoped performance observation did not finish'
    assert len(performance['samples']) == 9, 'Three repeats of hub and both case viewports required'
    assert {name: info['sha256'] for name, info in performance['dist_files'].items()} == inventory(args.build / 'pages/dist'), 'Performance used different dist bytes'

    pages_dist = args.build / 'pages/dist'
    standalone = args.build / 'standalone'
    for entry in read(ROOT / 'reports/standalone-manifest.json'):
        name = Path(entry['html']).name
        assert digest(standalone / name) == entry['sha256'], name
        assert digest(pages_dist / 'reports' / name) == entry['public_html_sha256'], name
    for brand in ['ASP24', 'NGGroup']:
        name = f'{brand}_Review.pdf'
        assert digest(standalone / name) == digest(pages_dist / 'reports' / name), name
    visual = read(ROOT / 'reports/rc3-visual-review.json')
    assert visual['status'] == 'PASS', 'Complete the actual rendering review before packaging'
    assert visual['content_sha256'] == digest(ROOT / 'reports/content.json'), 'Visual review used an older manuscript'
    assert visual['input_digest'] == read(ROOT / 'reports/input-manifest.json')['digest'], 'Visual review used older report inputs'
    pdf_manifests = {entry['file'].split('_')[0]: entry for entry in read(ROOT / 'reports/pdf-manifest.json')}
    for brand in ['ASP24', 'NGGroup']:
        assert visual['pdf_sha256'][brand] == digest(pages_dist / 'reports' / f'{brand}_Review.pdf'), (brand, 'Visual review used different PDF bytes')
        assert visual['html_sha256'][brand] == digest(pages_dist / 'reports' / f'{brand}_Review.html'), (brand, 'Visual review used different HTML bytes')
        count = pdf_manifests[brand]['pages']
        assert visual['pages'][brand] == count, (brand, 'Visual review page count is stale')
        assert sorted(visual['reviewed_pages'][brand]) == list(range(1, count + 1)), (brand, 'Review every final PDF page')
    args.output.mkdir(parents=True, exist_ok=False)
    bundle = args.output / f'asp24-nggroup-rc3-{sha}'
    bundle.mkdir()
    source = bundle / 'source'
    source.mkdir()
    archive = subprocess.check_output(['git', 'archive', sha], cwd=ROOT)
    with tarfile.open(fileobj=io.BytesIO(archive)) as tar:
        tar.extractall(source, filter='data')
    shutil.copytree(pages_dist, bundle / 'dist')
    shutil.copytree(standalone, bundle / 'reports')
    shutil.copytree(args.build / 'build-evidence', bundle / 'evidence/build')
    shutil.copytree(args.evidence, bundle / 'evidence/browser')
    editorial = bundle / 'evidence/editorial'
    editorial.mkdir()
    for name in ['reports/rc3-visual-review.json', 'reports/editorial-validation.json',
                 'research/editorial-decisions.json', 'research/editorial-source-register.json']:
        shutil.copy2(ROOT / name, editorial / Path(name).name)
    (bundle / 'scripts').mkdir()
    for name in ['serve.mjs', 'deployment-config.mjs']:
        shutil.copy2(ROOT / 'scripts' / name, bundle / 'scripts' / name)
    shutil.copy2(ROOT / 'deployment.config.json', bundle / 'deployment.config.json')
    shutil.copy2(ROOT / 'THIRD_PARTY_NOTICES.md', bundle / 'THIRD_PARTY_NOTICES.md')
    (bundle / 'START_HERE_UA.md').write_text(f'''# ASP24 / NG Group — RC3 для незалежного перегляду

Точний SHA: `{sha}`. Джерела: https://github.com/mathewfromua/asp24-nggroup-demo-research/tree/{sha}
Статус публікації: **PREVIEW_NOT_DEPLOYED**. Main та GitHub Pages не змінено.
Приймання незалежним рецензентом ще не виконано.

Спочатку відкрийте два PDF та самодостатні HTML у `reports/`.
Для робочих кейсів встановіть Node 24 та з цієї розпакованої папки виконайте:

```sh
node scripts/serve.mjs --host 127.0.0.1 --port 8000
```

Адреса: http://127.0.0.1:8000/asp24-nggroup-demo-research/
Встановлення npm-пакетів не потрібне. Не відкривайте інтерактивні ESM-сторінки через file://.
Посилання на кейси в PDF та самодостатніх HTML ведуть на налаштовану майбутню
HTTPS-публікацію. До дозволеної публікації користуйтеся HTML-оглядами HTTP-preview.

`dist/` — повні незмінні байти перевіреної збірки для підкаталогу.
`source/` — git archive точного SHA, включно з рукописом, input/output manifests,
джерельним реєстром і таблицею редакційних рішень. Для відтворення з джерел
потрібні Node 24, npm ci, pinned Python 3.12.14/packages і перевірені зовнішні шрифти.
Шрифти, кеші, приватний handoff-архів і профілі браузерів не включені.
`evidence/` — фактичні build/HTTP/Node/report/browser результати та скриншоти.
Коренева збірка перевірена окремо; її SHA inventory є в evidence/build.
`rc3-manifest.json` містить SHA-256 файлів. Контроль суми доводить байти, а не істинність джерел.

R34 залишається OPEN; фінальні PDF untagged (R42), HTML — семантична альтернатива.
Stable Safari, фізичний iPhone, native zoom, VoiceOver і PDF/UA — NOT_RUN.
WebKit не замінює ці перевірки. Performance PASS означає завершений локальний
вимір bytes/LCP; прискорення, польовий INP чи ефект конверсії не стверджуються.
''')
    files = {}
    for path in sorted(bundle.rglob('*')):
        if path.is_file():
            safe_file(path, bundle)
            files[path.relative_to(bundle).as_posix()] = {'sha256': digest(path), 'bytes': path.stat().st_size}
    manifest = {
        'schema': 1, 'kind': 'integrated-rc3-http-preview', 'commit': sha,
        'baseline_sha': BASELINE, 'status': 'READY_FOR_INDEPENDENT_REVIEW',
        'publication': 'PREVIEW_NOT_DEPLOYED', 'independent_review': 'PENDING',
        'build': build, 'browsers': browsers,
        'report_version': read(ROOT / 'publication.json')['reportVersion'],
        'report_input_digest': read(ROOT / 'reports/input-manifest.json')['digest'],
        'report_source_sha256': digest(ROOT / 'reports/content.json'),
        'performance': {'status': performance['status'], 'path': 'evidence/browser/chromium/performance/performance.json',
                        'interpretation': performance['interpretation']},
        'contracts': {'state_schema': 4, 'project_import_version': 1, 'personal_key': 'perspective-demo-v1',
                      'max_candidates': 6, 'project_limit': 64, 'catalogue_models': 384,
                      'manufacturers': 13, 'categories': 8},
        'limitations': ['R34 service-time origin unresolved', 'R42 final PDFs untagged; semantic HTML alternative',
                        'Stable Safari / physical iPhone / native zoom / VoiceOver / PDF-UA NOT_RUN',
                        'Synthetic catalogue; no real commerce or conversion claim', 'Public release not verified or authorized'],
        'file_hash_scope': 'Every bundle file except this manifest; no self-referential checksum',
        'files': files,
    }
    (bundle / 'rc3-manifest.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + '\n')
    zip_path = args.output / f'{bundle.name}.zip'
    with zipfile.ZipFile(zip_path, 'w', compression=zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
        for path in sorted(bundle.rglob('*')):
            if path.is_file():
                archive.write(path, path.relative_to(bundle.parent))
    assert zip_path.stat().st_size < 32 * 1024 * 1024, 'Review ZIP exceeds 32 MiB; move oversized diagnostic traces into separate CI artifacts'
    (args.output / 'bundle-sha256.txt').write_text(f'{digest(zip_path)}  {zip_path.name}\n')
    shutil.copy2(bundle / 'rc3-manifest.json', args.output / 'rc3-manifest.json')
    print(json.dumps({'commit': sha, 'files': len(files), 'zip_bytes': zip_path.stat().st_size, 'output': str(zip_path)}, ensure_ascii=False))


if __name__ == '__main__':
    main()
