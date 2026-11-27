#!/usr/bin/env python3
# windows: ok
# reads: skills/workflow-monitoring/scripts/board_cards.py skills/workflow-monitoring/scripts/board.py skills/workflow-monitoring/scripts/notify.py
"""v110-board-views: the board's cards and three views, with fixtures only. No model, no network.

usage: test-board-views.py [cards lines nowrite stale scan gate repos]   (no argument: all)
  cards    one release, two tasks, three goals: one card each, goal cards name task and machine, three groupings (done line 1)
  lines    a goal card keeps every line the old board showed (done line 2)
  nowrite  no model call; a second refresh writes nothing (done line 3)
  stale    a card older than board_max_age is stale (done line 4)
  scan     text the private-name scan refuses is not sent, and the refusal hides the word (done line 5)
  gate     a check-in due with nothing changed is not sent; none closer than checkin_every (done line 6)
  repos    a second repo's cards and settings are its own (done line 7)
"""
import datetime
import json
import os
import re
import subprocess
import sys
import tempfile
import time

here = os.path.dirname(os.path.abspath(__file__))
scripts = os.path.join(here, "..", "..", "skills", "workflow-monitoring", "scripts")
sys.path.insert(0, scripts)
os.environ["LOOP_ROLE"] = "worker"
failed = []
NOW = 1_800_000_000.0
AT = datetime.datetime.fromtimestamp(NOW, datetime.timezone.utc)


def check(ok, text):
    print(("PASS: " if ok else "FAIL: ") + text)
    if not ok:
        failed.append(text)


def iso(seconds_ago):
    return datetime.datetime.fromtimestamp(NOW - seconds_ago, datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def put(path, text):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="\n") as handle:
        handle.write(text if isinstance(text, str) else json.dumps(text))


def repo(tmp, name, cfg=None):
    root = os.path.join(tmp, name)
    subprocess.run(["git", "init", "-q", "-b", "main", root], check=True)
    put(os.path.join(root, ".loop", "config.json"), dict({"base": "main"}, **(cfg or {})))
    return root


def fixture(tmp):
    """One release (batch v1-1-0), two tasks (ta: g1 g2, tb: g3), three goals; g3 runs on the other machine."""
    root = repo(tmp, "toy")
    put(os.path.join(root, ".loop", "queue.md"), "## Batch: v1-1-0\n- slug: g1\n- slug: g2\n- slug: g3\n")
    for slug, goals in (("ta", "g1, g2"), ("tb", "g3")):
        put(os.path.join(root, ".loop", "tasks", slug + ".md"),
            "# Task %s\n- feature: Board\n- release: v1.1.0\n- source: the owner\n- goals: %s\n" % (slug, goals))
    runs = [{"slug": "g1", "status": "running", "machine": "pc", "updated": iso(60)},
            {"slug": "g2", "status": "running", "machine": "pc", "updated": iso(120)},
            {"slug": "g3", "status": "running", "machine": "mac", "updated": iso(180)}]
    items = [{"mark": "running", "slug": r["slug"], "left": 3600, "machine": r["machine"], "bars": [(1, 2, False)]} for r in runs]
    return root, runs, items


def build(root, runs, items, **more):
    import board_cards
    import board_tasks
    task_rows = board_tasks.tasks(root, runs)
    return board_cards.cards(items, runs, task_rows, {"v1.1.0": ["g1", "g2", "g3"]}, AT, root, **more)


def t_cards(tmp):
    import board_cards
    root, runs, items = fixture(tmp)
    found = build(root, runs, items)
    kinds = sorted(c["kind"] for c in found)
    check(kinds == ["goal"] * 3 + ["release"] + ["task"] * 2, "one release, two tasks and three goals make six cards, got %s" % kinds)
    goals = {c["id"]: c for c in found if c["kind"] == "goal"}
    check(all(c.get("state") and c.get("eta_of") for c in found), "every card shows its state and whose ETA it is")
    check(goals.get("goal:g1", {}).get("task") == "ta" and goals.get("goal:g3", {}).get("task") == "tb", "a goal card names its task")
    check(goals.get("goal:g1", {}).get("machine") == "pc" and goals.get("goal:g3", {}).get("machine") == "mac", "a goal card names its own machine")
    by_release = board_cards.group_by(found, "release")
    by_task = board_cards.group_by(found, "task")
    by_goal = board_cards.group_by(found, "goal")
    check(sorted(by_release) == ["v1.1.0"] and len(by_release["v1.1.0"]) == 6 - 0, "the by-release view lists the release and its tasks and goals")
    check(sorted(by_task) == ["ta", "tb"] and [c["id"] for c in by_task["ta"] if c["kind"] == "goal"] == ["goal:g1", "goal:g2"], "the by-task view groups goals under their task")
    check(sorted(by_goal) == ["g1", "g2", "g3"], "the by-goal view has one group per goal")


GOLD_GOAL = ["[>] ga ~1h00m left pc", "      d1 [####----] 1/2 by step ETA hh:mm (about 1h00m)"]


def mask(lines):
    return [re.sub(r"ETA \d\d:\d\d", "ETA hh:mm", x) for x in lines]


def t_lines(tmp):
    root, runs, items = fixture(tmp)
    item = {"mark": "running", "slug": "ga", "left": 3600, "machine": "pc", "bars": [(1, 2, False)]}
    run = {"slug": "ga", "status": "running", "machine": "pc", "updated": iso(60)}
    stopped = {"slug": "gb", "status": "stopped", "machine": "pc", "updated": iso(60), "finding": "usage limit reached, resets at 5pm"}
    bitem = {"mark": "stopped", "slug": "gb", "left": None, "machine": "pc", "bars": []}
    found = {c["id"]: c for c in build(root, runs + [run, stopped], items + [item, bitem])}
    check(mask(found["goal:ga"]["lines"])[:2] == GOLD_GOAL, "a goal card keeps the old board's goal line and done-line bar")
    check(any("usage limit" in x for x in found["goal:gb"]["lines"]), "a stopped goal's card keeps its limit line")
    check(any("ETA unknown" in x for x in found["goal:gb"]["lines"]) or any("ETA" in x for x in found["goal:ga"]["lines"]), "a goal card keeps its ETA text")


def t_nowrite(tmp):
    import board
    src = open(os.path.join(scripts, "board_cards.py"), encoding="utf-8").read()
    check(not re.search(r"^\s*(import|from)\s+(anthropic|openai|requests|urllib|http|socket|subprocess)\b", src, re.M), "board_cards.py imports no model client, network or process module")
    path = os.path.join(tmp, "board.json")
    board.write(path, json.dumps({"generated": "2026-11-27T10:00:00Z", "next_at": "10:30 UTC", "digest": "1 runs"}, sort_keys=True) + "\n")
    os.utime(path, (1_000_000_000, 1_000_000_000))
    board.write(path, json.dumps({"generated": "2026-11-27T10:05:00Z", "next_at": "10:35 UTC", "digest": "1 runs"}, sort_keys=True) + "\n")
    check(os.stat(path).st_mtime == 1_000_000_000, "a second refresh with nothing changed writes nothing")
    board.write(path, json.dumps({"generated": "2026-11-27T10:06:00Z", "next_at": "10:36 UTC", "digest": "2 runs"}, sort_keys=True) + "\n")
    check(os.stat(path).st_mtime != 1_000_000_000, "a refresh with a real change writes")


def t_stale(tmp):
    import board_cards
    root, runs, items = fixture(tmp)
    runs[0]["updated"] = iso(6 * 60)   # older than 5 minutes
    runs[1]["updated"] = iso(5 * 60)   # exactly 5: not older
    runs[2].pop("updated")               # no time at all
    got = {c["id"]: c for c in build(root, runs, items, max_age=5)}
    check(got["goal:g1"]["stale"] is True, "a card older than board_max_age is stale")
    check(got["goal:g2"]["stale"] is False, "a card exactly board_max_age old is not stale")
    check(got["goal:g3"]["stale"] is False, "a card with no time is not stale")
    check(board_cards.setting({"board_max_age": "soon"}, "board_max_age", 5) == 5 and board_cards.setting({"board_max_age": 45}, "board_max_age", 5) == 45,
          "a non-number board_max_age uses the default")
    sys.path.insert(0, os.path.join(here, "..", "..", "skills", "workflow-setup", "scripts"))
    import settings
    check(settings.repo_defaults()["board_max_age"] == 5, "the board_max_age default is the page's 5 minutes (BOARD-5)")


def t_scan(tmp):
    import notify_gate as notify
    word = "zorblax"
    names = os.path.join(tmp, "names.txt")
    put(names, word + "\n")
    os.environ["LOOP_PRIVATE_NAMES"] = names
    said = notify.outgoing_refusal({"subject": "Loop: stopped %s-goal (repo) [q1]" % word, "body": "a line\nanother line", "page": "ok"})
    check(bool(said) and "subject" in said and word not in said, "text the scan refuses is named by its place, never the word")
    check(notify.outgoing_refusal({"subject": "Loop: stopped goal", "body": "fine"}) == "", "clean text passes")
    os.environ["LOOP_PRIVATE_NAMES"] = os.path.join(tmp, "missing.txt")
    check(bool(notify.outgoing_refusal({"body": "fine"})), "no list fails closed")


def t_gate(tmp):
    import notify_gate as notify
    state = {}
    lines = ["CHANGE a/b step: x -> y"]
    now = NOW
    check(notify.checkin_gate(state, lines, now, 10) == "send", "a first change is sent")
    notify.checkin_sent(state, lines, now)
    check(notify.checkin_gate(state, lines, now + 3600, 10) == "same", "a check-in due with nothing changed is not sent")
    check(notify.checkin_gate(state, lines + ["CHANGE c/d step: p -> q"], now + 60, 10) == "early", "a change closer than checkin_every is held")
    check(notify.checkin_gate(state, lines + ["CHANGE c/d step: p -> q"], now + 11 * 60, 10) == "send", "a change after checkin_every is sent")
    held = json.dumps(state, sort_keys=True)
    notify.checkin_gate(state, lines + ["CHANGE c/d step: p -> q"], now + 60, 10)
    check(json.dumps(state, sort_keys=True) == held, "a held attempt writes nothing")
    import board_cards
    sys.path.insert(0, os.path.join(here, "..", "..", "skills", "workflow-setup", "scripts"))
    import settings
    check(settings.repo_defaults()["checkin_every"] == 10, "the checkin_every default is task 18's 10 minutes")
    refused = [board_cards.setting({"checkin_every": v}, "checkin_every", 10, 5, 10) for v in (4, 11, 0, "x")]
    import contextlib
    import io
    err = io.StringIO()
    with contextlib.redirect_stderr(err):
        board_cards.setting({"checkin_every": 11}, "checkin_every", 10, 5, 10)
    said = err.getvalue().strip().splitlines()
    check(len(said) == 1 and all(x in said[0] for x in ("checkin_every", "11", "5 to 10", "default 10")),
          "an out-of-range checkin_every prints one line naming the setting, the value, the range and the default")
    err = io.StringIO()
    with contextlib.redirect_stderr(err):
        board_cards.setting({"board_max_age": "soon"}, "board_max_age", 5)
    said = err.getvalue().strip().splitlines()
    check(len(said) == 1 and "board_max_age" in said[0] and "soon" in said[0] and "default 5" in said[0], "a board_max_age that is not a number prints one line too")
    check(refused == [10, 10, 10, 10] and board_cards.setting({"checkin_every": 5}, "checkin_every", 10, 5, 10) == 5 and board_cards.setting({"checkin_every": 8}, "checkin_every", 10, 5, 10) == 8,
          "checkin_every outside 5 to 10 is refused; 5 and 8 are kept")


def t_repos(tmp):
    import board
    a = repo(tmp, "repo-a", {"board_max_age": 7, "checkin_every": 5})
    b = repo(tmp, "repo-b", {"board_max_age": 3, "checkin_every": 8})
    third = os.path.join(tmp, "elsewhere")
    os.makedirs(third)
    here_now = os.getcwd()
    os.chdir(third)
    try:
        check(board.repo_setting(a, "board_max_age", 5) == 7 and board.repo_setting(b, "board_max_age", 5) == 3, "each repo's board_max_age is its own")
        check(board.repo_setting(a, "checkin_every", 10) == 5 and board.repo_setting(b, "checkin_every", 10) == 8, "each repo's checkin_every is its own")
        da, db = board.board_dir(a), board.board_dir(b)
        check(da != db and os.path.realpath(da).startswith(os.path.realpath(a)) and os.path.realpath(db).startswith(os.path.realpath(b)),
              "each repo's cards go to its own board folder")
    finally:
        os.chdir(here_now)


SECTIONS = {"cards": t_cards, "lines": t_lines, "nowrite": t_nowrite, "stale": t_stale, "scan": t_scan, "gate": t_gate, "repos": t_repos}


def main():
    names = sys.argv[1:] or list(SECTIONS)
    for name in names:
        tmp = tempfile.mkdtemp(prefix="bv-")
        try:
            SECTIONS[name](tmp)
        except Exception as err:  # a missing function is a red, never a crash that hides the others
            check(False, "%s raised %s: %s" % (name, type(err).__name__, err))
    print("ALL PASS" if not failed else "%d FAILED" % len(failed))
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
