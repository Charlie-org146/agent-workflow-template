#!/usr/bin/env python3
# windows: ok
# reads: skills/workflow-monitoring/scripts/auto.py skills/workflow-docs/scripts/deployments.py skills/workflow-health/scripts/controls.py
"""MON-11 (#4831, o118): full auto answers every recommended question unless it is a safety class, and that is enforced.

Drives auto.decide_all in a throwaway git repo (no model, no network): the answers, the safety waits, a negative control that
removes the safety guard, the standing owner record's reuse rules, and the two health rules over auto.log."""
import json
import os
import subprocess
import sys
import tempfile

root = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
for skill in ("monitoring", "docs", "health"):
    sys.path.insert(0, os.path.join(root, "skills", "workflow-" + skill, "scripts"))
os.environ.pop("LOOP_ROLE", None)
tmp = tempfile.mkdtemp()
os.environ.update(HOME=tmp, USERPROFILE=tmp)
import auto  # noqa: E402
import deployments  # noqa: E402

bad = []


def check(ok, text):
    print(("PASS: " if ok else "FAIL: ") + text)
    if not ok:
        bad.append(text)


def repo(name):
    where = os.path.join(tmp, name)
    os.makedirs(os.path.join(where, ".loop"))
    subprocess.run(["git", "init", "-q", where], check=True)
    with open(os.path.join(where, ".loop", "config.json"), "w") as handle:
        json.dump({"full_auto": True}, handle)
    os.makedirs(os.path.join(where, ".git", "loop", "runs"))
    os.chdir(where)
    return where


def loop(where):
    return os.path.join(where, ".git", "loop")


def ask(where, slug, text, kind="routine", eta=False):
    waiting = {"ask": text, "words": ["yes", "no"], "recommend": "yes", "kind": kind}
    if eta:
        waiting["eta"] = True
    with open(os.path.join(loop(where), "runs", slug + ".json"), "w") as handle:
        json.dump({"slug": slug, "goal": "g", "status": "waiting", "step": "build", "waiting": waiting}, handle)


RULE_ID = "full-auto-rule"


def words(where, text, ids):
    path = os.path.join(loop(where), "owner-words.tsv")
    count = sum(1 for _ in open(path)) if os.path.exists(path) else 0
    with open(path, "a") as handle:
        handle.write("o%d\t2026-11-17T00:00:00Z\toperation\t%s\t%s\n" % (count + 1, json.dumps(text), ids))
    return "o%d" % (count + 1)


def log(where):
    try:
        return open(os.path.join(loop(where), "auto.log")).read()
    except OSError:
        return ""


def answered(where, slug):
    return "| %s | AUTO |" % slug in log(where)


def waits(where, slug):
    return "| %s | WAITS |" % slug in log(where)


# 1. routine, owner (un-review, row cap, budget), no kind: answered with the rule and the revert words; security waits.
w = repo("answers")
rule = words(w, "take every recommendation unless it is a safety question", "full-auto-rule")
cases = {"r1": ("Which helper name should the toy use?", "routine"),
         "o1": ("Un-review the Monitoring page so MON-11 wording can change?", "owner"),
         "o2": ("Raise max_regression_rows from 1200 to 1300?", "owner"),
         "o3": ("Raise the token budget from 3000000 to 4000000 for this goal?", "owner"),
         "o4": ("Raise criteria_max from 18 to 19?", "owner"),
         "u1": ("Use the shorter log line?", ""),
         "s1": ("Allow the worker to read the credential file?", "security")}
for slug, (text, kind) in cases.items():
    ask(w, slug, text, kind)
auto.decide_all(w)
for slug in ("r1", "o1", "o2", "o3", "o4", "u1"):
    check(answered(w, slug), "full auto answers %s with its recommendation: %s" % (slug, cases[slug][0][:40]))
check(waits(w, "s1") and not answered(w, "s1"), "a security question still waits under Needs you")
check(all(" owner rule %s" % rule in line for line in log(w).splitlines() if "| AUTO |" in line) and "| AUTO |" in log(w),
      "every AUTO line carries the standing rule record")
inbox = os.path.join(loop(w), "inbox", "o1.txt")
check(os.path.exists(inbox) and "owner rule %s" % rule in open(inbox).read(), "the worker's answer names the rule record to cite")
check('"slug": "o2", "key"' in open(os.path.join(loop(w), "answers.jsonl")).read() and '"source": "auto"' in open(os.path.join(loop(w), "answers.jsonl")).read(),
      "each auto answer is logged with --source auto")
check(not os.path.exists(os.path.join(loop(w), "inbox", "s1.txt")) or not open(os.path.join(loop(w), "inbox", "s1.txt")).read().strip(),
      "nothing is sent for the waiting security question")

# 2. no standing record: everything waits (fail closed)
w = repo("norule")
ask(w, "n1", "Which helper name should the toy use?")
auto.decide_all(w)
check(waits(w, "n1") and "no standing owner rule" in log(w), "with no standing owner rule recorded, full auto waits")

# 2b. the rule recorded later answers the question that waited for it
words(w, "take every recommendation unless it is a safety question", RULE_ID)
auto.decide_all(w)
check(answered(w, "n1"), "a question that waited for the rule is answered once the rule is recorded")

# 3. every safety class waits, whatever the kind; kinds, the ETA choice and an always-ask goal wait
w = repo("safety")
words(w, "take every recommendation unless it is a safety question", "full-auto-rule")
classes = {"destructive-delete": "Delete the old worktree directory?", "destructive-force": "Force push the branch to main?",
           "destructive-rewrite": "Rewrite history with a rebase and squash?", "money-pay": "Buy more credits with the card on file?",
           "money-billing": "Raise the billing limit for the account?", "security-key": "Print the API key into the log?",
           "security-perm": "Add an allow rule to the permissions list?", "security-sandbox": "Turn the sandbox off for this run?",
           "private-names": "Add the private name to the names list?", "private-mail": "Send the digest to the Dro" "pbox folder?",
           "merge-steward": "Merge the steward's pull request now?",
           "token-rotate": "Rotate the token?", "write-access": "Grant write access to the repo?", "security-word": "Enable the security setting change?",
           "authorization": "Update the authorization header?", "close-pr": "Close PR #12 from another contributor?",
           "reset-branch": "Reset the branch to origin/main?", "unpublish": "Unpublish the package?", "purge": "Purge the cache?",
           "cleanup": "Clean up old worktrees?", "charge": "Charge the card?", "gmail": "Read the user's Gmail?",
           "records": "Store customer records in the db?", "eta-text": "Extend the ETA by 30 minutes?", "merge-pr": "Merge pull request #7 now?"}
for slug, text in classes.items():
    ask(w, slug, text, "owner" if slug.endswith(("delete", "key", "names")) else "routine")
for kind in ("destructive", "money", "security"):
    ask(w, "kind-" + kind, "Which helper name should the toy use?", kind)
ask(w, "eta1", "full-auto-all is past its ETA: ship now, extend once, or defer?", "owner", eta=True)
ask(w, "ask1", "Which helper name should the toy use?", "routine")
words(w, "always ask me about this goal", "always-ask:ask1")
auto.decide_all(w)
for slug, text in classes.items():
    check(waits(w, slug) and not answered(w, slug), "safety class waits: " + slug)
for slug in ("kind-destructive", "kind-money", "kind-security", "eta1", "ask1"):
    check(waits(w, slug) and not answered(w, slug), "waits: " + slug)

# 4. negative control: with the safety guard removed, the same security question is answered
saved = dict(auto.CLASSES)
auto.CLASSES.clear()
control = auto.why_not({"ask": classes["security-key"], "kind": "routine", "recommend": "yes", "words": ["yes", "no"]}, {})
auto.CLASSES.update(saved)
check(control == "", "negative control: without the safety guard a security question is answered")
check(auto.why_not({"ask": classes["security-key"], "kind": "routine", "recommend": "yes", "words": ["yes", "no"]}, {}) != "",
      "negative control: with the guard back it waits again")

# 5. the standing record: reusable to un-review (never to review), and for a budget only when full auto answered that goal
w = repo("reuse")
rid = words(w, "take every recommendation unless it is a safety question", "full-auto-rule")


def git(*args):
    return subprocess.run(["git"] + list(args), capture_output=True, text=True).stdout.strip()


def owner(command, ids):
    class A:
        pass
    a = A()
    a.owner_record, a.ids, a.command = rid, ids, command
    try:
        return deployments.owner_words(a, git)
    except SystemExit as stop:
        return "REFUSED" if "REFUSED" in str(stop) else str(stop)


first, second = owner("unreview", ["Monitoring", "MON-11"]), owner("unreview", ["Guardrails"])
with open(os.path.join(loop(w), "reviews.tsv"), "a") as handle:
    handle.write("2026-11-17T00:00:00Z\tunreview\tMonitoring\trecord %s: x\n" % rid)
third = owner("unreview", ["Health"])
check(first.startswith("record " + rid) and second.startswith("record " + rid) and third.startswith("record " + rid),
      "the standing record un-reviews any page, any number of times")
check(owner("review", ["Monitoring"]) == "REFUSED", "the standing record never stamps a review")


class G:
    def no(self, text):
        raise SystemExit("REFUSED " + text)

    def state_dir(self):
        return os.path.join(loop(w), "runs")


def record(slug, what):
    try:
        return auto.eta_record(G(), rid, slug, what)
    except SystemExit:
        return "REFUSED"


check(record("g1", "raising a budget") == "REFUSED", "a budget raise cites the standing record only after full auto answered that goal")
ask(w, "g1", "Raise the token budget from 3000000 to 4000000 for this goal?", "owner")
auto.decide_all(w)
check(record("g1", "raising a budget") == rid and record("g1", "raising a budget") == rid, "after full auto answered it the budget raise may cite the record again")
check(record("g1", "an ETA change") == "REFUSED", "an ETA move never accepts the standing record")

# 5b. pre-flight: the recommended answer rides the standing record when no item is a safety class
check(record("g9", "the recommended pre-flight answer") == rid and record("g9", "the recommended pre-flight answer") == rid,
      "the recommended pre-flight answer may cite the standing record again and again")
check(record("g1", "a pre-flight answer") == "REFUSED", "a chosen pre-flight answer needs the goal's own record, even after an auto answer")
ask(w, "g2", "Which helper name should the toy use?", "routine")
auto.decide_all(w)
check(record("g2", "raising a budget") == "REFUSED", "a budget raise needs an auto answer about a budget, not any auto answer")
items = {"plan": ("the plan step ends pending and waits for your approval (auto_approve is off)", "approve ahead"),
         "budget": ("its time budget is 240 minutes; held and waiting time may count toward it", "keep"),
         "memory": ("memory is under the floor", "lower min_free_memory_gb to the free memory"),
         "quota": ("the GitHub API quota is 10 requests; pr steps stall at 0", "go on with local steps")}
check(all(auto.why_not({"ask": a, "words": [r], "recommend": r, "kind": "owner"}, {}) == "" for a, r in items.values()),
      "the plan, budget, memory and quota pre-flight items are answered with their recommendation")
check(auto.why_not({"ask": "Merge main into the branch?", "words": ["yes"], "recommend": "yes", "kind": "routine"}, {}) == "",
      "merging main into the goal's branch is routine and answered")
check(auto.why_not({"ask": "the private-name list would refuse: x.py", "words": ["edit the list line"], "recommend": "edit the list line", "kind": "owner"}, {}) != "",
      "the private-name pre-flight item waits for the owner")

# 6. health: an AUTO line that hits a safety class, or carries no rule record, fails; the clean log is clean
with open(os.path.join(loop(w), "auto.log"), "a") as handle:
    handle.write("2026-11-16T00:00:00Z | old | AUTO | which name? | yes | routine, recommended\n")
clean = auto.auto_rows(w)
check(not clean, "health is clean over the log full auto wrote")
with open(os.path.join(loop(w), "auto.log"), "a") as handle:
    handle.write("2026-11-17T00:00:00Z | zz | AUTO | delete the old worktree directory? | yes | routine, recommended\n")
found = {rule for rule, level, text in auto.auto_rows(w) if level == "FAIL"}
check({"auto-safety", "auto-record"} <= found, "health fails an AUTO line with a safety question and no rule record")
import controls  # noqa: E402
names = {c[1] for c in controls.CONTROLS.values()} if isinstance(controls.CONTROLS, dict) else set()
check({"auto-safety", "auto-record"} <= names, "health has auto-safety and auto-record with negative controls")
# 7. private-lines-v1051: the private-data class matches each word it matched before the source was split
pat = auto.CLASSES["private data"]
for t in ["private-name list", "private list", "private data", "private repos", "dro" + "pbox folder", "mail", "gmail", "e-mail",
          "inbox", "smtp", "customer records", "personal record", "private records"]:
    check(bool(pat.search(t)), "private data class matches " + t)
for t in ["rename a variable", "raise the row cap", "update the wiki page"]:
    check(not pat.search(t), "private data class ignores " + t)
sys.exit(1 if bad else 0)
