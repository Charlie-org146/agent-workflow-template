# Regression, Automation, Documentation and Integrations carry the v2 rewrite text through the revision tooling, each requirement on the page it belongs to

- Slug: regroup-regression
- Touches: docs/wiki/Regression.md, docs/wiki/Automation.md, docs/wiki/Documentation.md, docs/wiki/Integrations.md, docs/wiki/Home.md, docs/wiki/Tests.md, .loop/regression.tsv
- ETA: 230 active minutes (estimate 182m plus a 25% margin)

## Done lines

Frozen. A wrong done line needs a new goal.

1. Given the Regression, Automation, Documentation and Integrations pages, when this goal merges, then every requirement in those four sections of prd-rewrite-to-10.md (Regression 16, Automation 9, Documentation 19, Integrations 8) has that text on its page as a new revision through the revision tooling from prd-revisions, with the new Integrations page added and every requirement that moves between pages retired on its old page as moved to its new ID; DOC-15, DOC-18 and DOC-23 are left to prd-principles, and no requirement outside these four features changes.
2. Given a moved or renumbered requirement, when the docs and health checks run, then every test row, issue link and How-to item that cited its old ID points at the new ID, the old ID still resolves through its moved-to marker, and Home lists the four pages with their milestones and Topic as before.
3. Given this goal's branch, when its lane and checks run, then the Tests tables re-render with zero regression rows added net, each new rule has a row seen failing and passing, wiki.py prepare is clean and entry.py check prints ENTRY OK.
4. Given this goal's diff, when it is compared with main, then no shipped file is added, no script crosses a size line it was under on main, and no page other than these four, Home and the Tests page changes.

## Verify by hand

<!-- Numbered steps for a person, each with an Expect: line. A release needs this. -->
