# Design: ci-setup-rows (SET-1, #4553)

## Problem

Fourteen setup, hooks and agent-permission rows fail on the Linux CI runner (run 43814023230) while they pass on the
PC. The issue guessed one shared cause (no claude CLI or settings on the runner); the row output shows several
separate causes instead: a macOS-only schedule step planned on Linux, a bare `--` pathspec git rejects when nothing
changed, toys that count or compare the wrong thing, and a signal during the adoption commit leaving git's
`index.lock` behind on Linux.

## Approaches

1. **Fix each row at its own cause** (chosen). Run each row alone on CI (`regression.yml` dispatch with the row id),
   read what it printed, fix the code or the toy, re-run. Cost: one CI dispatch per try (1-3 min a row). Risk: low;
   each fix is small and local to setup or its toys.
2. **Skip the rows on Linux** (mark them PC-only). Cost: near zero. Risk: hides real defects (the index.lock one is a
   real rollback bug on Linux and macOS) and does not meet done line 1.

## Causes and fixes

- `set1-never-blocks`, `set7-second-run-nothing`, `set9-from-borrows`, `setup-fit`, `adopt-fixture-ci-gitignore`,
  `grd10-install-hooks`, `grd3-private-commit`, `grd3-hooks-health`, `set8-hooks`, `set8-health`: two setup defects
  on Linux. Setup planned the local launch agent there, where automation.py refuses it (fix: plan the local schedule
  only on macOS, seed.py); and when every changed path was held back, it ran `git add -A -- --`, which git rejects
  (fix: add no paths then, setup.py). The SET-8 hook rows stopped at the same adoption step. The agent_command NOTE
  lines in their output were context, not the cause.
- `set1-no-fit-filed`: the toy compared filed issues to the preview's line count, which includes milestone lines and
  missing-milestone findings. Fix: count the preview's issues (toy).
- `sync-apply-keeps`: the SET-4 toy's package copy kept compiled files, and it treated automation (filled with the
  built-in routines) and README's generated tables (re-rendered) as unexpected changes. Fix: in the toy.
- `setup-refusal-writes-120`: on SIGTERM during a blocking commit hook, update.commit killed the git commit group with
  KILL, so git could not remove `.git/index.lock` and the rollback failed. Fix: TERM first, KILL after 10 s (update.py).
- `lanes-trace`: failed through `adopt-set-1` exiting 1 under the trace (same causes as above). The row now traces
  every land row inside one 900 s CI row limit and times out on rows outside this goal (#4153); that cause is
  written on #4553, not fixed here.

## Done lines

1. Each of the 14 rows passes on a CI run of this branch, or its real cause is written on #4553 (lanes-trace's
   timeout).
2. The same rows run on the PC and pass.

## Open questions

None left for the owner: lanes-trace's suite-wide timeout belongs to its own issue (#4153).
