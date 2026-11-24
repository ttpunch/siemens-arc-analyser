---
name: awl-decoder
description: Use to decode STEP 7 V5 (SIMATIC Manager) block logic to readable AWL/STL, build a call graph, and read the result. Read-only, works on a copy.
version: 1.0.0
license: MIT
metadata:
  hermes:
    tags: [step7, awl, stl, mc7, decoder, call-graph, read-only, windows]
---

# AWL decoder

Turn the binary blocks of a STEP 7 V5 project into readable AWL, then explain them. The block
tables (`BAUSTEIN.DBF`, `SYMLIST.DBF`, `XR*.DBF`) give inventory, symbols and references; the code
itself is MC7 binary and needs a decoder. This skill covers decoding and reading the result.
Inventory and project rules live in `siemens-arc-analyser`; project-level explanation in `tiaHarness`.

## Safety

- Work on a copy of the project. Nothing here writes to a project, connects to a controller, or
  runs extracted content.
- Know-how-protected blocks decode to the interface only (or garbage with Route B). Do not try to
  defeat the protection and do not look for passwords.
- Describe every decode as a read-only reconstruction, to be confirmed in SIMATIC Manager.

## Routes

| Route | Tool | Output | Needs |
|---|---|---|---|
| A (primary) | `tools/s7awl` over `DotNetSiemensPLCToolBoxLibrary` | symbolic AWL with network titles, FB parameters and instance DBs | .NET SDK 8+ |
| B (cross-check) | `rz-libmc7` `mc7dis` via `step7/s7_awl.py` | absolute operands, one instruction per line | a C compiler |

Use Route A for reading. Use Route B as an independent second opinion on important blocks.
Route B has not been run in every environment; if it is not built, say the decode was not cross-checked.

## Steps

1. **Copy** the project folder (or unzip a ZIP) somewhere disposable. Prefer long paths.
2. **Inventory** with the project reader and confirm the block counts:
   `PYTHONPATH=src python -m arc_analyser.step7.s7_project <project> --out out/`
3. **Build once** (see `docs/AWL_RECOVERY.md`, including the Windows notes):
   `dotnet build -c Release -f netstandard2.1` in the library's `LibNoDaveConnectionLibrary`, then
   `dotnet build -c Release -p:S7ToolBoxDll=<dll>` in `tools/s7awl`. Building third-party source runs its
   build scripts: tell the user first and let them run it if they prefer.
4. **Decode** (wrapper or direct):
   `PYTHONPATH=src python -m arc_analyser.step7.s7_dotnet_awl <project> --out awl/ --all`
   or `dotnet s7awl.dll <project.s7p> --all --out awl/`.
   Expect all blocks except VAT tables (a sample of 162 blocks gave 159 files).
5. **Call graph** from the decoded files (the inventory reader's `callgraph.csv` can be empty):
   `PYTHONPATH=src python -m arc_analyser.step7.awl_callgraph awl/ --out callgraph.csv`
   Names with a trailing `?` are callees no decoded file declares (library or missing blocks).
6. **Read** from OB1 and OB100 downward. OB1 gives the real scan order; OB100 the startup
   parameters. Then follow `CALL` / `UC` / `CC` lines into the machine-builder blocks.
7. **Verify** important blocks: compare the block's stored reference list and the xref DB set with
   the decode, and with Route B if built. If they disagree, distrust the decode first.

## Reading AWL

- `U` AND, `UN` AND NOT, `O` OR, `ON` OR NOT, `=` assign, `S` set, `R` reset, `FP`/`FN` rising/falling edge,
  `SE`/`SA`/`SV` on-delay / off-delay / extended pulse timers, `L`/`T` load/transfer, `SPB`/`SPA` jumps,
  `CALL`/`UC`/`CC` calls, `AUF` opens a DB, `BE` block end. (German mnemonics are used in these
  exports; the English equivalents are `A`, `AN`, `O`, `ON`, `OPN`.)
- Parentheses: `U(` and `O(` open a nested expression, `)` closes it. An `O` on its own line separates
  AND groups.
- Symbols appear as `"NAME"` from the symbol table; absolute operands as `M 12.0`, `E 36.6`/`I`, `A`/`Q`.
- A generic FB such as an axis or a push-button block is instantiated many times. Read the FB once, then
  read each call's parameters to see what differs.
- For SINUMERIK, DB bit addresses (for example axis or spindle interface `DBX` bits) follow the Siemens
  PLC interface layout. Check them against the PLC interface manual for the software version rather than
  guessing the meaning.

## Pitfalls

- **8.3 short paths** (`C:\Users\NAME~1\...`): the library reports `folders: 0`, `S7 programs: 0` and
  exports nothing. Use long absolute paths. The wrapper resolves this.
- A project with a nested copy of itself, or a second `ombstx/offline/0000000N` folder, is normal after
  copying. Analyse one block folder at a time (`--folder`).
- The Unix-style env vars (`DOTNET_ROOT`, colon PATH) do not work on Windows without the fixed wrapper.
- Do not count blocks by searching bytes; use `BAUSTEIN.DBF`.
- Unused or unnamed blocks (no symbol, no callers) are probably library leftovers; say "not checked".
- State coverage: which blocks were decoded, which were interface-only, which were skipped.
