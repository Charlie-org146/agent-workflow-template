#!/usr/bin/env python3
# windows: ok
# reads: skills/workflow-delivery/scripts/dlf.py
"""DLF-1.1 and DLF-1.3: the stop table. A stop is classified by its subject: each safety subject waits (one red fixture each), every
other stop becomes a line, an unclassifiable stop waits, the agent's label can only raise a stop, the word scan catches a safety
word in a stop labelled other, benign text passes (negative control), and the board's wait line has the pinned wording."""
import os
import sys

root = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
sys.path.insert(0, os.path.join(root, "skills", "workflow-delivery", "scripts"))
import dlf  # noqa: E402

failed = []


def check(ok, text):
    print(("PASS: " if ok else "FAIL: ") + text)
    if not ok:
        failed.append(text)


S = dlf.SAFETY
TEST_DIFF = "--- a/tests/test_a.py\n+++ b/tests/test_a.py\n@@ -1 +1 @@\n-    assert total == 3\n+    assert total >= 0\n"
SKIP_DIFF = "--- a/tests/test_a.py\n+++ b/tests/test_a.py\n@@ -1 +1,2 @@\n+@pytest.mark.skip\n def test():\n"
ROWS_DIFF = "--- a/.loop/regression.tsv\n+++ b/.loop/regression.tsv\n@@ -1 +1 @@\n-row-a\tland\tcmd\n+row-a\tland\ttrue\n"
ADD_DIFF = "--- a/tests/test_a.py\n+++ b/tests/test_a.py\n@@ -1 +1,2 @@\n def test():\n+    assert 1\n"
c = dlf.classify
check(c("test", "a test failed", diff=TEST_DIFF) == S[6], "a changed assertion in a test file is a loosened test: it waits")
check(c("test", "a test failed", diff=SKIP_DIFF) == S[6], "an added skip marker is a loosened test: it waits")
check(c("test", "a test failed", diff=ROWS_DIFF) == S[6], "an edited row in the regression rows file is a loosened test: it waits")
check(c("test", "a test failed", diff=ADD_DIFF) == "other", "a test only added is not loosened: it becomes a line (negative control)")
check(c("break", "a break", paths=[".claude/settings.json"]) == S[2], "a goal touching a settings file is a security subject: it waits")
check(c("break", "a break", paths=["skills/a/b.py"]) == "other", "a goal touching only code is other: it becomes a line")
check(c("break", "a break", cls=S[1]) == S[1], "a break with a recorded safety class takes it (money)")
check(c("choice", "pick one", paths=["docs/wiki/Deliver-first.md"]) == S[5], "a design choice touching a requirement page changes what a feature promises: it waits")
check(c("test", "oops", diff="+key = ghp_" + "a" * 36 + "\n") == S[3], "a secret pattern in the diff is private data: it waits")
for subject, text in zip(S, ("we must force-push the branch", "refund the payment", "grant the sandbox a new permission mode", "this would leak a private name",
                              "turn on the steward auto-merge", "this changes what the feature promises", "loosen the assertion")):
    check(c("break", text, paths=["x.py"]) == subject, "the word scan: %r in a stop labelled other waits as %s" % (text, subject))
check(c("break", "a break", paths=["x.py"], label=S[1]) == S[1], "the agent's label raises a stop to a safety subject")
check(c("break", "a break", paths=[".claude/settings.json"], label="other") == S[2], "the agent's label never lowers what the rule found")
check(c("break", "a break") == "unclassifiable", "a break with no class, no touches and no diff is unclassifiable: it waits")
check(c("test", "x") == "unclassifiable", "a failing test with no diff is unclassifiable: it waits")
check(c("nonsense", "x", paths=["a.py"]) == "unclassifiable", "an unknown stop is unclassifiable: it waits")
check(c("budget", "the budget needs more than the cap", template=True) == "other", "a budget stop built from the table's own template is other")
check(c("budget", "the sandbox budget", template=False) == S[2], "the template exemption holds only when declared: free text is scanned")
check(c("break", "the loop stalls when two goals race for one slot", paths=["skills/a/b.py"]) == "other", "benign text passes as other (negative control)")
check(dlf.wait_line("g1", S[6], "a test was loosened", "the operation answers it (goal.py answer g1)") ==
      "WAITING g1: a test loosened or deleted - a test was loosened - owner action: the operation answers it (goal.py answer g1)", "the board wait line has the pinned wording")
sys.exit(1 if failed else 0)
