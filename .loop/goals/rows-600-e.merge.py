#!/usr/bin/env python3
"""rows-600-e: the second merge pass over .loop/regression.tsv (after rows-600-c), with the two relaxations the owner approved:
B: defect rows with different links merge, every link kept in the link cell; D: nightly rows merge into land rows of the same script
and requirement. Known-red rows still merge only with other known-red rows (no A). One-time tool, not part of the package.

usage: merge_rows.py [--write] [--list]    print the before/after counts and the coverage check; --write also rewrites the files

A group is rows with the same requirement, type, script, known-red state and Windows-skip state (a row that skips native Windows never shares a row with one that runs there). A row already merged by rows-600-c is spliced in whole
(its command already is `( u1 ) && ( u2 )`); a plain `out=$(CMD); CHECK` or `CMD | grep -q "P"` row shares one run with the rows that
call the same CMD; anything else runs as its own ( subshell ). Commands join with `&&`, so the row passes only when every old case
passes. A group that would pass MAXRUNS distinct runs or 400 description characters is split into several rows."""
import collections
import os
import re
import sys

MAXRUNS = 6
SCRIPT = re.compile(r"dev/toy/[\w.-]+\.(?:sh|py)|skills/[\w./-]+\.py")
SKIP = re.compile(r"dev/toy/(?:skip-windows|ci-env|reap)\.sh")
VAR = re.compile(r"^(\w+)=\$\((.*?)\); (.*)$", re.S)
SIMPLE = re.compile(r'^((?:\w+=\S+ )*(?:bash|python3) dev/toy/[\w.-]+(?: [^|;&"$<>]+?)?(?: 2>&1)?) \| ((?:tail -1 \| )?grep -q[Fx]* "(?:[^"\\]|\\.)*")$')
HEAD = " cases, then each passes: "
LIMIT = re.compile(r"package[.]py|listing[.]json|19,?000|20,?480|-size [+]2047|under-19|under 20 KB")


def read(path):
    with open(path, encoding="utf-8", newline="") as handle:
        text = handle.read()
    return text, "\r\n" if "\r\n" in text else "\n"


def script_of(cmd):
    for found in SCRIPT.findall(cmd):
        if not SKIP.search(found):
            return found
    return None


def is_merged(row):
    return row[2].startswith("( ") and row[2].endswith(" )") and HEAD in row[5]


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
    """The merged command and how each member is covered: ('whole', cmd), ('var', key, check) or ('plain', key)."""
    runs, order, cover, whole = collections.OrderedDict(), [], {}, []
    for r in members:
        if is_merged(r):
            whole.append(r[2])
            cover[r[0]] = ("whole", r[2])
            continue
        unit = unit_of(r[2])
        key = ("var", unit[1], unit[2]) if unit[0] == "var" else ("plain", unit[1])
        if key not in runs:
            runs[key], order = [], order + [key]
        if unit[0] == "var":
            if unit[3] not in runs[key]:
                runs[key].append(unit[3])
            cover[r[0]] = ("var", key, unit[3])
        else:
            cover[r[0]] = ("plain", key)
    parts = list(dict.fromkeys(whole))
    for key in order:
        if key[0] == "var":
            parts.append("( %s=$(%s); %s )" % (key[1], key[2], " && ".join("{ %s; }" % c for c in runs[key])))
        else:
            parts.append("( %s )" % key[1])
    count = len(order) + sum(c.count(" ) && ( ") + 1 for c in dict.fromkeys(whole))
    return " && ".join(parts), cover, count


def pieces_of(r):
    if is_merged(r):
        return [p for p in r[5].split(HEAD, 1)[1].rstrip(".").split("; ") if p]
    m = re.search(r"\bthen (.*?)\.?$", r[5])
    return [(m.group(1) if m else r[5]).strip()[:50].rstrip()]


def describe(members, goal, script):
    """One Given-when-then sentence naming every case in short form; callers split a group when it passes 400 characters."""
    pieces = [p for r in members for p in pieces_of(r)]
    return "Given %s, when %s runs its %d%s%s." % (goal, os.path.basename(script), len(pieces), HEAD, "; ".join(pieces))


def reorder(cmd):
    """Units that skip native Windows go last, so a skip (exit 77) never hides the units that run there."""
    units = cmd.split(" ) && ( ")
    if len(units) < 2:
        return cmd
    units = [("( " if n else "") + u + (" )" if n < len(units) - 1 else "") for n, u in enumerate(units)]
    ordered = sorted(units, key=lambda u: "skip-windows" in u)
    out = " && ".join(ordered)
    return out if len(out) == len(cmd) and sorted(out.split()) == sorted(cmd.split()) else cmd


def covered(command, r, how):
    if how[0] == "whole":
        return how[1] in command
    if how[0] == "plain":
        return ("( %s )" % how[1][1]) in command
    key, check = how[1], how[2]
    return ("%s=$(%s);" % (key[1], key[2])) in command and ("{ %s; }" % check) in command


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
        key = ("single", r[0]) if s is None or len(r) < 8 or r[1] == "covered" or r[0] in known or LIMIT.search(r[2] + " " + r[5]) else (r[3], r[6], s, False, "skip-windows" in r[2])
        groups.setdefault(key, []).append(r)
    merged, removed, coverage, newcmd, links = {}, {}, [], {}, 0
    for key, members in groups.items():
        if key[0] == "single" or len(members) == 1:
            merged[members[0][0]] = members[0]
            newcmd[members[0][0]] = members
            continue
        chunks, cur = [], []
        for r in members:
            probe = cur + [r]
            if (build(probe)[2] > MAXRUNS or len(describe(probe, key[0], key[2])) > 400) and cur:
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
            row = list(chunk[0])
            row[1] = "land" if any(r[1] == "land" for r in chunk) else chunk[0][1]
            row[2], row[4], row[5] = command, max(r[4] for r in chunk), describe(chunk, key[0], key[2])
            if key[1] == "defect":
                row[7] = " ".join(dict.fromkeys(x for r in chunk for x in r[7].split()))
                links += len(row[7].split()) > 1
            merged[row[0]] = row
            newcmd[row[0]] = chunk
            for r in chunk[1:]:
                removed[r[0]] = row[0]
            for r in chunk:
                coverage.append((r[0], row[0], covered(command, r, cover[r[0]])))
    for mid, row in merged.items():
        if "skip-windows" in row[2] and row[2].startswith("( "):
            new = reorder(row[2])
            if new != row[2]:
                row[2] = new
    uncovered = [old for old, _, ok in coverage if not ok]
    gone = set(removed)
    stale = sorted({r[0] for r in merged.values() for t in re.findall(r"[A-Za-z0-9][A-Za-z0-9_.-]*[A-Za-z0-9]", r[2] + " " + r[5]) if t in gone for _ in [0]})
    print("rows before %d, after %d (merged away %d); uncovered old cases: %d; merged defect rows with several links: %d" % (len(rows), len(merged), len(removed), len(uncovered), links))
    print("descriptions over 400: %d; commands over 4000 characters: %d; rows whose command or description names a merged-away id: %d" % (
        sum(len(r[5]) > 400 for r in merged.values()), sum(len(r[2]) > 4000 for r in merged.values()), len(stale)))
    if "--list" in sys.argv:
        for old, mid, ok in coverage:
            print("%s -> %s %s" % (old, mid, "ok" if ok else "UNCOVERED"))
        for sid in stale:
            print("NAMES-GONE-ID", sid)
    if not write:
        return 1 if uncovered else 0
    if uncovered:
        sys.exit("REFUSED: uncovered old cases; nothing written")
    out = []
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
                continue
            rows2.append(l)
        if keep_first:
            have = {l.split("\t")[0] for l in rows2}
            for target, cells in taken.items():
                if target not in have:
                    rows2.append("\t".join([target] + cells[1:]))
        with open(name, "w", encoding="utf-8", newline="") as handle:
            handle.write(eol.join(rows2))
    with open(".loop/goals/rows-600-e.map.tsv", "w", encoding="utf-8", newline="\n") as handle:
        handle.write("".join("%s\t%s\n" % (old, mid) for old, mid, _ in coverage if old != mid))
    return 0


if __name__ == "__main__":
    sys.exit(main())
