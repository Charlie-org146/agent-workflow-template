# Every workflow-docs and workflow-release script is under 19,000 LF bytes, with behaviour unchanged, so no script sits at the size cap

- Slug: scripts-b
- Touches: skills, docs

## Done lines

Frozen. A wrong done line needs a new goal.

1. Every script in skills/workflow-docs/scripts and skills/workflow-release/scripts measures 19,000 LF bytes or fewer, checked by a row that fails when any of them is over
2. Behaviour is unchanged: the toys of both skills pass, docs-block-split passes on render.py, and the package gate shows no more files than before

## Verify by hand

<!-- Numbered steps for a person, each with an Expect: line. A release needs this. -->
