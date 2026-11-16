# A PRD page opted in to an external source keeps its last agreed version in the repo, so no checker needs the source or a reader; docs.py sync merges the source only when a reader exists.

- Slug: offline-prd-copy
- Touches: skills/workflow-docs, dev/toy, .loop/regression.tsv, docs/wiki, DECISIONS.md

## Done lines

Frozen. A wrong done line needs a new goal.

1. A PRD page opted in to an external source (a .loop/docs.tsv source such as mcp:notion:<id>, DOC-17) keeps the last agreed version in .loop/prd/PAGE.md. Every checker (docs check and audit, health, the rows, merge.py's wiki.pending) reads that copy, so no lane, CI run or health check needs Notion or LOOP_PRD_READER; with no reader there are no LINK or UNREAD failures. The wiki page still shows Problem, Requirements, Non-goals and Success metrics, as a block generated from .loop/prd/PAGE.md; deployments.py allows those sections when they are that block. docs.py sync uses the source only when a reader exists. It normalises the source's layout first (the Notion page writes 'NL-1 Functional: (Reviewed ...)' and has a 'New requirements' block), takes additions from either side as deltas accepted with --accept, and reports a change on both sides as a CONFLICT, never overwriting it. Toy cases are proven red: an opted-in page passing with no reader; the generated block; a delta from each side; a conflict; a page with no source unchanged. Files stay at or under 19,000 bytes and the package at 98 files or fewer; no ~/.workflow-loop file is edited; the DOC-17 sub-bullet text goes to operation before it is applied (owner records o37 and o38).

## Verify by hand

<!-- Numbered steps for a person, each with an Expect: line. A release needs this. -->
