#!/usr/bin/env python3
"""Check the RC3 report entry, narrow charts, citations and frozen return URLs.

Runs against an existing HTTP build at either root or the Pages subpath. Content
parity belongs to verify-reports.py; this suite exercises rendered reader paths.
It never follows source links off the preview origin or changes browser sandbox.
"""

import argparse
from datetime import datetime, timezone
import importlib.metadata
import json
from pathlib import Path
import platform
import re
import subprocess
import sys
import traceback
from urllib.parse import urljoin, urlsplit

from playwright.sync_api import expect, sync_playwright


parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--url', required=True)
parser.add_argument('--browser', choices=['chromium', 'firefox', 'webkit'], default='chromium')
parser.add_argument('--executable')
parser.add_argument('--output', type=Path, required=True)
args = parser.parse_args()
root = Path(__file__).resolve().parents[1]
base = args.url.rstrip('/') + '/'
origin = urlsplit(base).netloc
args.output.mkdir(parents=True, exist_ok=True)

REPORTS = {
    'ASP24': 'ASP24 — Від пошуку до підготовки закупівлі',
    'NGGroup': 'NG Group — Від технічної інформації до вибору рішення',
}
# These are semantic publication contracts, deliberately independent of current
# PDF pagination and the registry from which the build creates its links.
FROZEN_CASES = {
    'six-candidates': ('ASP24', 'asp24-09'),
    'unknown-and-difference': ('ASP24', 'asp24-05'),
    'two-reels': ('ASP24', 'asp24-07'),
    'model-document': ('NGGroup', 'nggroup-09'),
}
VIEWPORTS = [(320, 844), (390, 844), (1440, 900)]
results = {
    'schema': 1,
    'commit': subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=root, text=True).strip(),
    'working_tree_dirty': bool(subprocess.check_output(['git', 'status', '--porcelain'], cwd=root, text=True).strip()),
    'started_at_utc': datetime.now(timezone.utc).isoformat(),
    'browser': args.browser,
    'environment': {
        'platform': platform.platform(),
        'python': platform.python_version(),
        'playwright': importlib.metadata.version('playwright'),
    },
    'url': base,
    'command': [sys.executable, *sys.argv],
    'checks': [],
    'screenshots': [],
    'not_run': ['native Safari', 'physical iPhone', 'native zoom', 'VoiceOver', 'PDF/UA'],
}


def settle(page):
    page.evaluate('() => new Promise(resolve => requestAnimationFrame(() => requestAnimationFrame(resolve)))')


def no_global_overflow(page):
    geometry = page.evaluate('''() => ({viewport: innerWidth,
        document: document.documentElement.scrollWidth, body: document.body.scrollWidth})''')
    assert geometry['document'] <= geometry['viewport'] + 1, geometry
    assert geometry['body'] <= geometry['viewport'] + 1, geometry
    return geometry


def capture(page, name):
    page.screenshot(path=str(args.output / name))
    results['screenshots'].append(name)


def assert_fragment_in_view(page, fragment):
    expect(page).to_have_url(re.compile(r'#' + re.escape(fragment) + r'$'))
    target = page.locator('#' + fragment)
    expect(target).to_be_visible()
    settle(page)
    bounds = target.bounding_box()
    assert bounds is not None and bounds['y'] < page.viewport_size['height'] and bounds['y'] + bounds['height'] > 0, bounds


def hub(page):
    response = page.goto(base, wait_until='networkidle')
    assert response.status == 200
    expect(page.locator('h1')).to_have_text('ASP24 / NG Group')
    expect(page.locator('header .subtitle')).to_have_text('Огляди сайтів і демонстраційні приклади')
    order = page.evaluate('''() => {
        const h = document.querySelector('h1'), s = document.querySelector('header .subtitle');
        const r = document.querySelector('article.report'), c = document.querySelector('.cases');
        const precedes = (a,b) => !!(a && b && (a.compareDocumentPosition(b) & Node.DOCUMENT_POSITION_FOLLOWING));
        return {headingBeforeSubtitle: precedes(h,s), subtitleBeforeReports: precedes(s,r), reportsBeforeCases: precedes(r,c)};
    }''')
    assert all(order.values()), order
    for width, height in VIEWPORTS:
        page.set_viewport_size({'width': width, 'height': height})
        settle(page)
        no_global_overflow(page)
        for report in REPORTS:
            card = page.locator('article.report').filter(has=page.locator(f'a[href$="reports/{report}_Review.html"]'))
            expect(card.get_by_role('link', name='Читати HTML-огляд', exact=True)).to_be_visible()
            expect(card.get_by_role('link', name=re.compile(r'^PDF\b'))).to_be_visible()
        if width in (390, 1440):
            capture(page, f'hub-{width}.png')
    for report, title in REPORTS.items():
        html_link = page.locator(f'a[href$="reports/{report}_Review.html"]')
        expected_url = urljoin(base, f'reports/{report}_Review.html')
        assert urljoin(page.url, html_link.get_attribute('href')) == expected_url
        html_link.click()
        expect(page).to_have_url(expected_url)
        expect(page.locator('h1')).to_have_text(title)
        pdf_link = page.get_by_role('navigation', name='Подання огляду').get_by_role('link', name=re.compile('PDF'))
        pdf_url = urljoin(page.url, pdf_link.get_attribute('href'))
        assert pdf_url == urljoin(base, f'reports/{report}_Review.pdf')
        pdf = page.request.get(pdf_url)
        assert pdf.status == 200 and pdf.body().startswith(b'%PDF-'), {'url': pdf_url, 'status': pdf.status}
        assert 'application/pdf' in pdf.headers.get('content-type', ''), pdf.headers
        page.go_back(wait_until='networkidle')
        expect(page).to_have_url(base)
        expect(page.locator(f'a[href$="reports/{report}_Review.pdf"]')).to_be_visible()
    return {'viewports': [width for width, _ in VIEWPORTS], 'report_actions': list(REPORTS), 'heading_order': order}


def report_layout(report, width, height):
    def check(page):
        page.set_viewport_size({'width': width, 'height': height})
        response = page.goto(urljoin(base, f'reports/{report}_Review.html'), wait_until='networkidle')
        assert response.status == 200
        expect(page.locator('h1')).to_have_text(REPORTS[report])
        assert page.locator('html').get_attribute('lang') in ('uk', 'uk-UA')
        geometry = no_global_overflow(page)
        regions = page.locator('.table-scroll, .chart-scroll').evaluate_all('''els => els.map(el => {
            const labelled = (el.getAttribute('aria-labelledby') || '').split(/\\s+/).filter(Boolean)
                .map(id => document.getElementById(id)?.textContent || '').join(' ').trim();
            return {kind: el.className, role: el.getAttribute('role'), tabIndex: el.tabIndex,
                name: (el.getAttribute('aria-label') || labelled).trim(),
                overflow: getComputedStyle(el).overflowX, client: el.clientWidth, scroll: el.scrollWidth};
        })''')
        assert page.locator('.table-scroll').count() > 0 and page.locator('.chart-scroll').count() > 0
        assert len({region['name'] for region in regions}) == len(regions), regions
        for region in regions:
            assert region['role'] == 'region' and region['tabIndex'] >= 0, region
            assert len(region['name']) > 12 and region['name'] != 'Таблиця, доступна для горизонтального прокручування', region
            if region['scroll'] > region['client'] + 1:
                assert region['overflow'] in ('auto', 'scroll'), region
        chart_metrics = []
        for index in range(page.locator('.chart-scroll').count()):
            chart = page.locator('.chart-scroll').nth(index)
            chart.scroll_into_view_if_needed()
            chart.focus()
            expect(chart).to_be_focused()
            metrics = chart.evaluate('''el => {
                const svg = el.querySelector('svg'), box = svg.getBoundingClientRect();
                const labels = [...svg.querySelectorAll('text')].map(text => {
                    const matrix = text.getScreenCTM(), size = parseFloat(getComputedStyle(text).fontSize);
                    return {text: text.textContent, intrinsic: size,
                        rendered: size * Math.hypot(matrix.c, matrix.d)};
                });
                const table = el.parentElement.querySelector('table');
                return {name: el.getAttribute('aria-label'), client: el.clientWidth, scroll: el.scrollWidth,
                    svgWidth: box.width, viewBoxWidth: svg.viewBox.baseVal.width, labels,
                    hasDataTable: !!(table && table.querySelectorAll('tbody tr').length)};
            }''')
            assert metrics['labels'] and metrics['hasDataTable'], metrics
            assert metrics['svgWidth'] >= metrics['viewBoxWidth'] - 1, metrics
            assert all(label['intrinsic'] >= 16 and label['rendered'] >= 15.9 for label in metrics['labels']), metrics
            if metrics['scroll'] > metrics['client'] + 1:
                chart.press('ArrowRight')
                page.wait_for_function('el => el.scrollLeft > 0', arg=chart.element_handle(), timeout=3000)
                chart.evaluate('el => { el.scrollLeft = 0; }')
            no_global_overflow(page)
            if width in (390, 1440):
                capture(page, f'{report}-chart-{index + 1}-{width}.png')
            chart_metrics.append(metrics)
        return {'viewport': {'width': width, 'height': height}, 'geometry': geometry, 'regions': regions, 'charts': chart_metrics}
    return check


def report_citations(report):
    def check(page):
        report_url = urljoin(base, f'reports/{report}_Review.html')
        page.goto(report_url, wait_until='networkidle')
        citations = page.locator('a.citation').evaluate_all('''els => els.map(el => {
            const href = el.getAttribute('href'), target = document.getElementById(href.slice(1));
            return {href, text: el.textContent.trim(), name: el.getAttribute('aria-label'),
                section: el.closest('section')?.id,
                targetText: target?.textContent.trim(), targetClass: target?.className,
                matchingTargets: document.querySelectorAll('[id="' + href.slice(1) + '"]').length};
        })''')
        assert citations, 'No source citations linked from the report body'
        for citation in citations:
            number = citation['text']
            assert citation['href'] == '#source-' + number and citation['name'] == 'Джерело ' + number, citation
            assert citation['matchingTargets'] == 1 and citation['targetClass'] == 'source', citation
            assert citation['targetText'].startswith('[' + number + ']'), citation
        # Exercise two different sources, including a later citation. Every href
        # above is validated, while actual clicks check fragment history/return.
        selected = [citations[0]]
        later = next((citation for citation in reversed(citations) if citation['href'] != selected[0]['href']), None)
        if later:
            selected.append(later)
        for citation in selected:
            page.goto(report_url + '#' + citation['section'], wait_until='networkidle')
            link = page.locator('#' + citation['section']).locator(f'a.citation[href="{citation["href"]}"]').first
            link.click()
            assert_fragment_in_view(page, citation['href'][1:])
            expect(page.locator(citation['href'])).to_contain_text('[' + citation['text'] + ']')
            page.go_back(wait_until='networkidle')
            assert_fragment_in_view(page, citation['section'])
        return {'validated_citations': len(citations), 'clicked_sources': [citation['href'] for citation in selected]}
    return check


def frozen_return(case_id, report, section_id):
    def check(page):
        report_url = urljoin(base, f'reports/{report}_Review.html') + '#' + section_id
        page.goto(report_url, wait_until='networkidle')
        section = page.locator('#' + section_id)
        expect(section).to_have_count(1)
        link = section.locator(f'a[href*="cases/{case_id}/v1/"]').first
        expect(link).to_be_visible()
        assert urljoin(page.url, link.get_attribute('href')) == urljoin(base, f'cases/{case_id}/v1/')
        link.click()
        page.wait_for_load_state('networkidle')
        return_link = page.get_by_role('link', name='Повернутися до розділу огляду', exact=True)
        assert urljoin(page.url, return_link.get_attribute('href')) == report_url
        return_link.click()
        assert_fragment_in_view(page, section_id)
        page.go_back(wait_until='networkidle')
        page.get_by_role('link', name='Відкрити приклад', exact=True).click()
        page.wait_for_load_state('networkidle')
        banner = page.locator('.case-banner')
        expect(banner).to_be_visible()
        active_return = banner.get_by_role('link', name='Повернутися до розділу огляду', exact=True)
        assert urljoin(page.url, active_return.get_attribute('href')) == report_url
        active_return.click()
        assert_fragment_in_view(page, section_id)
        no_global_overflow(page)
        return {'case': case_id, 'frozen_section': section_id, 'landing_and_active_return': report_url}
    return check


checks = [('hub-ukrainian-hierarchy-html-pdf-actions', hub)]
checks += [(f'{report}-layout-{width}', report_layout(report, width, height))
           for report in REPORTS for width, height in VIEWPORTS]
checks += [(f'{report}-source-citation-click-back', report_citations(report)) for report in REPORTS]
checks += [(f'{case_id}-frozen-section-return', frozen_return(case_id, report, section_id))
           for case_id, (report, section_id) in FROZEN_CASES.items()]

with sync_playwright() as playwright:
    try:
        options = {'chromium_sandbox': True} if args.browser == 'chromium' else {}
        if args.executable:
            options['executable_path'] = args.executable
        browser = getattr(playwright, args.browser).launch(timeout=30000, **options)
    except Exception as error:
        results.update(status='BLOCKED', launch_error=str(error))
    else:
        results['browser_version'] = browser.version
        for name, check in checks:
            context = browser.new_context(viewport={'width': 390, 'height': 844})
            context.set_default_timeout(12000)
            context.tracing.start(screenshots=True, snapshots=True, sources=True)
            errors = []

            def local_only(route):
                if urlsplit(route.request.url).netloc == origin:
                    route.continue_()
                else:
                    errors.append('Unexpected outbound request: ' + route.request.url)
                    route.abort()

            context.route('**/*', local_only)
            page = context.new_page()
            page.on('pageerror', lambda error: errors.append(str(error)))
            try:
                details = check(page)
                assert not errors, errors
            except Exception as error:
                failure = {'name': name, 'status': 'FAIL', 'error': str(error),
                           'traceback': traceback.format_exc(), 'page_errors': errors}
                try:
                    capture(page, name + '-failure.png')
                    context.tracing.stop(path=str(args.output / (name + '-trace.zip')))
                except Exception as capture_error:
                    failure['capture_error'] = str(capture_error)
                results['checks'].append(failure)
                print('FAIL', name, str(error), flush=True)
            else:
                context.tracing.stop()
                results['checks'].append({'name': name, 'status': 'PASS', 'details': details})
                print('PASS', name, flush=True)
            finally:
                context.close()
        browser.close()
        results['status'] = 'FAIL' if any(check['status'] == 'FAIL' for check in results['checks']) else 'PASS'

results['completed_at_utc'] = datetime.now(timezone.utc).isoformat()
(args.output / 'results.json').write_text(json.dumps(results, ensure_ascii=False, indent=2) + '\n')
print(results['status'], args.output / 'results.json', flush=True)
raise SystemExit(0 if results['status'] == 'PASS' else 2 if results['status'] == 'BLOCKED' else 1)
