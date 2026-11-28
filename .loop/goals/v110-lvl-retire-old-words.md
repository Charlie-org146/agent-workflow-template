# One set of level words: L0, L1, L2

- Slug: v110-lvl-retire-old-words
- Touches: skills/workflow-regression, skills/workflow-setup, skills/workflow-delivery, skills/workflow-health, skills/workflow-docs, skills/workflow-release, skills/loop-files.md, .github/workflows, dev/toy, .loop/regression.tsv, .loop/config.json, docs/wiki
- ETA: 1050 active minutes (estimate 839m plus a 25% margin, rough)

## Done lines

Frozen. A wrong done line needs a new goal.

1. Given the goal_levels setting, the PR workflow's level map and the Regression runbook's labels, when they are read, then each uses the levels L0, L1 and L2 and none uses the words land, nightly, covered or draft.
2. Given a draft row, when the table is read, then its draft mark is in its own state column, it carries the level it will have, every level lists it as "not run: draft", and a requirement held only by drafts shows "not enforced".
3. Given a covered row, when the table is read, then it takes the highest level of the rows its list names and is green when they all are, and a covered row whose list doesn't resolve to row IDs is refused.
4. Given the package, when the goal's checks run, then every script stays under 20,480 bytes, no test is loosened, no row turns red, and committed text never names the service repo.
5. Given a release cut, when it is made, then it waits for a green full (L2) run.

## Notes

- Line (4)'s 20 KB limit is the package rule A keeps (A's done line 2: '20 KB per packaged script'; TD1973/TD1987); our own byte caps are void once A merges (o1008 'No size limits A wins').
- Line (5) comes from the owner's words, ledger o996: "Add the release cut's wait for a green full run to v110-lvl-retire-old-words."
- Lines 1, 2, 3 and 4 are the drafted lines 1, 2, 3 and 5 (o1008); the drafted line 4, dropping the old level column, is not in this goal (o1008).

## Preconditions

- The plan can be written and reviewed now. The BUILD waits for G1 (v110-lvl-relevel, which assigns each row's L0 to L2 level) and G3 (v110-lvl-l2, which provides the full L2 run) to be merged, and for G2 (v110-lvl-l1) if the plan shows a dependency on it.
- The safety parts need the owner's own words before the build; relayed words do not count (TD2002).

## Verify by hand

<!-- Numbered steps for a person, each with an Expect: line. A release needs this. -->
