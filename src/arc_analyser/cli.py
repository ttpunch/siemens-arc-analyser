"""Read-only signature inspector. Never extracts or executes content."""
import argparse
import json
from pathlib import Path
import zipfile


def inspect_archive(path: Path) -> dict[str, str | int | bool]:
    if not path.is_file():
        raise FileNotFoundError(path)
    with path.open('rb') as f:
        header = f.read(512)
    kind = 'unknown'
    if zipfile.is_zipfile(path):
        kind = 'zip-compatible'
    elif header[257:262] == b'ustar':
        kind = 'tar-compatible'
    elif header.startswith(bytes.fromhex('377abcaf271c')):
        kind = '7z-compatible'
    elif header.startswith((b'Rar!\x1a\x07\x00', b'Rar!\x1a\x07\x01\x00')):
        kind = 'rar-compatible'
    return {'filename': path.name, 'size_bytes': path.stat().st_size, 'header_hex_first_32': header[:32].hex(), 'detected_format': kind, 'extraction_supported': False}


def main() -> None:
    parser = argparse.ArgumentParser(description='Inspect archive without extraction')
    parser.add_argument('archive', type=Path)
    args = parser.parse_args()
    try:
        result = inspect_archive(args.archive)
    except OSError as exc:
        parser.exit(2, f'error: cannot inspect archive: {exc}\n')
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
