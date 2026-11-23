#!/usr/bin/env python3
"""DEL-25.3, shipped with the skills. lane(): skip the local lane when GitHub runs the tests (not on LOOP_LANE_LOCAL=1, with no
regression-pr.yml, or when GitHub does not answer; never a pass)."""
import os
import re
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


def required_jobs(top):
    """The job ids of regression-pr.yml that a pull request runs (the ones not only for the merge queue); [] when the file cannot be read."""
    try:
        with open(os.path.join(top, WORKFLOW), encoding="utf-8") as handle:
            lines = handle.read().splitlines()
    except OSError:
        return []
    jobs, inside = [], False
    for line in lines:
        if line.startswith("jobs:"):
            inside = True
        elif inside and (found := re.match(r"^  ([A-Za-z0-9_-]+):\s*$", line)):
            jobs.append([found.group(1), False])
        elif inside and jobs and re.match(r"^    if:.*==\s*'merge_group'", line):
            jobs[-1][1] = True
    return [name for name, queue_only in jobs if not queue_only]


def accepts(runs, slug, name, head):
    """lanekit.lane_ok's reader of the skip record: `head` when a skip is recorded for it, `.last` still says skipped at that head, and every job
    regression-pr.yml runs for a pull request has check runs on that exact head, all completed with success (other check runs never count; all pages
    are read); '' otherwise, and always '' when gh does not answer."""
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
    need = required_jobs(lanekit.git("rev-parse", "--show-toplevel").stdout.strip())
    ask = ["gh", "api", "--paginate", "repos/{owner}/{repo}/commits/%s/check-runs" % head, "--jq",
           '.check_runs[]|[.name,.status,.conclusion]|@tsv']
    try:
        seen = subprocess.run(ask, capture_output=True, text=True, timeout=30)
    except (OSError, subprocess.TimeoutExpired):
        return ""
    if not need or seen.returncode:
        return ""
    rows = [line.split("\t") + ["", ""] for line in seen.stdout.splitlines() if line.strip()]
    for job in need:
        mine = [r for r in rows if r[0] == job or r[0].startswith(job + " (")]
        if not mine or any(r[1] != "completed" or r[2] != "success" for r in mine):
            return ""
    return head
