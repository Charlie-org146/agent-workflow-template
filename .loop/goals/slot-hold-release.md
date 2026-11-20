# A goal whose pr lane has finished and that has no merge.py running no longer keeps the merge slot, so a held PR (for a batch or any reason) cannot block a later merge.py with a go-head; and merge.py's wait prints who holds the slot and gives up with a refusal after LOOP_MERGE_LOCK_SECONDS (#5309, TD194)

- Slug: slot-hold-release
- Touches: skills/workflow-monitoring/scripts/replan.py, skills/workflow-monitoring/scripts/pool.py, dev/toy/test-merge-batch.py, .loop/regression.tsv
- ETA: 250 active minutes (estimate 198m plus a 25% margin)

## Done lines

Frozen. A wrong done line needs a new goal.

1. Given goal A's pr lane finished and A has no merge.py running, when goal B's merge.py --go-head starts, then B does not wait on A and merges
2. Given a goal whose merge.py is running and holds the slot, when another merge.py starts, then it prints WAITING naming the holder and, past LOOP_MERGE_LOCK_SECONDS, refuses naming the holder instead of waiting forever, with a negative control that the old behaviour (waiting behind a finished lane) fails the toy
3. Given this goal's diff, then no shipped file is added, no touched script is over 19,000 bytes or larger than on main, net regression rows are 0 or fewer, and no requirement text changes

## Verify by hand

<!-- Numbered steps for a person, each with an Expect: line. A release needs this. -->
