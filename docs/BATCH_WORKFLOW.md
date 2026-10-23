# Offline batch ZIP workflow

This workflow copies a verified local ZIP container. It is not a universal
Siemens ARC decoder. Proprietary binary formats remain undecoded.

Run from the repository root with the existing virtual environment:

```powershell
$env:PYTHONPATH = (Join-Path (Get-Location) 'src')
.\.venv\Scripts\python.exe -m arc_analyser.batch --plan local_data/selected_plan.json --output-root local_data
```

Use the existing private identification-plan filename in place of selected_plan.
Dry-run is the default and reads only ZIP metadata. It verifies the private
SHA-256 baseline, inventory, path/link/collision safety, compression, headers,
size/ratio limits and available disk space. Unsafe entries block the whole ZIP.
No implicit safe-skip policy is implemented.

After explicit user approval in Codex, record that decision in an ignored local
JSON approval file. It must contain approved=true, the scope string
`batch-container-copy-and-local-classification`, sha256 matching the private
baseline, and budgets exactly matching the reviewed preflight. Approval is not
created automatically by the CLI. Never commit the record or its private hash.

One command then processes all eligible members without manual selection:

```powershell
.\.venv\Scripts\python.exe -m arc_analyser.batch --plan local_data/selected_plan.json --output-root local_data --execute --approval-file local_data/batch_approval.json
```

Use the actual private approval filename. Both --execute and a matching approval
record are required. Never invoke internal worker entry points manually.

Default budgets: 64 MiB per member, 512 MiB total raw output, ratio <=100,
100,000 entries, 64 MiB central-directory metadata, 32 MiB report allowance and
64 MiB free-disk reserve. Each member worker has a 256 MiB committed-memory limit
and ten-second deadline. Total runtime defaults to 600 seconds; a finite value
of 1-3600 seconds can be selected with --runtime-seconds and must match approval.
Byte/ratio limits cannot be raised through this CLI.

Payloads stream in chunks <=4 KiB to exclusively created temporary files. CRC,
actual size, counters and final archive hash are verified. Outputs use generated
member IDs and a private manifest rather than archive paths. A fresh ignored
batch directory is published by rename only after the whole run succeeds.
Caught errors/interruption roll back that run's temporary output. Older runs
are never overwritten or cleaned up. Hard process termination or power loss can
leave an ignored .pending directory; it is incomplete and never reused.

Classification retains at most 64 KiB in memory. Complete files within that
budget can receive strict text/XML classification and limited STEP 7 lexical
block/reference inventories. Larger or unsupported binary formats are copied
with integrity checks and remain binary/unknown. XML is never rendered. Nothing
is executed, restored, uploaded, or opened in Siemens applications.

Nested archive names and recognized nested-container signatures are rejected
with whole-run rollback; unknown nesting cannot be identified universally.
Unsupported methods, encryption, unsafe paths, links, inconsistent metadata and
resource overruns fail closed. Keep input/output folders exclusive to the task
while running. Future Siemens-specific adapters require separately verified
formats and scope.
