#!/usr/bin/env python3
# reads: .loop/regression-skips.tsv .loop/regression-limits.tsv dev/toy/approved-row-changes.tsv .loop/regression.tsv
"""skip-list-approved (TD1215): the rows that skip by design on main are a committed list, and it cannot grow without a record.

.loop/regression-skips.tsv holds `id TAB reason` for every row main's CI run reports SKIPPED. Each id must be a regression row,
carry a reason, and have a `skip:<id>` line in dev/toy/approved-row-changes.tsv naming its record and reason, so a PR that adds an
id to the list also adds that line. The header names the source run. Negative controls: an id with no approval, an id that is no
row, and a list with no reason each fail the same check."""
import os
import sys

root = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
failed = []


def check(ok, text):
    print(("PASS: " if ok else "FAIL: ") + text)
    if not ok:
        failed.append(text)


def table(path):
    with open(os.path.join(root, path), encoding="utf-8") as handle:
        return [x.rstrip("\n") for x in handle if x.strip()]


def problems(skips, approved, rows):
    """What is wrong with a skip list (lines), the approved lines and the row ids."""
    found = []
    ok = {a.split("\t")[0] for a in approved if not a.startswith("#") and len(a.split("\t")) == 3 and all(c.strip() for c in a.split("\t"))}
    for line in skips:
        if line.startswith("#"):
            continue
        cells = line.split("\t")
        if len(cells) not in (2, 3) or not cells[1].strip() or (len(cells) == 3 and cells[2] != "notrun"):
            found.append("no reason: " + cells[0])
        elif cells[0] not in rows:
            found.append("not a regression row: " + cells[0])
        elif "skip:" + cells[0] not in ok:
            found.append("no approved-row-changes line for skip:" + cells[0])
    return found


def limit_problems(limits, approved, rows):
    """o889, TD1326: each entry of .loop/regression-limits.tsv is a regression row with a number or `nightly`, a reason, and an approved line."""
    ok = {a.split("\t")[0] for a in approved if not a.startswith("#") and len(a.split("\t")) == 3}
    found = []
    for line in limits:
        cells = line.split("\t")
        if line.startswith("#"):
            continue
        if len(cells) != 3 or not cells[2].strip() or not (cells[1] == "nightly" or cells[1].isdigit()):
            found.append("bad limit entry: " + cells[0])
        elif cells[0] not in rows:
            found.append("not a regression row: " + cells[0])
        elif ("nightly:" if cells[1] == "nightly" else "limit:") + cells[0] not in ok:
            found.append("no approved-row-changes line for " + cells[0])
    return found


skips, approved = table(".loop/regression-skips.tsv"), table("dev/toy/approved-row-changes.tsv")
rows = {l.split("\t")[0] for l in table(".loop/regression.tsv") if not l.startswith("#")}
entries = [l for l in skips if not l.startswith("#")]
check(len(entries) >= 1 and "main run 45110588623 at c2ce6460a" in "\n".join(l for l in skips if l.startswith("#")), "the list names its source run and holds rows")
FIX = {"no reason": "give the row a reason (and, for a row the runner may not be able to start, the flag notrun in the third column) in .loop/regression-skips.tsv",
       "not a regression row": "remove the id from .loop/regression-skips.tsv, or add the row to .loop/regression.tsv",
       "no approved-row-changes line": "add `skip:<id><TAB>TD<n><TAB><reason>` to dev/toy/approved-row-changes.tsv, with the record that allows the skip"}
for one in problems(skips, approved, rows):
    print("FAIL: %s. Fix: %s" % (one, FIX[next(k for k in FIX if one.startswith(k))]))
check(problems(skips, approved, rows) == [], "every row on the skip list is a regression row with a reason and an approved record: %s" % problems(skips, approved, rows))
check(all(any(one.startswith(k) for k in FIX) for one in problems(skips + ["x\t"], approved, rows | {"x"}) + problems(skips + ["y\tr"], approved, rows) + problems(skips + ["z\tr"], approved, rows | {"z"})),
      "every failure the list check reports has its own repair line")
check(problems(skips + ["no-such-approval\tgood reason"], approved, rows | {"no-such-approval"}) == ["no approved-row-changes line for skip:no-such-approval"],
      "negative control: an id added to the list with no approved-row-changes line fails")
check(problems(skips + ["not-a-row\tgood reason"], approved + ["skip:not-a-row\tTD0\tr"], rows) == ["not a regression row: not-a-row"],
      "negative control: an id that is no regression row fails")
check(problems(skips + ["ls-plist\t"], approved, rows) == ["no reason: ls-plist"], "negative control: an entry with no reason fails")
limits = table(".loop/regression-limits.tsv")
check(limit_problems(limits, approved, rows) == [], "every entry of the limits file is a regression row with a number or nightly, a reason and a limit:/nightly: line in approved-row-changes.tsv: %s" % limit_problems(limits, approved, rows))
check(limit_problems(limits + ["tables-prep-151\t999\tr"], approved, rows) == [] and limit_problems(limits + ["fast-row\t5\tr"], approved, rows | {"fast-row"}) == ["no approved-row-changes line for fast-row"],
      "negative control: a limit with no approved-row-changes line fails")
check(limit_problems(limits + ["no-such-row\tnightly\tr"], approved + ["nightly:no-such-row\tTD0\tr"], rows) == ["not a regression row: no-such-row"] and limit_problems(limits + ["tables-prep-151\tabc\tr"], approved, rows) == ["bad limit entry: tables-prep-151"] and limit_problems(limits + ["tables-prep-151\t5"], approved, rows) == ["bad limit entry: tables-prep-151"],
      "negative control: an id that is no row, a limit that is no number and an entry with no reason each fail")
print("ALL PASS" if not failed else "FAILED: %d" % len(failed))
sys.exit(1 if failed else 0)
