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
- Symbolic call targets are checked for compatible declaration kinds; a DB symbol
  cannot become a callable block merely because its spelling matches. Quoted
  keyword-like symbols retain their explicit symbolic identity. Invocation
  delimiters must balance before an FC invocation gains a resolved edge.
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

### Separate reference evidence levels

Schema version 2 adds a qualified-DB inventory and an unresolved-reference ledger.
Each ledger row records its source location, origin block where established,
relationship, explicit target when present, evidence level and reason. Indirect
expressions are retained privately without invented targets. Unsupported
identifier/parenthesis syntax is labeled an invocation candidate, not asserted
to be an executable call. Generic syntax diagnostics are retained separately.

Four different questions must not be conflated:

1. **Block target:** is there a unique compatible declaration in these files?
   An unavailable declaration is not a proven missing implementation.
2. **Member identity:** does a simple symbolic DB member exactly match one
   explicitly parsed field of a unique DB? Duplicate names, ambiguous declaration
   scope, absent fields and complex/indexed paths remain unestablished. No external
   symbol table, case equivalence or flattened nested layout is assumed.
3. **Absolute address:** is a numeric address written in the source? A matched
   field does not imply a byte/bit offset. Packing, alignment and FB instance
   layout are not computed. Explicit CALL and instance operands can identify two
   separate targets without establishing a valid instance layout or runtime call.
4. **Syntax diagnostics:** which distinct source-line/reason pairs remain? These
   are neither occurrence counts nor counts of unavailable blocks.

The legacy relationship label `explicit_DB_address` denotes a qualified DB
reference; it does not certify a numeric address. The attached evidence records
whether an address is explicitly numeric, a symbolic field is matched, or a path
is unresolved. Supported field references no longer receive a misleading generic
"no numeric offset" diagnostic; their offset uncertainty remains explicit in the
DB inventory. Repeated uses and references sharing a line are counted separately
as occurrences even when a diagnostic is de-duplicated.

The current local review establishes 21 symbolic member-use identities among 24
qualified DB occurrences; three member-use identities remain unestablished. All
24 absolute offsets remain unknown. Block target resolution remains 26 of 35
occurrences within the readable scope and nine outside it. This does not add any
missing block implementation. Syntax diagnostic locations changed from 37 to 20;
the change reflects supported member identity evidence, not 17 recovered blocks.
Metric definitions and level-specific counts are included in private reports.

The [format-adapter plan](FORMAT_ADAPTER_PLAN.md) separates implemented lexical
analysis, documented export capabilities, metadata hypotheses and unverified
adapters. No speculative binary decoder or Siemens SDK was added.

The JSON/Markdown contents are deterministic for unchanged sources, manifest and
parser version. Generated output-directory names differ to avoid overwrites.
Markdown details are enclosed in dynamic-length code fences to keep private
identifiers inert. No source text is rendered as active HTML or executed.

This is a partial lexical recognizer, not full Siemens parsing, decompilation,
project loading or a symbol-table export. Binary-only logic, hardware mapping,
external symbol tables, missing blocks and runtime behavior cannot be established
from these five files. Any expansion needs explicit approval and an independently
verified format/tool workflow. Review this stage's coverage before a next phase.

## Three-member investigation — 2026-10-23

Revalidated the five-source manifest, prior private report schema, metrics and
input hashes. Each of the three unestablished uses has a unique, clearly delimited
DB declaration. All three are simple symbolic qualifications. None matches a
parsed field, even by case alone, and the exact member token is absent from its
DB declaration region after comments and literals are removed. The corresponding
DB declarations have no parser warnings. These are unavailable field identities
in the supplied declaration evidence, not demonstrated nested/indexed syntax,
duplicate ambiguity, parser omissions, missing implementations or symbol mappings.

No resolution grammar was changed. The private `DB_member_diagnoses` ledger records
locations, candidate declarations, parsed fields, exact declaration-token matches,
reasons and next evidence. A token in a type/initializer is only a review lead,
never field proof. A fresh ignored JSON/Markdown report contains the three-row
investigation, without disclosing its expressions or identifiers here.

Before/after: **21/24** member identities established and **3/24** unestablished;
**24/24** absolute offsets unknown; **26/35** block-reference occurrences resolved
within readable scope and **9/35** outside. Unique block references remain **12**,
graph edges **11**, and diagnostic locations **20**. These metrics are separate.

Validation: **122 tests passed**, including seven new diagnostic regressions.
Two bounded source-only runs produced identical reports. Source/manifest hashes
match the previous report and remain unchanged. Existing worker limits remain
256 MiB committed memory, ten seconds, 64 KiB per source, 256 KiB aggregate and
reads of at most 4 KiB. No archive or excluded payload access was required.

The next evidence needed is an authoritative matching DB source declaration or
explicit symbol/export mapping. Obtaining anything outside these five sources
requires separate approval. Absolute layout and runtime semantics remain unknown.
