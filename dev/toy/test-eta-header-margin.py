#!/usr/bin/env python3
# windows: ok
# reads: skills/workflow-monitoring/scripts/auto.py skills/workflow-monitoring/scripts/checkin.py skills/workflow-monitoring/scripts/board_status.py
# reads: skills/workflow-delivery/scripts/fit.py skills/workflow-setup/scripts/settings.py
"""eta-header-margin (#4519, #4528): the release header's ETA uses the goals' hard ETAs, and the ETA margin is a repo setting.

Renders the real check-in (checkin.render) of a throwaway repo, so the path from run records through the Dependencies block to the release header is the one
the operation reads, not only the helper. No model, no network."""
import datetime
import json
import os
import re
import subprocess
import sys
import tempfile
from types import SimpleNamespace

root = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
for skill in ("delivery", "monitoring", "setup"):
    sys.path.insert(0, os.path.join(root, "skills", "workflow-" + skill, "scripts"))
sys.dont_write_bytecode = True
os.environ.pop("LOOP_ROLE", None)
import auto  # noqa: E402
import checkin  # noqa: E402
import fit  # noqa: E402
import settings  # noqa: E402

failed = []


def check(ok, text):
    print(("PASS: " if ok else "FAIL: ") + text)
    if not ok:
        failed.append(text)


def stamp(at):
    return at.strftime("%Y-%m-%dT%H:%M:%SZ")


with tempfile.TemporaryDirectory() as tmp, tempfile.TemporaryDirectory() as home:
    for key in ("HOME", "USERPROFILE"):
        os.environ[key] = home
    top = os.path.join(tmp, "toyrepo")
    subprocess.run(["git", "init", "-q", "-b", "main", top], check=True)
    os.makedirs(os.path.join(top, ".loop"))
    with open(os.path.join(top, ".loop", "config.json"), "w") as handle:
        json.dump({"base": "main"}, handle)
    with open(os.path.join(top, ".loop", "queue.md"), "w") as handle:
        handle.write("## Batch: v1-1\n- slug: hardgoal | goal: Hard goal | done: x\n- slug: estgoal | goal: Estimated goal | done: x\n")
    runs = os.path.join(top, ".git", "loop", "runs")
    os.makedirs(runs)
    os.chdir(top)  # the check-in also reads the repo it runs in: keep this repo's own goals out of the header
    now = datetime.datetime.now(datetime.timezone.utc)
    flow = ["queued", "idea", "plan", "build", "review", "qa", "ship", "pr"]

    def write(slug, **more):
        base = {"slug": slug, "goal": "Goal " + slug, "status": "running", "step": "build", "worker": "session", "pid": os.getpid(),
                "updated": stamp(now), "report": {"at": stamp(now), "text": "working"}, "waits_on": [],
                "log": ["%s %s" % (stamp(now - datetime.timedelta(minutes=40 - 5 * n)), step) for n, step in enumerate(flow[:4])]}
        with open(os.path.join(runs, slug + ".json"), "w") as handle:
            json.dump(dict(base, **more), handle)

    hist = ["%s %s" % (stamp(now - datetime.timedelta(hours=9) + datetime.timedelta(minutes=10 * n)), step) for n, step in enumerate(flow)]
    write("hist", status="done", step="pr", release="merged", log=hist)  # gives every step an estimate

    def header():
        text = " ".join("\n".join(checkin.render(top, now)).split())  # the printed map wraps long lines
        return re.search(r"-- v1\.1 release ETA .*? --", text).group(0)

    def clock(seconds):
        return (now + datetime.timedelta(seconds=seconds)).astimezone().strftime("%H:%M")

    def seconds(slug):
        record = json.load(open(os.path.join(runs, slug + ".json")))
        every = checkin.lb.load(top)
        return (auto.eta_left(auto.eta_seen(top, record), now), checkin.bs.left_time(record, every, now))

    # Done 1: one goal at a hard ETA, one estimated goal: the header takes the later of the two
    write("estgoal")
    write("hardgoal", eta={"minutes": 900, "estimate": 700, "basis": "estimate"})
    hard, _ = seconds("hardgoal")
    _, est = seconds("estgoal")
    check(hard and est and hard > est, "set-up: the hard ETA (%s s) is later than the estimate (%s s)" % (hard, est))
    line = header()
    check("~" + clock(hard) in line and "hard ETA for 1, estimate for 1" in line and "(2 goals, 0 not started;" in line,
          "the release header takes the hard ETA when it is later, and says which it used: %s" % line)
    write("hardgoal", eta={"minutes": 30, "estimate": 20, "basis": "estimate"})
    hard, _ = seconds("hardgoal")
    check(hard is not None and hard < est, "set-up: now the hard ETA (%s s) is earlier than the estimate (%s s)" % (hard, est))
    line = header()
    check("~" + clock(est) in line and "hard ETA for 1, estimate for 1" in line, "an estimated goal later than the hard ETA sets the header: %s" % line)
    write("hardgoal", eta={"minutes": 1, "estimate": 1, "basis": "estimate"})
    check(seconds("hardgoal")[0] == 0 and "~" + clock(est) in header(), "a goal past its hard ETA counts as none left, the estimate still decides")

    # negative controls: no hard ETA reads as today; an ETA that has not started (open pre-flight items) counts as an estimate
    write("hardgoal")
    line = header()
    check("hard ETA" not in line and "(2 goals, 0 not started)" in line and line.startswith("-- v1.1 release ETA "), "negative control: a board with no hard ETAs reads as it does today: %s" % line)
    write("hardgoal", eta={"minutes": 900, "estimate": 700, "basis": "estimate"},
          preflight={"items": [{"id": "plan", "ask": "x", "options": ["a"], "recommend": "a"}]})
    check(seconds("hardgoal")[0] is None and "hard ETA" not in header(), "negative control: a goal whose ETA waits for its pre-flight answers counts by estimate")

    # Done 2: the margin is a repo setting; 40 percent moves a goal's hard ETA, the default gives today's value
    rows = {row[0]: row for row in settings.TABLE}
    check("eta_margin_percent" in rows and rows["eta_margin_percent"][2] == 25 and "ETA" in rows["eta_margin_percent"][3], "the settings table lists eta_margin_percent with its default of 25")
    check(auto.eta_margin({}) == 1.25 and auto.eta_margin({"eta_margin_percent": 40}) == 1.4 and auto.eta_margin({"eta_margin_percent": 0}) == 1.0,
          "the margin factor reads the setting (default 25 percent)")
    check(all(auto.eta_margin({"eta_margin_percent": bad}) == 1.25 for bad in (-5, 999, "forty", True, None)), "negative control: a value out of range or not a number reads as the default 25")
    real = auto.bs.estimate_full
    auto.bs.estimate_full = lambda *args, **more: (0, 0, 3600, False)  # a one-hour estimate
    try:
        make = lambda **cfg: fit.frozen_fields(SimpleNamespace(root=lambda: top, config=lambda: dict({"base": "main", "time_budget_minutes": 240}, **cfg)),
                                               SimpleNamespace(slug="m", goal="a goal"), ["1. one"], [])["eta"]
        default, wider = make(), make(eta_margin_percent=40)
    finally:
        auto.bs.estimate_full = real
    check(default["minutes"] == 75 and "25% margin" in default["basis"], "the default margin gives today's value: 60 minutes plus 25 percent is 75 (%s)" % default)
    check(wider["minutes"] == 85 and "40% margin" in wider["basis"], "a 40 percent setting moves the hard ETA to 85 minutes and the basis names it (%s)" % wider)
    os.chdir(os.path.dirname(os.path.abspath(__file__)))  # leave the temp repo before it is removed
sys.exit(1 if failed else 0)
