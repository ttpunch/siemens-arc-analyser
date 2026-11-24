# Codex instructions — Siemens ARC Analyser

Goal: build a Windows-first, read-only Siemens toolkit in two workstreams. **(1) Archives and STEP 7 Classic:** identify and analyse SINUMERIK `.arc` backups and STEP 7 V5 projects by evidence; never assume `.arc` is ZIP or a SIMATIC Manager project. **(2) TIA Portal:** inspect TIA projects read-only through the Openness API and diagnose why blocks report `IsConsistent = False`.

Safety: never modify original backups, connect to controllers, restore data, execute extracted programs, or upload confidential machine information. Keep real archives in `local_data/` (gitignored). Inspect only copies. Reject traversal paths, symlinks, oversized files and decompression bombs before any future extraction. Do not install proprietary software without permission.

TIA Portal rules, in addition to the above:

* Never compile a project unless it has been archived first (`Project.Archive()` → `.zap20`, path and size recorded) **and** the user has explicitly approved the compile scope. A compile writes artifacts into the project; it is never part of a read-only sweep.
* Never compile a failsafe (F) block as part of a general sweep. F programs follow the safety workflow and need their own acceptance.
* Never attempt to defeat know-how protection, and never present protected block logic as known. Report such blocks as interface-only.
* Never accept an Openness trust dialog on the user's behalf. That decision belongs to the operator at the machine.
* A probe launched over SSH sees nothing: Windows OpenSSH runs in **session 0**, TIA Portal runs in **session 1**, and Openness discovers instances per session. Launch probes inside the interactive session (scheduled task with `<LogonType>InteractiveToken</LogonType>`) instead of inventing a workaround that elevates privileges.
* Separate evidence from interpretation in every report. `IsConsistent = False` usually means *compile pending*, not defective, and TIA never exposes the reason for it — only compiler messages do.

Development: Python 3.11+, typed code, tests, standard library first. Phase 1: inspect signatures and metadata without extraction. Phase 2: identify installed Siemens utilities and research format-specific adapters. Phase 3: safely classify NC/PLC/drive/machine data and generate local reports. Record findings in `docs/STATUS.md`. Do not claim support until verified with tests.

Skills under `skills/` are the agent-facing procedures and must stay executable as written:

* `skills/siemens-arc-analyser/` — archive identification, STEP 7 V5 project inventory, AWL/STL recovery.
* `skills/tiaHarness/` — explain an open TIA Portal project or a STEP 7 V5 project end to end: V20 vs V21 routing, read-only export, decoded SCL/AWL, NCU backup machine data, and the safety rules (never handle passwords, archive before compile, no failsafe sweeps).
* `skills/tia-consistency-diagnosis/` — the evidence ladder for `IsConsistent = False`: project conversion log and fingerprint list (tier 0), Openness inventory plus attempted block export as an inconsistency oracle (tier 1), compiler messages (tier 2, mutating).

When adding or changing a skill: keep helper scripts standard-library only, add tests that use synthetic fixtures rather than real machine data, and update the skill's `version` in the frontmatter.

Codex first task: inspect Windows environment, run tests, inspect a local sample `.arc` read-only, report its signature and likely archive variant, and propose a tested extraction approach. Never push raw archive contents. If TIA Portal is installed, also report the Portal version, the `PublicAPI\V<version>\Siemens.Engineering.dll` file version, whether the current user is in the `Siemens TIA Openness` group, and the running instances — metadata only, no project contents.
