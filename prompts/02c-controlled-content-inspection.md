# Prompt 02C — Controlled Offline Content Inspection

You are working in the Siemens ARC Analyser repository on my Windows PC. Read AGENTS.md, docs/STATUS.md, and the previous Prompt 02B findings first.

## Objective
Determine whether up to five locally shortlisted ZIP members contain readable STEP 7 PLC source, project metadata, or opaque binary content. Distinguish confirmed observations from filename-based hypotheses. Do not claim Siemens-specific decoding without verified evidence.

## Authorization and scope
I authorize **read-only inspection of at most five ZIP member payloads** from the single existing archive copy in gitignored local_data, solely for local classification. This is not permission to extract files to disk, open a Siemens project, run scripts from the archive, launch Siemens software, restore anything, or connect to a CNC/PLC. Do not inspect other archives. Do not upload any machine data, payload snippets, filenames, hashes, or private reports.

## Procedure
1. Verify the repository's current git status, .gitignore rules, archive location, and unchanged SHA-256 against the private baseline. Stop if the baseline does not match or the exact candidate allowlist from the prior private report cannot be established.
2. Review the prior private inventory and select no more than five small, nonempty entries spanning likely PLC source, structured metadata, notes, and project descriptor. Keep their exact names and contents private. Do not accept user-controlled member paths as filesystem destinations.
3. Before reading, implement or use a strictly bounded in-memory reader with the limits below and add synthetic tests. If limits cannot be enforced reliably, stop and report the blocker without reading payloads.
4. Reject encrypted entries, unsupported compression, links, traversal, absolute/ambiguous Windows paths, duplicates or case collisions, suspicious size discrepancies, and unsupported nested archives. Enforce at most 100,000 inventory entries, 64 MiB central-directory metadata, 64 KiB decompressed per member, 256 KiB aggregate, and compression ratio <=100. Read in chunks <=4 KiB, count actual decompressed bytes, and cap worker resources at 256 MiB RAM and 10 seconds. Do not rely solely on advertised sizes. Abort safely on any limit or integrity error.
5. Inspect bytes **only in memory**. Determine BOM/encoding conservatively, inspect printable text only when decoding is unambiguous, and classify each member as verified text/source, structured metadata, binary/unknown, or unsafe/unreadable. No guessing binary schemas; never execute or render active content.
6. Keep member names, exact text, binary bytes, hashes, and detailed findings exclusively in ignored local reports, confined to a new ignored local output directory. Never echo confidential material to terminal, Git logs, issue comments, or remote services. Ensure reports cannot escape via symlinks/reparse points.
7. Add synthetic unit tests for decompression limits, rejected paths, malformed archives, text/binary classification, and unchanged input. Run the existing test suite as well. Do not install dependencies without asking.
8. Update docs/STATUS.md with a **sanitized** summary only: number of members inspected, categories confirmed, unresolved formats, tests, blockers, and recommended next step. Do not commit or push automatically. Report git status and which safe code/docs changes are ready for review.

## Completion criteria
Provide a concise evidence-based classification summary and say explicitly whether any PLC source was actually verified. Preserve the original and local archive copy byte-for-byte. Do not proceed to Prompt 03 or implement general extraction.
