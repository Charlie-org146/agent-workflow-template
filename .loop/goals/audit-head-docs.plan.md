# Plan: audit-head-docs

Steps (built):
1. skills/workflow-release/scripts/wiki.py, function pending: choose the head tree's skills/workflow-docs/scripts/docs.py when the head is not HEAD and the file exists, else DOCS; set release.DOCS to it around release.docs_trouble and use it for check --own; restore in the finally block. Docstring trims keep the file at 19,004 bytes.
2. dev/toy/test-audit-head-docs.py: branches own-ok, own-bad, no-own; seen red on the old wiki.py (case 1 fails), green on the new.
3. .loop/regression.tsv row audit-head-judges-own-docs (DEL-5); render the Tests tables.

Test per done line: the row above. What could break: a head whose own docs.py is broken refuses itself, which is wanted; the toy test-audit-pr-head still passes. Out of scope: other checks of merge.py. PENDING: none.
