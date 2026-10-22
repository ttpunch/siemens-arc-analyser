# Prompt 02 — Identify Local Siemens ZIP or ARC Archive

Run after Prompt 01B. Copy the following instructions into Codex:

```text
Read AGENTS.md and docs/STATUS.md. The user generated a backup using a Siemens application's "7-Zip archive (.zip)" option and placed a COPY in the repository's local_data/ folder. The software also offered "Siemens archive (.arc)" and "PKZIP archive (.zip)" options, but the current sample is the 7-Zip ZIP option. Do not infer the backup's internal Siemens structure or controller type from this description alone.

1. Check git status and confirm local_data/ and ZIP/ARC backup files are ignored. If any backup could be tracked, stop and report the risk.
2. Find only archive files directly inside local_data/. If there is more than one, ask which to inspect. Do not search the wider computer.
3. For the selected file, record its size and SHA-256 locally. Do not modify the file.
4. Read the file signature and use the existing read-only archive inspector. For ZIP, use Python's zipfile module to check whether it is ZIP-compatible; record encryption flags, compression methods, and whether the central directory is readable. Avoid any operation that extracts or decompresses entry payloads, including zipfile.testzip().
5. List ZIP member metadata only in a local gitignored report: entry paths, sizes, compressed sizes, flags, and folder hierarchy. Treat filenames and paths as confidential. Do not read file contents, extract entries, execute scripts, or invoke restore tools.
6. Check for suspicious entries (absolute paths, ../ traversal, symlinks, duplicates, excessive size/count or compression ratios) without extracting. Flag any concerns.
7. Summarize likely NC/PLC/drive/machine-data categories only where filenames provide evidence; distinguish inference from confirmed content. If the file is not a readable ZIP, report the exact failure and stop rather than guessing.
8. Write a sanitized, high-level summary in docs/STATUS.md without real machine identifiers, member names, local paths, credentials, or hashes. Keep the detailed local report under local_data/.
9. Run available tests without installing dependencies. Report results and recommend the next safe step. Do not commit or push anything without my approval.

Never modify the original backup, upload machine data, contact a CNC controller, launch Siemens applications, or extract/restore an archive. Ask permission before any new tool or software installation.
```
