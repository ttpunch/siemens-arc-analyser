# Prompt 03 — Implement a Verified Extraction Adapter

Run only after the archive format is confirmed and extraction is approved.

```text
Read AGENTS.md and the format-identification findings.

Implement a read-only extraction adapter only for the archive format verified in the previous stage. Prefer documented Siemens tooling when the archive requires it; do not reverse-engineer by guesswork or claim unsupported formats work.

Use a copied sample archive and a local, gitignored output directory. Before extraction, validate destination paths, reject traversal and symlink escapes, enforce file count and size limits, and avoid executing extracted files. Preserve original bytes and capture provenance.

Add tests with synthetic, non-confidential fixtures. If a required Siemens utility or license is missing, stop and explain the blocker. Update documentation with exact supported formats and limitations. Do not upload original or extracted machine data. Commit safe source code only; do not push until I ask.
```
