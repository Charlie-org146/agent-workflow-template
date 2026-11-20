#!/usr/bin/env python3
# windows: skip
# reads: .github/workflows/release.yml
"""TD507: no release is made while main is red. release.yml first asks GitHub for open issues labeled main-red (one gh call);
if any is open the job prints "held: main red (#N)", ends green and every later step is skipped; with none open it releases as
before. The hold step's own script is run here with a fake gh, once with an open issue and once with none; a negative control
shows the check is what holds (without it nothing is printed and no step is gated)."""
import os
import re
import subprocess
import sys
import tempfile

here = os.path.dirname(os.path.abspath(__file__))
YML = os.path.join(here, "..", "..", ".github", "workflows", "release.yml")
failed = []


def check(ok, text):
    print(("PASS: " if ok else "FAIL: ") + text)
    if not ok:
        failed.append(text)


def steps(text):
    body = text.split("    steps:\n", 1)[1]
    return [s for s in re.split(r"(?m)^      - ", body) if s.strip()]


def hold_script(text):
    for step in steps(text):
        if step.startswith("id: hold"):
            return step.split("run: |\n", 1)[1]
    return None


def run_hold(script, open_issues):
    with tempfile.TemporaryDirectory() as tmp:
        gh = os.path.join(tmp, "gh")
        with open(gh, "w") as handle:  # the fake prints what `gh issue list --jq` would print, and records its arguments
            handle.write('#!/bin/sh\necho "$@" >> "%s/args"\nprintf "%%s" "$FAKE_OPEN"\n' % tmp)
        os.chmod(gh, 0o755)
        out = os.path.join(tmp, "out")
        done = subprocess.run(["bash", "-c", script], capture_output=True, text=True, env=dict(
            os.environ, PATH=tmp + os.pathsep + os.environ["PATH"], GITHUB_OUTPUT=out, GITHUB_REPOSITORY="o/r", FAKE_OPEN=open_issues))
        written = open(out).read() if os.path.exists(out) else ""
        args = open(os.path.join(tmp, "args")).read() if os.path.exists(os.path.join(tmp, "args")) else ""
        return done.returncode, done.stdout, written, args


text = open(YML).read()
script = hold_script(text)
check(script is not None and steps(text)[0].startswith("id: hold"), "the hold step is the first step of the release job")
rc, out, written, args = run_hold(script or "exit 1", "#12")
check(rc == 0 and "held: main red (#12)" in out and "held=1" in written, "an open main-red issue: the job prints held: main red (#12) and sets held=1, ending green")
check(args.count("\n") == 1 and "--label main-red" in args and "--state open" in args, "the check is one gh issue list call for the main-red label, open issues only")
rc, out, written, args = run_hold(script or "exit 1", "")
check(rc == 0 and "held" not in out and written == "", "no open main-red issue: nothing is printed and held is not set, so the release goes ahead")
later = [s for s in steps(text)[1:]]
check(later and all("steps.hold.outputs.held != '1'" in s for s in later), "every step after the hold step is skipped while held")
check("issues: read" in text.split("jobs:")[0], "the job may read issues")
# negative control: the same file with the hold step cut out holds nothing
cut = text.replace("      - id: hold\n" + (script and "        run: |\n" + script or ""), "", 1)
check(hold_script(cut) is None and not any(s.startswith("id: hold") for s in steps(cut)), "negative control: a workflow with the hold step removed has no hold, so the checks above would fail")
if failed:
    sys.exit(1)
print("PASS: TD507: release.yml holds while an issue labeled main-red is open, and releases when none is")
