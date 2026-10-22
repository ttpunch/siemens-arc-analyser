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
