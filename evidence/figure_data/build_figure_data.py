#!/usr/bin/env python3
"""Build source-traceable CSV inputs for editorial figures. Standard library only.

Historical counts describe saved pages; autonomy is a model, not a measurement.
Outputs are deterministic. This script does not contact websites or edit reports.
"""
import csv
import hashlib
import importlib.util
import json
import re
import sys
from decimal import Decimal, ROUND_HALF_UP
from pathlib import Path


sys.dont_write_bytecode = True

HERE = Path(__file__).resolve().parent
RECOVERED = HERE.parent / "recovered_sources"


def write_csv(name, rows):
    with (HERE / name).open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    spec = importlib.util.spec_from_file_location(
        "source_counts", RECOVERED / "recompute_source_measures.py"
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    audit = module.recompute(RECOVERED)
    technical = []
    for pair in audit["pairs"]:
        for side in ("before", "after"):
            snapshot = pair[side]
            technical.append({
                "sku": pair["sku"], "model": pair["model"], "side": side,
                "capture_utc": snapshot["capture_utc"],
                "technical_rows": snapshot["technical_row_count"],
                "source_file": "../recovered_sources/" + snapshot["source_file"],
                "source_sha256": snapshot["parsed_file_sha256"],
                "evidence_kind": "historical_parser_row_count",
                "limit": "Selected product tables only; zero is not zero information in the page.",
            })
    write_csv("technical_rows.csv", technical)

    # Recount the two known DOM routes; do not treat page counts as user conversion.
    routes = [
        ("ASP24", "asp24-20260910", "2026-09-10", [
            ("Уся категорія", "asp-cable-category.txt", 9, "start"),
            ("Cu", "asp-cable-cu-settled.txt", 4, "filter"),
            ("Cu + У приміщеннях", "asp-cable-cu-indoor.txt", 2, "filter"),
        ]),
        ("NG Group", "nggroup-20260910", "2026-09-10", [
            ("Уся категорія", "cable-before.txt", 10, "start"),
            ("Cu", "cable-cu-success.txt", 4, "filter"),
            ("Cu + Ззовні", "cable-cu-out.txt", 2, "filter"),
            ("Cu + Ззовні + 4 пари", "cable-cu-out4.txt", 1, "filter"),
            ("Повернення через крихту «Вита пара»", "cable-breadcrumb-return.txt", 10, "return_reset"),
        ]),
    ]
    filter_rows = []
    for brand, directory, date, states in routes:
        for step, (label, filename, expected, action) in enumerate(states):
            path = RECOVERED / directory / filename
            text = path.read_text(encoding="utf-8")
            if brand == "ASP24":
                count = len(re.findall(r"Артикул", text))
                method = "SKU label occurrences in saved category DOM"
            else:
                urls = re.findall(r"- /url: (\S*?/nglan-utp-\S*)", text)
                count = len(set(urls))
                method = "Unique /nglan-utp- product URLs in saved DOM"
            if count != expected:
                raise ValueError(f"Unexpected source count for {filename}: {count}, expected {expected}")
            filter_rows.append({
                "brand": brand, "step": step, "condition_or_action": label,
                "product_count": count, "action_type": action, "capture_date": date,
                "source_file": f"../recovered_sources/{directory}/{filename}",
                "source_sha256": sha(path), "method": method,
                "evidence_kind": "historical_DOM_count",
                "limit": "One observed route; not user conversion or filter recall.",
            })
    write_csv("filter_paths.csv", filter_rows)

    # Explicit scenario grid. Only 13/15 W are the two reference loads in the review.
    cells, volts, amp_hours = Decimal("6"), Decimal("3.7"), Decimal("2.6")
    energy = cells * volts * amp_hours
    autonomy = []
    for load in ["5", "7.5", "10", "13", "15", "20", "25", "30", "35"]:
        hours = energy / Decimal(load)
        autonomy.append({
            "load_w": load, "nominal_energy_wh": str(energy),
            "ideal_hours": str(hours.quantize(Decimal("0.000001"), rounding=ROUND_HALF_UP)),
            "reference_load_in_review": load in ("13", "15"),
            "formula": "6*3.7*2.6/load_w", "efficiency_assumption": "1 (lossless model)",
            "evidence_kind": "calculated_scenario_not_measurement",
            "source_files": "../recovered_sources/nggroup-20260910/ups-m1550.txt;../recovered_sources/nggroup-20260910/ups-description.txt",
            "limit": "No conversion loss, ageing or time-varying load; not device runtime validation.",
        })
    write_csv("nominal_autonomy.csv", autonomy)

    inputs = [RECOVERED / "recompute_source_measures.py", RECOVERED / "real-data-measures.json",
              HERE / "demo_facts.json"]
    metadata = {
        "purpose": "Figure inputs for report editing, not final published figures.",
        "historical_count_method": audit["method"],
        "source_inputs": [{"file": str(p.relative_to(HERE.parent)), "sha256": sha(p)} for p in inputs],
        "outputs": {"technical_rows.csv": len(technical), "filter_paths.csv": len(filter_rows),
                    "nominal_autonomy.csv": len(autonomy)},
        "limits": audit["limitations"] + [
            "Autonomy grid is chosen for illustration, not a measured distribution.",
            "Demo facts are synthetic fixtures; do not infer market, user or business metrics.",
        ],
    }
    (HERE / "figure_data_provenance.json").write_text(
        json.dumps(metadata, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps({"generated": metadata["outputs"], "nominal_energy_wh": str(energy)}))


if __name__ == "__main__":
    main()
