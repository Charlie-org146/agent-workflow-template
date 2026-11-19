# Plan: slot-hold-release

Checked: `pr_hold`/`pr_free`/`pr_before`/`pr_wait` in skills/workflow-monitoring/scripts/replan.py (lines ~221-265); `graph.pr_queue` forwards hold/free/before/wait there; goal.py calls hold at pr start (line 350) and free on a failed try (177); merge.py calls wait (line 289) then `merge_lock`. Run records are `.git/loop/runs/<slug>.json` with a `pr` URL once the PR opens.

## Steps
1. replan.py: `pr_before` unlinks and skips any slot of another goal whose run record has `pr`; `pr_wait` records its start and, past LOOP_MERGE_LOCK_SECONDS, exits `REFUSED: <holder>'s pr lane still holds the merge slot after N s`. Trim comments in replan.py to stay at or under 18,818 bytes.
2. dev/toy/test-merge-batch.py: add checks in a temp runs dir (run record with/without `pr`, `pr_before`, `pr_wait` wait then refusal with LOOP_MERGE_LOCK_SECONDS=1 and LOOP_SLOT_POLL=0.05) plus a final PASS line; widen row `merge-batch-split` to require it. Zero new rows.
3. Seen failing: run the toy with main's replan.py (`regression.py red merge-batch-split --break "git show origin/main:... > replan.py"`).

## Could break
A run record unreadable or absent: the slot keeps blocking as today. A goal re-running its lane after its PR opened: it re-holds and blocks again, as today.

## Out of scope
goal.py, pool.py, graph.merge_lock, batch merging.
