# howto-per-requirement plan

Checked against the code: deployments.howto, milestones.py (new howto_items), criteria.py line ~264 and docs/wiki/*.md exist.

Build steps
1. milestones.howto_items checks the items; deployments.howto calls it for non-link pages; deployments.howto_runbook replaces the criteria.py runbook branch (#4666).
2. Generate the items for all eight pages; DOC-19 on the Documentation page, Unreviewed.
3. Toy checks in dev/toy/test-how-to-use.py and three regression rows (doc19-*).

Tests per done line: 1 doc19-item-missing and doc19-item-unknown; 2 docs.py check; 3 the doc19 rows and the page text.

What could break: other repos' How-to-use pages must add items; criteria.py and prd.py stay at or under their main sizes (criteria 19096 vs 19118, prd unchanged).

Out of scope: marking anything Reviewed.

PENDING: none
