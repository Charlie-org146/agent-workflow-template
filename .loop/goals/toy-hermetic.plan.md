# Plan: toy-hermetic

## Implementation plan

Checked against the code: the two toys are `dev/toy/test-platform-limits.py` (row `platform-sends-counted`, land) and `dev/toy/test-machine-log.py` (row `machine-status-live-workers`, land), both in `.loop/regression.tsv`. The build is already committed (cfbcd143a and 6b10f26c7); this plan reviews and verifies it, it does not rewrite it.

What the build does, per toy:

1. `test-machine-log.py`: before importing anything it drops every `CLAUDE*`, `ANTHROPIC*` and `LOOP_*` variable and `GIT_DIR`, `GIT_COMMON_DIR`, `GIT_WORK_TREE`, and points HOME and USERPROFILE at a throwaway directory. `run_loop` changes into the fixture directory so the wait loop's operation-session claim follows the fixture repo, never the checkout. New checks: no session id reaches the wait loop so it claims nothing; a negative control that a host session id left in the environment makes the wait loop claim, and the claim lands only in the fixture; the checkout's own `.git/loop/operation.id` hashes the same before and after.
2. `test-platform-limits.py`: `run()` builds the child environment without `LOOP_*`, `CLAUDE*`, `ANTHROPIC*` and the three git location variables, and with a throwaway HOME. New checks: with a host session id and GIT_DIR set in the parent environment the fixture still counts its send; the checkout's own operation id file is unchanged before and after.
3. Both toys keep every earlier assertion; nothing is skipped or loosened.

Test for each done line:

- Done line 1: with the Mac's real session state in the environment, each toy prints its OK line (`PLATFORM LIMITS TOY OK`; machine-log exits 0 with every PASS) and its row passes in a qa lane on the Mac. The "fails as today" half is shown by the negative controls: a leaked host session id changes the outcome unless the scrub is there.
- Done line 2: `git diff origin/main...HEAD -- dev/toy` removes no assertion line and adds no skip; each toy keeps its original negative controls and gains the controls above.
- Done line 3: `git diff origin/main...HEAD --stat` lists only the two toys and this goal's records (`.loop/goals/toy-hermetic.*`, `.loop/kept/`, `.loop/lane-results/`); `docs.py check --own` passes; the private scan is clean.

What could break:

- A state source the scrub does not cover (another variable family, another dotfile under HOME) would leak again; the controls fail only when the scrub is bypassed, not for a new source.
- The hash check reads the checkout's operation id file; it must only read it, never write or print it.
- Running either toy against the real operation id file from any other checkout is outside this goal (operator ban: run the toys only from this goal's worktree).

Out of scope: any script under skills/, the regression table, any other toy, the toys' CI behavior.

PENDING: none for the owner.

## Review record

Filled by the plan review.
