#!/usr/bin/env python3
# windows: ok
# reads: skills/workflow-monitoring/scripts/sessions.py skills/workflow-monitoring/scripts/worker.py skills/workflow-monitoring/scripts/mailbox.py
"""#3868: a goal's pull request merges only through its own merge.py, never as a side effect of a report.

Two goals sit at pr in a repo with auto_merge on. A session report for one of them (waiting, or merged for a PR that is
still open) must not run merge.py for either; merge.py for one goal runs only when asked for that goal."""
import argparse
import ast
import copy
import contextlib
import io
import json
import os
import subprocess
import sys
import tempfile
import types

here = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(here, "..", "..", "skills", "workflow-monitoring", "scripts"))
import sessions  # noqa: E402
import worker  # noqa: E402

failed = []


def check(ok, text):
    print(("PASS: " if ok else "FAIL: ") + text)
    if not ok:
        failed.append(text)


real = subprocess.run
calls = []


def run(command, *a, **k):
    if isinstance(command, list) and any("merge.py" in str(part) for part in command) or isinstance(command, list) and command[:3] == ["gh", "pr", "merge"]:
        calls.append(command)
        return type("R", (), {"returncode": 0, "stdout": "", "stderr": ""})()
    return real(command, *a, **k)


subprocess.run = run
worker.merged = sessions.merged = lambda url: False


def report(slug, status, text="PR open; holding before merge.py", hold=False):
    args = argparse.Namespace(hold=hold, slug=slug, status=status, step="", pr="https://example.test/pull/" + slug[-1], ask="", words=[],
                              text=text, recommend="", kind="", attempt=None)
    out = io.StringIO()
    with contextlib.redirect_stdout(out):
        try:
            sessions.cmd_report(args)
        except SystemExit as stop:
            out.write("(exit: %s)" % stop)
    return out.getvalue()


with tempfile.TemporaryDirectory() as tmp:
    real(["git", "init", "-q", tmp], check=True)
    os.makedirs(os.path.join(tmp, ".loop"))
    with open(os.path.join(tmp, ".loop", "config.json"), "w") as handle:
        json.dump({"auto_merge": True}, handle)
    os.chdir(tmp)
    runs = os.path.join(tmp, ".git", "loop", "runs")
    os.makedirs(runs)
    for slug in ("goal1", "goal2"):
        with open(os.path.join(runs, slug + ".json"), "w") as handle:
            json.dump({"slug": slug, "status": "running", "step": "pr", "worktree": tmp, "branch": "loop/" + slug,
                       "pr": "https://example.test/pull/" + slug[-1]}, handle)
    said = report("goal1", "waiting")
    check("NEXT: merge.py goal1" in said, "the report prints NEXT: merge.py for the goal instead of merging it")
    check(not calls, "a waiting report for a goal at pr, with auto_merge on, runs no merge.py")
    report("goal2", "merged")
    check(not calls, "a merged report for a PR that is still open runs no merge.py for either goal")
    state = sessions.load("goal1")
    check(state.get("status") == "done" and state.get("pr"), "the report still records the goal as done with its pull request")
    worker.release_step(dict(state, release=""))
    check(len(calls) == 1 and calls[0][-1] == "goal1", "the release step for one goal runs merge.py for only that goal")
    # the worker's exit fallback goes through merge.py, and skips a goal the operation holds
    del calls[:]
    with open(os.path.join(runs, "goal3.json"), "w") as handle:
        json.dump({"slug": "goal3", "status": "running", "step": "pr", "worktree": tmp, "branch": "loop/goal3", "pr": "https://example.test/pull/3"}, handle)
    report("goal3", "waiting", "worker · goal3: PR open; holding before merge.py")
    held = sessions.load("goal3")
    check(worker.held_by_operation(held), "a goal whose last report says it is holding before merge.py is held by the operation")
    worker.release_step(dict(held, release=""))
    check(not calls, "the worker's exit fallback skips a goal the operation holds")
    check(not worker.held_by_operation(sessions.load("goal1")), "a goal that only reported its pull request waiting is not held")
    report("goal2", "waiting", "PR open, wait for the go", hold=True)  # wording says nothing about holding
    held2 = sessions.load("goal2")
    check(worker.held_by_operation(held2), "report --hold holds a goal whatever the report says")
    del calls[:]
    worker.release_step(dict(held2, release=""))
    check(not calls, "the worker's exit fallback skips a goal held with --hold")
    os.chdir(here)
subprocess.run = real
# TD499 / PR 5608 intentionally added the operation's armed watcher job as a second caller.
# Check the launch's function and exercise that function through tick; a file-wide allowlist is insufficient.
def mailbox_errors(source):
    tree = ast.parse(source)
    functions = {node.name: node for node in tree.body if isinstance(node, ast.FunctionDef)}
    resume = functions.get("resume")
    tick = functions.get("cmd_tick")
    if resume is None or tick is None:
        return ["mailbox lacks resume or cmd_tick"]
    if any(isinstance(node, (ast.List, ast.Tuple))
           and [part.value if isinstance(part, ast.Constant) else None for part in node.elts[:3]] == ["gh", "pr", "merge"]
           for node in ast.walk(tree)):
        return ["mailbox must merge through merge.py, never gh pr merge"]
    launches = [node for node in ast.walk(tree) if isinstance(node, ast.Call)
                and isinstance(node.func, ast.Attribute) and node.func.attr == "run"
                and any(isinstance(part, ast.Name) and part.id == "MERGE" for part in ast.walk(node))]
    if len(launches) != 1 or launches[0] not in list(ast.walk(resume)):
        return ["mailbox merge.py launch must be in resume, reached through cmd_tick's job files"]
    # A second literal launch or a use of MERGE outside this command must not inherit the exception.
    assignment = next((node for node in tree.body if isinstance(node, ast.Assign)
                       and any(isinstance(target, ast.Name) and target.id == "MERGE" for target in node.targets)), None)
    allowed = list(ast.walk(launches[0])) + (list(ast.walk(assignment)) if assignment else [])
    if any((isinstance(node, ast.Name) and node.id == "MERGE"
            or isinstance(node, ast.Constant) and node.value == "merge.py") and node not in allowed
           for node in ast.walk(tree)):
        return ["mailbox starts or references merge.py outside its guarded job launch"]

    # Execute only the real tick/resume definitions, with all external effects replaced.
    # No import of mailbox, real gh call, or real merge can occur in these probes.
    module = ast.Module(body=[resume, tick], type_ignores=[])
    errors = []
    with tempfile.TemporaryDirectory() as folder:
        launched = []

        def probe_run(command, **kwargs):
            if "merge.py" in command:
                launched.append(command)
            return types.SimpleNamespace(returncode=0, stdout="", stderr="")

        def read_job(path):
            with open(path, encoding="utf-8") as handle:
                return json.load(handle)

        scope = {"os": os, "sys": sys, "HERE": folder, "MERGE": "merge.py", "now": lambda: "now",
                 "jobs_dir": lambda root: folder, "read_json": read_job, "write_json": lambda *args: None,
                 "subprocess": types.SimpleNamespace(run=probe_run)}
        exec(compile(module, "mailbox tick probe", "exec"), scope)
        job = {"id": "only-this-goal", "pr": 42, "state": "waiting", "arm": True, "head": "exact-head"}
        green = {"state": "OPEN", "headRefOid": "exact-head",
                 "statusCheckRollup": [{"status": "COMPLETED", "conclusion": "SUCCESS"}]}
        cases = [("no job file", None, green, False), ("no job record", {}, green, False),
                 ("nonwaiting job record", dict(job, state="done"), green, False),
                 ("invalid PR record", dict(job, pr="42"), green, False),
                 ("unarmed job", dict(job, arm=False), green, False),
                 ("moved head", dict(job, head="old-head"), green, False),
                 ("pending checks", job, dict(green, statusCheckRollup=[{"status": "PENDING"}]), False),
                 ("red checks", job, dict(green, statusCheckRollup=[{"conclusion": "FAILURE"}]), False),
                 ("armed job at exact head", job, green, True)]
        for label, record, result, expected in cases:
            launched.clear()
            if record is not None:
                with open(os.path.join(folder, "job.json"), "w", encoding="utf-8") as handle:
                    json.dump(record, handle)
            scope["gh_json"] = lambda *args: result
            try:
                with contextlib.redirect_stdout(io.StringIO()):
                    scope["cmd_tick"](types.SimpleNamespace(root=folder))
            except Exception as exc:
                errors.append("%s: %s" % (label, type(exc).__name__))
                continue
            wanted = [[sys.executable, "merge.py", job["id"], "--go-head", job["head"]]] if expected else []
            if launched != wanted:
                errors.append("%s: unexpected merge commands %r" % (label, launched))
    return errors


MAILBOX = "workflow-monitoring/mailbox.py"
WORKER = "workflow-monitoring/worker.py"


def caller_errors(sources):
    def names_merge(source):
        nodes = list(ast.walk(ast.parse(source)))
        return any(isinstance(node, ast.Constant) and node.value == "merge.py" for node in nodes) or any(
            isinstance(node, (ast.List, ast.Tuple))
            and [part.value if isinstance(part, ast.Constant) else None for part in node.elts[:3]] == ["gh", "pr", "merge"]
            for node in nodes)

    callers = sorted(name for name, source in sources.items() if names_merge(source))
    errors = [] if callers == [MAILBOX, WORKER] else ["unexpected callers: %r" % callers]
    if MAILBOX in sources:
        errors.extend(mailbox_errors(sources[MAILBOX]))
    return errors


scripts = os.path.join(here, "..", "..", "skills")
sources = {}
for folder in ("workflow-monitoring", "workflow-delivery"):
    for name in sorted(os.listdir(os.path.join(scripts, folder, "scripts"))):
        if name.endswith(".py"):
            with open(os.path.join(scripts, folder, "scripts", name), encoding="utf-8") as handle:
                sources[folder + "/" + name] = handle.read()
errors = caller_errors(sources)
check(not errors, "only worker.py and mailbox.py's guarded tick-job path start merge.py: %s" % (errors or "OK"))

third = dict(sources, **{"toy-third.py": 'subprocess.run([sys.executable, "merge.py", "other-goal"])'})
errors = caller_errors(third)
check(any("toy-third.py" in error for error in errors), "negative control: third caller rejected: %s" % errors)

# Remove the waiting/PR record guard from a toy copy, keeping its launch and the rest of the path intact.
mutant = copy.deepcopy(ast.parse(sources[MAILBOX]))
resume = next(node for node in mutant.body if isinstance(node, ast.FunctionDef) and node.name == "resume")
guard = next(node for node in resume.body if isinstance(node, ast.If))
resume.body.remove(guard)
errors = caller_errors(dict(sources, **{MAILBOX: ast.unparse(mutant)}))
check(any("nonwaiting job record: unexpected merge commands" in error for error in errors),
      "negative control: mailbox tick without job-record guard rejected: %s" % errors)
if not failed:
    print("PASS: #3868: report --hold holds a goal whatever its wording says")
    print("PASS: #3868: a report merges neither goal; merge.py runs only for the goal it is asked for")
    print("PASS: #3868: the worker exit fallback runs merge.py for an unheld goal and skips a held one")
sys.exit(1 if failed else 0)
