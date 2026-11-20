#!/usr/bin/env python3
# windows: skip
# reads: skills/workflow-monitoring/scripts/mailbox.py skills/workflow-monitoring/scripts/proctree.py
"""restart-tick (TD487): the 300 s launch agent and the watcher jobs a stopped session leaves. The installer writes a plist
(StartInterval 300, running the tick) into a temp folder and an uninstall removes it; a fake launchctl fails the toy if the
build ever loads, bootstraps or boots out anything. A job left by a stopped session is resumed once by the tick, with a fake
gh: clean green and --arm queues the pull request, red records the failed checks and queues nothing. Only the operation session
may leave an --arm job, and the tick reads and prints (checkin.py): it never runs operate.py run, watch.py or sessions.py assign."""
import json
import os
import plistlib
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
        run("watch", ident, "--pr", str(number), *(["--arm"] if arm else []))  # as a session that then stopped
    folder = os.path.join(repo, ".git", "loop", "watchers")
    refused = run("watch", "workerjob", "--pr", "9", "--arm", LOOP_ROLE="worker")
    check(refused.returncode != 0 and "REFUSED" in refused.stderr + refused.stdout and not os.path.exists(os.path.join(repo, ".git", "loop", "watchers", "workerjob.json")),
          "a worker's --arm job is refused and nothing is written")
    check(run("watch", "workerjob2", "--pr", "9", LOOP_ROLE="worker").returncode == 0, "a worker may still leave a report-only job")
    pr(80, "OPEN", [ok_])
    pr(81, "OPEN", [ok_])
    run("watch", "headok", "--pr", "80", "--arm", "--head", "a" * 40)  # the head the operation session saw
    run("watch", "headbad", "--pr", "81", "--arm", "--head", "b" * 40)  # the pull request has moved to another head since
    first = run("tick")
    state = {n[:-5]: json.load(open(os.path.join(folder, n))) for n in os.listdir(folder)}
    log = open(os.path.join(tmp, "gh.log")).read()
    check(state["green"]["state"] == "armed" and log.count("pr merge 1 --auto --merge --match-head-commit " + "a" * 40) == 1,
          "a clean green job with --arm is queued once at its head")
    check(state["red"]["state"] == "red" and "small" in state["red"]["result"] and "pr merge 2" not in log, "a red job records the failed check and queues nothing")
    check(state["running"]["state"] == "waiting" and "pr merge 3" not in log, "a job whose checks still run is left waiting")
    check(state["report"]["state"] == "green" and "pr merge 4" not in log, "a green job without --arm is only reported")
    check(state["gg-pending"]["state"] == "waiting" and "pr merge 5" not in log, "a status check still pending (GitGuardian) keeps the job waiting")
    check(state["gg-ok"]["state"] == "armed" and "pr merge 6 " in log, "a status check that succeeded (GitGuardian) lets it arm")
    check(state["gg-bad"]["state"] == "red" and "GitGuardian" in state["gg-bad"]["result"] and "pr merge 7" not in log, "a failed status check names GitGuardian and arms nothing")
    run("tick")
    check(open(os.path.join(tmp, "gh.log")).read().count("pr merge 1") == 1, "a second tick does not queue it again")
    log = open(os.path.join(tmp, "gh.log")).read()
    state = {n[:-5]: json.load(open(os.path.join(folder, n))) for n in os.listdir(folder)}
    check(state["headok"]["state"] == "armed" and log.count("pr merge 80 --auto --merge --match-head-commit " + "a" * 40) == 1,
          "a job whose recorded head is the pull request's head arms, once, and a second tick refuses to arm it again (armed is consumed)")
    check(state["headbad"]["state"] == "refused" and "head moved" in state["headbad"]["result"] and "pr merge 81" not in log,
          "negative control: a job whose recorded head is not the pull request's head refuses and queues nothing")
    check("next check-in" in first.stdout or "Coming up" in first.stdout, "the tick then prints the check-in")
    sys.path.insert(0, os.path.dirname(mailbox))
    import inspect
    import importlib.util
    spec = importlib.util.spec_from_file_location("mailbox_under_test", mailbox)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    body = inspect.getsource(module.cmd_tick)
    check(not any(word in body for word in ("operate.py", "watch.py", "sessions.py", "assign", "send")), "the tick's code never names operate.py, watch.py, sessions.py, assign or send")
    used = open(os.path.join(tmp, "launchctl.log")).read() if os.path.exists(os.path.join(tmp, "launchctl.log")) else ""
    check(not any(word in used for word in ("bootstrap", "load", "bootout", "enable", "kickstart")), "nothing was loaded, bootstrapped or booted out: launchctl saw only %r" % used.strip())
sys.exit(1 if failed else 0)
