---
name: siemens-tia-project-reading
description: Read an offline Siemens TIA Portal project through compatible Openness tools or the native editor. Use for PLC code and DB export, tags, types, cross-references and nested SINUMERIK device software; use the Classic skill for S7P projects.
---

# TIA Portal offline project reading

Identify the intended project and actual TIA version from its path and the
running Portal executable. A tool or server name containing a version is not
proof that it matches the project. Use the available tool schemas to check
server diagnostics, configured version, connection and read-only mode. A
successful environment check does not establish project attachment or export.

1. Choose the compatible read-only connection and attach to the intended
   Portal instance. If a tool must open the project, use its verified absolute
   project/session path. Check the returned project identity before reading.
   Do not upgrade the project or repoint an active server to bypass mismatch.
2. Discover device and PLC software trees and use the exact returned object
   paths. Inventory block groups, blocks, tags and data types. Read block
   interfaces and actual networks/source; retain the best supported export and
   record rejected/protected objects separately.
3. On a nested SINUMERIK device, a visible PLC item may still fail resolution.
   Stop trying path spellings once the exact discovered path fails. Use a
   supported recursive Openness reader that traverses child device items,
   checks each for a SoftwareContainer with PlcSoftware, and walks block
   groups, or inspect the same project in the native editor. Inspect any
   existing helper before running it: check version, target selection, output
   paths and absence of compile/save/download calls.
4. Use cross-references to find writers and readers, then inspect conditions,
   call order and indirect references or bulk writes. Verify standard-layout
   offsets; do not infer absolute addresses from optimized DB field order.
5. Record project/version, PLC path, block/network, operand, representation and
   export coverage. When an export fails, try another supported representation
   or inspect the editor. Do not compile just to make a block exportable.

An Openness permission prompt belongs to the user. Reuse a stable approved
reader where available; its approval can depend on executable identity. Do not
change security settings or enable write mode. Work offline from controllers;
no download, forcing, value writes or machine motion.
