# The reply-hook, check-in, operate, guards and monitoring regression rows that are red on main in the full runs 44463859531 and 44465229184 pass again: reply-hook-all reply-hook-blocks reply-hook-checkin-123 operate-10-under-load operate-wait-99 guards-resume grd5-regression-dry landed-left-alone lane-control-all lane-messages-table toy-no-leftovers del9-scan-sites. Each is fixed, or removed with evidence that the behaviour it tests is gone; none is moved to the known list (owner: "No waivers u can do it").

- Slug: known-red-w7-ops-checkin
- Touches: not declared
- ETA: 270 active minutes (estimate 213m plus a 25% margin, rough)

## Done lines

Frozen. A wrong done line needs a new goal.

1. Each of these rows passes on the PR head in the CI full-suite shards, or is removed from .loop/regression.tsv with evidence in the PR that the behaviour it tests no longer exists: reply-hook-all reply-hook-blocks reply-hook-checkin-123 operate-10-under-load operate-wait-99 guards-resume grd5-regression-dry landed-left-alone lane-control-all lane-messages-table toy-no-leftovers del9-scan-sites
2. No row is added to .loop/regression-known.tsv, and net regression rows are 0 or fewer against main

## Verify by hand

1. Run `bash dev/toy/test-operate.sh`.
   Expect: it ends with ALL PASS.
2. Run `bash dev/toy/test-scan-sites.sh`.
   Expect: it lists only operate.py:apply as unscanned until the operate.py scan call lands; after that, ALL PASS.
3. Run `python3 skills/workflow-regression/scripts/regression.py run operate-10-under-load`.
   Expect: PASS operate-10-under-load.
