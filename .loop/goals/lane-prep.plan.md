# lane-prep: plan

Fixes #5730, #5728 and #5735 (DEL-17). Done lines are frozen in `.loop/goals/lane-prep.md`.

## Build steps, in order

1. `skills/workflow-docs/scripts/audit.py`: `relock(root, slug="", only=None)` tests `only is not None`, so an empty set of
   pages means none and `None` means every page (`docs.py audit --relock` keeps the old meaning); the DOC-18 loop reads
   `(only or ())`; `restamp_own` returns `[]` when `docs.py check --own HEAD` names no STALE page, so a lane start with
   nothing stale makes no Kept commit and HEAD stays (#5730). The `restamp` command line needs a page name, so it never
   passes an empty set.
2. `skills/workflow-delivery/scripts/fit.py` `regen`: note `git status --porcelain -- README.md` before `wiki.py prepare
   --commit`; after it, when README was clean before, the wiki step exited 0 and README is now modified, commit it alone
   by explicit path with the wiki update subject and print `COMMITTED README.md`. A README already dirty before (a hand
   edit, staged or untracked) is left alone, so the pr lane still refuses it with LANE_DIRTY (#5728). `wiki.py` is in
   workflow-release, outside this goal's touches, so it is not edited.
3. `skills/workflow-delivery/scripts/lane.py` `lane()`: `os.makedirs(runs, exist_ok=True)` first, so the first lane start in
   a fresh clone makes `.git/loop/runs` (#5735).
4. Tests: `dev/toy/test-lane-prep.py` (runs folder, README regen with negative controls) and one case in
   `dev/toy/test-merge-unblock.py` (an empty page set re-stamps nothing, HEAD stays); three rows in
   `.loop/regression.tsv`, seen red against the old code; Tests tables re-rendered.

## Tests (each seen red before the change)
Each new assertion was run against the old scripts in a clean clone and fails there; the negative controls (a stale page
is still re-kept, a hand-edited README stays dirty, a failed wiki step commits no README, `lane_status` makes no folder)
pass before and after.

## What could break
Script size caps (`fit.py` is near 20 KB), the meaning of an empty set for any other `relock` caller (none passes one),
the README commit failing after the wiki commit (the run stops with the hook's words).

## Reviews so far
Four independent fresh-context reviews of the plan (one first pass, then CEO, DX and eng), then an adversarial and a Codex
review of the diff; their findings are folded in above.
