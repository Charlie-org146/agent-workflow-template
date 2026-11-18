#!/usr/bin/env python3
# windows: ok
# reads: skills/workflow-health/scripts/file.py skills/workflow-health/scripts/judge.py skills/workflow-health/scripts/issues.py
"""HLT-9, issue 4543: a judge finding's key comes from its rule and its subject, not from its wording, so a later round updates
the open issue instead of re-filing it. Runs the real planner (file.plan) on fixture findings and fixture issues: no model, no
network.

1. Two rounds of the judge's savings with reworded advice on one file file one issue; a different file files a second.
2. The same for review findings: the feature, the kind and the first citation name the issue, not the whole citation set.
3. An open issue filed under an old wording-hash key is matched by rule and subject and updated under the new key, never
   re-filed or closed as gone; one closed by the owner stays closed; a different subject still files."""
import os
import sys
import tempfile

root = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
sys.path.insert(0, os.path.join(root, "skills", "workflow-health", "scripts"))
os.environ.pop("LOOP_ROLE", None)
import file as F  # noqa: E402
import judge  # noqa: E402

failed = []


def check(ok, text):
    print(("PASS: " if ok else "FAIL: ") + text)
    if not ok:
        failed.append(text)


def acts(rows, issues, group, tmp):
    return [a for a in F.plan([], issues, (group,), extra=rows, judged=True, root=tmp) if a["kind"] != "same"]


def filed(act, number):
    return {act["key"]: {"number": number, "state": "open", "body": act["body"], "labels": [act["tag"], act["feature"]], "evidence": act["evidence"]}}


with tempfile.TemporaryDirectory() as tmp:
    # 1. savings: the same file, reworded
    first = F.saves_rows([("25%", "land lane is 974 s over budget because test-goal-adopt.sh reruns x3 at 26 s", "Run each toy once through the tree-once cache")])
    second = F.saves_rows([("30%", "the toy test-goal-adopt.sh costs about 80 s a lane in three rows", "Cache its output and let the rows grep it")])
    other = F.saves_rows([("5%", "test-docs-link.sh runs three times at 37 s", "Run it once")])
    check(first[0]["rule"] == second[0]["rule"] != other[0]["rule"], "two savings about test-goal-adopt.sh share a rule; test-docs-link.sh has its own")
    got = acts(first, {}, "performance", tmp)
    check([a["kind"] for a in got] == ["open"], "round one files one issue")
    issues = filed(got[0], 7)
    got = acts(second, issues, "performance", tmp)
    check([a["kind"] for a in got] == ["update"] and got[0]["number"] == "7", "round two, reworded, updates #7 and files nothing")
    check([a["kind"] for a in acts(first + other, issues, "performance", tmp)] == ["open"], "control: a finding about another file files a new issue")

    # 2. review findings: the first citation names the subject, the other citations and the wording may change
    one = judge.as_rows([{"feature": "Delivery", "kind": "weak-test", "detail": "depth rows link DEL-1", "fix": "relink", "evidence": "DEL-6, DEL-1, depth-markers", "angle": "auditor"}])
    two = judge.as_rows([{"feature": "Delivery", "kind": "weak-test", "detail": "DEL-6 shows no test", "fix": "move the rows", "evidence": "DEL-6:12, depth-recorded", "angle": "auditor"}])
    diff = judge.as_rows([{"feature": "Delivery", "kind": "weak-test", "detail": "x", "fix": "y", "evidence": "DEL-9, depth-markers", "angle": "auditor"}])
    check(one[0]["subject"] == two[0]["subject"] != diff[0]["subject"], "review findings with one first citation share a subject; another first citation has its own")
    got = acts(one, {}, "review", tmp)
    issues = filed(got[0], 9)
    got = acts(two, issues, "review", tmp)
    check([a["kind"] for a in got] == ["update"] and got[0]["number"] == "9", "a later round with another wording and citation set updates #9")
    check([a["kind"] for a in acts(diff, issues, "review", tmp)] == ["open"], "control: a finding on another citation files a new issue")

    # 3. old keys
    old_body = ("<!-- loop-health performance:judge:saves-5726bdc4 evidence=e385f7dc placed= -->%s%sWARN performance judge saves-5726bdc4: 25%% saving: land lane is 974 s over "
                "its 900 s budget (test-goal-adopt.sh x3 at 26 s, test-docs-link.sh x3) -> fix: Run each toy once.%s%sGroup: Performance. Evidence: judge%s" % ("\n\n", "", "\n\n", "", "\n"))
    old = {"performance:judge:saves-5726bdc4": {"number": 4326, "state": "open", "body": old_body, "labels": ["health:performance"], "evidence": "e385f7dc"}}
    got = acts(first, old, "performance", tmp)
    check([(a["kind"], a["number"]) for a in got] == [("update", "4326")], "an open issue under an old wording-hash key is matched by rule and subject and updated (#4326)")
    plan = F.plan([], old, ("performance",), extra=first, judged=True, root=tmp)
    check(not [a for a in plan if a["kind"] == "close"], "the old-key issue is not closed as no longer found")
    got = acts(other, old, "performance", tmp)
    check(any(a["kind"] == "open" for a in got) and not any(a["kind"] == "update" for a in got), "control: another subject is not matched to it and files a new issue")
    closed = {"performance:judge:saves-5726bdc4": dict(old["performance:judge:saves-5726bdc4"], state="closed", labels=["health:performance", "health:closed"])}
    check([a for a in F.plan([], closed, ("performance",), extra=first, judged=True, root=tmp) if a["kind"] in ("open", "reopen")] == [],
          "an old-key issue the owner closed stays closed: nothing is re-filed or reopened")
    old_review = {"review:Delivery-40f5e9:weak-test": {"number": 405, "state": "open", "labels": ["health:review-weak-test"],
                  "body": "<!-- loop-health review:Delivery-40f5e9:weak-test evidence=a13c85c2 -->\n\nWARN review Delivery-40f5e9 weak-test: x -> fix: y\n\nGroup: review. Evidence: DEL-6, DEL-1, depth-condensed-refused\n"}}
    got = acts(two, old_review, "review", tmp)
    check([(a["kind"], a["number"]) for a in got] == [("update", "405")], "an old review key (feature-hash:kind) is matched by feature, kind and first citation")

sys.exit(1 if failed else 0)
