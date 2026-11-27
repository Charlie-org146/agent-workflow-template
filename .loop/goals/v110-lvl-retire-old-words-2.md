# One set of level words: L0, L1, L2

- Slug: v110-lvl-retire-old-words-2
- Touches: skills/workflow-regression, skills/workflow-setup, skills/workflow-delivery, skills/workflow-health, skills/workflow-docs, skills/workflow-release, skills/loop-files.md, dev/toy, .loop/regression.tsv, .loop/config.json, docs/wiki
- ETA: 1060 active minutes (estimate 848m plus a 25% margin, rough)

## Done lines

Frozen. A wrong done line needs a new goal.

1. Given the goal_levels setting, the PR workflow's level map and the Regression runbook's labels, when they are read, then each uses the levels L0, L1 and L2 and none uses the words land, nightly, covered or draft.
2. Given a draft row, when the table is read, then its draft mark is in its own state column, it carries the level it will have, every level lists it as "not run: draft", and a requirement held only by drafts shows "not enforced".
3. Given a covered row, when the table is read, then it takes the highest level of the rows its list names and is green when they all are, and a covered row whose list doesn't resolve to row IDs is refused.
4. Given the package, when the goal's checks run, then every script stays under 20,480 bytes, no test is loosened, no row turns red, and committed text never names the service repo.

## Verify by hand

<!-- Numbered steps for a person, each with an Expect: line. A release needs this. -->
