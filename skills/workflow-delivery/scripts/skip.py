#!/usr/bin/env python3
"""DEL-25.3, shipped with the skills. lane(): skip the local lane when GitHub runs the tests (not on LOOP_LANE_LOCAL=1, with no
regression-pr.yml, or when GitHub does not answer; never a pass)."""
import os
import subprocess
import time

WORKFLOW = ".github/workflows/regression-pr.yml"
LINE = "SKIPPED: no local lane is owed on this head; the tests run on GitHub and its required checks decide (DEL-25.3); see them: gh pr checks"


def probe(limit=5):
    """'' when GitHub answers and regression-pr.yml is active there, else why not."""
    ask = ["gh", "api", "repos/{owner}/{repo}/actions/workflows?per_page=100", "--jq",
           '.workflows[]|select(.path=="%s")|.state' % WORKFLOW]
    try:
        done = subprocess.run(ask, capture_output=True, text=True, timeout=limit)
    except (OSError, subprocess.TimeoutExpired):
        return "GitHub did not answer in %ds" % limit
    if done.returncode:
        return "GitHub did not answer (gh api exit %d)" % done.returncode
    return "" if done.stdout.strip() == "active" else "%s is not active on GitHub" % os.path.basename(WORKFLOW)


def lane(base, head, name):
    """A skipped lane is recorded apart and is NEVER a pass: `.last` says `skipped` (not terminal, so lane-wait answers NO LANE, exit 3), `.txt` starts
    with the SKIPPED line, and `<step>-lane.skip` holds the head. `.ok` means a tested pass and nothing else. None: the lane runs."""
    import lanekit
    top = lanekit.git("rev-parse", "--show-toplevel").stdout.strip()
    if os.environ.get("LOOP_LANE_LOCAL") == "1" or not os.path.exists(os.path.join(top, WORKFLOW)):
        return None
    why = probe()
    if why:
        return print("lane runs: " + why)
    left = lanekit.dirty()
    if left:
        return "fail", "LANE_DIRTY at start: %s. Fix: commit or remove them; %s." % (", ".join(left[:10]), lanekit.NOTHING), []
    now = time.time()
    with open(base + ".txt", "w") as handle:
        handle.write(LINE + chr(10))
    lanekit.set_last(base + ".last", "skip-%d-%d" % (os.getpid(), now * 1000), head=head, state="skipped", skipped=True, started=now,
                     rc=None, line=LINE, ids=[], note="", log=base + ".txt")
    with open(base + ".skip", "w") as handle:
        handle.write(head)
    return "skipped", LINE, []


def accepts(runs, slug, name, head):
    """lanekit.lane_ok's reader of the skip record: `head` when a skip is recorded for it, `.last` still says skipped at that head, and every
    GitHub check run on that exact head is green (and there is at least one); '' otherwise, and always '' when gh does not answer."""
    import lanekit
    base = lanekit.lane_base(runs, slug, name)
    try:
        with open(base + ".skip") as handle:
            if handle.read().strip() != head:
                return ""
    except OSError:
        return ""
    last = lanekit.read_json(base + ".last") or {}
    if (last.get("state"), last.get("head")) != ("skipped", head):
        return ""
    ask = ["gh", "api", "repos/{owner}/{repo}/commits/%s/check-runs" % head, "--jq",
           '[.check_runs[].conclusion]|if length>0 and all(.=="success") then "green" else "no" end']
    try:
        seen = subprocess.run(ask, capture_output=True, text=True, timeout=10)
    except (OSError, subprocess.TimeoutExpired):
        return ""
    return head if not seen.returncode and seen.stdout.strip() == "green" else ""
