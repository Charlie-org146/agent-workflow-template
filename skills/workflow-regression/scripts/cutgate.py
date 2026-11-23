#!/usr/bin/env python3
"""The cut gate (DEL-26.4, #5757): a test cut for time, or not run, fails the checks, naming the test and its time.

Run by the PR workflow's affected job (lanes_cli.py), and by any gate that must fail on an unfinished row:
    python3 cutgate.py 's/shard-[0-7]/t.tsv' [all.tsv [skips.tsv]]
It reads the shard times files (rows `id TAB seconds TAB status`: RAN on the shard that ran the row, SEL on the others, CUT
when the budget ran out, LEFT when the row passed its limit). A row that is SEL or RAN somewhere and RAN nowhere is unfinished:
it prints `FAIL cut or not run: <id> <STATUS> <seconds>s: ...` and exits 1. No file matching the pattern is also exit 1, and
writes nothing. It writes the best non-SEL line of each row to all.tsv (the times cache) before it fails, and prints
`run twice: <ids>` for a row two shards ran. A SKIP row (it could not run on its shard) is never counted as run: it passes only
when its id is in skips.tsv, the rows that skip by design on main, and is printed `SKIPPED <id>: <reason>`; any other SKIP row
prints `FAIL skipped and not skipped on main: <id>` and exits 1. It reruns nothing."""
import glob
import sys


def main(pattern, out="all.tsv", known=""):
    files = sorted(glob.glob(pattern))
    if not files:
        print("FAIL cut or not run: no shard times file matches " + pattern)
        return 1
    rows = [x.split() for f in files for x in open(f).read().splitlines() if len(x.split()) >= 3]
    best = {}
    for row in sorted(rows, key=lambda r: (r[0], [-ord(c) for c in r[2]], r)):
        if row[2] != "SEL":
            best.setdefault(row[0], row)
    if best:  # an empty record is never written: the times cache keeps the last real one
        with open(out, "w") as handle:
            handle.writelines("\t".join(r) + "\n" for r in best.values())
    ran = [r[0] for r in rows if r[2] == "RAN"]
    print("run twice: " + ",".join(sorted({i for i in ran if ran.count(i) > 1})))
    skip = sorted({r[0] for r in rows if r[2] == "SKIP"})
    why = {}
    try:  # the rows that skip by design on main: id TAB reason
        why = {x.split("\t")[0]: x.split("\t")[-1] for x in open(known).read().splitlines() if x and not x.startswith("#")} if known else {}
    except OSError:
        pass
    for i in skip:
        print(("SKIPPED %s: %s" % (i, why[i])) if i in why else "FAIL skipped and not skipped on main: " + i)
    if skip:
        print("skipped, never counted as run: " + ",".join(skip))
    bad = sorted({r[0] for r in rows if r[2] in ("SEL", "RAN")} - set(ran) - set(skip))
    for i in bad:
        what = "%s %ss" % (best[i][2], best[i][1]) if i in best else "not run"
        print("FAIL cut or not run: %s %s: raise the shard budget (owner) or move the row" % (i, what))
    return 1 if bad or [i for i in skip if i not in why] else 0


if __name__ == "__main__":
    if sys.argv[1:2] in (["-h"], ["--help"]):
        print(__doc__)
        sys.exit(0)
    sys.exit(main(*sys.argv[1:4]) if len(sys.argv) > 1 else 2)
