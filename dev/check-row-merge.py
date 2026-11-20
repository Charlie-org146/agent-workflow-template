#!/usr/bin/env python3
"""Prove a row merge kept every check: the (script, mode, PASS text) set the rows of the base branch check equals the set
the rows of this tree check, and each merged row also fails on a FAIL line. usage: check-row-merge.py [BASE-REF=origin/main]"""
import re
import subprocess
import sys

OLD = re.compile(r'^(?P<s>(?:bash|python3) dev/toy/[A-Za-z0-9_.-]+(?: [A-Za-z0-9_-]+)?) {1,2}2>&1 \| grep -q(?P<f>[Fx]?) (?P<q>"(?:[^"\\]|\\.)*")$')
NEW = re.compile(r'^out=\$\((?P<s>(?:bash|python3) dev/toy/[A-Za-z0-9_.-]+(?: [A-Za-z0-9_-]+)?) 2>&1\); (?P<c>.*) && ! printf "%s\\n" "\$out" \| grep -q "\^ \*FAIL"$')
CHK = re.compile(r'printf "%s\\n" "\$out" \| grep -q(?P<f>[Fx]?) (?P<q>"(?:[^"\\]|\\.)*")')


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
# rows run under /bin/sh (dash on the CI runner): every merged command must pass there, not only under bash
dash = "/bin/dash" if __import__("os").path.exists("/bin/dash") else None
for line in open(".loop/regression.tsv").read().splitlines():
    cells = line.split("\t")
    if dash and len(cells) > 3 and NEW.match(cells[2]):
        done = subprocess.run([dash, "-c", cells[2]], capture_output=True, text=True)
        print("dash %s %s" % ("PASS" if done.returncode == 0 else "FAIL", cells[0]))
        if done.returncode:
            bad.append(cells[0])
sys.exit(1 if lost or added or bad else 0)
