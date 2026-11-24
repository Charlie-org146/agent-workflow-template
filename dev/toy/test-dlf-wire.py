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
git_t = lambda *a: subprocess.run(["git", "-C", tmp, "-c", "user.name=t", "-c", "user.email=t@t"] + list(a), capture_output=True)
git_t("commit", "-q", "--allow-empty", "-m", "base")
git_t("update-ref", "refs/remotes/origin/main", "HEAD")  # the base a live stop's branch diff is read against
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
check(dlf.choices(goal_mod, {"slug": "gq", "touches": ["skills/a/b.py"]}, ask, "plan") is True and len(lines("gq")) == 2, "two PENDING choices on a goal with declared touches become two lines and the goal goes on")
check(dlf.choices(goal_mod, {"slug": "gq", "touches": ["skills/a/b.py"]}, ask, "plan") is True and len(lines("gq")) == 2, "the same choices again file no second line")
check(dlf.choices(goal_mod, {"slug": "gp", "touches": ["skills/a/b.py"]}, ["the plan is past its review cap: approve one more round"], "plan") is True
      and len([l for l in lines("gp") if "| plan |" in l]) == 1, "a plan past its review cap is its own stop, one line, and the goal goes on")
check(dlf.choices(goal_mod, {"slug": "gr", "touches": []}, ask, "plan") is False and not lines("gr"), "a choice on a goal with no touches is unclassifiable: it waits")
check(dlf.choices(goal_mod, {"slug": "gs", "touches": [".claude/settings.json"]}, ask, "plan") is False, "a choice on a goal touching a settings file waits")
check(dlf.choices(goal_mod, {"slug": "gt", "touches": ["docs/wiki/Deliver-first.md"]}, ask, "plan") is False, "a choice on a goal touching a requirement page changes what a feature promises: it waits")
check(dlf.choices(goal_mod, {"slug": "gu", "touches": ["skills/a/b.py"]}, [], "plan") is None, "no PENDING items: nothing to settle")
# DLF-1.1's own test: three red-team breaks, a plan past its cap and a budget past the cap: the goal goes on and the release has ONE issue listing all five
import fit  # noqa: E402
import guards  # noqa: E402
code, said = build("gx", ["skills/a/b.py"], ["break one", "break two", "break three"])
dlf.choices(goal_mod, {"slug": "gx", "touches": ["skills/a/b.py"]}, ["the plan is past its review cap: one more round?"], "plan")
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
check(dlf.autoapprove(goal_mod, {"slug": "ga1", "touches": [".claude/settings.json"]}, ["approve the new sandbox setting"], "plan", auto) is False, "finding 1: with auto_approve on, a pending decision on a security setting still waits")
check(dlf.autoapprove(goal_mod, {"slug": "ga2", "touches": ["skills/a/b.py"]}, ["pick a name"], "plan", auto) is True and len([l for l in lines("ga2") if "| choice |" in l]) == 1, "finding 1: with auto_approve on, a benign pending decision files its line and the goal goes on")
check(dlf.autoapprove(goal_mod, {"slug": "ga3", "touches": ["skills/a/b.py"]}, [], "plan", auto) is True and not lines("ga3"), "with auto_approve on and nothing pending the old rule holds")
json.dump(dict(config, deliver_first={"goal": {"ga4": False}}), open(tmp + "/.loop/config.json", "w"))
check(dlf.autoapprove(goal_mod, {"slug": "ga4", "touches": [".claude/settings.json"]}, ["approve it"], "plan", auto) is True and not lines("ga4"), "with deliver-first off for the goal auto_approve works as it always did")
# round 3, finding A: `STEP: pending <reason>` with NO PENDING line is a pending decision too: with auto_approve on, a sandbox one never auto-approves
reply = "STEP: pending approve the sandbox permission change"
why_a = reply.split("pending ", 1)[1]
check(dlf.autoapprove(goal_mod, {"slug": "gpa", "touches": ["skills/a/b.py"]}, [], "plan", auto, "pending", why_a) is False, "finding A: a pending result naming a sandbox permission change, with no PENDING line, waits under auto_approve")
check(dlf.autoapprove(goal_mod, {"slug": "gpb", "touches": ["skills/a/b.py"]}, [], "plan", auto, "pending", "") is False, "finding A: a pending result with no decision context at all fails closed: it waits")
check(dlf.autoapprove(goal_mod, {"slug": "gpc", "touches": ["skills/a/b.py"]}, [], "plan", auto, "pending", "pick a name") is True and len([l for l in lines("gpc") if "| choice |" in l]) == 1, "finding A: a benign pending result files its line and goes on (negative control)")
check(dlf.autoapprove(goal_mod, {"slug": "gpd", "touches": ["skills/a/b.py"]}, [], "plan", auto, "done", "") is True, "a done step with nothing pending still follows the old rule")
# round 3, finding C: a raise and the cap line are independent: estimate 240, held 240, spend 500 raises to 480 AND files one cap line
guards.add_set(runs, "gcc", "budget", {"minutes": 240, "tokens": 0}, "set")
fit.active_minutes = lambda state, at=None, cfg=None: 500
with __import__("contextlib").redirect_stdout(__import__("io").StringIO()):
    dlf.budget_stop("gcc", {"slug": "gcc", "eta": {"minutes": 288, "estimate": 240, "basis": "x"}, "flow": {}, "log": []}, runs, {}, top=tmp)
check(fit.view({"slug": "gcc"}, runs)["budget"]["minutes"] == 480, "finding C: 500 spent against 240 held with a 240 estimate raises the budget to 480")
check(len(lines("gcc")) == 1 and "reached its 2x cap at 500 of 240" in lines("gcc")[0], "finding C: and files exactly one cap line in the same check")
# round 4, finding 3: a later DIFFERENT decision at the same position is a new line, never the earlier (maybe accepted) one
dlf.choices(goal_mod, {"slug": "go1", "touches": ["skills/a/b.py"]}, ["first question"], "plan")
dlf.choices(goal_mod, {"slug": "go1", "touches": ["skills/a/b.py"]}, ["a different question"], "plan")
check(len([l for l in lines("go1") if "| choice |" in l]) == 2, "finding 3: two different choices at the same position of the same step are two lines")
dlf.choices(goal_mod, {"slug": "go1", "touches": ["skills/a/b.py"]}, ["first question"], "plan")
check(len([l for l in lines("go1") if "| choice |" in l]) == 2, "finding 3: the same choice again is still one line")
fit.breaks(goal_mod, {"slug": "go2", "touches": ["skills/a/b.py"]}, [{"principle": 1, "text": "first break"}])
fit.breaks(goal_mod, {"slug": "go2", "touches": ["skills/a/b.py"]}, [{"principle": 1, "text": "a different break"}])
check(len([l for l in lines("go2") if "| break |" in l]) == 2, "finding 3: a fresh review's different break at the same index is a new line")
# round 4/5 privacy: a secret-shaped value OR a configured private name in a pending decision is never held, printed or stored (withheld whole)
import guards  # noqa: E402
secret = "ghp_" + "Q7" * 18
ask_text = dlf.held_ask(tmp, "plan", ["rotate the key %s today" % secret], "")
check(secret not in ask_text and "Q7Q7" not in ask_text and ask_text == "plan left this for you: text withheld", "finding 4: a secret-shaped value in a pending decision is withheld: %s" % ask_text)
check(secret not in dlf.held_ask(tmp, "plan", [], "STEP reason has %s" % secret), "finding 4: a secret in the step's pending reason is withheld too")
named = dlf.held_ask(tmp, "plan", ["approve the page about acmesecret"], "")
check("acmesecret" not in named and named.endswith("text withheld"), "round 5: a configured private name in a pending decision is withheld: %s" % named)
wait_text = dlf.settle(tmp, runs, "gpn", "break", "n1", "touch the sandbox for acmesecret", "words", "rec", paths=["skills/a/b.py"])
check(wait_text[0] == "wait" and "acmesecret" not in wait_text[1], "round 5: a safety wait line never prints a configured private name: %s" % wait_text[1])
check(dlf.held_ask(tmp, "plan", ["pick a name"], "") == "plan left this for you: pick a name", "a benign ask is unchanged (negative control)")
os.environ["LOOP_PRIVATE_NAMES"] = "/dev/null"
check(dlf.held_ask(tmp, "plan", ["about acmesecret"], "") == "plan left this for you: about acmesecret", "with an explicit empty private-name list there is nothing to withhold")
os.environ["LOOP_PRIVATE_NAMES"] = home + "/names"
# round 5, safety finding: a live stop is classified with the branch's REAL diff, so a weakened assertion is found; an unreadable diff fails closed
subprocess.run(["git", "-C", tmp, "-c", "user.name=t", "-c", "user.email=t@t", "commit", "-q", "--allow-empty", "-m", "base"], capture_output=True)
subprocess.run(["git", "-C", tmp, "branch", "-f", "main"], capture_output=True)
subprocess.run(["git", "-C", tmp, "update-ref", "refs/remotes/origin/main", "HEAD"], capture_output=True)
os.makedirs(tmp + "/tests", exist_ok=True)
open(tmp + "/tests/test_a.py", "w").write("def test():\n    assert total == 3\n")
subprocess.run(["git", "-C", tmp, "add", "tests"], capture_output=True)
subprocess.run(["git", "-C", tmp, "-c", "user.name=t", "-c", "user.email=t@t", "commit", "-q", "-m", "test"], capture_output=True)
subprocess.run(["git", "-C", tmp, "update-ref", "refs/remotes/origin/main", "HEAD"], capture_output=True)
st_n = {"slug": "gw3", "touches": ["skills/a/b.py"]}
check(dlf.choices(goal_mod, st_n, ["pick a name"], "plan") is True, "negative control: with only benign changes on the branch a choice becomes a line (the diff is read and clean)")
open(tmp + "/tests/test_a.py", "w").write("def test():\n    assert total >= 0\n")
subprocess.run(["git", "-C", tmp, "-c", "user.name=t", "-c", "user.email=t@t", "commit", "-q", "-am", "revise the expected value"], capture_output=True)
st_w = {"slug": "gw1", "touches": ["tests/test_a.py"]}
check(dlf.choices(goal_mod, st_w, ["approve the revised expected value"], "plan") is False and not lines("gw1"), "round 5: a pending decision after a weakened assertion in a test file waits (the branch diff is read)")
check(fit.breaks(goal_mod, {"slug": "gw2", "touches": ["tests/test_a.py"]}, [{"principle": 1, "text": "approve the revised expected value"}]).startswith("WAITING gw2: a test loosened or deleted"), "round 5: a red-team break after a weakened assertion waits and names the class")
st_n = {"slug": "gw3", "touches": ["skills/a/b.py"]}
real_branch_diff = fit.branch_diff
fit.branch_diff = lambda g: None
check(dlf.choices(goal_mod, st_n, ["pick another name"], "plan") is False, "round 5: a diff that cannot be read fails closed: unclassifiable, it waits")
fit.branch_diff = real_branch_diff
# round 5 re-review, privacy (low): the scan covers the WHOLE text before the wait line is cut to 120 characters (a configured private name straddling the cut is not half printed)
straddle = "x" * 115 + "acmesecret and more"
cut_wait = dlf.settle(tmp, runs, "gst", "break", "s1", straddle, "words", "rec", paths=[".claude/settings.json"])
check(cut_wait[0] == "wait" and "acmes" not in cut_wait[1] and "text withheld" in cut_wait[1], "re-review: a private name straddling character 120 is withheld whole, not half printed: %s" % cut_wait[1][:90])
# final re-review, privacy: callers must not cut the free text before the scan sees it (a private name starting near character 196 leaked its first letters into the posted line)
git_t("update-ref", "refs/remotes/origin/main", "HEAD")
tail_name = "y" * 195 + "acmesecret and more"
st_x = {"slug": "gcx", "touches": ["skills/a/b.py"]}
git_t("reset", "-q", "--hard", "origin/main")
check(dlf.choices(goal_mod, st_x, [tail_name], "plan") is False and not any("acmes" in b for b in [c["body"] for cs in json.load(open(fake + "/state.json"))["comments"].values() for c in cs]), "final: a choice whose private name straddles the old 200-character cut waits and posts no prefix of it")
check(fit.breaks(goal_mod, {"slug": "gcy", "touches": ["skills/a/b.py"]}, [{"principle": 1, "text": tail_name}]).startswith("WAITING gcy: private data") and not any("acmes" in b for b in [c["body"] for cs in json.load(open(fake + "/state.json"))["comments"].values() for c in cs]), "final: a break whose private name straddles the old 200-character cut waits and posts no prefix of it")
sys.exit(1 if failed else 0)
