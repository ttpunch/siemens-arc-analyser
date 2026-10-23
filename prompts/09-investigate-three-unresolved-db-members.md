# Phase 08 — Investigate Three Unresolved DB Member Identities (Existing Approved Sources Only)

You are working in the local `ttpunch/siemens-arc-analyser` project. Read `AGENTS.md`, `docs/STATUS.md`, `docs/SOURCE_ANALYSIS.md`, and `docs/FORMAT_ADAPTER_PLAN.md` before making changes. Read the current source-analysis implementation and synthetic tests, plus **only the previously approved five readable PLC source files and their existing private reports/manifests**.

## Objective
Investigate the **three unestablished symbolic DB member-use identities** among 24 qualified DB reference occurrences. Current documented baseline: 21 of 24 member-use identities established; three unestablished; all 24 absolute byte/bit offsets unknown; 26 of 35 block-reference occurrences resolved within readable scope, nine outside. These metrics represent different evidence levels: do not conflate them.

For each of the three unresolved member-use identities, determine from authorized evidence only:
- The exact expression and source location, kept **private**.
- Whether the corresponding DB declaration exists uniquely within the five approved sources.
- Whether the member field is explicitly declared and matches under the parser's supported lexical rules.
- Whether resolution is blocked by an absent declaration, nested/indexed/qualified syntax, ambiguity, duplicate definitions, unsupported grammar, symbol table dependency, or another precise reason.
- Whether a narrow, evidence-based parser enhancement could safely establish the member identity; distinguish identity from absolute byte/bit address.
- Which additional evidence would be necessary if resolution is impossible under current scope.

## Execution constraints
- **Do not open, stat, decompress, classify, or inspect any additional archive member payload**, including the 298 binary/unknown files or other extracted text/XML.
- Do not reopen the .arc/ZIP archive or original backups. Do not run STEP 7, TIA, SINUMERIK, Siemens utilities, PLC/CNC connections, restores, uploads, or network transfers.
- No proprietary binary decoder, guessed DB layout, inferred absolute offsets, inferred symbol-table mappings, or reconstruction of missing PLC code.
- Preserve read-only handling of approved inputs; all detailed output remains in a **new gitignored local report directory**. Do not commit private source text, paths, names, addresses, hashes, or machine details.
- Do not install packages or push commits without explicit permission. Follow existing memory/time/size budgets and integrity/determinism protections.

## Workflow
1. **Baseline/preflight:** Verify current git status, approved manifest, approved source count, allowed paths, existing report schema, and exact current metrics. Print only sanitized counts and broad categories.
2. **Private diagnosis:** Create a three-row private investigation table with one row per unresolved member-use identity: source reference, DB target evidence, candidate declaration/field evidence, parser reason, resolution possibility, and next evidence needed.
3. **Implement only if justified:** If an unresolved identity can be established by an unambiguous declaration already present in approved source text, implement the **smallest conservative parser change**. Add synthetic positive, negative, ambiguity, malformed-input, and regression tests. Never force resolution just to improve a metric.
4. **Validate:** Run synthetic tests and the source-only analyzer within approved limits; verify unchanged input hashes, deterministic report content, and zero access to excluded payloads. Report test counts accurately.
5. **Update documentation:** Update `docs/SOURCE_ANALYSIS.md` and `docs/STATUS.md` with sanitized before/after counts and explicit limits. Update `docs/FORMAT_ADAPTER_PLAN.md` only if the evidence materially changes it.
6. **Finish with a concise summary:** For each of the three references, state privately whether resolved, still unresolved, or requires a new separately approved source/export. Explain why. Report counts and the next smallest safe step. **Stop before any expansion of scope.**

## Success criteria
Success is an evidence-backed diagnosis of all three identities, **not necessarily resolving all three**. If any identity cannot be established from the five authorized sources, preserve it as unknown and explain the exact missing evidence. Keep member identity, block-target resolution, syntax diagnostics, and absolute offsets as separate metrics.