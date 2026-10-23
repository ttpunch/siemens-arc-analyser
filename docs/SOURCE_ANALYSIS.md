# Read-only PLC source analysis

This stage consumes the existing approved extracted run and its manifest. It
does not open ZIPs, original backups, binary payloads, XML payloads, Siemens
applications, or controllers. Only the five manifest records already classified
as readable source are eligible. Any different count requires a separate scope.

Run from the repository root, without installing packages:

```powershell
$env:PYTHONPATH = (Join-Path (Get-Location) 'src')
.\.venv\Scripts\python.exe -m arc_analyser.plc_analysis --run-locator local_data/completed_batch_locator.json
```

Alternatively, pass `--run` with the approved private run directory. Do not pass
both forms. Inputs remain read-only; reports are written into a new generated
ignored directory under the local output root. Existing reports are never
overwritten. The program prints anonymized numeric coverage only, not input IDs,
member names, code, symbols, paths, addresses or hashes. All detailed JSON and
Markdown reports are confidential and must remain ignored.

## Validation and bounds

The command requires a complete, explicitly approved manifest and its recorded
baseline agreement. It does not recompute the ZIP hash, because opening archives
is outside this source-only scope. It selects records by prior classification and
validates generated file IDs, unique mappings, sizes and CRCs against that
manifest. Archive-provided names never become filesystem destinations. Ancestor
symlinks/reparse points and path escapes are rejected. Only selected source paths
are opened or statted; excluded payload paths are not inspected.

The worker is capped at 256 MiB committed memory and ten seconds. Inputs are
limited to 64 KiB per source and 256 KiB combined, with <=4 KiB reads; manifest
metadata is limited to 32 MiB and worker reports to 16 MiB. Strict UTF-8, or
BOM-marked UTF-8/16/32, are supported. Other encodings stay unknown; no guessing.
Selected input SHA-256 values and manifest bytes are compared before/after.
Keep the input/output folders exclusive to the analysis while it runs; hostile
concurrent filesystem changes are not a supported operating model.

## Recognized observations

- Explicit OB, FB, FC, DB and UDT-style declarations, identifiers, line ranges,
  matching end markers, common declaration headings and name/type declarations.
- Multiline declarations, explicit AT addresses, matching lexical boundaries,
  comments, nested block comments and quoted values. Nested/ambiguous declaration
  structures and unsupported attributes are warned rather than silently decoded.
- Explicit CALL/UC/CC, instance operands, qualified DB references and direct DB
  open instructions. Occurrences and unique block-level references are distinct.
- Exact-spelling symbolic calls or FC invocation syntax resolve only against a
  single compatible declaration in these readable sources. Duplicate definitions
  block resolution. Numeric references outside the scope remain explicitly
  external mentions, not evidence that the missing blocks are available.
- Supported absolute I/Q/M addresses, numeric DB offsets, relative DB offsets and
  timer/counter mentions. Symbolic/indexed DB offsets stay unresolved. Relative
  DB offsets are not bound to a guessed active DB context.

No instruction is evaluated or executed. A reference graph expresses lexical
relationships, not runtime order, reachability or controller-loaded logic.
Absolute I/Q mentions do not establish physical terminals, wiring, signal meaning
or read/write semantics. Unsupported pointer syntax, indirect calls and FB
instance invocation are not inferred. Local symbols that resemble addresses are
excluded from the supported absolute-address inventory.

## Reports and determinism

Reports include per-source block/declaration inventories, variables and supported
address mentions, reference occurrences, unique directed edges, duplicate
definitions, unresolved items and warnings, source coverage, and integrity checks.
Unresolved counts are unique diagnostic `(line, reason)` pairs per source, not
counts of missing PLC blocks. Unique references are keyed by origin block,
relationship and written target; they do not count each different byte address.
Body-line counts explicitly record that executable semantics were not analyzed.

The JSON/Markdown contents are deterministic for unchanged sources, manifest and
parser version. Generated output-directory names differ to avoid overwrites.
Markdown details are enclosed in dynamic-length code fences to keep private
identifiers inert. No source text is rendered as active HTML or executed.

This is a partial lexical recognizer, not full Siemens parsing, decompilation,
project loading or a symbol-table export. Binary-only logic, hardware mapping,
external symbol tables, missing blocks and runtime behavior cannot be established
from these five files. Any expansion needs explicit approval and an independently
verified format/tool workflow. Review this stage's coverage before a next phase.
