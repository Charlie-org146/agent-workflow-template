# merge.py's wiki check audits the goal's PR head with the head's own docs scripts, so a goal that changes a rendered setting or the Review stamp format can merge (#4340 did it for START.md)

- Slug: audit-head-docs
- Touches: skills/workflow-release/scripts, dev/toy, .loop/regression.tsv, docs/wiki

## Done lines

Frozen. A wrong done line needs a new goal.

1. merge.py's wiki.pending runs docs.py audit and check from the PR head's own tree when that tree has them, otherwise from main's; a toy case is proven red (a head whose own render differs from main's passes, a head stale under its own scripts is still refused); wiki.py grows at most 400 bytes and every file touched stays net-zero or under 19,000

## Verify by hand

<!-- Numbered steps for a person, each with an Expect: line. A release needs this. -->
