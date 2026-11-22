# STEP 7 Classic (V5.x) project container — verified layout

Scope: read-only, offline inspection of a project **copy**. Every statement below was
verified against a legacy STEP 7 Classic project delivered as a plain ZIP and
cross-checked with a second, independent implementation
(`DotNetSiemensPLCToolBoxLibrary`). Counts quoted come from that sample project; they
illustrate the format, not a guarantee for other projects.

No proprietary decoder is bundled. Nothing here connects to a controller, writes into
a project, restores data or executes extracted content.

## 1. Container

```
project.zip
└── <project>/              *.s7p + s7asrcom/ ombstx/ sdb/ YDBs/ XUTILS/ Global/ ...
    └── <project>/          a SECOND, older copy of the same project
```

* A STEP 7 project is a directory (or a ZIP containing one). The `.s7p` file is only
  a pointer; the program lives in the sibling folders.
* Archives frequently pack **two copies** of the project. Always enumerate every
  `ombstx/offline/*/BAUSTEIN.DBF`; counting blocks across copies doubles the answer.
  The sample had four: two project copies × two S7 programs (`00000001` plus a
  nearly empty `00000002`).
* Select one with `--folder <regex>`; the reader auto-picks the richest copy and
  prints which ones it skipped.

## 2. Program folders

| Path | Content |
| --- | --- |
| `ombstx/offline/<n>/BAUSTEIN.DBF` + `.DBT` | block catalog — one row per block |
| `ombstx/offline/<n>/SUBBLK.DBF` + `.DBT` | per-block part records (header, titles, references, code) |
| `YDBs/<n>/SYMLIST.DBF` | symbol table (name, operand, datatype, comment) |
| `XUTILS/listen/XR<n>.DBF` | cross-reference list (block → operand usage) |
| `XUTILS/listen/BS<n>.DBF`, `CT<n>.DBF` | block / contact lists |
| `sdb/<n>/list/<n>.DBF` | system data blocks (hardware configuration) |
| `Global/s7lst/*.lst` | localized block title / interface / line comments (DE+EN, comment strings only) |
| `s7asrcom/`, `pvr/`, `hrs/`, `omgd/`, `pgs/` | project bookkeeping — irrelevant for logic analysis |

Tables are **dBase III** (`0x03` version byte, or `0x8b` when a memo file is
attached). Field types are C/N/M; `M` fields hold a memo index.

## 3. Memo (`.DBT`) format

dBase III memo pointers are 512-byte block numbers, so entry `i` starts at
`i * 512`. STEP 7 does **not** terminate entries with `0x1A1A`; each entry is wrapped:

```
ff ff          magic
<u16 LE>       header size = 8
<u32 LE>       payload length N
N bytes        payload
```

The declared `N` equals the `MC5LEN` / `SSBLEN` / `ADDLEN` column of the matching
`SUBBLK.DBF` row, which is what makes extraction verifiable. `N + 8` is the real
entry size. Reading to end-of-file (a common bug) returns the whole `.DBT` — in the
sample, 162,304 bytes instead of 788 for one block's code part.

## 4. `BAUSTEIN.DBF` — block catalog

Fields: `ID`, `TYP`, `NUMMER`, `ATTRIBS`, `LINKS`, `UDA`, `SUBBLOCKS`.
`ID` joins to `SUBBLK.OBJECTID`.

`TYP` is an internal code. Derived by intersecting each code's `NUMMER` set with the
symbolic operands in `SYMLIST` (FC/FB/DB prefixes), and confirmed against block names
produced by `DotNetSiemensPLCToolBoxLibrary`:

| TYP | Block | Evidence |
| --- | --- | --- |
| 8 | OB | 5 blocks = OB1, OB40, OB82, OB86, OB100 |
| 10 | DB | 60 blocks |
| 12 | FC | 54 blocks, 48 numbers also exist as `FC n` symbols |
| 13 | SFC | 11 blocks = SFC17/22/41/42/46/47/51/52/58/59/64, matching `SFC 17`/`SFC 64` symbols in SYMLIST |
| 14 | FB | 18 blocks, 17 numbers also exist as `FB n` symbols |
| 27 | VAT | 3 blocks = the 3 `VAT` symbols |
| 0 | UDT | 11 blocks |

Sample totals: **162 blocks — 54 FC, 18 FB, 5 OB, 60 DB, 11 SFC, 11 UDT, 3 VAT.**
`DotNetSiemensPLCToolBoxLibrary` loads the same project and reports the identical 162
blocks under the identical type names — an independent confirmation of this table.

## 5. `SUBBLK.DBF` — per-block parts

Fields of interest: `OBJECTID`, `BLKLANG`, `SUBBLKTYP`, `BLKNUMBER`, `BLKTOTLEN`,
`MC5LEN`, `SSBLEN`, `ADDLEN`, `MC5CODE`, `SSBPART`, `ADDINFO`, `TIMESTAMP1/2`,
`BLOCKNAME`, `VERSION`, `CHECKSUM`, `CPUTYPE`.

One block = several rows, one per part. Part codes verified by payload content:

| SUBBLKTYP | Meaning | Payload field | Sample (one FC) |
| --- | --- | --- | --- |
| `00019` | block title + section/network titles | `SSBPART` (title), `MC5CODE` (titles) | 325 B → title + 5 section titles |
| `00005` | referenced-library / parameter names | `ADDINFO` | 4,021 B of FB parameter names |
| `00065` | reference list (blocks used) | `ADDINFO` | 174 B → `DB2, DB10, … FC103, FB99` |
| `00012` | compiled code part | `MC5CODE` | 788 B → 780 B code |

Other part codes exist (`00004`, `00025`, `00029`, `00034`, `00049`, `00056`) and are
reported raw by the reader.

## 6. Code part

* `BLKLANG = 1` → STL/AWL for every block seen.
* The payload is **compiled MC5/MC7 machine code**, byte-exact and hashable. It is not
  STL text and is not line-addressable without a disassembler.
* No AWL/STL source objects existed in the sample project — the `Global/s7lst/*.lst`
  files hold comments only, not code.

## 7. `XR*.DBF` — cross reference

Fields: `ID`, `OPTYPE`, `OPACCESS`, `BYTEADR`, `BITADR`, `DBNB`, `BLOCKTYPE`,
`BLOCKNB`, `ACCESS`, `LANGUAGE`, `LANGSPEC1..5`, `LOCALSYM`.

`BLOCKTYPE` + `BLOCKNB` identify the block that uses the operand (same numeric codes
as `BAUSTEIN.TYP`). `OPTYPE` codes resolved for the sample project:

| OPTYPE | Meaning | Evidence |
| --- | --- | --- |
| 2 | input (I) | 253/302 uniquely resolvable rows land on `I` symbols |
| 3 | output (Q) | 151/165 land on `Q` symbols |
| 4 | flag (M) | 425/582 land on `M` symbols |
| 5 | data block access | `DBNB` always > 0 and equals the block's own DB reference list |
| 12 | FC call | `DBNB` 103 = `FC103` from the block's reference list, 6 call sites |
| 13 | FB call | `DBNB` 99 = `FB99`, 3 call sites |
| 8, 9 | timer/counter class — **unresolved** | `OPACCESS='0'`, no symbol area to match against |
| 14 | call class — **unresolved** | `OPACCESS='5'`, `DBNB == BYTEADR` |

`ACCESS` codes are reported verbatim (1 dominates for inputs, 2 for outputs/flags —
treat that as inference, not a documented mapping).

Because `DBNB` carries the callee number for OPTYPE 12/13, the cross-reference table
alone yields the call graph, and it agrees with the textual reference list stored in
part `00065`. Use both; they are independent.

## 8. Limits

Networks, contacts/coils, comparators, timers, jumpers, indirect addressing, symbolic
local variables inside the code part and the exact STL listing are **not** derivable
from the container alone. They require decoding the code part — see
[AWL_RECOVERY.md](AWL_RECOVERY.md) — or an AWL export from SIMATIC Manager / STEP 7
Classic.
