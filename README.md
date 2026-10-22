# Siemens ARC Analyser

Read-only Siemens SINUMERIK `.arc` archive identification and analysis project.

**Current status:** initial scaffold only. Archive extraction is not implemented.

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
