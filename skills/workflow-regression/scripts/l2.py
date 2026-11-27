#!/usr/bin/env python3
"""The L2 run's rules (design items 6 to 9, 12 to 17): the full run that counts a row a state, names every row it did not run
and files its issues. The block between the l2tail markers is copied into the workflow, as runs.py's rowtail block is."""
import re


# l2tail:begin (actions.py copies this block into the workflow)
def l2_state(rid, code, said, late, known, skips):
    """(state, result comment, cause) for a row at L2. A row that never started is SKIPPED and red; one that ran is PASS, a
    by-design skip (exempt: counts as run, shown apart), KNOWN, any other skip (named), or FAIL."""
    if late:
        return "SKIPPED", "", "out of job time"
    if code == 0:
        return "PASS", "", ""
    why = skips.get(rid)
    if why and (code == 77 or why[1] == "notrun" and unrunnable(code, said)):
        return "SKIPPED", "# exempt %s %s" % (rid, why[0]), why[0]
    if rid in known:
        return "KNOWN", "", ""
    if code == 77:
        return "SKIPPED", "# skipped %s cannot run here" % rid, "cannot run here"
    return "FAIL", "", ""


def l2_again(run, row_s, job_s, begun, code):
    """The runner for a silent failing row's second run: the lesser of the row's limit and the job time left; with none left it is not run."""
    left = min(row_s, int(job_s - (time.time() - begun)))
    return lambda c: run(c, left) if left > 0 else (code, "")


def l2_refuse(target, cleanup):
    """The refusal line for a target and cleanup that L2 does not take, else an empty string."""
    if target == "L2" and cleanup == "true":
        return "REFUSED (L2_CLEANUP_EXCLUSIVE): cleanup runs no row and L2 runs every row. Fix: rerun with cleanup off, or with target nightly"
    return ""
# l2tail:end
