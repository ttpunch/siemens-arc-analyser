import csv
import tempfile
import unittest
from pathlib import Path

from arc_analyser.step7 import awl_callgraph

OB1 = '''ORGANIZATION_BLOCK OB1
TITLE =
BEGIN
NETWORK
TITLE =
      CALL  "GP_HP";
      CALL  "Push button", DB165 (
            Conditions_ok := M 1.0);
      CALL  FC 12;
// CALL "COMMENTED"
      CC    "Reset Allarms";
      CALL  "Unknown block";
END_ORGANIZATION_BLOCK
'''

FC2 = '''FUNCTION "GP_HP" : VOID
BEGIN
NETWORK
      UC    FC    9;
END_FUNCTION
'''

FB99 = '''FUNCTION_BLOCK "Push button"
BEGIN
END_FUNCTION_BLOCK
'''

FC110 = '''FUNCTION "Reset Allarms" : VOID
BEGIN
END_FUNCTION
'''


class AwlCallgraphTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.dir = Path(self.tmp.name)
        for name, text in {"OB1": OB1, "FC2": FC2, "FB99": FB99, "FC110": FC110}.items():
            (self.dir / f"{name}.awl").write_text(text, encoding="utf-8")

    def tearDown(self):
        self.tmp.cleanup()

    def test_edges_resolve_symbols_and_skip_comments(self):
        files = sorted(self.dir.glob("*.awl"))
        table = awl_callgraph.symbol_table(files)
        self.assertEqual(table["GP_HP"], "FC2")
        self.assertEqual(table["Push button"], "FB99")
        rows = set(awl_callgraph.edges(files, table))
        self.assertIn(("OB1", "FC2", "CALL", ""), rows)
        self.assertIn(("OB1", "FB99", "CALL", "DB165"), rows)
        self.assertIn(("OB1", "FC12", "CALL", ""), rows)
        self.assertIn(("OB1", "FC110", "CC", ""), rows)
        self.assertIn(("FC2", "FC9", "UC", ""), rows)
        self.assertIn(("OB1", "Unknown block?", "CALL", ""), rows)
        self.assertFalse(any("COMMENTED" in r[1] for r in rows))

    def test_cli_writes_csv(self):
        out = self.dir / "out" / "callgraph.csv"
        self.assertEqual(awl_callgraph.main([str(self.dir), "--out", str(out)]), 0)
        with out.open(encoding="utf-8") as fh:
            rows = list(csv.DictReader(fh))
        self.assertTrue(rows)
        self.assertEqual(set(rows[0]), {"caller", "callee", "kind", "instance"})


if __name__ == "__main__":
    unittest.main()
