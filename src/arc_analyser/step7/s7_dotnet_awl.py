"""Full symbolic AWL export via DotNetSiemensPLCToolBoxLibrary (best-quality path).

This is the highest-fidelity route: the library decodes MC7 using the project's own
network boundaries and interface, so it recovers symbolic names, block titles,
network titles, FB call parameters and DB instance names.

It needs the locally built ``s7awl`` console app (see references/local-tools.md):

    dotnet                                                   .NET SDK 8 (DOTNET_ROOT)
    <repo>/tools/s7awl/bin/Release/net8.0/s7awl.dll           s7awl console app (S7AWL_DLL)
    dotnet s7awl.dll <project.s7p> --all --out DIR

Usage
-----
    python3 s7_dotnet_awl.py <project.zip|dir> --out OUTDIR [--block FC67] [--all]
                             [--workdir DIR] [--s7awl PATH]

If the input is a ZIP it is copied/extracted read-only to ``--workdir`` first,
because the library opens a project directory, not a ZIP.

Read-only: never writes into the project, never connects to a controller.
"""

from __future__ import annotations

import argparse
import os
import shutil
import subprocess
import sys
import zipfile
from pathlib import Path

DOTNET_ROOT = Path(os.environ.get("DOTNET_ROOT", "")) if os.environ.get("DOTNET_ROOT") else Path("/usr/local/share/dotnet")
DEFAULT_S7AWL = Path(
    os.environ.get("S7AWL_DLL", "")
) if os.environ.get("S7AWL_DLL") else Path("s7awl/bin/Release/net8.0/s7awl.dll")
DEFAULT_WORKDIR = Path(os.environ.get("S7_WORKDIR", "local_data/s7_work"))


def find_project(s7p_dir: Path) -> Path | None:
    cands = sorted(s7p_dir.glob("*.s7p")) or sorted(s7p_dir.glob("*.S7P"))
    return cands[0] if cands else None


def prepare(project: Path, workdir: Path) -> Path:
    """Return a directory containing the .s7p file, extracting a ZIP if needed."""
    if project.is_dir():
        direct = find_project(project)
        if direct:
            return direct
        # maybe the .s7p sits one level down
        for sub in sorted(project.iterdir()):
            if sub.is_dir():
                hit = find_project(sub)
                if hit:
                    return hit
        raise SystemExit(f"no .s7p found under {project}")

    if project.suffix.lower() != ".zip":
        return project  # let the tool try the file directly

    workdir.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(project) as z:
        tops = {n.split("/")[0] for n in z.namelist() if n.strip()}
        # pick the shallowest project folder that holds a .s7p
        s7p_members = [n for n in z.namelist() if n.lower().endswith(".s7p")]
        if not s7p_members:
            raise SystemExit(f"{project} contains no .s7p")
        s7p_members.sort(key=lambda n: n.count("/"))
        target_member = s7p_members[0]
        root = target_member.rsplit("/", 1)[0]
        out_dir = workdir / root
        if not find_project(out_dir):
            n = 0
            for info in z.infolist():
                name = info.filename
                if not name.startswith(root + "/") or name.endswith("/"):
                    continue
                dst = workdir / name
                dst.parent.mkdir(parents=True, exist_ok=True)
                dst.write_bytes(z.read(info))
                n += 1
            print(f"extracted : {n} files -> {out_dir}")
    s7p = find_project(out_dir)
    if not s7p:
        raise SystemExit(f"extraction did not produce a .s7p in {out_dir}")
    return s7p


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Symbolic AWL export via DotNetSiemensPLCToolBoxLibrary")
    ap.add_argument("project", type=Path)
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--block", default="", help="comma-separated labels, e.g. FC67,FC82")
    ap.add_argument("--all", action="store_true", help="export every block")
    ap.add_argument("--workdir", type=Path, default=DEFAULT_WORKDIR)
    ap.add_argument("--s7awl", type=Path, default=DEFAULT_S7AWL)
    args = ap.parse_args(argv)

    if not args.s7awl.exists():
        raise SystemExit(
            f"s7awl not built at {args.s7awl}\n"
            "build it with:\n"
            "  dotnet build -c Release   (in tools/s7awl, with DOTNET_ROOT set to your SDK)"
        )
    dotnet = DOTNET_ROOT / "dotnet"
    if not dotnet.exists():
        raise SystemExit(f".NET runtime missing at {dotnet} (see references/local-tools.md)")

    s7p = prepare(args.project, args.workdir)
    args.out.mkdir(parents=True, exist_ok=True)

    env = dict(os.environ)
    env["DOTNET_ROOT"] = str(DOTNET_ROOT)
    env["DOTNET_CLI_TELEMETRY_OPTOUT"] = "1"
    env["PATH"] = f"{DOTNET_ROOT}:{env.get('PATH', '')}"

    base = [str(dotnet), str(args.s7awl), str(s7p), "--out", str(args.out)]
    runs: list[list[str]] = []
    if args.all:
        runs.append(base + ["--all"])
    elif args.block:
        for label in [x for x in args.block.replace(",", " ").split() if x]:
            runs.append(base + ["--block", label])
    else:
        runs.append(base + ["--list"])

    for cmd in runs:
        res = subprocess.run(cmd, capture_output=True, text=True, env=env, timeout=1800)
        sys.stdout.write(res.stdout)
        if res.returncode != 0:
            sys.stderr.write(res.stderr[-2000:])
            return res.returncode
    n = len(list(args.out.glob("*.awl")))
    print(f"symbolic  : {n} AWL file(s) in {args.out.resolve()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
