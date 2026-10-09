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
BASELINE = 'b320abc302ed895704db2437ce7dbe3a6964e603'
SUITES = {
    'regression': 'results.json',
    'cases': 'cases/results.json',
    'case_storage': 'case-storage/results.json',
    'modern': 'modern/results.json',
    'rc3': 'rc3/results.json',
    'reports_rc3': 'reports-rc3/results.json',
    'hardening': 'hardening/results.json',
    'workbench_hardening': 'workbench-hardening/results.json',
    'lazy_science': 'lazy-science/results.json',
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
                           'private', 'backups', '.aws', '.openai'} for part in relative.parts), relative
    # This tracked, public README describes the intake policy. No submitted
    # material or other inbox file is permitted in the review bundle.
    assert 'inbox' not in relative.parts or relative.as_posix() == 'source/research/inbox/README.md', relative
    assert not path.name.startswith(('.env', 'cookies', 'storage-state', 'storageState')), relative


def selected_browser_evidence(relative):
    """Keep every result/log and the screenshots addressing RC3's changed views."""
    return relative.suffix.lower() in {'.json', '.log', '.txt'} or (
        relative.suffix.lower() == '.png' and len(relative.parts) >= 3
        and relative.parts[1] in {'rc3', 'reports-rc3', 'hardening', 'workbench-hardening', 'lazy-science'}
    )


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
    native = read(args.build / 'build-evidence/native-renderer.json')
    native_profile = read(ROOT / 'reports/native-runtime.json')
    assert native['status'] == 'PASS' and native['packages'] == native_profile['packages']
    assert native['base_image'] == native_profile['base_image'], 'Wrong native PDF renderer'
    for base in ['pages', 'root', 'baseline']:
        assert inventory(args.build / base / 'dist') == read(args.build / f'build-evidence/{base}-sha256.json'), f'{base} dist differs from tested bytes'
    reproduction = read(args.build / 'build-evidence/verification/report-reproduction.json')
    assert reproduction['status'] == 'PASS' and len(reproduction['compared']) >= 4
    assert set(reproduction['negative_checks']) == {'content change rejected', 'template change rejected'}, 'Both meaningful stale-output checks are required'
    structured = read(args.build / 'build-evidence/verification/reports/structured-pdf-validation.json')
    assert structured['status'] == 'PASS', 'Structured PDFs must pass the independent machine gate'
    assert structured['manuscript_sha256'] == digest(ROOT / 'reports/content.json')
    for brand in ['ASP24', 'NGGroup']:
        report = structured['reports'][brand]
        assert report['status'] == 'PASS' and report['verapdf_ua1']['status'] == 'PASS', (brand, 'Structural or veraPDF UA-1 validation failed')
        assert report['sha256'] == digest(args.build / 'pages/dist/reports' / f'{brand}_Review.pdf'), (brand, 'Different PDF validation bytes')
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
    comparison = read(args.evidence / 'chromium/performance/hardening-comparison.json')
    assert comparison['commit'] == sha and comparison['baseline_sha'] == BASELINE and comparison['status'] == 'PASS'
    assert not comparison['working_tree_changes'], 'Comparative performance used modified source'
    assert {path: info['sha256'] for path, info in comparison['dist_files']['candidate'].items()} == inventory(args.build / 'pages/dist'), 'Comparative performance used different candidate bytes'
    assert {path: info['sha256'] for path, info in comparison['dist_files']['baseline'].items()} == inventory(args.build / 'baseline/dist'), 'Comparative performance used different baseline bytes'
    assert len(comparison['samples']) == 30, 'Five paired repeats of desktop/mobile comparison and hub required'

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
    for path in sorted(args.evidence.rglob('*')):
        if path.is_file() and selected_browser_evidence(path.relative_to(args.evidence)):
            destination = bundle / 'evidence/browser' / path.relative_to(args.evidence)
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(path, destination)
    editorial = bundle / 'evidence/editorial'
    editorial.mkdir()
    for name in ['reports/rc3-visual-review.json', 'reports/hardening-pdf-acceptance.json', 'reports/hardening-renderer-acceptance.json', 'reports/editorial-validation.json',
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
Усі JSON-результати й журнали дев'яти suites збережені. Компактний пакет включає
скриншоти `rc3/`, `reports-rc3/` та нових hardening suites; повні скриншоти попередніх
suites доступні в артефактах `rc3-browser-<engine>-{sha}` точного CI-запуску:
{build['run_url']}
Звужено лише склад зображень пакета; gates для всіх дев’яти suites залишаються повними.
Коренева збірка перевірена окремо; її SHA inventory є в evidence/build.
`rc3-manifest.json` містить SHA-256 файлів. Контроль суми доводить байти, а не істинність джерел.

R34 — OPEN_EXTERNAL_SOURCE. R42 закрито щодо структурного тегування після
структурної, текстової та візуальної перевірки обох PDF. veraPDF UA-1 PASS —
результат машинного профілю; читання допоміжною технологією — NOT_RUN.
Native Safari/macOS/iOS, фізичний iPhone, Chrome Android, Telegram iOS/Android,
WKWebView/Android WebView, native zoom та VoiceOver — NOT_RUN.
WebKit не замінює ці перевірки. Performance містить порівняння з прийнятим RC3
на одному runner; висновки обмежені виміряними лабораторними метриками.
Інструкція власнику та питання R34: `source/docs/FINAL_HARDENING.md`.
''')
    files = {}
    for path in sorted(bundle.rglob('*')):
        if path.is_file():
            safe_file(path, bundle)
            files[path.relative_to(bundle).as_posix()] = {'sha256': digest(path), 'bytes': path.stat().st_size}
    manifest = {
        'schema': 1, 'kind': 'integrated-rc3-hardening-http-preview', 'commit': sha,
        'baseline_sha': BASELINE, 'status': 'READY_FOR_INDEPENDENT_REVIEW',
        'publication': 'PREVIEW_NOT_DEPLOYED', 'independent_review': 'PENDING',
        'build': build, 'browsers': browsers,
        'evidence_scope': {
            'included': 'All build and structured-PDF evidence; all browser JSON/results/logs; rc3, reports-rc3 and hardening PNG screenshots for each engine',
            'complete_browser_screenshots': {
                'run_url': build['run_url'],
                'artifact_names': [f'rc3-browser-{browser}-{sha}' for browser in ['chromium', 'firefox', 'webkit']],
            },
            'gates': 'All nine suites per engine must pass on this SHA before any evidence selection; no failures are omitted or reclassified',
        },
        'report_version': read(ROOT / 'publication.json')['reportVersion'],
        'report_input_digest': read(ROOT / 'reports/input-manifest.json')['digest'],
        'report_source_sha256': digest(ROOT / 'reports/content.json'),
        'performance': {'status': performance['status'], 'path': 'evidence/browser/chromium/performance/performance.json',
                        'interpretation': performance['interpretation'],
                        'comparison_path': 'evidence/browser/chromium/performance/hardening-comparison.json',
                        'comparison_baseline_sha': BASELINE},
        'pdf_accessibility': {'status': 'STRUCTURAL_TAGGING_VERIFIED',
                              'r42': 'CLOSED_STRUCTURAL_TAGGING',
                              'machine_profile': 'veraPDF PDF/UA-1 PASS for both PDFs',
                              'assistive_reading': 'NOT_RUN',
                              'evidence': 'evidence/build/verification/reports/structured-pdf-validation.json'},
        'contracts': {'state_schema': 4, 'project_import_version': 1, 'personal_key': 'perspective-demo-v1',
                      'max_candidates': 6, 'project_limit': 64, 'catalogue_models': 384,
                      'manufacturers': 13, 'categories': 8},
        'limitations': ['R34 OPEN_EXTERNAL_SOURCE: service-time origin unresolved',
                        'Native Safari macOS/iOS / physical iPhone / Chrome Android / Telegram iOS/Android / WKWebView / Android WebView NOT_RUN',
                        'Assistive PDF reading / native zoom / VoiceOver NOT_RUN; machine PDF/UA-1 validation is a separate result',
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
