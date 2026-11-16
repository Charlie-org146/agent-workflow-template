# Design: trim-monitoring-4

## Problem
checkin.py (20,143), auto.py (20,120), replan.py (19,520) and pool.py (19,053) in workflow-monitoring sit over the 19,000-byte script cap (health size issues). The package has a file cap, so new files are out.

## Approaches
1. **Fold duplicates, trim prose, no new files (chosen).** auto.py gets one `stamp()`, one `owner_rows()` for the owner-words file, a `since(root, stamp, name)` shared with replan, and replan imports `loop_dir` and `top` from auto instead of redefining them; board_status.py gets `timed()`, the one time-format refusal that auto, replan and checkin each repeated; checkin.py folds its two pod loops into `others()`, builds live and queued goal items with one helper and shares the release/feature key; docstrings and comments are tightened.
2. Move code into a new module. Rejected: the package file cap (99 of 99).
3. Delete features. Rejected: done line 2 forbids behavior changes.

## Each done line
1. Sizes as git stores them: checkin 18,974, auto 18,924, replan 18,590, pool 18,927; dev/toy/test-trim-monitoring.py and row trim-monitoring-4-size (seen red) hold them.
2. The toys that run these scripts (auto-owner-words, blockers-first, checkin-view, eta-header-margin, eta-preflight, hard-eta, pr-order, pr-parallel, pr-queue-step, merge-unblock, reply-deps, graph-times, held-time-charge, machine-local, machine-status, backlog) pass; no file is added to the package; after merge the open health size issues for the four scripts are closed with a comment naming this goal.

## Open
none.
