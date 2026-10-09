#!/usr/bin/env python3
"""Full-report R42 experiment; never writes to accepted reports or their manifests.

Requires the existing requirements-tagged-pilot.txt, Poppler, and report fonts.
The result is evidence, not a PDF/UA conformance or release-acceptance claim.
"""
from __future__ import annotations

import argparse
from collections import Counter
from datetime import datetime, timezone
import hashlib
import html
from html.parser import HTMLParser
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
from urllib.parse import urljoin

from PIL import Image, ImageChops
from pypdf import PdfReader
from weasyprint import HTML, __version__ as weasyprint_version
from weasyprint.urls import URLFetcher

ROOT = Path(__file__).resolve().parents[1]
BRANDS = ("ASP24", "NGGroup")


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def compact(text):
    # Normalize layout whitespace only, not digits, signs, units, or punctuation.
    return re.sub(r"\s+", "", text.replace("\u00ad", ""))


class Node:
    def __init__(self, tag, attrs=()):
        self.tag, self.attrs, self.children = tag, dict(attrs), []

    def text(self):
        return "".join(c.text() if isinstance(c, Node) else c for c in self.children)

    def find(self, *tags):
        for child in self.children:
            if isinstance(child, Node):
                if child.tag in tags:
                    yield child
                yield from child.find(*tags)


class Document(HTMLParser):
    def __init__(self, source):
        super().__init__(convert_charrefs=True)
        self.root = Node("document")
        self.stack = [self.root]
        self.feed(source)

    def handle_starttag(self, tag, attrs):
        child = Node(tag, attrs)
        self.stack[-1].children.append(child)
        if tag == "br":
            child.children.append(" ")
        if tag not in {"area", "base", "br", "col", "embed", "hr", "img", "input", "link", "meta", "param", "source", "track", "wbr"}:
            self.stack.append(child)

    def handle_endtag(self, tag):
        for index in range(len(self.stack) - 1, 0, -1):
            if self.stack[index].tag == tag:
                del self.stack[index:]
                break

    def handle_data(self, data):
        self.stack[-1].children.append(data)


def command(args):
    return subprocess.run(args, check=True, capture_output=True, text=True).stdout


def render(pdf, folder):
    folder.mkdir(parents=True, exist_ok=True)
    for previous in folder.glob("page-*.png"):
        previous.unlink()
    command(["pdftoppm", "-r", "96", "-png", str(pdf), str(folder / "page")])
    return sorted(folder.glob("page-*.png"))


def source_copy(source, cover_png, cover_text, public_url):
    # These are print adapters only; visible report text is never rewritten.
    result = re.sub(r'<html lang="[^"]+"', '<html lang="uk-UA"', source, count=1)
    result = re.sub(r'<header>.*?</header>',
                    '<header class="accepted-cover"><h1><img src="' + cover_png.as_uri() +
                    '" alt="' + html.escape(cover_text, quote=True) + '"></h1></header>',
                    result, count=1, flags=re.S)

    def svg_title(match):
        opening = match.group(0)
        label = re.search(r'aria-label="([^"]+)"', opening)
        # WeasyPrint 70 consumes SVG <title>, not aria-label. Preserve the existing
        # HTML alternative exactly; do not invent a second description.
        return opening + ('<title>' + html.escape(html.unescape(label[1])) + '</title>' if label else '')

    result = re.sub(r'<svg\b[^>]*>', svg_title, result)
    palette = dict(re.findall(r'--(accent|ink):([^;}]+)', source))

    def svg_colors(match):
        # SVG presentation attributes are not CSS declaration values in the
        # renderer. Resolve the existing brand variables only inside SVG.
        drawing = match.group(0)
        for name, value in palette.items():
            drawing = drawing.replace(f"var(--{name})", value)
        return drawing.replace("currentColor", palette["ink"])

    result = re.sub(r'<svg\b.*?</svg>', svg_colors, result, flags=re.S)

    def absolute_link(match):
        href = html.unescape(match[1])
        if href.startswith("#"):
            return match.group(0)
        return 'href="' + html.escape(urljoin(public_url, href), quote=True) + '"'

    return re.sub(r'href="([^"]+)"', absolute_link, result)


def print_css(font_dir):
    regular = (font_dir / "NotoSans-Regular.ttf").as_uri()
    bold = (font_dir / "NotoSans-Bold.ttf").as_uri()
    return f'''
    @font-face {{font-family:Report;src:url("{regular}");font-weight:400}}
    @font-face {{font-family:Report;src:url("{bold}");font-weight:700}}
    @page {{size:A4;margin:18mm;@bottom-right{{content:counter(page);font:9pt Report;color:#61565c}}}}
    @page:first {{margin:0;@bottom-right{{content:none}}}}
    html,body {{font-family:Report,sans-serif;font-size:12pt;line-height:1.42;hyphens:none}}
    header,main,footer {{max-width:none;margin:0;padding:0}}
    .accepted-cover {{border:0;padding:0;margin:0;width:210mm;height:297mm;break-after:page}}
    .accepted-cover h1 {{margin:0;padding:0;font-size:0;line-height:0;bookmark-level:none}}
    .accepted-cover img {{display:block;margin:0;width:210mm;height:297mm;max-width:none}}
    nav,.skip {{display:none}}
    section {{padding:0;border:0;break-inside:auto;break-before:page}}
    section:first-of-type {{break-before:auto}}
    .section-label {{font-size:10pt;margin:0 0 10pt;font-weight:700}}
    h2 {{font-size:22pt;line-height:1.25;margin:0 0 13pt;break-after:avoid;bookmark-level:1}}
    h3 {{font-size:12.2pt;line-height:1.4;margin:10pt 0 6pt;color:var(--accent);break-after:avoid;bookmark-level:2}}
    p,li {{font-size:12pt;line-height:1.42;margin:0 0 9pt}}
    .note,.source,figcaption {{font-size:10pt;line-height:1.41;margin:0 0 9pt}}
    .callout {{padding:10pt 12pt;margin:9pt 0;break-inside:avoid}}
    .callout p {{font-size:11.6pt;margin:0}}
    .table-scroll {{overflow:visible;margin:9pt 0}}
    table {{font-size:10.5pt;line-height:1.4;table-layout:fixed}}
    th,td {{font-size:10.5pt;padding:6pt;min-width:0;overflow-wrap:anywhere}}
    tr {{break-inside:avoid}}
    caption {{font-size:10pt;margin-bottom:6pt}}
    figure {{margin:9pt 0;break-inside:avoid}}
    figure img {{max-height:62mm;width:auto;max-width:100%;object-fit:contain}}
    svg {{max-height:67mm}}
    .action {{display:inline;padding:0;margin:0;border:0;border-radius:0;min-height:0}}
    footer {{font-size:9pt;line-height:1.4;margin-top:12pt}}
    '''


def structure(reader):
    tags, records = Counter(), []
    page_map = {page.indirect_reference.idnum: number + 1 for number, page in enumerate(reader.pages)}
    marked_text = {}
    for number, page in enumerate(reader.pages, 1):
        stack = []

        def before(operator, args, *_):
            if operator in (b"BDC", b"BMC"):
                stack.append(args[1].get("/MCID") if operator == b"BDC" and isinstance(args[1], dict) else None)
            elif operator == b"EMC" and stack:
                stack.pop()

        def text_piece(value, *_):
            mcid = next((item for item in reversed(stack) if item is not None), None)
            if value and mcid is not None:
                key = (number, int(mcid))
                marked_text[key] = marked_text.get(key, "") + value

        page.extract_text(visitor_operand_before=before, visitor_text=text_piece)
    seen = set()

    def walk(ref, inherited_page=None):
        obj = ref.get_object() if hasattr(ref, "get_object") else ref
        if isinstance(obj, dict):
            if id(obj) in seen:
                return ""
            seen.add(id(obj))
            page = obj.get("/Pg", inherited_page)
            record = None
            if "/S" in obj:
                tag = str(obj["/S"])
                tags[tag] += 1
                record = {"tag": tag, "page": page_map.get(getattr(page, "idnum", None))}
                for key in ("/Alt", "/ID", "/A"):
                    if key in obj:
                        value = obj[key]
                        record[key[1:]] = str(value) if key != "/A" else {
                            str(k): [str(v) for v in val] if isinstance(val, list) else str(val)
                            for k, val in value.items()}
                records.append(record)
            value = walk(obj["/K"], page) if "/K" in obj else ""
            if record is not None:
                if record["tag"] == "/Figure":
                    value = record.get("Alt", "") + value
                if record["tag"] in {"/H1", "/H2", "/H3", "/P", "/TH", "/TD", "/Caption", "/Figure"}:
                    record["logical_text"] = value
            return value
        elif isinstance(obj, list):
            return " ".join(walk(child, inherited_page) for child in obj)
        elif isinstance(obj, int):
            return marked_text.get((page_map.get(getattr(inherited_page, "idnum", None)), int(obj)), "")
        return ""

    logical_text = walk(reader.trailer["/Root"].get("/StructTreeRoot"))
    headers = {item["ID"] for item in records if item["tag"] == "/TH" and "ID" in item}
    cells = [item for item in records if item["tag"] == "/TD"]
    missing = [item for item in cells if not item.get("A", {}).get("/Headers")]
    unresolved = [item for item in cells if any(header not in headers for header in item.get("A", {}).get("/Headers", []))]
    figures = [item for item in records if item["tag"] == "/Figure"]
    # This tests actual structural page order. It is deliberately not described
    # as a screen-reader or complete logical reading-order verification.
    leaf_pages = [item["page"] for item in records if item["page"] is not None and item["tag"] in {"/H1", "/H2", "/H3", "/P", "/TH", "/TD", "/Figure"}]
    return {
        "tags": dict(tags), "elements": records, "logical_text": logical_text,
        "language": str(reader.trailer["/Root"].get("/Lang")),
        "table_header_ids": len(headers), "data_cells": len(cells),
        "data_cells_without_headers": missing, "unresolved_header_references": unresolved,
        "figures_without_alternative": [item for item in figures if not item.get("Alt")],
        "structure_page_order_nondecreasing": leaf_pages == sorted(leaf_pages),
    }


def content_evidence(source, reader, public_url, logical_text):
    doc = Document(source).root
    sections = list(doc.find("section"))
    text = "\n".join(page.extract_text() or "" for page in reader.pages)
    flat = compact(text)
    blocks = [(section.attrs.get("id"), node.tag, node.text())
              for section in sections
              for node in section.find("p", "h2", "h3", "th", "td", "caption", "figcaption")]
    missing = [{"section": section, "tag": tag, "text": value}
               for section, tag, value in blocks if compact(value) not in flat]
    logical_flat, logical_cursor = compact(logical_text), 0
    logical_order_failures = []
    for section, tag, value in blocks:
        target = compact(value)
        position = logical_flat.find(target, logical_cursor)
        if position < 0:
            logical_order_failures.append({"section": section, "tag": tag, "text": value})
        else:
            logical_cursor = position + len(target)
    cursor, heading_order = 0, []
    for section in sections:
        heading = next(section.find("h2")).text()
        position = flat.find(compact(heading), cursor)
        heading_order.append({"section": section.attrs.get("id"), "found_in_order": position >= 0})
        if position >= 0:
            cursor = position + len(compact(heading))
    expected_links = {urljoin(public_url, link.attrs["href"])
                      for section in sections for link in section.find("a")
                      if "href" in link.attrs and not link.attrs["href"].startswith("#")}
    actual_links = set()
    for page in reader.pages:
        for ref in page.get("/Annots", []):
            annotation = ref.get_object()
            uri = annotation.get("/A", {}).get("/URI")
            if uri:
                actual_links.add(str(uri))
    expected_alts = [img.attrs.get("alt", "") for section in sections for img in section.find("img")]
    expected_alts += [svg.attrs.get("aria-label", "") for section in sections for svg in section.find("svg")]
    return {
        "sections": len(sections), "blocks_checked": len(blocks),
        "missing_exact_blocks": missing,
        "missing_or_out_of_order_logical_blocks": logical_order_failures,
        "logical_order_method": "Walk /K in structure-tree order, resolve page /MCID to extracted text; locate every source block in order, including table headers/cells and captions. Figure /Alt is retained. This is not assistive-technology testing.",
        "numbers_and_units_check": "Included without numerical normalization in every exact block check",
        "heading_order": heading_order,
        "source_tables": sum(1 for section in sections for _ in section.find("table")),
        "source_table_cells": sum(1 for section in sections for _ in section.find("th", "td")),
        "source_figures_with_alternatives": expected_alts,
        "source_link_count": len(expected_links), "pdf_link_count": len(actual_links),
        "missing_links": sorted(expected_links - actual_links),
        "text_extraction_limit": "Block coverage and heading order do not establish screen-reader reading order or visual clipping absence.",
    }


def contact_sheet(paths, destination):
    thumbs = []
    for number, path in enumerate(paths, 1):
        im = Image.open(path).convert("RGB")
        im.thumbnail((230, 330))
        tile = Image.new("RGB", (250, 355), "#ddd")
        tile.paste(im, ((250 - im.width) // 2, 5))
        from PIL import ImageDraw
        ImageDraw.Draw(tile).text((10, 337), f"Page {number}", fill="#111")
        thumbs.append(tile)
    sheet = Image.new("RGB", (1000, 355 * ((len(thumbs) + 3) // 4)), "white")
    for index, tile in enumerate(thumbs):
        sheet.paste(tile, ((index % 4) * 250, (index // 4) * 355))
    sheet.save(destination)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=ROOT / "output/tagged-full")
    parser.add_argument("--font-dir", type=Path, default=Path(os.environ.get("REPORT_FONT_DIR", ROOT / "reports/fonts")))
    args = parser.parse_args()
    args.output = args.output.resolve()
    args.font_dir = args.font_dir.resolve()
    for protected in (ROOT / "public", ROOT / "reports"):
        if args.output == protected or protected in args.output.parents:
            raise SystemExit("Experiment output must not be inside accepted public/reports inputs.")
    if weasyprint_version != "70.0":
        raise SystemExit("Install pinned scripts/requirements-tagged-pilot.txt (WeasyPrint 70.0).")
    for font in ("NotoSans-Regular.ttf", "NotoSans-Bold.ttf"):
        if not (args.font_dir / font).is_file():
            raise SystemExit(f"Missing report font: {font}; set REPORT_FONT_DIR.")
    args.output.mkdir(parents=True, exist_ok=True)
    accepted = {str(path.relative_to(ROOT)): sha(path) for brand in BRANDS
                for path in (ROOT / f"public/reports/{brand}_Review.pdf", ROOT / f"public/reports/{brand}_Review.html")}
    results = {
        "status": "EXPERIMENTAL_NOT_ACCEPTED", "r42": "OPEN",
        "sha": command(["git", "-C", str(ROOT), "rev-parse", "HEAD"]).strip(),
        "working_tree_dirty": bool(command(["git", "-C", str(ROOT), "status", "--porcelain"]).strip()),
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "renderer": "WeasyPrint " + weasyprint_version,
        "experiment_script_sha256": sha(Path(__file__)),
        "python": command(["python", "--version"]).strip(),
        "poppler": subprocess.run(["pdftoppm", "-v"], capture_output=True, text=True).stderr.splitlines()[0],
        "font_sha256": {name: sha(args.font_dir / name) for name in ("NotoSans-Regular.ttf", "NotoSans-Bold.ttf")},
        "accepted_inputs": accepted, "reports": {},
        "assistive_reading": "NOT_RUN", "pdf_ua_claim": False,
        "visual_review": "NOT_RUN; inspect generated contact sheets and full page renders",
    }
    for brand in BRANDS:
        out = args.output / brand
        out.mkdir(exist_ok=True)
        source_path = ROOT / f"public/reports/{brand}_Review.html"
        source = source_path.read_text()
        public_url = re.search(r'<link rel="canonical" href="([^"]+)"', source)[1]
        cover = ROOT / f"reports/covers/{brand}.pdf"
        cover_text = " ".join(PdfReader(cover).pages[0].extract_text().split())
        command(["pdftoppm", "-r", "144", "-f", "1", "-singlefile", "-png", str(cover), str(out / "accepted-cover")])
        adapted = source_copy(source, out / "accepted-cover.png", cover_text, public_url)
        css = print_css(args.font_dir)
        # Append as an author stylesheet: WeasyPrint's stylesheets= parameter
        # is a user stylesheet and cannot override author @media print rules.
        # In particular those rules intentionally hide HTML action links, which
        # this PDF experiment must preserve as usable URI annotations.
        adapted = adapted.replace("</head>", "<style>" + css + "</style></head>", 1)
        (out / "print.html").write_text(adapted)
        (out / "print.css").write_text(css)
        pdf = out / f"{brand}_Review_tagged_experiment.pdf"
        # Assets are local; missing fonts/images fail instead of silently
        # producing an apparently complete PDF. Source URLs remain hyperlinks.
        fetcher = URLFetcher(allowed_protocols={"file", "data"}, fail_on_errors=True)
        HTML(string=adapted, base_url=source_path.parent.as_uri() + "/", url_fetcher=fetcher).write_pdf(
            pdf, pdf_tags=True, presentational_hints=False)
        reader = PdfReader(pdf)
        structure_result = structure(reader)
        content = content_evidence(source, reader, public_url, structure_result["logical_text"])
        alts = {element.get("Alt") for element in structure_result["elements"] if element["tag"] == "/Figure"}
        content["missing_figure_alternatives"] = [alt for alt in content["source_figures_with_alternatives"] if alt not in alts]
        tagged_pages = render(pdf, out / "render-tagged")
        accepted_pdf = ROOT / f"public/reports/{brand}_Review.pdf"
        accepted_pages = render(accepted_pdf, out / "render-accepted")
        contact_sheet(tagged_pages, out / "contact-tagged.png")
        contact_sheet(accepted_pages, out / "contact-accepted.png")
        cover_diff = ImageChops.difference(Image.open(tagged_pages[0]).convert("RGB"), Image.open(accepted_pages[0]).convert("RGB"))
        cover_diff.save(out / "cover-render-difference.png")
        pixel_changes = sum(1 for pixel in cover_diff.get_flattened_data() if pixel != (0, 0, 0))
        validator = {"status": "NOT_RUN", "reason": "No veraPDF executable found; no PDF/UA assertion was added."}
        if shutil.which("verapdf"):
            check = subprocess.run(["verapdf", "--format", "json", str(pdf)], capture_output=True, text=True)
            (out / "verapdf.json").write_text(check.stdout)
            (out / "verapdf-stderr.txt").write_text(check.stderr)
            validator = {"status": "EXECUTED_REVIEW_REQUIRED", "exit_code": check.returncode, "result": "verapdf.json", "limit": "Validator output must be read; a process exit code alone is not conformance."}
        outline_titles = []
        def walk_outline(items):
            for item in items:
                if isinstance(item, list):
                    walk_outline(item)
                else:
                    outline_titles.append(str(item.get("/Title", "")))
        walk_outline(reader.outline)
        result = {
            "output": str(pdf.relative_to(args.output)), "pdf_sha256": sha(pdf),
            "source_sha256": sha(source_path),
            "print_html_sha256": sha(out / "print.html"), "print_css_sha256": sha(out / "print.css"),
            "pages": len(reader.pages), "accepted_pages": len(PdfReader(accepted_pdf).pages),
            "structure": structure_result, "content": content,
            "bookmarks": outline_titles, "pdf_ua_validator": validator,
            "cover": {"method": "144 dpi raster of unchanged accepted cover; full extracted cover text preserved as Figure /Alt inside H1",
                      "alternative": cover_text, "pixel_changes_at_96dpi": pixel_changes,
                      "pixels_compared": cover_diff.width * cover_diff.height,
                      "limit": "Rasterization preserves artwork composition but loses vector text sharpness and cover text selection. H1 contains Figure rather than text. Not approved as a final cover replacement."},
            "body_render_comparison": "Both complete render sets emitted. HTML tables add accessible figure data and can change pagination; body render equality is not claimed.",
        }
        result["content_structure_checks"] = "PASS" if not any((
            content["missing_or_out_of_order_logical_blocks"], content["missing_links"],
            content["missing_figure_alternatives"], structure_result["figures_without_alternative"],
            structure_result["data_cells_without_headers"], structure_result["unresolved_header_references"],
            structure_result["language"] != "uk-UA",
        )) else "FAIL"
        (out / "result.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n")
        results["reports"][brand] = result
        print(json.dumps({"report": brand, "pages": result["pages"], "accepted_pages": result["accepted_pages"],
                          "missing_blocks": len(content["missing_exact_blocks"]), "missing_links": content["missing_links"],
                          "missing_alternatives": content["missing_figure_alternatives"], "tags": structure_result["tags"]}, ensure_ascii=False))
    results["accepted_inputs_unchanged"] = all(sha(ROOT / name) == digest for name, digest in accepted.items())
    (args.output / "result.json").write_text(json.dumps(results, ensure_ascii=False, indent=2) + "\n")
    assert results["accepted_inputs_unchanged"], "Accepted inputs changed during experiment."
    assert all(report["content_structure_checks"] == "PASS" for report in results["reports"].values()), \
        "Content/structure regression; inspect result.json. This is not a PDF/UA check."


if __name__ == "__main__":
    main()
