#!/usr/bin/env python3
# reads: skills/workflow-monitoring/scripts/checkin.py, auto.py, replan.py, pool.py
"""Proves workflow-monitoring's checkin.py, auto.py, replan.py and pool.py are each at or under the 19,000-byte script cap,
measured as git stores them (line ends as LF), and that the measure fails a script one byte over."""
import os
import sys
import tempfile

here = os.environ.get("TOY_HERE") or os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
CAP = 19000
fails = []


def size(path):
    with open(path, "rb") as handle:
        return len(handle.read().replace(b"\r", b""))


def check(name, ok):
    print(("PASS " if ok else "FAIL ") + name)
    if not ok:
        fails.append(name)


for name in ("checkin", "auto", "replan", "pool"):
    found = size(os.path.join(here, "skills", "workflow-monitoring", "scripts", name + ".py"))
    check("%s.py is %d bytes, at or under %d" % (name, found, CAP), found <= CAP)
with tempfile.TemporaryDirectory() as tmp:
    over = os.path.join(tmp, "over.py")
    with open(over, "wb") as handle:
        handle.write(b"#" * 19000 + b"\r\n")  # 19,001 bytes as LF, 19,002 on disk
    check("negative control: a script of 19,001 bytes as LF is over the cap", size(over) == CAP + 1 and size(over) > CAP)
sys.exit(1 if fails else 0)
