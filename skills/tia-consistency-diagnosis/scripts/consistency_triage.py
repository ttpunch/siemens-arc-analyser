#!/usr/bin/env python3
"""Triage TIA Portal blocks reported as inconsistent, read-only.

Inputs are the artefacts of the tia-harness probe:
  --inventory   stdout of `TiaProbe.exe --blocks`            (BLOCK|... lines)
  --export-log  stdout of `TiaProbe.exe --blocks --export`    (EXPORT|ok/fail|... lines)
  --xml-dir     the directory the probe exported into

Outputs a markdown report: counts, protection overlay, the export-failure oracle check, the call-graph
edges that point into the inconsistent set, root candidates and header-version clusters.

Nothing here writes to the project; it only reads files already on disk.
"""
from __future__ import annotations

import argparse
import collections
import pathlib
import re


def parse_inventory(path: pathlib.Path) -> list[dict]:
    blocks = []
    for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        if not line.startswith("BLOCK|"):
            continue
        p = line.split("|")
        # BLOCK|plc|depth|group|class|name|number|lang|hdr|mem|consistent|protected
        blocks.append(dict(
            plc=p[1], group=p[3], cls=p[4], name=p[5], num=p[6], lang=p[7],
            hdr=p[8], mem=p[9], cons=p[10] == "True",
            prot=(p[11] == "True" if len(p) > 11 else False),
        ))
    return blocks


def parse_export_log(path: pathlib.Path) -> tuple[set[str], set[str]]:
    ok, fail = set(), set()
    for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        if line.startswith("EXPORT|ok|") or line.startswith("EXPORT|fail|"):
            parts = line.split("|")
            tag = parts[2]
            name = tag.split("_", 1)[1] if "_" in tag else tag  # tags are "<number>_<Name>"
            (ok if parts[1] == "ok" else fail).add(name)
    return ok, fail


def build_call_graph(xml_dir: pathlib.Path, names: list[str]) -> dict[str, set[str]]:
    ordered = sorted(names, key=len, reverse=True)
    pattern = re.compile(
        r"(?<![A-Za-z0-9_])(" + "|".join(re.escape(n) for n in ordered) + r")(?![A-Za-z0-9_])"
    )
    graph: dict[str, set[str]] = {}
    for path in sorted(xml_dir.rglob("*.xml")):
        stem = path.stem
        caller = stem.split("_", 1)[1] if "_" in stem else stem
        graph[caller] = set(pattern.findall(path.read_text(encoding="utf-8", errors="replace"))) - {caller}
    return graph


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--inventory", required=True, type=pathlib.Path)
    ap.add_argument("--export-log", required=True, type=pathlib.Path)
    ap.add_argument("--xml-dir", required=True, type=pathlib.Path)
    ap.add_argument("--out", required=True, type=pathlib.Path)
    args = ap.parse_args()

    blocks = parse_inventory(args.inventory)
    by_name = {b["name"]: b for b in blocks}
    inconsistent = {b["name"] for b in blocks if not b["cons"]}
    protected = {b["name"] for b in blocks if b["prot"]}
    ok, fail = parse_export_log(args.export_log)
    graph = build_call_graph(args.xml_dir, list(by_name))

    inbound: dict[str, set[str]] = collections.defaultdict(set)
    for caller, callees in graph.items():
        for callee in callees:
            inbound[callee].add(caller)

    upstream = sorted({c for n in inconsistent for c in inbound[n] if by_name.get(c, {}).get("cons")})
    # Inconsistent blocks cannot be exported, so the graph has no edges *out of* them; "no known caller"
    # therefore means "not called from any exported block", not "a root".
    unknown_callers = sorted(n for n in inconsistent if not inbound[n])

    L: list[str] = []
    add = L.append
    add("# Inconsistency triage\n")
    add(f"Blocks enumerated: **{len(blocks)}** · inconsistent: **{len(inconsistent)}** · "
        f"know-how protected: **{len(protected)}** · overlap: **{len(inconsistent & protected)}**\n")

    add("## Export-failure oracle\n")
    add(f"- inconsistent blocks that failed export: **{len(inconsistent & fail)}/{len(inconsistent)}**")
    only_fail = sorted(fail - inconsistent)
    if only_fail:
        add(f"- failed export but reported consistent (auto-generated or unexportable): {', '.join(only_fail)}")
    if inconsistent - fail:
        add(f"- inconsistent but exported anyway: {', '.join(sorted(inconsistent - fail))}")
    add("")

    add("## Inconsistent blocks\n")
    add("| Class | No. | Name | Language | Header | Protected | Group |")
    add("|---|---|---|---|---|---|---|")
    for n in sorted(inconsistent, key=lambda x: (by_name[x]["group"], by_name[x]["cls"], x)):
        b = by_name[n]
        add(f"| {b['cls']} | {b['num']} | {n} | {b['lang']} | {b['hdr']} | "
            f"{'yes' if b['prot'] else 'no'} | {b['group']} |")
    add("")

    add("## Header-version clusters\n")
    for hdr, count in collections.Counter(by_name[n]["hdr"] for n in inconsistent).most_common():
        members = sorted(n for n in inconsistent if by_name[n]["hdr"] == hdr)
        add(f"- `{hdr}` — {count}: {', '.join(members)}")
    add("")

    add("## Called from consistent code (upstream candidates)\n")
    if upstream:
        for n in sorted(inconsistent):
            callers = sorted(c for c in inbound[n] if by_name.get(c, {}).get("cons"))
            if callers:
                add(f"- **{n}** ← {', '.join(callers)}")
    else:
        add("- none: every reference to an inconsistent block comes from another inconsistent block")
    add("")

    add("## No known caller in the exported graph\n")
    add("Inconsistent blocks cannot be exported, so their own calls are invisible. These have no incoming\n"
        "edge from any exported block — usually because their caller is inconsistent too (e.g. OB1).\n")
    for n in unknown_callers:
        add(f"- {n} ({by_name[n]['cls']} {by_name[n]['num']}, {by_name[n]['lang']})")
    add("")
    add("> Evidence only. TIA does not expose the reason for `IsConsistent=False`; "
        "the authoritative reason comes from compiler messages (tier 2, mutating).\n")

    args.out.write_text("\n".join(L), encoding="utf-8")
    print(f"wrote {args.out} ({len(L)} lines)")
    print(f"inconsistent={len(inconsistent)} protected={len(protected)} "
          f"export_fail={len(fail)} no_known_caller={len(unknown_callers)} upstream={len(upstream)}")


if __name__ == "__main__":
    main()
