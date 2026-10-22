# Codex Prompt Library

All prompts are written in English and are ready to copy and paste into Codex.

Use the prompts **in numerical order**. Each prompt is a separate stage; review its results before moving to the next stage.

| Order | File | Purpose |
| --- | --- | --- |
| 01 | [01-environment-and-tests.md](01-environment-and-tests.md) | Inspect Windows setup and test scaffold |
| 02 | [02-archive-identification.md](02-archive-identification.md) | Identify a local Siemens .arc file safely |
| 03 | [03-extraction-adapter.md](03-extraction-adapter.md) | Develop extraction only for verified format |
| 04 | [04-analysis-and-reporting.md](04-analysis-and-reporting.md) | Classify NC/PLC/drive data and report |
| 05 | [05-review-and-sync.md](05-review-and-sync.md) | Review tests and sync safe code to GitHub |

**Safety:** Keep actual CNC archives, extracted files, passwords, machine-specific settings, and confidential reports off GitHub. Never connect to or write to a CNC controller. Prompt 03 must wait until the archive format is confirmed.
