---
name: siemens-archive-inspection
description: Identify offline Siemens SINUMERIK ARC backups, STEP 7 Classic ZIP archives and exported PLC sources. Use to inspect archive signatures, inventory local evidence, assess source coverage and make archives searchable within authorized local scope.
---

# Siemens archive inspection

Start with the supplied backup or declared input directory. An `.arc` suffix,
a recognizable container signature, and a Siemens project identity are three
different findings. Do not assume that an ARC is ZIP, that a ZIP is a STEP 7
project, or that a commissioning backup contains editable PLC sources.

1. Inspect a local copy read-only. Record its hash, size, signature and
   evidence of project, controller family and software version. Start with
   metadata and a bounded listing. Separate PLC, NC, drive, HMI and unknown
   entries; filenames are classification clues.
2. In the analyser checkout, verify which modules are present at the checked-out
   revision. Use `arc_analyser.cli` for signature inspection. Read the
   [repository README](../../../README.md) before invoking any additional
   workflow; do not assume a documented module is shipped on this branch.
   Signature recognition does not validate or decode payloads.
3. Inspect or extract payloads only within the user's authorized scope. Use a
   fresh local output directory and a bounded reader. Reject absolute and
   traversal paths, symlinks, duplicate or case-colliding paths, and entries
   exceeding configured size or decompression limits. Never restore a backup
   to a controller or execute its contents.
4. Read existing text sources first. Preserve original encoding, archive member
   paths and source line numbers. Identify examples, library templates and old
   versions separately. Native block catalogs, symbols and printable fragments
   can support an inventory; they are not a reconstruction of compiled logic.
   Compare coverage with the block inventory before calling a source current or
   complete.
5. For missing logic, use a supported offline export or native editor for the
   matching Classic or TIA version. Establish project, CPU and revision again
   after opening an export or copy. Do not migrate or compile solely to gain
   access. Keep original and generated files separate.

Keep outputs in an ignored, local evidence area. Alongside retained source,
record block numbers/types, DB layouts, interfaces, calls, operand references
and available hardware mapping. Link conclusions back to source lines or
networks; mark partial, protected, failed and uninspected entries. Check the
archive hash or project revision before reusing evidence. Report exactly what is
readable and the smallest useful next export when coverage is incomplete.

Never commit or upload real backups, project paths, derived machine data, or
credentials. An archive inspection request does not authorize sending its
content to a notebook or external service.
