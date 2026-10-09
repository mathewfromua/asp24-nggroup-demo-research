#!/usr/bin/env python3
"""Independent tagged-report gate: manuscript, MCIDs, tables, covers and links.

Does not import the PDF generator or repair files. A machine PASS is not visual
acceptance, assistive-technology testing, or a blanket PDF/UA conformance claim.
"""
from __future__ import annotations

import argparse
from collections import Counter, defaultdict
from datetime import datetime, timezone
import hashlib
import html
import json
from pathlib import Path
import re
import shutil
import subprocess
import sys
from urllib.parse import urljoin

from pypdf import PdfReader

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "reports"))
from content import REPORTS, PUBLIC_BASE_URL


def compact(text):
    # Layout whitespace and discretionary hyphens only: preserve every number,
    # sign, unit, model, price, date, punctuation mark and grammatical word.
    return re.sub(r"\s+", "", str(text).replace("\u00ad", ""))


def plain(text):
    return html.unescape(re.sub(r"<[^>]+>", "", str(text)))


def print_chart_label(value):
    # Print replaces a redundant visual table with its complete Figure Alt.
    # These two references must describe that equivalent accurately; no data,
    # interpretation or other wording is normalized by this comparison.
    return value.replace("Точні дати та значення наведено в таблиці.", "Точні дати та значення:").replace(
        "Точні значення наведено в таблиці.", "Точні значення:")


def deref(value):
    return value.get_object() if hasattr(value, "get_object") else value


def refid(value):
    ref = getattr(value, "indirect_reference", value)
    return getattr(ref, "idnum", None)


def attr(obj):
    attributes = deref(obj.get("/A", {}))
    if isinstance(attributes, list):
        attributes = {key: value for part in attributes if isinstance(deref(part), dict)
                      for key, value in deref(part).items()}
    return attributes


def identifier(value):
    return value.decode("utf-8") if isinstance(value, bytes) else str(value)


def number_tree(value):
    obj = deref(value)
    if not obj:
        return {}
    values = obj.get("/Nums", [])
    result = {int(values[index]): deref(values[index + 1]) for index in range(0, len(values), 2)}
    for child in obj.get("/Kids", []):
        result.update(number_tree(child))
    return result


def inspect_structure(reader):
    catalog = reader.trailer["/Root"]
    tree = deref(catalog.get("/StructTreeRoot"))
    errors = []
    if not tree:
        return {"errors": ["Missing StructTreeRoot"], "tags": {}, "records": [], "logical_text": ""}
    if deref(catalog.get("/MarkInfo", {})).get("/Marked") != True:
        errors.append("MarkInfo/Marked is not true")
    if catalog.get("/Lang") != "uk-UA":
        errors.append("Document Lang must be uk-UA")
    pages = {refid(page): index + 1 for index, page in enumerate(reader.pages)}
    marked_text, untagged, artifacts = defaultdict(str), [], []
    for page_number, page in enumerate(reader.pages, 1):
        stack = []

        def operand(operator, args, *_):
            if operator in (b"BDC", b"BMC"):
                properties = deref(args[1]) if operator == b"BDC" else {}
                if not isinstance(properties, dict):
                    properties = deref(page.get("/Resources", {}).get("/Properties", {}).get(properties, {}))
                stack.append((str(args[0]), properties.get("/MCID")))
            elif operator == b"EMC" and stack:
                stack.pop()

        def text_piece(text, *_):
            if not text.strip():
                return
            mcid = next((value for _, value in reversed(stack) if value is not None), None)
            if any(tag == "/Artifact" for tag, _ in stack):
                artifacts.append({"page": page_number, "text": text})
            elif mcid is not None:
                marked_text[(page_number, int(mcid))] += text
            else:
                untagged.append({"page": page_number, "text": text})

        page.extract_text(visitor_operand_before=operand, visitor_text=text_piece)
    records, tags, owners, object_refs = [], Counter(), defaultdict(list), {}
    seen = set()

    def walk(value, page_ref=None, parent=None, table=None, row=None):
        obj = deref(value)
        if isinstance(obj, list):
            return " ".join(walk(child, page_ref, parent, table, row) for child in obj)
        if isinstance(obj, int):
            key = (pages.get(refid(page_ref)), int(obj))
            if parent is not None:
                owners[key].append(parent)
            return marked_text.get(key, "")
        if not isinstance(obj, dict):
            return ""
        if obj.get("/Type") == "/MCR":
            return walk(obj.get("/MCID"), obj.get("/Pg", page_ref), parent, table, row)
        if obj.get("/Type") == "/OBJR":
            object_refs[refid(obj.get("/Obj"))] = parent
            return ""
        identity = refid(obj) or id(obj)
        if identity in seen:
            errors.append(f"Repeated/cyclic structure object {identity}")
            return ""
        seen.add(identity)
        page_ref = obj.get("/Pg", page_ref)
        tag = str(obj.get("/S", ""))
        record = None
        if tag:
            tags[tag] += 1
            record = {"tag": tag, "object": refid(obj), "page": pages.get(refid(page_ref)),
                      "parent": parent, "id": identifier(obj["/ID"]) if "/ID" in obj else None,
                      "alt": str(obj.get("/Alt", "")), "attributes": attr(obj)}
            index = len(records)
            if tag == "/Table":
                table = index
            if tag == "/TR":
                row = index
            record.update(table=table, row=row)
            records.append(record)
            if parent is not None and refid(obj.get("/P")) != records[parent]["object"]:
                errors.append(f"Wrong structure parent for object {record['object']}")
            parent = index
        text = walk(obj.get("/K"), page_ref, parent, table, row)
        if record is not None:
            record["text"] = text
            if tag == "/Figure":
                text = record["alt"] + " " + text
        return text

    logical_text = walk(tree)
    if untagged:
        errors.append(f"{len(untagged)} visible text runs have neither MCID nor Artifact")
    unowned = [key for key in marked_text if not owners[key]]
    multiple = [key for key, values in owners.items() if len(values) > 1]
    if unowned:
        errors.append(f"{len(unowned)} text MCIDs have no logical owner")
    if multiple:
        errors.append(f"{len(multiple)} MCIDs have duplicate logical owners")
    parent_tree = number_tree(tree.get("/ParentTree"))
    for page_number, page in enumerate(reader.pages, 1):
        refs = parent_tree.get(int(page.get("/StructParents", -1)), [])
        for (owner_page, mcid), owner in owners.items():
            if owner_page == page_number and owner:
                expected = records[owner[0]]["object"]
                if not isinstance(refs, list) or mcid >= len(refs) or refid(refs[mcid]) != expected:
                    errors.append(f"ParentTree mismatch page {page_number} MCID {mcid}")
    for record in records:
        if record["tag"] == "/Figure" and not record["alt"].strip():
            errors.append(f"Figure object {record['object']} lacks meaningful Alt")
    tables = check_tables(records)
    errors.extend(tables["errors"])
    return {"errors": errors, "tags": dict(tags), "records": records, "logical_text": logical_text,
            "marked_text_runs": len(marked_text), "untagged_text": untagged,
            "artifact_text": artifacts, "unowned_mcids": unowned,
            "table_checks": tables, "object_references": object_refs, "parent_tree": parent_tree}


def check_tables(records):
    """Validate associations to the actual row and column, not merely an ID."""
    errors, cells_checked = [], 0
    for table_index, table in enumerate(records):
        if table["tag"] != "/Table":
            continue
        cells = [r for r in records if r["table"] == table_index and r["tag"] in {"/TH", "/TD"}]
        rows = []
        for cell in cells:
            if cell["row"] not in rows:
                rows.append(cell["row"])
        grid = [[cell for cell in cells if cell["row"] == row] for row in rows]
        ids = {cell["id"]: cell for cell in cells if cell["tag"] == "/TH" and cell["id"]}
        if not grid or not all(cell["tag"] == "/TH" for cell in grid[0]):
            errors.append(f"Table {table['object']} lacks a complete TH column-header row")
            continue
        for row_number, row in enumerate(grid):
            if len(row) != len(grid[0]):
                errors.append(f"Table {table['object']} row {row_number} has inconsistent cell count")
            for column, cell in enumerate(row):
                if cell["tag"] == "/TH":
                    expected_scope = "/Column" if row_number == 0 else "/Row"
                    # Explicit /Headers + IDs are a valid alternative to Scope.
                    # If Scope exists, it must agree with the table geometry.
                    if cell["attributes"].get("/Scope", expected_scope) != expected_scope:
                        errors.append(f"TH {cell['object']} has incorrect {expected_scope} scope")
                    continue
                cells_checked += 1
                headers = [identifier(value) for value in cell["attributes"].get("/Headers", [])]
                expected = {grid[0][column]["id"]} if column < len(grid[0]) else set()
                if row and row[0]["tag"] == "/TH":
                    expected.add(row[0]["id"])
                if not headers or None in expected or set(headers) != expected or any(value not in ids for value in headers):
                    errors.append(f"TD {cell['object']} header associations do not match its row/column")
    return {"data_cells_checked": cells_checked, "errors": errors}


def expected_blocks(brand):
    for section in REPORTS[brand]:
        yield section["id"], "/P", section["section"]
        yield section["id"], "/H2", section["title"]
        for block in section["blocks"]:
            kind = block[0]
            if kind in {"p", "note", "source", "link", "h"}:
                yield section["id"], "/H3" if kind == "h" else "/P", plain(block[1])
            elif kind == "box":
                yield section["id"], "/H3", plain(block[1])
                yield section["id"], "/P", plain(block[2])
            elif kind == "table":
                for value in block[1]:
                    yield section["id"], "/TH", plain(value)
                for row in block[2]:
                    for column, value in enumerate(row):
                        yield section["id"], "/TH" if column == 0 else "/TD", plain(value)
            elif kind == "image":
                yield section["id"], "/Caption", plain(block[3])


def verify_report(path, brand):
    reader = PdfReader(path)
    structure = inspect_structure(reader)
    errors = structure["errors"][:]
    extracted = "\n".join(page.extract_text() or "" for page in reader.pages)
    flat, logical = compact(extracted), compact(structure["logical_text"])
    if any(character in extracted for character in ("\x00", "\ufffd")):
        errors.append("Extracted text has NUL or replacement characters")
    records = structure["records"]
    cursor = 0
    coverage = defaultdict(lambda: {"blocks": 0, "missing": [], "logical_order_failures": [], "semantic_failures": []})
    for section, tag, value in expected_blocks(brand):
        target = compact(value)
        result = coverage[section]
        result["blocks"] += 1
        if target not in flat:
            result["missing"].append(value)
        position = logical.find(target, cursor)
        if position < 0:
            result["logical_order_failures"].append(value)
        else:
            cursor = position + len(target)
        allowed = {tag}
        if not any(record["tag"] in allowed and target in compact(record.get("text", "")) for record in records):
            result["semantic_failures"].append({"expected_tag": tag, "text": value})
    for section, values in coverage.items():
        for category in ("missing", "logical_order_failures", "semantic_failures"):
            if values[category]:
                errors.append(f"{section}: {len(values[category])} {category}")
    # Canonical HTML provides exact illustration alternatives, generated chart
    # values, source links and in-document citation targets; prose above comes
    # directly from content.json through its token resolver.
    source = (ROOT / f"public/reports/{brand}_Review.html").read_text()
    image_alts = [html.unescape(value) for value in re.findall(r'<img\b[^>]*\balt="([^"]*)"', source)]
    svg_alts = [print_chart_label(html.unescape(value)) for value in re.findall(r'<svg\b[^>]*\baria-label="([^"]*)"', source)]
    actual_alts = {record["alt"] for record in records if record["tag"] == "/Figure"}
    missing_alts = [value for value in image_alts if value not in actual_alts]
    missing_alts += [value for value in svg_alts if not any(alt.startswith(value) for alt in actual_alts)]
    chart_data_checks = []
    for figure in re.findall(r'<figure\b[^>]*>(.*?)</figure>', source, re.S):
        match = re.search(r'<svg\b[^>]*\baria-label="([^"]*)"', figure)
        if "<table" not in figure:
            continue
        label = print_chart_label(html.unescape(match[1])) if match else "Semantic figure data table"
        equivalent = next((alt for alt in actual_alts if alt.startswith(label)), "") if match else structure["logical_text"]
        # Compact print charts may carry the HTML data table inside Figure Alt.
        # Every caption/header/value must remain in that alternative or actual
        # selectable PDF text, including dated rows and zero values.
        values = [plain(value) for value in re.findall(r'<(?:th|td)\b[^>]*>(.*?)</(?:th|td)>', figure, re.S)]
        position = 0
        missing = []
        for value in values:
            located = compact(equivalent).find(compact(value), position)
            if located < 0:
                missing.append(value)
            else:
                position = located + len(compact(value))
        captions = [plain(value) for value in re.findall(r'<caption\b[^>]*>(.*?)</caption>', figure, re.S)]
        missing += [value for value in captions if compact(value) not in compact(equivalent)]
        chart_data_checks.append({"label": label, "values_checked": len(values) + len(captions), "missing": missing})
        if missing:
            errors.append(f"Chart text alternative omits {len(missing)} exact caption/header/data values")
    if missing_alts:
        errors.append(f"{len(missing_alts)} source illustration alternatives missing")
    # HTML report links in header/nav are not print-body requirements.
    sections_html = "".join(re.findall(r'<section\b.*?</section>', source, re.S))
    hrefs = [html.unescape(value) for value in re.findall(r'href="([^"]+)"', sections_html)]
    expected_uris = {urljoin(PUBLIC_BASE_URL + f"reports/{brand}_Review.html", value)
                     for value in hrefs if not value.startswith("#")}
    expected_internal = {value[1:] for value in hrefs if value.startswith("#")}
    uris, internal, link_count = set(), set(), 0
    names = reader.named_destinations
    for page_number, page in enumerate(reader.pages, 1):
        for ref in page.get("/Annots", []):
            annotation = deref(ref)
            if annotation.get("/Subtype") != "/Link":
                continue
            link_count += 1
            action = deref(annotation.get("/A", {}))
            uri = action.get("/URI")
            if uri:
                uris.add(str(uri))
                if re.search(r"\s|\{\{", str(uri)) or not str(uri).startswith(("https://", "mailto:")):
                    errors.append(f"Invalid external URI on page {page_number}: {uri}")
            destination = annotation.get("/Dest", action.get("/D"))
            if destination is not None:
                if isinstance(destination, str):
                    internal.add(destination)
                    if destination not in names:
                        errors.append(f"Unresolved internal destination: {destination}")
                elif isinstance(destination, list) and refid(destination[0]) not in {refid(p) for p in reader.pages}:
                    errors.append(f"Internal destination points outside document on page {page_number}")
            owner = structure.get("object_references", {}).get(refid(ref))
            if owner is None or records[owner]["tag"] != "/Link":
                errors.append(f"Link annotation {refid(ref)} lacks a logical Link/OBJR owner")
            elif refid(structure["parent_tree"].get(int(annotation.get("/StructParent", -1)))) != records[owner]["object"]:
                errors.append(f"Link annotation {refid(ref)} has inconsistent ParentTree ownership")
    missing_links = sorted(expected_uris - uris)
    if missing_links:
        errors.append(f"{len(missing_links)} source external links missing")
    if expected_internal - internal:
        errors.append(f"{len(expected_internal - internal)} source internal citation targets missing")
    outline = []

    def bookmarks(values):
        for value in values:
            if isinstance(value, list):
                bookmarks(value)
            else:
                outline.append(str(value.get("/Title", "")))

    bookmarks(reader.outline)
    if any(section["title"] not in outline for section in REPORTS[brand]):
        errors.append("Not all report section headings have bookmarks")
    accepted_cover = ROOT / f"reports/covers/{brand}.pdf"
    cover_source = PdfReader(accepted_cover).pages[0].extract_text() or ""
    cover_text = reader.pages[0].extract_text() or ""
    if compact(cover_source) != compact(cover_text):
        errors.append("Selectable cover text differs from the accepted cover")
    cover_records = [record for record in records if record["page"] == 1 and record["tag"] in {"/H1", "/P"}]
    if not any(record["tag"] == "/H1" and record.get("text", "").strip() for record in cover_records):
        errors.append("Cover has no selectable textual H1")
    if any(compact(line) not in logical for line in cover_source.splitlines() if line.strip()):
        errors.append("Accepted cover text missing from logical structure")
    cover_logical = compact(" ".join(record.get("text", "") for record in cover_records))
    cover_visual_order = PdfReader(accepted_cover).pages[0].extract_text(extraction_mode="layout")
    if cover_logical != compact(cover_visual_order):
        errors.append("Cover H1/P reading order differs from accepted cover text")
    def invoked_images(container):
        contents = container.get_contents() if hasattr(container, "get_contents") else None
        if contents is None:
            from pypdf.generic import ContentStream
            contents = ContentStream(container, reader)
        resources = deref(container.get("/Resources", {}))
        for operands, operator in contents.operations:
            if operator != b"Do":
                continue
            item = deref(resources.get("/XObject", {}).get(operands[0]))
            if item and item.get("/Subtype") == "/Image":
                yield item
            elif item and item.get("/Subtype") == "/Form":
                yield from invoked_images(item)
    if any(invoked_images(reader.pages[0])):
        errors.append("Cover contains a raster image replacement")
    cover_pixels = "NOT_RUN"
    if shutil.which("pdftoppm"):
        def rendered(pdf):
            return subprocess.check_output(["pdftoppm", "-f", "1", "-l", "1", "-singlefile", "-r", "72", "-png", str(pdf)])
        cover_pixels = "PASS" if rendered(accepted_cover) == rendered(path) else "FAIL"
        if cover_pixels == "FAIL":
            errors.append("Cover pixels differ from the accepted vector cover")
    counts = structure["tags"]
    for required in ("/H1", "/H2", "/H3", "/P", "/Table", "/TH", "/TD", "/Caption", "/Figure", "/Link"):
        if not counts.get(required):
            errors.append(f"Missing required semantic role {required}")
    return {"status": "FAIL" if errors else "PASS", "file": str(path),
            "sha256": hashlib.sha256(path.read_bytes()).hexdigest(), "pages": len(reader.pages),
            "errors": errors, "structure_tags": counts, "sections": dict(coverage),
            "blocks_checked": sum(value["blocks"] for value in coverage.values()),
            "marked_text_runs": structure.get("marked_text_runs", 0),
            "untagged_text": structure.get("untagged_text", []),
            "tables": structure.get("table_checks", {}), "missing_alternatives": missing_alts,
            "chart_data": chart_data_checks,
            "links": {"annotations": link_count, "external_unique": len(uris), "internal_unique": len(internal),
                      "missing_external": missing_links, "missing_internal": sorted(expected_internal - internal)},
            "bookmarks": len(outline), "cover": {"selectable_text": bool(cover_text.strip()),
                "vector_pixels_match": cover_pixels, "logical_text_blocks": len(cover_records)},
            "assistive_reading": "NOT_RUN", "visual_review": "SEPARATE_REQUIRED"}


def run_verapdf(executable, path, destination):
    command = [str(executable), "--flavour", "ua1", "--format", "json", str(path)]
    process = subprocess.run(command, capture_output=True, text=True, timeout=180)
    destination.write_text(process.stdout)
    destination.with_suffix(".stderr.txt").write_text(process.stderr)
    try:
        report = json.loads(process.stdout)
        details = report["report"]["jobs"][0]["validationResult"][0]
        compliant = details["compliant"]
        profile = details["profileName"]
        if "UA-1" not in profile:
            raise ValueError("Unexpected validation profile")
        return {"status": "PASS" if compliant else "FAIL", "profile": profile,
                "machine_compliant": compliant, "process_exit": process.returncode,
                "report": str(destination), "details": details}
    except (ValueError, KeyError, IndexError, TypeError) as error:
        return {"status": "FAIL", "reason": "Cannot establish UA-1 result: " + str(error),
                "process_exit": process.returncode, "report": str(destination)}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--pdf-dir", type=Path, default=ROOT / "public/reports")
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--verapdf", type=Path)
    args = parser.parse_args()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    reports = {}
    for brand in ("ASP24", "NGGroup"):
        path = args.pdf_dir / f"{brand}_Review.pdf"
        try:
            result = verify_report(path, brand)
        except Exception as error:
            result = {"status": "FAIL", "file": str(path), "errors": [f"{type(error).__name__}: {error}"]}
        result["verapdf_ua1"] = run_verapdf(args.verapdf, path, args.output.parent / f"{brand}-verapdf-ua1.json") if args.verapdf else {"status": "NOT_RUN"}
        if result["verapdf_ua1"]["status"] == "FAIL":
            result["status"] = "FAIL"
        reports[brand] = result
    passed = all(result["status"] == "PASS" for result in reports.values())
    result = {"status": "PASS" if passed else "FAIL", "generated_at_utc": datetime.now(timezone.utc).isoformat(),
              "manuscript_sha256": hashlib.sha256((ROOT / "reports/content.json").read_bytes()).hexdigest(),
              "reports": reports, "r42": "STRUCTURE_MACHINE_VERIFIED_VISUAL_ACCEPTANCE_REQUIRED" if passed else "OPEN",
              "assistive_reading": "NOT_RUN", "pdf_ua_claim": False,
              "pdf_ua": "PASS_MACHINE_VALIDATION" if all(value["verapdf_ua1"]["status"] == "PASS" for value in reports.values()) else "NOT_CONFIRMED",
              "scope": "Automated structural, exact text/reading order, tables, links and cover gate. Full-page visual review and assistive reading are separate evidence."}
    args.output.write_text(json.dumps(result, ensure_ascii=False, indent=2, default=str) + "\n")
    print(json.dumps({"status": result["status"], "output": str(args.output),
                      "reports": {brand: {key: value.get(key) for key in ("status", "pages", "blocks_checked", "errors")} for brand, value in reports.items()}}, ensure_ascii=False))
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
