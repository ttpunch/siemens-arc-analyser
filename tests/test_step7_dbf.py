"""dBase III table and STEP 7 memo (`fff`-wrapped) reader tests. Synthetic only."""
import tempfile
import unittest
import zipfile
from pathlib import Path

from arc_analyser.step7.s7_dbf import (
    BAUSTEIN_TYP,
    memo_bytes,
    memo_payload,
    read_dbf,
    text_runs,
)
from step7_fixtures import build_dbf, build_dbt


class DbfReaderTest(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.dir = Path(self.temp.name)

    def test_reads_fields_and_rows(self) -> None:
        data = build_dbf(
            [("ID", "N", 11), ("TYP", "C", 5), ("NUMMER", "C", 5)],
            [{"ID": 15, "TYP": 12, "NUMMER": 67}, {"ID": 16, "TYP": 14, "NUMMER": 99}],
        )
        (self.dir / "t.DBF").write_bytes(data)
        table = read_dbf(self.dir, "t.DBF")
        self.assertEqual(len(table.rows), 2)
        self.assertEqual([f.name for f in table.fields], ["ID", "TYP", "NUMMER"])
        self.assertEqual(table.rows[0]["NUMMER"].strip(), "67")

    def test_deleted_rows_are_skipped(self) -> None:
        data = build_dbf([("ID", "N", 5)], [{"ID": 1}, {"ID": 2}], deleted={0})
        (self.dir / "d.DBF").write_bytes(data)
        table = read_dbf(self.dir, "d.DBF")
        self.assertEqual([r["ID"].strip() for r in table.rows], ["2"])
        self.assertEqual(table.deleted, 1)

    def test_reader_accepts_zipfile_members(self) -> None:
        data = build_dbf([("ID", "N", 5)], [{"ID": 7}])
        path = self.dir / "p.zip"
        with zipfile.ZipFile(path, "w") as z:
            z.writestr("proj/ombstx/offline/00000001/BAUSTEIN.DBF", data)
        with zipfile.ZipFile(path) as z:
            table = read_dbf(z, "proj/ombstx/offline/00000001/BAUSTEIN.DBF")
        self.assertEqual(table.rows[0]["ID"].strip(), "7")


class MemoTest(unittest.TestCase):
    def test_wrapped_entry_length_is_honoured(self) -> None:
        payload = bytes(range(40))
        self.assertEqual(memo_payload(build_dbt({3: payload}), 3), payload)

    def test_zero_index_is_empty(self) -> None:
        self.assertEqual(memo_payload(build_dbt({1: b"abc"}), 0), b"")

    def test_unwrapped_entry_falls_back_to_terminator(self) -> None:
        buf = bytearray(1024)
        buf[512:515] = b"abc"
        buf[520:522] = b"\x1a\x1a"
        raw = memo_bytes(bytes(buf), 1)
        self.assertTrue(raw.startswith(b"abc"))
        self.assertLessEqual(len(raw), 8)

    def test_truncated_memo_index_is_empty(self) -> None:
        self.assertEqual(memo_payload(build_dbt({1: b"abc"}), 99), b"")

    def test_text_runs_picks_titles_from_binary(self) -> None:
        blob = b"\x00\x01HYDRAULIC PUMP\xff\x00SPHERICAL JOINT\x00"
        self.assertEqual(text_runs(blob), ["HYDRAULIC PUMP", "SPHERICAL JOINT"])


class CodeTableTest(unittest.TestCase):
    def test_block_type_codes(self) -> None:
        self.assertEqual(BAUSTEIN_TYP[12], "FC")
        self.assertEqual(BAUSTEIN_TYP[14], "FB")
        self.assertEqual(BAUSTEIN_TYP[8], "OB")
        self.assertEqual(BAUSTEIN_TYP[10], "DB")
        self.assertEqual(BAUSTEIN_TYP[13], "SFC")


if __name__ == "__main__":
    unittest.main()
