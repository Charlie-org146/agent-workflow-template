#!/usr/bin/env python3
"""The cut gate (DEL-26.4, #5757): a test cut for time, or not run, fails the checks, naming the test and its time.

Run by the PR workflow's affected job (lanes_cli.py), and by any gate that must fail on an unfinished row:
    python3 cutgate.py 's/shard-[0-7]/t.tsv' [all.tsv [skips.tsv]]
It reads the shard times files (rows `id TAB seconds TAB status`: RAN on the shard that ran the row, SEL on the others, CUT
when the budget ran out, LEFT when the row passed its limit, SKIP when the row asked to be skipped, NOTRUN when the runner could
not start it). A row that is SEL or RAN somewhere and RAN nowhere is unfinished: it prints `FAIL cut or not run: <id> <STATUS>
<seconds>s: ...` and exits 1. No file matching the pattern is also exit 1, and a malformed times line is exit 1 with its file
and line before anything is written. It writes the best non-SEL line of each row to all.tsv (the times cache) before it fails,
only when there is a record, and replaces the file whole; it prints `run twice: <ids>` for a row two shards ran. A SKIP or
NOTRUN row is never counted as run: it passes only when its id is in skips.tsv (`id TAB reason`, the rows that skip by design
on main; a NOTRUN row also needs the flag `notrun` in the third column) and is printed `SKIPPED <id>: <reason>`; any other
prints a FAIL line naming the row and the repair. An unreadable skips.tsv is exit 1. It reruns nothing."""
import glob
import math
import os
import sys

STATES = ("", "RAN", "SEL", "CUT", "LEFT", "SKIP", "NOTRUN")
LIST = ".loop/regression-skips.tsv"


def read(files):
    """The rows [id, seconds, status] of the times files, or the malformed lines found."""
    rows, bad = [], []
    for name in files:
        for n, line in enumerate(open(name).read().splitlines(), 1):
            if not line.strip():
                continue
            cells = line.split("\t")
            sec = cells[1] if len(cells) > 1 else ""
            try:
                ok = math.isfinite(float(sec)) and float(sec) >= 0
            except ValueError:
                ok = False
            why = "fields" if len(cells) < 2 or not cells[0].strip() else "seconds" if not ok else "status" if (cells[2:3] or [""])[0] not in STATES else ""
            if why:
                bad.append("FAIL malformed times line: %s:%d: bad %s in %r; the shard's times file is corrupt: rerun the shard job" % (name, n, why, line))
            elif len(line.split()) >= 3:
                rows.append(line.split())
    return rows, bad


def main(pattern, out="all.tsv", known=None):
    files = sorted(glob.glob(pattern))
    if not files:
        print("FAIL cut or not run: no shard times file matches " + pattern)
        return 1
    listed = {}
    if known:
        try:
            for x in open(known).read().splitlines():
                cells = x.split("\t")
                if x.strip() and not x.startswith("#"):
                    listed[cells[0]] = (cells[1] if len(cells) > 1 else "", "notrun" in cells[2:])
        except OSError as err:
            print("FAIL cannot read the skip list %s: %s; run from the repo root or restore the file" % (known, err.strerror or err))
            return 1
    rows, bad_lines = read(files)
    if bad_lines:
        print("\n".join(bad_lines))
        return 1
    best = {}
    for row in sorted(rows, key=lambda r: (r[0], [-ord(c) for c in r[2]], r)):
        if row[2] != "SEL":
            best.setdefault(row[0], row)
    if best:  # an empty record is never written: the times cache keeps the last real one
        try:
            with open(out + ".new", "w") as handle:
                handle.writelines("\t".join(r) + "\n" for r in best.values())
            os.replace(out + ".new", out)
        except OSError as err:
            print("FAIL cannot write the times file %s: %s; the times cache is unchanged" % (out, err.strerror or err))
            return 1
    ran = [r[0] for r in rows if r[2] == "RAN"]
    print("run twice: " + ",".join(sorted({i for i in ran if ran.count(i) > 1})))
    skip = sorted({r[0] for r in rows if r[2] in ("SKIP", "NOTRUN")})
    gone, fail = set(), []
    for i in skip:
        started = any(r[0] == i and r[2] == "NOTRUN" for r in rows)
        if i in listed and (listed[i][1] or not started):
            print("SKIPPED %s: %s" % (i, listed[i][0]))
        elif started:
            fail.append("FAIL could not run: %s: the runner could not start the row here; fix the runner, or add it to %s with the notrun flag, its reason and a skip:%s line in dev/toy/approved-row-changes.tsv" % (i, LIST, i))
        else:
            fail.append("FAIL skipped and not skipped on main: %s: the row skipped here; fix why it cannot run, or add it to %s with its reason and a skip:%s line in dev/toy/approved-row-changes.tsv" % (i, LIST, i))
    if skip:
        picked = {r[0] for r in rows if r[2] in ("RAN", "SEL", "CUT", "LEFT", "SKIP", "NOTRUN")}
        print("skipped, never counted as run: %s (%d of %d selected rows)" % (",".join(skip), len(skip), len(picked)))
    print("\n".join(fail)) if fail else None
    unfinished = sorted({r[0] for r in rows if r[2] in ("SEL", "RAN")} - set(ran) - set(skip))
    for i in unfinished:
        what = "%s %ss" % (best[i][2], best[i][1]) if i in best else "not run"
        print("FAIL cut or not run: %s %s: raise the shard budget (owner) or move the row" % (i, what))
    return 1 if unfinished or fail else 0


if __name__ == "__main__":
    if sys.argv[1:2] in (["-h"], ["--help"]):
        print(__doc__)
        sys.exit(0)
    if len(sys.argv) < 2:
        print("usage: python3 cutgate.py 's/shard-[0-7]/t.tsv' [all.tsv [skips.tsv]] (see --help)", file=sys.stderr)
        sys.exit(2)
    sys.exit(main(*sys.argv[1:4]))
