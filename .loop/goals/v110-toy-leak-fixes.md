# Four known toy leaks fixed

- Slug: v110-toy-leak-fixes
- Touches: skills/workflow-regression/scripts/actions.py, dev/toy/test-merge-where.py, dev/toy/test-budget-order.py, dev/toy/test-platform-limits.py, dev/toy/test-entry-config.sh, .loop/regression.tsv, docs/wiki/Tests.md
- ETA: 460 active minutes (estimate 367m plus a 25% margin)

## Done lines

Frozen. A wrong done line needs a new goal.

1. Given test-merge-where.py started from a checkout, when it ends, then it has written no run record into that checkout.
2. Given a row started while a lane's handoff variables are set, when its environment is set, then it holds none of the lane's note, queued or started paths.
3. Given test-platform-limits.py started by a caller whose home trusts no folder, when it runs, then its session checks pass.
4. Given test-entry-config.sh run from a worktree, when it ends, then it has not changed that repo's user name or email and has registered no worktree in it.
5. The standard package line.

## Verify by hand

<!-- Numbered steps for a person, each with an Expect: line. A release needs this. -->
