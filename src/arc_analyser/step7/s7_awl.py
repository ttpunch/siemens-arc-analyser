"""Decode a STEP 7 block's compiled MC7 payload into annotated AWL/STL.

Uses the ``mc7dis`` CLI built from rizinorg/rz-libmc7 (see
``references/local-tools.md`` for the build command). The decoder supplies the
instruction stream; the project's own symbol table supplies names and comments,
so every annotation traces back to the project files.

Usage
-----
    python3 s7_awl.py <project.zip|dir> --out OUTDIR --block FC67
    python3 s7_awl.py <project.zip|dir> --out OUTDIR --awl-all
    python3 s7_awl.py <project.zip|dir> --out OUTDIR --block FC67 --mc7dis /path/to/mc7dis

Output: ``OUTDIR/awl/<LABEL>.awl`` plus a short console summary.

Read-only: the project is never modified, nothing is written back, no PLC is
contacted.
"""

from __future__ import annotations

import argparse
import collections
import hashlib
import os
import re
import subprocess
import sys
from pathlib import Path

from s7_dbf import clean  # noqa: E402
from .s7_project import (  # noqa: E402
    _open,
    block_key,
    load_blocks,
    load_symbols,
    load_xref,
    symbol_index,
)

DEFAULT_MC7DIS = [
    Path(os.environ.get("MC7DIS", "")) if os.environ.get("MC7DIS") else Path("/nonexistent"),
    Path("mc7dis"),
    Path("rz-libmc7/mc7dis"),
]

LINE = re.compile(r"^([0-9a-f]{4,}):\s+(.*)$")
BIT_OP = re.compile(r"\b([IQM])\s(\d+)\.([0-7])\b")
DB_OP = re.compile(r"\b(?:OPN\s+)?(DB|DI)\s+(\d+)\b")
BLK_OP = re.compile(r"\b(UC|CC|CALL)\s+(FB|FC|SFB|SFC)\s+(\d+)\b")
DBX_OP = re.compile(r"\b(DBX|DBB|DBW|DBD|DIX|DIB|DIW|DID)\s+(\d+)\.?(\d*)")
TEMP_OP = re.compile(r"\b([LTS])\s(\d+)\.(\d)\b")


def find_mc7dis(explicit: str = "") -> Path | None:
    if explicit:
        p = Path(explicit)
        return p if p.exists() else None
    for p in DEFAULT_MC7DIS:
        if p.exists():
            return p
    return None


def disassemble(mc7dis: Path, blob: Path) -> list[tuple[int, str]]:
    res = subprocess.run([str(mc7dis), str(blob)], capture_output=True, text=True, timeout=120)
    if res.returncode != 0:
        raise SystemExit(f"mc7dis failed on {blob}: {res.stderr.strip()[:300]}")
    out = []
    for raw in res.stdout.splitlines():
        m = LINE.match(raw.strip())
        if m:
            out.append((int(m.group(1), 16), m.group(2).strip()))
    return out


def annotate(text: str, sym_idx: dict, sym_by_block: dict, cur_db: int) -> tuple[str, int]:
    """Return (annotated_text, current_db) for one decoded instruction."""
    notes: list[str] = []
    m = DB_OP.search(text)
    if m and text.upper().startswith(("OPN",)):
        cur_db = int(m.group(2))
        s = sym_by_block.get(("DB", cur_db))
        if s:
            notes.append(f"{s['name']}" + (f" — {s['comment']}" if s["comment"] else ""))
    for mm in BIT_OP.finditer(text):
        area, byte, bit = mm.group(1), int(mm.group(2)), int(mm.group(3))
        s = sym_idx.get(area, {}).get((byte, bit))
        if s:
            note = s["name"] + (f" — {s['comment']}" if s["comment"] else "")
            if note not in notes:
                notes.append(note)
    blk = BLK_OP.search(text)
    if blk:
        s = sym_by_block.get((blk.group(2)[-2:], int(blk.group(3))))
        if s:
            notes.append(s["name"] + (f" — {s['comment']}" if s["comment"] else ""))
    if notes:
        text = f"{text:<34} ; {' | '.join(notes)}"
    return text, cur_db


def render(block: dict, surf: dict, decoded: list[tuple[int, str]], symbols: list[dict],
           sym_idx: dict, sym_by_block: dict, project: Path) -> str:
    code = surf["code"]
    head = [
        f"// {block['label']} — {block['symbol'] or '(no symbol)'}",
        f"// stored title : {surf['title'] or '—'}",
        f"// section titles: {' | '.join(surf['titles']) if surf['titles'] else '—'}",
        f"// references    : {', '.join(surf['references']) or '—'}",
        f"// source        : {project} [{block['folder']}]",
        f"// code payload  : {len(code)} bytes, sha256 {hashlib.sha256(code).hexdigest()}",
        "// decoded       : MC7 -> AWL by rizinorg/rz-libmc7; symbol names from the project",
        "//                 symbol table (SYMLIST.DBF). Read-only reconstruction, not a",
        "//                 Siemens-exported listing: verify against SIMATIC Manager",
        "//                 before using it for maintenance decisions.",
        "",
    ]
    body = []
    cur_db = 0
    for off, text in decoded:
        annotated, cur_db = annotate(text, sym_idx, sym_by_block, cur_db)
        body.append(f"      {annotated}")
    return "\n".join(head + body) + "\n"


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Decode STEP 7 MC7 payloads into annotated AWL")
    ap.add_argument("project", type=Path)
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--folder", default="", help="ombstx folder regex (see s7_project.py)")
    ap.add_argument("--block", default="", help="comma-separated labels, e.g. FC67,FC82")
    ap.add_argument("--awl-all", action="store_true", help="every FC/FB that has a code payload")
    ap.add_argument("--mc7dis", default="", help="path to the mc7dis binary")
    args = ap.parse_args(argv)

    mc7dis = find_mc7dis(args.mc7dis)
    if not mc7dis:
        raise SystemExit(
            "mc7dis not found. Build it first:\n"
            "  cd rz-libmc7 && "
            "cc -O2 -I include -I src mc7dis.c src/simatic.c -o mc7dis\n"
            "(see references/local-tools.md)"
        )

    out = args.out
    awl_dir = out / "awl"
    awl_dir.mkdir(parents=True, exist_ok=True)

    with _open(args.project) as source:
        blocks = load_blocks(source, args.folder)
        root = ""
        if blocks:
            f = blocks[0]["folder"]
            root = f.split("/ombstx")[0] if "/ombstx" in f else ""
        symbols = load_symbols(source, root)
        sym_idx = symbol_index(symbols)
        sym_by_block = {}
        for s in symbols:
            m = re.match(r"\s*([A-Z]+)\s+0*(\d+)\s*$", s["operand"])
            if m:
                sym_by_block.setdefault((m.group(1), int(m.group(2))), s)
        for b in blocks:
            s = sym_by_block.get((b["type"], b["number"]))
            b["symbol"] = s["name"] if s else ""
            b["comment"] = s["comment"] if s else ""
        from .s7_project import surface as surface_fn

        wanted: list[dict] = []
        if args.awl_all:
            wanted = [b for b in blocks if b["type"] in ("FC", "FB")]
        elif args.block:
            for label in re.split(r"[,\s]+", args.block):
                if not label:
                    continue
                wtype, wnum = block_key(label)
                blk = next((b for b in blocks
                            if b["type"] == wtype and b["number"] == wnum), None)
                if blk:
                    wanted.append(blk)
                else:
                    print(f"{label}: not in catalog")
        else:
            raise SystemExit("give --block LABEL or --awl-all")

        made = 0
        skipped = 0
        for blk in wanted:
            surf = surface_fn(source, blk)
            if not surf["code"]:
                skipped += 1
                continue
            tmp = out / f"{blk['label']}.mc5"
            tmp.write_bytes(surf["code"])
            decoded = disassemble(mc7dis, tmp)
            text = render(blk, surf, decoded, symbols, sym_idx, sym_by_block, args.project)
            (awl_dir / f"{blk['label']}.awl").write_text(text, encoding="utf-8")
            made += 1
            if args.block:
                print(f"\n===== {blk['label']}.awl ({len(decoded)} statements) =====")
                print(text)

    print(f"awl     : {made} file(s) in {awl_dir.resolve()}"
          + (f", {skipped} block(s) without a code payload skipped" if skipped else ""))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
