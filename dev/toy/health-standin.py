#!/usr/bin/env python3
# windows: ok
# reads: skills/workflow-health/scripts/health.py skills/workflow-health/scripts/report.py skills/workflow-health/scripts/controls.py
"""A stand-in for a size rule that health no longer has (SET-10: the script byte limit came from the Agensi package), so the toys that
test how health FILES a WARN keep a WARN to file. It runs health.py unchanged, with one extra rule, `scripts`, in the Size group: a WARN
for each file named in $HEALTH_STANDIN (paths from the repo root, comma-separated) that exists and is 19000 bytes or more, as the old
rule did; a missing or small file adds no row. The planning, the labels, the milestones, the markers and the closing are health's own.
usage: HEALTH_STANDIN=skills/x/scripts/near.py health-standin.py check|preview|file ..."""
import os
import runpy
import sys

here = os.path.dirname(os.path.abspath(__file__))
scripts = os.path.join(here, "..", "..", "skills", "workflow-health", "scripts")
health = os.path.abspath(os.path.join(scripts, "health.py"))
sys.path.insert(0, os.path.dirname(health))
import controls  # noqa: E402
import defects  # noqa: E402
import report  # noqa: E402


def scripts_rule(root):
    out = []
    for name in filter(None, os.environ.get("HEALTH_STANDIN", "").split(",")):
        path = os.path.join(root, name)
        size = os.path.getsize(path) if os.path.isfile(path) else 0
        if size >= 19000:
            out.append(defects.row("WARN", "size", name, "scripts", "%d bytes, over 19000" % size, "split it into modules", name))
    return out


report.RULES_OF = dict(report.RULES_OF, size=tuple(report.RULES_OF["size"]) + ("scripts",))
report.RULES = tuple(report.RULES) + ("scripts",)
report.GROUP_OF = dict(report.GROUP_OF, scripts="size")
report.FUNCTIONS["scripts"] = scripts_rule
controls.CONTROLS["scripts"] = ("size", "scripts", lambda root: [])
sys.argv = [health] + sys.argv[1:]
runpy.run_path(health, run_name="__main__")
