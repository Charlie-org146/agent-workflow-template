# Whole-tree rows run first in every PR's shard budget (TD494, TD497): rows the selector's closure shows reach the whole tree (one-way-to-run 27 s, package-gate-head, package-passes-3800, trim-package-98) get rank 0 ahead of changed-file rows; the merge queue's small job also runs python3 dev/package.py --static (0.94 s); rows LEFT in the branch's previous PR run go first in their shard on the next run. Added seconds per PR measured; armed only if merges stay within 3 minutes

- Slug: tree-rules-first
- Touches: skills/workflow-regression, .github, dev/toy
- ETA: 445 active minutes (estimate 355m plus a 25% margin)

## Done lines

Frozen. A wrong done line needs a new goal.

1. Given a PR that changes one unrelated file, when shards are planned, then the whole-tree rows run first and are never LEFT, shown by a toy
2. Given the merge queue workflow, then the small job runs package.py --static, and a toy or workflow check proves it
3. Given this goal's diff, then the PR body shows the added seconds per PR, the package stays at 100 files, no script newly crosses 19,000 bytes, and each new regression row has a red proof

## Verify by hand

<!-- Numbered steps for a person, each with an Expect: line. A release needs this. -->
