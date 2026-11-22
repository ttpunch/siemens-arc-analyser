# Siemens ARC Analyser

Read-only Siemens SINUMERIK `.arc` archive identification and analysis project, plus read-only
STEP 7 Classic project inspection and TIA Portal consistency diagnosis.

**Current status:** generic archive signature inspection, explicitly approved local
ZIP batch copying/classification, and bounded read-only PLC source inventories
are implemented. A read-only STEP 7 Classic (V5.x) project reader and AWL/STL
recovery path are now included — see
[docs/STEP7_PROJECT_FORMAT.md](docs/STEP7_PROJECT_FORMAT.md) and
[docs/AWL_RECOVERY.md](docs/AWL_RECOVERY.md). TIA Portal projects can be inspected
read-only through the Openness API to explain `IsConsistent = False` — see
[skills/tia-consistency-diagnosis/SKILL.md](skills/tia-consistency-diagnosis/SKILL.md).
Proprietary Siemens binary decoding is not implemented **in this repository**; block
code is decoded with external, separately built decoders (documented, never bundled).

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

## TIA Portal — consistency diagnosis

TIA exposes `PlcBlock.IsConsistent` and never the reason for it. The skill in
[skills/tia-consistency-diagnosis/](skills/tia-consistency-diagnosis/SKILL.md) answers
*"why is this block inconsistent?"* by climbing an evidence ladder, cheapest first:

| Tier | Evidence | Writes to the project? |
|---|---|---|
| 0 | the project's own `Logs\ConversionLog_*.xml` and its fingerprint list | no |
| 1 | Openness block inventory + attempted export of every block | no |
| 2 | compiler messages from a real compile | **yes** |

Tier 0 is often conclusive: after a version migration the conversion log names every
know-how-protected object whose integrity fingerprint the upgrader deliberately left
intact — those objects no longer match their compiled state and report
`IsConsistent = False`. Tier 1 adds the enumeration and uses the export attempt as an
inconsistency oracle, because TIA refuses to export a block whose source and compiled
state disagree.

```powershell
# on the Windows host, from a folder holding Siemens.Engineering*.dll
csc /out:TiaProbe.exe /r:"C:\Program Files\Siemens\Automation\Portal V20\PublicAPI\V20\Siemens.Engineering.dll" TiaProbe.cs
TiaProbe.exe                                                   # running instances + open project path
TiaProbe.exe --blocks --export "C:\Users\<user>\tiaexport" > export_result.txt
```

```bash
python skills/tia-consistency-diagnosis/scripts/consistency_triage.py \
    --inventory result.txt --export-log export_result.txt --xml-dir tiaexport --out report.md
```

Tier 2 is the only authoritative source and the only one that mutates the project, so it
requires an archive first and explicit approval of the compile scope; failsafe blocks are
excluded from any general sweep.

## Safety

Everything here is read-only against originals: no project writes, no controller
connection, no restore, no execution of extracted content. The one documented exception
is the tier-2 compile above, which is archived and approved first. Probes launched over
SSH see no TIA instance — Windows OpenSSH runs in session 0 while TIA Portal runs in
session 1 — so they are started inside the interactive session, never by elevating.

## Files

`src/arc_analyser/` · `tests/` · `docs/` · `prompts/` · `skills/` (agent-facing
procedures) · [AGENTS.md](AGENTS.md) · [.gitignore](.gitignore) ·
[pyproject.toml](pyproject.toml)

## Approved batch output

For the existing approved batch output, analyze only its five classified source
files without reopening an archive:

```powershell
$env:PYTHONPATH = (Join-Path (Get-Location) 'src')
.\.venv\Scripts\python.exe -m arc_analyser.plc_analysis --run-locator local_data/completed_batch_locator.json
```

See [the source-analysis guide](docs/SOURCE_ANALYSIS.md) for limits, repeatability,
confidential report handling and the distinction between lexical evidence and
unknown project semantics.
