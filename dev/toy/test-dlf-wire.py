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
check(goal_mod.choices({"slug": "gp", "touches": ["skills/a/b.py"]}, ["the plan is past its review cap: approve one more round"], "plan") is True
      and len([l for l in lines("gp") if "| plan |" in l]) == 1, "a plan past its review cap is its own stop, one line, and the goal goes on")
check(goal_mod.choices({"slug": "gr", "touches": []}, ask, "plan") is False and not lines("gr"), "a choice on a goal with no touches is unclassifiable: it waits")
check(goal_mod.choices({"slug": "gs", "touches": [".claude/settings.json"]}, ask, "plan") is False, "a choice on a goal touching a settings file waits")
check(goal_mod.choices({"slug": "gt", "touches": ["docs/wiki/Deliver-first.md"]}, ask, "plan") is False, "a choice on a goal touching a requirement page changes what a feature promises: it waits")
check(goal_mod.choices({"slug": "gu", "touches": ["skills/a/b.py"]}, [], "plan") is None, "no PENDING items: nothing to settle")
# DLF-1.1's own test: three red-team breaks, a plan past its cap and a budget past the cap: the goal goes on and the release has ONE issue listing all five
import fit  # noqa: E402
import guards  # noqa: E402
code, said = build("gx", ["skills/a/b.py"], ["break one", "break two", "break three"])
goal_mod.choices({"slug": "gx", "touches": ["skills/a/b.py"]}, ["the plan is past its review cap: one more round?"], "plan")
runs = tmp + "/.git/loop/runs"
guards.add_set(runs, "gx", "budget", {"minutes": 480, "tokens": 0}, "set")
fit.active_minutes = lambda state, at=None, cfg=None: 480
dlf.budget_stop("gx", {"slug": "gx", "eta": {"minutes": 288, "estimate": 240, "basis": "x"}, "flow": {}, "log": []}, runs, {}, top=tmp)
five = lines("gx")
check(code == 0 and len(five) == 5 and len(json.load(open(fake + "/state.json"))["issues"]) == 1, "three breaks, a plan past its cap and a budget past the cap: one issue, five lines (%d)" % len(five))
check(sorted(l.split("|")[1].strip() for l in five) == ["break", "break", "break", "cap", "plan"] and all("settle with:" in l for l in five), "the five are three breaks, one plan, one cap, each with its settle line")
check("reached its 2x cap at 480 of 240" in "".join(five) and "keep working at the cap" in "".join(five), "the cap line says the goal reached its 2x cap and keeps working")
# the ON-scope token case past the cap: one cap line, the goal keeps working (no refusal), and a second check files no second line
guards.add_set(runs, "gk", "budget", {"minutes": 0, "tokens": 2000}, "set")
fit.active_minutes = lambda state, at=None, cfg=None: 5
for _ in range(2):
    dlf.budget_stop("gk", {"slug": "gk", "eta": {"minutes": 288, "estimate": 240, "basis": "x"}, "flow": {}, "tokens": {"idea": 2000}, "log": []}, runs, {"token_budget": 1000}, top=tmp)
check(len(lines("gk")) == 1 and "reached its 2x cap at 2000 of 1000" in lines("gk")[0], "2000 tokens against a 1000 estimate: one cap line, the goal keeps working, and a second check files none")
# review finding 1: with auto_approve on, a pending decision is still settled: a safety one waits, a benign one becomes a line
auto = {"auto_approve": True}
check(goal_mod.autoapprove({"slug": "ga1", "touches": [".claude/settings.json"]}, ["approve the new sandbox setting"], "plan", auto) is False, "finding 1: with auto_approve on, a pending decision on a security setting still waits")
check(goal_mod.autoapprove({"slug": "ga2", "touches": ["skills/a/b.py"]}, ["pick a name"], "plan", auto) is True and len([l for l in lines("ga2") if "| choice |" in l]) == 1, "finding 1: with auto_approve on, a benign pending decision files its line and the goal goes on")
check(goal_mod.autoapprove({"slug": "ga3", "touches": ["skills/a/b.py"]}, [], "plan", auto) is True and not lines("ga3"), "with auto_approve on and nothing pending the old rule holds")
json.dump(dict(config, deliver_first={"goal": {"ga4": False}}), open(tmp + "/.loop/config.json", "w"))
check(goal_mod.autoapprove({"slug": "ga4", "touches": [".claude/settings.json"]}, ["approve it"], "plan", auto) is True and not lines("ga4"), "with deliver-first off for the goal auto_approve works as it always did")
# round 3, finding A: `STEP: pending <reason>` with NO PENDING line is a pending decision too: with auto_approve on, a sandbox one never auto-approves
reply = "STEP: pending approve the sandbox permission change"
why_a = reply.split("pending ", 1)[1]
check(goal_mod.autoapprove({"slug": "gpa", "touches": ["skills/a/b.py"]}, [], "plan", auto, "pending", why_a) is False, "finding A: a pending result naming a sandbox permission change, with no PENDING line, waits under auto_approve")
check(goal_mod.autoapprove({"slug": "gpb", "touches": ["skills/a/b.py"]}, [], "plan", auto, "pending", "") is False, "finding A: a pending result with no decision context at all fails closed: it waits")
check(goal_mod.autoapprove({"slug": "gpc", "touches": ["skills/a/b.py"]}, [], "plan", auto, "pending", "pick a name") is True and len([l for l in lines("gpc") if "| choice |" in l]) == 1, "finding A: a benign pending result files its line and goes on (negative control)")
check(goal_mod.autoapprove({"slug": "gpd", "touches": ["skills/a/b.py"]}, [], "plan", auto, "done", "") is True, "a done step with nothing pending still follows the old rule")
sys.exit(1 if failed else 0)
