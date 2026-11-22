"""Synthetic STEP 7 project fixtures (DBF/DBT writers). No machine data involved."""
from __future__ import annotations

import struct
import zipfile
from pathlib import Path


def build_dbf(fields, rows, deleted=()):
    """Minimal dBase III table writer: ``fields`` = [(name, type, length), ...]."""
    header_len = 32 + 32 * len(fields) + 1
    record_len = 1 + sum(f[2] for f in fields)
    out = bytearray(32)
    out[0] = 0x03
    out[4:8] = struct.pack("<I", len(rows))
    out[8:10] = struct.pack("<H", header_len)
    out[10:12] = struct.pack("<H", record_len)
    for name, ftype, length in fields:
        fd = bytearray(32)
        fd[0:len(name)] = name.encode("latin1")
        fd[11] = ord(ftype)
        fd[16] = length
        out += fd
    out += b"\x0d"
    for i, row in enumerate(rows):
        out += b"*" if i in deleted else b" "
        for name, ftype, length in fields:
            val = str(row.get(name, "")).encode("latin1")
            out += val.ljust(length, b" ")[:length]
    out += b"\x1a"
    return bytes(out)


def build_dbt(entries):
    """Build a .DBT where ``entries`` maps memo index -> payload, STEP 7 wrapped."""
    size = (max(entries) + 1) * 512 if entries else 512
    buf = bytearray(size)
    for index, payload in entries.items():
        off = index * 512
        buf[off:off + 8] = b"\xff\xff" + struct.pack("<H", 8) + struct.pack("<I", len(payload))
        buf[off + 8:off + 8 + len(payload)] = payload
    return bytes(buf)


CODE = b"\x80\x0c\xc1\x28"
TITLES = b"\x00HYDROSTATICS OF STEADY REST 1\x00QUILL UP /DOWN\x00"
BLOCK_TITLE = b"\x00HYDROSTATIC SR 1"
REFS = b"DB2,;DB10,;FC103,;FB99,"

BAUSTEIN_FIELDS = [("ID", "N", 11), ("TYP", "C", 5), ("NUMMER", "C", 5), ("LINKS", "N", 11)]
SUBBLK_FIELDS = [
    ("OBJECTID", "N", 11), ("BLKLANG", "C", 5), ("SUBBLKTYP", "C", 5), ("BLKNUMBER", "C", 5),
    ("BLKTOTLEN", "N", 11), ("MC5LEN", "N", 11), ("SSBLEN", "N", 11), ("ADDLEN", "N", 11),
    ("TIMESTAMP1", "C", 6), ("TIMESTAMP2", "C", 6), ("BLOCKNAME", "C", 8),
    ("MC5CODE", "M", 10), ("SSBPART", "M", 10), ("ADDINFO", "M", 10),
]
SYMLIST_FIELDS = [("_SKZ", "C", 24), ("_OPIEC", "C", 12), ("_DATATYP", "C", 10), ("_COMMENT", "C", 80)]
XR_FIELDS = [
    ("BLOCKTYPE", "C", 2), ("BLOCKNB", "C", 5), ("OPTYPE", "C", 2), ("OPACCESS", "C", 2),
    ("BYTEADR", "C", 5), ("BITADR", "C", 1), ("DBNB", "C", 5), ("ACCESS", "N", 1),
    ("LANGUAGE", "N", 2),
]


def project_members(root: str = "proj") -> dict[str, bytes]:
    """A minimal but structurally faithful STEP 7 V5 project as {member: bytes}."""
    base = f"{root}/ombstx/offline/00000001"
    parts = [
        {"OBJECTID": 1, "BLKLANG": "00001", "SUBBLKTYP": "00019", "BLKNUMBER": 67,
         "BLKTOTLEN": 60, "MC5LEN": len(TITLES), "SSBLEN": len(BLOCK_TITLE),
         "ADDLEN": 0, "MC5CODE": 1, "SSBPART": 2, "ADDINFO": 0},
        {"OBJECTID": 1, "BLKLANG": "00001", "SUBBLKTYP": "00065", "BLKNUMBER": 67,
         "BLKTOTLEN": 40, "MC5LEN": 0, "SSBLEN": 0, "ADDLEN": len(REFS),
         "MC5CODE": 0, "SSBPART": 0, "ADDINFO": 3},
        {"OBJECTID": 1, "BLKLANG": "00001", "SUBBLKTYP": "00012", "BLKNUMBER": 67,
         "BLKTOTLEN": 20, "MC5LEN": len(CODE), "SSBLEN": 0, "ADDLEN": 0,
         "MC5CODE": 4, "SSBPART": 0, "ADDINFO": 0},
    ]
    symbols = [
        {"_SKZ": "S.R. 1 - HYDROSTATIC", "_OPIEC": "FC     67", "_DATATYP": "FC     67",
         "_COMMENT": "steady rest hydraulics"},
        {"_SKZ": "60Q1", "_OPIEC": "I      36.6", "_DATATYP": "BOOL", "_COMMENT": "T.S. HYDROSTATIC"},
        {"_SKZ": "60K1", "_OPIEC": "Q      33.0", "_DATATYP": "BOOL", "_COMMENT": "HYDROSTATIC PUMP"},
    ]
    xref = [
        {"BLOCKTYPE": 12, "BLOCKNB": 67, "OPTYPE": 2, "OPACCESS": 1, "BYTEADR": 36,
         "BITADR": 6, "DBNB": 0, "ACCESS": 1, "LANGUAGE": 1},
        {"BLOCKTYPE": 12, "BLOCKNB": 67, "OPTYPE": 3, "OPACCESS": 1, "BYTEADR": 33,
         "BITADR": 0, "DBNB": 0, "ACCESS": 2, "LANGUAGE": 1},
        {"BLOCKTYPE": 12, "BLOCKNB": 67, "OPTYPE": 5, "OPACCESS": 1, "BYTEADR": 205,
         "BITADR": 4, "DBNB": 2, "ACCESS": 1, "LANGUAGE": 1},
        {"BLOCKTYPE": 12, "BLOCKNB": 67, "OPTYPE": 12, "OPACCESS": 5, "BYTEADR": 103,
         "BITADR": 0, "DBNB": 103, "ACCESS": 1, "LANGUAGE": 1},
    ]
    return {
        f"{base}/BAUSTEIN.DBF": build_dbf(BAUSTEIN_FIELDS, [{"ID": 1, "TYP": 12, "NUMMER": 67}]),
        f"{base}/SUBBLK.DBF": build_dbf(SUBBLK_FIELDS, parts),
        f"{base}/SUBBLK.DBT": build_dbt({1: TITLES, 2: BLOCK_TITLE, 3: REFS, 4: CODE}),
        f"{root}/YDBs/4483/SYMLIST.DBF": build_dbf(SYMLIST_FIELDS, symbols),
        f"{root}/XUTILS/listen/XR000001.DBF": build_dbf(XR_FIELDS, xref),
    }


def write_project_zip(path: Path, root: str = "proj") -> Path:
    with zipfile.ZipFile(path, "w", zipfile.ZIP_DEFLATED) as z:
        for name, data in project_members(root).items():
            z.writestr(name, data)
    return path
