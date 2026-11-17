# Design: doc-milestone-sync

## Problem
The Documentation page says DOC-17 syncs milestones through `milestones_source`, and its last Non-goals line says "Syncing milestones, the README or Google Docs from an external source: left for later goals." The two contradict (#4546).

## Approaches
1. Reword the Non-goals line to drop "milestones" and point at DOC-17. Cost: one line, the page loses its Reviewed mark until the owner reviews it again. Risk: none to behavior.
2. Delete DOC-17's milestone bullets. Cost: removes shipped, tested behavior (13 milestone-sync tests). Risk: high.

## Choice
Approach 1, with the owner's approved wording (record o85): "Syncing the README or Google Docs from an external source: left for later goals. (Milestone sync is DOC-17.)" Nothing else on the page changes, and the page stays Unreviewed for the owner's later review.

## Done lines
1. A test reads the page and fails when DOC-17 syncs milestones and a Non-goals line leaves milestone sync for later; it failed on the old line and passes on the new one (row doc-nongoal-milestone-sync, proven red).
2. The wording went to the owner and was approved (o85); the page is un-reviewed and nothing is marked Reviewed.

## Open questions
None.
