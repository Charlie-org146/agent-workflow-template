# Part 0a of the merge queue (TD231): the per-page Review stamp <!-- kept GOAL@SHA --> and the How-to kept lines leave the shared wiki pages; each goal records its kept stamps in its own .loop/kept/<slug>.tsv, and docs freshness reads them (towncrier fragments)

- Slug: kept-fragments
- Touches: skills/workflow-docs/scripts/audit.py, skills/workflow-docs/scripts/docs.py, skills/workflow-docs/scripts/criteria.py, .loop/kept/, dev/toy/test-docs.sh, .loop/regression.tsv
- ETA: 250 active minutes (estimate 200m plus a 25% margin)

## Done lines

Frozen. A wrong done line needs a new goal.

1. Given three fixture branches that each re-stamp the same wiki page, when they merge in any order, then no merge conflicts on any page and docs.py check gives the same freshness result whichever order
2. Given docs.py check on a page with its stamp in .loop/kept/ and none on the page, then it reports the page fresh, and a page whose kept fragment is missing is STALE (negative control)
3. Given this goal's diff, then no shipped file is added, no touched script is over 19,000 bytes or larger than on main (trim to pay), net regression rows are 0, and no requirement text changes

## Verify by hand

<!-- Numbered steps for a person, each with an Expect: line. A release needs this. -->
