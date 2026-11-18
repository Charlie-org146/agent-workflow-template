# merge.py's wiki gate refuses only on pages the goal changed and on stale generated tables; DOC-19/DOC-4 findings on untouched pages become filed issues, and a repo's own published sites count as inside the repo

- Slug: docs-gate-scope
- Touches: skills/workflow-release/scripts/merge.py, skills/workflow-release/scripts/wiki.py, skills/workflow-docs/scripts/milestones.py, docs/wiki/Release.md, docs/wiki/Documentation.md, docs/wiki/Tests.md, .loop/regression.tsv
- ETA: 235 active minutes (estimate 186m plus a 25% margin)

## Done lines

Frozen. A wrong done line needs a new goal.

1. Given a goal whose diff changes no wiki page while other pages in the repo carry DOC-19 or DOC-4 findings, when merge.py runs, then it does not refuse on those findings and files one issue per untouched page on that feature's backlog milestone, with no second issue while one is open; a finding on a page the goal changed, or a stale generated block or table (Tests tables, START.md), is still refused.
2. Given a page that links to one of the repo's own published sites (listed in scripts/public-origins.json or a config setting naming them) or to its own README, when docs check runs, then that link is not a LINKS finding; every other outside link still is, and this template's own pages stay clean.
3. Each new rule has a test row seen failing and passing, the Release and Documentation pages state the rules with the new wording going to the owner for review, wiki.py prepare is clean and entry.py check prints ENTRY OK.
4. No script crosses 20,480 bytes and none crosses 19,000 from under it on main except where o39 allows; if milestones.py needs room, trim it in the same goal without changing behaviour.

## Verify by hand

<!-- Numbered steps for a person, each with an Expect: line. A release needs this. -->
