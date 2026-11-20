# PR CI shards are balanced by each row's recorded time, not by position (principle 3, DEL-17; owner words o643: the fast principle is a top priority; TD381). regression.py today splits the selected rows with todo[i::n], so one shard can draw the slow rows and set the whole run's time. The change: rows are assigned to the n shards by their recorded run time (longest first, each to the shard with the least total so far; a row with no recorded time gets the median), deterministic for the same input so every shard computes the same split. A row cut off by the per-row limit inside a PR shard is reported LEFT with its name, not FAILED (TD357 item 2), and the final affected job lists every LEFT row; a row that fails on its own still fails. Files: skills/workflow-regression/scripts/regression.py and skills/workflow-regression/scripts/lanes_cli.py only (rows-600-b does not touch them), plus one guard toy and the goal's record files; neither script ends over 20,480 bytes, and lanes_cli.py, if regenerated, keeps regression-pr.yml in step

- Slug: shard-balance
- Touches: skills/workflow-regression/scripts/regression.py, skills/workflow-regression/scripts/lanes_cli.py, .github/workflows/regression-pr.yml
- ETA: 460 active minutes (estimate 368m plus a 25% margin)

## Done lines

Frozen. A wrong done line needs a new goal.

1. Given a selection whose rows have recorded times, when the six shards compute their split, then each row lands in exactly one shard, the split is the same in every shard, and the largest shard's summed recorded time is within 20% of the mean or one row's time, whichever is larger; with LOOP_PR_SHARD unset nothing changes (negative control)
2. Given a PR shard run where one row passes its per-row limit, then that row is reported LEFT with its name and the shard does not fail because of it, while a row that exits non-zero inside the limit still fails the shard (negative control), and the affected job lists the LEFT rows
3. Given one new guard toy or regression row proving D1 and D2, when it runs, then it passes, net regression rows are at most plus 1, only regression.py, lanes_cli.py (and regression-pr.yml if regenerated from it), the toy and the goal's record files change, and each script is under 20,480 bytes

## Verify by hand

<!-- Numbered steps for a person, each with an Expect: line. A release needs this. -->
