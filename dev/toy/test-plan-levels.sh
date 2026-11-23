#!/bin/bash
# reads: skills/workflow-delivery/scripts/planlevel.py skills/workflow-delivery/scripts/planfault.py skills/workflow-delivery/scripts/fitkit.py skills/workflow-delivery/scripts/fit.py
# DEL-22.1 and DEL-22.2: every goal gets one plan level by a fixed decision table, the same goal always the same level, a plan past its level's limit is
# reported missed with its cause, and a changed setting applies with no code change. Each rule's check runs once on its real fixture (PASS) and once
# as a CONTROL on a fixture that breaks only that rule (the same check must then fail).
# DEL-22.4's scope: the fallback is on only for a goal the frozen release brief reaches, read by implement-v110's own brief.py from origin/main.
# Own temp HOME and TMPDIR, removed at the end; stand-ins only. usage: test-plan-levels.sh
set -u
unset LOOP_SESSION_TOOL LOOP_OPERATION_SESSION CLAUDE_CODE_HOST_SESSION_ID CLAUDE_CODE_SESSION_ID CLAUDE_SESSION_ID LOOP_POD_ID
export LOOP_ROLE=worker
here=$(cd "$(dirname "$0")/../.." && pwd)
. "$here/dev/toy/reap.sh"
export HOME=$(mktemp -d) USERPROFILE="$HOME" LOOP_PRIVATE_NAMES=/dev/null
export TMPDIR="$HOME/tmp"; mkdir -p "$TMPDIR"
toy_on_exit 'rm -rf "$HOME"'
d="$HOME/repo"; mkdir -p "$d" && cd "$d" && git init -q -b main && git config user.email t@example.test && git config user.name Toy
mkdir -p skills/a/scripts skills/b/scripts docs && : > skills/a/scripts/x.py && : > skills/b/scripts/y.py && : > docs/p.md
git add -A && git commit -qm base; mkdir -p .git/loop/runs
export PLAN_SCRIPTS="$here/skills/workflow-delivery/scripts" PLAN_HERE="$here"
python3 - <<'PY'
import json, os, random, subprocess, sys, tempfile, time
sys.path.insert(0, os.environ["PLAN_SCRIPTS"])
import planlevel

fails = []
def check(ok, text):
    print(("PASS: " if ok else "FAIL: ") + text)
    ok or fails.append(text)

top = os.getcwd()
lv = lambda lines, touches, cfg=None: planlevel.level_of(lines, touches, top, cfg)
# 22.1: the decision table, first match wins
check(lv(["x"], []) == {"level": "large", "rule": "no touches"}, "rule 1: no touches declared gives large")
check(lv(["x"], ["github:wiki"])["level"] == "large" and "GitHub" in lv(["x"], ["github:wiki"])["rule"], "rule 1: a GitHub surface gives large")
check(lv(["x"], ["skills/a/scripts", "skills/b/scripts"]) == {"level": "large", "rule": "2 areas"}, "rule 2: two code areas give large")
check(lv(["it changes a guard"], ["skills/a/scripts"]) == {"level": "large", "rule": "safety word guard"}, "rule 3: a safety word in a done line gives large")
check(lv(["it changes a hook"], ["skills/a/scripts"], {"safety_words": ["lane"]})["level"] != "large", "rule 3 is the SETTING: with safety_words set to lane only, a hook is not safety")
check(lv(["DEL-22.1 holds"], ["skills/a/scripts"]) == {"level": "normal", "rule": "one area, names DEL-22"}, "rule 4: one area and a done line naming an ID gives normal")
check(lv(["it works"], ["skills/a/scripts"]) == {"level": "small", "rule": "one area, no ID"}, "rule 5: one area and no ID gives small")
check(lv(["it works"], ["docs"]) == {"level": "small", "rule": "no code area"}, "rule 5: docs only gives small, no code area")
# controls: breaking only one rule's fixture changes the answer the check looks at
check(lv(["it works"], ["skills/a/scripts"])["level"] != "normal", "control: the same goal WITHOUT an ID is not normal (so rule 4 is what made it normal)")
check(lv(["DEL-22.1 holds"], ["skills/a/scripts", "skills/b/scripts"])["level"] != "normal", "control: with a second area the ID no longer makes it normal (rule 2 comes first)")
# determinism: the same goal always gets the same level, whatever the order of its touches
touches = ["skills/a/scripts", "skills/b/scripts", "docs"]
seen = set()
for _ in range(20):
    random.shuffle(touches)
    seen.add(str(lv(["x"], list(touches))))
check(len(seen) == 1, "the same goal gets the same level and rule on 20 shuffles of its touches")
# 22.2: limits are settings; a changed setting applies with no code change; a bad value names itself
check({k: v["minutes"] for k, v in planlevel.limits({}).items()} == {"small": 10, "normal": 30, "large": 45}, "the template defaults are small 10, normal 30, large 45 minutes")
check(planlevel.limits({"small": {"minutes": 1}})["small"]["minutes"] == 1, "a repo setting changes a level's limit with no code change")
check(planlevel.limits({"small": {"needs": ["a", "b"]}})["small"]["needs"] == ["a", "b"], "a repo setting changes a level's review set")
check(planlevel.limits({"small": {"minutes": "x"}})["small"]["minutes"] == 10 and planlevel.fixes({"small": {"minutes": "x"}}) and "plan_levels.small.minutes" in planlevel.fixes({"small": {"minutes": "x"}})[0],
      "a bad value falls back to the default AND a FIX line names the key")
check(not planlevel.fixes({"small": {"minutes": 5}}), "control: a good value gives no FIX line")
# missed: the record compares the measured minutes with the limit (detect-only, with its cause)
class Board:
    def __init__(self, seconds):
        self.s = seconds
    def seconds_by_step(self, run, at):
        return {"plan": self.s}
import fit
state = {"slug": "g", "plan": {"level": "small", "rule": "one area, no ID"}}
def recorded(seconds):
    fit.monitor = lambda *a, **k: Board(seconds)
    planlevel.config = lambda top=None: {"small": {"minutes": 1}}  # the repo's setting, as origin/main would give it
    planlevel.record("g", state, "plan")
    return planlevel.sidecar("g")["record"]
long = recorded(120)
check(long["missed"] is True and long["limit"] == 1 and long["minutes"] == 2.0, "a plan that took 2 minutes against a 1-minute limit is MISSED")
check(long["cause"] == "cause unknown", "with no per-review data the missed cause reads 'cause unknown', never a guess")
planlevel.config = lambda top=None: {"small": {"minutes": 10}}
def seconds_vs_ten(seconds):
    fit.monitor = lambda *a, **k: Board(seconds)
    planlevel.record("g", state, "plan")
    return planlevel.sidecar("g")["record"]
check(seconds_vs_ten(602)["missed"] is True and seconds_vs_ten(602)["minutes"] == 10.0, "a plan 2 seconds over its 10-minute limit is MISSED (the compare is on seconds, not on the rounded 10.0 minutes)")
check(seconds_vs_ten(600)["missed"] is False, "control: a plan of exactly 10 minutes is not missed")
short = recorded(30)
check(short["missed"] is False, "control: a plan within its limit is not missed")

# 22.4's scope: the approval covers a goal only if the FROZEN release brief on origin/main reaches it (read by brief.py)
import hashlib
here = os.environ["PLAN_HERE"]
real = ""
for ref in ("origin/main", "origin/loop/implement-v110"):  # the branch until it has merged
    real = real or subprocess.run(["git", "-C", here, "show", ref + ":skills/workflow-release/scripts/brief.py"], capture_output=True, text=True).stdout
check(bool(real), "brief.py is on origin/main or on implement-v110's branch, so the ON cases below can run (this goal merges after implement-v110)")
bare = tempfile.mkdtemp()
git = lambda *a: subprocess.run(["git"] + list(a), capture_output=True, text=True, cwd=top)
git("init", "-q", "-b", "main", bare)  # a non-bare local origin: nothing is sent anywhere
git("remote", "add", "origin", bare)
approval = {"fallback_approved": {"id": "o807", "release": "v1.1.0"}}
def frozen(text, rec="o1"):
    body = text if text.endswith("\n") else text + "\n"
    return body + "Frozen: %s %s 2026-11-22\n" % (hashlib.sha256(body.encode()).hexdigest(), rec)
RELEASE = "# v1.1.0 brief\n\n## Tasks\n\n1. task-a\n"
TASK = "# task-a\n\n- Feature: DEL-22\n- Release: v1.1.0\n- Goals: v110-del22, other\n- Needs: \n\n## Purpose\n\nx\n\n## Done when\n\n- x\n"
def publish(release, task, brief=True, sources=None):
    for rel in ["docs/release-brief-1.1.0.md", ".loop/tasks/task-a.md", "skills/workflow-release/scripts/brief.py"] + [".loop/sources/" + n for n in os.listdir(os.path.join(top, ".loop/sources"))] if os.path.isdir(os.path.join(top, ".loop/sources")) else ["docs/release-brief-1.1.0.md", ".loop/tasks/task-a.md", "skills/workflow-release/scripts/brief.py"]:
        if os.path.exists(os.path.join(top, rel)):
            os.remove(os.path.join(top, rel))
    for name, body in (sources or {}).items():
        os.makedirs(os.path.join(top, ".loop/sources"), exist_ok=True)
        open(os.path.join(top, ".loop/sources", name), "w").write(body)
    os.makedirs(os.path.join(top, "docs"), exist_ok=True)
    os.makedirs(os.path.join(top, ".loop/tasks"), exist_ok=True)
    os.makedirs(os.path.join(top, "skills/workflow-release/scripts"), exist_ok=True)
    if brief and real:
        open(os.path.join(top, "skills/workflow-release/scripts/brief.py"), "w").write(real)
    release is None or open(os.path.join(top, "docs/release-brief-1.1.0.md"), "w").write(release)
    task is None or open(os.path.join(top, ".loop/tasks/task-a.md"), "w").write(task)
    git("add", "-A")
    git("commit", "-q", "-m", "briefs", "--allow-empty")
    subprocess.run(["git", "-C", bare, "fetch", "-q", top, "HEAD"])
    subprocess.run(["git", "-C", bare, "checkout", "-q", "-f", "-B", "main", "FETCH_HEAD"])
    git("fetch", "-q", "origin", "main")
on = lambda slug="v110-del22", cfg=approval: planlevel.fallback_on(cfg, slug, top)
publish(frozen(RELEASE), frozen(TASK), brief=False)
check(on() is False, "brief.py is not on main: the fallback is off (fail closed), however well formed the briefs are")
if real:
    publish(None, None)
    check(on() is False, "no brief on origin/main: off")
    publish(RELEASE, frozen(TASK))
    check(on() is False, "a release brief with no Frozen last line: off")
    publish(frozen(RELEASE), frozen(TASK))
    check(on() is True, "a frozen release brief naming a task whose frozen task brief lists the goal: ON")
    check(on("some-other-goal") is False, "control: the same briefs, a goal the task does not list: off")
    publish(frozen(RELEASE), frozen(TASK.replace("Goals: v110-del22, other", "Goals: other")))
    check(on() is False, "control: the task's Goals bullet without this goal's slug: off")
    publish(frozen(RELEASE.replace("task-a", "task-b")), frozen(TASK))
    check(on() is False, "control: the release brief names another task, so this goal's task is not in the cut: off")
    edited = frozen(RELEASE).replace("1. task-a\n", "1. task-a\n2. task-z\n")  # a SEPARATE numbered line added after the freeze: it must be refused
    publish(edited, frozen(TASK))
    check(on() is False, "control: a release brief with a numbered task line added after its freeze (its sha256 no longer matches) is refused, not read: off")
    publish(frozen(RELEASE), frozen(TASK).replace("v110-del22", "v110-del22, intruder"))
    check(on() is False, "control: a task brief edited after its freeze: off")
    publish(frozen(RELEASE), frozen(TASK))
    check(on(cfg={}) is False and on(cfg={"fallback_approved": "o807"}) is False, "no approval object, or one of the wrong shape: off")
    check(on(cfg={"fallback_approved": {"id": "o807", "release": "../../x"}}) is False, "a release that is not a version name never reaches git")
    # the Source form (existing task briefs): it counts ONLY when its .loop/sources file verifies against the sha256 it names
    raw = "the owner's draft\n\n## Purpose\n\nx\n\n## Done when\n\n- x\n"
    sha = hashlib.sha256(raw.encode()).hexdigest()[:16]
    SRC = "# task-a\n\n- Feature: DEL-22\n- Release: v1.1.0\n- Goals: v110-del22\n- Needs: \n- Source: src-a (sha256 %s), owner o1\n\n## Purpose\n\nx\n\n## Done when\n\n- x\n" % sha
    publish(frozen(RELEASE), SRC, sources={"src-a.md": raw})
    check(on() is True, "a Source-form task brief whose .loop/sources file matches its sha256 and holds its words: ON")
    publish(frozen(RELEASE), SRC)
    check(on() is False, "control: the same Source-form brief with NO source file is only 'unverified' and does not count: off")
    publish(frozen(RELEASE), SRC, sources={"src-a.md": raw.replace("the owner's draft", "another draft")})
    check(on() is False, "control: a source file whose words changed (the sha256 no longer matches): off")
    # the missing-task-brief reason, fallback-off reasons (no record id), fault codes (default snapshot; the reviewed test sets evidence), masks
    # DEL-22.4 test sets "evidence" in its own config), and every mask in a quoted record is marked
    import planfault
    publish(frozen(RELEASE), None)
    got = planlevel.fallback_check(approval, "v110-del22", top)
    check(got[0] is False and "has no brief file on origin/main" in got[1] and "task-a" in got[1], "a task named by the frozen release brief with no brief file gives the reason 'has no brief file', naming the task")
    publish(frozen(RELEASE), frozen(TASK))
    check(planlevel.fallback_check({}, "v110-del22", top) == (False, "no plan_levels.fallback_approved on origin/main (the owner's approval record is not set there)"), "no approval: off, with a reason")
    reasons = [planlevel.fallback_check(c, s, top)[1] for c, s in ((approval, "some-other-goal"), ({}, "g"), ({"fallback_approved": {"id": "o807", "release": "../x"}}, "g"))]
    check(all(reasons) and not any("o807" in r for r in reasons), "every 'fallback off' reason is given and none names the owner's record id")
    log = os.path.join(tempfile.mkdtemp(), "g.jsonl")
    open(log, "w").write("")
    row = lambda code: json.dumps({"schema": "1", "decision": "deny", "disposition": "fallback", "code": code, "path": "/home/someone/proj/x"}) + "\n"
    held = {"log_pos": 0}
    open(log, "w").write(row("snapshot") + row("evidence"))
    check([r["code"] for r in planfault.faults({"guard_log": log}, held)[0]] == ["snapshot"], "the DEFAULT fault codes are snapshot only (an 'evidence' refusal is not a fault unless the config says so)")
    check([r["code"] for r in planfault.faults({"guard_log": log, "fault_codes": ["evidence"]}, held)[0]] == ["evidence"], "a config that sets fault_codes to evidence takes the evidence refusal (the reviewed DEL-22.4 test) and not the snapshot one")
    lst = os.path.join(tempfile.mkdtemp(), "names")
    open(lst, "w").write("# toy list\nzebra-secret\n")
    os.environ["LOOP_PRIVATE_NAMES"] = lst
    word = planfault.mask("the Zebra-Secret service")
    check("zebra" not in word.lower() and "<masked: private word>" in word, "a flagged private word (any case) is replaced by a mark that says what it was")
    check(planfault.mask("an ordinary refusal") == "an ordinary refusal", "control: text with no flagged word is unchanged")
    # the REAL call path: a guard-log row is masked per string value and then dumped (quote_of); the raw dumps text is checked too
    win = "C:" + chr(92) + "Users" + chr(92) + "bob" + chr(92) + "proj"
    rowx = {"path": win, "posix": "/home/bob", "mail": "a@b.co", "tok": "abcdefghijklmnopqrstuvwxyz0123", "gh": "https://github.com/o/r/issues/1", "web": "https://evil.test/x", "word": "caf" + chr(233) + "-secret"}
    quote = planfault.quote_of(rowx)
    try:
        back = json.loads(quote)
    except (TypeError, ValueError):  # each check below must fail on its own, never crash the toy
        back = {}
    check(quote is not None and "bob" not in quote and back.get("path", "").startswith("<masked: path>") and back.get("posix") == "<masked: path>", "a Windows and a POSIX home path in a guard row are masked, and the quote stays whole JSON")
    check(back.get("gh") == "https://github.com/o/r/issues/1" and back.get("web") == "<masked: url>" and back.get("mail") == "<masked: email>" and back.get("tok") == "<masked: token>", "a GitHub URL is kept exactly; another URL, an email and a token are each marked")
    # more masking cases (TD1113): home paths of every form, which URLs are kept, a token in a kept URL
    cases = {"c:" + chr(92) + "users" + chr(92) + "bob" + chr(92) + "x": "lower-case drive path", "C:" + chr(92) + "USERS" + chr(92) + "bob": "upper-case folder",
             chr(92) * 2 + "srv" + chr(92) + "Users" + chr(92) + "bob" + chr(92) + "p": "UNC path", "C:" + chr(92) + "Users" + chr(92) + "John Smith" + chr(92) + "proj": "name with a space",
             "/" + "Users/John Smith/x": "POSIX name with a space", "/" + "home/john smith/x": "lower-case second name", "C:" + chr(92) + "Users" + chr(92) + "O'Brien" + chr(92) + "x": "apostrophe", "/" + "home/bob " + chr(201) + "mile/x": "non-ASCII capital"}
    for text, what in cases.items():
        got = planfault.mask(text)
        check("bob" not in got and "John" not in got and "Smith" not in got and got.startswith("<masked: path>"), "home path masked: " + what)
    for bad in ("https://github.com.evil.test/x", "https://github.com@evil.test/x", "https://github.com/o/r?x=1"):
        check(planfault.mask(bad) == "<masked: url>", "not a plain github.com URL, so masked: " + bad.split("/")[2] + (" with a query" if "?" in bad else ""))
    check(planfault.mask("https://github.com/o/r/issues/1 ok") == "https://github.com/o/r/issues/1 ok", "control: a plain github.com URL is kept exactly")
    check(planfault.mask("https://github.com/o/r/ghp_abcdefgh1234567890") == "https://github.com/o/r/<masked: token>", "a token inside a kept GitHub URL is masked")
    open(lst, "w").write("zebra-secret\ncaf" + chr(233) + "-secret\n")
    os.environ["LOOP_PRIVATE_NAMES"] = lst
    check("secret" not in planfault.quote_of(rowx) and "<masked: private word>" in planfault.quote_of(rowx), "a flagged word with a non-ASCII letter is masked")
    os.environ["LOOP_PRIVATE_NAMES"] = os.path.join(os.path.dirname(lst), "missing")
    check(planfault.quote_of(rowx) is None, "a broken private list gives no quote at all")
    # a withheld quote leaves a MARKED entry; two refusals of one goal keep two issue keys
    log = os.path.join(os.path.dirname(lst), "guard.jsonl")
    open(log, "w").write("")
    json.dump({"slug": "wh", "worker": "session", "plan": {"level": "small", "rule": "x"}}, open(os.path.join(top, ".git", "loop", "runs", "wh.json"), "w"))
    planlevel.save("wh", {"log_pos": 0})
    planlevel.config = lambda top=None: {"guard_log": log}
    def refuse(ts):
        open(log, "a").write(json.dumps({"decision": "deny", "disposition": "fallback", "code": "snapshot", "ts": ts, "path": win}) + "\n")
        planlevel.ask("wh", "base")
        return planlevel.sidecar("wh")
    one = refuse("t1")
    check(one["refusals"] == ["<masked: quote withheld, private list broken>"] and "bob" not in json.dumps(one), "with a broken list the record holds one marked 'quote withheld' entry and none of the words")
    two = refuse("t2")
    check(two["refusals"] == ["<masked: quote withheld, private list broken>"] * 2 and two["issue"]["key"] != one["issue"]["key"], "a second refusal while the list is still broken gets its own issue key (not one shared key)")
    def refuse_nots(path):
        open(log, "a").write(json.dumps({"decision": "deny", "disposition": "fallback", "code": "snapshot", "path": path}) + "\n")
        planlevel.ask("wh", "base")
        return planlevel.sidecar("wh")["issue"]["key"]
    k1, k2 = refuse_nots("a"), refuse_nots("b")
    check(k1 != k2, "withheld refusals whose log rows carry no ts still get their own issue keys")
    os.environ["LOOP_PRIVATE_NAMES"] = "/dev/null"
    check(planfault.mask(chr(0) + "0" + chr(0) + " plain") == chr(0) + "0" + chr(0) + " plain", "odd characters in the log text leave the quote whole")
    # interrupts are not swallowed, an exit from brief.py is
    publish(frozen(RELEASE), frozen(TASK))
    import planfault
    saved = planlevel.git
    def boom(exc):
        def raiser(*a, **k):
            raise exc
        return raiser
    planlevel.git = boom(SystemExit(3))
    check(planfault.brief_goals("v1.1.0", top) == [], "an exit from the brief reader gives no goals (fail closed)")
    planlevel.git = boom(KeyboardInterrupt())
    try:
        planfault.brief_goals("v1.1.0", top)
        check(False, "an interrupt is not swallowed by the brief reader")
    except KeyboardInterrupt:
        check(True, "an interrupt is NOT swallowed by the brief reader (only Exception and SystemExit are)")
    planlevel.git = saved
print("ALL PASS" if not fails else "%d FAILED" % len(fails))
sys.exit(1 if fails else 0)
PY
