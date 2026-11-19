# merge.py refuses a merge unless every required check is green on the exact PR head it is given, and goal.py pr commits its record before it pushes, so CI always runs on the final head (merge-queue slice A; issues #5171 and #5178; design accepted).

- Slug: merge-queue-a
- Touches: not declared
- ETA: 270 active minutes (estimate 216m plus a 25% margin, rough)

## Done lines

Frozen. A wrong done line needs a new goal.

1. merge.py --go-head SHA refuses unless the PR head equals SHA and every required check completed green on that exact sha, naming CI_PENDING, CI_RED or CI_MISSING; a green parent never counts; negative controls for each
2. goal.py pr commits its record (issue states, lane results) before it pushes, so the pushed head is the head CI runs on; a toy proves the head does not move after the push
3. Any changed requirement wording is sent to the operation for the owner before merge; it merges only after the v2.0 tag; net regression rows are 0 or fewer

## Verify by hand

<!-- Numbered steps for a person, each with an Expect: line. A release needs this. -->
