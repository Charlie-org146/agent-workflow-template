# lane-prep: plan

Fixes #5730, #5728 and #5735 (DEL-17). Done lines are frozen in `.loop/goals/lane-prep.md`.

## Build steps, in order

1. `skills/workflow-docs/scripts/audit.py`: `relock(root, slug="", only=None)` tests `only is not None`, so an empty set of
   pages means none and `None` means every page; the DOC-18 loop reads `(only or ())`; `restamp_own` reads the lines of
   `docs.py check --own HEAD` that start `STALE <page>` (the form it already parses) and returns `[]` when there are none,
   so a lane start with nothing stale makes no Kept commit and HEAD stays (#5730). The only callers of `relock` are
   `restamp_own` (always a set) and `docs.py audit --relock` (passes none, so it keeps meaning every page); the
   `restamp` command line needs a page name, so it never passes an empty set.
2. `skills/workflow-delivery/scripts/fit.py` `regen`: read `git status --porcelain -- README.md` before `wiki.py prepare
   --commit`; afterwards, when README was clean before, the wiki step exited 0 and README now shows a modification, commit
   README alone by explicit path (`git commit -- README.md`, subject "Wiki: update pages for <slug>") and print
   `COMMITTED README.md for <slug>`. A README already dirty before (a hand edit, staged or untracked) is never committed, so
   the pr lane still refuses it with LANE_DIRTY. The regen is one sequential step in the worker's own worktree, so no hand
   edit can land between the two reads; the status line is the same source the lane's own LANE_DIRTY check reads. If the
   commit is refused (a hook) regen prints one plain line, "NOTE: README.md was re-rendered but not committed (<the git
   words>). Fix: commit it by hand, then run goal.py pr again", and goes on; the lane then refuses LANE_DIRTY and the
   operation session sees both lines. `wiki.py` is in workflow-release, outside this goal's touches, so it is not edited.
3. `skills/workflow-delivery/scripts/lane.py` `lane()`: `os.makedirs(runs, exist_ok=True)` first, so the first lane start in
   a fresh clone makes the runs folder, whatever `.git/loop` held (#5735). `lane_status` and `wait_for` only read and make
   nothing.
4. Tests: `dev/toy/test-lane-prep.py` (temp git repos made by the toy itself, so nothing depends on the machine) and one case in
   `dev/toy/test-merge-unblock.py`; three rows in `.loop/regression.tsv`, one per issue (5730 to DOC-2, 5728 and 5735 to
   DEL-17); the Tests tables the check requires are re-rendered (`docs/wiki/Delivery.md`, `Documentation.md`, `Tests.md`:
   the declared `docs` touch). The toys use fixture text only; the private-name scan runs at commit and in the lane's checks.

## Seen red (clean clone, old scripts, then the new ones)
Old scripts: FAIL "an empty set of pages re-stamps nothing, makes no Kept commit and HEAD does not move (#5730)"; FAIL "a lane
start in a clone with no runs folder makes the folder and does not crash"; FAIL "the regen commits a README its own render
changed, and the tree is clean"; FAIL "that commit is named for the wiki update and holds README.md"; FAIL "a refused README
commit says so in plain words with the fix and does not crash". New scripts: all pass, with the controls (a stale page is still
re-kept, a hand-edited README stays dirty, a failed wiki step commits no README, `lane_status` makes no folder).

## What could break
Script size caps: `fit.py` is 20,222 bytes (cap 20,480, warning 19,000), `lane.py` 18.8 KB and `audit.py` 19.1 KB, and no step grows
`fit.py` further. The meaning of an empty set for any other `relock` caller (none passes one).

## Open for the owner
Committing README inside the wiki commit, as one commit, needs `wiki.py` (workflow-release), outside this goal's touches; a later
goal could do it. Splitting the goal in three was weighed and not done: the three bugs share the lane-prep path and were
frozen as one goal.
