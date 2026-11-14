# A feature's PRD can be changed on either side, in the repo by an agent's goal or in the external document by people, and the two always say the same: docs.py sync names each difference as a DELTA, posts it for review as a GitHub issue and a comment on the external page, writes only the accepted text to the other side, and health and the check-in show open deltas as inconsistencies

- Slug: ext-two-way
- Touches: skills/workflow-docs, skills/workflow-health, skills/workflow-monitoring, dev/toy, docs, README.md, .loop/regression.tsv

## Done lines

Frozen. A wrong done line needs a new goal.

1. With a requirement changed on only one side, docs.py sync prints a DELTA naming the page, the ID, which side changed and both texts, and overwrites neither side
2. docs.py sync posts each delta once as a GitHub issue on the feature's milestone and once as a comment on the external page, and prints not connected, never failing, when it has no connector
3. docs.py sync --accept PAGE:ID=repo or =source writes only that side's text to the other side, Notion included, closes the delta and leaves every other requirement as it was
4. Health and the check-in list each open delta as an inconsistency

## Verify by hand

<!-- Numbered steps for a person, each with an Expect: line. A release needs this. -->
