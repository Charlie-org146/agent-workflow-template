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

## Review changes (red-team pass)
- A slot is ignored only when the other goal's record shows the lane finished: `status == "done"` and a `pr` URL (goal.py sets them together at the end of pr); a rerun that is `running` keeps blocking.
- The record is read per entry in its own try; an unreadable record keeps the slot blocking, and the loop is never aborted by it.
- The refusal in `pr_wait` is measured from the wait's own start, so it fires when a holder keeps its slot fresh (a running lane or a waiting merge.py, which refreshes its own slot); the toy keeps the holder's slot fresh to exercise it.
- Not covered: a `merge.py` that holds `graph.merge_lock` (a different mechanism, graph.py, outside the touches); reported to the owner of the batch as a follow-up.
- Widen row `merge-batch-split` with `out=$(...)` so the toy runs once; measure bytes with LF only.
