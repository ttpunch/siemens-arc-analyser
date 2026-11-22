---
name: tia-consistency-diagnosis
description: Use when TIA Portal blocks report IsConsistent=False.
version: 1.0.0
license: MIT
metadata:
  hermes:
    tags: [tia-portal, openness, plc, consistency, compile, sinumerik, read-only]
---

# TIA consistency diagnosis

Answer the question *"why is this block inconsistent?"* for a TIA Portal project.

TIA exposes `PlcBlock.IsConsistent` and **never exposes the reason**. The authoritative reason only
appears in compiler messages, which require an actual compile. So work the cheapest evidence first:

| Tier | What | Writes to the project? |
|---|---|---|
| **0** | the project's own conversion log and fingerprint list | no |
| **1** | Openness enumeration + attempted export of every block | no |
| **2** | compiler messages from a real compile | **yes** |

Nothing in tiers 0 and 1 connects to a controller, restores data or executes anything.

## When to use

* a block, group or whole PLC shows `IsConsistent = False`
* a project was migrated between TIA versions or toolboxes and blocks will not compile
* you need to know whether an inconsistency is a defect or just *compile pending*
* before any "compile all" decision, so the blast radius is known first

## Tier 0 — read the project's own history (cheapest, often conclusive)

Read the project folder over the filesystem, read-only:

```
<project>\Logs\ConversionLog_<from>_to_<to>.xml   upgrade / conversion protocol
<project>\<name>.ap20                             zipped project container
<project>\XRef\XRef.db                            cross-reference database
<project>\Vci\                                   version-control interface workspace
<project>.backup\                                 previous project states, timestamped
```

`ConversionLog_*.xml` is the highest-value file. Search it for:

- `Upgrade started` and `Project upgraded from Version: <n>` — proves the project was migrated, and from
  which version (`1800.100.4201.1` = V18.0.1, `2000.…` = V20).
- `Package container '<product>' was deleted` — which products/toolboxes the upgrade retired
  (e.g. `Siemens.MC.Sinumerik.Toolbox:18.00.01.01` deleted = the V18 SINUMERIK toolbox was replaced).
- **`Not invalidating fingerprints for protected object: <Name>[<Number>]`** — the key line. A fingerprint
  is the integrity hash TIA keeps for a know-how-protected object. The upgrader deliberately does *not*
  invalidate it across a version change, so afterwards those objects no longer match their compiled state
  and report `IsConsistent = False`.

Cross-reference that name list against the inconsistent set. On a verified 244-block SINUMERIK ONE project
upgraded V18.0.1 → V20, 122 objects were left with preserved fingerprints and **15 of them were
inconsistent** (10 `LBP_*` + 5 `LSUD_*`) — those 15 are explained by the conversion itself. The remaining
17 (OB1/OB100, the machine-builder FC set, the axis FBs, two `LSinuMCPs`, two F-blocks) were **not**
explained by it and have to be accounted for separately, usually as blocks edited or regenerated after
the upgrade.

Do not claim the inconsistency "propagated up the call tree". TIA marks a caller inconsistent when a
callee's **interface** changes, not when only the callee's compiled state was rebuilt. Verified
counter-example: `AxisManagement` (FB300) is consistent while calling `LinearAxis`, `RotaryAxis` and
`SpindleAxis`, all three inconsistent. Group the blocks and explain each group on its own evidence.

Evidence rule: quote the log lines. "Fingerprint not invalidated for protected object X" is Siemens'
statement, not an inference.

## Tier 1 — read-only triage

Use the Openness probe (`scripts/TiaProbe.cs`) in the interactive Windows session, then attempt a
**read-only export of every block**:

```
TiaProbe.exe --blocks --export "C:\Users\<user>\tiaexport" > export_result.txt
```

The export attempt is an **inconsistency oracle**: TIA refuses to export a block whose source and
compiled state disagree, so a block that fails `PlcBlock.Export` with
`EngineeringTargetInvocationException` is either inconsistent or auto-generated. Verified on the same
244-block project: all 32 inconsistent blocks failed export, plus one auto-generated failsafe runtime OB.

Then triage:

```
python scripts/consistency_triage.py --inventory result.txt --export-log export_result.txt \
    --xml-dir tiaexport --out report.md
```

What it establishes, without touching the project:

- which blocks are inconsistent, and how many of those are also **know-how protected** (their logic is
  unreadable — do not attempt to defeat protection)
- the **call graph** of the exported blocks: who calls whom, which inconsistent blocks are reached from
  consistent code, which have no visible caller because their caller is inconsistent too. Treat the graph
  as a map, not as a cause ranking — invalidation direction is interface-driven (see Tier 0)
- **header-version clusters**, which separate vendor library blocks from machine-builder code and point at
  which library generation a group came from

Tier 1 cannot tell you *why* — it narrows *where*. Say so in the report.

## Tier 2 — compiler messages (authoritative, mutating)

`IsConsistent = False` is cleared by compiling, and the compile returns `CompilerResult.Messages`
(`Path`, `State`, `Message`) with the real reasons: unresolved interface, missing dependency, syntax
error, F-runtime missing, version downgrade, prohibited structural change.

This **writes compile artifacts into the project**. Therefore, in order:

1. Confirm the exact project path from the probe — never assume it.
2. Archive the project first (`Project.Archive()` → `.zap20`) and record path and size.
3. Get explicit approval for the compile, and state the scope (whole PLC, group, or one block).
4. Compile the smallest scope that reproduces the message, e.g. one block via `ICompilable`:

```csharp
var compilable = block.GetService<ICompilable>();
var result = compilable.Compile();
foreach (var m in result.Messages) Console.WriteLine($"{m.State}|{m.Path}|{m.Message}");
```

5. Re-read `IsConsistent` afterwards and report exactly what changed.

Never compile a project that has not been archived first. Never compile a block of a failsafe (F) program
as part of a general sweep — F blocks follow the safety workflow and need their own acceptance.

## Reporting rules

- Separate **evidence** (counts, classes, call edges, header versions, log lines) from **interpretation**
  (probable root cause). Never present a hypothesis as a TIA-documented fact.
- Never claim a block is "broken": `IsConsistent = False` most often means *compile pending*, not defective.
- Name blocks by group + class + number so they can be found in the TIA tree.

## Pitfalls

- `TiaPortal.GetProcesses()` returns 0 from an SSH session: Windows OpenSSH runs in **session 0**, Portal
  runs in **session 1**, and Openness discovers instances per session. Launch the probe inside the
  interactive session with a scheduled task using `<LogonType>InteractiveToken</LogonType>`.
- A compiled probe needs `Siemens.Engineering*.dll` next to the executable, not just at compile time.
- A read-only export of a 244-block project takes ~90 s and produces tens of MB. Stream it back with
  Windows `tar.exe -Cf -` over SSH rather than `scp` — a Windows user name containing a space breaks
  scp's remote path parsing.
- Do not infer block type from the block name; symbolic names carry no type. Use the runtime class from
  `GetType().Name` (`OB`, `FB`, `FC`, `GlobalDB`, `InstanceDB`).
- Protected + inconsistent is a normal combination: a vendor library block whose interface moved.
- `IsConsistent` is per block; the project as a whole has no single consistency flag, so always report the
  denominator (e.g. 32 of 244).

## Files

- `scripts/TiaProbe.cs` — read-only Openness probe: list Portal instances, enumerate devices/PLCs/block
  groups, optionally export every block. Compile with `csc.exe` against the installed
  `PublicAPI\V<version>\Siemens.Engineering.dll`.
- `scripts/consistency_triage.py` — turns the probe's inventory, export log and exported XML into a
  markdown report. Standard library only, read-only.
