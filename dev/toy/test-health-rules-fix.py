#!/usr/bin/env python3
# windows: ok
# reads: skills/workflow-health/scripts/rules.py skills/workflow-health/scripts/defects.py skills/workflow-health/scripts/controls.py skills/workflow-docs/scripts/entry.py
"""TD521: health's requirements-per-page counts live requirements, not `- ID: moved to X` forwarding lines (negative control: 25 live
still fail), and the migration rule can run: a sibling module loaded through defects.mod still finds its own lazy imports, so
controls.py run migration fires on its fixture. Runs on scratch repos; nothing in this repo is touched."""
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


def rule(limit, live, forwarding):
    """What requirements_per_page says for a page with that many live and forwarding lines, in a fresh interpreter."""
    code = (
        "import sys, tempfile, os; sys.path.insert(0, %r); import controls, rules\n"
        "root = tempfile.mkdtemp(); controls.repo(root, {'criteria_max': %d})\n"
        "page = '# One\\n\\n## Requirements\\n\\n' + ''.join('- AB-%%d: **Unreviewed** a.\\n' %% n for n in range(1, %d + 1))\n"
        "page += '\\n## Revisions\\n\\n### Retired\\n\\n' + ''.join(('- AB-%%d: %%s\\n' %% (n, ['moved to AB-1', 'merged into AB-1', 'Retired'][n %% 3])) for n in range(100, 100 + %d))\n"
        "controls.write(root, 'docs/wiki/One.md', page)\n"
        "print([x['detail'] for x in rules.requirements_per_page(root)])\n" % (scripts, limit, live, forwarding))
    return subprocess.run([sys.executable, "-c", code], capture_output=True, text=True, cwd=tempfile.mkdtemp()).stdout.strip()


check(rule(24, 3, 23) == "[]", "3 live requirements and 23 moved-to lines: no FAIL (was '26 requirements, over 24')")
check(rule(5, 5, 30) == "[]", "5 live and 30 moved, merged or Retired lines under a limit of 5: no FAIL")
check(rule(24, 25, 0) == "['25 requirements, over 24']", "negative control: 25 live requirements still fail, counted as 25")
check(rule(5, 6, 40) == "['6 requirements, over 5']", "negative control: 6 live plus 40 forwarding lines fail on the 6 only")

lazy = ("import sys; sys.path.insert(0, %r); import defects; e = defects.mod('workflow-docs', 'entry'); "
        "e.config(%r); print('lazy ok')" % (scripts, top))
got = subprocess.run([sys.executable, "-c", lazy], capture_output=True, text=True, cwd=tempfile.mkdtemp())
check("lazy ok" in got.stdout, "a sibling loaded through defects.mod finds its own lazy import (entry.config -> counting) after mod returns: %s" % (got.stderr.strip().splitlines() or ["ok"])[-1])
run = subprocess.run([sys.executable, os.path.join(scripts, "controls.py"), "run", "migration"], capture_output=True, text=True, cwd=top)
check("PASS controls migration: fires on its fixture" in run.stdout, "controls.py run migration fires on its fixture: %s" % (run.stdout.strip().splitlines() or ["no output"])[-1][:100])
print("ALL PASS" if not fails else "FAILED: %d" % fails)
sys.exit(1 if fails else 0)
