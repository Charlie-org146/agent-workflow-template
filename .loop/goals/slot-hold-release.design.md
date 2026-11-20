# Design: slot-hold-release

## Problem
`replan.pr_hold` takes a merge-slot file in `.git/loop/pr-slots/` when a goal's pr lane starts, and only a failed try or the goal's own
`merge.py` exit frees it. A goal whose lane finished and whose PR is held (batch or any reason), or whose merge ran, keeps the file, so
`replan.pr_before` makes every later `merge.py` wait behind it with one WAITING line that never ends until the 1800 s staleness drop.

## Approaches
1. Free the slot in `goal.py pr` when the PR opens. Cost: touches goal.py (outside this goal's touches); misses held and already-merged goals whose file already exists.
2. In `replan.pr_before`, ignore (and delete) the slot of any other goal whose run record already has a `pr` URL: its lane is finished, and a merge.py that is running holds `merge.lock`, which already makes later merges wait with a message. Add a refusal in `pr_wait` after LOOP_MERGE_LOCK_SECONDS naming the holder. Cost: ~10 lines in replan.py. Risk: a lane rerun on a goal with a PR re-holds at its next `pr_hold`, as today.

## Chosen
Approach 2: it fixes goals already stuck, needs no goal.py change, and stays inside the declared touches.

## Done lines
1. Toy: goal A has a slot and a `pr` in its run record; `before(B)` is "" and A's slot file is gone. Negative control: with no `pr` in A's record B waits behind A (the old behaviour for a running lane stays).
2. Toy: `pr_wait` with a running holder prints WAITING naming it and, with LOOP_MERGE_LOCK_SECONDS small, exits REFUSED naming the holder. Negative control: the old pr_before (a finished lane's slot still blocks) fails the toy; shown by running the toy against main's replan.py.
3. replan.py stays at or under main's bytes (18,818); no new file; zero net rows (an existing row's command is widened, not added).

## Open questions
None.
