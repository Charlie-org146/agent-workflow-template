#!/usr/bin/env python3
"""Prove a row merge kept every check: the (script, mode, PASS text) set the rows of the base branch check equals the set
the rows of this tree check, and each merged row also fails on a FAIL line. usage: check-row-merge.py [BASE-REF=origin/main]"""
import re
import subprocess
import sys

OLD = re.compile(r'^(?P<s>(?:bash|python3) dev/toy/[A-Za-z0-9_.-]+(?: [A-Za-z0-9_-]+)?) 2>&1 \| grep -q(?P<f>[Fx]?) (?P<q>"(?:[^"\\]|\\.)*")$')
NEW = re.compile(r'^out=\$\((?P<s>(?:bash|python3) dev/toy/[A-Za-z0-9_.-]+(?: [A-Za-z0-9_-]+)?) 2>&1\); (?P<c>.*) && ! grep -q "\^ \*FAIL" <<<"\$out"$')
CHK = re.compile(r'grep -q(?P<f>[Fx]?) (?P<q>"(?:[^"\\]|\\.)*") <<<"\$out"')


def checks(text):
    got, bad = set(), []
    for line in text.splitlines():
        cells = line.split("\t")
        if line.startswith("#") or len(cells) < 3:
            continue
        old, new = OLD.match(cells[2]), NEW.match(cells[2])
        if old:
            got.add((old["s"], old["f"], old["q"]))
        elif new:
            found = CHK.findall(new["c"])
            if not found:
                bad.append(cells[0])
            got |= {(new["s"], f, q) for f, q in found}
    return got, bad


base = sys.argv[1] if len(sys.argv) > 1 else "origin/main"
before, _ = checks(subprocess.run(["git", "show", base + ":.loop/regression.tsv"], capture_output=True, text=True, check=True).stdout)
after, bad = checks(open(".loop/regression.tsv").read())
lost, added = sorted(before - after), sorted(after - before)
print("checks before %d, after %d; lost %d, added %d" % (len(before), len(after), len(lost), len(added)))
for item in lost[:10]:
    print("LOST", item)
for item in added[:10]:
    print("ADDED", item)
for row in bad:
    print("NO CHECK in merged row", row)
sys.exit(1 if lost or added or bad else 0)
