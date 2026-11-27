#!/usr/bin/env python3
# windows: ok
# reads: skills/workflow-delivery/scripts/outcomes.py skills/workflow-delivery/scripts/dlf.py skills/workflow-delivery/scripts/decisions.py
"""One review (DLF-1.3), after the start: each stop of a marked goal is a recorded decision and none waits on the owner; a
safety stop outside the approved items is an open finding, which pr and merge refuse until it is dropped, stopped or fixed.
A throwaway repo with its own home; the line filing is a stand-in; no network."""
import json
import os
import subprocess
import sys
import tempfile

root = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
sys.path.insert(0, os.path.join(root, "skills", "workflow-delivery", "scripts"))
home = tempfile.mkdtemp()
open(os.path.join(home, "names"), "w").write("zz-dummy-private-name\n")
os.environ.update(HOME=home, USERPROFILE=home, GIT_CONFIG_NOSYSTEM="1", LOOP_PRIVATE_NAMES=os.path.join(home, "names"),
                  GIT_AUTHOR_NAME="t", GIT_AUTHOR_EMAIL="t@example.invalid", GIT_COMMITTER_NAME="t", GIT_COMMITTER_EMAIL="t@example.invalid")
tmp = os.path.join(home, "repo")
subprocess.run(["git", "init", "-q", "-b", "main", tmp], check=True)
runs = os.path.join(tmp, ".git", "loop", "runs")
os.makedirs(runs)
failed = []


def check(ok, text):
    print(("PASS: " if ok else "FAIL: ") + text)
    if not ok:
        failed.append(text)


def sh(*args):
    return subprocess.run(["git", "-C", tmp] + list(args), capture_output=True, text=True, check=True).stdout.strip()


def put(rel, text):
    os.makedirs(os.path.dirname(os.path.join(tmp, rel)) or tmp, exist_ok=True)
    open(os.path.join(tmp, rel), "w").write(text)


def commit(rel, text, message="c"):
    put(rel, text)
    sh("add", rel)
    sh("commit", "-qm", message)


def refused(call):
    try:
        call()
    except SystemExit as stop:
        return str(stop.code)
    return ""


import decisions  # noqa: E402
import dlf  # noqa: E402

filed = []
dlf.file_line = lambda top, r, slug, rel, stop, subject, occ, what, words, rec: (filed.append((slug, stop, what)) or ("%s-%s-%d" % (slug, stop, len(filed)), ""))
dlf.retry = lambda *a: []
commit(".loop/config.json", json.dumps({"base": "main", "one_review": True}))
commit("tools/old.sh", "echo old\n")
commit("dev/toy/test-a.sh", "check one\ncheck two\n")
sh("update-ref", "refs/remotes/origin/main", "HEAD")
sh("switch", "-q", "-c", "loop/g")
commit(".loop/goals/g.md", "# G\n\n- Slug: g\n- Review: one\n")

ITEMS = [{"n": 1, "class": "a test loosened or deleted", "action": "update test a", "files": ["dev/toy/test-a.sh"], "approvable": True, "approved": True},
         {"n": 2, "class": "money", "action": "buy a seat", "files": [], "approvable": True, "approved": False}]


def record(slug="g", **more):
    state = dict({"slug": slug, "goal": slug, "status": "running", "step": "build", "branch": "loop/" + slug, "flow": {}, "log": [],
                  "worktree": tmp, "touches": ["docs/wiki"], "one_review": {"at": "t"},
                  "start_answer": {"record": "o1", "verdict": "approve", "items": ITEMS}}, **more)
    json.dump(state, open(os.path.join(runs, slug + ".json"), "w"))
    os.path.exists(decisions.ledger(runs, slug)) or decisions.create(runs, slug, by="t")
    return state


def settle(stop, what, occ, rec="do the recommended thing", **ctx):
    return dlf.settle(tmp, runs, "g", stop, occ, what, "say so", rec, **ctx)


def found(kind):
    return [e for e in decisions.entries(runs, "g") if e["kind"] == kind]


try:
    import outcomes
except ImportError as error:
    print("FAIL: outcomes.py is missing: %s" % error)
    sys.exit(1)
record()
got = settle("choice", "rename a local variable or keep it", "c1", paths=["docs/wiki"], diff="")
check(got[0] == "continue" and found("decision") and found("decision")[-1]["safety"] == [] and found("decision")[-1]["taken"] == "do the recommended thing"
      and not found("finding") and len(filed) == 1, "a stop with no safety class takes the recommendation, listed and filed (a goal that touches wiki pages opens no finding): %s" % (got,))
got = settle("break", "red-team break: the plan would delete the old release", "b1", paths=["docs/wiki"], diff="")
one = found("finding")
check(got[0] == "continue" and len(one) == 1 and one[0]["classes"] == ["deleting what cannot be restored"] and one[0]["files"] == []
      and found("decision")[-1]["safety"], "a safety stop outside the items waits on nobody: an open finding and a listed decision (%s)" % (got,))
settle("break", "red-team break: the plan would delete the old release", "b1", paths=["docs/wiki"], diff="")
check(len(found("finding")) == 1, "the same stop again opens no second finding")
got = settle("choice", "buy a paid seat", "c2")
check(got[0] == "continue" and len(found("finding")) == 2, "a refused item's class is outside: the safe option")
settle("test", "a test failed", "t1", diff="diff --git a/dev/toy/test-a.sh b/dev/toy/test-a.sh\n--- a/dev/toy/test-a.sh\n+++ b/dev/toy/test-a.sh\n@@ -1 +1 @@\n-check one\n")
check(len(found("finding")) == 2 and found("decision")[-1]["inside"] == [1], "a stop inside an approved item goes on under that item: %s" % found("decision")[-1])
before = len(decisions.entries(runs, "g"))
check("ONE_REVIEW_DIFF" in refused(lambda: settle("test", "a test failed", "t2", diff=None)) and len(decisions.entries(runs, "g")) == before,
      "a needed diff that can't be read refuses and records nothing")
got = settle("choice", "key = " + "AKIA" + "B" * 16, "c3")
check(got[0] == "continue" and "AKIA" not in json.dumps(decisions.entries(runs, "g")) and found("decision")[-1]["question"] == "text withheld"
      and "private data" in found("finding")[-1]["classes"], "private text is withheld and is a finding, never a wait: %s" % (got,))

# deliver-first off, in the committed base or in the working copy, keeps today's wait
put(".loop/config.json", json.dumps({"base": "main", "one_review": True, "deliver_first": {"goal": {"g": False}}}))
got = settle("choice", "rename a local variable", "c4")
check(got[0] == "wait", "deliver-first off keeps today's wait: %s" % (got,))
sh("checkout", "-q", "--", ".loop/config.json")
sh("switch", "-q", "main")
commit(".loop/config.json", json.dumps({"base": "main", "one_review": True, "deliver_first": {"goal": {"g": False}}}))
sh("update-ref", "refs/remotes/origin/main", "HEAD")
sh("switch", "-q", "loop/g")
check(settle("choice", "rename a local variable", "c5")[0] == "wait", "off in the committed base wins over the branch")
sh("update-ref", "refs/remotes/origin/main", "main~1")


# pr and merge refuse while a finding is open, and open one for each new uncovered class and file of the branch diff
def blockers():
    return outcomes.blockers(tmp, runs, json.load(open(os.path.join(runs, "g.json"))), "origin/main", "HEAD")


listed = blockers()
check(len(listed) == 3 and all(x.startswith("finding ") for x in listed), "each open finding blocks pr and merge: %s" % listed)
commit("tools/clean.sh", 'rm -rf "$HOME/x"\n')
commit("dev/toy/test-a.sh", "check one\n")
listed = blockers()
check(len(listed) == 4 and "tools/clean.sh" in listed[-1] and len(found("finding")) == 4,
      "the branch diff opens one finding for a new class and file; a file an approved item covers opens none: %s" % listed)
blockers()
check(len(found("finding")) == 4, "and only once")
check(outcomes.blockers(tmp, runs, {"slug": "plain"}, "origin/main", "HEAD") == [], "an unmarked goal is not held")
ids = [e["n"] for e in found("finding")]


def close(number, how, files=()):
    return refused(lambda: outcomes.close(tmp, runs, json.load(open(os.path.join(runs, "g.json"))), number, how, "why", list(files), "origin/main", "operation"))


new = ids[-1]
check("ONE_REVIEW_CLOSE" in close(new, "drop") and len(blockers()) == 4, "a drop is refused while the part is still in the branch")
sh("rm", "-q", "tools/clean.sh")
sh("commit", "-qm", "take it out")
check(close(new, "drop") == "" and len(blockers()) == 3 and any("tools/clean.sh" in f[2] or "finding" in f[2] for f in filed),
      "once its files match the base it closes as dropped, and the part is filed: %s" % blockers())
commit("tools/clean.sh", 'rm -rf "$HOME/y"\n', "back again")
listed = blockers()
check(len(listed) == 4 and "tools/clean.sh" in " ".join(listed), "a dropped file changed again opens its finding again: %s" % listed)
sh("rm", "-q", "tools/clean.sh")
sh("commit", "-qm", "take it out again")
check("ONE_REVIEW_CLOSE" in close(ids[0], "drop"), "a finding that names no file isn't dropped as files without saying the action was not taken")
check(refused(lambda: outcomes.close(tmp, runs, json.load(open(os.path.join(runs, "g.json"))), ids[0], "not-taken", "the action was refused", [], "origin/main", "operation")) == ""
      and len(blockers()) == 2, "an asked action that is not taken closes its finding")
check("ONE_REVIEW_CLOSE" in close(999, "drop") and "ONE_REVIEW_CLOSE" in close(ids[0], "not-taken"), "an unknown or closed finding is refused")

# stop: the goal ends for good without merging
check(close(ids[1], "stop") == "" and json.load(open(os.path.join(runs, "g.json")))["status"] == "stopped"
      and decisions.stopped(decisions.entries(runs, "g")), "closing by stop stops the goal for good")

import reverts  # noqa: E402

# revert (done line 4): a listed decision has a command that says what it stops, and reverting stops that part
sh("update-ref", "refs/remotes/origin/main", "main")
sh("switch", "-q", "-c", "loop/r", "main")
commit("dev/toy/test-a.sh", "check one\n")
record("r", branch="loop/r")
diff_ = "diff --git a/dev/toy/test-a.sh b/dev/toy/test-a.sh\n--- a/dev/toy/test-a.sh\n+++ b/dev/toy/test-a.sh\n@@ -1 +1 @@\n-check two\n"
dlf.settle(tmp, runs, "r", "test", "t1", "a test failed", "w", "update the test", diff=diff_)
dlf.settle(tmp, runs, "r", "choice", "c1", "pick the shorter name", "w", "take it")


def rec(slug):
    return json.load(open(os.path.join(runs, slug + ".json")))


def decided(slug):
    return [e for e in decisions.entries(runs, slug) if e["kind"] == "decision"]


def revert(slug, number, **more):
    return refused(lambda: reverts.revert(tmp, runs, rec(slug), number, "operation", base="origin/main", **more))


let_go, plain = [e["n"] for e in decided("r")]
lines = reverts.listing(tmp, runs, rec("r"))
check(len(lines) == 2 and all("goal.py revert r " in x[1] and "\n" not in x[1] for x in lines)
      and "takes out dev/toy/test-a.sh" in lines[0][0] and "stops the goal" in lines[1][0],
      "each decision is listed with one revert command that runs as printed and what it stops: %s" % lines)
check(outcomes.blockers(tmp, runs, rec("r"), "origin/main", "HEAD") == [], "before a revert nothing holds the goal")
check(revert("r", let_go) == "" and rec("r")["status"] == "running" and not decisions.stopped(decisions.entries(runs, "r")),
      "reverting a decision that let files go on doesn't stop the goal")
held = outcomes.blockers(tmp, runs, rec("r"), "origin/main", "HEAD")
check(any("decision %d reverted" % let_go in x and "dev/toy/test-a.sh" in x for x in held) and any("finding" in x for x in held),
      "pr and merge wait for the part to be taken out, and the approval no longer covers it: %s" % held)
count = len(decisions.entries(runs, "r"))
check(revert("r", let_go) == "" and len(decisions.entries(runs, "r")) == count, "a repeat changes nothing")
sh("checkout", "-q", "main", "--", "dev/toy/test-a.sh")
sh("commit", "-qm", "take the part out")
held = outcomes.blockers(tmp, runs, rec("r"), "origin/main", "HEAD")
check(any("done lines are still met" in x for x in held), "with the files back it still needs operation's record that the done lines are met: %s" % held)
check(revert("r", let_go, met="done line 1 doesn't need the test change") == "", "operation records that")
held = outcomes.blockers(tmp, runs, rec("r"), "origin/main", "HEAD")
check(not [x for x in held if "reverted" in x], "then the revert holds nothing: %s" % held)
check(revert("r", plain) == "" and rec("r")["status"] == "stopped" and decisions.stopped(decisions.entries(runs, "r")),
      "reverting any other decision stops the goal without merging")
check("ONE_REVIEW_REVERT" in revert("r", 999) and "ONE_REVIEW_REVERT" in revert("r", 1), "only a listed decision is reverted")

# after the merge a revert takes nothing back: it records, files, and holds releases while named files stay shipped
sh("switch", "-q", "-c", "loop/m", "main")
commit("dev/toy/test-a.sh", "check one\n")
record("m", branch="loop/m", status="done", release="merged")
dlf.settle(tmp, runs, "m", "test", "t1", "a test failed", "w", "update the test", diff=diff_)
shipped = decided("m")[0]["n"]
before = len(filed)
check(revert("m", shipped) == "" and rec("m")["status"] == "done" and len(filed) == before + 1 and "reverted" in filed[-1][2],
      "after a merge the revert files a line and leaves the merged goal alone")
holds = reverts.holds(tmp)
check([(h["slug"], h["decision"]) for h in holds] == [("m", shipped)], "and holds releases until the removal is in: %s" % holds)
check(refused(lambda: reverts.release_check(tmp, "HEAD")) .find("ONE_REVIEW_HOLD") >= 0, "a release refuses while a removal is pending")
sh("switch", "-q", "main")
commit("other.txt", "unrelated\n", "unrelated")
check(refused(lambda: reverts.release_check(tmp, "HEAD")).find("ONE_REVIEW_HOLD") >= 0, "an unrelated commit clears no hold")
sys.path.append(os.path.join(root, "skills", "workflow-release", "scripts"))
import autorelease  # noqa: E402
check("ONE_REVIEW_HOLD" in autorelease.release_hold(tmp, "HEAD"), "the release scripts read the hold")
callers = {name: open(os.path.join(root, "skills", "workflow-release", "scripts", name)).read().count("release_hold(") for name in ("release.py", "autorelease.py", "review.py")}
check(callers["release.py"] >= 1 and callers["autorelease.py"] >= 2 and callers["review.py"] >= 1, "the manual cut, the automatic release and promote each ask: %s" % callers)
check(refused(lambda: reverts.clear_hold(tmp, "m", shipped, "0" * 40, "operation")).find("ONE_REVIEW_HOLD") >= 0, "a hold names a real removal commit")
commit("dev/toy/test-a.sh", "check one\ncheck two\nremoved the shipped part\n", "the removal")
reverts.clear_hold(tmp, "m", shipped, sh("rev-parse", "HEAD"), "operation")
check(refused(lambda: reverts.release_check(tmp, "HEAD")) == "" and "ONE_REVIEW_HOLD" in refused(lambda: reverts.release_check(tmp, "HEAD~1")),
      "once the removal is in the commit being released, the release goes on, and not before")
sh("switch", "-q", "loop/g")

# the check-in lists every decision with its command until the owner has been shown it and the goal is finished
sh("update-ref", "refs/remotes/origin/main", "main")
sh("switch", "-q", "-c", "loop/k", "main")
record("k", branch="loop/k")
dlf.settle(tmp, runs, "k", "choice", "c1", "pick the shorter name", "w", "take it")


def checkin(*flags):
    got = subprocess.run([sys.executable, os.path.join(root, "skills", "workflow-monitoring", "scripts", "checkin.py")] + list(flags),
                         capture_output=True, text=True, cwd=tmp, env=dict(os.environ))
    return got.stdout + got.stderr


def section(text):
    return text.split("\nDecided for you\n", 1)[1].split("\n\n")[0].split("\n") if "\nDecided for you\n" in text else []


number = decided("k")[0]["n"]
said = checkin()
mine = [x for x in section(said) if " k " in x or "k #" in x]
command = next((x.strip() for x in section(said) if "revert k %d" % number in x), "")
check(any("k #%d: pick the shorter name -> take it. Reverting it stops the goal." % number in x for x in mine) and command.startswith("cd ")
      and said.index("Decided for you") < said.index("Coming up"), "the check-in lists the decision with what a revert stops: %s" % (section(said) or said[-400:]))
check(command and len(command) > 100 and command.endswith("revert k %d" % number), "the command stands whole on its own line, however long: %d" % len(command))
check(not [e for e in decisions.entries(runs, "k") if e["kind"] == "delivered"], "a plain check-in marks nothing delivered")
json.dump(dict(rec("k"), status="retired"), open(os.path.join(runs, "k.json"), "w"))
check("revert k %d" % number in checkin(), "a retired goal's decision stays listed until the owner was shown it")
json.dump(dict(rec("k"), status="running"), open(os.path.join(runs, "k.json"), "w"))
checkin("--owner")
marked = [e for e in decisions.entries(runs, "k") if e["kind"] == "delivered"]
check([e["ids"] for e in marked] == [[number]], "--owner marks exactly the ids it printed: %s" % marked)
check("revert k %d" % number in checkin(), "shown but unfinished, it stays listed")
json.dump(dict(rec("k"), status="retired"), open(os.path.join(runs, "k.json"), "w"))
check("revert k %d" % number not in checkin(), "shown and finished, it leaves the list")
ran = subprocess.run(command, shell=True, capture_output=True, text=True, env=dict(os.environ))
check("stops without merging" in ran.stdout, "the printed command runs as it stands: %s" % (ran.stdout + ran.stderr).strip()[-160:])
sh("switch", "-q", "loop/g")

# closing by fix (E14, RT18): a later commit on the files, a clean rescan, a row of this finding seen red, and a reader's verdict
sh("switch", "-q", "main")
commit(".loop/regression.tsv", "# id\tlevel\tcommand\tgoal\tseen_red\tdescription\tcategory\tlink\nold-row\tland\ttrue\tD\t2026-01-01\tGiven x\tcriterion\t\n", "a row on the base")
sh("update-ref", "refs/remotes/origin/main", "main")
sh("switch", "-q", "-c", "loop/x", "main")
record("x", branch="loop/x")
commit("tools/clean.sh", 'echo start\nrm -rf "$HOME/x"\n', "risky")


def blk():
    return outcomes.blockers(tmp, runs, rec("x"), "origin/main", "HEAD")


def row(link, red="2026-02-02", ident="fix-row", note="Given a clean run, then nothing outside is removed"):
    text = open(os.path.join(tmp, ".loop/regression.tsv")).read()
    commit(".loop/regression.tsv", text + "%s\tland\ttrue\tD\t%s\t%s\tdefect\t%s\n" % (ident, red, note, link), "add " + ident)


verdict = os.path.join(home, "verdict.txt")
open(verdict, "w").write("looked at the change\nVERDICT: FIXED\n")
bad_verdict = os.path.join(home, "bad.txt")
open(bad_verdict, "w").write("VERDICT: NOT FIXED\n")
blk()
n = [e["n"] for e in decisions.entries(runs, "x") if e["kind"] == "finding"][-1]


def fix(row_id="fix-row", reader=None):
    return refused(lambda: outcomes.close(tmp, runs, rec("x"), n, "fix", "fixed it", [], "origin/main", "operation", row=row_id, reader=reader or verdict))


check("no commit after the finding" in fix(), "no fix without a commit on the finding's files: " + fix()[:90])
commit("tools/clean.sh", 'echo start\nrm -rf "$HOME/x/cache"\n', "narrower, still destructive")
row("finding:x:%d" % n)
check("the rescan still matches" in fix(), "no fix while the rescan still matches: " + fix()[:90])
commit("tools/clean.sh", "echo start\n", "the destructive line is gone")
check("not a row this goal added or changed" in fix("old-row"), "not with a row this goal didn't add or change")
row("finding:x:999", ident="other-row")
check("does not name finding:x:" in fix("other-row"), "not with a row that names another finding")
row("finding:x:%d" % n, red="", ident="never-red")
check("no recorded red run" in fix("never-red"), "not with a row never seen red")
check("VERDICT: FIXED" in fix(reader=bad_verdict), "not without a reader's verdict that it is fixed")
check(fix() == "" and not blk(), "a real fix closes the finding: %s %s" % (fix()[:60], blk()))
at = sh("rev-parse", "HEAD")
commit("tools/clean.sh", 'echo start\nrm -rf "$HOME/y"\n', "the match comes back")
check(any("open again" in x for x in blk()), "a later match opens it again: %s" % blk())
sh("reset", "-q", "--hard", at)
sh("reset", "-q", "--hard", "HEAD~6")
check(any("open again" in x for x in blk()), "and so does the fix leaving the branch: %s" % blk())
sh("switch", "-q", "loop/g")

# the two operation-only commands, and a safety break that nobody can accept away
record("h")
put("flow.json", "{}")
sh("update-ref", "refs/remotes/origin/main", "main")


def tool(role, *args):
    got = subprocess.run([sys.executable, os.path.join(root, "skills", "workflow-delivery", "scripts", "goal.py")] + list(args),
                         capture_output=True, text=True, cwd=tmp, env=dict(os.environ, LOOP_ROLE=role))
    return got.stdout + got.stderr


args = ("decide", "h", "--finding", "a mail asks for a paid add-on", "--class", "money")
check("a worker can't" in tool("worker", *args) and not [e for e in decisions.entries(runs, "h") if e["kind"] == "finding"], "a worker opens no finding by hand")
said = tool("operation", *args)
check("FINDING" in said and [e["source"] for e in decisions.entries(runs, "h") if e["kind"] == "finding"] == ["decide"], "operation records one from a report: " + said.strip()[:100])
number = [e["n"] for e in decisions.entries(runs, "h") if e["kind"] == "finding"][0]
done = ("finding-close", "h", str(number), "--how", "not-taken", "--why", "the reply said not to buy it")
check("a worker can't" in tool("worker", *done), "a worker closes nothing")
said = tool("operation", *done)
check("CLOSED finding" in said, "operation closes it: " + said.strip()[-120:])

sys.path.append(os.path.join(root, "skills", "workflow-monitoring", "scripts"))
# done line 2: after the start review nothing about a one-review goal waits on the owner; operation holds it
sh("update-ref", "refs/remotes/origin/main", "main")
for slug in os.listdir(runs):
    slug.startswith("h.") or os.remove(os.path.join(runs, slug))
ASK = {"ask": "pick the colour of the thing", "words": ["go on w1"]}
record("w1", status="waiting", waiting=ASK)
json.dump({"slug": "u1", "goal": "u1", "status": "waiting", "step": "build", "branch": "loop/u1", "flow": {}, "log": [], "worktree": tmp,
           "touches": [], "waiting": {"ask": "an older goal's question", "words": ["go on u1"]}}, open(os.path.join(runs, "u1.json"), "w"))
record("w2", status="stopped", finding="it stopped", preflight={"items": [{"id": "budget", "ask": "raise the budget?"}]})


def part(text, head):
    return text.split("\n%s\n" % head, 1)[1].split("\n\n")[0] if "\n%s\n" % head in text else ""


said = checkin()
needs, held = part(said, "Needs you"), part(said, "Held by the operation")
check("w1" not in needs and "w2" not in needs and "u1" in needs, "only the older goal needs the owner: %s" % needs[:300])
check("w1" in held and "pick the colour" in held and "goal.py answer w1" in held and "w2" in held, "the one-review goals are held by the operation: %s" % held[:300])
check(said.split("\n")[0].startswith("0 running, 1 waiting on you"), "the headline counts only what waits on the owner: %s" % said.split("\n")[0])
sys.path.append(os.path.join(root, "skills", "workflow-monitoring", "scripts"))
here = os.getcwd()
os.chdir(tmp)
import notify  # noqa: E402
mails = notify.events(tmp, "")
check(not [e for e in mails if e[2] in ("w1", "w2")], "no mail asks the owner about a one-review goal's stop: %s" % [(e[1], e[2]) for e in mails])
os.chdir(here)
# what stays the owner's: the release choice, and a goal whose deliver-first is off or set to always ask
record("w4", status="waiting", step="release", release="ask", waiting={"ask": "cut or leave", "words": ["cut w4", "leave w4"]})
record("w5", status="waiting", waiting={"ask": "a question with deliver first off", "words": ["go on w5"]})
record("w6", status="waiting", waiting={"ask": "a question set to always ask", "words": ["go on w6"]})
record("w7", status="stopped", finding="stopped with deliver first off")
put(".loop/config.json", json.dumps({"base": "main", "one_review": True, "deliver_first": {"goal": {"w5": False, "w7": False}}}))
open(os.path.join(tmp, ".git", "loop", "owner-words.tsv"), "a").write('o9\t2026-01-01T00:00:00Z\toperation\t"always ask me"\talways-ask:w6\n')
# the operation's own lines are not lost for a one-review goal
record("w8", status="done", step="release", review_wait=True, pr="https://example.invalid/pr/8")
record("w9", status="running", worker="session", session={"id": "local_x", "name": "w"}, updated="2026-01-01T00:00:00Z", log=["2026-01-01T00:00:00Z STEP build"])
said = checkin()
needs, held = part(said, "Needs you"), part(said, "Held by the operation")
check("w4 asks: cut or leave" in needs and "w4" not in held, "the owner's release choice stays under Needs you: %s" % needs[:260])
check("w5 asks" in needs and "w6 asks" in needs and "w5" not in held and "w6" not in held,
      "a goal with deliver-first off or set to always ask waits for the owner as before: %s" % needs[:300])
kept = {slug: open(os.path.join(runs, slug + ".json")).read() for slug in ("w4", "w5", "w6", "w7")}
for slug, text in kept.items():
    json.dump({k: v for k, v in json.loads(text).items() if k != "one_review"}, open(os.path.join(runs, slug + ".json"), "w"))
plain_head = checkin().split("\n")[0]
for slug, text in kept.items():
    open(os.path.join(runs, slug + ".json"), "w").write(text)
check(said.split("\n")[0] == plain_head, "and the headline counts them as it counts any goal waiting on the owner: %s / %s" % (said.split("\n")[0], plain_head))
check("w8" in held and "review.py record w8" in held and "w8: merge waiting on review" not in needs, "the review-wait line is kept, for the operation: %s" % held[-400:])
check("STALLED w9" in held and "STALLED w9" not in needs, "the stalled line is kept, for the operation: %s" % held[-400:])
here = os.getcwd()
os.chdir(tmp)
sys.path.append(os.path.join(root, "skills", "workflow-monitoring", "scripts"))
import notify  # noqa: E402
told = {e[2] for e in notify.events(tmp, "") if e[1] == "stopped"}
check("w7" in told and "w2" not in told, "a stop with deliver-first off is mailed to the owner as before: %s" % sorted(told))
os.chdir(here)
sh("checkout", "-q", "--", ".loop/config.json")
for slug in ("w4", "w5", "w6", "w7", "w8", "w9"):
    for name in os.listdir(runs):
        name.startswith(slug + ".") and os.remove(os.path.join(runs, name))
os.remove(os.path.join(tmp, ".git", "loop", "owner-words.tsv"))
got = tool("operation", "answer", "w1")
last = [e for e in decisions.entries(runs, "w1") if e["kind"] == "decision"]
check("ANSWERED w1" in got and last and last[-1]["stop"] == "hold" and "pick the colour" in last[-1]["question"], "operation's answer is a listed decision: %s %s" % (got.strip()[:60], last[-1:]))
import start_review  # noqa: E402
check(start_review.mark(runs, "w3", "t").get("preflight") == {"items": []}, "a marked goal asks no pre-flight questions")

# RT16: after a merge the revert command itself queues the removal goal, and is that goal's start review
sh("switch", "-q", "main")
sh("reset", "-q", "--hard")
record("z", branch="loop/z", status="done", release="merged")
dlf.settle(tmp, runs, "z", "test", "t1", "a test failed", "w", "update the test",
           diff="diff --git a/dev/toy/test-a.sh b/dev/toy/test-a.sh\n--- a/dev/toy/test-a.sh\n+++ b/dev/toy/test-a.sh\n@@ -1 +1 @@\n-check two\n")
shipped = [e for e in decisions.entries(runs, "z") if e["kind"] == "decision"][0]["n"]
os.makedirs(os.path.join(home, "f"), exist_ok=True)
flow = os.path.join(home, "f", "flow.json")
open(flow, "w").write(json.dumps({"steps": {x: "x" for x in ("idea", "plan", "review", "qa", "ship")}}))
os.environ["LOOP_FLOW"] = flow
said = tool("operation", "revert", "z", str(shipped))
queue = open(os.path.join(tmp, ".loop", "queue.md")).read() if os.path.exists(os.path.join(tmp, ".loop", "queue.md")) else ""
new_slug = "undo-z-%d" % shipped
check("QUEUED %s" % new_slug in said and "- slug: %s | touches: dev/toy/test-a.sh" % new_slug in queue and "done: " in queue,
      "the revert queues the removal goal: %s" % said.strip()[-200:])
row = [h for h in reverts.holds(tmp) if h.get("removal_goal") == new_slug][0]
made = start_review.mark(runs, new_slug, "t", done_sha=__import__("hashlib").sha256(("1. " + row.get("removal_done", "")).encode()).hexdigest())
check(made.get("start_answer", {}).get("verdict") == "approve" and made["start_answer"]["record"] == "revert:z:%d" % shipped
      and [(i["class"], i["files"], i["approved"]) for i in made["start_answer"]["items"]] == [("a test loosened or deleted", ["dev/toy/test-a.sh"], True)]
      and start_review.unanswered(dict(made, slug=new_slug)) == "", "the owner's revert command is its start review, for those files and classes only: %s" % made.get("start_answer"))
check("start_answer" not in start_review.mark(runs, "undo-z-999", "t"), "a goal no revert queued gets no such answer")

# RT3: a one-review goal with no estimate (any monitored start) takes its time budget as the estimate: it rises by itself up
# to twice that budget and then keeps working, so no step waits for the owner's words; an older goal is as before
sh("update-ref", "refs/remotes/origin/main", "main")
import fit  # noqa: E402
spent = [250]
fit.active_minutes = lambda *a, **k: spent[0]
fit.spent_tokens = lambda *a, **k: 0
CFG = {"time_budget_minutes": 240}


def budget(slug, **more):
    state = record(slug, budget={"minutes": 240, "tokens": 0}, **more)
    if "one_review" in more and more["one_review"] is None:
        state.pop("one_review")
        json.dump(state, open(os.path.join(runs, slug + ".json"), "w"))
    return refused(lambda: dlf.budget_stop(slug, json.load(open(os.path.join(runs, slug + ".json"))), runs, CFG, top=tmp))


def raised(slug):
    try:
        return json.load(open(os.path.join(runs, slug + ".extra.json")))["set"]["budget"]["minutes"]
    except (OSError, KeyError):
        return 240


said = budget("n1")
check(said == "" and 250 < raised("n1") <= 480, "with no estimate the budget rises by itself: %s %s" % (said[:90], raised("n1")))
first = raised("n1")
spent[0] = 600
before = len(filed)
said = refused(lambda: dlf.budget_stop("n1", json.load(open(os.path.join(runs, "n1.json"))), runs, CFG, top=tmp))
check(said == "" and first <= raised("n1") <= 480 and len(filed) == before + 1, "past twice the first budget it files one line and keeps working at the cap: %s %s" % (said[:90], raised("n1")))
spent[0] = 250
said = budget("n2", one_review=None)
check("BUDGET_MINUTES" in said, "an older goal with no estimate is held as before: %s" % said[:110])

# RT8: revert and merge take one lock, so a revert waits for a merge that is under way
record("lk")
dlf.settle(tmp, runs, "lk", "choice", "c1", "pick the shorter name", "w", "take it")
first = [e for e in decisions.entries(runs, "lk") if e["kind"] == "decision"][0]["n"]
lock = os.path.join(tmp, ".git", "loop", "merge.lock")
open(lock, "w").write("%d\n" % os.getpid())  # a live holder, as a running merge is
waiter = subprocess.Popen([sys.executable, os.path.join(root, "skills", "workflow-delivery", "scripts", "goal.py"), "revert", "lk", str(first)],
                          cwd=tmp, env=dict(os.environ, LOOP_ROLE="operation"), stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
try:
    waiter.wait(timeout=6)
    early = True
except subprocess.TimeoutExpired:
    early = False
check(not early and not [e for e in decisions.entries(runs, "lk") if e["kind"] == "revert"], "a revert waits while a merge holds the lock")
os.remove(lock)
out, err = waiter.communicate(timeout=60)
check("REVERTED lk" in out and not os.path.exists(lock), "and goes on once it is free: %s" % (out + err).strip()[-140:])
# a merge by hand isn't checked, and the output says so
check("not enforced" in outcomes.hand_note({"auto_merge": False}, {"one_review": {"at": "t"}}) and "not enforced" in outcomes.hand_note({"auto_merge": True}, {"one_review": {"at": "t"}, "release": "ask"})
      and outcomes.hand_note({"auto_merge": True}, {"one_review": {"at": "t"}}) == "" and outcomes.hand_note({"auto_merge": False}, {}) == "", "pr says a hand merge is not held")
check("hand_note(" in open(os.path.join(root, "skills", "workflow-delivery", "scripts", "goal_steps.py")).read(), "goal.py pr prints that note")

import board_log  # noqa: E402
import board_model  # noqa: E402
put(".loop/goals/h.plan.md", "plan\n")
red = board_log.red_dir(tmp)
os.makedirs(red, exist_ok=True)
json.dump({"sha": board_log.plan_sha(tmp, "h"), "breaks": [{"principle": 6, "text": "it deletes the old release"}, {"principle": 3, "text": "the plan is slow"}]},
          open(os.path.join(red, "plan-h.json"), "w"))
open(os.path.join(tmp, ".git", "loop", "owner-words.tsv"), "w").write('o1\t2026-01-01T00:00:00Z\toperation\t"accept it"\th\n')
said = refused(lambda: board_model.plan_accept(tmp, "h", 6, "o1"))
check("ONE_REVIEW_SAFETY_BREAK" in said and "accepted" not in open(os.path.join(red, "plan-h.json")).read(), "a safety break is never accepted away: " + said[:110])
check(refused(lambda: board_model.plan_accept(tmp, "h", 3, "o1")) == "", "a break with no safety class can still be accepted")


# ---- review fixes ----
sh("switch", "-q", "main")
sh("reset", "-q", "--hard")
sh("update-ref", "refs/remotes/origin/main", "main")
for name in os.listdir(runs):
    os.remove(os.path.join(runs, name))


def one(slug, **more):
    record(slug, **more)
    return slug


# a permanent stop holds pr and merge too, and no writer saves a stopped goal as done
one("p1")
decisions.stop(runs, "p1", "a done line needs the part", "t")
held = outcomes.blockers(tmp, runs, rec("p1"), "origin/main", "HEAD")
check(any("stopped for good" in x for x in held), "R1 a stopped goal never becomes a pull request or merges: %s" % held)
check("ONE_REVIEW_STOPPED" in refused(lambda: decisions.hold(runs, dict(rec("p1"), status="done"))), "R1 and it is never saved as done")
merge_py = os.path.join(root, "skills", "workflow-release", "scripts", "merge.py")
done_state = dict(status="done", step="release", pr="https://example.invalid/pull/9", flow={x: "done" for x in ("idea", "plan", "review", "qa", "ship")})
one("p2", **done_state)
put(".loop/config.json", json.dumps({"base": "main", "one_review": True, "auto_merge": True}))
lock = os.path.join(tmp, ".git", "loop", "merge.lock")
open(lock, "w").write("%d\n" % os.getpid())
merging = subprocess.Popen([sys.executable, merge_py, "p2"], cwd=tmp, env=dict(os.environ), stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
try:
    merging.wait(timeout=5)
except subprocess.TimeoutExpired:
    pass
decisions.stop(runs, "p2", "reverted while the merge waited", "t")
json.dump(dict(rec("p2"), status="stopped"), open(os.path.join(runs, "p2.json"), "w"))
os.remove(lock)
out, err = merging.communicate(timeout=60)
check("ONE_REVIEW_STOPPED" in out + err and rec("p2")["status"] == "stopped", "R2 merge reads the record again once it holds the lock: %s" % (out + err).strip()[-170:])
sh("checkout", "-q", "--", ".loop/config.json")

# closing by stop records the stop before anything else, and a cut-off revert is finished by running it again
one("p4")
outcomes.cmd_decide  # noqa: B018
decisions.add(runs, "p4", "finding", key="k", classes=["money"], files=[], question="q", source="stop", head=sh("rev-parse", "HEAD"))
real_add = decisions.add


def cut(r, slug, kind, **data):
    if kind == "close":
        raise KeyboardInterrupt
    return real_add(r, slug, kind, **data)


decisions.add = cut
try:
    outcomes.close(tmp, runs, rec("p4"), 2, "stop", "why", [], "origin/main", "operation")
except KeyboardInterrupt:
    pass
decisions.add = real_add
check(decisions.stopped(decisions.entries(runs, "p4")) != "", "R4 a close by stop that is cut off has already stopped the goal")
one("p5")
dlf.settle(tmp, runs, "p5", "choice", "c1", "pick the shorter name", "w", "take it")
d5 = [e["n"] for e in decisions.entries(runs, "p5") if e["kind"] == "decision"][0]
decisions.add(runs, "p5", "revert", decision=d5, effect="stop", files=[], by="operation")
reverts.revert(tmp, runs, rec("p5"), d5, "operation", "origin/main")
check(decisions.stopped(decisions.entries(runs, "p5")) != "" and rec("p5")["status"] == "stopped", "R5 a revert cut off before its stop stops the goal when run again")
one("p6", status="done", release="merged")
diff_ = "diff --git a/dev/toy/test-a.sh b/dev/toy/test-a.sh\n--- a/dev/toy/test-a.sh\n+++ b/dev/toy/test-a.sh\n@@ -1 +1 @@\n-check two\n"
dlf.settle(tmp, runs, "p6", "test", "t1", "a test failed", "w", "update the test", diff=diff_)
d6 = [e["n"] for e in decisions.entries(runs, "p6") if e["kind"] == "decision"][0]
decisions.add(runs, "p6", "revert", decision=d6, effect="after-merge", files=["dev/toy/test-a.sh"], by="operation")
reverts.revert(tmp, runs, rec("p6"), d6, "operation", "origin/main")
check([(h["slug"], h["decision"]) for h in reverts.holds(tmp) if h["slug"] == "p6"] == [("p6", d6)], "R6 and an after-merge revert cut off before its hold adds it")

# a finding that is open again can be closed again
one("p3")
decisions.add(runs, "p3", "finding", key="k3", classes=["money"], files=["r3.txt"], question="q", source="pr diff", head=sh("rev-parse", "HEAD"))
n3 = [e["n"] for e in decisions.entries(runs, "p3") if e["kind"] == "finding"][0]
decisions.add(runs, "p3", "close", finding=n3, how="drop", why="w", files=["r3.txt"], by="operation")
commit("r3.txt", "changed after the close %s\n" % os.getpid())
check(any("open again" in x for x in outcomes.blockers(tmp, runs, rec("p3"), "origin/main", "HEAD")), "R3 setup: the dropped finding opens again")
got3 = refused(lambda: outcomes.close(tmp, runs, rec("p3"), n3, "stop", "why", [], "origin/main", "operation"))
check(got3 == "", "R3 a reopened finding can be closed: %s" % got3)

# state-matrix cells that must refuse or stop (the review's untested cells): none lets a goal through
one("c1")
decisions.add(runs, "c1", "finding", key="kc1", classes=["money"], files=["c1.txt"], question="q", source="pr diff", head=sh("rev-parse", "HEAD"))
c1n = [e["n"] for e in decisions.entries(runs, "c1") if e["kind"] == "finding"][0]
check("ONE_REVIEW_CLOSE" in refused(lambda: outcomes.close(tmp, runs, rec("c1"), c1n, "not-taken", "why", [], "origin/main", "operation"))
      and outcomes.findings(decisions.entries(runs, "c1"))[0], "CELL pr-diff x not-taken is refused and the finding stays open")
refused(lambda: outcomes.close(tmp, runs, rec("c1"), c1n, "stop", "why", [], "origin/main", "operation"))
check(decisions.stopped(decisions.entries(runs, "c1")) != "" and rec("c1")["status"] == "stopped", "CELL pr-diff x stop closes it and stops the goal")
one("c2")
dlf.settle(tmp, runs, "c2", "choice", "c2", "pick the shorter name", "w", "take it")
c2n = [e["n"] for e in decisions.entries(runs, "c2") if e["kind"] == "decision"][0]
reverts.revert(tmp, runs, rec("c2"), c2n, "operation", "origin/main")
for flag in ("met", "cannot"):
    got = refused(lambda: reverts.revert(tmp, runs, rec("c2"), c2n, "operation", "origin/main", **{flag: "words"}))
    check("ONE_REVIEW_REVERT" in got, "CELL stop-decision x %s is refused: %s" % (flag, got[:90]))
one("c3")
decisions.add(runs, "c3", "decision", key="kc3", stop="pr", question="q", taken="t", safety=["money"], inside=[1], files=["dev/toy/test-a.sh"])
c3n = [e["n"] for e in decisions.entries(runs, "c3") if e["kind"] == "decision"][0]
reverts.revert(tmp, runs, rec("c3"), c3n, "operation", "origin/main")
reverts.revert(tmp, runs, rec("c3"), c3n, "operation", "origin/main", cannot="cannot be met")
check(decisions.stopped(decisions.entries(runs, "c3")) != "" and rec("c3")["status"] == "stopped", "CELL files-decision x cannot stops the goal for good")

# reverts.py: git/gh settings only on its own subprocess calls, and an older hold row has no removal_done
probe = subprocess.run([sys.executable, "-c", "import sys, os; sys.path.insert(0, %r); import reverts; print(os.environ.get('GIT_EDITOR', 'unset'))"
                        % os.path.join(root, "skills", "workflow-delivery", "scripts")], capture_output=True, text=True, env={k: v for k, v in os.environ.items() if k != "GIT_EDITOR"})
check(probe.stdout.strip() == "unset", "R14 importing reverts sets no process-wide git setting: %r %s" % (probe.stdout.strip(), probe.stderr.strip()[-80:]))
add_hold = reverts.add_hold
old_row = {"op": "hold", "slug": "old1", "decision": 7, "files": ["dev/toy/test-a.sh"], "classes": [], "removal_goal": "undo-old1-7"}
reverts.add_hold(tmp, old_row)
queued = []


class FakeG:
    fit = type("F", (), {"cmd_queue": staticmethod(lambda g, args: queued.append(args.done))})
    root = staticmethod(lambda: tmp)


try:
    reverts.queue_removal(FakeG(), "old1", 7)
    got14 = ""
except KeyError as err:
    got14 = "KeyError %s" % err
check(got14 == "" and queued and queued[0], "R14 a hold row with no removal_done queues its removal: %s" % got14)

# a hold is cleared only by a later commit that takes the shipped change out
commit("other.txt", "x%s\n" % d6)
check("ONE_REVIEW_HOLD" in refused(lambda: reverts.clear_hold(tmp, "p6", d6, sh("log", "--format=%H", "-1", "--", "dev/toy/test-a.sh"), "operation")),
      "R7 the commit that shipped the part doesn't clear its hold")
commit("dev/toy/test-a.sh", "check one\ncheck two\nout %s\n" % d6)
check(refused(lambda: reverts.clear_hold(tmp, "p6", d6, sh("rev-parse", "HEAD"), "operation")) == "", "R7 a later commit that changes it does")

# a removal goal's approval: only the goal the revert queued, once, while its hold is pending
import start_review  # noqa: E402
import hashlib  # noqa: E402
one("p8", status="done", release="merged")
dlf.settle(tmp, runs, "p8", "test", "t1", "a test failed", "w", "update the test", diff=diff_)
d8 = [e["n"] for e in decisions.entries(runs, "p8") if e["kind"] == "decision"][0]
reverts.revert(tmp, runs, rec("p8"), d8, "operation", "origin/main")
row = [h for h in reverts.holds(tmp) if h["slug"] == "p8"][0]
name = row["removal_goal"]
good = hashlib.sha256(("1. " + row.get("removal_done", "?")).encode()).hexdigest()
check("start_answer" not in start_review.mark(runs, name, "t", done_sha="0" * 64), "R8 another goal under that name gets no approval")
check(start_review.mark(runs, name + "x", "t", done_sha=good).get("start_answer") is None, "R8 nor another name")
check(start_review.mark(runs, name, "t", done_sha=good).get("start_answer", {}).get("verdict") == "approve", "R8 the queued goal does")
os.remove(os.path.join(runs, name + ".decisions.jsonl"))
commit("dev/toy/test-a.sh", "check one\ncheck two\nremoved %s\n" % d8)
reverts.clear_hold(tmp, "p8", d8, sh("rev-parse", "HEAD"), "operation")
check("start_answer" not in start_review.mark(runs, name, "t", done_sha=good), "R8 and not after the hold is cleared")

# an approved file names one file; only an approved folder covers what is under it
st = {"start_answer": {"verdict": "approve", "items": [{"n": 1, "class": "money", "files": ["a/new"], "approved": True},
                                                        {"n": 2, "class": "money", "files": ["skills/x/scripts/sub/"], "approved": True}]}}
check(outcomes.covering(st, "money", ["a/new"]) and not outcomes.covering(st, "money", ["a/new/deep.py"]) and outcomes.covering(st, "money", ["skills/x/scripts/sub/f.py"]),
      "R9 an approved file doesn't cover a folder of that name")

# a one-review goal's own wait is answered by operation, and a safety question stays a finding
one("p10", status="waiting", waiting={"ask": "may I delete the old release", "words": ["go on p10"]})
got = tool("worker", "answer", "p10")
check("a worker can't" in got and rec("p10")["status"] == "waiting", "R10 a worker doesn't answer its own one-review wait: %s" % got.strip()[:110])
tool("operation", "answer", "p10")
still = [e for e in decisions.entries(runs, "p10") if e["kind"] == "finding"]
check(rec("p10")["status"] == "running" and still and still[-1]["classes"] == ["deleting what cannot be restored"]
      and any("finding" in x for x in outcomes.blockers(tmp, runs, rec("p10"), "origin/main", "HEAD")),
      "R10 answering a safety wait waives nothing: a finding holds pr and merge: %s" % still[-1:])

# a revert asks GitHub whether the pull request merged (a squash merge leaves no ancestor behind)
fake = os.path.join(home, "bin")
os.makedirs(fake, exist_ok=True)
open(os.path.join(fake, "gh"), "w").write('#!/bin/sh\n[ "$TOY_GH" = fail ] && exit 1\necho \'{"state": "MERGED"}\'\n')
os.chmod(os.path.join(fake, "gh"), 0o755)
path_was = os.environ["PATH"]
os.environ["PATH"] = fake + os.pathsep + path_was
one("p11", status="done", pr="https://example.invalid/pull/11")
dlf.settle(tmp, runs, "p11", "test", "t1", "a test failed", "w", "update the test", diff=diff_)
d11 = [e["n"] for e in decisions.entries(runs, "p11") if e["kind"] == "decision"][0]
os.environ["TOY_GH"] = "fail"
check("ONE_REVIEW_REVERT" in refused(lambda: reverts.revert(tmp, runs, rec("p11"), d11, "operation", "origin/main")), "R11 when it can't tell, the revert refuses")
os.environ.pop("TOY_GH")
reverts.revert(tmp, runs, rec("p11"), d11, "operation", "origin/main")
check([e["effect"] for e in decisions.entries(runs, "p11") if e["kind"] == "revert"] == ["after-merge"], "R11 a squash-merged pull request is treated as merged")
os.environ["PATH"] = path_was

# E15: the regression levels gate reads owner records too, and a start answer covers no lowering there
sys.path.append(os.path.join(root, "skills", "workflow-regression", "scripts"))
import levels_gate  # noqa: E402
kept_words = os.path.join(tmp, ".git", "loop", "owner-words.tsv")
was = open(kept_words).read() if os.path.exists(kept_words) else None
open(kept_words, "w").write('o1\t2026-01-01T00:00:00Z\toperation\t"approve start ask abc123"\task,some-row\no2\t2026-01-01T00:00:00Z\toperation\t"lower that row"\task,some-row\n')
got = levels_gate.ledger(tmp)
check(sorted(got) == ["o2"] and not levels_gate.covers_subject(tmp, got, "o1", "some-row") and levels_gate.covers_subject(tmp, got, "o2", "some-row"),
      "E15 a start answer covers no level lowering: %s" % sorted(got))
os.remove(kept_words) if was is None else open(kept_words, "w").write(was)

# full auto, a one-review goal and a safety question: no action at all (TD2246)
sys.path.append(os.path.join(root, "skills", "workflow-monitoring", "scripts"))
import auto  # noqa: E402
for name in os.listdir(runs):
    os.remove(os.path.join(runs, name))
put(".loop/config.json", json.dumps({"base": "main", "one_review": True, "full_auto": True}))
open(os.path.join(tmp, ".git", "loop", "owner-words.tsv"), "w").write('o1\t2026-01-01T00:00:00Z\toperation\t"full auto"\tfull-auto-rule\n')
one("fa", status="waiting", waiting={"ask": "may I delete the old release branch to free space?", "words": ["yes, delete it", "keep it"],
                                      "recommend": "yes, delete it"})
sent = []
real_run = auto.subprocess.run


def spy(cmd, *a, **k):
    if any(str(x).endswith("operate.py") for x in cmd):
        sent.append(cmd)
        return subprocess.CompletedProcess(cmd, 0, "", "")
    return real_run(cmd, *a, **k)


auto.subprocess.run = spy
lines = auto.decide_all(tmp)
again = auto.decide_all(tmp)
auto.subprocess.run = real_run
state = rec("fa")
check(not sent and state["status"] == "waiting" and any(" fa | WAITS " in x and "safety class" in x for x in lines) and not [x for x in lines + again if " AUTO " in x]
      and not os.path.exists(os.path.join(tmp, ".git", "loop", "inbox", "fa.txt")),
      "FULL-AUTO a safety question on a one-review goal leads to no action: nothing sent, it stays waiting (%s)" % lines)
import review_view  # noqa: E402
check(not review_view.owners(tmp, state), "FULL-AUTO and it is held by the operation")
one("fb", status="waiting", waiting={"ask": "which of the two names reads better?", "words": ["the first", "the second"], "recommend": "the first"})
would = auto.decide_all(tmp, dry=True)
check(any(x.startswith("WOULD ANSWER fb") for x in would), "FULL-AUTO control: full auto is on and would answer an ordinary question: %s" % would)
sh("checkout", "-q", "--", ".loop/config.json")
print("ALL PASS" if not failed else "%d FAILED" % len(failed))
sys.exit(1 if failed else 0)
