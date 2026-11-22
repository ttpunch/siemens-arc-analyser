"""Tests for skills/tia-consistency-diagnosis/scripts/consistency_triage.py.

The fixtures are synthetic: three blocks, two inconsistent, one auto-generated export failure and one
consistent caller, so every section of the report is exercised without any Siemens data.
"""

from __future__ import annotations

import pathlib
import subprocess
import sys
import tempfile
import unittest

SCRIPT = (
    pathlib.Path(__file__).resolve().parents[1]
    / "skills"
    / "tia-consistency-diagnosis"
    / "scripts"
    / "consistency_triage.py"
)

# BLOCK|plc|depth|group|class|name|number|language|header|memory|consistent|protected
INVENTORY = """\
BLOCK|/PLC_1|0|Grp|FB|BlockA|10|SCL|1.0|Standard|False|True
BLOCK|/PLC_1|0|Grp|FC|BlockB|11|LAD|1.0|Standard|True|False
BLOCK|/PLC_1|1|Grp/Sub|DB|BlockC|12|DB|2.0|Standard|False|False
BLOCK|/PLC_1|1|Grp/Sub|OB|Main|1|LAD|2.0|Standard|True|False
"""

# EXPORT|state|<number>_<Name>|<path or error>
EXPORT_LOG = """\
EXPORT|ok|11_BlockB|C:\\out\\11_BlockB.xml
EXPORT|ok|1_Main|C:\\out\\1_Main.xml
EXPORT|fail|10_BlockA|EngineeringTargetInvocationException: Error when calling method 'Export'
EXPORT|fail|12_BlockC|EngineeringTargetInvocationException: Error when calling method 'Export'
EXPORT|fail|123_FobRuntime|EngineeringTargetInvocationException: Error when calling method 'Export'
"""

BLOCK_B_XML = """<?xml version="1.0" encoding="utf-8"?>
<Document>
  <SW.Blocks.FC ID="0">
    <Call><CallInfo Name="BlockA" BlockType="FB"/></Call>
  </SW.Blocks.FC>
</Document>
"""

MAIN_XML = """<?xml version="1.0" encoding="utf-8"?>
<Document>
  <SW.Blocks.OB ID="0">
    <Call><CallInfo Name="BlockB" BlockType="FC"/></Call>
  </SW.Blocks.OB>
</Document>
"""


class TriageTest(unittest.TestCase):
    def _run(self, tmp: pathlib.Path) -> str:
        inventory = tmp / "inventory.txt"
        log = tmp / "export_log.txt"
        xml_dir = tmp / "xml"
        xml_dir.mkdir()
        inventory.write_text(INVENTORY, encoding="utf-8")
        log.write_text(EXPORT_LOG, encoding="utf-8")
        (xml_dir / "11_BlockB.xml").write_text(BLOCK_B_XML, encoding="utf-8")
        (xml_dir / "1_Main.xml").write_text(MAIN_XML, encoding="utf-8")
        out = tmp / "report.md"

        proc = subprocess.run(
            [
                sys.executable,
                str(SCRIPT),
                "--inventory", str(inventory),
                "--export-log", str(log),
                "--xml-dir", str(xml_dir),
                "--out", str(out),
            ],
            capture_output=True,
            text=True,
        )
        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertTrue(out.is_file(), "report was not written")
        return out.read_text(encoding="utf-8")

    def test_counts_and_header(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            report = self._run(pathlib.Path(d))
        self.assertIn("Blocks enumerated: **4**", report)
        self.assertIn("inconsistent: **2**", report)
        self.assertIn("know-how protected: **1**", report)

    def test_export_oracle_separates_inconsistent_from_auto_generated(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            report = self._run(pathlib.Path(d))
        self.assertIn("inconsistent blocks that failed export: **2/2**", report)
        # FobRuntime failed export but is reported consistent -> auto-generated bucket
        self.assertIn("FobRuntime", report)
        self.assertIn("failed export but reported consistent", report)

    def test_inconsistent_table_lists_block_details(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            report = self._run(pathlib.Path(d))
        self.assertIn("| FB | 10 | BlockA | SCL | 1.0 | yes | Grp |", report)
        self.assertIn("| DB | 12 | BlockC | DB | 2.0 | no | Grp/Sub |", report)

    def test_header_version_clusters(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            report = self._run(pathlib.Path(d))
        self.assertIn("`1.0` — 1: BlockA", report)
        self.assertIn("`2.0` — 1: BlockC", report)

    def test_consistent_caller_detected_from_exported_xml(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            report = self._run(pathlib.Path(d))
        self.assertIn("## Called from consistent code", report)
        self.assertIn("**BlockA** ← BlockB", report)

    def test_evidence_disclaimer_present(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            report = self._run(pathlib.Path(d))
        self.assertIn("TIA does not expose the reason for `IsConsistent=False`", report)


if __name__ == "__main__":
    unittest.main()
