#!/usr/bin/env python3
# windows: ok
# reads: .loop/regression.tsv dev/toy/test-dlf-stops.py dev/toy/test-dlf-wire.py dev/toy/test-dlf-budget.py dev/toy/test-dlf-ledger.py dev/toy/test-dlf-scan.py
"""v110-dlf-1 done line 1: each DLF-1 test case (DLF-1.1 to DLF-1.5) has a regression row linked to its requirement id, and the toys behind
the rows all pass. Reads the rows file and runs the five toys; no network."""
import os
import subprocess
import sys

root = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
linked = {line.split("\t")[3] for line in open(os.path.join(root, ".loop", "regression.tsv")) if line.count("\t") >= 3}
missing = [n for n in ("DLF-1.1", "DLF-1.2", "DLF-1.3", "DLF-1.4", "DLF-1.5") if n not in linked]
if missing:
    sys.exit("FAIL: no regression row linked to %s" % ", ".join(missing))
for toy in ("stops", "wire", "budget", "ledger", "scan"):
    done = subprocess.run([sys.executable, os.path.join(root, "dev", "toy", "test-dlf-%s.py" % toy)], capture_output=True, text=True)
    if done.returncode:
        sys.exit("FAIL: test-dlf-%s.py: %s" % (toy, [l for l in done.stdout.splitlines() if l.startswith("FAIL")][:3]))
print("ALL PASS")
