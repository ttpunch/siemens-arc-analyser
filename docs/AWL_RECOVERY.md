# AWL / STL recovery from a STEP 7 V5 project

Two independent decoders are supported. Both are offline and read-only; neither
touches a controller.

* **Route A — symbolic export** through
  [`DotNetSiemensPLCToolBoxLibrary`](https://github.com/dotnetprojects/DotNetSiemensPLCToolBoxLibrary):
  highest fidelity, because it decodes using the project's own network boundaries and
  interface. Produces Siemens-style source with symbolic operands, block/network
  titles, FB call parameters and DB instance names. Requires a .NET SDK.
* **Route B — linear MC7 disassembly** through
  [`rz-libmc7`](https://github.com/rizinorg/rz-libmc7): no .NET needed, absolute
  operands, one statement per line. Use it as the independent second opinion, or when
  .NET is unavailable.

## Route A — symbolic export

```bash
# one-time: a .NET 8 SDK and a built copy of the library (netstandard2.1)
dotnet build -c Release -f netstandard2.1    # in DotNetSiemensPLCToolBoxLibrary/LibNoDaveConnectionLibrary
dotnet build -c Release                      # in tools/s7awl, with -p:S7ToolBoxDll=<built dll> if not vendored

export DOTNET_ROOT=/path/to/dotnet
export S7AWL_DLL=/path/to/s7awl/bin/Release/net8.0/s7awl.dll

PYTHONPATH=src python -m arc_analyser.step7.s7_dotnet_awl project.zip --out out/ --all
PYTHONPATH=src python -m arc_analyser.step7.s7_dotnet_awl project.zip --out out/ --block FC67
```

The library opens a project directory, not a ZIP, so the wrapper extracts a
read-only copy to `--workdir` (default `local_data/s7_work`, gitignored) first.

Output shape:

```
FUNCTION "HYDROSTATIC / HYDRAULIC" : VOID
TITLE =HYDROSTATIC / HYDRAULIC / LUBRICATION
VAR_INPUT
  ...
END_VAR
BEGIN
NETWORK
TITLE = HYDROSTATIC / LUBRICATION PUMP
      U     "MACHINE ON";
      UN    "20Q4";
      =     "20K4";
      CALL  "Push button", DB165 (Conditions_ok := M 52.0, Enabling_key := "90S9");
```

On the sample project this exported 159 of 162 blocks; only the three VAT tables have
no source (expected).

## Route B — mc7dis

```bash
cd rz-libmc7 && cc -O2 -I include -I src mc7dis.c src/simatic.c -o mc7dis   # mc7dis.c lives here
export MC7DIS=$(pwd)/mc7dis

PYTHONPATH=src python -m arc_analyser.step7.s7_project project.zip --out out/ --blobs
PYTHONPATH=src python -m arc_analyser.step7.s7_awl project.zip --out out/ --awl-all
```

`--blobs` writes the byte-exact `<LABEL>.mc5` payloads; `s7_awl` decodes each into
`awl/<LABEL>.awl` with every operand annotated from the project's symbol table:

```
      A M 12.0        ; MACHINE ON
      AN I 36.6       ; 60Q1 — T.S. HYDROSTATIC S.R. 1
      OPN DI 165
      UC FB 99
      S Q 33.0        ; 60K1 — HYDROSTATIC PUMP S.R. 1
```

`mc7dis.c` is a small CLI over upstream's `simatic_s7_decode_instruction`. Upstream
builds as a rizin plugin needing `rz_core`/`rz_util`; the plugin path is unnecessary
for offline block analysis.

## Windows notes (verified on a real V5 project)

* Build both pieces with a .NET SDK (8 or newer; a newer SDK builds `net8.0` fine, and the
  .NET 8 runtime must be installed to run it):
  `dotnet build -c Release -f netstandard2.1` in `LibNoDaveConnectionLibrary`, then
  `dotnet build -c Release -p:S7ToolBoxDll=<path to the built DLL>` in `tools/s7awl`.
  `bin/` and `obj/` are gitignored.
* The Python wrapper now picks `dotnet.exe`, uses `os.pathsep`, and resolves the project to a long
  absolute path. If you call `s7awl.dll` directly, pass a **long** Windows path: with an 8.3 short
  path (`C:\Users\NAME~1\...`) it reports `folders: 0`, `S7 programs: 0` and exports nothing.
* Direct call (no wrapper): `dotnet s7awl.dll <project.s7p> --all --out <dir>`.
* A project folder that holds a nested duplicate of itself and a second `ombstx/offline/0000000N`
  block folder is normal for copied projects. The reader analyses the first folder; use `--folder`
  to choose another.
* Result on one 162-block project: 159 files exported; the 3 VAT tables have no source.

## How to know a decode is right

Never trust a single source. On the sample project three independent sources agree on
one block:

1. **Route A**: `U "MACHINE ON"; U "60B1B"; UN "60Q1"; CALL "Push button", DB165 (...); S "60K1"`
2. **Route B**: `A M 12.0`, `A I 40.1`, `UN I 36.6`, `UC FB 99`, `OPN DI 165`, `S Q 33.0`
3. **Project tables**: the block's stored reference list (part `00065`) names
   `DB2, DB10, DB21, DB33, DB165, DB170, DB172, FC103, FB99`; the xref `DBNB` set is
   `{2,10,21,33,165,170,172}` plus FB99/FC103; SYMLIST names `Q 33.0` = the pump contactor.

If a decode disagrees with the reference list or the xref DB set, treat the **decode**
as suspect before the project.

### Known divergences between the two routes

Operator counts (`U/UN/O/ON/=/S/R/FP/FN`) for all 72 FC/FB blocks of the sample:
**39/72 agree exactly**. The remainder are explained, not noise:

* **know-how protected blocks** — Route A returns the interface only; Route B still
  sweeps the bytes.
* **standard-library blocks with embedded jump tables/parameter data** — a linear
  sweep over-decodes the tail while Route A respects network boundaries.
* blocks whose code sits behind multi-instance calls, where Route A emits interface
  and code as separate sections.

## Reporting rule

Always describe a decode as a **read-only reconstruction**, never as a
Siemens-exported listing, and state that it should be confirmed in SIMATIC Manager /
STEP 7 Classic before it is used for maintenance decisions.
