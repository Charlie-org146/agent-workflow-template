#!/usr/bin/env python3
# reads: skills/workflow-health/scripts/milestone.py skills/workflow-health/scripts/health.py dev/toy/fakegh/gh
"""CHK-1/HLT-2 (fast-3min): health prints the queue's use for the last 20 merges (PRs per merge, the wait before the queue) and FAILS a wait over 2 minutes.
A fake gh answers the GraphQL query with prepared merges. Run: python3 dev/toy/test-queue-use.py"""
import json
import os
import subprocess
import sys
import tempfile

here = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, os.path.join(here, "skills", "workflow-health", "scripts"))
import milestone  # noqa: E402

d = tempfile.mkdtemp()
subprocess.run(["git", "init", "-q", d], check=True)
subprocess.run(["git", "-C", d, "remote", "add", "origin", "https://github.com/o/r.git"], check=True)
os.environ["PATH"] = os.path.join(here, "dev", "toy", "fakegh") + os.pathsep + os.environ["PATH"]
os.environ["FAKE_GH_DIR"] = os.path.join(d, "gh")
fails = 0


def check(ok, what):
    global fails
    print(("PASS: " if ok else "FAIL: ") + what)
    fails += 0 if ok else 1


def pr(number, checks, queued, merged):
    return {"number": number, "mergedAt": merged, "commits": {"nodes": [{"commit": {"statusCheckRollup": {"contexts": {"nodes": [
        {"completedAt": checks}, {"createdAt": "2026-01-01T00:00:00Z"}]}}}}]},
        "timelineItems": {"nodes": [{"createdAt": queued}]}}


def rows(nodes, since="2026-01-01T00:00:00Z"):
    path = os.path.join(d, "q.json")
    open(path, "w").write(json.dumps({"data": {"repository": {"pullRequests": {"nodes": nodes}}}}))
    os.environ["FAKE_GH_GRAPHQL"] = path
    return milestone.queue_rows(d, since=since)


got = rows([pr(1, "2026-01-01T10:00:00Z", "2026-01-01T10:00:08Z", "2026-01-01T10:01:00Z"),
            pr(2, "2026-01-01T11:00:00Z", "2026-01-01T11:00:02Z", "2026-01-01T11:01:00Z")])
check(got[0]["state"] == "PASS" and "1.0 PRs per merge" in got[0]["detail"] and "longest wait before the queue 8s" in got[0]["detail"],
      "waits of 8 s and 2 s pass and the row prints PRs per merge and the longest wait")
got = rows([pr(1, "2026-01-01T10:00:00Z", "2026-01-01T10:00:08Z", "2026-01-01T10:01:00Z"),
            pr(2, "2026-01-01T11:00:00Z", "2026-01-01T11:02:42Z", "2026-01-01T11:03:34Z")])
check(got[0]["state"] == "FAIL" and "#2 (162s)" in got[0]["detail"] and got[0]["fix"],
      "negative control: a PR that entered the queue 162 s after its checks passed FAILS, naming it and the fix")
got = rows([pr(1, "2026-01-01T10:00:00Z", "2026-01-01T10:00:08Z", "2026-01-01T10:01:00Z"),
            pr(2, "2026-01-01T10:00:00Z", "2026-01-01T10:00:09Z", "2026-01-01T10:01:00Z")])
check(got[0]["state"] == "PASS" and "2.0 PRs per merge" in got[0]["detail"], "two PRs merged together count as 2.0 PRs per merge")
got = rows([pr(1, "2026-01-01T10:00:00Z", "2026-01-01T10:02:42Z", "2026-01-01T10:03:34Z")], since="2026-02-01T00:00:00Z")
check(got[0]["state"] == "PASS" and "longest wait before the queue 162s" in got[0]["detail"] and "only info" in got[0]["detail"],
      "a 162 s wait in a merge before the start stamp is shown as info and does not fail")
os.environ["FAKE_GH_GRAPHQL"] = os.path.join(d, "missing.json")
got = milestone.queue_rows(d)
check(got[0]["state"] == "UNREAD", "an answer gh cannot read is UNREAD, never a pass")
sys.exit(1 if fails else 0)
