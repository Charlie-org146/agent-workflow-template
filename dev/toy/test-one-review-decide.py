#!/usr/bin/env python3
# windows: ok
# reads: skills/workflow-delivery/scripts/decisions.py skills/workflow-delivery/scripts/goal.py skills/workflow-monitoring/scripts/graph.py
"""One review (DLF-1.3), decisions after the start: the ledger is a file of its own that is only added to, writers of the
run record cannot lose an entry, a missing or torn ledger refuses, and a permanent stop holds at every change into
queued or running. Throwaway folders with their own home; no network."""
import json
import os
import subprocess
import sys
import tempfile

root = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
delivery = os.path.join(root, "skills", "workflow-delivery", "scripts")
monitoring = os.path.join(root, "skills", "workflow-monitoring", "scripts")
sys.path[:0] = [delivery, monitoring]
home = tempfile.mkdtemp()
os.environ.update(HOME=home, USERPROFILE=home, GIT_CONFIG_NOSYSTEM="1")
tmp = os.path.join(home, "repo")
runs = os.path.join(tmp, ".git", "loop", "runs")
subprocess.run(["git", "init", "-q", tmp], check=True)
subprocess.run(["git", "-C", tmp, "-c", "user.name=t", "-c", "user.email=t@t", "commit", "-q", "--allow-empty", "-m", "base"], check=True)
os.makedirs(runs)
os.makedirs(os.path.join(tmp, ".loop", "goals"))

failed = []


def check(ok, text):
    print(("PASS: " if ok else "FAIL: ") + text)
    if not ok:
        failed.append(text)


try:
    import decisions
except ImportError as error:
    print("FAIL: decisions.py is missing: %s" % error)
    sys.exit(1)


def record(slug, **more):
    state = dict({"slug": slug, "goal": slug, "status": "running", "step": "build", "tries": 0, "flow": {}, "branch": "loop/" + slug,
                  "worktree": tmp, "touches": [], "log": []}, **more)
    json.dump(state, open(os.path.join(runs, slug + ".json"), "w"))
    return state


def refused(call):
    try:
        call()
    except SystemExit as stop:
        return str(stop.code)
    return ""


# the ledger: its own file, numbered, only added to
record("a", one_review={"at": "t"})
decisions.create(runs, "a", by="test")
first = decisions.add(runs, "a", "decision", question="q1", taken="x")
second = decisions.add(runs, "a", "decision", question="q2", taken="y")
check([first, second] == [2, 3] and [e["n"] for e in decisions.entries(runs, "a")] == [1, 2, 3], "entries are numbered in order")
check(refused(lambda: decisions.create(runs, "a", by="test")) != "", "a ledger is made once and never made again over another")

# many writers at once lose nothing and share no number
child = ("import sys; sys.path.insert(0, %r); import decisions\n"
         "for i in range(20): decisions.add(%r, 'a', 'decision', question='%%s-%%d' %% (sys.argv[1], i), taken='x')" % (delivery, runs))
procs = [subprocess.Popen([sys.executable, "-c", child, str(k)]) for k in range(4)]
codes = [p.wait() for p in procs]
got = [e["n"] for e in decisions.entries(runs, "a")]
check(codes == [0] * 4 and got == list(range(1, 84)), "80 concurrent entries are all kept with unique numbers (%d entries)" % len(got))

# a writer of the whole run record cannot lose an entry
import goal  # noqa: E402
os.chdir(tmp)
stale = goal.load("a")
decisions.add(runs, "a", "decision", question="added while another writer holds the record", taken="x")
goal.save(stale, "a stale writer saves")
check(len(decisions.entries(runs, "a")) == 84, "a stale whole-record save keeps every entry")

# a missing or torn ledger refuses
record("gone", one_review={"at": "t"})
said = refused(lambda: decisions.require(runs, {"slug": "gone", "one_review": {"at": "t"}}))
check("decisions" in said, "a marked goal with no ledger is refused: %s" % said[:80])
decisions.create(runs, "torn", by="test")
open(decisions.ledger(runs, "torn"), "a").write('{"n": 2, "kind"')
check(refused(lambda: decisions.entries(runs, "torn")) != "", "a torn ledger is refused, not read as shorter")
check(refused(lambda: decisions.require(runs, {"slug": "plain"})) == "", "an unmarked goal needs no ledger")

# a permanent stop holds at every change into queued or running
record("s", one_review={"at": "t"}, status="stopped")
decisions.create(runs, "s", by="test")
decisions.stop(runs, "s", "a done line needs the part", by="operation")
for status in ("queued", "running", "waiting"):
    state = goal.load("s")
    state["status"] = status
    said = refused(lambda: goal.save(state, "set " + status))
    check("stopped for good" in said and json.load(open(os.path.join(runs, "s.json")))["status"] == "stopped",
          "goal.py cannot set a stopped goal %s: %s" % (status, said[:70]))
import sessions  # noqa: E402
import watch  # noqa: E402
import worker  # noqa: E402
import mend  # noqa: E402
sys.path.append(os.path.join(root, "skills", "workflow-release", "scripts"))
import release  # noqa: E402
for module in (sessions, watch, worker, mend, release):
    state = dict(json.load(open(os.path.join(runs, "s.json"))), status="queued" if module is watch else "running")
    said = refused(lambda m=module, s=state: m.save(s, "revive"))
    check("stopped for good" in said and json.load(open(os.path.join(runs, "s.json")))["status"] == "stopped",
          "%s.py cannot revive it: %s" % (module.__name__, said[:60]))
state = goal.load("s")
state["status"] = "retired"
check(refused(lambda: goal.save(state, "retired")) == "", "it can still be retired")

# the stop also holds when a writer has lost the mark from the record
lost = {k: v for k, v in json.load(open(os.path.join(runs, "s.json"))).items() if k != "one_review"}
lost["status"] = "running"
check("stopped for good" in refused(lambda: goal.save(lost, "revive")), "a record without the mark is still held by its ledger")

# a handover carries the ledger and the pre-flight and review files
os.makedirs(os.path.join(tmp, ".git", "loop", "redteam"), exist_ok=True)
open(os.path.join(runs, "a.extra.json"), "w").write('{"touches": ["x"]}')
open(os.path.join(tmp, ".git", "loop", "redteam", "plan-a.json"), "w").write('{"breaks": []}')
bundle = decisions.pack(runs, json.load(open(os.path.join(runs, "a.json"))))
there = os.path.join(home, "other", "loop", "runs")
decisions.unpack(there, {"slug": "a", "one_review": {"at": "t"}}, bundle)
check(len(decisions.entries(there, "a")) == 84 and os.path.exists(os.path.join(there, "a.extra.json"))
      and os.path.exists(os.path.join(there, "..", "redteam", "plan-a.json")), "a handover carries the decisions, pre-flight and review files")
said = refused(lambda: decisions.unpack(os.path.join(home, "third", "loop", "runs"), {"slug": "a", "one_review": {"at": "t"}}, {}))
check("carries no decisions" in said, "a marked goal handed over without its ledger is refused: %s" % said[:80])
open(os.path.join(there, "a.decisions.jsonl"), "a").write('{"n": 85, "kind": "decision"}\n')
check("don't continue" in refused(lambda: decisions.unpack(there, {"slug": "a", "one_review": {"at": "t"}}, bundle)),
      "an older copy never replaces a longer ledger")

# the safety scan: every matching class, from a stop's text and from a diff (E7, E10, CEO B1)
import safety_scan as sc  # noqa: E402
S = ("deleting what cannot be restored", "money", "security and sandbox settings", "private data", "steward merges",
     "a change to what a feature promises", "a test loosened or deleted")
for want, texts in ((S[0], ("delete the old release", "purge the backup folder", "this wipes the database", "run rm -rf on the worktree",
                            "force-push over the branch history", "the remote branch gets removed", "erase last week's run records")),
                    (S[1], ("buy a paid plan", "charge the card on file", "it costs $20 a month", "renew the subscription",
                            "start a purchase for more credits", "pay the invoice")),
                    (S[4], ("steward merge the PR", "admin-merge it", "merge the pull request as steward", "bypass the required check and merge",
                            "put it in the merge queue", "turn on auto-merge for it")),
                    (S[2], ("widen the sandbox", "edit settings.json", "switch to bypass permissions mode", "add the API key")),
                    (S[6], ("remove the failing test", "disable two assertions", "mark it xfail", "comment out the check"))):
    missed = [t for t in texts if want not in sc.text_classes(t)]
    check(not missed, "text scan finds %s in varied wording (missed %d)" % (want, len(missed)))
both = sc.text_classes("delete the failing test and pay the invoice")
check({S[1], S[6]} <= set(both), "every matching class is reported: %s" % both)
check(sc.text_classes("rename a local variable") == [], "plain wording matches no class")
check(sc.text_classes("rename a local variable", label=S[1]) == [S[1]], "a label raises the class")
got = sc.action("rename a local variable")
check(got == {"state": "unknown", "classes": []}, "an action with no match is not cleared: it is held under operation (%s)" % got)
check(sc.action("pay the invoice")["state"] == "safety", "a matching action is a safety stop")


def diff(path, removed=(), added=(), gone=False):
    return "diff --git a/%s b/%s\n%s--- a/%s\n+++ %s\n@@ -1 +1 @@\n%s" % (
        path, path, "deleted file mode 100644\n" if gone else "", path, "/dev/null" if gone else "b/" + path,
        "".join("-%s\n" % x for x in removed) + "".join("+%s\n" % x for x in added))


def found(d, units=()):
    return sc.diff_classes(d, units)


check(S[6] in found(diff("dev/toy/test-a.sh", removed=["check one"])), "a removed test line is a loosened test")
check(S[6] in found(diff("tests/a_test.py", removed=["x"], gone=True)), "a deleted test file is found")
check(S[6] in found(diff(".loop/regression.tsv", removed=["row\tgiven"])), "a removed regression row is found")
check(S[6] not in found(diff("dev/toy/test-a.sh", added=["check two"])), "an added test line is not")
for path in (".claude/settings.json", ".loop/config.json", ".github/workflows/ci.yml", ".loop/permissions.tsv"):
    check(S[2] in found(diff(path, added=["x"])), "a settings path is found: %s" % path)
check(S[3] in found(diff("a.py", added=["key = '" + "AKIA" + "A" * 16 + "'"])), "a secret-shaped added line is private data")
check(S[0] in found(diff("tools/x.sh", added=['rm -rf "$HOME/backups"'])), "an added destructive command is found")
check(S[4] in found(diff("tools/x.py", added=['run(["gh", "pr", "merge", "--admin"])'])), "an added admin merge is found")
check(found(diff("docs/wiki/Page.md", added=["plain words"])) == {}, "a wiki path alone is no promise change")
check(found(diff("docs/wiki/Page.md", added=["x"]), units=[("docs/wiki/Page.md", "AB-1")]) == {S[5]: ["docs/wiki/Page.md"]},
      "a changed Reviewed unit is a promise change")
base = "- AB-1: **Reviewed 2026-11-24** One <!-- reviewed 2069271e -->\n  - sub line [AB-1]\n\n- AB-2: **Unreviewed** Two\n"
check(sc.reviewed_units(base) == {"AB-1": "One\n  - sub line [AB-1]"}, "a Reviewed unit, in the pages' own form, holds its heading and sub-bullets: %s" % sc.reviewed_units(base))
real = open(os.path.join(root, "docs", "wiki", "Deliver-first.md"), encoding="utf-8").read()
marked = len(__import__("re").findall(r"^- [A-Z]{2,5}-\d+: \*\*Reviewed", real, __import__("re").M))
check(marked and len(sc.reviewed_units(real)) == marked, "every Reviewed requirement of a real page is read (%d of %d)" % (len(sc.reviewed_units(real)), marked))
check(sc.units(base.replace("**Reviewed 2026-11-24**", "**Unreviewed**").replace(" <!-- reviewed 2069271e -->", ""))["AB-1"] == "One\n  - sub line [AB-1]",
      "losing the mark alone doesn't change the unit's text")
after = base.replace("  - sub line [AB-1]\n\n", "  - sub line [AB-1]\n\n  - a slipped sentence [AB-1]\n\n")
check(sc.changed_units(base, after) == [sc.OUTSIDE], "a requirement line added outside its unit is found: %s" % sc.changed_units(base, after))
notes = base.replace("  - sub line [AB-1]\n\n", "  - sub line [AB-1]\n\n  - Reference: a tool\n\n")
check(sc.changed_units(base, notes) == [], "an untagged note outside a unit is not")
check(sc.changed_units(after, after) == [], "a tagged line that was already there is not new")

# the diff is read as git sees it, with names that need quoting, and an unreadable one refuses
repo = os.path.join(home, "scanrepo")
subprocess.run(["git", "init", "-q", repo], check=True)


def g(*a):
    return subprocess.run(["git", "-C", repo, "-c", "user.name=t", "-c", "user.email=t@t"] + list(a), check=True, capture_output=True, text=True).stdout.strip()


os.makedirs(os.path.join(repo, "docs", "wiki"))
open(os.path.join(repo, "docs", "wiki", "P.md"), "w").write(base)
g("add", "-A"); g("commit", "-qm", "a")
first = g("rev-parse", "HEAD")
open(os.path.join(repo, "docs", "wiki", "P.md"), "w").write(base.replace("sub line", "other line").replace("**Reviewed 2026-11-24**", "**Unreviewed**"))
open(os.path.join(repo, "odd name \u00e9.bin"), "wb").write(b"\xff\xfe\x00data")
g("add", "-A"); g("commit", "-qm", "b")
g("config", "diff.external", "false")
text, units = sc.read_diff(repo, first, "HEAD")
check("other line" in text and units == [("docs/wiki/P.md", "AB-1")], "the diff is read with external tools off: %s" % (units,))
check("ONE_REVIEW_DIFF" in refused(lambda: sc.read_diff(repo, "0" * 40, "HEAD")), "an unreadable diff refuses")

# an unmarked goal saves as today
record("u", status="stopped")
state = goal.load("u")
state["status"] = "running"
check(refused(lambda: goal.save(state, "resumed")) == "", "an unmarked goal is not held")

print("ALL PASS" if not failed else "%d FAILED" % len(failed))
sys.exit(1 if failed else 0)
