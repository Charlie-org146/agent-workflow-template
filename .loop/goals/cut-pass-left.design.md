# Design: cut-pass-left

## Problem
The v1.0.0 cut ran about 1,000 rows one by one with no budget (#4508). The fix on loop/v1-go-no-go added the known list, exit 77 as skipped, a PASS skip and a 900 s stop; two weaknesses remain: a PASS in regression-runs.tsv is per row, not per commit, and rows not run before the stop are not reported.

## Approaches
1. **A lane-record check and a LEFT list, in the release skill's review.py (chosen).** regression-runs.tsv holds no commit (by design: a commit column would conflict on every merge), so the commit of a PASS comes from the lane records in the git common folder (rows[id].commit). `review.proven()` returns the rows with a PASS on HEAD; the cut skips only those (and the known list) and runs the rest until the stop (900 s, LOOP_CUT_SECONDS for tests); the rest are returned as `left`, printed as LEFT with their count and written into the release notes (`review.left_text`).
2. A commit column in regression-runs.tsv: conflicts on every merge. Rejected.
3. A new helper module: the package is at its 99-file cap (package-headroom allows 98), so no new file; review.py is an existing small file of the same skill that release.py already shares with merge.py. The criteria loop moved there, which also takes release.py from 18,909 to 17,890 bytes.

## Each done line
1. toy case 1 (current PASS skipped, older PASS rerun); row cut-pass-current-commit.
2. toy cases 3 to 5 (forced stop lists LEFT with a count; negative control nothing LEFT); rows cut-left-listed and cut-left-none.

## Open questions
None. Caveat: a row whose PASS was recorded on an earlier commit (for example before a merge commit) reruns; the cut runs until its stop and lists the rest, which is the point.
