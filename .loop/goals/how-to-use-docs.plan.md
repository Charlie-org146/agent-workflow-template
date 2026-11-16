# how-to-use-docs plan

Checked against the code: docs.py (problems, contract, publish), deployments.py, prd.py (review_of), counting.read_map exist.

Build steps
1. deployments.py: mapped() and howto(); docs.py uses them in problems, contract and publish; prd.py tolerates the link line.
2. DOC-18 on the Documentation page (Unreviewed; page unreviewed under owner record o62).
3. Eight How-to-use pages, link lines on the feature pages, README sections shortened with links, Home row edit.
4. dev/toy/test-how-to-use.py and four regression rows.

Tests per done line: 1 the toy test (a negative control for a missing page, an orphan, a wrong title, a section off the skeleton, an unlinked page) and docs check; 2 docs check on this repo.

What could break: repos whose wiki already has How-to-use-* pages with no matching feature (reported as orphans); thermis' Mac pages follow the same skeleton.

Out of scope: dropping the README tables (DOC-5); moving machine-checked Runbooks.

PENDING: none
