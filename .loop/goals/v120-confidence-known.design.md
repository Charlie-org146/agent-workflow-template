# Design: v120-confidence-known (#5790 first half, TD945)

## Problem
`sections.confidence(row, tests, runs)` keeps only PASS and FAIL from the latest run, so a row whose real state is KNOWN (a failing row listed in regression-known.tsv) drops out of both the passing count and the total. A feature with a known-failing row therefore reads higher than it is. The sub-requirement half of #5790 moved to v120-del3-text (TD945).

## Approaches
A. In `confidence()` keep KNOWN as well as PASS and FAIL; KNOWN enters the total and never the passing count. Real states only, from `latest_full`: a row that passes, was SKIPPED or never ran is unchanged. Cost: one filter tuple in sections.py (11,575 LF bytes); format, keep regex and signatures untouched. Risk: scores of features with real KNOWN rows drop (intended; listed in the PR).
B. Overlay regression-known.tsv onto runs. Rejected: actions.py and runs.py mark KNOWN only when a row exits non-zero, so an overlay would turn passing and never-run known ids into not-passing (the Mac's gate-1 B2).

## Chosen: A
render.py (18,737 LF bytes) untouched; no file crosses 19,000 or 20,480.

## Done lines
1. KNOWN counts as not passing, in the total only: toy cases C1 to C3, C5; one regression row with a negative control (break: filter back to PASS/FAIL).
2. No KNOWN row: exact old strings; C4 and the keep-mode round trip C6; test-follows-adoption stays green.
3. Whole change: docs check, package check, private scan, one row (REG-4: one row per script and requirement), LF byte counts, and the PR lists every moved score from a main-vs-worktree run over the same input (expected REG-4 and SET-10); no cell is re-rendered, the next live render settles them.

## Open questions
None for the owner. Out of scope: sub-requirements (v120-del3-text).
