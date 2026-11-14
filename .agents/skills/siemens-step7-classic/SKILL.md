---
name: siemens-step7-classic
description: Inspect a Siemens SIMATIC Manager STEP 7 Classic project offline. Use for S7 blocks, DB declarations, linked logic, reference data, I/O Assignment and candidate spare inputs in Classic projects.
---

# STEP 7 Classic offline inspection

Confirm the intended `.s7p`, station, CPU and S7 Program. SIMATIC Manager
(`S7tgtopx.exe`) is separate from TIA Portal; do not point TIA Openness at a
Classic project. Prefer a matching export or verified Classic reader for bulk
inspection. A COM registration or unsuccessful active-object probe does not
prove whether a supported reader works.

For UI access, use the host's supported desktop controls. If Manager is closed,
launch the installed application and refresh window discovery after startup.
Confirm the restored project identity; open the verified project path if
needed. A background process without a usable window is a startup blocker,
not proof that the project is open. Dismiss routine informational notices when
authorized; leave security/permission prompts to the user.

## Reference Data and Assignment

1. Select the intended **CPU → S7 Program → Blocks**.
2. Open **Options → Reference Data → Display**. If fresh data are requested
   and the project may regenerate its offline references, choose
   **Regenerated / Regenerate**, then **Yes**, rather than the incremental
   **Updated** option. The dialog may be skipped when data are current.
3. In **Customize**, choose **Assignment (Input, Output, Bit Memory, Timers,
   Counters)** and confirm. If the viewer is already open, use its Assignment
   toolbar control. Verify the resulting view and select the relevant operand
   area with no unintended filters.
4. Check the legend: `X` is a listed use; a blank bit is an unreferenced
   candidate. Check byte/word/dword overlap, indirect I/O and bulk copies.
   Confirm the module address, slot, channel and actual wiring before calling a
   terminal spare. Record unresolved hardware or reference coverage.

Offline reference regeneration refreshes derived information. It does not
authorize changes to logic or other project data.

## Read and trace

Inventory Blocks, Sources and Symbols. Use cross-references for readers/writers
and Program Structure for call paths; confirm important references in the
actual network or source. Trace raw input, mapped bit, timer/latch, resets,
interlock and final consumer. Check call order, later writers and overlapping
DB writes or pointer-based transfers. For DBs, distinguish global, instance
and multi-instance data; use the declared type and displayed offset.

Match source to the editor before diagnosing compilation: **STL/AWL** uses
instruction-list syntax (such as `NETWORK`, `AN`, `CALL`); **SCL** is a
different language. A quote-related title error can be the first symptom of
AWL pasted into an SCL source. Identify the source type and exact first error;
correct the full language mismatch or use the matching editor. Do not claim a
draft compiles before seeing a successful offline build from the intended
compiler. Use an isolated copy for any authorized import or compile.

Report project/CPU, block, network and symbolic/absolute operand. Distinguish
source logic from runtime data and partial exports. Keep routine review
offline: no live monitoring, downloads, forcing, controller changes or saves
as part of inspection.
