#!/usr/bin/env python3
"""Corrupt real generated PDFs in memory to prove the structural gate fails.

No synthetic mirrors of renderer output and no changes to accepted files.
"""
import argparse
import importlib.util
from pathlib import Path
import unittest

from pypdf import PdfReader
from pypdf.generic import ArrayObject, BooleanObject, NameObject, TextStringObject

SPEC = importlib.util.spec_from_file_location("validator", Path(__file__).with_name("verify-structured-pdfs.py"))
VALIDATOR = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(VALIDATOR)
PDF_DIR = VALIDATOR.ROOT / "public/reports"


def elements(reader):
    def visit(value):
        obj = VALIDATOR.deref(value)
        if isinstance(obj, list):
            for child in obj:
                yield from visit(child)
        elif isinstance(obj, dict):
            if "/S" in obj:
                yield obj
            yield from visit(obj.get("/K"))
    yield from visit(reader.trailer["/Root"]["/StructTreeRoot"])


class CorruptionTests(unittest.TestCase):
    def reader(self):
        return PdfReader(PDF_DIR / "ASP24_Review.pdf")

    def failures(self, reader):
        return VALIDATOR.inspect_structure(reader)["errors"]

    def test_both_real_reports_have_valid_structure(self):
        for brand in ("ASP24", "NGGroup"):
            with self.subTest(brand=brand):
                self.assertEqual(self.failures(PdfReader(PDF_DIR / f"{brand}_Review.pdf")), [])

    def test_missing_tree_is_rejected(self):
        reader = self.reader()
        del reader.trailer["/Root"]["/StructTreeRoot"]
        self.assertIn("Missing StructTreeRoot", self.failures(reader))

    def test_false_mark_info_is_rejected(self):
        reader = self.reader()
        reader.trailer["/Root"]["/MarkInfo"][NameObject("/Marked")] = BooleanObject(False)
        self.assertIn("MarkInfo/Marked is not true", self.failures(reader))

    def test_missing_figure_alternative_is_rejected(self):
        reader = self.reader()
        figure = next(obj for obj in elements(reader) if obj.get("/S") == "/Figure")
        del figure["/Alt"]
        self.assertTrue(any("lacks meaningful Alt" in value for value in self.failures(reader)))

    def test_existing_but_wrong_header_id_is_rejected(self):
        reader = self.reader()
        all_elements = list(elements(reader))
        cell = next(obj for obj in all_elements if obj.get("/S") == "/TD")
        current = {str(value) for value in cell["/A"]["/Headers"]}
        wrong = next(obj["/ID"] for obj in all_elements
                     if obj.get("/S") == "/TH" and "/ID" in obj and str(obj["/ID"]) not in current)
        cell["/A"][NameObject("/Headers")] = ArrayObject([TextStringObject(str(wrong))])
        self.assertTrue(any("header associations do not match" in value for value in self.failures(reader)))

    def test_removed_logical_text_owner_is_rejected(self):
        reader = self.reader()
        paragraph = next(obj for obj in elements(reader)
                         if obj.get("/S") == "/P" and obj.get("/K"))
        paragraph[NameObject("/K")] = ArrayObject()
        self.assertTrue(any("text MCIDs have no logical owner" in value for value in self.failures(reader)))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--pdf-dir", type=Path, default=PDF_DIR)
    args = parser.parse_args()
    PDF_DIR = args.pdf_dir
    unittest.main(argv=[__file__])
