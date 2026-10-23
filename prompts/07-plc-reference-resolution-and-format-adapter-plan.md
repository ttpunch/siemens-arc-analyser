# Phase 07 — PLC reference resolution and format adapter plan

Work in `ttpunch/siemens-arc-analyser`. Read `AGENTS.md`, `README.md`, `docs/STATUS.md`, `docs/SOURCE_ANALYSIS.md`, current implementation, tests and existing authorized confidential local reports first.

## Goal
Improve repeatable, read-only Siemens PLC source analysis, resolve references only where supported by evidence, and plan documented offline adapters for other Siemens project formats. Do not claim proprietary binary decoding without verified results.

## Current baseline to verify
The previous stage reports 356 extracted files, five approved readable STEP 7-style sources, 14 blocks (5 OB, 1 FB, 2 FC, 6 DB), 135 variables, 35 reference occurrences, 26 resolved within readable scope and nine outside it, 24 qualified DB references without supported absolute numeric offsets, 298 binary/unknown or classification-limited files, and 89 passing tests. Verify rather than assume these numbers.

## 1. Investigate unresolved references
Using **only** the five previously approved readable source files, their approved manifest, and already authorized local reports:
- Inventory each unresolved reference with its origin, explicit target if available, source location, relationship (CALL/UC/CC, instance, DB open, qualified DB reference, symbolic/indirect reference), and reason.
- Distinguish an external or unavailable declaration from a proven missing implementation. Do not invent block definitions, symbols, DB offsets, or behavior.
- Resolve more references only if the existing source evidence supports it; distinguish occurrences, unique references, graph edges and diagnostics.
- Analyze the 24 qualified DB references conservatively; do not infer symbolic/indexed offsets or active DB contexts without proof.

## 2. Improve the source recognizer
Assess supported STEP 7 syntax for explicit symbolic block references, DB member and absolute addressing, FB instances, multiline declarations, calls and indirect forms. Implement only bounded, evidence-backed enhancements. Keep lexical relationships distinct from execution, reachability, controller-loaded program, hardware mapping or full PLC semantics.

## 3. Format research — metadata/documentation only
**Do not open, stat, read, decompress, classify further or decode the 298 excluded binary/unknown payloads, or other unapproved extracted text/XML files.** Use only already authorized metadata and existing documentation. Identify plausible Siemens PLC/NC/drive/HMI formats and official/documented offline exports or adapters, explicitly distinguishing verified facts, filename hypotheses and unknowns. Do not install or launch Siemens software, download proprietary utilities or claim universal .arc support.

## 4. Adapter architecture plan
Document modular Archive Reader → Safe Extractor → Classifier → PLC Source Parser/Reference Resolver/Documented Format Adapters/Unsupported Reporter → JSON and Markdown reports. For each proposed adapter specify evidence, supported versions, input limits, output schema, validation, unknowns and a separate approval boundary. Do not implement speculative binary decoders.

## 5. Tests and reports
Add synthetic tests for supported reference resolution, external/ambiguous symbols, DB addressing, unsupported indirect syntax, malformed source, duplicate declarations, deterministic output, immutable inputs, confined output, and excluded files remaining unopened. Run the full suite. Store detailed machine-specific identifiers, addresses, source names, hashes and reports only in fresh gitignored local directories; do not disclose them in tracked files or logs.

Update sanitized `docs/STATUS.md` and `docs/SOURCE_ANALYSIS.md`; create `docs/FORMAT_ADAPTER_PLAN.md`. Report implementation, before/after resolved and unresolved counts with precise definitions, test results, files changed, input integrity and the recommended next bounded phase.

## Hard restrictions
Follow `AGENTS.md`. No new archive/member access, excluded payload access, controller connections, restores, executing extracted code, uploads of private data, or push. Do not modify original backups. Before any expanded payload scope, stop, show a sanitized metadata-only preflight and request explicit approval; this prompt is **not** that approval. Do not present planned work as completed.
