# how-to-use-docs design

Problem: usage text for each feature sits in the README and, for runbooks and deployments, in feature pages; the owner wants one How-to-use page per feature, from the user's side.

Approaches:
1. Enforce the page in docs.py/deployments.py: a feature page needs docs/wiki/How-to-use-<Feature>.md on a fixed skeleton, mapped to its feature with no docs.tsv row, orphans reported; move the README tables onto the pages. Low risk, additive; README keeps DOC-5's minimum (intro line, table of at least one row).
2. Change DOC-4/DOC-5 so the README drops the tables. Breaks every repo that follows the current README format, including thermis. Rejected.

Chosen: 1. Runbook sections that the docs check keeps in step with routines (Health, Regression) stay in their feature pages and the How-to-use page points to them.

Each done line: 1 needs DOC-18, the check and negative controls (dev/toy/test-how-to-use.py); 2 needs the eight pages, the link line and the README links.

Open questions: none for the owner beyond the owner's later review of DOC-18's wording.
