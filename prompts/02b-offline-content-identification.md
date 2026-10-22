# Prompt 02B — Offline Siemens ZIP Content Identification

Read AGENTS.md, docs/STATUS.md and the ignored local ZIP metadata report from Prompt 02. The user asks how we can identify actual NC/PLC/drive data without a Siemens-specific skill. Be explicit: no Siemens parser or verified Siemens SDK is installed in this repository, and filename clues are not proof. Use only evidence from the archive and installed tools. Do not hallucinate formats or decoding.

1. Check Git ignore rules for local_data/ and reports. Work on the single selected ZIP copy under local_data/; never touch the original. Confirm its SHA-256 against the previous local report before proceeding.
2. First inspect only the existing ZIP entry inventory and metadata. Group likely PLC, NC, drive, HMI, configuration and unknown entries by names/extensions; label each as hypothesis with confidence and evidence.
3. Search *locally available documentation/help files* of installed STEP 7 V5.7 SP3, SINUMERIK Add-on, SINUMERIK Commissioning 4.8.4 and SinuTrain for documented archive formats and safe offline export/inspection tools. Do not launch Siemens software, use network access, install software or connect to any controller. Report precisely what is verified versus unverified. Do not claim Siemens has a Codex/VS Code skill.
4. Prepare a proposed shortlist of at most five low-risk ZIP entries for later content inspection, explaining why each is useful, its declared uncompressed size, and whether it is likely text or binary. Do not decompress or read any entry payload in this run.
5. Produce a private detailed report under local_data/ and a sanitized summary in docs/STATUS.md. Do not include machine identifiers, real archive/member names, hashes, file paths or secrets in the tracked summary.
6. State the exact read-only, resource-bounded inspection method you would use in a *subsequent approved task* (limits on decompressed bytes, compression ratio, entry count, output location, and handling of binary/unknown data). Do not implement extraction or payload decoding now.
7. Run existing tests and report findings and blockers. Do not commit or push without approval.

Never extract, restore, execute or upload archive contents. Stop and ask the user for approval before reading/decompressing any ZIP member payload or using proprietary Siemens utilities. If the available evidence cannot establish the format, say so.
