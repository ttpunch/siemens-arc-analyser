"""Read-only readers for Siemens STEP 7 Classic (V5.x) project databases.

Design distilled from open-source STEP 7 tooling:

* dotnetprojects/DotNetSiemensPLCToolBoxLibrary
  (``LibNoDaveConnectionLibrary/DataTypes/Projectfolders/Step7V5/BlocksOfflineFolder.cs``)
  — the offline block catalog lives in ``ombstx/offline/<n>/BAUSTEIN.DBF`` and the
  per-network / per-block-part records in ``SUBBLK.DBF``; the block body is a memo
  field (``MC5CODE``) inside ``SUBBLK.DBT``. Both are plain dBase tables.
* enlyze/S7-Project-Explorer — symbol/DB variable flattening and CSV export shape.
* fleibede/Stp7Toolbox — a block envelope is (header + code + secondary parts +
  local data); lengths come from the table, never from guessing at the bytes.

Nothing here writes, converts in place, or talks to a controller. Every reader
takes an already-opened ``zipfile.ZipFile`` or a directory root.
"""

from __future__ import annotations

import struct
import zipfile
from dataclasses import dataclass, field
from pathlib import Path

import re

MEMO_TERMINATOR = b"\x1a\x1a"
DBT_BLOCK = 512


@dataclass
class DbfField:
    name: str
    type: str
    length: int
    decimals: int


@dataclass
class DbfTable:
    path: str
    version: int
    fields: list[DbfField]
    rows: list[dict] = field(default_factory=list)
    deleted: int = 0

    def column(self, name: str) -> list[str]:
        return [r.get(name, "") for r in self.rows]


def _parse_header(buf: bytes) -> tuple[int, int, int, int, list[DbfField]]:
    version = buf[0]
    nrec = struct.unpack("<I", buf[4:8])[0]
    hlen = struct.unpack("<H", buf[8:10])[0]
    rlen = struct.unpack("<H", buf[10:12])[0]
    fields: list[DbfField] = []
    pos = 32
    while pos + 32 <= len(buf) and buf[pos] != 0x0D:
        fd = buf[pos : pos + 32]
        name = fd[0:11].split(b"\x00")[0].decode("latin1")
        fields.append(
            DbfField(name, chr(fd[11]), fd[16], fd[17])
        )
        pos += 32
    return version, nrec, hlen, rlen, fields


def read_dbf(source, path: str) -> DbfTable:
    """Parse one dBase III table from a zipfile member or a file on disk."""
    if isinstance(source, zipfile.ZipFile):
        buf = source.read(path)
    else:
        buf = Path(source, path).read_bytes()
    version, nrec, hlen, rlen, fields = _parse_header(buf)
    table = DbfTable(path=path, version=version, fields=fields)
    pos = hlen
    for _ in range(nrec):
        rec = buf[pos : pos + rlen]
        pos += rlen
        if len(rec) < rlen:
            break
        if rec[:1] == b"*":
            table.deleted += 1
            continue
        row: dict[str, str] = {}
        p = 1
        for f in fields:
            row[f.name] = rec[p : p + f.length].decode("latin1")
            p += f.length
        table.rows.append(row)
    return table


def read_dbt(source, path: str) -> bytes:
    """Return the raw memo (``.DBT``) body for a table, already de-blocked."""
    if isinstance(source, zipfile.ZipFile):
        return source.read(path)
    return Path(source, path).read_bytes()


def memo_bytes(dbt: bytes, index: int) -> bytes:
    """Fetch memo entry ``index`` from a dBase III ``.DBT`` file, raw bytes.

    dBase III memo pointers are block numbers into 512-byte blocks. Siemens keeps
    that convention, so ``index * 512`` is the entry start. The entry is *not*
    0x1A1A terminated in STEP 7 projects — every STEP 7 memo entry carries an
    8-byte wrapper instead (see :func:`memo_payload`) — so the raw slice is
    returned here and callers must bound it with the documented length field.
    """
    if index <= 0:
        return b""
    start = index * DBT_BLOCK
    if start >= len(dbt):
        return b""
    end = dbt.find(MEMO_TERMINATOR, start)
    if end == -1:
        end = len(dbt)
    return dbt[start:end]


def memo_payload(dbt: bytes, index: int) -> bytes:
    """Return the byte-exact payload of a STEP 7 memo entry.

    Verified layout on a legacy STEP 7 V5 project (every part of several FC/FB blocks, and 307/307
    blocks in ``--blobs`` mode):

        ff ff          magic
        <u16 LE>       header size (always 8)
        <u32 LE>       payload length N
        payload        N bytes

    The length field matches the ``MC5LEN`` / ``ADDLEN`` / ``SSBLEN`` column of
    ``SUBBLK.DBF`` for the same part, which is what makes the extraction
    verifiable rather than guessed.
    """
    if index <= 0:
        return b""
    off = index * DBT_BLOCK
    if off + 8 > len(dbt):
        return b""
    magic, hdr_len = struct.unpack("<HH", dbt[off : off + 4])
    length = struct.unpack("<I", dbt[off + 4 : off + 8])[0]
    if magic != 0xFFFF or hdr_len not in (8, 0):
        # not a wrapped entry: fall back to a terminator-bounded read
        raw = memo_bytes(dbt, index)
        return raw
    start = off + hdr_len
    return dbt[start : start + length]


PRINTABLE_RUN = re.compile(rb"[\x20-\x7e]{4,}")


def text_runs(payload: bytes, min_len: int = 4) -> list[str]:
    """ASCII runs inside a binary STEP 7 payload (titles, references, names)."""
    return [m.group().decode("latin1") for m in re.finditer(rb"[\x20-\x7e]{%d,}" % min_len, payload)]


def dbt_members(source, dbf_path: str) -> str:
    """Return the ``.DBT`` sibling path for a ``.DBF`` member (case-tolerant)."""
    base = dbf_path.rsplit(".", 1)[0]
    if isinstance(source, zipfile.ZipFile):
        candidates = source.namelist()
    else:
        candidates = [str(p) for p in Path(source).rglob("*.DBT")]
        candidates += [str(p) for p in Path(source).rglob("*.dbt")]
    lowered = {c.lower(): c for c in candidates}
    for ext in (".DBT", ".dbt"):
        hit = lowered.get((base + ext).lower())
        if hit:
            return hit
    return ""


# --- STEP 7 block/type codes ------------------------------------------------

# Derived by joining BAUSTEIN.TYP against the symbolic operands in YDBs/*/SYMLIST.DBF
# for a sample project (54/48, 18/17, 5/5, 60/12 agreement on TYP 12/14/8/10) and
# confirmed for TYP 13 by DotNetSiemensPLCToolBoxLibrary, which names those blocks
# SFC17/22/41/42/46/47/51/52/58/59/64 — matching the SFC 17 (ALARM_SQ) and
# SFC 64 (TIME_TCK) symbols in the same project's symbol table.
BAUSTEIN_TYP = {
    8: "OB",
    10: "DB",
    12: "FC",
    13: "SFC",
    14: "FB",
    27: "VAT",
    0: "UDT",
}

# BLKLANG / SUBBLKTYP are internal enums; only languages confirmed on real blocks
# are named here. Everything else is reported as its raw code.
BLKLANG = {
    1: "STL/AWL",
}

OPTYPE_NOTE = (
    "OPTYPE/LANGUAGE/LANGSPECn in XR*.DBF are STEP 7 internal enumerations. "
    "Codes are reported verbatim; only BLOCKTYPE and DB usage (DBNB>0) are confirmed."
)


def clean(text: str) -> str:
    """Trim a dBase field and drop the NUL padding Siemens leaves behind."""
    return text.replace("\x00", "").strip()
