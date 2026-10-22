# Prompt 02 — Identify a Local Siemens .arc Archive

Run after Prompt 01. Copy into Codex:

```text
Read AGENTS.md and docs/STATUS.md. I will provide the path to a local Siemens SINUMERIK .arc archive.

Ask me for the local archive path if it is not yet known. Inspect the file strictly read-only; do not modify, move, extract, execute, or upload it.

1. Record file size and a cryptographic hash locally.
2. Inspect the file signature and run the project's non-extracting inspector.
3. Determine whether it is a standard container or a Siemens-specific archive. Do not assume ZIP compatibility from the .arc extension.
4. Investigate available installed Siemens tools and their documented archive support.
5. Produce a local report of format evidence, confidence, limitations, and safe extraction options. Redact paths, machine identifiers, and secrets before sharing any report.
6. Update docs/STATUS.md with non-sensitive findings only.

Stop and ask me before installing software, using proprietary tools, or extracting contents. Never push the archive or raw inspection reports.
```
