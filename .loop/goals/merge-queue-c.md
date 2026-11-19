# merge.py merges up to 3 ready PRs as one batch with one CI run and one release, so the train no longer needs a re-merge, a pr lane and CI for every PR (slice C of the merge queue; owner 01:42 o364; TOP-DECISION 99 design choices).

- Slug: merge-queue-c
- Touches: not declared
- ETA: 270 active minutes (estimate 213m plus a 25% margin, rough)

## Done lines

Frozen. A wrong done line needs a new goal.

1. Batching lives in merge.py or goal.py with no new file and the package at 100 files; a batch takes up to 3 done, mergeable PRs whose own CI is green, assembles them in queue order on a draft PR of the combined head, and binds the GO to that exact sha's CI; a member that conflicts goes alone
2. A red batch bisects to singles; a safety-class merge (steward, a cross-machine merge under a local rule, anything the owner marked) is never batched; one release lands for the batch; negative controls cover a red batch, a conflicting member, a safety-class member and a stale GO sha
3. Batching is off by default behind a setting, every script stays under its size cap (if it truly cannot fit, the worker reports it to operation-mac before adding a file), net regression rows 0 or fewer, the Release page states the rule, and new requirement IDs are reserved with operation-mac first and land Unreviewed

## Verify by hand

<!-- Numbered steps for a person, each with an Expect: line. A release needs this. -->
