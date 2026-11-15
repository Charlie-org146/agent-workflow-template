# merge.py audits .loop/START.md with the PR head's skills, not the main checkout's

- Slug: start-from-head
- Touches: skills/workflow-release/scripts, dev/toy, .loop/regression.tsv, docs/wiki

## Done lines

Frozen. A wrong done line needs a new goal.

1. merge.py audits .loop/START.md with the PR head's skills in a temporary worktree (as audit-pr-head did for wiki pages), so a PR that adds skill commands and carries a correct START.md merges, and a PR whose START.md is really stale is still refused, each with a toy case proven red (#4340)

## Verify by hand

<!-- Numbered steps for a person, each with an Expect: line. A release needs this. -->
