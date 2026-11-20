#!/usr/bin/env python3
# windows: skip
# reads: skills/workflow-monitoring/scripts/mailbox.py skills/workflow-monitoring/scripts/operate.py
"""restart-tick (TD487): the 300 s launch agent and the watcher jobs a stopped session leaves. The installer writes a plist
(StartInterval 300, running the tick) into a temp folder and an uninstall removes it; a fake launchctl fails the toy if the
build ever loads, bootstraps or boots out anything. A job left by a stopped session is resumed once by the tick, with a fake
gh: clean green and --arm queues the pull request, red records the failed checks and queues nothing."""
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

    def run(*argv):
        return subprocess.run([sys.executable, mailbox, *argv, "--root", repo], capture_output=True, text=True, env=env, timeout=120)

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
    for ident, number, arm in (("green", 1, True), ("red", 2, True), ("running", 3, True), ("report", 4, False)):
        run("watch", ident, "--pr", str(number), *(["--arm"] if arm else []))  # as a session that then stopped
    folder = os.path.join(repo, ".git", "loop", "watchers")
    first = run("tick")
    state = {n[:-5]: json.load(open(os.path.join(folder, n))) for n in os.listdir(folder)}
    log = open(os.path.join(tmp, "gh.log")).read()
    check(state["green"]["state"] == "armed" and log.count("pr merge 1 --auto --merge --match-head-commit " + "a" * 40) == 1,
          "a clean green job with --arm is queued once at its head")
    check(state["red"]["state"] == "red" and "small" in state["red"]["result"] and "pr merge 2" not in log, "a red job records the failed check and queues nothing")
    check(state["running"]["state"] == "waiting" and "pr merge 3" not in log, "a job whose checks still run is left waiting")
    check(state["report"]["state"] == "green" and "pr merge 4" not in log, "a green job without --arm is only reported")
    run("tick")
    check(open(os.path.join(tmp, "gh.log")).read().count("pr merge 1") == 1, "a second tick does not queue it again")
    check("next check-in" in first.stdout or "Coming up" in first.stdout, "the tick then runs the operate pass and prints the check-in")
    used = open(os.path.join(tmp, "launchctl.log")).read() if os.path.exists(os.path.join(tmp, "launchctl.log")) else ""
    check(not any(word in used for word in ("bootstrap", "load", "bootout", "enable", "kickstart")), "nothing was loaded, bootstrapped or booted out: launchctl saw only %r" % used.strip())
sys.exit(1 if failed else 0)
