---
name: siemens-arc-analyser
description: Use when identifying SINUMERIK ARC archives or STEP 7 projects read-only.
version: 1.3.0
license: MIT
metadata:
  hermes:
    tags: [sinumerik, cnc, arc, archive, plc, read-only, step7, s7-300, awl, fc, fb]
---

# Siemens ARC Analyser

Read-only inspection of Siemens SINUMERIK `.arc` archives **and** legacy STEP 7
Classic (V5.x) projects, including block inventory and AWL/STL recovery.
Everything here operates on a copy: no project writes, no controller connection, no
restore, no execution of extracted content.

## When to use

* Identify what an `.arc` file or an archive actually is (signature first, extension
  never trusted).
* Answer "how many FC/FB does this project have", "what does FC67 do", "which blocks
  does it call", "which signals does it touch".
* Recover instruction-level AWL/STL when no Siemens software is available.

## Classification first

A `.zip`/folder containing `ombstx/`, `sdb/`, `YDBs/`, `XUTILS/`, `s7asrcom/` is a
**STEP 7 Classic project package**, not a Siemens `.arc` backup. Say so explicitly,
then use the STEP 7 readers. Verify ZIP integrity, record entries/sizes and the
SHA-256 of the analyzed copy.

## STEP 7 project inventory

```bash
PYTHONPATH=src python -m arc_analyser.step7.s7_project <project.zip|dir> --out out/
PYTHONPATH=src python -m arc_analyser.step7.s7_project <project.zip> --out out/ --block FC67
PYTHONPATH=src python -m arc_analyser.step7.s7_project <project.zip> --out out/ --report-all --blobs
```

Artifacts: `blocks.csv`, `symbols.csv`, `xref.csv`, `callgraph.csv`,
`blocks/<LABEL>.md`, optional `<LABEL>.mc5`.

Rules learned the hard way (evidence in `docs/STEP7_PROJECT_FORMAT.md`):

1. **Count blocks from `BAUSTEIN.DBF`**, never by grepping archive bytes. A regex over
   a real project over-counted 65 "FC" where the catalog held 54.
2. **Check for two copies of the project inside one archive.** Enumerate every
   `ombstx/offline/*/BAUSTEIN.DBF`; use `--folder` to isolate one.
3. **Memo entries are `ff ff` + u16 header(8) + u32 length + payload**, not
   `0x1A1A`-terminated. Bound every payload with the declared length, which equals
   `MC5LEN`/`SSBLEN`/`ADDLEN`.
4. Block titles, section titles and reference lists are ordinary memo text — read
   them before claiming logic is unavailable.
5. `TYP` codes: 8=OB, 10=DB, 12=FC, 13=SFC, 14=FB, 27=VAT, 0=UDT.
6. `XR` `OPTYPE`: 2=I, 3=Q, 4=M, 5=DB access, 12=FC call, 13=FB call; 8/9/14 are
   unresolved and must be reported raw.

## AWL / STL recovery

Route A (symbolic, requires .NET) then Route B (independent cross-check):

```bash
PYTHONPATH=src python -m arc_analyser.step7.s7_dotnet_awl <project.zip> --out out/ --all
PYTHONPATH=src python -m arc_analyser.step7.s7_awl       <project.zip> --out out/ --awl-all
```

Verify a decode against the block's stored reference list (part `00065`) and the xref
`DBNB` values before trusting it. Report a decode as a **read-only reconstruction**,
never as a Siemens-exported listing, and say it should be confirmed in SIMATIC
Manager / STEP 7 Classic before maintenance decisions.

## Safety

Never modify originals, connect to controllers, restore data, execute extracted
programs, upload archives, or expose confidential machine contents. Analyze only a
copy under a gitignored local-data directory. Reject traversal/absolute paths,
symlinks, oversized entries and decompression bombs before any extraction. Reports
must distinguish lexical evidence from unknown project semantics.

See `docs/STEP7_PROJECT_FORMAT.md`, `docs/AWL_RECOVERY.md`,
`src/arc_analyser/step7/README.md`.
