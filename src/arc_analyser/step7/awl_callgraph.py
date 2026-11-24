"""Build a call graph from decoded STEP 7 AWL files (read-only, standard library only).

Input: a directory of ``<LABEL>.awl`` files written by ``s7awl`` / ``s7_dotnet_awl``
(for example ``FC2.awl``, ``OB1.awl``). Each file starts with a header such as
``FUNCTION "GP_HP" : VOID`` or ``ORGANIZATION_BLOCK OB1``.

Output: ``callgraph.csv`` with ``caller,callee,kind,instance`` where kind is
CALL / UC / CC and instance is the DB used for an FB call (empty otherwise).

Calls may name a block symbolically (``CALL "GP_HP"``) or absolutely (``CALL FC 12``).
Symbolic names are resolved to labels from the header of the matching file; a name that
no file declares is kept as written and marked unresolved with ``?``.

    python -m arc_analyser.step7.awl_callgraph <awl dir> --out callgraph.csv
"""
from __future__ import annotations

import argparse
import csv
import re
import sys
from pathlib import Path

HEADER = re.compile(
    r'^\s*(FUNCTION_BLOCK|FUNCTION|ORGANIZATION_BLOCK|DATA_BLOCK|TYPE)\s+("([^"]+)"|\S+)',
    re.IGNORECASE,
)
CALL = re.compile(
    r'^\s*(CALL|UC|CC)\s+("[^"]+"|(?:FC|FB|SFC|SFB)\s*\d+)'
    r'(?:\s*,\s*(DB\s*\d+|DI\s*\d+|"[^"]+"))?',
    re.IGNORECASE,
)
LABEL = re.compile(r'^(FC|FB|SFC|SFB|OB|DB|UDT|VAT)(\d+)$', re.IGNORECASE)


def normalise(token: str) -> str:
    """'FC  12' -> 'FC12'; a quoted symbol keeps its text without quotes."""
    token = token.strip()
    if token.startswith('"'):
        return token.strip('"')
    return re.sub(r"\s+", "", token).upper()


def symbol_table(files: list[Path]) -> dict[str, str]:
    """Map symbolic block names to labels using the file name as the label."""
    table: dict[str, str] = {}
    for f in files:
        label = f.stem.upper()
        if not LABEL.match(label):
            continue
        for line in f.read_text(encoding="utf-8", errors="replace").splitlines()[:10]:
            m = HEADER.match(line)
            if m and m.group(3):
                table[m.group(3)] = label
                break
    return table


def edges(files: list[Path], table: dict[str, str]) -> list[tuple[str, str, str, str]]:
    rows: list[tuple[str, str, str, str]] = []
    for f in sorted(files):
        caller = f.stem.upper()
        if not LABEL.match(caller):
            continue
        for line in f.read_text(encoding="utf-8", errors="replace").splitlines():
            if line.lstrip().startswith("//"):
                continue
            m = CALL.match(line)
            if not m:
                continue
            kind = m.group(1).upper()
            callee = normalise(m.group(2))
            if callee in table:
                callee = table[callee]
            elif not LABEL.match(callee):
                callee = callee + "?"
            inst = normalise(m.group(3)) if m.group(3) else ""
            rows.append((caller, callee, kind, inst))
    return rows


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Call graph from decoded AWL files")
    ap.add_argument("awl_dir", type=Path)
    ap.add_argument("--out", type=Path, required=True)
    args = ap.parse_args(argv)

    files = sorted(args.awl_dir.glob("*.awl"))
    if not files:
        print(f"no .awl files in {args.awl_dir}", file=sys.stderr)
        return 1
    table = symbol_table(files)
    rows = edges(files, table)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    with args.out.open("w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(["caller", "callee", "kind", "instance"])
        w.writerows(rows)
    unresolved = sorted({r[1] for r in rows if r[1].endswith("?")})
    print(f"files   : {len(files)}")
    print(f"symbols : {len(table)}")
    print(f"edges   : {len(rows)}")
    if unresolved:
        print(f"unresolved callee names: {', '.join(unresolved[:20])}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
