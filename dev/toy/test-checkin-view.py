#!/usr/bin/env python3
# windows: ok
# reads: skills/workflow-monitoring/scripts/checkin.py skills/workflow-monitoring/scripts/reply_hook.py skills/workflow-monitoring/scripts/graph.py
"""MON-5, MON-14, MON-16: the check-in prints a Machine line first, groups each repo block by release then feature, and
shows each goal's status marker, time left and machine; the reply hook flags a check-in missing any of these."""
import datetime
import json
import os
import subprocess
import sys
import tempfile

here = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(here, "..", "..", "skills", "workflow-monitoring", "scripts"))
import checkin  # noqa: E402
import reply_hook  # noqa: E402

failed = []
NL = chr(10)


def check(ok, text):
    print(("PASS: " if ok else "FAIL: ") + text)
    if not ok:
        failed.append(text)


def reply(deps, machine="Machine: RAM 9.0 GB, commit 12.0 GB free, CPU 10%, 2 claude, 1 node; memory allows 3 goal starts"):
    return ("Two goals run.\n" + machine + "\n\n## All sessions\n| a | b |\n|---|---|\n| x | y |\n\n## Dependencies\n" + deps +
            "\n\n## Needs you\nNothing needs you\n\n## Coming up\n- soon\n")


GOOD = "== toyrepo ==\n[>] first-goal\n-- v1.0.1 release ETA tomorrow ~20:00 (2 goals, 1 not started) --\n  Monitoring:\n    [>] first-goal ~40m left pc\n    [ ] later-goal ~? left mac"
with tempfile.TemporaryDirectory() as tmp, tempfile.TemporaryDirectory() as home:
    for key in ("HOME", "USERPROFILE"):
        os.environ[key] = home
    os.environ["LOOP_MACHINE_NAME"] = "pc"
    root = os.path.join(tmp, "toyrepo")
    subprocess.run(["git", "init", "-q", "-b", "main", root], check=True)
    os.makedirs(os.path.join(root, ".loop"))
    os.makedirs(os.path.join(root, "docs", "wiki"))
    with open(os.path.join(root, "docs", "wiki", "Monitoring.md"), "w") as f:
        f.write("- MON-5: Reviewed\n")
    with open(os.path.join(root, ".loop", "config.json"), "w") as f:
        json.dump({"base": "main"}, f)
    with open(os.path.join(root, ".loop", "queue.md"), "w") as f:
        f.write("## Batch: v1-0-1\n- slug: later-goal | goal: Later (MON-5) | done: Done\n- slug: plain-goal | goal: No id here | done: Done\n")
    runs = os.path.join(root, ".git", "loop", "runs")
    os.makedirs(runs)
    now = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    with open(os.path.join(runs, "first-goal.json"), "w") as f:
        json.dump({"slug": "first-goal", "goal": "First (MON-14)", "status": "running", "step": "build", "worker": "session",
                   "pid": os.getpid(), "updated": now, "machine": "mac", "report": {"at": now, "text": "working"}}, f)

    check(checkin.release_of(root, "later-goal") == "v1.0.1", "a queued goal's release is its batch name, v1-0-1 read as v1.0.1")
    check(checkin.release_of(root, "nobody") == "no release", "a goal in no batch is under no release")
    check(checkin.feature_of(root, "Later (MON-5)") == "Monitoring", "a goal's feature is the page that defines its first requirement ID")
    check(checkin.feature_of(root, "no id here") == "no feature", "a goal naming no requirement ID is under no feature")
    with open(os.path.join(root, ".loop", "docs.tsv"), "w") as f:
        f.write("# page\tpaths\tnotion sync\nMonitoring\tskills/workflow-monitoring\tnotion:abc\n")
    check(checkin.feature_of(root, "no id here", {"touches": ["skills/workflow-monitoring/scripts/x.py"]}) == "Monitoring",
          "a docs.tsv row with a third column is read by its first two")
    os.remove(os.path.join(root, ".loop", "docs.tsv"))
    line = checkin.goal_line(dict(slug="a-goal", mark="running", left=2400, machine="mac"))
    check(line == "[>] a-goal ~40m left mac", "a goal line is its marker, slug, time left and machine (%s)" % line)
    check(checkin.goal_line(dict(slug="b", mark="queued")).startswith("[ ] b ~? left pc"), "no estimate reads ~? and the machine defaults to this one")

    here_out = "\n".join(checkin.render(root=root, at=datetime.datetime.now(datetime.timezone.utc), stamp="0000"))
    rows = here_out.splitlines()
    check(rows[1].startswith("Machine:"), "the Machine line is the second line, straight after the headline")
    check("-- v1.0.1 release ETA " in here_out and "  Monitoring:" in here_out and "  no feature:" in here_out, "each repo block is grouped by release, then feature")
    check("[>] first-goal ~" in here_out and " left mac" in here_out, "a running goal shows its marker, time left and its record's machine")
    check("[ ] later-goal ~? left pc" in here_out, "a queued goal shows its marker, a time and this machine")

    check(checkin.bs.intro("Caps test rows and suite time so delivery isn't blocked, and more (x; #4511)", "test-caps") == "Caps test rows and suite time so delivery isn't blocked (test-caps, #4511)", "the for cell is the goal's first clause, then (slug, #issue)")
    check(len(checkin.bs.intro("a " * 30, "s").split("(")[0].split()) <= 12, "the for cell is at most 12 words")
    at = datetime.datetime.now(datetime.timezone.utc)
    head = checkin.bs.release_header("v1.1", [dict(mark="running", left=3600), dict(mark="queued"), dict(mark="queued")], at)
    check(head.startswith("v1.1 release ETA ") and "(3 goals, 2 not started)" in head, "a release header starts with its ETA and its counts (%s)" % head)
    check(checkin.bs.release_header("v1.2", [dict(mark="queued")], at) == "v1.2 release ETA unknown (1 not started)", "a release with nothing started reads unknown with its count")
    check("release ETA" in here_out, "the printed map has a release ETA in each release header")
    table = NL.join(["| session | repo | for | status | progress | left | latest |", "|---|---|---|---|---|---|---|", "| w | r | %s | running | x | 1m | y |"])
    stub = NL.join(["| a | b |", "|---|---|", "| x | y |"])
    plain = reply_hook.shown(reply(GOOD).replace(stub, table % "Shows the machine first (a-slug, #4496)"), root)
    check(not any("for cell" in w for w in plain), "a for cell with a sentence passes")
    for bad in ("a-slug", "#4496", "a-slug (#4496)"):
        wrong = reply_hook.shown(reply(GOOD).replace(stub, table % bad), root)
        check(any("for cell" in w for w in wrong), "negative control: a for cell of only %s is flagged" % bad)
    wrong = reply_hook.shown(reply(GOOD.replace(" release ETA tomorrow ~20:00 (2 goals, 1 not started)", "")), root)
    check(any("no release ETA" in w for w in wrong), "negative control: a release header with no release ETA is flagged")
    os.chdir(root)
    got = reply_hook.shown(reply(GOOD), root)
    check(got == [], "a check-in with the Machine line and every goal line passes %s" % got)
    wrong = reply_hook.shown(reply(GOOD, machine=""), root)
    check(any("Machine line" in w for w in wrong), "negative control: a check-in with no Machine line is flagged")
    other = "== otherrepo =="+NL+"[>] some-goal ~5m left mac"
    wrong = reply_hook.shown(reply(GOOD + NL + other), root)
    check(any("otherrepo" in w and "not grouped" in w for w in wrong), "negative control: a non-template repo block with no release and feature grouping is flagged")
    grouped_other = GOOD + NL + "== otherrepo ==" + NL + "-- no release release ETA unknown (1 not started) --" + NL + "  no feature:" + NL + "    [>] some-goal ~5m left mac"
    check(not any("not grouped" in w for w in reply_hook.shown(reply(grouped_other), root)), "a non-template repo block grouped under no release and no feature passes")
    for drop, text in (("marker", "[>] first-goal ~40m left pc"), ("time", "[>] first-goal left pc"), ("machine", "[>] first-goal ~40m left")):
        deps = GOOD.replace("[>] first-goal ~40m left pc", text).replace("[>] first-goal\n", "first-goal\n")
        wrong = reply_hook.shown(reply(deps.replace(text, text.replace("[>] ", "") if drop == "marker" else text)), root)
        check(any("first-goal" in w for w in wrong), "negative control: a goal with no %s is flagged by name" % drop)
    # OPS-24: the operation layer files its own findings (layers.finding), and the check-in lists them
    import argparse
    import layers
    calls, opened = [], [{"number": 5167, "title": "Merge slot wait is not logged"}, {"number": 5168, "title": "Slot wait never logged (#5170)"}]
    def fake(args, cwd):
        calls.append(args)
        out = json.dumps(opened) if args[:2] == ["issue", "list"] else "https://github.com/o/r/issues/6001\n"
        return subprocess.CompletedProcess(args, 0, out, "")
    layers.gh = fake
    subprocess.run = (lambda real: lambda a, *k, **kw: subprocess.CompletedProcess(a, 0, "", "") if "milestone.py" in " ".join(map(str, a)) else real(a, *k, **kw))(subprocess.run)
    with open(os.path.join(root, ".loop", "docs.tsv"), "w") as f:
        f.write("Operation\tskills/workflow-monitoring\n")
    make = lambda title, **kw: layers.file_finding(root, argparse.Namespace(**dict(dict(title=title, feature="operation", found="TOP-DECISION 88", text="", owner_words="", dry_run=False), **kw)))
    code, line = make("Slot hand-out order was guessed")
    creates = [c for c in calls if c[:2] == ["issue", "create"]]
    check(code == 0 and len(creates) == 1 and "Backlog: Operation" in creates[0] and "backlog,ops-finding" in creates[0] and "TOP-DECISION 88" in creates[0][-1],
          "a finding is filed on the feature's Backlog milestone with its decision linked (%s)" % line)
    check(make("Unmapped thing", feature="nothing")[1].count("Backlog: Other") == 1 and calls[-1][1] == "create", "a finding with no matching feature goes to Backlog: Other")
    del calls[:]
    for title, why in (("merge slot  WAIT is not logged!", "the same normalised title"), ("Slot wait for #5170 never logged", "the same IDs and most of the words")):
        code, line = make(title)
        check(code == 1 and "repeats open issue #516" in line and not any(c[:2] == ["issue", "create"] for c in calls), "negative control: %s is refused as a duplicate" % why)
    code, line = make("Delete the old worktrees by hand")
    check(code == 2 and "safety class destructive" in line and not any(c[:2] == ["issue", "create"] for c in calls), "negative control: a safety-class finding with no owner's words is refused (%s)" % line)
    with open(os.path.join(root, ".git", "loop", "owner-words.tsv"), "w") as f:
        f.write('o9\t2026-11-19T00:00:00Z\ttop\t"file it"\tOPS-1\no10\t2026-11-19T00:00:00Z\ttop\t"file it"\tOperation\n')
    check(make("Delete the old worktrees by hand", owner_words="o9")[0] == 2, "negative control: owner's words that list other IDs do not cover the finding")
    check(make("Delete the old worktrees by hand", owner_words="o10")[0] == 0, "a safety-class finding is filed with the owner's words that list its page")
    check(make("A title", found="")[0] == 2, "negative control: a finding naming no decision or record is refused")
    shown = "\n".join(checkin.render(root=root, at=datetime.datetime.now(datetime.timezone.utc), stamp="0000"))
    check("Findings filed (operation layer):" in shown and "#6001 on Backlog: Operation: Slot hand-out order was guessed" in shown, "the check-in lists the findings filed since the last check-in")
    check("Findings filed" not in "\n".join(checkin.render(root=root, at=datetime.datetime.now(datetime.timezone.utc), stamp="9999")), "the check-in lists none filed before its stamp")
    os.chdir(here)

sys.exit(1 if failed else 0)
