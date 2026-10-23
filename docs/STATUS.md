# Status

Verified locally on 2026-10-22. Initial scaffold remains a read-only container
signature inspector. No extraction or Siemens-specific decoding is implemented.

## Environment

- Windows build 10.0.26200; PowerShell 7.6.5; Git 2.46.0.windows.1.
- CPython 3.13.14, 64-bit, available as `python`; meets Python >=3.11.
  The installed `py` launcher reports no registered Python installations.
- Created `.venv` with `python -m venv --without-pip .venv`.
  No packages or software were installed. Use `PYTHONPATH=src` for local execution.
- The project declares setuptools >=68 as its build requirement and no runtime
  dependencies. Global setuptools exists; its version/build compatibility was
  not tested. Editable installation was not attempted.
- Repository contains `src/arc_analyser/cli.py`, tests, docs, and workflow prompts.
  Initial Git status was clean on main, tracking origin/main, at 6211322.
  Remote freshness was not checked; this session previously could not write
  `.git/FETCH_HEAD`.

## Installed software evidence

Registry entries identify STEP 7 V5.7 SP3, SINUMERIK Add-on for STEP 7,
TIA Portal V13/V17/V20, SINUMERIK Commissioning 4.8.4,
SinuTrain 840D sl 4.93 HF5, SINUCOM PCIN, and ProSave V20.
Access MyMachine 4.7 and AMMEditor executables exist. DriveMonitor,
NCVar Selector, and 808D/828D toolbox directories also exist; directory presence
alone does not establish their working state or version.

7-Zip 26.02 and WinRAR 7.01 are registered and their executables exist under
Program Files, although neither command is on PATH. Windows `tar` is available
(bsdtar/libarchive 3.8.9). A bundled 7z.exe also exists under SINUMERIK
Commissioning. Siemens applications were not launched, licensed operation was
not verified, and no archive conversion capability is claimed from this inventory.
No controllers were accessed.

## Verified format coverage

| Result | Evidence used | Limits |
| --- | --- | --- |
| zip-compatible | Python zipfile.is_zipfile | Container recognition, not full integrity/content validation |
| tar-compatible | ustar marker at offset 257 | Signature only; no checksum or payload validation |
| 7z-compatible | Six-byte 7z signature | Signature only; no integrity validation |
| rar-compatible | Complete RAR4 or RAR5 signature | Signature only; no integrity validation |
| unknown | None of the above | Does not imply corrupt or invalid archive |

All results report `extraction_supported: false`. Extension alone is never used
as evidence. These labels do not identify controller generation or NC/PLC/drive
content. Siemens proprietary/binary or text archives, combined commissioning
archives, and controller-specific Power Line/Solution Line/828D/ONE variants
have no dedicated identification or decoding support. A Siemens archive using
one of the generic containers can only receive that generic label.
No real archive was inspected: no sample `.arc` files were found in the project's
`local_data/` or `raw_archives/` locations. No machine data was uploaded.

## Tests and fixes

- Initial `python -m pytest -q` could not run: pytest is not installed.
- Converted the two pytest fixtures/tests to stdlib unittest and expanded coverage
  to 11 tests, requiring no third-party test dependency.
- Fixed false RAR recognition for truncated/invalid signature suffixes.
- CLI now returns exit code 2 with a concise error instead of a traceback on
  file-access failures. Added return annotations.
- Tests cover synthetic ZIP (including empty), ustar TAR, 7z and RAR signatures,
  unknown/empty input, incomplete RAR signatures, missing paths, directories,
  CLI JSON/error behavior, unchanged fixture hashes, and no extracted files.
- First unittest attempt failed on sandbox temporary-directory permissions.
  Rerunning with TEMP/TMP pointing to the permitted Windows Temp folder passed:
  **11 tests, OK**. Synthetic 7z/RAR signatures do not establish valid payloads.

Reproduce without installing packages (PowerShell, repository root):

```powershell
$env:PYTHONPATH = 'src'
# Needed in this restricted session; normal Windows shells may not need these.
$env:TEMP = 'C:\Users\bhelcnc\AppData\Local\Temp'
$env:TMP = $env:TEMP
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
```

## Recommended next steps

1. Supply an offline copy of a representative archive in gitignored `local_data/`.
   Inspect that copy read-only; keep original backups untouched. Do not commit
   raw headers, filenames, or machine-derived reports without confidentiality review.
2. Establish the exact archive variant from local evidence, then investigate
   the installed Siemens utilities' documented offline capabilities for that variant.
   Installation presence is not proof of a usable extraction API.
3. Before implementing extraction, test rejection of traversal/absolute paths,
   symlinks, oversized entries, archive bombs, and output outside an isolated folder.
4. Add variant-specific synthetic/sanitized fixtures before claiming Siemens
   support, then implement NC/PLC/drive/machine-data classification.
5. Ask before installing packages or software. Keep all work offline from CNC
   machines and do not restore archives or execute extracted programs.

## Delivery state

`git diff --check` passed. Staging the four source/test/documentation files failed
because the session cannot create `.git/index.lock` (Permission denied).
No commit was created and nothing was pushed. Commit locally after review:

```powershell
git add src/arc_analyser/cli.py tests/test_cli.py README.md docs/STATUS.md
git commit -m "Verify Windows environment and strengthen archive inspection tests"
```

## Offline ZIP metadata inspection - 2026-10-22

This entry supersedes the earlier statement that no sample was available.
Git status was initially clean. The local-data directory and ZIP/ARC extensions
were confirmed ignored; no backup or local-data report was tracked.
Exactly one archive was present directly in the designated local-data directory.
No wider filesystem search was performed.

The existing read-only inspector identified a ZIP-compatible container, and
Python zipfile successfully read its central directory. Entry metadata uses
stored and deflate compression methods; no entries advertise encryption.
Metadata-only checks found no flagged absolute/parent-traversal paths, symlinks,
duplicate or Windows case-colliding paths, or configured size/ratio concerns.
Inspection was bounded to 100,000 entries and a 64 MiB central directory;
warning thresholds were 1 GiB per entry, 10 GiB aggregate declared size, and
compression ratios over 1,000. These checks do not certify archive safety or
payload integrity, and do not verify local-header consistency or CRCs.

Filename evidence suggests possible PLC-related and NC/configuration material.
These are inferences only, not confirmed content. Drive/machine-data categories
and a specific Siemens/controller archive variant were not established.
Detailed paths, hierarchy, entry metadata, size and SHA-256 were retained only
in an ignored local report. Before/after hashes matched. No entry payload was
read or decompressed; no extraction, testzip, restore, Siemens application,
controller connection, upload, installation, staging, commit or push occurred.

The existing standard-library suite passed again: **11 tests, OK**.
Next safe step: review the confidential local inventory on this PC and agree on
an exact offline identification plan. Any payload inspection or extraction would
be a separate task requiring explicit scope; generic ZIP recognition alone does
not demonstrate Siemens archive decoding support.

## Inventory-led identification plan - 2026-10-22

The single selected ZIP copy matched the previous local SHA-256 baseline before
inventory analysis. Local-data and report ignore rules were confirmed; no tracked
backup/report risk was found. Only existing inventory metadata and installed help
were analyzed; no member payload was opened or decompressed.

No Siemens parser or verified Siemens SDK is installed in this repository.
No Siemens Codex/VS Code skill has been established. A skill is not a decoder:
actual identification requires payload evidence matched to documented syntax or
a verified offline parser, with separate approval before member reads.

Primary filename hypotheses (confidence refers to names, never confirmed content):

| Category | Confidence | Evidence and limits |
| --- | --- | --- |
| PLC | High for source/project-like names | Several PLC source/project extensions coexist; valid syntax and project schema remain unverified |
| Configuration | Medium | Structured/configuration extensions; not proof of NC machine data |
| NC | Unsupported | No category-specific hit in the conservative inventory rules; absence is not proved |
| Drive | Unsupported | No category-specific hit; absence is not proved |
| HMI | Unsupported | No category-specific hit; absence is not proved |
| Unknown | Low | Most files have database/index or other opaque extensions; no schemas decoded |

This suggests a STEP 7 project-like ZIP, not a confirmed controller archive
variant. Earlier generic NC/configuration grouping should not be interpreted as
positive NC evidence: generic configuration files are ambiguous.

Installed documentation findings:

- STEP 7 readme documents standard ZIP archive/retrieval support. Its getting-
  started manual describes Archive and Print commands. This is documentary
  evidence only, not a tested project-open or export operation.
- Installed S7-SCL manual describes ASCII sources and import/export, plus standard
  editor source creation. No exact compiled-block-to-source workflow was verified.
- Installed SinuTrain operating manual describes binary and punched-tape archives,
  recommending punched-tape for external processing. This does not identify the
  selected ZIP or supply a binary decoding schema.
- Commissioning ATW guideline was searched without finding applicable archive-
  format evidence. Add-on help candidates exist but ownership/content and archive
  capabilities were not established. Compiled help was not decoded; no utility
  or SDK API was verified. Search coverage is limited, not proof of nonexistence.

Private report contains member-level groups, documentation locations/page evidence,
confidence/reasons, and a shortlist of five nonempty small entries: likely PLC
source, structured metadata, notes, and a possibly binary project descriptor.
No payload classification has been confirmed. All details stay ignored locally.

Proposed subsequent approved inspection only: recheck hash and exact allowlist;
maximum five entries, 64 KiB decompressed per entry, 256 KiB aggregate, compression
ratio at most 100, 100,000 inventory entries, and 64 MiB central-directory metadata.
Reject links, traversal/absolute or ambiguous Windows paths, encryption, unsupported
compression, duplicate names, and size inconsistencies. Stream at most 4 KiB chunks
in a worker capped at 256 MiB and ten seconds with explicit actual-output counters;
abort on limit or integrity failure. No extraction, nested archive processing,
restore, or archive-provided filesystem paths. Generated private reports only in
a new ignored local output directory, with confinement/reparse checks. Strict text
encoding/BOM handling; binary, ambiguous encoding or unknown data stays unknown,
with no guessed schema. Escape all output and do not render active content.
No payload reader or extraction implementation was added in this run.

Tests: existing standard-library suite passed, **11 tests, OK**. No dependency
installation, network access, Siemens application launch, controller access,
staging, commit or push. Approval is required before reading any shortlisted
payload or using proprietary utilities. Exact Siemens format remains unresolved.

## Approved bounded payload classification - 2026-10-22

The prior private allowlist and unchanged archive baseline were verified before
reading. Git ignore protection for private data and reports was confirmed; no
tracked backup risk was present. Only the five previously shortlisted members
were inspected. Exact names, hashes and member-level results remain exclusively
in a new ignored local report directory. No raw member files were written.

Confirmed observations:

- Two members contain readable text with STEP 7-style block declarations, a body
  start marker, and corresponding block-end markers. Readable PLC source text
  was therefore observed, beyond filename clues. This is syntax-marker evidence,
  not full grammar/type checking, compilation, verified project compatibility,
  confirmation of controller-loaded logic, or proprietary binary decoding.
- One member is well-formed structured XML metadata with no DTD/entities; its
  configuration meaning and correctness have not been verified.
- Two members remain binary/unknown under strict supported text decoding.
  Their schemas and meanings were not guessed. No NC or drive payload content
  was established by these five reads.

Added an allowlisted in-memory reader supporting only stored/raw-deflate ZIP
members, with bounded decompressor output and CRC/actual-size checks. It rejects
unsafe or colliding paths, special/link entries, encrypted/unsupported entries,
unsupported data descriptors, mismatched headers, overlapping selected compressed
ranges, and recognizable nested archives. It does not implement extraction or
Siemens-specific parsing. Unknown nested formats cannot be identified universally;
no nested content is recursively opened.

Limits enforced: five members, 64 KiB each, 256 KiB aggregate, compression ratio
at most 100, 100,000 inventory entries, 64 MiB central-directory metadata, and
chunks/output batches at most 4 KiB. A Windows Job Object enforces 256 MiB process
and job committed-memory limits and a single-process limit; the parent enforces
a ten-second wall-clock timeout with kill/wait on expiry. Memory configuration
was queried back and a synthetic 300 MiB allocation failed under the cap. These
Windows memory limits constrain committed memory, not a sampling-based RSS check.
No additional member was read after the five authorized reads.

The archive's before/after hashes matched the private baseline. The original
backup was never accessed. No extraction, project opening, script execution from
the archive, Siemens application launch, network operation, installation, restore,
controller access, staging, commit or push occurred.

Validation: **30 tests passed**, comprising the 11 existing tests and 19 new
synthetic tests for source/text/binary/structured classification, malformed ZIPs,
paths/collisions/links, encryption and unsupported compression, header/CRC errors,
decompression/aggregate/ratio/metadata limits, baseline/allowlist checks, nested
archive rejection, unchanged input, worker timeout handling and Windows memory
limit enforcement. One initial XML-classification test found a self-closing-tag
recognition defect; it was fixed before any real payload inspection.

Remaining limitations: no Siemens parser or verified Siemens SDK is installed in
this repository; opaque binary formats and complete project semantics remain
unresolved. Synthetic test evidence does not imply general Siemens archive support.
Recommended next step is local review of these limited findings, followed by a
separately scoped authorization if further source analysis is wanted. No general
extraction or subsequent adapter phase was started. Safe code, tests and this
sanitized documentation are ready for review; private reports must remain ignored.

## Two-source structure analysis - 2026-10-22

Reinspection was limited to the two previously verified source-text members.
The original private baseline, exact two-member subset, archive selection,
ignore protection and worker confinement were verified before reads. The same
bounded reader retained all ZIP safety, size, ratio, chunk, memory and deadline
checks. Archive before/after SHA-256 matched the prior private baseline. No other
member payload was opened, and no raw member files were written to disk.

Verified lexical structure observations:

| Clearly delimited block type | Count |
| --- | ---: |
| DB | 3 |
| FC | 1 |
| OB | 0 |
| FB | 0 |
| UDT | 0 |

These counts cover only the two authorized sources; zero does not imply absence
from the project. Four declarations have matching delimiters and required body
markers under the conservative recognizer. No incomplete/tentative block candidate
was returned. Explicit identifiers, any symbolic declaration names, declaration
sections and variable declarations, source line ranges, reference locations and
warnings are retained in the existing ignored private report location only.

There are 24 explicit DB-address reference occurrences, not necessarily 24 unique
targets. No explicit CALL, UC or CC edge was recognized. Two invocation-like
expressions remain unresolved and are not treated as calls. Two STRUCT headings
and one VAR_INPUT heading were observed. Comments and quoted values do not
independently create executable-reference edges. Quoted symbolic targets are
accepted only in explicit declaration/call syntax contexts.

Added a conservative lexical structure recognizer and a narrower worker mode
that derives exactly two sources from the previous private classification report
and original allowlist. No new source format, archive member or binary schema
was assumed. Recognition covers common block/declaration delimiters and explicit
references; it does not constitute full STEP 7 grammar/type checking, compilation,
symbol resolution, runtime reachability, machine-behavior analysis or verification
of controller-loaded code. Invocation-like syntax, indirect calls, nested or
ambiguous declarations and unrecognized attributes remain unsupported or warned.

Validation: **42 tests passed** (30 prior tests plus 12 source-structure tests).
New synthetic coverage includes OB/FB/FC/DB/UDT declarations, multiline interfaces,
explicit calls/instances/address/type references, comment/string false positives,
malformed/incomplete syntax, BOM/encoding handling, byte bounds, unchanged input,
and a confined-worker test with a deliberately corrupt excluded member that is
not opened. Existing ZIP/resource-limit tests also passed. No dependencies were
installed. The private report contains no raw extracted payload file.

The two sources are sufficient for this partial block/declaration and explicit-
reference inventory, but insufficient for meaningful project-wide PLC logic or
call mapping. Broader source access or Siemens tools require a separate approved
scope. No further archive phase, general extraction, project opening, execution,
controller access, restore, data upload, commit or push was performed. Safe reader,
worker, lexical recognizer, synthetic tests and sanitized status changes are ready
for review; private reports must remain ignored.

## Approved offline ZIP batch execution - 2026-10-23

The user explicitly approved processing the complete reviewed batch under the
previously stated limits. After reconnecting, the implementation and original
42-test suite were verified present, and the expanded suite passed: **64 tests**.
A fresh metadata-only preflight and the private baseline checks matched the
reviewed archive before a baseline-bound local approval record was created.

Preflight: 403 entries, comprising 356 files and 47 directories. Declared output
was 8,785,752 bytes; the largest file was 1,719,783 bytes and the maximum declared
compression ratio was 98:1. No blocking metadata concern was found. Seven names
had potentially active/shortcut extensions; no such content was executed.
Filename hypotheses were kept distinct from verified payload classification.

Execution was approved and actually performed in one offline batch. **356 files
were copied, totaling 8,785,752 bytes**, into a newly created ignored run directory
using generated IDs and a confidential manifest. Directory hierarchy was retained
as manifest metadata rather than trusted filesystem destinations. Every file's
CRC and actual size was verified. All final output files matched manifest sizes,
and archive SHA-256 before/after matched the private baseline. No temporary pending
run remained. The original backup was never accessed or modified.

| Local classification | Files |
| --- | ---: |
| Readable STEP 7-style source text | 5 |
| Structured metadata | 1 |
| Other verified text, including empty text | 52 |
| Binary/unknown or beyond bounded classification budget | 298 |

Limited lexical source analysis observed 14 clearly delimited blocks: 6 DB,
5 OB, 1 FB and 2 FC, plus 33 explicit reference occurrences. These are syntax
observations only, not complete symbol resolution, controller-loaded program
verification, compilation, runtime behavior, or a complete PLC logic map.
No proprietary binary database, NC, drive or HMI format was labeled decoded.
No universal Siemens ARC parser or verified Siemens SDK is established here.

The reusable CLI defaults to dry-run. Execution requires both an explicit opt-in
and a private approval record matching the baseline and budgets. Metadata is
inventoried in one central-directory pass; each file uses a separate confined
worker. Limits remain 64 MiB per file, 512 MiB aggregate output, ratio <=100,
100,000 entries, 64 MiB central-directory metadata, 32 MiB report allowance,
64 MiB disk reserve, 256 MiB worker committed memory, ten seconds per worker,
and 600 seconds total by default. Recognized nested archives, unsupported methods,
encryption, unsafe paths/links/collisions and inconsistent headers fail closed.
No automatic safe-skip policy is used. Caught failures roll back only the current
run; final directories are published after whole-run verification and never
reused or overwritten. Hard termination can leave an unpublished pending folder.

Tests cover dry-run, approval gates, streaming limits, unsafe paths/collisions,
links/reparse points, bombs, output confinement, interruptions and rollback,
CRC errors, unsupported entries, fresh-run/no-overwrite behavior, disk/runtime
budgets, classification, and unchanged input, alongside prior reader/parser tests.
The workflow guide documents commands and limitations. All raw copies, original
member names, approval records, hashes, source identifiers and manifests remain
local and ignored. No installation, Siemens application launch, executable
payload execution, CNC/PLC connection, restore, upload, commit or push occurred.

Recommended next step: review the local text/source inventory and choose a
separately scoped format-specific adapter only where documentation and fixtures
support it. Opaque binaries remain undecoded. Safe source, synthetic tests and
sanitized documentation are ready for review; private outputs must stay ignored.
