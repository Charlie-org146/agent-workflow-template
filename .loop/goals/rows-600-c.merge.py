#!/usr/bin/env python3
"""rows-600-c: merge .loop/regression.tsv rows that call the same script for the same requirement (REG-4: one row per test script
and requirement, a row runs every case of its script for that requirement). One-time tool, not part of the package.

usage: merge_rows.py [--write]    print the before/after counts and the coverage check; --write also rewrites the files

A group is rows with the same level, requirement, type, defect link, script and known-red state. A member's command stays whole
inside the merged row: `out=$(CMD); CHECK` members that run the same CMD share one run and keep every CHECK, and a plain
`CMD | grep -q "P"` is rewritten the same way; anything else runs as its own ( subshell ). Commands join with `&&`, so the merged
row passes only when every old case passes. Groups with more than MAXRUNS distinct runs are split so a row stays within its timeout."""
import collections
import os
import re
import sys

MAXRUNS = 6
SCRIPT = re.compile(r"dev/toy/[\w.-]+\.(?:sh|py)|skills/[\w./-]+\.py")
SKIP = re.compile(r"dev/toy/(?:skip-windows|ci-env|reap)\.sh")
VAR = re.compile(r"^(\w+)=\$\((.*?)\); (.*)$", re.S)
SIMPLE = re.compile(r'^((?:\w+=\S+ )*(?:bash|python3) dev/toy/[\w.-]+(?: [^|;&"$<>]+?)?(?: 2>&1)?) \| ((?:tail -1 \| )?grep -q[Fx]* "(?:[^"\\]|\\.)*")$')


def read(path):
    with open(path, encoding="utf-8", newline="") as handle:
        text = handle.read()
    return text, "\r\n" if "\r\n" in text else "\n"


def script_of(cmd):
    for found in SCRIPT.findall(cmd):
        if not SKIP.search(found):
            return found
    return None


def unit_of(cmd):
    """('var', var, run, check) or ('plain', cmd)."""
    m = VAR.match(cmd)
    if m and m.group(2).count("(") == m.group(2).count(")") and "$(" not in m.group(2):
        return ("var", m.group(1), m.group(2), m.group(3))
    m = SIMPLE.match(cmd)
    if m and "$(" not in m.group(1):
        return ("var", "out", m.group(1), "printf '%s\\n' \"$out\" | " + m.group(2))
    return ("plain", cmd)


def build(members):
    """The merged command and the (old id -> how it is covered) records."""
    runs, order, cover = collections.OrderedDict(), [], {}
    for r in members:
        unit = unit_of(r[2])
        if unit[0] == "var":
            key = ("var", unit[1], unit[2])
            if key not in runs:
                runs[key], order = [], order + [key]
            if unit[3] not in runs[key]:
                runs[key].append(unit[3])
            cover[r[0]] = (key, unit[3])
        else:
            key = ("plain", unit[1])
            if key not in runs:
                runs[key], order = [], order + [key]
            cover[r[0]] = (key, None)
    parts = []
    for key in order:
        if key[0] == "var":
            parts.append("( %s=$(%s); %s )" % (key[1], key[2], " && ".join("{ %s; }" % c for c in runs[key])))
        else:
            parts.append("( %s )" % key[1])
    return " && ".join(parts), cover, len(order)


def describe(members, goal, script):
    head = "Given %s, when %s runs its %d cases, then each passes: " % (goal, os.path.basename(script), len(members))
    out, used = head, 0
    for r in members:
        m = re.search(r"\bthen (.*?)\.?$", r[5])
        piece = (m.group(1) if m else r[5]).strip()[:60].rstrip()
        add = ("; " if used else "") + piece
        if len(out + add) > 360 and used < len(members):
            return out + " (+%d more cases)" % (len(members) - used)
        out, used = out + add, used + 1
    return out + "."


def main():
    write = "--write" in sys.argv
    text, nl = read(".loop/regression.tsv")
    lines = text.split(nl)
    if lines and lines[-1] == "":
        lines.pop()
    rows = [l.split("\t") for l in lines if l.strip() and not l.startswith("#")]
    known = {l.split("\t")[0] for l in read(".loop/regression-known.tsv")[0].splitlines() if l.strip() and not l.startswith("#")}
    groups = collections.OrderedDict()
    for r in rows:
        s = script_of(r[2])
        key = ("single", r[0]) if s is None or len(r) < 8 else (r[1], r[3], r[6], r[7] if r[6] == "defect" else "", s, r[0] in known)
        groups.setdefault(key, []).append(r)
    merged, removed, coverage, newcmd = {}, {}, [], {}
    for key, members in groups.items():
        if key[0] == "single" or len(members) == 1:
            merged[members[0][0]] = members[0]
            newcmd[members[0][0]] = members
            continue
        chunks, cur = [], []
        for r in members:
            probe = cur + [r]
            if build(probe)[2] > MAXRUNS and cur:
                chunks.append(cur)
                cur = [r]
            else:
                cur = probe
        chunks.append(cur)
        for chunk in chunks:
            if len(chunk) == 1:
                merged[chunk[0][0]] = chunk[0]
                newcmd[chunk[0][0]] = chunk
                continue
            command, cover, _ = build(chunk)
            first = chunk[0]
            row = list(first)
            row[2], row[4], row[5] = command, max(r[4] for r in chunk), describe(chunk, key[1], key[4])
            merged[first[0]] = row
            newcmd[first[0]] = chunk
            for r in chunk[1:]:
                removed[r[0]] = first[0]
    uncovered = []
    for mid, chunk in newcmd.items():
        command = merged[mid][2]
        for r in chunk:
            unit = unit_of(r[2])
            ok = mid == r[0] and len(chunk) == 1 or (("( %s )" % unit[1]) in command if unit[0] == "plain" else
                                                       (("%s=$(%s);" % (unit[1], unit[2])) in command and ("{ %s; }" % unit[3]) in command))
            coverage.append((r[0], mid, ok))
            if not ok:
                uncovered.append(r[0])
    print("rows before %d, after %d (merged away %d); uncovered old cases: %d" % (len(rows), len(merged), len(removed), len(uncovered)))
    long = [mid for mid, r in merged.items() if len(r[5]) > 400]
    print("descriptions over 400: %d; commands over 3000 characters: %d" % (len(long), sum(len(r[2]) > 3000 for r in merged.values())))
    if "--list" in sys.argv:
        for old, mid, ok in coverage:
            print("%s -> %s %s" % (old, mid, "ok" if ok else "UNCOVERED"))
    if not write:
        return 1 if uncovered else 0
    if uncovered:
        sys.exit("REFUSED: uncovered old cases; nothing written")
    out, seen = [], set()
    for l in lines:
        if not l.strip() or l.startswith("#"):
            out.append(l)
            continue
        cells = l.split("\t")
        if cells[0] in removed:
            continue
        out.append("\t".join(merged[cells[0]]) if cells[0] in merged else l)
    with open(".loop/regression.tsv", "w", encoding="utf-8", newline="") as handle:
        handle.write(nl.join(out) + nl)
    for name, keep_first in ((".loop/regression-known.tsv", False), (".loop/regression-runs.tsv", False), (".loop/regression-red.tsv", True)):
        body, eol = read(name)
        rows2, taken = [], {}
        for l in body.split(eol):
            cells = l.split("\t")
            if l.strip() and not l.startswith("#") and cells[0] in removed:
                taken[removed[cells[0]]] = cells
                if keep_first:
                    continue
                continue
            rows2.append(l)
        if keep_first:
            have = {l.split("\t")[0] for l in rows2}
            for target, cells in taken.items():
                if target not in have:
                    rows2.append("\t".join([target] + cells[1:]))
        with open(name, "w", encoding="utf-8", newline="") as handle:
            handle.write(eol.join(rows2))
    with open(".loop/goals/rows-600-c.map.tsv", "w", encoding="utf-8", newline="\n") as handle:
        handle.write("".join("%s\t%s\n" % (old, mid) for old, mid, _ in coverage if old != mid))
    return 0


if __name__ == "__main__":
    sys.exit(main())
