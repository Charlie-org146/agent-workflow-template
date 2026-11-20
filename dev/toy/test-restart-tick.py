#!/usr/bin/env python3
# windows: skip
# reads: skills/workflow-monitoring/scripts/mailbox.py skills/workflow-monitoring/scripts/proctree.py
"""restart-tick (TD487): the 300 s launch agent and the watcher jobs a stopped session leaves. The installer writes a plist
(StartInterval 300, running the tick) into a temp folder and an uninstall removes it; a fake launchctl fails the toy if the
build ever loads, bootstraps or boots out anything. A job left by a stopped session is resumed once by the tick, with a fake
gh: clean green at the job's recorded head and --arm runs merge.py's own path once (the job id is the goal's slug, --go-head the head, as
the pod that wrote the job), another head waits, red records the failed checks and merges nothing. Only the operation session may
leave an --arm job (it names a head), and the tick reads and prints (checkin.py): it never runs operate.py run, watch.py or sessions.py assign."""
import json
import os
import plistlib
import shutil
import subprocess
import sys
import tempfile

here = os.path.dirname(os.path.abspath(__file__))
mailbox = os.path.join(here, "..", "..", "skills", "workflow-monitoring", "scripts", "mailbox.py")
failed = []


def check(ok, text):
    print(("PASS: " if ok else "FAIL: ") + text)
    if not ok:
        failed.append(text)


with tempfile.TemporaryDirectory() as tmp:
    bin_, agents, repo = (os.path.join(tmp, x) for x in ("bin", "agents", "repo"))
    # a copy of the monitoring scripts beside a stub merge.py: the tick finds merge.py by its path from mailbox.py, so the stub records each call
    tree = os.path.join(tmp, "skills")
    shutil.copytree(os.path.dirname(mailbox), os.path.join(tree, "workflow-monitoring", "scripts"), ignore=shutil.ignore_patterns("__pycache__"))
    os.makedirs(os.path.join(tree, "workflow-release", "scripts"))
    with open(os.path.join(tree, "workflow-release", "scripts", "merge.py"), "w") as handle:
        handle.write("import os, sys\nopen(os.path.join(os.environ['FAKE_DIR'], 'merge.log'), 'a').write(' '.join(sys.argv[1:]) + ' pod=' + os.environ.get('LOOP_POD_ID', '') + '\\n')\n"
                     "sys.exit(1 if sys.argv[1] == 'failgoal' else 0)\n")
    mailbox = os.path.join(tree, "workflow-monitoring", "scripts", "mailbox.py")
    os.makedirs(bin_)
    os.makedirs(repo)
    fake = {"gh": '#!/bin/sh\necho "$*" >> "$FAKE_DIR/gh.log"\nif [ "$1 $2" = "pr view" ]; then cat "$FAKE_DIR/pr-$3.json"; exit 0; fi\nexit 0\n',
            "launchctl": '#!/bin/sh\necho "$*" >> "$FAKE_DIR/launchctl.log"\nexit 1\n'}
    for name, text in fake.items():
        with open(os.path.join(bin_, name), "w") as handle:
            handle.write(text)
        os.chmod(os.path.join(bin_, name), 0o755)
    env = dict(os.environ, FAKE_DIR=tmp, LOOP_AGENTS_DIR=agents, LOOP_SCHEDULE_HOME=os.path.join(tmp, "sched"), LOOP_LAUNCHCTL=os.path.join(bin_, "launchctl"),
               PATH=bin_ + ":" + os.environ["PATH"], HOME=tmp)
    env.pop("CLAUDE_CODE_HOST_SESSION_ID", None)
    subprocess.run(["git", "init", "-q", "-b", "main", repo], check=True)
    subprocess.run(["git", "-c", "user.email=t@t", "-c", "user.name=t", "commit", "-q", "--allow-empty", "-m", "x"], cwd=repo, check=True)

    env.pop("LOOP_ROLE", None)
    os.makedirs(os.path.join(repo, ".git", "loop"))
    open(os.path.join(repo, ".git", "loop", "operation.id"), "w").write("ops-session\n")
    env["CLAUDE_SESSION_ID"] = "ops-session"

    def run(*argv, **extra):
        return subprocess.run([sys.executable, mailbox, *argv, "--root", repo], capture_output=True, text=True, cwd=repo, env=dict(env, **extra), timeout=120)

    got = run("install")
    path = os.path.join(agents, "com.workflow-loop.tick.plist")
    plist = plistlib.load(open(path, "rb")) if os.path.exists(path) else {}
    check(plist.get("StartInterval") == 300 and plist.get("ProgramArguments", [""])[2:3] == ["tick"] and plist.get("Label") == "com.workflow-loop.tick",
          "install writes a plist with StartInterval 300 that runs the tick: %s" % got.stdout.strip()[:60])
    check("not loaded" in got.stdout, "install says it did not load the agent")
    run("status")
    check(run("uninstall").returncode == 0 and not os.path.exists(path), "uninstall removes the plist")

    def pr(number, state, checks):
        with open(os.path.join(tmp, "pr-%d.json" % number), "w") as handle:
            json.dump({"state": state, "headRefOid": "a" * 40, "statusCheckRollup": checks}, handle)

    ok_ = {"name": "affected", "status": "COMPLETED", "conclusion": "SUCCESS"}
    pr(1, "OPEN", [ok_])
    pr(2, "OPEN", [ok_, {"name": "small", "status": "COMPLETED", "conclusion": "FAILURE"}])
    pr(3, "OPEN", [{"name": "affected", "status": "IN_PROGRESS", "conclusion": None}])
    pr(4, "OPEN", [ok_])
    pr(5, "OPEN", [ok_, {"context": "GitGuardian", "state": "PENDING"}])
    pr(6, "OPEN", [ok_, {"context": "GitGuardian", "state": "SUCCESS"}])
    pr(7, "OPEN", [ok_, {"context": "GitGuardian", "state": "FAILURE"}])
    for ident, number, arm in (("green", 1, True), ("red", 2, True), ("running", 3, True), ("report", 4, False), ("gg-pending", 5, True), ("gg-ok", 6, True), ("gg-bad", 7, True)):
        run("watch", ident, "--pr", str(number), *(["--arm", "--head", "a" * 40] if arm else []))  # as a session that then stopped
    folder = os.path.join(repo, ".git", "loop", "watchers")
    check(not os.path.exists(os.path.join(tmp, "merge.log")), "no job: nothing has called merge.py")
    nohead = run("watch", "nohead", "--pr", "9", "--arm")
    check(nohead.returncode != 0 and "--head" in nohead.stderr + nohead.stdout and not os.path.exists(os.path.join(folder, "nohead.json")),
          "an --arm job with no head is refused and nothing is written")
    pr(82, "OPEN", [ok_])
    run("watch", "movedhead", "--pr", "82", "--arm", "--head", "b" * 40)  # the pull request is at another head than the job names
    pr(83, "OPEN", [ok_])
    run("watch", "failgoal", "--pr", "83", "--arm", "--head", "a" * 40)  # merge.py refuses it
    refused = run("watch", "workerjob", "--pr", "9", "--arm", LOOP_ROLE="worker")
    check(refused.returncode != 0 and "REFUSED" in refused.stderr + refused.stdout and not os.path.exists(os.path.join(repo, ".git", "loop", "watchers", "workerjob.json")),
          "a worker's --arm job is refused and nothing is written")
    check(run("watch", "workerjob2", "--pr", "9", LOOP_ROLE="worker").returncode == 0, "a worker may still leave a report-only job")
    first = run("tick")
    state = {n[:-5]: json.load(open(os.path.join(folder, n))) for n in os.listdir(folder)}
    calls = open(os.path.join(tmp, "merge.log")).read().splitlines()
    called = lambda ident: [c for c in calls if c.split()[0] == ident]
    check(state["green"]["state"] == "armed" and called("green") == ["green --go-head " + "a" * 40 + " pod=ops-session"],
          "a clean green job with --arm calls merge.py's own path once, with the job's head and the pod that wrote the job")
    check(state["red"]["state"] == "red" and "small" in state["red"]["result"] and not called("red"), "a red job records the failed check and merges nothing")
    check(state["running"]["state"] == "waiting" and not called("running"), "a job whose checks still run is left waiting")
    check(state["report"]["state"] == "green" and not called("report"), "a green job without --arm is only reported")
    check(state["gg-pending"]["state"] == "waiting" and not called("gg-pending"), "a status check still pending (GitGuardian) keeps the job waiting")
    check(state["gg-ok"]["state"] == "armed" and len(called("gg-ok")) == 1, "a status check that succeeded (GitGuardian) lets it arm")
    check(state["gg-bad"]["state"] == "red" and "GitGuardian" in state["gg-bad"]["result"] and not called("gg-bad"), "a failed status check names GitGuardian and merges nothing")
    check(state["movedhead"]["state"] == "waiting" and "head moved" in state["movedhead"]["result"] and not called("movedhead"),
          "a job whose head is not the pull request's head waits, consumes nothing and calls nothing")
    check(state["failgoal"]["state"] == "arm-failed" and len(called("failgoal")) == 1, "a job merge.py refuses is consumed as arm-failed")
    run("tick")
    check(len(called_again := [c for c in open(os.path.join(tmp, "merge.log")).read().splitlines() if c.split()[0] in ("green", "gg-ok", "failgoal")]) == 3,
          "a second tick calls merge.py for none of them again (%d calls in all)" % len(called_again))
    check("next check-in" in first.stdout or "Coming up" in first.stdout, "the tick then prints the check-in")
    sys.path.insert(0, os.path.dirname(mailbox))
    import inspect
    import importlib.util
    spec = importlib.util.spec_from_file_location("mailbox_under_test", mailbox)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    body = inspect.getsource(module.cmd_tick)
    check(not any(word in body for word in ("operate.py", "watch.py", "sessions.py", "assign", "send")), "the tick's code never names operate.py, watch.py, sessions.py, assign or send")
    check("gh pr merge" not in open(mailbox).read() and '"pr", "merge"' not in open(mailbox).read(), "mailbox.py never merges itself: merge.py is the one merging script")
    used = open(os.path.join(tmp, "launchctl.log")).read() if os.path.exists(os.path.join(tmp, "launchctl.log")) else ""
    check(not any(word in used for word in ("bootstrap", "load", "bootout", "enable", "kickstart")), "nothing was loaded, bootstrapped or booted out: launchctl saw only %r" % used.strip())
sys.exit(1 if failed else 0)
