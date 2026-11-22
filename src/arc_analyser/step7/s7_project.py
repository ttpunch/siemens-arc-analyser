"""Read-only STEP 7 Classic (V5.x) project inventory: blocks, symbols, xref, MC5, report.

Usage
-----
    python s7_project.py <project.zip|project-dir> [--out OUTDIR]
                         [--folder SUBSTR] [--block FC67] [--report FC67,FC82]
                         [--report-all] [--blobs]

What it produces (read-only; the source is never modified):

* console summary       — block counts by type, per project folder (avoids double
                          counting archives that pack two copies of a project)
* ``blocks.csv``        — type, number, symbol, comment, language, part lengths,
                          MC5 length, memo index, timestamp
* ``symbols.csv``       — symbol table (name, operand, datatype, comment)
* ``xref.csv``          — cross-reference rows (block -> operand usage)
* ``callgraph.csv``     — block references parsed from the stored reference lists
* ``blocks/<LABEL>.md`` — per-block report: identity, stored titles, referenced
                          blocks, callers, operand usage, MC5 code hash + hexdump
* ``--blobs``           — byte-exact ``<LABEL>.mc5`` code payloads

Ground truth is the project's own tables and memo fields. The MC5 payload is the
compiled machine code of the block; this tool does **not** decompile MC5/MC7 into
AWL. It gives you every decidable fact (titles, references, symbols, cross
references, byte-exact code) and states plainly where decompilation is required.
"""

from __future__ import annotations

import argparse
import collections
import csv
import hashlib
import json
import re
import sys
import zipfile
from pathlib import Path

from .s7_dbf import (  # noqa: E402
    BAUSTEIN_TYP,
    BLKLANG,
    OPTYPE_NOTE,
    clean,
    dbt_members,
    memo_payload,
    read_dbf,
    read_dbt,
    text_runs,
)

BLOCK_REF = re.compile(r"\b(FC|FB|DB|OB|SDB|VAT|UDT)\s?(\d{1,4})\b")

# OPTYPE mapping in XR*.DBF, derived from a sample project and cross-checked:
#   * op 5  -> always DBNB>0, and the DBNB set equals the block's own reference
#              list (DB2, DB10, DB21, DB33, DB165, DB170, DB172 for FC67) => DB access
#   * op 12 -> DBNB equals the referenced FC number (103 => FC103)             => FC call
#   * op 13 -> DBNB equals the referenced FB number (99 => FB99)               => FB call
#   * op 2  -> 253/302 uniquely-resolved rows land on I symbols               => input
#   * op 3  -> 151/165 uniquely-resolved rows land on Q symbols               => output
#   * op 4  -> 425/582 uniquely-resolved rows land on M symbols               => flag
#   * op 8/9/14 share OPACCESS='5' or '0' and cannot be resolved from the
#              symbol table alone; reported verbatim as timer/counter/call class.
OPTYPE_AREA = {2: "I", 3: "Q", 4: "M", 5: "DB"}
OPTYPE_CALL = {12: "FC", 13: "FB", 14: "CALL?"}
OPTYPE_LABEL = {
    2: "input", 3: "output", 4: "flag", 5: "data block",
    7: "unknown(7)", 8: "timer/counter?", 9: "timer/counter?",
    12: "FC call", 13: "FB call", 14: "call class(14)",
}

# SUBBLKTYP part codes observed in real projects. Only codes confirmed by payload
# content are named; anything else is reported raw.
PART_KIND = {
    "00019": "title/comment block",
    "00005": "referenced-library/parameter names",
    "00065": "reference list",
    "00012": "code part",
}


def _find(source, pattern: str) -> list[str]:
    if isinstance(source, zipfile.ZipFile):
        names = source.namelist()
    else:
        names = [p.relative_to(source).as_posix() for p in Path(source).rglob("*") if p.is_file()]
    rx = re.compile(pattern, re.I)
    return sorted((n for n in names if rx.search(n)), key=lambda n: (n.count("/"), n))


def _open(source_path: Path):
    if source_path.is_dir():
        return source_path
    return zipfile.ZipFile(source_path)


def load_blocks(source, folder_filter: str = "") -> list[dict]:
    """Join BAUSTEIN.DBF (block catalog) with SUBBLK.DBF (per-part records)."""
    catalogs = _find(source, r"ombstx/offline/\d+/BAUSTEIN\.DBF$")
    if not catalogs:
        raise SystemExit("no ombstx/offline/<n>/BAUSTEIN.DBF found — not a STEP 7 V5 project?")
    if folder_filter:
        catalogs = [c for c in catalogs if re.search(folder_filter, c.rsplit("/", 1)[0], re.I)]
        if not catalogs:
            raise SystemExit(f"no ombstx folder matched --folder {folder_filter!r}")
    elif len(catalogs) > 1:
        # archives often pack two copies of the same project; take the richest one
        catalogs.sort(key=lambda c: len(read_dbf(source, c).rows), reverse=True)
        skipped = catalogs[1:]
        catalogs = catalogs[:1]
        for s in skipped:
            print(f"note    : also present, skipped: {s.rsplit('/', 1)[0]} "
                  f"(use --folder to select it)")
    blocks: list[dict] = []
    for cat in catalogs:
        folder = cat.rsplit("/", 1)[0]
        sub_path = next(iter(_find(source, re.escape(folder) + r"/SUBBLK\.DBF$")), "")
        catalog = read_dbf(source, cat)
        parts: dict[str, list[dict]] = collections.defaultdict(list)
        if sub_path:
            for row in read_dbf(source, sub_path).rows:
                parts[clean(row.get("OBJECTID", ""))].append(row)
        for row in catalog.rows:
            oid = clean(row.get("ID", ""))
            typ_code = int(clean(row.get("TYP", "0")) or 0)
            number = int(clean(row.get("NUMMER", "0")) or 0)
            recs = parts.get(oid, [])
            btype = BAUSTEIN_TYP.get(typ_code, f"TYP{typ_code}")
            lang = ""
            memo_idx = 0
            part_rows = []
            for r in recs:
                ptype = clean(r.get("SUBBLKTYP", ""))
                part_rows.append(
                    {
                        "kind": PART_KIND.get(ptype, f"part {ptype}"),
                        "code": ptype,
                        "mc5_len": int(clean(r.get("MC5LEN", "0")) or 0),
                        "mc5_idx": int(clean(r.get("MC5CODE", "0")) or 0),
                        "ssb_len": int(clean(r.get("SSBLEN", "0")) or 0),
                        "ssb_idx": int(clean(r.get("SSBPART", "0")) or 0),
                        "add_len": int(clean(r.get("ADDLEN", "0")) or 0),
                        "add_idx": int(clean(r.get("ADDINFO", "0")) or 0),
                        "total_len": int(clean(r.get("BLKTOTLEN", "0")) or 0),
                    }
                )
                if int(clean(r.get("MC5LEN", "0")) or 0) > 0:
                    memo_idx = int(clean(r.get("MC5CODE", "0")) or 0)
                    lang = clean(r.get("BLKLANG", ""))
            blocks.append(
                {
                    "folder": folder,
                    "objectid": oid,
                    "type": btype,
                    "typ_code": typ_code,
                    "number": number,
                    "label": f"{btype}{number}",
                    "language": BLKLANG.get(int(lang or 0), lang),
                    "parts": len(recs),
                    "part_rows": part_rows,
                    "mc5_len": next(
                        (p["mc5_len"] for p in part_rows if p["kind"] == "code part"), 0
                    ) or max((p["mc5_len"] for p in part_rows), default=0),
                    "ssb_len": max((p["ssb_len"] for p in part_rows), default=0),
                    "add_len": max((p["add_len"] for p in part_rows), default=0),
                    "total_len": sum(p["total_len"] for p in part_rows),
                    "memo_index": memo_idx,
                    "subblk_dbt": dbt_members(source, sub_path) if sub_path else "",
                }
            )
    return blocks


def load_symbols(source, root: str = "") -> list[dict]:
    tables = _find(source, r"YDBs/\d+/SYMLIST\.DBF$") or _find(source, r"SYMLIST\.DBF$")
    if root:
        tables = [t for t in tables if t.rsplit("/YDBs", 1)[0] == root] or tables
    symbols: list[dict] = []
    seen: set[tuple[str, str]] = set()
    for t in tables:
        for row in read_dbf(source, t).rows:
            name = clean(row.get("_SKZ", ""))
            operand = clean(row.get("_OPIEC", ""))
            if not name and not operand:
                continue
            key = (name, operand)
            if key in seen:
                continue
            seen.add(key)
            symbols.append(
                {
                    "table": t,
                    "name": name,
                    "operand": operand,
                    "datatype": clean(row.get("_DATATYP", "")),
                    "comment": clean(row.get("_COMMENT", "")),
                }
            )
    return symbols


def load_xref(source, root: str = "") -> tuple[list[dict], list[str]]:
    tables = _find(source, r"XUTILS/listen/XR\d+\.DBF$") or _find(source, r"XR\d+\.DBF$")
    if root:
        tables = [t for t in tables if t.rsplit("/XUTILS", 1)[0] == root] or tables
    rows: list[dict] = []
    for t in tables:
        for row in read_dbf(source, t).rows:
            rows.append(
                {
                    "table": t,
                    "block_type": int(clean(row.get("BLOCKTYPE", "0")) or 0),
                    "block_number": int(clean(row.get("BLOCKNB", "0")) or 0),
                    "op_type": int(clean(row.get("OPTYPE", "0")) or 0),
                    "op_access": clean(row.get("OPACCESS", "")),
                    "byte_addr": int(clean(row.get("BYTEADR", "0")) or 0),
                    "bit_addr": int(clean(row.get("BITADR", "0")) or 0),
                    "db_number": int(clean(row.get("DBNB", "0")) or 0),
                    "access": int(clean(row.get("ACCESS", "0")) or 0),
                    "language": int(clean(row.get("LANGUAGE", "0")) or 0),
                }
            )
    return rows, tables


def surface(source, block: dict) -> dict:
    """Extract the stored, human-readable surface of one block."""
    out = {"title": "", "titles": [], "references": [], "params": [], "code": b""}
    if not block.get("subblk_dbt"):
        return out
    dbt = read_dbt(source, block["subblk_dbt"])
    for p in block["part_rows"]:
        if p["kind"] == "title/comment block":
            ssb = memo_payload(dbt, p["ssb_idx"]) if p["ssb_idx"] else b""
            runs = text_runs(ssb)
            if runs:
                out["title"] = runs[0]
            # section titles live in the code field of this part
            for idx in (p["mc5_idx"], p["add_idx"]):
                if idx:
                    out["titles"] += text_runs(memo_payload(dbt, idx))
        elif p["kind"] == "reference list" and p["add_idx"]:
            payload = memo_payload(dbt, p["add_idx"]).decode("latin1")
            refs = []
            for m in BLOCK_REF.finditer(payload):
                label = f"{m.group(1)}{int(m.group(2))}"
                if label not in refs:
                    refs.append(label)
            out["references"] = refs
        elif p["kind"] == "referenced-library/parameter names" and p["add_idx"]:
            names = []
            for n in text_runs(memo_payload(dbt, p["add_idx"])):
                if n not in names:
                    names.append(n)
            out["params"] = names
        if p["kind"] == "code part" and p["mc5_idx"]:
            out["code"] = memo_payload(dbt, p["mc5_idx"])[: p["mc5_len"]]
    if not out["code"] and block["memo_index"]:
        out["code"] = memo_payload(dbt, block["memo_index"])[: block["mc5_len"]]
    # de-duplicate section titles, keep stored order
    seen: set[str] = set()
    out["titles"] = [t for t in out["titles"] if not (t in seen or seen.add(t))]
    return out


def write_csv(path: Path, rows: list[dict], fields: list[str]) -> None:
    with path.open("w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=fields, extrasaction="ignore")
        w.writeheader()
        for r in rows:
            w.writerow(r)


def block_key(label: str) -> tuple[str, int]:
    m = re.fullmatch(r"(FC|FB|OB|DB|SDB|SFC|VAT|UDT)\s*0*(\d+)", label.strip(), re.I)
    if not m:
        raise SystemExit(f"cannot parse block label {label!r}; expected e.g. FC67 or FC 67")
    return m.group(1).upper(), int(m.group(2))


BIT_OPERAND = re.compile(r"^(I|Q|M)\s+(\d+)\.([0-7])$")


def symbol_index(symbols: list[dict]) -> dict[str, dict[tuple[int, int], dict]]:
    """(byte, bit) -> symbol, per bit-addressable area."""
    idx: dict[str, dict[tuple[int, int], dict]] = {"I": {}, "Q": {}, "M": {}}
    for s in symbols:
        m = BIT_OPERAND.match(s["operand"])
        if m:
            idx[m.group(1)][(int(m.group(2)), int(m.group(3)))] = s
    return idx


def footprint(used: list[dict], sym_idx: dict, sym_by_block: dict) -> list[dict]:
    """Resolve cross-reference rows into a named operand footprint for one block."""
    agg: dict[tuple[str, str], dict] = {}
    for r in used:
        op = r["op_type"]
        area = OPTYPE_AREA.get(op)
        symbol = ""
        comment = ""
        if area in ("I", "Q", "M"):
            operand = f"{area} {r['byte_addr']}.{r['bit_addr']}"
            s = sym_idx[area].get((r["byte_addr"], r["bit_addr"]))
            if s:
                symbol, comment = s["name"], s["comment"]
        elif area == "DB":
            operand = f"DB{r['db_number']}.DBX{r['byte_addr']}.{r['bit_addr']}"
        elif op in OPTYPE_CALL:
            prefix = OPTYPE_CALL[op]
            operand = f"{prefix}{r['db_number']}" if prefix in ("FC", "FB") else f"call#{r['db_number']}"
            s = sym_by_block.get((prefix, r["db_number"]))
            if s:
                symbol, comment = s["name"], s["comment"]
        else:
            operand = f"op{op}:{r['byte_addr']}.{r['bit_addr']}"
        key = (OPTYPE_LABEL.get(op, f"op{op}"), operand)
        row = agg.setdefault(key, {"kind": OPTYPE_LABEL.get(op, f"op{op}"), "operand": operand,
                                   "symbol": symbol, "comment": comment, "count": 0,
                                   "access": set()})
        row["count"] += 1
        row["access"].add(str(r["access"]))
    out = []
    for row in agg.values():
        row["access"] = ",".join(sorted(row["access"]))
        out.append(row)
    order = {"input": 0, "output": 1, "flag": 2, "data block": 3, "FC call": 4, "FB call": 5}
    return sorted(out, key=lambda x: (order.get(x["kind"], 9), x["operand"]))


def render_report(block: dict, surf: dict, callers: list[str], used: list[dict],
                  foot: list[dict] | None = None, hex_bytes: int = 96) -> str:
    b = block
    lines = [f"# {b['label']} — {b['symbol'] or '(no symbol)'}", ""]
    lines += [
        "| field | value |",
        "| --- | --- |",
        f"| type | {b['type']} |",
        f"| number | {b['number']} |",
        f"| symbolic name | {b['symbol'] or '—'} |",
        f"| symbol comment | {b['comment'] or '—'} |",
        f"| stored title | {surf['title'] or '—'} |",
        f"| language | {b['language'] or '—'} |",
        f"| parts | {b['parts']} |",
        f"| MC5 code length | {b['mc5_len']} bytes |",
        f"| secondary parts | ssb {b['ssb_len']} B, add {b['add_len']} B |",
        f"| block total | {b['total_len']} bytes |",
        f"| project folder | `{b['folder']}` |",
        "",
    ]
    if surf["titles"]:
        lines += ["## Stored section / network titles (in project order)", ""]
        lines += [f"{i}. {t}" for i, t in enumerate(surf["titles"], 1)]
        lines += [""]
    if surf["references"]:
        lines += ["## Blocks referenced by this block (from its own reference list)", ""]
        lines += [f"- `{r}`" for r in surf["references"]]
        lines += [""]
    if surf["params"]:
        lines += ["## Library / parameter names stored with this block", ""]
        lines += ["- " + ", ".join(surf["params"][:40])]
        lines += [""]
    if callers:
        lines += ["## Called from", ""]
        lines += [f"- `{c}`" for c in callers]
        lines += [""]
    if used:
        hist = collections.Counter((r["op_type"], r["db_number"] > 0) for r in used)
        dbs = sorted({r["db_number"] for r in used
                      if r["db_number"] and r["op_type"] == 5})
        lines += ["## Operand footprint (cross-reference rows, resolved)", ""]
        lines += [f"- cross-reference rows for this block: {len(used)}"]
        lines += [f"- (OPTYPE, uses_DB) histogram: {sorted(hist.items())}"]
        if dbs:
            lines += [f"- data blocks touched: {', '.join('DB' + str(d) for d in dbs)}"]
        lines += [""]
        if foot:
            groups = collections.defaultdict(list)
            for f in foot:
                groups[f["kind"]].append(f)
            for kind in ("input", "output", "flag", "data block", "FC call", "FB call"):
                if kind not in groups:
                    continue
                lines += [f"### {kind}s ({len(groups[kind])})", "",
                          "| operand | symbol | comment | refs | access |",
                          "| --- | --- | --- | --- | --- |"]
                for f in groups[kind]:
                    lines.append(
                        f"| `{f['operand']}` | {f['symbol'] or '—'} | "
                        f"{(f['comment'] or '—')[:60]} | {f['count']} | {f['access']} |"
                    )
                lines += [""]
            other = [f for f in foot if f["kind"] not in
                     ("input", "output", "flag", "data block", "FC call", "FB call")]
            if other:
                lines += [f"- unresolved operand class rows: {len(other)} "
                          f"(OPTYPE codes reported verbatim)", ""]
    code = surf["code"]
    lines += [
        "## MC5 code payload",
        "",
        f"- length: {len(code)} bytes",
        f"- sha256: `{hashlib.sha256(code).hexdigest()}`",
        f"- first {min(hex_bytes, len(code))} bytes:",
        "",
        "```",
        code[:hex_bytes].hex(" "),
        "```",
        "",
        "## Limits of this report",
        "",
        "- Titles, references, symbols and cross references are read from the project's own tables — they are evidence, not interpretation.",
        "- The MC5 payload is byte-exact but **not** decompiled: instruction-level logic (contacts, coils, comparators, timers) needs an AWL export from SIMATIC Manager/STEP 7 Classic or an MC7 disassembler.",
        "- OPTYPE/LANGUAGE codes are STEP 7 internal enumerations, reported verbatim.",
        "",
    ]
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Read-only STEP 7 V5 project inventory")
    ap.add_argument("project", type=Path, help="project .zip or unpacked project directory")
    ap.add_argument("--out", type=Path, default=None, help="output directory")
    ap.add_argument("--folder", default="", help="only this ombstx folder (substring), e.g. project/ombstx")
    ap.add_argument("--block", default="", help="print detail for one block, e.g. FC67")
    ap.add_argument("--report", default="", help="comma-separated blocks to render as Markdown")
    ap.add_argument("--report-all", action="store_true", help="render a Markdown report for every FC/FB")
    ap.add_argument("--blobs", action="store_true", help="write raw MC5 payloads per block")
    ap.add_argument("--max-blobs", type=int, default=0, help="limit blob writes (0 = all)")
    ap.add_argument("--hex-bytes", type=int, default=96, help="hex bytes in reports")
    args = ap.parse_args(argv)

    src_path = args.project
    if not src_path.exists():
        raise SystemExit(f"not found: {src_path}")
    out = args.out or Path("s7_inventory_out")
    out.mkdir(parents=True, exist_ok=True)
    reports_dir = out / "blocks"

    with _open(src_path) as source:
        blocks = load_blocks(source, args.folder)
        root = ""
        if blocks:
            f = blocks[0]["folder"]
            root = f.split("/ombstx")[0] if "/ombstx" in f else ""
        symbols = load_symbols(source, root)
        xref, xref_tables = load_xref(source, root)

        by_operand = {}
        for s in symbols:
            m = re.match(r"\s*([A-Z]+)\s+0*(\d+)\s*$", s["operand"])
            if m and m.group(1) in ("FC", "FB", "OB", "DB", "SDB", "VAT", "UDT"):
                by_operand.setdefault((m.group(1), int(m.group(2))), s)
        for b in blocks:
            s = by_operand.get((b["type"], b["number"]))
            b["symbol"] = s["name"] if s else ""
            b["comment"] = s["comment"] if s else ""

        # per-folder summary + duplicate detection by code hash
        per_folder = collections.defaultdict(collections.Counter)
        for b in blocks:
            per_folder[b["folder"]][b["type"]] += 1
        print(f"project : {src_path}")
        for folder, cnt in sorted(per_folder.items()):
            total = sum(cnt.values())
            print(f"folder  : {folder}  ({total} blocks)  " + "  ".join(f"{k}={v}" for k, v in sorted(cnt.items())))
        if len(per_folder) > 1:
            print("note    : more than one ombstx copy present (archives often pack two); use --folder to isolate one")
        print(f"symbols : {len(symbols)}   xref rows: {len(xref)}  tables: {', '.join(xref_tables) or 'none'}")

        # block surface (titles, references, code)
        for b in blocks:
            b["surface"] = surface(source, b)

        callgraph = []
        for b in blocks:
            for ref in b["surface"]["references"]:
                callgraph.append({"source": b["label"], "target": ref,
                                  "kind": "reference", "folder": b["folder"]})
        callers_of = collections.defaultdict(list)
        for e in callgraph:
            if e["source"] != e["target"]:
                callers_of[e["target"]].append(e["source"])

        rows = []
        for b in sorted(blocks, key=lambda x: (x["type"], x["number"])):
            r = {k: v for k, v in b.items() if k != "part_rows" and k != "surface"}
            r["surface_title"] = b["surface"]["title"]
            r["titles"] = " | ".join(b["surface"]["titles"])
            r["references"] = ";".join(b["surface"]["references"])
            rows.append(r)
        write_csv(out / "blocks.csv", rows,
                  ["type", "number", "label", "symbol", "comment", "language", "parts",
                   "mc5_len", "ssb_len", "add_len", "total_len", "memo_index",
                   "surface_title", "titles", "references", "objectid", "folder"])
        write_csv(out / "symbols.csv", symbols,
                  ["name", "operand", "datatype", "comment", "table"])
        write_csv(out / "xref.csv", xref,
                  ["block_type", "block_number", "op_type", "op_access", "byte_addr",
                   "bit_addr", "db_number", "access", "language", "table"])
        write_csv(out / "callgraph.csv", callgraph, ["source", "target", "kind", "folder"])

        if args.blobs:
            made = 0
            for b in sorted(blocks, key=lambda x: (x["type"], x["number"])):
                code = b["surface"]["code"]
                if not code:
                    continue
                (out / f"{b['label']}.mc5").write_bytes(code)
                made += 1
                if args.max_blobs and made >= args.max_blobs:
                    break
            print(f"blobs   : wrote {made} MC5 payload(s) to {out}")

        wants = []
        if args.block:
            wants.append(args.block)
        if args.report:
            wants += [w for w in re.split(r"[,\s]+", args.report) if w]
        if args.report_all:
            wants += [b["label"] for b in blocks if b["type"] in ("FC", "FB")]

        if wants:
            reports_dir.mkdir(exist_ok=True)
            sym_idx = symbol_index(symbols)
            sym_by_block = {}
            for s in symbols:
                m = re.match(r"\s*([A-Z]+)\s+0*(\d+)\s*$", s["operand"])
                if m:
                    sym_by_block.setdefault((m.group(1), int(m.group(2))), s)
            for want in wants:
                wtype, wnum = block_key(want)
                blk = next((b for b in blocks
                            if b["type"] == wtype and b["number"] == wnum), None)
                if not blk:
                    print(f"\nblock {want}: not present in the catalog")
                    continue
                usable = [r for r in xref
                          if r["block_number"] == wnum and r["block_type"] == blk["typ_code"]]
                callers = sorted(set(callers_of.get(blk["label"], [])))
                foot = footprint(usable, sym_idx, sym_by_block)
                md = render_report(blk, blk["surface"], callers, usable, foot, args.hex_bytes)
                (reports_dir / f"{blk['label']}.md").write_text(md, encoding="utf-8")
                if args.block and want == args.block:
                    print("\n" + md)
            print(f"reports : {reports_dir}")

    print(f"\nartifacts: {out.resolve()}")
    print(OPTYPE_NOTE)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
