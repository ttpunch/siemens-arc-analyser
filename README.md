# Siemens ARC Analyser

Read-only Siemens SINUMERIK `.arc` archive identification and analysis project.

**Current status:** generic archive signature inspection, explicitly approved local
ZIP batch copying/classification, and bounded read-only PLC source inventories
are implemented. A read-only STEP 7 Classic (V5.x) project reader and AWL/STL
recovery path are now included — see
[docs/STEP7_PROJECT_FORMAT.md](docs/STEP7_PROJECT_FORMAT.md) and
[docs/AWL_RECOVERY.md](docs/AWL_RECOVERY.md). Proprietary Siemens binary decoding is
not implemented **in this repository**; block code is decoded with external,
separately built decoders (documented, never bundled).

## Windows setup
```powershell
git clone https://github.com/ttpunch/siemens-arc-analyser.git
cd siemens-arc-analyser
py -3 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -e .
python -m arc_analyser.cli "C:\path\to\backup.arc"
```

Keep real archives locally. Do not commit machine backups, extracted data, passwords or confidential settings.

## Development without installing packages

If `py` cannot find Python, use the available `python` command (Python 3.11+).
The runtime and test suite use the standard library:

```powershell
python -m venv --without-pip .venv
$env:PYTHONPATH = 'src'
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
.\.venv\Scripts\python.exe -m arc_analyser.cli "C:\path\to\backup.arc"
```

The inspector recognizes generic ZIP, ustar TAR, 7z, and RAR signatures;
it does not validate all archive contents or identify Siemens-specific variants.
See [docs/STATUS.md](docs/STATUS.md) for verified coverage and environment findings.

## STEP 7 Classic project reader and AWL recovery

A ZIP or folder carrying `ombstx/`, `sdb/`, `YDBs/`, `XUTILS/`, `s7asrcom/` is a legacy
STEP 7 V5 project, not an `.arc` backup. Its program is enumerable read-only, offline:

```bash
PYTHONPATH=src python -m arc_analyser.step7.s7_project <project.zip|dir> --out out/
PYTHONPATH=src python -m arc_analyser.step7.s7_project <project.zip> --out out/ --block FC67
PYTHONPATH=src python -m arc_analyser.step7.s7_project <project.zip> --out out/ --report-all --blobs
```

That yields block inventory (`BAUSTEIN.DBF` is authoritative — never count by grepping
the archive), symbolic names and comments, stored block/section titles, the reference
list per block, a resolved operand footprint, a call graph, and byte-exact code
payloads. Instruction-level AWL/STL is recoverable with one of two independent
decoders — symbolic via `DotNetSiemensPLCToolBoxLibrary` (needs a .NET SDK) or linear
MC7 disassembly via `rz-libmc7`:

```bash
PYTHONPATH=src python -m arc_analyser.step7.s7_dotnet_awl <project.zip> --out out/ --all
PYTHONPATH=src python -m arc_analyser.step7.s7_awl        <project.zip> --out out/ --awl-all
```

See [docs/STEP7_PROJECT_FORMAT.md](docs/STEP7_PROJECT_FORMAT.md) for the verified
container/table/memo layout, [docs/AWL_RECOVERY.md](docs/AWL_RECOVERY.md) for both
decoders and the cross-check rule, and
[skills/siemens-arc-analyser/SKILL.md](skills/siemens-arc-analyser/SKILL.md) for the
agent-facing procedure.

For the existing approved batch output, analyze only its five classified source
files without reopening an archive:

```powershell
$env:PYTHONPATH = (Join-Path (Get-Location) 'src')
.\.venv\Scripts\python.exe -m arc_analyser.plc_analysis --run-locator local_data/completed_batch_locator.json
```

See [the source-analysis guide](docs/SOURCE_ANALYSIS.md) for limits, repeatability,
confidential report handling and the distinction between lexical evidence and
unknown project semantics.
