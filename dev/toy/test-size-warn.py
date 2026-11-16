#!/usr/bin/env python3
# reads: skills/workflow-health/scripts/health.py
"""Proves health's script-size warning sits at the 19,000-byte target, not at 90% of the 20 KB limit (#4370, #4560): a script of
18,900 bytes raises no row, one of 19,100 warns, one over 20,480 fails, and a repo of only small scripts passes."""
import os
import sys
import tempfile

here = os.environ.get("TOY_HERE") or os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(here, "skills", "workflow-health", "scripts"))
import health  # noqa: E402

fails = []


def check(name, ok):
    print(("PASS " if ok else "FAIL ") + name)
    if not ok:
        fails.append(name)


def rows(*sizes):
    with tempfile.TemporaryDirectory() as root:
        folder = os.path.join(root, "skills", "x", "scripts")
        os.makedirs(folder)
        for n, size in enumerate(sizes):
            with open(os.path.join(folder, "s%d.py" % n), "wb") as handle:
                handle.write(b"#" * (size - 1) + b"\n")
        return [(r["state"], r["subject"]) for r in health.size_rows(root)]


check("a script of 18,900 bytes raises no warning", [s for s, _ in rows(18900)] == ["PASS"])
check("a script of exactly 19,000 bytes raises no warning", [s for s, _ in rows(19000)] == ["PASS"])
check("a script of 19,100 bytes warns", [s for s, _ in rows(19100)] == ["WARN"])
check("a script over the 20,480 limit fails", [s for s, _ in rows(20600)] == ["FAIL"])
check("negative control: scripts of 18,432 and 18,900 bytes, the old warning band, raise nothing", [s for s, _ in rows(18432, 18900)] == ["PASS"])
sys.exit(1 if fails else 0)
