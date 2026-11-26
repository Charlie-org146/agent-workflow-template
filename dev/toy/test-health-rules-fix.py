#!/usr/bin/env python3
# windows: ok
# reads: skills/workflow-health/scripts/defects.py skills/workflow-health/scripts/controls.py skills/workflow-docs/scripts/entry.py
"""TD521: the migration rule can run: a sibling module loaded through defects.mod still finds its own lazy imports, so controls.py
run migration fires on its fixture. (Principle 5 retired the requirements-per-page count, o988.) Runs on scratch repos; nothing in
this repo is touched."""
import os
import subprocess
import sys
import tempfile

here = os.path.dirname(os.path.abspath(__file__))
top = os.path.abspath(os.path.join(here, "..", ".."))
scripts = os.path.join(top, "skills", "workflow-health", "scripts")
fails = 0


def check(ok, text):
    global fails
    print(("PASS: " if ok else "FAIL: ") + text)
    fails += 0 if ok else 1


lazy = ("import sys; sys.path.insert(0, %r); import defects; e = defects.mod('workflow-docs', 'entry'); "
        "e.config(%r); print('lazy ok')" % (scripts, top))
got = subprocess.run([sys.executable, "-c", lazy], capture_output=True, text=True, cwd=tempfile.mkdtemp())
check("lazy ok" in got.stdout, "a sibling loaded through defects.mod finds its own lazy import (entry.config -> counting) after mod returns: %s" % (got.stderr.strip().splitlines() or ["ok"])[-1])
run = subprocess.run([sys.executable, os.path.join(scripts, "controls.py"), "run", "migration"], capture_output=True, text=True, cwd=top)
check("PASS controls migration: fires on its fixture" in run.stdout, "controls.py run migration fires on its fixture: %s" % (run.stdout.strip().splitlines() or ["no output"])[-1][:100])
print("ALL PASS" if not fails else "FAILED: %d" % fails)
sys.exit(1 if fails else 0)
