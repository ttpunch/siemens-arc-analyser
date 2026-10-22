# Prompt 02D — Offline PLC Source Structure Analysis

Read AGENTS.md, docs/STATUS.md and Prompt 02C results before proceeding.

## Goal
Analyze the structure of the **two previously verified STEP 7-style source-text members only** from the same local ZIP archive. Identify actual source block declarations (OB, FB, FC, DB, UDT, if present), symbolic names, interfaces, declaration sections, and statically visible CALL/reference relationships. Report uncertainty; do not infer executable PLC behavior from names alone.

## Authorization and boundaries
This authorizes a **read-only reinspection of only the two previously approved, verified source members** using the already implemented bounded in-memory reader and the exact prior private allowlist and SHA-256 baseline. No new archive members, binary/unknown members, or XML payload may be opened. Do not extract to filesystem, open projects in STEP 7, execute code, connect to controllers, restore backups, or upload archive-derived information. Stop and ask for explicit approval if further members or Siemens software are needed.

## Steps
1. Verify the same local archive copy, unchanged SHA-256 baseline, private member allowlist, gitignore protection, and bounded reader/worker. If any condition fails, stop before payload reads.
2. Reread **only the two previously verified text members** within the existing limits: <=64 KiB decompressed per member, <=256 KiB aggregate, <=100 compression ratio, <=4 KiB chunks, 256 MiB Windows Job Object committed-memory limit, 10-second timeout. Preserve all existing ZIP safety checks.
3. Parse text conservatively and offline. Recognize only clearly delimited STEP 7-style source blocks and common declaration keywords; distinguish source text from compiled PLC binaries. Capture block kind, declared identifier/number when explicit, optional symbol, interface headings (VAR_INPUT, VAR_OUTPUT, VAR_IN_OUT, VAR, VAR_TEMP, etc.), and explicitly written CALL/reference targets. Do not claim completeness or infer targets when syntax is ambiguous. Treat comments and quoted strings as data, not executable calls.
4. Produce a **private local-only** structured report in the existing ignored report location: member-level block inventory, source line ranges, explicitly detected references, unresolved syntax, and parser warnings. Never print or commit actual archive member paths, proprietary code, symbol names, raw snippets, machine-specific identifiers, or detailed report contents.
5. Add synthetic fixtures and unit tests for OB/FB/FC/DB recognition, multiline declarations, quoted/commented false positives, references, malformed/incomplete syntax, encodings, bounds, and unchanged archive. Reuse the bounded reader; no new dependencies without permission.
6. Run the complete test suite. Update docs/STATUS.md with **sanitized aggregates only**: number of authorized source members inspected, counts by recognized block type, number of explicit references (without identifiers), unsupported constructs, tests, and limitations. Avoid revealing private block identifiers or project names.
7. Review git status and confirm no private data is staged. Do not commit or push automatically; provide safe review instructions.

## Completion criteria
Clearly separate **verified source structure**, **tentative syntax recognition**, and **unknown project semantics**. Confirm archive before/after SHA-256 equality. State whether the two sources are sufficient for meaningful PLC logic mapping or whether broader inspection would require a separately approved scope. **Do not proceed to Prompt 03 or implement general extraction.**
