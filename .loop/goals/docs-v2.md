# docs-v2: the wiki and skill docs stand alone with a system diagram per How-to-use page and on Home, and the How-to-use rules of #4657, #4666, #4677, #4698 and #4632 are met and enforced by docs check (#4784)

- Slug: docs-v2
- Touches: docs/wiki, skills/workflow-docs, skills/loop-files.md, dev/toy, .loop/regression.tsv, DECISIONS.md
- ETA: 275 active minutes (estimate 219m plus a 25% margin)

## Done lines

Frozen. A wrong done line needs a new goal.

1. #4784: Given the wiki pages and skill docs, when docs check runs, then it fails naming the page and the item for an external link, a foreign owner/repo reference or a machine path outside a Deployments table, and for a Home page without the whole-system diagram; it passes on this repo, whose Home shows the system diagram and whose every feature shows its diagram on its How-to-use page
2. #4698: Given a How-to-use page whose System diagram misses a delivered row or names a part its table lacks, when docs check runs, then it fails naming the part, and a diagram with one box per row, a legend and where each part runs passes; every How-to-use page here passes, and DOC-19 states the rule with a test row, reworded as Unreviewed
3. #4677: Given a feature page that names a skill, command or schedule its How-to-use page does not list, when docs check runs, then it fails naming it, and it passes once listed; the Kind blocks, one file per feature and links-only README already enforced on main stay green, each with its existing test row
4. #4657: Given a feature page whose How-to-use page lacks an item for a functional requirement ID, or names an unknown ID, when docs check runs, then it fails naming the ID; every feature page here passes; shown by the existing doc19 test rows passing and docs check clean
5. #4666: Given a How-to-use page with plain When X, do Y runbook steps and no scheduled routine, when docs check runs, then it passes, and a page naming a scheduled routine without the seven DOC-16 fields still fails; shown by passing test rows for both
6. #4632: Given a pushed branch whose only STALE lines are generated blocks differing from a fresh render, when operate.py apply runs, then merge.py accepts it with no worker step, and a hand edit inside a generated block is still refused; shown by the existing apply-rerender test rows passing

## Verify by hand

<!-- Numbered steps for a person, each with an Expect: line. A release needs this. -->

1. Run `python3 skills/workflow-docs/scripts/docs.py check` from the repo root.
   Expect: it prints DOCS OK and no LINKS, HOME or HOWTO line.
2. Open `docs/wiki/How-to-use-Health.md` and find its System diagram under What's delivered.
   Expect: one box per row of the table, each saying where it runs, the flows between them and a Legend line.
3. Delete one box from that diagram and run `docs.py check` again.
   Expect: it fails naming that part (DOC-19); restore the box.
4. Open `docs/wiki/Home.md`.
   Expect: a System diagram under the features table shows the operation session, workers and steps, staging and production (planned), machines, routines, a legend and guard marks.
5. Put an issue link into any wiki page outside its Tests section and run `docs.py check`.
   Expect: a LINKS line names the page, the line and the link; remove the link.
