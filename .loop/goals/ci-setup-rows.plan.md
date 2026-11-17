# Plan: ci-setup-rows (SET-1, #4553)

## Checked against the code

- `skills/workflow-setup/scripts/seed.py`: the local-schedule plan line now also needs
  `(LOOP_SCHEDULE_PLATFORM or sys.platform) == "darwin"` (commit 54129438).
- `skills/workflow-setup/scripts/setup.py` `adopt()`: `git add -A` runs only when some changed path is not held back
  (commit ea86425f); before, it passed a literal `--` pathspec.
- `skills/workflow-setup/scripts/update.py` `commit()`: on an interrupt it now sends TERM to the commit's process group,
  waits up to 10 s, then KILL (new helper `stop()`); Windows keeps `taskkill /T /F`.
- `dev/toy/test-setup-adopt.sh`, `dev/toy/test-adopt.sh`, `dev/toy/test-setup-fit.sh`: the toy fixes (preview issue
  count, package copy without compiled files, SET-4's expected changes).

## Build steps (in order)

1. The two setup defects (seed.py, setup.py). Done on the branch.
2. The toy fixes. Done on the branch.
3. The index.lock rollback (update.py). Done on the branch (cb2a4083).
4. Merge main (done: v1.0.35 to v1.0.39), then one full-suite CI run of the branch (`regression.yml` dispatch, no
   target) to prove all 14 rows on Linux together.
5. Run the 14 rows on the PC (`regression.py run ROW`) for done line 2.
6. Write each row's cause and its passing run on #4553; for lanes-trace, its remaining cause (the suite-wide trace
   exceeds the 900 s CI row limit on rows outside this goal, tracked on #4153).

## Tests per done line

1. The 14 rows themselves are the tests. Each was seen failing on CI run 43814023230 (loop/ci-fail-causes) and must
   pass on the full-suite run of this branch. `setup-refusal-writes-120` is the defect row for the index.lock bug
   (seen failing on CI run 43998234317, linked to issue 120).
2. The same 14 rows run on the PC through the regression lane.

## What could break

- `update.commit` on POSIX now waits up to 10 s after an interrupt before KILL; a hook that ignores TERM delays the
  rollback by that much, never more.
- The macOS-only schedule plan: a Linux adoption no longer seeds the local launch-agent schedule; it never could
  install it there.
- `test-windows-safe.py` and `test-portable.sh` guard POSIX-only calls; the new lines carry the `posix-only branch`
  marker (test-windows-safe passes on the PC).

## Out of scope

- lanes-trace's suite-wide timeout and the other rows it trips on (scripts-no-hang, defect-categories): #4153.
- The health finding on #4553 about SET-4 defined on two pages (ids-unique): a docs fix, not a Linux CI row.
