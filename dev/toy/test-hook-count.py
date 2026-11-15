#!/usr/bin/env python3
# windows: ok
# reads: skills/workflow-health/scripts/lean.py skills/workflow-health/scripts/rules.py skills/workflow-health/scripts/report.py
"""hook-count (#4345): MIG_HOOKS counts hook entries, not how often a script's name appears.

Every hook command names its script twice (an existence test, then the run), so counting the name reported one installed
hook as "installed 2 times". Builds settings.local.json files with one entry, two entries and none for each hook script and
reads the gaps lean.hook_gaps reports."""
import json
import os
import sys
import tempfile

root = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
sys.path.insert(0, os.path.join(root, "skills", "workflow-health", "scripts"))
sys.dont_write_bytecode = True
import lean  # noqa: E402

failed = []
NAMES = ("reply_hook.py", "govern_hook.py")


def check(ok, text):
    print(("PASS: " if ok else "FAIL: ") + text)
    if not ok:
        failed.append(text)


def entry(name):
    command = "if [ -f '/x/%s' ]; then python3 '/x/%s'; fi" % (name, name)
    return {"matcher": "", "hooks": [{"type": "command", "command": command}]}


def gaps(per_script):
    """The (code, subject) gaps and the owner steps hook_gaps reports for a settings file with per_script entries each."""
    with tempfile.TemporaryDirectory() as repo:
        os.makedirs(os.path.join(repo, ".claude"))
        hooks = {"Stop": [entry(n) for n in NAMES for _ in range(per_script)]} if per_script else {}
        with open(os.path.join(repo, ".claude", "settings.local.json"), "w") as handle:
            json.dump({"hooks": hooks}, handle)
        found, steps = [], []
        lean.hook_gaps(repo, lambda code, subject, what, fix: found.append((code, subject, what)), steps)
        return found, steps


found, steps = gaps(1)
check(not found and not steps, "one entry for each hook is not reported as a duplicate")
found, steps = gaps(2)
check(sorted(s for _, s, _ in found) == sorted(NAMES) and all("2 times" in w for _, _, w in found),
      "two entries for a hook are reported as installed 2 times")
found, steps = gaps(0)
check(not found and len(steps) == 2, "no entry for a hook asks for the install step, not a duplicate")
sys.exit(1 if failed else 0)
