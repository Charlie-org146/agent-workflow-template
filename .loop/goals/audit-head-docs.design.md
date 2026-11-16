# Design: audit-head-docs

Problem: merge.py audits a PR head's pages with the main checkout's docs scripts. A goal that changes a rendered setting (max_merge_rounds 3 to 8) or the Review stamp format is refused, because main's old render and parser judge the head's new pages. #4340 fixed this for START.md only.

Approaches:
1. Judge the head with its own docs.py when its tree has one (chosen): wiki.pending points release.DOCS and its own check at the head tree's docs.py, restoring after. Cost: about 10 lines in wiki.py. Risk: a head with a broken docs.py refuses itself, which is right.
2. Bypass the check for goals that touch docs scripts. Rejected: operation will not bypass checks.

Done lines: the toy `test-audit-head-docs.py` has three cases (own docs.py passing, own docs.py refusing, no own docs.py falls back to main's); the first is red on the old code. wiki.py stays at 19,004 bytes, 12 over main and under the 400 growth limit; no file over 19,000 grows.

Open questions: none.
