"""End-to-end tests of the STEP 7 project reader on a synthetic project. No machine data."""
import csv
import tempfile
import unittest
import zipfile
from pathlib import Path

from arc_analyser.step7.s7_project import (
    _open,
    block_key,
    footprint,
    load_blocks,
    load_symbols,
    load_xref,
    main,
    render_report,
    surface,
    symbol_index,
)
from step7_fixtures import project_members, write_project_zip


class ProjectReaderTest(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.dir = Path(self.temp.name)
        self.zip = write_project_zip(self.dir / "proj.zip")

    def test_block_catalog_joins_catalog_and_parts(self) -> None:
        with zipfile.ZipFile(self.zip) as z:
            blocks = load_blocks(z)
        self.assertEqual(len(blocks), 1)
        block = blocks[0]
        self.assertEqual((block["type"], block["number"], block["label"]), ("FC", 67, "FC67"))
        self.assertEqual(block["parts"], 3)
        self.assertEqual(block["mc5_len"], 4)
        self.assertEqual(block["language"], "STL/AWL")

    def test_symbolic_name_comes_from_symbol_table(self) -> None:
        with zipfile.ZipFile(self.zip) as z:
            blocks = load_blocks(z)
            symbols = load_symbols(z, "proj")
        by_operand = {s["operand"].split()[0] + s["operand"].split()[1]: s for s in symbols}
        self.assertIn("FC67", by_operand)
        self.assertEqual(by_operand["FC67"]["name"], "S.R. 1 - HYDROSTATIC")

    def test_surface_recovers_title_titles_references_and_code(self) -> None:
        with zipfile.ZipFile(self.zip) as z:
            block = load_blocks(z)[0]
            surf = surface(z, block)
        self.assertEqual(surf["title"], "HYDROSTATIC SR 1")
        self.assertIn("HYDROSTATICS OF STEADY REST 1", surf["titles"])
        self.assertIn("QUILL UP /DOWN", surf["titles"])
        self.assertEqual(surf["references"], ["DB2", "DB10", "FC103", "FB99"])
        self.assertEqual(surf["code"], b"\x80\x0c\xc1\x28")

    def test_footprint_resolves_operands_to_symbols_and_calls(self) -> None:
        with zipfile.ZipFile(self.zip) as z:
            blocks = load_blocks(z)
            symbols = load_symbols(z, "proj")
            xref, tables = load_xref(z, "proj")
        self.assertEqual(len(tables), 1)
        self.assertEqual(len(xref), 4)
        idx = symbol_index(symbols)
        foot = footprint(xref, idx, {})
        kinds = {f["kind"]: f for f in foot}
        self.assertEqual(kinds["input"]["operand"], "I 36.6")
        self.assertEqual(kinds["input"]["symbol"], "60Q1")
        self.assertEqual(kinds["output"]["symbol"], "60K1")
        self.assertEqual(kinds["data block"]["operand"], "DB2.DBX205.4")
        self.assertEqual(kinds["FC call"]["operand"], "FC103")

    def test_report_states_evidence_and_limits(self) -> None:
        with zipfile.ZipFile(self.zip) as z:
            blocks = load_blocks(z)
            symbols = load_symbols(z, "proj")
            xref, _ = load_xref(z, "proj")
            block = blocks[0]
            block["symbol"] = "S.R. 1 - HYDROSTATIC"
            block["comment"] = ""
            surf = surface(z, block)
            md = render_report(block, surf, [], xref, footprint(xref, symbol_index(symbols), {}))
        self.assertIn("# FC67 — S.R. 1 - HYDROSTATIC", md)
        self.assertIn("HYDROSTATICS OF STEADY REST 1", md)
        self.assertIn("60Q1", md)
        self.assertIn("Limits of this report", md)

    def test_cli_writes_artifacts(self) -> None:
        out = self.dir / "out"
        self.assertEqual(main([str(self.zip), "--out", str(out), "--report", "FC67"]), 0)
        for name in ("blocks.csv", "symbols.csv", "xref.csv", "callgraph.csv"):
            self.assertTrue((out / name).is_file(), name)
        rows = list(csv.DictReader((out / "blocks.csv").open()))
        self.assertEqual(rows[0]["label"], "FC67")
        self.assertEqual(rows[0]["surface_title"], "HYDROSTATIC SR 1")
        self.assertTrue((out / "blocks" / "FC67.md").is_file())

    def test_block_label_parser(self) -> None:
        self.assertEqual(block_key("FC67"), ("FC", 67))
        self.assertEqual(block_key("FC 67"), ("FC", 67))
        self.assertEqual(block_key("sfc17"), ("SFC", 17))
        with self.assertRaises(SystemExit):
            block_key("nonsense")


class DuplicateCopyTest(unittest.TestCase):
    def test_two_ombstx_copies_are_not_double_counted(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            zpath = Path(td) / "two.zip"
            with zipfile.ZipFile(zpath, "w") as z:
                for root in ("old", "new"):
                    for name, data in project_members(root).items():
                        z.writestr(name, data)
            with zipfile.ZipFile(zpath) as z:
                blocks = load_blocks(z)
            self.assertEqual(len(blocks), 1, "only the chosen copy must be counted")

    def test_folder_filter_selects_a_copy(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            zpath = Path(td) / "two.zip"
            with zipfile.ZipFile(zpath, "w") as z:
                for root in ("old", "new"):
                    for name, data in project_members(root).items():
                        z.writestr(name, data)
            with zipfile.ZipFile(zpath) as z:
                blocks = load_blocks(z, "old/ombstx")
            self.assertEqual(len(blocks), 1)
            self.assertTrue(blocks[0]["folder"].startswith("old"))


if __name__ == "__main__":
    unittest.main()
