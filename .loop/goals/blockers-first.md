# The check-in's Needs you section ranks each owner item by what it blocks, most-blocking first, and the Stop hook enforces it (#4040)

- Slug: blockers-first
- Touches: skills/workflow-monitoring, dev/toy, DECISIONS.md

## Done lines

Frozen. A wrong done line needs a new goal.

1. A check-in's Needs you lists each owner item with the goals it holds up, its count and whether it is on the critical path to the next release, most-blocking first; an item that holds nothing says blocks nothing; the Stop hook refuses a check-in without that

## Verify by hand

<!-- Numbered steps for a person, each with an Expect: line. A release needs this. -->
