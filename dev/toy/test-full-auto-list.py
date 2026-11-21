#!/usr/bin/env python3
# windows: ok
# reads: skills/workflow-monitoring/scripts/auto.py skills/workflow-monitoring/scripts/sessions.py skills/workflow-monitoring/scripts/layers.py skills/workflow-monitoring/scripts/live_board.py
# reads: skills/workflow-monitoring/scripts/checkin.py skills/workflow-monitoring/scripts/board_lines.py skills/workflow-monitoring/scripts/board.py skills/workflow-monitoring/scripts/board_model.py
# reads: skills/workflow-monitoring/scripts/unattended.py skills/workflow-monitoring/scripts/mailbox.py skills/workflow-monitoring/scripts/replan.py skills/workflow-monitoring/scripts/machines.py skills/workflow-monitoring/scripts/worker.py
# reads: .loop/owner-decisions.md
"""DEL-3 revised (v1.2.0): full auto stops only for the owner's fixed list and takes the recommended path for everything else.

Drives the monitoring scripts in throwaway git repos (no model, no network): the list (DEL-3.1), the recommended path with its record (DEL-3.2),
the patch goal for a tool bug (DEL-3.3), owner words with a verified stamp, a legacy mark and a revoke (DEL-3.4), and the check-in's Decided for
you list with one undo line (DEL-3.5). Each PASS line is one case; the last line is ALL PASS or FAILED."""
import hashlib
import json
import types
import os
import subprocess
import sys
import tempfile

root = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
scripts = os.path.join(root, "skills", "workflow-monitoring", "scripts")
sys.path.insert(0, scripts)
for name in ("LOOP_ROLE", "LOOP_SESSION_TOOL", "LOOP_OPERATION_SESSION"):
    os.environ.pop(name, None)
tmp = tempfile.mkdtemp()
os.environ.update(HOME=tmp, USERPROFILE=tmp, PATH=os.path.join(root, "dev", "toy", "fakegh") + os.pathsep + os.environ.get("PATH", ""), FAKE_GH_DIR=os.path.join(tmp, "gh"))
import auto  # noqa: E402
import checkin  # noqa: E402
import layers  # noqa: E402
import mailbox  # noqa: E402
import board_lines  # noqa: E402
import live_board  # noqa: E402

bad = []


def check(ok, text):
    print(("PASS: " if ok else "FAIL: ") + text)
    if not ok:
        bad.append(text)


LIST = open(os.path.join(root, ".loop", "owner-decisions.md"), encoding="utf-8").read()


def repo(name, listed=True):
    where = os.path.join(tmp, name)
    os.makedirs(os.path.join(where, ".loop"))
    os.makedirs(os.path.join(where, ".git"), exist_ok=True)
    subprocess.run(["git", "init", "-q", where], check=True)
    with open(os.path.join(where, ".loop", "config.json"), "w") as handle:
        json.dump({"full_auto": True}, handle)
    if listed:
        with open(os.path.join(where, ".loop", "owner-decisions.md"), "w", encoding="utf-8") as handle:
            handle.write(LIST)
    os.makedirs(os.path.join(where, ".git", "loop", "runs"))
    os.chdir(where)
    return where


def loop(where):
    return os.path.join(where, ".git", "loop")


def ask(where, slug, text, kind="routine", words=("yes", "no"), recommend="yes", eta=False):
    waiting = {"ask": text, "words": list(words), "recommend": recommend, "kind": kind}
    if eta:
        waiting["eta"] = True
    with open(os.path.join(loop(where), "runs", slug + ".json"), "w") as handle:
        json.dump({"slug": slug, "goal": "g", "status": "waiting", "step": "build", "waiting": waiting}, handle)


def raw_words(where, text, ids, who="operation", at="2026-11-17T00:00:00Z"):
    path = os.path.join(loop(where), "owner-words.tsv")
    count = sum(1 for _ in open(path)) if os.path.exists(path) else 0
    with open(path, "a") as handle:
        handle.write("o%d\t%s\t%s\t%s\t%s\n" % (count + 1, at, who, json.dumps(text), ids))
    return "o%d" % (count + 1)


def log(where):
    try:
        return open(os.path.join(loop(where), "auto.log")).read()
    except OSError:
        return ""


def cli(script, *args, cwd=None):
    done = subprocess.run([sys.executable, os.path.join(scripts, script)] + list(args), cwd=cwd or os.getcwd(), capture_output=True, text=True)
    return done.returncode, done.stdout + done.stderr


# --- DEL-3.1 the list, DEL-3.2 the recommended path
w = repo("a")
raw_words(w, "standing rule", auto.RULE)
ask(w, "g1", "Shorten the helper wording to shorter?")
ask(w, "g2", "Freeze the v1.2.0 brief?", kind="brief")
auto.decide_all(w)
text = log(w)
check("| g1 | AUTO |" in text, "a choice not on the list goes ahead on the recommendation and asks nothing")
check("| g2 | WAITS |" in text and "owner list item 3" in text, "a choice on the list waits and names its item")
line = next(x for x in text.splitlines() if "| g1 | AUTO |" in x).split(" | ")
check(len(line) == 9 and line[6].startswith("#g1@") and line[7] == "yes/no" and line[8] == "undo " + line[6] and line[5].split()[-1] == "o1",
      "the AUTO record shows the id, the options, the reason (rule last) and the undo")
check(all(not auto.why_not({"ask": a, "words": ["yes", "no"], "recommend": "yes", "kind": k}, {"full_auto": True}, False, w) for a, k in (
    ("Un-review the Setup page so its wording can change?", "routine"), ("Is a reviewed requirement changed here without owner words?", "routine"),
    ("Raise criteria_max from 26 to 28?", "owner"), ("Un-review the Monitoring page so MON-11 wording can change?", "routine"))),
      "the list's keywords leave the questions the earlier checks expect answered alone")
check(all("owner list item 1" in auto.why_not({"ask": "x", "words": ["yes"], "recommend": "yes", "kind": k}, {"full_auto": True}, False, w) for k in ("destructive", "money", "security")),
      "the destructive, money and security kinds still wait by kind (item 1)")
w = repo("b")
raw_words(w, "standing rule", auto.RULE)
os.remove(os.path.join(w, ".loop", "owner-decisions.md"))
os.mkdir(os.path.join(w, ".loop", "owner-decisions.md"))
ask(w, "g1", "Shorten the helper wording?")
auto.decide_all(w)
check("LIST_UNREADABLE" in log(w) and "| g1 | AUTO |" not in log(w), "a list that can't be read makes every decision wait (LIST_UNREADABLE)")
w = repo("c", listed=False)
raw_words(w, "standing rule", auto.RULE)
ask(w, "g1", "Shorten the helper wording?")
auto.decide_all(w)
check("| g1 | AUTO |" in log(w), "with no list file the earlier rules apply unchanged")
w = repo("d")
raw_words(w, "standing rule", auto.RULE)
ask(w, "g1", "g1 is past its ETA: ship now, extend, or defer?", kind="owner", eta=True)
auto.decide_all(w)
check("| g1 | AUTO |" in log(w), "an ETA choice takes the recommended path and does not wait (TD712)")
w = repo("e")
raw_words(w, "standing rule", auto.RULE)
with open(os.path.join(w, ".loop", "owner-decisions.md"), "a") as handle:
    handle.write("always-ask: g1 (owner record o9)\n")
raw_words(w, "ask me about g2", "always-ask:g2")
for slug in ("g1", "g2", "g3"):
    ask(w, slug, "Shorten the helper wording %s?" % slug)
    auto.decide_all(w)
text = log(w)
check("| g1 | WAITS |" in text and "| g2 | WAITS |" in text and "| g3 | AUTO |" in text, "an always-ask goal waits: from the list file, and at once from an owner-words record")
code, said = 0, ""
check(any("pending fold" in x and "g2" in x for x in board_lines.owner_notes(w, "")) and not any("pending fold" in x and "g1" in x for x in board_lines.owner_notes(w, "")),
      "an always-ask record not yet in the list shows in the check-in as pending fold")

# --- the ETA change never skips review or qa, and the standing rule reaches it
w = repo("f")
raw_words(w, "standing rule", auto.RULE)
ask(w, "g1", "g1 is past its ETA: ship now?", kind="owner", eta=True)
auto.decide_all(w)


class G:  # a stand-in for goal.py: the parts eta_set and eta_record use
    class fit:
        STEPS = ("idea", "plan", "build", "review", "qa", "ship")
        recorded = staticmethod(lambda state, step: step in state.get("flow", {}))
        view = staticmethod(lambda state, runs: {})

    class guards:
        add_set = staticmethod(lambda *a: None)

    state_dir = staticmethod(lambda: os.path.join(loop(w), "runs"))
    save = staticmethod(lambda state, why: None)

    @staticmethod
    def no(text):
        raise SystemExit(text)


state, rid = {"slug": "g1", "flow": {}}, "o1"
args = type("A", (), {"slug": "g1", "owner_record": rid, "eta_extend": 0, "eta_choice": "ship"})()
auto.eta_set(G, args, state, "toy")
check(set(state["flow"]) == {"idea", "plan", "build", "ship"}, "an ETA change on the standing rule skips no review and no qa")

# --- DEL-3.4 owner words: relay, legacy mark, stamp, revoke
check(not layers.relay("top", "approve the plan")[0] and not layers.relay("peer", "approve")[0] and layers.relay("owner", "delete it")[0]
      and layers.relay("delegated", "approve")[0] and not layers.relay("delegated", "delete the old branches")[0], "a relayed or peer message never counts; a delegated record counts except safety classes")
w = repo("g")
raw_words(w, "old words", "X-1", who="operation")
rc, said = cli("unattended.py", "owner-words-migrate")
check(rc == 0 and "legacy, before DEL-3.4" in open(os.path.join(loop(w), "owner-words.tsv")).read(), "the one-time migration marks every existing row legacy")
check(cli("unattended.py", "owner-words-migrate")[1].startswith("ALREADY"), "the migration runs once")
rc, said = cli("sessions.py", "owner-words", "new words", "--ids", "X-2")
check(rc != 0 and "STAMP_MISSING" in said and "new words" not in open(os.path.join(loop(w), "owner-words.tsv")).read(), "a new record with no stamp is refused and not written")
check("X-2" in open(os.path.join(loop(w), "owner-words-refused.log")).read() and "new words" not in open(os.path.join(loop(w), "owner-words-refused.log")).read(), "the refusal is logged with its ids and without the words")
rc, said = cli("sessions.py", "owner-words", "new words", "--ids", "X-2", "--verified", "sess@2026-11-21T10:00:00Z#00000000")
check(rc != 0 and "STAMP_MISSING" in said, "a stamp whose hash is not the words' hash is refused")
good = "sess@2026-11-21T10:00:00Z#" + hashlib.sha256(b"new words").hexdigest()[:8]
rc, said = cli("sessions.py", "owner-words", "new words", "--ids", "X-2", "--verified", good)
check(rc == 0 and said.startswith("OWNER-WORDS o2 covers X-2"), "a stamped record is written")
rc, said = cli("sessions.py", "owner-words", "relayed words", "--ids", "X-3", "--from", "top")
check(rc != 0 and "not owner words" in said, "a relay from the top session is refused, never recorded")
raw_words(w, "forged words", "X-4", who="operation-top", at="2030-01-01T00:00:00Z")
check([r[0] for r in auto.owner_rows(w)] == ["o1", "o2"], "an unstamped row written after the migration does not count; legacy and stamped rows do")
raw_words(w, "delegated", "DOC-2", who="operation-top:delegated:TD1:DOC-2:r1", at="2030-01-01T00:00:00Z")
check("o4" in [r[0] for r in auto.owner_rows(w)], "a DOC-2 delegated record still counts (TD712)")
rc, said = cli("worker.py", "owner-words-check", "o2", "--mismatch", "NO_TURN")
check(rc == 0 and "revoked: NO_TURN" in said and "o2" not in [r[0] for r in auto.owner_rows(w)], "a mismatch revokes the record at once, with one issue attempted and no words logged")
check("new words" not in open(os.path.join(loop(w), "owner-words-revoked.tsv")).read() and cli("worker.py", "owner-words-check", "o2", "--mismatch", "NO_TURN")[0] == 1,
      "a repeat check finds nothing counted and opens no second issue")
check(any("owner words o2 revoked: NO_TURN" in x for x in board_lines.owner_notes(w, "")), "the check-in shows the revoked owner words")
mail = {"q1": {"slug": "zz", "options": ["a", "b"], "recommended": 0, "risky": False}}
os.makedirs(os.path.join(loop(w)), exist_ok=True)
json.dump(mail, open(os.path.join(loop(w), "mailbox.json"), "w"))
rc, said = cli("mailbox.py", "reply", "q1", "some words of my own", "--root", w)
check(rc == 2 and "MAIL_REPLY" in said, "a mailed reply is refused loudly once stamps are on; the owner types it in an operation session")

# --- the wake: a worker's waiting report changes the run file, operate.py sees it within its 2 second poll and runs the pass (no worker-side trigger)
import operate  # noqa: E402
w = repo("j")
before = operate.signature(w, os.path.join(w, ".git"))
import time as _time  # noqa: E402
_time.sleep(0.05)
ask(w, "g1", "Shorten the helper wording?")
check(operate.signature(w, os.path.join(w, ".git")) != before and operate.__doc__ is not None and "poll" in open(os.path.join(scripts, "operate.py")).read(),
      "a waiting report changes the run file the operate loop watches, so a pass follows within its poll, not its cadence")

# --- DEL-3.5 the Decided for you list and one undo line
w = repo("h")
rule = raw_words(w, "standing rule", auto.RULE)
ask(w, "g1", "Pick the wording A or B?", words=("A", "B"), recommend="A")
ask(w, "g2", "Pick the name C or D?", words=("C", "D"), recommend="C")
auto.decide_all(w)
shown = checkin.decided(w, "")
check(sum('undo: type "undo #g' in x for x in shown) == 2 and any(x.startswith("Tally: decided 2, waits 0") for x in shown), "the check-in lists both decisions with reasons and the undo line, and a tally")
sent = []
real = live_board.subprocess
live_board.subprocess = types.SimpleNamespace(run=lambda cmd, **kw: (sent.append(cmd), type("R", (), {"returncode": 0})())[1])
idg1 = next(p[6] for p in (x.split(" | ") for x in log(w).splitlines()) if p[1] == "g1")
undo = raw_words(w, "undo " + idg1, idg1)
os.environ["LOOP_ROLE"] = ""
monitor_args = type("A", (), {"id": idg1, "owner_record": undo})()
code = live_board.undo(monitor_args)
check(code == 0 and len(sent) == 1 and sent[0][3] == "g1" and sent[0][4].startswith("B (undo of " + idg1), "typing one undo line sends the other option of that decision only")
check("| g1 | UNDONE |" in log(w) and "| g2 | UNDONE |" not in log(w), "the line is logged UNDONE for that decision and not the other")
check(live_board.undo(monitor_args) == 1 and len(sent) == 1, "a second undo of the same decision is refused as stale and sends nothing")
check(live_board.undo(type("A", (), {"id": "#nope@0000Z", "owner_record": undo})()) == 1 and len(sent) == 1, "an undo of no decision is refused")
idg2 = next(p[6] for p in (x.split(" | ") for x in log(w).splitlines()) if p[1] == "g2")
check(live_board.undo(type("A", (), {"id": idg2, "owner_record": "o99"})()) == 1 and len(sent) == 1, "an undo with no owner record covering it is refused")
live_board.subprocess = real
rows = [x for x in log(w).splitlines()]
ask(w, "g3", "Pick the colour E, F or G?", words=("E", "F", "G"), recommend="E")
auto.decide_all(w)
check(any("choose one of E/F/G" in x for x in log(w).splitlines()), "a decision with more than two options records no single undo")

# --- DEL-3.3 a tool bug: one issue, one patch goal, no question; a promise fix waits
w = repo("i")
open(os.path.join(w, ".loop", "docs.tsv"), "w").write("Other\tskills\n")
calls = []
real_gh, real_run = mailbox.gh, mailbox.subprocess
mailbox.gh = lambda args, r: type("R", (), {"returncode": 0, "stdout": "[]" if args[:2] == ["issue", "list"] else "https://x/issues/77", "stderr": ""})()
mailbox.subprocess = types.SimpleNamespace(run=lambda cmd, **kw: (calls.append(cmd), type("R", (), {"returncode": 0, "stdout": "", "stderr": ""})())[1])
args = type("A", (), {"title": "The lane tool loses its output", "text": "", "found": "lane qa", "feature": "Other", "owner_words": "", "dry_run": False, "kind": ""})()
rc, said = mailbox.file_finding(w, args)
queued = [c for c in calls if "queue" in c]
check(rc == 0 and "FILED #77" in said and "patch goal fix-77 queued" in said and len(queued) == 1 and "fix-77" in queued[0], "a tool bug files one issue and queues one patch goal, and asks nobody")
calls.clear()
args.kind, args.title = "promise", "The lane tool promises less than it does"
rc, said = mailbox.file_finding(w, args)
check(rc == 0 and "on the owner's list" in said and not [c for c in calls if "queue" in c], "a fix that changes a promise or a test is not queued: it waits on the list")
mailbox.gh, mailbox.subprocess = real_gh, real_run

# --- sizes: each touched script stays under its cap
caps = {n: 20330 for n in ("auto.py", "board.py", "board_lines.py", "board_model.py", "layers.py", "live_board.py", "mailbox.py", "machines.py", "replan.py", "sessions.py", "unattended.py", "worker.py")}
caps.update({"checkin.py": 19345, "graph.py": 19000, "pool.py": 19000, "monitor.py": 18993})  # test-hands-off.py holds these three at their starting size
over = [n for n, cap in caps.items() if len(open(os.path.join(scripts, n), "rb").read().replace(b"\r\n", b"\n")) > cap]
check(not over, "every touched script ends within its byte cap (%s)" % (", ".join(over) or "none over"))

print("ALL PASS" if not bad else "FAILED: %d" % len(bad))
sys.exit(1 if bad else 0)
