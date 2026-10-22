# Prompt 01B — Prepare Local Archive Folder (Codex on Windows)

Work in the currently opened `siemens-arc-analyser` repository. Do not require VS Code.

1. Find the repository root and create `local_data/` if it does not exist. Do not modify or delete existing files.
2. Open `local_data/` in Windows File Explorer, if permitted. If opening Explorer is blocked, print the absolute folder path so I can open it manually.
3. Run `git status --short --branch` and report any uncommitted or unpushed changes. Do not stage, commit, push, or modify Git state in this task.
4. Check that `local_data/` and `*.arc` are ignored by Git. Use `git check-ignore -v` with a hypothetical `local_data/example.arc` path, without creating a fake archive. If either is not ignored, report the problem; do not change .gitignore without approval.
5. Ask me to manually COPY (not move) one Siemens `.arc` backup into `local_data/`. Never touch the original backup. Do not search other directories for archives.
6. Once I confirm that I copied the file, inspect only metadata of `.arc` files directly inside `local_data/`: filename, size in bytes, and SHA-256 hash. Read-only inspection only. If no file is present, report that and stop.
7. Do not extract, restore, execute, alter, rename, delete, upload, or commit any archive or machine-derived data. Do not access CNC controllers or start Siemens applications.
8. Report the folder path, Git ignore verification, Git status, and local archive metadata. Keep machine-specific details local.

Wait for my confirmation before inspecting an archive.
