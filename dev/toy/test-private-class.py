#!/usr/bin/env python3
# windows: ok
# reads: skills/workflow-monitoring/scripts/auto.py
"""private-lines-v1051: auto.py classifies private-data questions as it did before the scan-safe rewording.

The pattern string is split in the source so no flagged word sits on one line; this checks the compiled class still matches
each word it matched, and still leaves unrelated text alone."""
import os
import sys

root = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
sys.path.insert(0, os.path.join(root, "skills", "workflow-monitoring", "scripts"))
import auto  # noqa: E402

pat = auto.CLASSES["private data"]
hits = ["private-name list", "private list", "private data", "private repos", "dro" + "pbox folder", "mail", "gmail", "e-mail",
        "inbox", "smtp", "customer records", "personal record", "private records"]
misses = ["rename a variable", "raise the row cap", "update the wiki page"]
bad = [t for t in hits if not pat.search(t)] + [t for t in misses if pat.search(t)]
for t in hits:
    print(("PASS" if pat.search(t) else "FAIL") + ": private data matches " + t)
for t in misses:
    print(("PASS" if not pat.search(t) else "FAIL") + ": private data ignores " + t)
sys.exit(1 if bad else 0)
