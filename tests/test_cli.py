"""Synthetic fixtures only; no machine archives are needed."""
import hashlib
import io
import json
from pathlib import Path
import subprocess
import sys
import tarfile
import tempfile
import unittest
import zipfile

from arc_analyser.cli import inspect_archive


class ArchiveTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.path = Path(self.temp.name) / 'test.arc'

    def check_format(self, content: bytes, expected: str) -> None:
        self.path.write_bytes(content)
        before = hashlib.sha256(content).hexdigest()
        result = inspect_archive(self.path)
        self.assertEqual(result['detected_format'], expected)
        self.assertFalse(result['extraction_supported'])
        self.assertEqual(result['filename'], 'test.arc')
        self.assertEqual(result['size_bytes'], len(content))
        self.assertEqual(result['header_hex_first_32'], content[:32].hex())
        self.assertEqual(hashlib.sha256(self.path.read_bytes()).hexdigest(), before)
        self.assertEqual(list(self.path.parent.iterdir()), [self.path])

    def test_unknown_and_empty(self) -> None:
        for content in (b'unknown', b''):
            with self.subTest(content=content):
                self.check_format(content, 'unknown')

    def test_zip(self) -> None:
        buffer = io.BytesIO()
        with zipfile.ZipFile(buffer, 'w') as archive:
            archive.writestr('test.txt', 'test')
        self.check_format(buffer.getvalue(), 'zip-compatible')

    def test_empty_zip(self) -> None:
        buffer = io.BytesIO()
        with zipfile.ZipFile(buffer, 'w'):
            pass
        self.check_format(buffer.getvalue(), 'zip-compatible')

    def test_tar(self) -> None:
        buffer = io.BytesIO()
        with tarfile.open(fileobj=buffer, mode='w', format=tarfile.USTAR_FORMAT) as archive:
            archive.addfile(tarfile.TarInfo('test.txt'), io.BytesIO())
        self.check_format(buffer.getvalue(), 'tar-compatible')

    def test_7z_signature(self) -> None:
        self.check_format(bytes.fromhex('377abcaf271c'), '7z-compatible')

    def test_rar_signatures(self) -> None:
        for signature in (b'Rar!\x1a\x07\x00', b'Rar!\x1a\x07\x01\x00'):
            with self.subTest(signature=signature):
                self.check_format(signature, 'rar-compatible')

    def test_incomplete_rar_signatures(self) -> None:
        for signature in (b'Rar!\x1a\x07', b'Rar!\x1a\x07\x01', b'Rar!\x1a\x07\xff'):
            with self.subTest(signature=signature):
                self.check_format(signature, 'unknown')

    def test_missing_file(self) -> None:
        with self.assertRaises(FileNotFoundError):
            inspect_archive(self.path)

    def test_directory(self) -> None:
        with self.assertRaises(FileNotFoundError):
            inspect_archive(self.path.parent)

    def test_cli_json(self) -> None:
        self.path.write_bytes(b'unknown')
        result = subprocess.run([sys.executable, '-m', 'arc_analyser.cli', str(self.path)], capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(json.loads(result.stdout)['detected_format'], 'unknown')

    def test_cli_missing_file(self) -> None:
        result = subprocess.run([sys.executable, '-m', 'arc_analyser.cli', str(self.path)], capture_output=True, text=True)
        self.assertEqual(result.returncode, 2)
        self.assertIn('cannot inspect archive', result.stderr)
        self.assertNotIn('Traceback', result.stderr)


if __name__ == '__main__':
    unittest.main()
