#!/usr/bin/env python3
# windows: ok
# reads: skills/workflow-delivery/scripts/role.py skills/workflow-delivery/scripts/private.py skills/workflow-delivery/scripts/lane.py skills/workflow-regression/scripts/narrow.py skills/workflow-delivery/scripts/flow.py
# reads: skills/workflow-docs/scripts/render.py skills/workflow-docs/scripts/counting.py
"""Defects 3841, 3840, 3839 and 4184. usage: test-defects-a.py CASE (3841 | 3840 | 3839 | 4184); exit 0 when it holds.
No model, no network: a throwaway repo, and gh is replaced by a function."""
import json
import os
import subprocess
import sys
import tempfile

here = os.path.dirname(os.path.abspath(__file__))
top = os.path.abspath(os.path.join(here, "..", ".."))
for skill in ("delivery", "docs", "monitoring"):
    sys.path.insert(0, os.path.join(top, "skills", "workflow-" + skill, "scripts"))
os.environ.pop("LOOP_ROLE", None)


def repo():
    path = tempfile.mkdtemp()
    subprocess.run(["git", "-c", "user.name=t", "-c", "user.email=t@t", "init", "-q", path], check=True)
    os.makedirs(os.path.join(path, ".loop"))
    return path


def write(path, text):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as handle:
        handle.write(text)


def home_in_body():
    """3841: the lane's results in a pull request body name no home folder, in a Unix or a Windows form."""
    import role
    tmp = repo()
    runs = os.path.join(tmp, ".git", "loop", "runs", "g.pr-lane")
    write(runs + ".last", json.dumps({"line": "LANE pr AFFECTED 3/3 in 9s; log: C:\\Users\\zed\\code\\r\\log.txt; saw /Users/zed/code/r/x.txt and C:\\Users\\zed\\code\\r"}))
    write(runs + ".txt", "SELECTED a-row (C:\\Users\\zed\\code\\r\\a.sh) /home/zed/code/r/b.sh\nUNMAPPED C:/Users/zed/code/r/c.py\n")
    os.chdir(tmp)
    body = role.lane_part("g")
    print(body)
    return bool(body) and "zed" not in body


def statuses():
    """3840: a required check gets a status only when its workflow job runs the lane's own regression command; the others are BLOCKS."""
    import private
    tmp = repo()
    write(os.path.join(tmp, ".github", "workflows", "ci.yml"), "jobs:\n  regression:\n    name: regression\n    steps:\n      - run: python3 skills/workflow-regression/scripts/regression.py run land\n"
          "  stories:\n    name: stories\n    steps:\n      - run: npm run build-storybook\n      - run: python3 skills/workflow-regression/scripts/regression.py run land\n")
    posted = []
    private.repo_is_private = lambda root: True
    private.required_checks = lambda root, base: (["regression", "stories", "Cloudflare Pages"], [])
    private.post_statuses = lambda root, head, ok, contexts: posted.extend(contexts) or True
    private.pr_result(tmp, "main", "a" * 40, "loop/g", True)
    print("posted: %s" % posted)
    return posted == ["regression"]


def workflow_link():
    """3839: the Tests links name the workflow file the automation registry points the regression routine at."""
    import render
    tmp = repo()
    write(os.path.join(tmp, ".loop", "config.json"), json.dumps({"automation": [{"name": "regression", "does": "x", "cadence": "off", "runs": "github:nightly.yml"}]}))
    flow = render.workflow_file(tmp)
    cell = render.run_cell("", "o/r", "2026-11-14", flow)
    print(cell)
    other = repo()
    return flow == "nightly.yml" and "workflows/nightly.yml" in cell and render.workflow_file(other) == "regression.yml"


def app_refuses():
    """4184: with workers: app, flow.py refuses a step for a goal with no bound session and names sessions.py bind; a bound goal is not refused."""
    tmp = repo()
    flow = os.path.join(tmp, "flow.json")
    write(flow, json.dumps({"steps": dict.fromkeys(("idea", "plan", "build", "review", "qa", "ship"), "built-in"), "command": ["true"]}))
    write(os.path.join(tmp, ".loop", "config.json"), json.dumps({"workers": "app", "base": "main"}))
    script = os.path.join(top, "skills", "workflow-delivery", "scripts", "flow.py")
    env = dict(os.environ, LOOP_FLOW=flow, LOOP_ROLE="worker")

    def run(worker):
        write(os.path.join(tmp, ".git", "loop", "runs", "g.json"), json.dumps({"slug": "g", "worker": worker, "status": "running", "step": "idea"}))
        done = subprocess.run([sys.executable, script, "g", "idea"], cwd=tmp, capture_output=True, text=True, env=env)
        return done.returncode, done.stdout + done.stderr

    code, said = run("app")
    print(said)
    return code != 0 and "sessions.py bind g" in said and "NO_SESSION" in said and "NO_SESSION" not in run("session")[1]


CASES = {"3841": home_in_body, "3840": statuses, "3839": workflow_link, "4184": app_refuses}
case = sys.argv[1] if len(sys.argv) > 1 else ""
try:
    held = CASES[case]()
except Exception as error:  # a missing function is a red result, not a crash
    print("%s: %s" % (type(error).__name__, error))
    held = False
print(("PASS: " if held else "FAIL: ") + CASES.get(case, lambda: None).__doc__.split(":")[0] + " " + case if case in CASES else "FAIL: no case " + case)
sys.exit(0 if held else 1)
