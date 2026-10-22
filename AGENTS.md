# Codex instructions — Siemens ARC Analyser

Goal: build a Windows-first, read-only Siemens SINUMERIK `.arc` archive analyser. Identify archive variants by evidence; never assume `.arc` is ZIP or a SIMATIC Manager project.

Safety: never modify original backups, connect to controllers, restore data, execute extracted programs, or upload confidential machine information. Keep real archives in `local_data/` (gitignored). Inspect only copies. Reject traversal paths, symlinks, oversized files and decompression bombs before any future extraction. Do not install proprietary software without permission.

Development: Python 3.11+, typed code, tests, standard library first. Phase 1: inspect signatures and metadata without extraction. Phase 2: identify installed Siemens utilities and research format-specific adapters. Phase 3: safely classify NC/PLC/drive/machine data and generate local reports. Record findings in `docs/STATUS.md`. Do not claim support until verified with tests.

Codex first task: inspect Windows environment, run tests, inspect a local sample `.arc` read-only, report its signature and likely archive variant, and propose a tested extraction approach. Never push raw archive contents.
