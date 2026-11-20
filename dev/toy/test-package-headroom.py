#!/usr/bin/env python3
# windows: ok
# reads: dev/package.py skills/workflow-health/scripts/rules.py skills/workflow-health/scripts/report.py skills/workflow-delivery/scripts/lane.py skills/workflow-delivery/scripts/goal.py skills/workflow-regression/scripts/actions.py
"""Headroom under dev/package.py's caps: five scripts within GRD-20 (warn over 19,000, fail over 20,480), and no more than 100 shipped files.

The files are counted the way package.py counts them: the ones git tracks, never __pycache__ or other loose files."""
import importlib.util
import os
import subprocess
import sys

root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
FIVE = ("workflow-health/scripts/rules.py", "workflow-health/scripts/report.py", "workflow-delivery/scripts/lane.py",
        "workflow-delivery/scripts/goal.py", "workflow-regression/scripts/actions.py")
fails = 0
done = subprocess.run([sys.executable, os.path.join(root, "dev", "toy", "size-check.py"), "--control"] + [os.path.join(root, "skills", n) for n in FIVE],
                      capture_output=True, text=True)
print(done.stdout.strip())
print("%s: the five scripts warn over 19,000 and fail only over 20,480 (GRD-20); a 20,481-byte fixture fails, a 19,500-byte one only warns" % ("PASS" if done.returncode == 0 else "FAIL"))
fails += done.returncode != 0
spec = importlib.util.spec_from_file_location("package", os.path.join(root, "dev", "package.py"))
package = importlib.util.module_from_spec(spec)
spec.loader.exec_module(package)
files = len(package.walk(root))
print("%s: the package holds %d files (at most 100)" % ("PASS" if files <= 100 else "FAIL", files))
fails += files > 100
raise SystemExit(1 if fails else 0)
