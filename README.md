# Siemens ARC Analyser

Read-only Siemens SINUMERIK `.arc` archive identification and analysis project.

**Current status:** generic archive signature inspection, explicitly approved local
ZIP batch copying/classification, and bounded read-only PLC source inventories
are implemented. Proprietary Siemens binary decoding is not implemented.

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

## Codex skills

The repository bundles five independent offline workflows under
[`.agents/skills/`](.agents/skills). Ask Codex for the matching workflow, or
invoke its skill by name:

| Skill | Use it for |
| --- | --- |
| [`$siemens-archive-inspection`](.agents/skills/siemens-archive-inspection/SKILL.md) | Identify an archive, inventory available sources, and establish coverage. |
| [`$siemens-step7-classic`](.agents/skills/siemens-step7-classic/SKILL.md) | Inspect SIMATIC Manager blocks, reference data, I/O assignments and spare-input candidates. |
| [`$siemens-tia-project-reading`](.agents/skills/siemens-tia-project-reading/SKILL.md) | Read an offline TIA Portal project through a compatible Openness connection or the native editor. |
| [`$sinumerik-plc-alarms`](.agents/skills/sinumerik-plc-alarms/SKILL.md) | Trace PLC alarm display, acknowledgment, NC reactions and restart conditions. |
| [`$siemens-manual-research`](.agents/skills/siemens-manual-research/SKILL.md) | Find Siemens manual evidence and reconcile it with project behavior; optionally use NotebookLM. |

These are instructions, not additional archive decoders or installed connectors.
Classic GUI reading has been exercised on a sample project, but automatic
reopening is not reliable on every launch. Bulk decoding of compiled Classic
blocks and end-to-end TIA export are not established by these skills. NotebookLM
requires a working connection and is optional.

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

For the existing approved batch output, analyze only its five classified source
files without reopening an archive:

```powershell
$env:PYTHONPATH = (Join-Path (Get-Location) 'src')
.\.venv\Scripts\python.exe -m arc_analyser.plc_analysis --run-locator local_data/completed_batch_locator.json
```

See [the source-analysis guide](docs/SOURCE_ANALYSIS.md) for limits, repeatability,
confidential report handling and the distinction between lexical evidence and
unknown project semantics.
