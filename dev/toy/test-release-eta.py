#!/usr/bin/env python3
# windows: ok
# reads: skills/workflow-monitoring/scripts/layers.py skills/workflow-monitoring/scripts/machines.py
"""release-eta (v2.1): the finish is forecast from MEASURED merge pace (median and quartiles of the last 5 merge gaps, MERGE-GO
and CI waits included), each worker's STATUS line carries eta, eta_basis and slip, a slip over 15 minutes sends STATUS at once,
and the owner's release target and freeze come from a release record. The first fixture is the night's measured gaps
(merges at 21:26, 22:10, 22:59, 23:21, 23:41). Builds a throwaway repo with a bare origin; no model, no network."""
import json
import os
import subprocess
import sys
import tempfile
import time

root = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
sys.path.insert(0, os.path.join(root, "skills", "workflow-monitoring", "scripts"))
os.environ.update(GIT_AUTHOR_NAME="t", GIT_AUTHOR_EMAIL="t@t", GIT_COMMITTER_NAME="t", GIT_COMMITTER_EMAIL="t@t", LOOP_FLOW="/nonexistent")
import layers  # noqa: E402
import machines  # noqa: E402

failed = []


def check(ok, text):
    print(("PASS: " if ok else "FAIL: ") + text)
    if not ok:
        failed.append(text)


def git(*args, cwd, env=None):
    done = subprocess.run(["git"] + list(args), cwd=cwd, capture_output=True, text=True, env=dict(os.environ, **(env or {})))
    return done.stdout.strip()


# 1. the pure part, on the night's gaps
gaps = [44, 49, 22, 20]
found = machines.pace(gaps)
check(found == {"q25": 22, "median": 33.0, "q75": 49}, "the last gaps 44, 49, 22, 20 give a median of 33 minutes and quartiles 22 and 49 (%s)" % found)
check(machines.pace([44, 49]) is None, "fewer than 3 gaps gives no measured pace")
check(machines.pace([10, 10, 10, 10, 10, 10, 90])["median"] == 10, "only the last 5 gaps count")
band = machines.forecast(1000, 4, found)
check(band == {"q25": 1000 + 4 * 22 * 60, "median": 1000 + 4 * 33 * 60, "q75": 1000 + 4 * 49 * 60}, "4 goals left forecast the last merge plus 4 gaps, as a band")
check(machines.forecast(1000, 4, None) is None and machines.forecast(1000, 0, found) is None, "no pace or nothing left forecasts nothing")
check(machines.when("2026-11-19T02:00Z") == machines.when("2026-11-19T01:00Z") + 3600 and machines.when("soon") is None, "release times parse as ISO, UTC or local")

with tempfile.TemporaryDirectory(prefix="release-eta-") as tmp:
    repo, bare = os.path.join(tmp, "repo"), os.path.join(tmp, "origin.git")
    subprocess.run(["git", "init", "-q", "--bare", "-b", "main", bare], check=True)
    subprocess.run(["git", "clone", "-q", bare, repo], check=True, capture_output=True)
    git("switch", "-q", "-c", "main", cwd=repo)
    open(os.path.join(repo, "a"), "w").write("0")
    git("add", "-A", cwd=repo)
    git("commit", "-qm", "base", cwd=repo)
    base = int(time.mktime(time.strptime("2026-11-18T21:26", "%Y-%m-%dT%H:%M")))
    for i, minute in enumerate([0, 44, 93, 115, 135]):  # 21:26, 22:10, 22:59, 23:21, 23:41
        at = "%d +0000" % (base + minute * 60)
        git("switch", "-q", "-c", "g%d" % i, "main", cwd=repo)
        open(os.path.join(repo, "f%d" % i), "w").write("x")
        git("add", "-A", cwd=repo)
        git("commit", "-qm", "goal %d" % i, cwd=repo)
        git("switch", "-q", "main", cwd=repo)
        git("merge", "-q", "--no-ff", "-m", "Merge goal %d" % i, "g%d" % i, cwd=repo, env={"GIT_COMMITTER_DATE": at, "GIT_AUTHOR_DATE": at})
    git("push", "-q", "origin", "main", cwd=repo)
    git("fetch", "-q", "origin", cwd=repo)
    times, measured = machines.merge_gaps(repo)
    check(measured == [44.0, 49.0, 22.0, 20.0], "merge_gaps reads the gaps between merges on origin/main: %s" % measured)

    # 2. STATUS: etas, slip, freeze, release record
    common = os.path.join(repo, ".git")
    for name, step in (("alpha", "pr"), ("beta", "qa"), ("gamma", "build")):
        os.makedirs(os.path.join(common, "loop", "runs"), exist_ok=True)
        layers.write(os.path.join(common, "loop", "runs", name + ".json"), {"slug": name, "status": "running", "step": step, "pr": 0})
    now = times[-1] + 600
    status = layers.build(common, {}, now)
    byslug = {w["slug"]: w for w in status["workers"]}
    check(byslug["alpha"]["eta"] == times[-1] + 33 * 60 and byslug["beta"]["eta"] == times[-1] + 66 * 60 and byslug["gamma"]["eta"] == times[-1] + 99 * 60,
          "the goal furthest along gets the next turn at the measured pace, the others one gap each after it")
    check(all(w["eta_basis"] == "measured" and w["slip"] == 0 for w in byslug.values()), "every worker line carries eta_basis measured and slip 0 before any report")
    check(status["release"]["forecast"]["median"] == times[-1] + 3 * 33 * 60, "the release block forecasts the three goals left at the median")
    said = layers.send(common, {}, now=now)[1]
    check(said == "sent" and layers.send(common, {}, now=now + 60)[1] == "no change", "STATUS goes out once and an unchanged second pass sends nothing")
    sent = layers.read(os.path.join(common, "loop", "status-sent.json"))
    sent["eta"]["alpha"] -= 20 * 60  # the eta last reported was 20 minutes earlier: the goal slipped 20
    layers.write(os.path.join(common, "loop", "status-sent.json"), sent)
    status, said = layers.send(common, {}, now=now + 120)
    check(said == "sent" and status["slips"] and status["slips"][0]["slug"] == "alpha" and status["slips"][0]["minutes"] == 20, "a slip over 15 minutes sends STATUS at once")
    sent["eta"]["alpha"] = byslug["alpha"]["eta"] - 10 * 60
    layers.write(os.path.join(common, "loop", "status-sent.json"), sent)
    check(layers.send(common, {}, now=now + 180)[1] == "no change", "a slip of 10 minutes does not send early")
    text = layers.board([status], now + 120)
    check("SLIP: " in text and "alpha" in text and "+20 min" in text, "top's board carries one SLIP line: slug, old eta, new eta")
    target, freeze = machines.when("2026-11-19T02:00Z"), machines.when("2026-11-19T01:00Z")
    check(layers.set_release(common, ["status", "--target", "2026-11-19T02:00Z", "--freeze", "2026-11-19T01:00Z", "--go", "alpha"]) == 0
          and layers.set_release(common, ["status", "--freeze", "tomorrow"]) == 2, "the release times are set with options on status; a bad time is refused")
    before = layers.build(common, {}, freeze - 60)
    after = layers.build(common, {}, freeze + 60)
    marks = {w["slug"]: w["next_release"] for w in after["workers"]}
    check(not any(w["next_release"] for w in before["workers"]) and marks == {"alpha": False, "beta": True, "gamma": True},
          "after the freeze a goal with no MERGE-GO is marked next release; one with it is not")
    check("target" in layers.board([after], freeze) and "freeze" in layers.board([after], freeze), "the board prints the release target, freeze and forecast")

print("ALL PASS" if not failed else "%d FAILED" % len(failed))
sys.exit(1 if failed else 0)
