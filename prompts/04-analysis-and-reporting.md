# Prompt 04 — Analyse Extracted Archive Data

Run after safe extraction has been tested.

```text
Read AGENTS.md and docs/STATUS.md.

Develop local-only analysis for extracted SINUMERIK archive content. Classify files into NC programs, PLC-related data, machine data, drive data, alarms, and unknown. Preserve source file paths and evidence for every classification.

Create searchable local JSON and Markdown reports, with cautious interpretation and explicit unknowns. Never invent PLC logic or parameter meaning. Use Siemens manuals and version-specific documentation when available. Add tests using synthetic examples.

Keep reports and extracted data in gitignored local directories. Do not expose passwords, machine identifiers, network details, or confidential settings. Update docs/STATUS.md and commit only safe code and documentation; do not push until I ask.
```
