#!/usr/bin/env python3
# windows: ok
# reads: dev/toy/approved-row-changes.tsv skills/workflow-monitoring/scripts/board_lines.py skills/workflow-monitoring/scripts/live_board.py skills/workflow-monitoring/scripts/checkin.py
# reads: dev/toy/hist.py skills/workflow-delivery/scripts/dlf.py skills/workflow-delivery/scripts/private.py
# History codes, each printed with its fix (dev/toy/hist.py): HIST-E01 the base ref is missing; HIST-E02 the history is shallow;
# HIST-E03 a git command failed; HIST-E04 a fixture could not be built. A history that can't be read fails this test.
"""DEL-23: tasks. Each brief under .loop/tasks/ becomes one line of the Tasks list on the check-in and the live board, by name, with its
state (queued, running, waiting, done or replaced), its goals and progress, and its ETA. A fixture repo holds toy briefs and fake run
records; nothing here touches the real .git/loop, a network or a held toy."""
import datetime
import json
import os
import re
import subprocess
import sys
import tempfile

here = os.path.dirname(os.path.abspath(__file__))
top = os.path.abspath(os.path.join(here, "..", ".."))
sys.path.insert(0, os.path.join(top, "skills", "workflow-monitoring", "scripts"))
CALLER = dict(os.environ)  # read before HOME moves: error lines are screened with the runner's own private-name list
home = tempfile.mkdtemp()
for key in ("HOME", "USERPROFILE"):
    os.environ[key] = home
os.environ["LOOP_MACHINE_NAME"] = "pc"
import board_lines  # noqa: E402
import board_model  # noqa: E402
import board_tasks  # noqa: E402
import checkin  # noqa: E402
import live_board  # noqa: E402
import reply_hook  # noqa: E402
sys.path.insert(0, here)
import hist  # noqa: E402
hist.NAMES = hist.caller_names(CALLER)

failed = []
now = datetime.datetime.now(datetime.timezone.utc)
stamp = now.strftime("%Y-%m-%dT%H:%M:%SZ")
LEFT = {}
checkin.bs.left_time = lambda run, runs_, at, root=None: LEFT.get(run["slug"], 0)  # no history of finished goals in a fixture


def check(ok, text):
    print(("PASS: " if ok else "FAIL: ") + text)
    if not ok:
        failed.append(text)


def brief(name, goals="", needs="", by="", feature="DEL-23", release="v1.1.0", source="a toy source"):
    return "# %s\n\n- Feature: %s\n- Release: %s\n- Goals: %s\n- Needs: %s\n- Replaced by: %s\n- Source: %s\n\n## Purpose\n\nToy.\n" % (
        name, feature, release, goals, needs, by, source)


def repo(briefs, runs):
    tmp = tempfile.mkdtemp()
    root = os.path.join(tmp, "toyrepo")
    subprocess.run(["git", "init", "-q", "-b", "main", root], check=True)
    os.makedirs(os.path.join(root, ".loop", "tasks"))
    with open(os.path.join(root, ".loop", "config.json"), "w") as f:
        json.dump({"base": "main", "parallel": 3}, f)
    for slug, text in briefs.items():
        with open(os.path.join(root, ".loop", "tasks", slug + ".md"), "w", encoding="utf-8") as f:
            f.write(text)
    folder = os.path.join(root, ".git", "loop", "runs")
    os.makedirs(folder)
    for slug, extra in runs.items():
        record = {"slug": slug, "goal": "Goal " + slug, "status": "running", "step": "build", "worker": "session", "pid": os.getpid(),
                  "updated": stamp, "report": {"at": stamp, "text": "working"}}
        record.update(extra)
        with open(os.path.join(folder, slug + ".json"), "w") as f:
            json.dump(record, f)
    return root


def listed(root, runs, gone=()):
    return {t["slug"]: t for t in board_tasks.tasks(root, runs, set(gone))}


def shown(root, name, gone=()):
    """(the task's line, {goal: label}) from the real Tasks lines."""
    lines = live_board.task_lines(root, load(root), now, set(gone))
    i = next(n for n, l in enumerate(lines) if l.startswith("- %s:" % name))
    goals = {}
    for l in lines[i + 1:]:
        if not l.startswith("    "):
            break
        slug, _, label = l.strip().partition(" ")
        goals[slug] = label
    return lines[i], goals


def load(root):
    return live_board.load(root)


MERGED = {"status": "done", "step": "release", "release": "merged"}
ASKING = {"status": "waiting", "step": "plan"}

# the state rule
root = repo({"a": brief("Task A", "ga"), "b": brief("Task B", "gb"), "c": brief("Task C", "gc", needs="a"), "d": brief("Task D", "gd", needs="zzz")},
            {"ga": {}, "gb": {}, "gc": {}})
got = listed(root, load(root))
check(got["a"]["state"] == "running" and got["b"]["state"] == "running", "two tasks with no dependency both show running")
check(got["c"]["state"] == "running", "a task whose goal already runs stays running even with an unmet need")
check(got["d"]["state"] == "waiting" and "zzz (no brief)" in got["d"]["note"], "a need that names no brief shows waiting and says no brief")
root = repo({"a": brief("Task A", "ga"), "c": brief("Task C", "", needs="a")}, {"ga": {}})
got = listed(root, load(root))
check(got["c"]["state"] == "waiting" and "Task A" in got["c"]["note"], "a task that needs another shows waiting until that one is done, by its name")
root = repo({"a": brief("Task A", "ga"), "c": brief("Task C", "", needs="a")}, {"ga": MERGED})
got = listed(root, load(root))
check(got["a"]["state"] == "done" and got["c"]["state"] == "queued", "once the needed task is done the dependent task shows queued")
root = repo({"a": brief("Task A", "ga, gb")}, {"ga": MERGED, "gb": {}})
got = listed(root, load(root))
check(got["a"]["state"] == "running" and got["a"]["done"] == 1, "a task whose last goal is still open is not done")
check(shown(root, "Task A")[1] == {"ga": "finished", "gb": "build"}, "a goal reads finished or its flow step")
root = repo({"a": brief("Task A", "ga, gb, gc, gd")}, {"gb": {"status": "queued"}, "gc": {"status": "done", "step": "pr"}, "gd": ASKING})
got = listed(root, load(root))
labels = shown(root, "Task A")[1]
check(labels["ga"] == "not started" and labels["gb"] == "not started", "a goal with no record and a goal with status queued are both not started")
check(labels["gc"] == "awaiting merge" and labels["gd"] == "plan", "a done goal that is not merged reads awaiting merge, a waiting goal its step")
check(got["a"]["state"] == "running", "a goal done but not merged keeps the task running")
root = repo({"a": brief("A", "gw"), "b": brief("B", "gf")}, {"gw": ASKING, "gf": {"status": "failed"}})
got = listed(root, load(root))
check(got["a"]["state"] == "waiting" and got["b"]["state"] == "waiting", "a task whose only live goals wait on the owner or failed shows waiting, not running")
root = repo({"a": brief("Task A", "ga")}, {"ga": {"status": "running"}})
check(listed(root, load(root), gone={"ga"})["a"]["state"] == "done", "a goal in the merged set passed in counts as finished")
root = repo({"old": brief("Old", "g1", by="new"), "new": brief("New", "g2"), "n": brief("Needs old", "", needs="old"), "m": brief("Needs new", "", needs="new")},
            {"g2": MERGED})
got = listed(root, load(root))
check(got["old"]["state"] == "replaced", "a task with Replaced by shows replaced")
check(got["n"]["state"] == "queued" and got["m"]["state"] == "queued", "a need that names a replaced task follows the replacement")
root = repo({"x": brief("X", "", needs="y"), "y": brief("Y", "", needs="z"), "z": brief("Z", "")}, {})
got = listed(root, load(root))
check([got[k]["state"] for k in "xyz"] == ["waiting", "waiting", "queued"], "a three-task chain in reversed order resolves in one run")
root = repo({"x": brief("X", "", needs="y"), "y": brief("Y", "", needs="x")}, {})
got = listed(root, load(root))
check(got["x"]["note"] == "cycle" and got["y"]["note"] == "cycle", "a cycle of needs shows every member waiting with the word cycle")
root = repo({"x": brief("X", "", needs="old"), "old": brief("Old", "", by="x")}, {})
got = listed(root, load(root))
check(got["x"]["state"] == "waiting" and got["x"]["note"] == "cycle", "a replacement that points back at its dependant is a cycle, not a hang")

# the ETA words
root = repo({"a": brief("A", "g1"), "b": brief("B", "g2"), "c": brief("C", "g3"), "d": brief("D", "g4")},
            {"g1": {"status": "done", "step": "pr"}, "g2": {}, "g3": {}})
LEFT.update(g2=600, g3=1800)
got = listed(root, load(root))
check(shown(root, "A")[0].endswith("ETA awaiting merge"), "every live goal done but unmerged gives the ETA words awaiting merge")
check(shown(root, "B")[0].endswith("ETA 10m"), "the ETA is the time left of the live goal: %s" % shown(root, "B")[0])
check(shown(root, "D")[0].endswith("ETA -"), "a task with nothing in flight shows an ETA of a dash")
LEFT["g3"] = None
check(shown(root, "C")[0].endswith("ETA ?"), "a live goal with no estimate gives an ETA of a question mark")
LEFT.clear()
calls = []
checkin.bs.left_time = lambda run, runs_, at, root=None: calls.append(root) or 60
here_cwd = os.getcwd()
os.chdir(tempfile.mkdtemp())
try:
    root = repo({"a": brief("A", "g1")}, {"g1": {}})
    shown(root, "A")
finally:
    os.chdir(here_cwd)
check(calls and all(c == root for c in calls), "left_time gets the fixture's root, not the working directory")
checkin.bs.left_time = lambda run, runs_, at, root=None: LEFT.get(run["slug"], 0)

root = repo({"a": brief("A", ""), "b": brief("B", "", needs="a")}, {})
check(listed(root, load(root))["b"]["state"] == "waiting", "a task with no goals is never done, so a task that needs it keeps waiting")
root = repo({"s": brief("S", "g[31mx|" + "y" * 200)}, {})
line = live_board.task_lines(root, [], now)[3]
check("" not in line and "|" not in line and len(line) < 100, "a goal slug with a control character or a pipe is printed clean and bounded")
check(live_board.task_lines(root, None, now)[2].startswith("- tasks unavailable: "), "a failure inside the task code shows one tasks-unavailable line, not a crash")

# bad briefs are named, the rest still print
root = repo({"ok": brief("Fine", "g1"), "bare": "# Bare name\n\n- Goals: g2\n", "dir": brief("Dir")}, {"g1": {}})
os.remove(os.path.join(root, ".loop", "tasks", "dir.md"))
os.makedirs(os.path.join(root, ".loop", "tasks", "dir.md"))  # a directory where a brief should be: unreadable
got = listed(root, load(root))
check("unreadable" in got["dir"]["note"] and got["ok"]["state"] == "running", "an unreadable brief gives one note and the other tasks still print")
check("add its feature, release, source line" in got["bare"]["note"], "an incomplete brief names the lines to add: %s" % got["bare"]["note"])
root = repo({"k": "# Keys\n\n-  FEATURE :  DEL-23 \n- release: v1.1.0\n- GOALS: g1 ,g2\n- Source:x\n"}, {})
got = listed(root, load(root))
check(got["k"]["note"] == "" and got["k"]["goals"][0][0] == "g1" and len(got["k"]["goals"]) == 2, "keys are read without case or spacing, and every goal is listed")
root = repo({"w": "# Hostile | name\x1b[31m " + "x" * 500 + "\n\n- Feature: F\n- Release: R\n- Source: S\n"}, {})
lines = live_board.task_lines(root, [], now)
check(len(lines) == 3 and "|" not in lines[2] and "\x1b" not in lines[2] and len(lines[2]) < 200, "a name with a pipe, a control character and 500 characters prints as one clean bounded line")

# no briefs: nothing printed
root = repo({}, {})
check(live_board.task_lines(root, [], now) == [], "no briefs prints nothing")
check("Tasks" not in "\n".join(live_board.render(root=root, at=now)), "the board prints no Tasks lines without briefs")
plain_checkin = "\n".join(checkin.render(root=root, at=now, stamp="0000"))
check("Tasks" not in plain_checkin, "the check-in prints no Tasks section without briefs")

# the real surfaces, from one fixture
root = repo({"a": brief("Alpha task", "ga"), "b": brief("Beta task", "", needs="a"), "h": brief("History tokens task", "gh")},
            {"ga": {}, "gh": MERGED})
text = "\n".join(checkin.render(root=root, at=now, stamp="0000"))
board = "\n".join(live_board.render(root=root, at=now))
want = ["Alpha task", "Beta task", "History tokens task", "ga"]
check(all(w in " ".join(text.split()) for w in want), "the check-in shows every task by name and its goal")
check(all(w in " ".join(board.split()) for w in want), "the board shows every task by name and its goal")
check("waiting (needs Alpha task)" in " ".join(text.split()) and "waiting (needs Alpha task)" in " ".join(board.split()), "both surfaces say why a task waits")
check("History tokens task: done" in " ".join(text.split()) and "History tokens task: done" in " ".join(board.split()), "both surfaces agree a merged goal is finished, and a task name may hold a forbidden word")
check(text.index("Tasks") > text.index("All sessions") and text.index("Tasks") < text.index("Dependencies"), "the check-in puts Tasks after All sessions and before Dependencies")
check(board.index("Tasks") > board.index("Queued goals") and board.index("Tasks") < board.index("Dependencies"), "the board puts Tasks between Queued goals and Dependencies")
bare_root = repo({}, {"ga": {}, "gh": MERGED})
bare = "\n".join(checkin.render(root=bare_root, at=now, stamp="0000"))
check(reply_hook.problems(text) == reply_hook.problems(bare) and reply_hook.shown(text, root) == reply_hook.shown(bare, bare_root),
      "the Tasks section adds no problem to the reply hook's layout check of the same fixture")
check(not any(l.lstrip().startswith("|") and "Tasks" in l for l in text.splitlines()), "the Tasks section has no pipe rows")
stripped = re.sub(r"\n\nTasks\n(?:(?:- |    ).*\n?)+", "\n", text)
check("Tasks" not in stripped and len(stripped) < len(text), "removing the Tasks lines leaves the check-in text without briefs' lines only")
generated = [l for l in board.splitlines() if "Tasks" in l or "goals finished" in l]
check(not any(re.search(r"merged|hist|closed|milestone|tokens|total|done lines|longest|Roadmap|Needs you|level [0-9]", l.replace("History tokens task", "")) for l in generated), "the generated labels avoid the board's forbidden words")

# the real briefs
folder = os.path.join(top, ".loop", "tasks")
names = sorted(n for n in os.listdir(folder) if n.endswith(".md")) if os.path.isdir(folder) else []
check(len(names) >= 11, "the repo holds at least the eleven briefs: %d" % len(names))
real = board_tasks.task_rows(top)
check(all(not t["note"] for t in real) and len(real) == len(names), "every real brief has its feature, release and source lines")
bodies = [open(os.path.join(folder, n), encoding="utf-8").read() for n in names]
check(all("## Purpose" in b and "## Done when" in b for b in bodies), "every real brief has a Purpose and a Done when section")
check(not any(re.search("ther" + "mis", b, re.I) for b in bodies), "no real brief names the service repo")
check(all(re.search(r"^- Source: .+", b, re.M) for b in bodies), "every real brief carries its source record")
# done line 5: nothing added under skills/, no existing regression row changed
def unapproved(diff_rows, ok):
    """The changed or removed existing rows in a diff whose id the approved list does not name."""
    return [l for l in diff_rows if l.startswith("-") and not l.startswith("---") and l[1:].split("\t")[0] not in ok]


# the rows an approved record names (owner words or an operation ruling), each with its record: dev/toy/approved-row-changes.tsv
listed = os.path.join(here, "approved-row-changes.tsv")
approved = [l.split("\t") for l in open(listed, encoding="utf-8").read().splitlines() if l.strip() and not l.startswith("#")] if os.path.exists(listed) else []
ok = {a[0] for a in approved}
check(all(len(a) == 3 and a[1].strip() and a[2].strip() for a in approved), "every approved row change names its record and its reason")
check(unapproved(["-some-other-row\tland\tcommand"], ok) != [] and unapproved(["--- a/.loop/regression.tsv"], ok) == [], "negative control: a changed or removed row the list does not name still fails")
ALLOWED = "skills/workflow-monitoring/scripts/board_tasks.py"  # owner o788: the one file v110-tasks may add under skills/
PR = r"^Merge pull request #[0-9]* from .*/loop/v110-tasks$"


def tasks_added(repo):
    """The files under skills/ that v110-tasks' own merge added: the first-parent merge of its pull request on origin/main, found by
    its message (TD1176; no sha is pinned), compared with that merge's first parent. (merge found, added files)."""
    return hist.added(repo, PR, "skills", what="v110-tasks' merge")


def fixture(extra):
    """A repo whose origin/main has v110-tasks' pull request merged, adding board_tasks.py and the files in extra."""
    repo = tempfile.mkdtemp()
    hist.fixture(repo, "init", "-q", "-b", "main", ".")
    os.makedirs(os.path.join(repo, ".loop"))
    with open(os.path.join(repo, ".loop", "regression.tsv"), "w") as f:
        f.write("a\tland\ttrue\nb\tland\ttrue\n")
    hist.fixture(repo, "add", "-A")
    hist.fixture(repo, "commit", "-qm", "base")
    hist.fixture(repo, "checkout", "-q", "-b", "loop/v110-tasks")
    for name in [ALLOWED] + extra:
        os.makedirs(os.path.dirname(os.path.join(repo, name)), exist_ok=True)
        open(os.path.join(repo, name), "w").write("x\n")
    hist.fixture(repo, "add", "-A")
    hist.fixture(repo, "commit", "-qm", "tasks")
    hist.fixture(repo, "checkout", "-q", "main")
    hist.fixture(repo, "merge", "-q", "--no-ff", "-m", "Merge pull request #1 from o/loop/v110-tasks", "loop/v110-tasks")
    hist.fixture(repo, "update-ref", "refs/remotes/origin/main", "HEAD")
    return repo


def row_changes(repo, change):
    """Unapproved changed or removed rows when a PR branch of the fixture applies change to .loop/regression.tsv."""
    hist.fixture(repo, "checkout", "-q", "-b", "pr")
    base = hist.fixture(repo, "merge-base", "origin/main", "HEAD").strip()
    path = os.path.join(repo, ".loop", "regression.tsv")
    open(path, "w").write(change)
    return unapproved(hist.run(repo, "a practice change to the rows", "diff", base, "--", ".loop/regression.tsv").splitlines(), set())


# negative controls: a fixture of v110-tasks' merge adding another skills file fails, and a PR changing an existing row fails
check(tasks_added(fixture([]))[1] == [ALLOWED], "a fixture of v110-tasks' merge adding only board_tasks.py reads as allowed")
check([f for f in tasks_added(fixture(["skills/x/other.py"]))[1] if f != ALLOWED] == ["skills/x/other.py"],
      "negative control: a fixture of v110-tasks' merge adding another skills file still fails")
check(len(row_changes(fixture([]), "a\tland\tfalse\nb\tland\ttrue\n")) == 1, "negative control: a change to an existing row fails on any PR")
check(len(row_changes(fixture([]), "a\tland\ttrue\n")) == 1, "negative control: removing an existing row fails on any PR")
check(row_changes(fixture([]), "a\tland\ttrue\nb\tland\ttrue\nc\tland\ttrue\n") == [], "a row added by a PR is not a change to an existing row")
COMPARED = "the skills files and the regression rows this test compares"
hist.require(top, COMPARED)
sha = hist.run(top, COMPARED, "merge-base", "origin/main", "HEAD").strip()
rows = hist.run(top, COMPARED, "diff", sha, "--", ".loop/regression.tsv").splitlines()  # the working tree against the merge base
check(not unapproved(rows, ok), "no existing regression row is changed or removed except the rows an approved record names (%d listed)" % len(ok))
merge, added = tasks_added(top)
check(bool(merge), "v110-tasks' pull request merge is found on origin/main by its message")
check(added == [ALLOWED], "no file is added under skills/ except board_tasks.py (o788), by v110-tasks' own merge: %s" % hist.shown(added))
sys.exit(1 if failed else 0)
