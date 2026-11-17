# hook-stub-mark design

## Problem
After the prose trim in adcaf82c, `seed.STUB` lost its hook mark line, so `seed.hook_state`, `setup.py --git-hooks --check` and health's hook rows read the hooks setup had just written as foreign (#4506, SET-1). The operator-setup goal restored the mark line in `seed.py` (14e19abe, now on main), but nothing tests it, so the next trim can drop it again.

## Approaches
1. Do nothing: the fix is on main. Cost zero, but the same trim can silently break it again.
2. Add one toy and two rows that write the hooks from an installed copy of the skills and read them back: the three hooks must report `installed`, and a hook someone else wrote must report `foreign` and stay byte for byte unchanged. Cost: one toy file and two rows; no change to setup code.

## Chosen
Approach 2. The code already meets both done lines; the goal needs the proof, with each row seen failing against a stub that has no mark line.

## What each done line needs
1. `dev/toy/test-hook-stub-mark.py` copies workflow-setup and workflow-delivery into a temp folder (setup refuses to write hooks from inside a goal's worktree), runs `setup.py --git-hooks`, then `--git-hooks --check`: no hook is foreign and the exit code is 0.
2. The same toy puts a hand-written hook (no private.py call) in place first: setup reports it as left alone, `--check` reports it foreign, and its text is unchanged.

## Open questions
None. Hooks written by the trimmed stub (before 14e19abe) in someone's clone stay foreign until `setup.py --git-hooks --remove` is run by hand; they were never marked, so setup cannot tell them from the owner's own. Out of scope.
