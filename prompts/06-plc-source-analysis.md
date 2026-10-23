# 06 — Complete Offline PLC Source Analysis (Codex)

You are continuing the existing Siemens ARC Analyser repository, not starting a new project.

## Read first
Read `AGENTS.md`, `docs/STATUS.md` (especially the 2026-10-23 approved offline ZIP batch section), `prompts/README.md`, the batch workflow documentation, current source code/tests, and existing **ignored local** batch manifests and reports. Check git status and the latest actual code before making changes. Do not assume README's old scaffold statement reflects current implementation.

## Goal and scope
Complete a reliable, repeatable **read-only analysis stage for the five already classified readable STEP 7-style PLC source files** in the existing approved local batch output. This is a source-level inventory, not full PLC decompilation or Siemens binary decoding. Do not read additional opaque/binary payloads, expand to other archives, open Siemens software, connect to controllers, or access original backups. Use only the already approved local extracted source files and synthetic fixtures. If a new archive-member read or expanded scope is required, stop and ask for explicit approval with a bounded preflight.

## Implement in stages
1. Inspect the existing extracted-file manifest, source classification, lexical recognizer, and tests. Identify gaps before changing code. Reuse existing parsers and safety controls.
2. Create a deterministic offline PLC source-analysis command/API consuming the existing approved run directory and manifest, using generated IDs rather than trusting archive paths. Enforce path confinement, no symlink/reparse escape, size limits, no executable content, and unchanged input. Default to read-only.
3. Parse and inventory all supported explicit OB, FB, FC, DB and UDT declarations, source line ranges, declaration sections, variables, addresses, and block boundaries. Record evidence and confidence; preserve ambiguous/unrecognized syntax as warnings, not guesses.
4. Build a conservative directed call/reference graph: explicit CALL/UC/CC, DB accesses, symbolic references only when resolvable from supported syntax, and clearly separate unresolved or indirect calls. Distinguish occurrence counts from unique references. Do not claim runtime call flow or controller-loaded logic.
5. Extract explicitly present I/Q/M/DB addressing and timer/counter references where syntactically supported. Clearly distinguish address mentions from actual physical I/O mapping and read/write semantics. Do not infer machine behavior or interlocks from names alone.
6. Produce confidential local JSON and readable Markdown reports: inventory, references/call graph, unresolved items, per-source coverage, warnings, and suggested next investigations. Keep source text, member names, machine data, IDs, hashes, and local paths out of tracked reports and logs. Reports must stay in a newly created gitignored directory; avoid overwrites.
7. Add synthetic unittest fixtures covering all supported block types, comments/strings, mixed encoding/BOM, multiline declarations, indirect/ambiguous calls, duplicates, malformed syntax, traversal/reparse protection, and determinism. Run the full existing suite; report exact results.

## Completion gate
Before suggesting the next phase, provide a coverage table showing which of the five readable sources were analyzed, counts by supported block type, explicit calls, references, I/O-address mentions, unresolved constructs, and validation outcomes. Explain precisely what cannot be established without binary decoding or a Siemens tool. Do not invent missing results. Keep the 298 binary/unknown files untouched.

## Repository discipline
Keep all confidential inputs/outputs offline and gitignored. No package installation, network upload, controller access, Siemens application launch, restore, or execution of archive content. Do not commit or push without separate user approval. Update `docs/STATUS.md` with sanitized findings and a recommended next phase; give the user a concise review and ask permission before progressing beyond this PLC source-analysis scope.
