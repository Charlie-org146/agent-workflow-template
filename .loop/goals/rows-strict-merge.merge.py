#!/usr/bin/env python3
"""rows-strict-merge: merge the strict groups of .loop/regression.tsv rows (same script, level, goal, category and link, none on the
known list) into one row each, as rows-600-c did. One-time tool, not part of the package.

usage: rows-strict-merge.merge.py [--write]    print the before/after counts and the coverage check; --write also rewrites the files

A member's command stays whole inside the merged row: `out=$(CMD); CHECKS` members that run the same CMD share one run and keep every
check, and a plain `CMD | grep -q "P"` is rewritten the same way (its grep goes on the shared output). A unit guarded by
dev/toy/skip-windows.sh keeps its guard and goes last, so a skip (exit 77) never hides the checks that run on Windows. Different
arguments are chained with &&. Two groups run a script once with no argument (it runs every case): the sources named
each case, the merged row names every case's PASS line (estimates) or takes the exit status of the whole run (release gate)."""
import collections
import re
import sys

SKIPW = re.compile(r'^bash dev/toy/skip-windows\.sh ("[^"]*") && (.*)$', re.S)
VAR = re.compile(r"^(\w+)=\$\((.*?)\); (.*)$", re.S)
PLAIN = re.compile(r'^((?:\w+=\S+ )*(?:bash|python3) dev/toy/[\w.-]+(?: (?:[^|;&"$<>]|"")+?)?(?: 2>&1)?) \| (.*)$', re.S)
SCRIPT = re.compile(r"dev/toy/[\w.-]+\.(?:sh|py)")

# survivor -> (members in order, description). One entry per group; the command is built below.
GROUPS = collections.OrderedDict()


def read(path):
    with open(path, encoding="utf-8", newline="") as handle:
        text = handle.read()
    return text, "\r\n" if "\r\n" in text else "\n"


def top_units(cmd):
    """Split a command into its top-level `( unit ) && ( unit )` parts, honouring quotes."""
    units, depth, start, quote, i = [], 0, None, None, 0
    while i < len(cmd):
        c = cmd[i]
        if quote:
            if c == "\\" and quote == '"':
                i += 1
            elif c == quote:
                quote = None
        elif c in "\"'":
            quote = c
        elif c == "(" :
            if depth == 0:
                start = i
            depth += 1
        elif c == ")":
            depth -= 1
            if depth == 0:
                units.append(cmd[start + 1:i].strip())
        i += 1
    return units


def unit_parts(unit):
    """('var', var, run, checks) | ('plain', run, rest) | ('guard', msg, inner) | ('raw', unit)."""
    m = SKIPW.match(unit)
    if m:
        return ("guard", m.group(1), unit_parts(m.group(2)))
    m = VAR.match(unit)
    if m and "$(" not in m.group(2):
        return ("var", m.group(1), m.group(2), m.group(3))
    m = PLAIN.match(unit)
    if m:
        return ("plain", m.group(1), m.group(2))
    return ("raw", unit)


def braces(checks):
    return checks if checks.lstrip().startswith("{") else "{ %s; }" % checks


def build(cmds):
    """One command from the members' commands: one run per distinct invocation, every check kept, guarded checks last."""
    runs, order, guarded = {}, [], collections.OrderedDict()
    for cmd in cmds:
        units = top_units(cmd) if cmd.startswith("(") else [cmd]
        for u in units:
            p = unit_parts(u)
            guard = None
            if p[0] == "guard":
                guard, p = p[1], p[2]
            if p[0] == "raw":
                raise SystemExit("cannot merge unit: " + u)
            run = p[2] if p[0] == "var" else p[1]
            if run not in runs:
                runs[run] = {"var": p[1] if p[0] == "var" else None, "checks": [], "guarded": []}
                order.append(run)
            if p[0] == "var" and runs[run]["var"] is None:
                runs[run]["var"] = p[1]
    for cmd in cmds:
        units = top_units(cmd) if cmd.startswith("(") else [cmd]
        for u in units:
            p = unit_parts(u)
            guard = None
            if p[0] == "guard":
                guard, p = p[1], p[2]
            run = p[2] if p[0] == "var" else p[1]
            var = runs[run]["var"] or "out"
            if p[0] == "var":
                check = braces(p[3])
                if p[1] != var:
                    raise SystemExit("variable clash in " + u)
            else:
                check = "{ printf '%%s\\n' \"$%s\" | %s; }" % (var, p[2])
            slot = runs[run]["guarded"] if guard else runs[run]["checks"]
            item = ("bash dev/toy/skip-windows.sh %s && " % guard + check, guard) if guard else (check, None)
            if guard:
                item = ("( bash dev/toy/skip-windows.sh %s && %s )" % (guard, check.strip()[2:-3] if check.startswith("{ printf") else check), guard)
            if item[0] not in (x[0] for x in slot):
                slot.append(item)
    parts = []
    for run in order:
        r = runs[run]
        var = r["var"] or "out"
        body = " && ".join([c[0] for c in r["checks"]] + [c[0] for c in r["guarded"]])
        parts.append("( %s=$(%s); %s )" % (var, run, body))
    return " && ".join(parts)


def rows_of(text, nl):
    lines = text.split(nl)
    if lines and lines[-1] == "":
        lines.pop()
    return lines


def main():
    write = "--write" in sys.argv
    text, nl = read(".loop/regression.tsv")
    lines = rows_of(text, nl)
    table = {l.split("\t")[0]: l.split("\t") for l in lines if l.strip() and not l.startswith("#")}
    known = {l.split("\t")[0] for l in read(".loop/regression-known.tsv")[0].splitlines() if l.strip() and not l.startswith("#")}
    specs = {}
    for line in open(".loop/goals/rows-strict-merge.groups.tsv", encoding="utf-8").read().splitlines():
        if not line.strip() or line.startswith("#"):
            continue
        survivor, members, how, description = line.split("\t")[:4]
        specs[survivor] = (members.split(), how, description)
    removed, merged, cover = {}, {}, []
    for survivor, (members, how, description) in specs.items():
        rows = [table[m] for m in members]
        assert survivor == members[0], survivor
        assert not [m for m in members if m in known], "known row in " + survivor
        assert len({(r[1], r[3], r[6], r[7] if len(r) > 7 else "") for r in rows}) == 1, "not strict: " + survivor
        assert len({SCRIPT.findall(r[2])[0] if "skip-windows" not in r[2] else SCRIPT.findall(r[2].replace("dev/toy/skip-windows.sh", ""))[0] for r in rows}) == 1, "scripts differ: " + survivor
        if how == "chain":
            command = build([r[2] for r in rows])
        else:
            command = how  # an explicit command (a script run once with no argument)
        assert len(description) <= 400, (survivor, len(description))
        row = list(rows[0])
        row[2], row[4], row[5] = command, max(r[4] for r in rows), description
        merged[survivor] = row
        for r in rows[1:]:
            removed[r[0]] = survivor
        cover.append((survivor, members, command))
    before = len(table)
    print("rows before %d, after %d (merged away %d); groups %d" % (before, before - len(removed), len(removed), len(specs)))
    print("longest merged command: %d characters" % max(len(c) for _, _, c in cover))
    if "--list" in sys.argv:
        for survivor, members, command in cover:
            print(survivor, members)
            print("   ", command)
    if not write:
        return 0
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
    for name in (".loop/regression-runs.tsv", ".loop/regression-red.tsv", ".loop/regression-issues.tsv"):
        body, eol = read(name)
        kept = [l for l in body.split(eol) if l.split("\t")[0] not in removed]
        with open(name, "w", encoding="utf-8", newline="") as handle:
            handle.write(eol.join(kept))
    with open(".loop/goals/rows-strict-merge.map.tsv", "w", encoding="utf-8", newline="\n") as handle:
        handle.write("".join("%s\t%s\n" % (old, new) for old, new in removed.items()))
    return 0


if __name__ == "__main__":
    sys.exit(main())
