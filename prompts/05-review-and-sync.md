# Prompt 05 — Review and GitHub Sync

Copy into Codex when you want to publish safe code updates.

```text
Read AGENTS.md and docs/STATUS.md. Review the current Git diff and run all available tests.

Check every staged file for sensitive machine information, credentials, archive contents, proprietary data, absolute local paths, and large binary files. Ensure archives, extracted files, and raw reports remain excluded from Git.

Summarize changes and test results. If the changes are safe, commit source code and documentation with a clear message. Ask for my explicit approval before pushing to GitHub. Never force-push or overwrite unrelated work. Report the resulting commit SHA and changed files.
```
