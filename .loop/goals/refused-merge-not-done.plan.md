# Plan: refused-merge-not-done

1. autorelease.py: `fail()` sets status `failed` while the release is not `merged`; new `mergeable(state)` (done, or
   failed with a release_error, and a pull request) and `mark_merged(state)` (release merged, status done).
2. merge.py: use both helpers; the file ends shorter (62 bytes free under the 20480 cap).
3. dev/toy/test-merge-refused.sh: merge.py refused by a failing gh merge leaves status failed with release_error; resume
   revives it; merge.py run again merges it and ends done. Regression row `merge-refused-failed` (seen red first).
Out of scope: HEAD_MOVED and BASE_MOVED exits (no release failure is recorded, the goal stays done and retries by
goal.py pr), a worker that fails after the merge.
