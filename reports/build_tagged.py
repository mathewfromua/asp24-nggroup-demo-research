"""Structured report export, developed from scripts/tagged-reports-experiment.py.

The HTML and PDF share content.json.  The print adapter changes layout only.
Accepted covers retain their original vector/text operators and embedded fonts;
the five existing text objects receive real structure tags in reading order.
"""
from __future__ import annotations

import argparse
import base64
import csv
import hashlib
import html
import json
import os
from pathlib import Path
import re
from urllib.parse import urljoin

from pypdf import PdfReader, PdfWriter
from pypdf.generic import (ArrayObject, ContentStream, DictionaryObject,
                          BooleanObject, NameObject, NullObject, NumberObject, TextStringObject)
from weasyprint import HTML, __version__ as weasyprint_version
from weasyprint.urls import URLFetcher

from build_inputs import inventory
from content import REPORTS, PUBLIC_BASE_URL

ROOT = Path(__file__).resolve().parents[1]
HERE = ROOT / "reports"


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def cover_structure(writer, brand):
    """Keep the accepted cover artwork and add a complete, non-raster structure.

    Original painting order starts with the footer.  MCIDs are assigned in
    visual reading order and the structure tree follows that order, independently
    of painting order.  Every non-text operation belongs to an Artifact.
    """
    original = PdfReader(HERE / "covers" / f"{brand}.pdf")
    cover = original.pages[0]
    page = writer.pages[0]
    stream = ContentStream(cover["/Contents"], original)
    assert sum(op == b"BT" for _, op in stream.operations) == 5
    assert sum(op == b"ET" for _, op in stream.operations) == 5
    order = [4, 0, 1, 2, 3]  # original: footer, brand, type, title, subtitle
    tags = ["/P", "/P", "/H1", "/P", "/P"]
    operations = [([NameObject("/Artifact")], b"BMC")]
    text_index = 0
    for operands, operator in stream.operations:
        if operator == b"BT":
            mcid = order[text_index]
            operations.extend([
                ([], b"EMC"),
                ([NameObject(tags[mcid]), DictionaryObject({NameObject("/MCID"): NumberObject(mcid)})], b"BDC"),
            ])
            text_index += 1
        operations.append((operands, operator))
        if operator == b"ET":
            operations.extend([([], b"EMC"), ([NameObject("/Artifact")], b"BMC")])
    operations.append(([], b"EMC"))
    stream.operations = operations
    page[NameObject("/Contents")] = writer._add_object(stream.clone(writer))
    page[NameObject("/Resources")] = cover["/Resources"].clone(writer)
    page[NameObject("/Tabs")] = NameObject("/S")
    root = writer._root_object["/StructTreeRoot"]
    document = root["/K"][0].get_object()
    section = DictionaryObject({NameObject("/Type"): NameObject("/StructElem"),
                                NameObject("/S"): NameObject("/Sect"),
                                NameObject("/P"): document.indirect_reference})
    section_ref = writer._add_object(section)
    refs = ArrayObject()
    for mcid, tag in enumerate(tags):
        element = DictionaryObject({NameObject("/Type"): NameObject("/StructElem"),
                                    NameObject("/S"): NameObject(tag),
                                    NameObject("/P"): section_ref,
                                    NameObject("/Pg"): page.indirect_reference,
                                    NameObject("/K"): NumberObject(mcid)})
        refs.append(writer._add_object(element))
    section[NameObject("/K")] = refs
    document["/K"].insert(0, section_ref)
    parent_tree = root["/ParentTree"]
    nums = parent_tree["/Nums"]
    keys = [int(nums[i]) for i in range(0, len(nums), 2)]
    key = max(keys, default=-1) + 1
    nums.extend([NumberObject(key), refs])
    page[NameObject("/StructParents")] = NumberObject(key)
    root[NameObject("/ParentTreeNextKey")] = NumberObject(key + 1)
    writer._root_object[NameObject("/Lang")] = TextStringObject("uk-UA")
    writer._root_object[NameObject("/MarkInfo")] = DictionaryObject({NameObject("/Marked"): BooleanObject(True)})


def print_chart(kind, alternative, palette):
    """The accepted PDF chart geometry, expressed as vector SVG, with real text."""
    width = 493.2756
    height = 150 if kind == 'history' else 124
    ink, accent = palette['ink'], palette.get('chart-accent', palette['accent'])
    parts = [f'<svg viewBox="0 0 {width} {height}" role="img"><title>{html.escape(alternative)}</title>']
    def text(x, y, value, size=10.5, weight=400, anchor='start'):
        parts.append(f'<text x="{x}" y="{y}" font-size="{size}" font-weight="{weight}" text-anchor="{anchor}" fill="{ink}">{html.escape(str(value))}</text>')
    if kind == 'history':
        rows = list(csv.DictReader((ROOT/'evidence/figure_data/technical_rows.csv').open()))
        labels = {'MED001988': 'RG-EW1200G Pro', 'MED005534': 'XPON Stick', 'MED000715': 'Cu-кабель'}
        for index, (sku, label) in enumerate(labels.items()):
            y = 15 + index * 47
            text(0, y, label, 10, 700)
            text(0, y+14, sku, 9)
            pair = [row for row in rows if row['sku'] == sku]
            for row, yy, filled in [(next(r for r in pair if r['side']=='before'), y, False),
                                     (next(r for r in pair if r['side']=='after'), y+17, True)]:
                count = int(row['technical_rows'])
                bar = (width-267-25)*count/30
                text(151, yy, '.'.join(reversed(row['capture_utc'][:10].split('-'))))
                if count:
                    parts.append(f'<rect x="267" y="{yy-8}" width="{bar}" height="10" fill="{accent if filled else "none"}" stroke="{accent}"/>')
                else:
                    parts.append(f'<path d="M267 {yy-8}v10" stroke="{accent}"/>')
                text(273+bar, yy, count, 10, 700)
    else:
        left, bottom, pw, ph = 40, height-32, width-57, height-48
        def point(load, hours):
            return left+(load-5)/15*pw, bottom-hours/12*ph
        for hours in [0,4,8,12]:
            yy = point(5,hours)[1]
            parts.append(f'<path d="M{left} {yy}h{pw}" stroke="#ded6e3" stroke-width=".6"/>')
            text(left-8, yy+3, hours, anchor='end')
        for load in [5,10,15,20]:
            text(point(load,0)[0],height-15,load,anchor='middle')
        text(0,8,'год')
        text(width,height,'Стале навантаження, Вт',anchor='end')
        points = ' '.join(f'{point(5+i*.1,57.72/(5+i*.1))[0]:.4f},{point(5+i*.1,57.72/(5+i*.1))[1]:.4f}' for i in range(151))
        parts.append(f'<polyline points="{points}" fill="none" stroke="{accent}" stroke-width="1.8"/>')
        for load,label,dy,dx in [(13,'13 Вт: 4,44 год',-18,-83),(15,'15 Вт: 3,85 год',18,10)]:
            xx, yy = point(load,57.72/load)
            parts.append(f'<circle cx="{xx}" cy="{yy}" r="3" fill="{accent}"/>')
            text(xx+dx,yy+dy,label)
    return ''.join(parts)+'</svg>'


def table_scopes(writer):
    """Keep WeasyPrint's explicit header IDs and also identify row/column scope."""
    def walk(value, in_head=False):
        obj = value.get_object() if hasattr(value, 'get_object') else value
        if isinstance(obj, list):
            for child in obj:
                walk(child,in_head)
        elif isinstance(obj, dict):
            tag = obj.get('/S')
            if tag == '/TH':
                attributes = obj.get('/A', DictionaryObject())
                attributes[NameObject('/O')] = NameObject('/Table')
                attributes[NameObject('/Scope')] = NameObject('/Column' if in_head else '/Row')
                obj[NameObject('/A')] = attributes
            if '/K' in obj:
                walk(obj['/K'],in_head or tag == '/THead')
    walk(writer._root_object['/StructTreeRoot'])


def pagination_artifacts(writer, brand):
    """Classify generated running page numbers, never substantive text, as artifacts.

    WeasyPrint 70 gives margin-box numbers MCIDs without structure-tree owners.
    Assert their extracted content before changing those wrappers to Artifact.
    """
    nums = writer._root_object['/StructTreeRoot']['/ParentTree']['/Nums']
    parents = {int(nums[i]): nums[i+1].get_object() for i in range(0,len(nums),2)}
    owners = {}
    def walk(value,page=None):
        obj = value.get_object() if hasattr(value,'get_object') else value
        if isinstance(obj,list):
            for child in obj:
                walk(child,page)
        elif isinstance(obj,dict):
            page = obj.get('/Pg',page)
            if '/MCID' in obj and page is not None:
                owners.setdefault(page.idnum,set()).add(int(obj['/MCID']))
            if '/K' in obj:
                walk(obj['/K'],page)
        elif isinstance(obj,int) and page is not None:
            owners.setdefault(page.idnum,set()).add(int(obj))
    walk(writer._root_object['/StructTreeRoot'])
    for number,page in enumerate(writer.pages,1):
        if number == 1:
            continue
        refs = parents[int(page['/StructParents'])]
        owned = owners.get(page.indirect_reference.idnum,set())
        stack, texts = [], {}
        def before(operator,args,*_):
            if operator in (b'BDC',b'BMC'):
                stack.append(args[1].get('/MCID') if operator == b'BDC' and isinstance(args[1],dict) else None)
            elif operator == b'EMC' and stack:
                stack.pop()
        def text(value,*_):
            mcid = next((item for item in reversed(stack) if item is not None),None)
            if value and mcid is not None:
                texts[int(mcid)] = texts.get(int(mcid),'')+value
        page.extract_text(visitor_operand_before=before,visitor_text=text)
        stream = ContentStream(page['/Contents'],writer)
        for index,(operands,operator) in enumerate(stream.operations):
            if operator == b'BDC' and isinstance(operands[1],dict) and '/MCID' in operands[1]:
                mcid = int(operands[1]['/MCID'])
                if mcid not in owned:
                    assert texts.get(mcid,'').strip() in {str(number),'NG Group' if brand=='NGGroup' else brand}, ('Unexpected unowned content',number,mcid,texts.get(mcid))
                    stream.operations[index] = ([NameObject('/Artifact')],b'BMC')
                    if mcid < len(refs):
                        refs[mcid] = NullObject()
        page[NameObject('/Contents')] = writer._add_object(stream)


def print_source(source, brand):
    # Reuse the experiment's semantic HTML adapter, without its raster cover.
    source = re.sub(r'<html lang="[^"]+"', '<html lang="uk-UA"', source, count=1)
    source = re.sub(r'<header>.*?</header>', '<header class="accepted-cover"></header>', source, count=1, flags=re.S)
    source = re.sub(r'<footer>.*?</footer>', '', source, count=1, flags=re.S)
    # The link already provides underline styling. A nested <u> makes WeasyPrint
    # create a second annotation owned by NonStruct rather than the Link element.
    source = re.sub(r'(<a\b[^>]*>)<u>(.*?)</u>(</a>)', r'\1\2\3', source, flags=re.S)
    # WeasyPrint names PDF image resources from the source URL. Absolute file
    # URLs therefore make identical checkouts produce different bytes. Embed
    # the exact generated PNG bytes so identity depends on content, not cwd.
    def embedded_image(match):
        path = (ROOT/'public/reports'/html.unescape(match[1])).resolve()
        assert path.is_relative_to((ROOT/'public/reports/assets').resolve()) and path.suffix == '.png', path
        return 'src="data:image/png;base64,'+base64.b64encode(path.read_bytes()).decode('ascii')+'"'
    source = re.sub(r'src="([^"]+)"',embedded_image,source)
    # A chart's HTML data table is a redundant accessible alternative. For print
    # its complete values become Figure /Alt while the vector graph stays visible.
    # This preserves all values without printing a second representation below it.
    palette = dict(re.findall(r'--(chart-accent|accent|ink):([^;}]+)', source))
    def chart_alternative(match):
        chart, table = match[1], match[2]
        rows = re.findall(r'<tr>(.*?)</tr>', table, flags=re.S)
        data = '; '.join(' | '.join(html.unescape(re.sub('<[^>]+>', '', cell))
                                  for cell in re.findall(r'<t[hd][^>]*>(.*?)</t[hd]>', row, flags=re.S))
                         for row in rows)
        title = re.search(r'aria-label="([^"]+)"', chart[chart.index('<svg'):])
        caption = re.search(r'<caption>(.*?)</caption>', table, flags=re.S)
        alternative = (html.unescape(title[1]) if title else '') + ' ' + data
        alternative = alternative.replace('Точні дати та значення наведено в таблиці.', 'Точні дати та значення:').replace('Точні значення наведено в таблиці.', 'Точні значення:')
        if caption:
            alternative += '. ' + html.unescape(re.sub('<[^>]+>', '', caption[1]))
        kind = 'history' if 'class="chart-scroll history"' in chart else 'autonomy'
        return re.sub(r'<svg\b.*?</svg>', lambda _: print_chart(kind,alternative,palette), chart, flags=re.S)
    source = re.sub(r'(<div class="chart-scroll.*?</div>)(<div class="table-scroll.*?</div>)', chart_alternative, source, flags=re.S)
    def svg_colors(match):
        svg = match[0]
        for name, value in palette.items():
            svg = svg.replace(f'var(--{name})', value)
        return svg.replace('currentColor', palette['ink'])
    source = re.sub(r'<svg\b.*?</svg>', svg_colors, source, flags=re.S)
    public_url = PUBLIC_BASE_URL + f'reports/{brand}_Review.html'
    source = re.sub(r'href="([^"]+)"', lambda m: m[0] if m[1].startswith('#') else
                    'href="' + html.escape(urljoin(public_url, html.unescape(m[1])), quote=True) + '"', source)
    # Retain explicit table proportions from the manuscript and normal-weight
    # row-header typography while keeping real TH/scope semantics.
    for section in REPORTS[brand]:
        target = re.search(r'<section id="' + section['id'] + r'".*?</section>', source, flags=re.S)[0]
        widths = iter(b for b in section['blocks'] if b[0] == 'table')
        def columns(match):
            try:
                block = next(widths)
            except StopIteration:
                return match[0]
            values = block[3] if len(block) > 3 else None
            if not values:
                return match[0]
            size = block[4] if len(block) > 4 else 11.1
            return f'<table style="--table-size:{size}pt"><colgroup>' + ''.join(f'<col style="width:{100 * value}%">' for value in values) + '</colgroup>'
        replaced = re.sub(r'<table>', columns, target)
        heights = iter(b[2] for b in section['blocks'] if b[0] == 'image')
        replaced = re.sub(r'<img ', lambda m: f'<img style="max-height:{next(heights)}pt" ', replaced)
        source = source.replace(target, replaced)
    return source


def print_css(font_dir, brand):
    regular = (font_dir / 'NotoSans-Regular.ttf').as_uri()
    bold = (font_dir / 'NotoSans-Bold.ttf').as_uri()
    symbols = (font_dir / 'DejaVuSans.ttf').as_uri()
    brand_label = 'NG Group' if brand == 'NGGroup' else brand
    accent = '#a84000' if brand == 'ASP24' else '#753697'
    return f'''
    @font-face {{font-family:Report;src:url("{regular}");font-weight:400}}
    @font-face {{font-family:Report;src:url("{bold}");font-weight:700}}
    @font-face {{font-family:Symbols;src:url("{symbols}");font-weight:400}}
    @page {{size:A4;margin:45pt 51pt 54pt;@top-left{{content:"{brand_label}";font:700 10.5pt Report;color:{accent};vertical-align:bottom;transform:translateY(14pt)}}@bottom-right{{content:counter(page);font:10pt Report;color:#60575c}}}}
    @page:first {{margin:0;@top-left{{content:none}}@bottom-right{{content:none}}}}
    html,body {{font-family:Report,Symbols;font-size:12pt;line-height:1.42;hyphens:none}}
    header,main,footer {{max-width:none;margin:0;padding:0}}
    .accepted-cover {{border:0;padding:0;margin:0;width:210mm;height:297mm;break-after:page}}
    nav,.skip {{display:none}}
    section {{padding:0;border:0;break-inside:auto;break-before:page}}
    section:first-of-type {{break-before:auto}}
    section>p {{max-width:none}}
    .section-label {{font-size:10pt;line-height:14pt;margin:0 0 17pt;padding:0 0 8pt;border-bottom:1px solid var(--soft);font-weight:400;text-align:right;color:#60575c}}
    h2 {{font-size:22.2pt;line-height:28pt;margin:0 0 13pt;break-after:avoid;bookmark-level:1}}
    h3 {{font-size:12.2pt;line-height:17.3pt;margin:0 0 6pt;color:var(--accent);break-after:avoid;bookmark-level:2}}
    p,li {{font-size:12pt;line-height:17pt;margin:0 0 10pt;orphans:2;widows:2}}
    .note,figcaption {{font-size:10pt;line-height:14.1pt;margin:0 0 9pt;color:#61565c}}
    .source {{font-size:11.2pt;line-height:16pt;margin:0 0 9pt}}
    .callout {{padding:12pt 14pt;margin:0 0 11pt;border-left-width:1.4pt;break-inside:avoid}}
    .callout h3 {{font-size:12pt;line-height:17pt;margin:0 0 6pt}}
    .callout p {{font-size:11.6pt;line-height:16.6pt;margin:0}}
    .table-scroll {{overflow:visible;margin:0 0 9pt}}
    table {{font-size:11.1pt;line-height:1.42;table-layout:fixed}}
    th,td {{font-size:var(--table-size,11.1pt);line-height:1.42;padding:7pt 9pt;min-width:0;overflow-wrap:normal}}
    tbody th {{font-weight:400}}
    tr {{break-inside:avoid}}
    caption {{font-size:10pt;line-height:14.1pt;margin-bottom:6pt}}
    figure {{margin:0 0 9pt;break-inside:avoid}}
    figure img {{max-height:145pt;width:auto;max-width:100%;object-fit:contain;margin-bottom:6pt}}
    .chart-scroll {{overflow:visible;margin:0}}
    .chart-scroll svg {{width:100%;min-width:0;max-width:100%;max-height:150pt}}
    .autonomy svg {{max-height:124pt}}
    svg {{font-family:Report}}
    .action {{display:inline;padding:0;margin:0;border:0;border-radius:0;min-height:0;font-size:11.4pt;line-height:16.5pt;font-weight:700}}
    a {{overflow-wrap:anywhere}}
    '''


def build(output, font_dir):
    assert weasyprint_version == '70.0', 'Pinned WeasyPrint 70.0 required'
    output.mkdir(parents=True, exist_ok=True)
    results = []
    for brand in REPORTS:
        source_path = ROOT / f'public/reports/{brand}_Review.html'
        source = source_path.read_text()
        assert f'content="{sha(HERE / "content.json")}"' in source, 'Regenerate semantic HTML from current manuscript first'
        adapted = print_source(source, brand)
        adapted = adapted.replace('</head>', '<style>' + print_css(font_dir,brand) + '</style></head>', 1)
        (output / f'{brand}_print.html').write_text(adapted)
        fetcher = URLFetcher(allowed_protocols={'file', 'data'}, fail_on_errors=True)
        document = HTML(string=adapted, base_url=source_path.parent.as_uri() + '/', url_fetcher=fetcher).render()
        draft = document.write_pdf(pdf_tags=True, pdf_variant='pdf/ua-1')
        import io
        writer = PdfWriter(clone_from=PdfReader(io.BytesIO(draft)))
        cover_structure(writer, brand)
        table_scopes(writer)
        pagination_artifacts(writer,brand)
        outline = writer.get_outline_root()
        writer.add_outline_item(('NG Group' if brand == 'NGGroup' else brand)+' — обкладинка',0,before=outline.get('/First'))
        writer.add_metadata({'/Title': html.unescape(re.search(r'<title>(.*?)</title>',source)[1]),
                             '/Subject': 'Технічний каталог, документи й консультація' if brand == 'NGGroup' else 'Пошук, технічний вибір і підготовка закупівлі'})
        dest = output / f'{brand}_Review.pdf'
        with dest.open('wb') as f:
            writer.write(f)
        results.append({'brand': brand, 'file': dest.name, 'pages': len(writer.pages), 'sha256': sha(dest),
                        'input_digest': inventory()['digest'], 'content_sha256': sha(HERE/'content.json'),
                        'deployment_config_sha256': sha(ROOT/'deployment.config.json'), 'public_base_url': PUBLIC_BASE_URL,
                        'renderer': 'WeasyPrint 70.0 + semantically tagged original vector cover', 'pdf_ua_claim': False,
                        'section_pages': {section['id']: next(i+1 for i,p in enumerate(document.pages) if section['id'] in p.anchors) for section in REPORTS[brand]}})
    (output / 'tagged-manifest.json').write_text(json.dumps(results, ensure_ascii=False, indent=2) + '\n')
    return results


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--font-dir', type=Path, default=Path(os.environ.get('REPORT_FONT_DIR', HERE/'fonts')))
    args = parser.parse_args()
    print(json.dumps(build(args.output.resolve(), args.font_dir.resolve()), ensure_ascii=False, indent=2))
