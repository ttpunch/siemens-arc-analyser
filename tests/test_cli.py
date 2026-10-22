from pathlib import Path
import zipfile
from arc_analyser.cli import inspect_archive


def test_unknown(tmp_path: Path):
    file = tmp_path / 'test.arc'
    file.write_bytes(b'unknown')
    assert inspect_archive(file)['detected_format'] == 'unknown'


def test_zip(tmp_path: Path):
    file = tmp_path / 'test.arc'
    with zipfile.ZipFile(file, 'w') as archive:
        archive.writestr('test.txt', 'test')
    assert inspect_archive(file)['detected_format'] == 'zip-compatible'
