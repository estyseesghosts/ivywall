#!/usr/bin/env python3
"""Generate references/feps/registry.md from a local clone of the FEP repository.

Usage: python3 tools/fep_registry.py <path-to-fep-clone> [output]

Status, title and dates come from each proposal's front matter. The
"Implementations" column lists the names the proposal itself gives in its
"Implementations" section (at most four); it is not a conformance claim.
"""
import os
import re
import subprocess
import sys

MAX_IMPL = 4
ORDER = ["FINAL", "DRAFT", "WITHDRAWN"]
TITLES = {"FINAL": "Final", "DRAFT": "Draft", "WITHDRAWN": "Withdrawn"}


def implementations(text):
    m = re.search(r"^## Implement(?:ations|ors)\s*\n(.*?)(?=^## |\Z)", text, re.S | re.M)
    if not m:
        return []
    names = []
    for line in m.group(1).split("\n"):
        line = line.strip()
        if not line.startswith(("-", "*")):
            continue
        item = line.lstrip("-* ").strip()
        item = re.sub(r"\[([^\]]+)\]\([^)]*\)", r"\1", item)
        item = re.sub(r"^(?:Implemented|Supported) (?:by|in)\s+", "", item)
        item = re.split(r"\s+(?:can|has|have|is|are|exposes|supports?|implements?|issues|only|as of|\(|[-—:])|[,(:]", item)[0].strip()
        item = item[:28].rsplit(" ", 1)[0] if len(item) > 28 else item
        if item and item.lower() not in {n.lower() for n in names}:
            names.append(item)
    return names


def main():
    clone = sys.argv[1]
    out = sys.argv[2] if len(sys.argv) > 2 else os.path.join(os.path.dirname(__file__), "..", "references", "feps", "registry.md")
    sha = subprocess.run(["git", "-C", clone, "log", "-1", "--format=%H %cs"], capture_output=True, text=True).stdout.split()
    sha, date = sha[0], sha[1]
    base = os.path.join(clone, "fep")
    rows = {s: [] for s in ORDER}
    for slug in sorted(os.listdir(base)):
        path = os.path.join(base, slug, f"fep-{slug}.md")
        if not os.path.exists(path):
            continue
        text = open(path, encoding="utf-8").read().replace("\r\n", "\n")
        fm = {}
        m = re.match(r"---\n(.*?)\n---\n", text, re.S)
        if m:
            for line in m.group(1).split("\n"):
                if ": " in line:
                    k, v = line.split(": ", 1)
                    fm[k.strip()] = v.strip().strip('"')
        status = fm.get("status", "DRAFT").upper()
        title = re.search(r"^# (.*)$", text, re.M)
        title = re.sub(r"^FEP-[0-9a-f]{4}:\s*", "", title.group(1).strip()) if title else slug
        title = title.replace("|", "/")
        year = (fm.get("dateReceived") or "")[:4]
        end = fm.get("dateFinalized") or fm.get("dateWithdrawn") or ""
        impl = implementations(text)
        shown = ", ".join(impl[:MAX_IMPL]) + (f" +{len(impl) - MAX_IMPL}" if len(impl) > MAX_IMPL else "")
        rows[status if status in rows else "DRAFT"].append((slug, title, year, end, shown or "none listed"))

    total = sum(len(v) for v in rows.values())
    lines = [
        "# FEP registry",
        "",
        f"All {total} Fediverse Enhancement Proposals in the official repository, checked {date} at commit `{sha[:10]}`: "
        + ", ".join(f"{len(rows[s])} {TITLES[s].lower()}" for s in ORDER)
        + ". A proposal's status describes its document, not how widely it is used. A draft can be deployed and a final proposal can have one implementer.",
        "",
        "The last column repeats the first four names in the proposal's own implementations list; proposals that describe implementers in prose show 'none listed'. It is not tested conformance and it is only as current as the proposal text. "
        "For the proposals this wiki uses, see the individual records: [FEP-044f](fep-044f.md), [FEP-521a](fep-521a.md), [FEP-67ff](fep-67ff.md) and [FEP-7628](fep-7628.md). "
        "Support in one studied release is recorded in that project's [federation document](../federation-docs/index.md).",
        "",
        "This page is generated: `python3 tools/fep_registry.py <fep-clone>`. Do not edit it by hand.",
        "",
    ]
    for s in ORDER:
        lines += [f"## {TITLES[s]} ({len(rows[s])})", ""]
        head = "| FEP | Title | Received | " + ("Finalized" if s == "FINAL" else "Withdrawn" if s == "WITHDRAWN" else "") + " | Named in the FEP's list |"
        if s == "DRAFT":
            head = "| FEP | Title | Received | Named in the FEP's list |"
            sep = "| --- | ----- | -------- | ------------------------------ |"
        else:
            sep = "| --- | ----- | -------- | --- | ------------------------------ |"
        lines += [head, sep]
        for slug, title, year, end, impl in rows[s]:
            link = f"[{slug}](https://fediverse.codeberg.page/fep/fep/{slug}/)"
            if s == "DRAFT":
                lines.append(f"| {link} | {title} | {year} | {impl} |")
            else:
                lines.append(f"| {link} | {title} | {year} | {end} | {impl} |")
        lines.append("")
    lines += [
        "## Sources",
        "",
        f"- [FEP repository at commit `{sha[:10]}`](https://codeberg.org/fediverse/fep/src/commit/{sha}/fep) — every proposal's text, status and implementation list",
        "- [Fediverse Enhancement Proposals](https://fediverse.codeberg.page/fep/) — the published registry",
        "",
    ]
    with open(out, "w", encoding="utf-8", newline="\n") as f:
        f.write("\n".join(lines))
    print(f"wrote {out}: {total} proposals")


if __name__ == "__main__":
    main()
