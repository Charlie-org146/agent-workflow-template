#!/usr/bin/env python3
# windows: ok
# reads: skills/workflow-delivery/scripts/dlf.py skills/workflow-delivery/scripts/guards.py skills/workflow-delivery/scripts/goal.py skills/workflow-monitoring/scripts/govern_hook.py
"""DLF-1.1, DLF-1.3 and DLF-1.5 at the plan gate: a goal's red-team breaks become lines on the release issue and the build starts;
a break that loosens a test or touches a security setting still waits and the board names the class; with the setting off for one
goal its first break waits and the other goal's breaks do not; the setting changes only with an owner reference, and nests
goal over task over release. Real goal.py step in a throwaway repo, a fake gh on PATH, no network."""
import json
import os
import subprocess
import sys
import tempfile

root = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
for skill in ("delivery", "monitoring"):
    sys.path.insert(0, os.path.join(root, "skills", "workflow-" + skill, "scripts"))
home = tempfile.mkdtemp()
tmp, fake = os.path.join(home, "repo"), os.path.join(home, "fake")
for d in (tmp, fake, home + "/bin"):
    os.makedirs(d)
os.symlink(os.path.join(root, "dev", "toy", "dlf-gh"), home + "/bin/gh")
open(home + "/names", "w").write("acmesecret\n")
env = dict(os.environ, LOOP_ROLE="worker", HOME=home, PATH=home + "/bin" + os.pathsep + os.environ["PATH"], DLF_FAKE_DIR=fake, LOOP_PRIVATE_NAMES=home + "/names")
os.environ.update(env)
import dlf  # noqa: E402
import govern_hook  # noqa: E402

failed = []


def check(ok, text):
    print(("PASS: " if ok else "FAIL: ") + text)
    if not ok:
        failed.append(text)


subprocess.run(["git", "init", "-q", tmp], check=True)
for sub in (".loop/goals", ".loop/tasks", ".git/loop/runs", "docs/wiki"):
    os.makedirs(os.path.join(tmp, sub))
open(tmp + "/docs/wiki/Principles.md", "w").write("## 1. Documentation-driven\nfirst\n## 2. The loop\nsecond\n## 3. The docs are true\nthird\n")
config = {"owner_login": "boss"}
json.dump(config, open(tmp + "/.loop/config.json", "w"))
goal_py = os.path.join(root, "skills", "workflow-delivery", "scripts", "goal.py")


def build(slug, touches, breaks, cfg=None):
    json.dump(dict(config, **(cfg or {})), open(tmp + "/.loop/config.json", "w"))
    for ext, body in ((".md", "# %s\n" % slug), (".plan.md", "plan of %s\n" % slug)):
        open(tmp + "/.loop/goals/" + slug + ext, "w").write(body)
    json.dump({"slug": slug, "status": "running", "step": "plan", "tries": 0, "flow": {}, "goal": slug, "branch": "loop/" + slug, "touches": touches,
               "log": ["2099-01-01T00:00:00Z frozen 1 done lines"]}, open(tmp + "/.git/loop/runs/%s.json" % slug, "w"))
    govern_hook.plan_record(tmp, slug, "".join("B%d: %s\n" % (i + 1, b) for i, b in enumerate(breaks)))
    got = subprocess.run([sys.executable, goal_py, "step", slug, "build"], capture_output=True, text=True, cwd=tmp, env=env)
    return got.returncode, got.stdout + got.stderr


def lines(slug):
    try:
        rows = json.load(open(fake + "/state.json"))["comments"].get("1", [])
    except OSError:
        rows = []
    return [r["body"] for r in rows if "dlf key=%s|" % slug in r["body"]]


code, said = build("g1", ["skills/a/b.py"], ["the plan misses a case", "the lane can stall", "a page is out of date"])
check(code == 0 and "STEP g1 build" in said, "a goal with three red-team breaks starts its build (rc %s): %s" % (code, said.strip()[:80]))
check(len(lines("g1")) == 3 and all("settle with:" in l and "recommend:" in l for l in lines("g1")), "its three breaks are three lines on the release issue, each with its settle words and a recommendation")
check(len(json.load(open(fake + "/state.json"))["issues"]) == 1, "one issue for the release")
code, said = build("g1", ["skills/a/b.py"], ["the plan misses a case", "the lane can stall", "a page is out of date"])
check(code == 0 and len(lines("g1")) == 3, "building again (a resumed goal) files no second line")
code, said = build("g2", ["skills/a/b.py"], ["we should loosen the assertion in the toy"])
check(code == 2 and "WAITING g2: a test loosened or deleted" in said and "PLAN_BREAK" in said and not lines("g2"), "a break that loosens a test still waits and the board names the class: %s" % said.strip()[:100])
code, said = build("g3", [".claude/settings.json"], ["a plain break"])
check(code == 2 and "WAITING g3: security and sandbox settings" in said, "a goal touching a settings file waits as a security subject")
code, said = build("g4", [], ["a plain break"])
check(code == 2 and "WAITING g4: unclassifiable" in said, "a break with no touches and no class is unclassifiable and waits")
code, said = build("g5", ["skills/a/b.py"], ["a plain break", "a second break"], {"deliver_first": {"goal": {"g5": False}}})
check(code == 2 and "WAITING g5: setting off" in said and not lines("g5"), "with the setting off for g5, its first break waits for the owner as today")
code, said = build("g6", ["skills/a/b.py"], ["a plain break"], {"deliver_first": {"goal": {"g5": False}}})
check(code == 0 and len(lines("g6")) == 1, "the other goal's break does not wait and files its line")

# the setting: nesting and the owner reference
open(tmp + "/.loop/tasks/t1.md", "w").write("# t1\n- release: v1\n- goals: ga gb\n")
open(tmp + "/.loop/tasks/t2.md", "w").write("# t2\n- release: v1\n- goals: gc\n")
open(tmp + "/.loop/tasks/t3.md", "w").write("# t3\n- release: v1\n- goals: gd\n")
json.dump({"deliver_first": {"release": {"v1": False}, "task": {"t1": True}, "goal": {"ga": False}}}, open(tmp + "/.loop/config.json", "w"))
on = lambda g: dlf.setting(tmp, g)[0]
check([on("ga"), on("gb"), on("gc"), on("gd"), on("zz")] == [False, True, False, False, True],
      "release off, task t1 on, goal ga off inside it: ga waits, t1's other goal does not, the release's other tasks wait, a goal in no task is on")
check(dlf.setting(tmp, "ga")[1] == "goal" and dlf.setting(tmp, "gb")[1] == "task" and dlf.setting(tmp, "gc")[1] == "release" and dlf.setting(tmp, "zz")[1] == "default", "the most specific scope wins and is named")
said = dlf.set_setting(tmp, "goal", "gb", "off", "")
check(said == "refused: set deliver_first off for goal gb needs an owner reference; unchanged (on, from task)", "a change with no owner reference is refused, with the pinned wording: %s" % said)
check(json.load(open(tmp + "/.loop/config.json"))["deliver_first"].get("goal", {}).get("gb") is None, "and nothing changed")
got = subprocess.run([sys.executable, os.path.join(root, "skills", "workflow-delivery", "scripts", "dlf.py"), "set", "deliver_first", "off", "--scope", "goal", "--id", "gb"], capture_output=True, text=True, cwd=tmp, env=env)
check(got.returncode == 1 and got.stdout.startswith("refused: set deliver_first off for goal gb"), "the command refuses the same way and exits non-zero")
# an open design choice in a step's reply (a PENDING line): a line and the recommended answer, unless the table says it waits
import goal as goal_mod  # noqa: E402
os.chdir(tmp)
json.dump(dict(config), open(tmp + "/.loop/config.json", "w"))
ask = ["approve the plan wording", "pick the first of two names"]
check(goal_mod.choices({"slug": "gq", "touches": ["skills/a/b.py"]}, ask, "plan") is True and len(lines("gq")) == 2, "two PENDING choices on a goal with declared touches become two lines and the goal goes on")
check(goal_mod.choices({"slug": "gq", "touches": ["skills/a/b.py"]}, ask, "plan") is True and len(lines("gq")) == 2, "the same choices again file no second line")
check(goal_mod.choices({"slug": "gr", "touches": []}, ask, "plan") is False and not lines("gr"), "a choice on a goal with no touches is unclassifiable: it waits")
check(goal_mod.choices({"slug": "gs", "touches": [".claude/settings.json"]}, ask, "plan") is False, "a choice on a goal touching a settings file waits")
check(goal_mod.choices({"slug": "gt", "touches": ["docs/wiki/Deliver-first.md"]}, ask, "plan") is False, "a choice on a goal touching a requirement page changes what a feature promises: it waits")
check(goal_mod.choices({"slug": "gu", "touches": ["skills/a/b.py"]}, [], "plan") is False, "no PENDING items: nothing to settle")
sys.exit(1 if failed else 0)
