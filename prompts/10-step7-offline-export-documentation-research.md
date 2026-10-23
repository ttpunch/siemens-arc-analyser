# Phase 10 — Classic STEP 7 Offline Text Export: Documentation-Only Feasibility Study

You are working on `ttpunch/siemens-arc-analyser`. Read `AGENTS.md`, `docs/STATUS.md`, `docs/SOURCE_ANALYSIS.md`, `docs/FORMAT_ADAPTER_PLAN.md`, and the latest Phase 09 results before proceeding. Follow all repository confidentiality and approval rules.

## Objective
Research **documented, offline, read-only or disposable-copy export methods** for obtaining authoritative PLC DB declarations, symbols, and block source/text from a Classic STEP 7 V5.x project (installed STEP 7 V5.7 SP3 is a candidate environment). We need evidence potentially relevant to the **three unresolved symbolic DB member uses** from the five already approved PLC sources. This is a **documentation-only investigation**, not permission to open a project or export anything.

## Strict authorization boundary
- Do not open, decompress, read, stat or inspect any previously excluded archive member payload, original .arc/ZIP archive, backup, project database, XML, or other unapproved source.
- Do not launch STEP 7, SIMATIC Manager, TIA Portal, SCL editor, Siemens utilities, or any executable/script from an archive.
- Do not connect to any PLC/CNC, network share, online service, device or cloud endpoint; no uploads, restores, downloads, package installs or license changes.
- You may read existing approved reports, sanitized repository docs, and previously identified **local Siemens manuals/readmes/help text**, but do not broaden filesystem searching or open compiled help without an explicit separate scope.
- Keep machine names, identifiers, paths, addresses, hashes, and private report details only in a fresh gitignored local report. Public tracked docs must remain sanitized.
- Do not claim a format/API works unless the cited version-specific documentation establishes it. No fabricated commands, APIs, database layouts or Siemens binary decoding.
- No git push or commit without permission.

## Research questions
1. For STEP 7 Classic V5.x, distinguish **existing source files**, **generated STL/AWL representation of compiled blocks**, **SCL source availability**, **DB declarations**, **symbol table export**, **hardware configuration**, and **cross-reference export**. Identify which operations are documented and what they actually preserve or omit.
2. Determine documented manual/offline paths, if any, for viewing/exporting DB structure and symbolic names from a disposable copy of a project, including prerequisites, UI menu path or supported interface and product/version limitations.
3. Establish whether the documented source/symbol export can disambiguate the three missing DB fields; do not assume those fields exist. Distinguish DB field names from absolute DB byte/bit offsets and from symbols in an external symbol table.
4. Examine only authorized documentation for official automation options (e.g., documented interfaces/APIs), version constraints, licensing and potential project mutation. Mark anything unverified as a research lead.
5. Assess offline safety: whether opening/retrieving a project changes files, what copy/backup isolation is necessary, whether any operation can contact a PLC, and how to prevent that in a future separately approved trial.
6. Propose a minimal **future** bounded experiment using a synthetic or non-machine project first. Include preflight: exact input count/types, maximum bytes, destination, tool/version, time/resource limits, rollback, private output policy, and explicit approval gate. Do not perform the experiment.

## Deliverables
- `docs/STEP7_OFFLINE_EXPORT_RESEARCH.md`: concise sanitized evidence matrix: task/capability, exact manual/readme title and edition/page/section where available, applicable STEP 7 version, prerequisites, output form, confidence, limitations, and whether actually tested (expected: no).
- `docs/STATUS.md`: add a dated, sanitized Phase 10 status section, with documentation examined, supported versus unsupported conclusions, and the next approval gate.
- Update `docs/FORMAT_ADAPTER_PLAN.md` only where the documentary evidence genuinely changes the adapter plan. Leave `docs/SOURCE_ANALYSIS.md` unchanged unless correcting a factual error.
- Private gitignored research notes with any sensitive identifiers or local documentation paths; no machine-specific details in tracked files.
- Synthetic/documentation-only tests if useful, but no need to change parser code. Report test execution truthfully.

## Completion criteria
Give a short summary of **verified documentation**, **hypotheses**, **unverified capabilities**, and a precise **approval request for a later experiment**. Stop. Do not open a real project, run Siemens software, read new archive members, export actual blocks or resolve the three member identities by guesswork.

Begin with a metadata-only git status and a review of the already authorized documentation inventory. If even documentation access would exceed the current approved scope, stop and ask before proceeding.