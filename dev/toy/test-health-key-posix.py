#!/usr/bin/env python3
# windows: ok
# reads: skills/workflow-health/scripts/file.py skills/workflow-health/scripts/issues.py
"""HLT-4 (#4379): a finding's key, evidence and title name its path with forward slashes only, so a Windows run and a Mac or
Linux run find one issue per finding instead of reopening each other's. Reads the issues from a stand-in, calls
file.held_all and file.plan, and prints PASS lines. usage: test-health-key-posix.py"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "..", "skills", "workflow-health", "scripts"))
import file as F  # noqa: E402
import issues as IS  # noqa: E402

BACK, FWD = "skills\\workflow-x\\scripts\\y.py", "skills/workflow-x/scripts/y.py"
fails = []


def check(name, ok):
    print(("PASS: " if ok else "FAIL: ") + name)
    if not ok:
        fails.append(name)


def item(subject):
    return {"state": "WARN", "family": "size", "subject": subject, "rule": "scripts", "detail": "18,900 of 19,000 bytes", "fix": "trim it"}


check("the key of a backslash path is the key of its forward-slash path", IS.key_of(item(BACK)) == IS.key_of(item(FWD)))
check("the evidence of a finding is the same on both", IS.evidence_of(item(BACK)) == IS.evidence_of(item(FWD)))
check("the older keys a finding may hold read the same on both", IS.legacy(item(BACK)) == IS.legacy(item(FWD)))
check("no key holds a backslash", "\\" not in IS.key_of(item(BACK)) and not any("\\" in k for k in IS.legacy(item(BACK))))


def issue(number, key, state="open"):
    return {"number": number, "state": state, "labels": ["health", "health:size"], "body": "<!-- loop-health %s evidence=abc -->\ntext" % key}


F.IS.fetch = lambda root, what: ([issue(10, "size:%s:scripts" % BACK), issue(11, "size:%s:scripts" % FWD), issue(12, "size:other.py:scripts")], "")
held, every, why = F.held_all(".")
check("two issues held under both spellings of one path are one key, and a different file stays its own",
      sorted(held) == ["size:other.py:scripts", "size:%s:scripts" % FWD] and len(every) == 3)

F.IS.fetch = lambda root, what: ([issue(10, "size:%s:scripts" % BACK, "closed"), issue(11, "size:%s:scripts" % FWD)], "")
held, _, _ = F.held_all(".")
check("an open duplicate wins over a closed one under the other spelling", held["size:%s:scripts" % FWD]["number"] == 11)

for subject in (BACK, FWD):
    acts = F.plan([item(subject)], {"size:%s:scripts" % FWD: {"number": 11, "state": "open", "labels": ["health:size"]}}, ["size"], root="")
    check("a finding at %s with the issue held under the forward-slash key is carried on, not opened again" % subject,
          [a["kind"] for a in acts if a["kind"] != "same"] in ([], ["update"]) and not any(a["kind"] == "open" for a in acts))
acts = F.plan([item(BACK)], {}, ["size"], root="")
check("a new finding is opened with a forward-slash key and title", len(acts) == 1 and acts[0]["kind"] == "open" and "\\" not in acts[0]["key"]
      and "\\" not in acts[0]["title"])
print("ALL PASS" if not fails else "%d FAILED" % len(fails))
sys.exit(1 if fails else 0)
