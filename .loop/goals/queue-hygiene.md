# A merged goal never holds the pr queue, and the merge-main-own toy passes or is explained

- Slug: queue-hygiene
- Touches: skills/workflow-monitoring/scripts/pool.py, skills/workflow-release/scripts/merge.py, dev/toy, .loop/regression.tsv, docs/wiki

## Done lines

Frozen. A wrong done line needs a new goal.

1. Once a goal's PR merges, merge.py removes that goal's pr-queue ticket and beat, and the queue treats a ticket whose goal is done, merged or stopped as free, each with a toy case proven red (#4343)
2. dev/toy/test-merge-main-own.py's last case, which fails on main, passes or is explained (#4343)

## Verify by hand

<!-- Numbered steps for a person, each with an Expect: line. A release needs this. -->
