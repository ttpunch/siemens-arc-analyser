# STEP 7 Classic project reader

Read-only readers for legacy STEP 7 V5 projects (`BAUSTEIN.DBF` / `SUBBLK.DBF` /
`SYMLIST.DBF` / `XR*.DBF`). Standard library only, Python 3.11+.

Format details and their evidence: [docs/STEP7_PROJECT_FORMAT.md](../../../docs/STEP7_PROJECT_FORMAT.md).
AWL/STL decoding: [docs/AWL_RECOVERY.md](../../../docs/AWL_RECOVERY.md).

## Block inventory and per-block reports

```bash
PYTHONPATH=src python -m arc_analyser.step7.s7_project <project.zip|dir> --out out/
PYTHONPATH=src python -m arc_analyser.step7.s7_project <project.zip> --out out/ --block FC67
PYTHONPATH=src python -m arc_analyser.step7.s7_project <project.zip> --out out/ --report-all --blobs
PYTHONPATH=src python -m arc_analyser.step7.s7_project <project.zip> --out out/ --folder '^proj/ombstx'
```

Writes `blocks.csv`, `symbols.csv`, `xref.csv`, `callgraph.csv`,
`blocks/<LABEL>.md` and, with `--blobs`, byte-exact `<LABEL>.mc5` payloads.

Per block it reports: type and number, symbolic name and comment, stored block title,
section titles in project order, referenced blocks (call graph), the resolved operand
footprint (I/Q/M with signal names, DB accesses, FC/FB calls) and the code payload
hash.

## AWL recovery

```bash
# route A: symbolic, needs .NET (docs/AWL_RECOVERY.md)
PYTHONPATH=src python -m arc_analyser.step7.s7_dotnet_awl <project.zip> --out out/ --all
# route B: linear MC7 disassembly, needs the mc7dis binary
PYTHONPATH=src python -m arc_analyser.step7.s7_awl <project.zip> --out out/ --awl-all
```

## Safety

Copy first, analyse the copy. The readers never modify a project, never connect to a
controller and never execute extracted content. Do not commit project data, block
sources or reports containing machine information — `local_data/` is gitignored for
that reason.

## Tests

```bash
PYTHONPATH=src python -m unittest discover -s tests -v
```

The STEP 7 tests build their fixture project from synthetic DBF/DBT tables
(`tests/step7_fixtures.py`); no archive or machine data is required.
