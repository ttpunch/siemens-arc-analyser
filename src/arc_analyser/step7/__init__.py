"""Read-only STEP 7 Classic (V5.x) project readers and AWL recovery helpers.

Everything here works on a copy: project ZIPs are opened read-only, block code is
extracted from memo fields and decoded offline. Nothing connects to a controller,
writes into a project or restores data.

Modules
-------
s7_dbf      dBase III table + memo (``.DBT``) reader shared by the others
s7_project  block inventory, symbol/xref export, per-block Markdown reports
s7_awl      linear MC7 disassembly via the ``mc7dis`` CLI (no .NET required)
s7_dotnet_awl  full symbolic AWL export via DotNetSiemensPLCToolBoxLibrary
"""

__all__ = ["s7_dbf", "s7_project", "s7_awl", "s7_dotnet_awl"]
