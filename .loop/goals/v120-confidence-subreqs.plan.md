# Plan: v120-confidence-subreqs

Budget: 4 build units, one lane. No file may newly cross 19,000 bytes or 20,480; sections.py has room, render.py is untouched. No comment or docstring trimming (GRD-20); if sections.py would near 19,000, move helpers out instead and stop to report.

1. sections.py: add `subs(page, fid)` (IDs `fid.<n>` from `- fid.n:` bullets) and `rows_for(ids, tests)`; widen `confidence()` so rows keyed `ID` or `ID.n` count, KNOWN counts as not passing, and each declared sub-requirement without a PASS row adds one to the denominator and is named: "NN% (P of T; untested ID.n, ID.m)". A feature with no subs and no KNOWN returns the exact old string. `fresh()` reads the linked page through its `read` to pass the declared set (`tables(..., pages)`), a missing page means no subs.
2. dev/toy/test-confidence-subreqs.py (windows: ok): fixtures for sub rows counting, KNOWN not passing, one untested sub never 100% (negative control: remove the untested declaration, it reaches 100%), no-subs identical to the old string, a row for an undeclared sub still counts. The existing test-follows-adoption stays green.
3. .loop/regression.tsv: rows for done lines 1, 2, 3 (land), each with `--break` proven red; net rows are the new behaviours only, no existing row changes result.
4. Docs: Principles/Regression wording of Confidence, README line if it describes the score, re-render, `docs.py check`. The PR body lists every feature score moved, from a before/after render over main's regression.tsv.

Gates before push: private.py scan, package check, byte counts of every touched script against 19,000.
