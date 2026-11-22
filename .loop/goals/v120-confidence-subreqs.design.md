# Design: v120-confidence-subreqs (#5790, TD940)

## Problem
`sections.confidence(row, tests, runs)` counts only regression rows whose requirement column equals a feature ID exactly, keeps only PASS and FAIL, and drops KNOWN. A row keyed `DEL-3.1` never counts, a sub-requirement with no row never lowers the score, and a KNOWN row vanishes, so DEL-3 reads "100% (11 of 11)" with ten untested sub-requirements. `render.py` prints "not enforced" only for a feature with no passing row at all.

## Approaches
A. Widen the match in `confidence()`: a row counts when its requirement equals the ID or `ID.<n>`; KNOWN joins the denominator as not passing; each declared sub-requirement with no PASS row adds one to the denominator and is named in the cell ("67% (2 of 3; untested DEL-3.4)"). Declared sub-requirements are the `- ID.n:` bullets on the feature's page (the page the principle row links to). Cost: small, in sections.py (11,774 bytes, 7k of room). Risk: the page read is new; the cell text gets longer.
B. Change render.py to print an untested list per feature. Cost: render.py is already 19,162 bytes (over 19,000), so any growth breaks done line 4. Rejected.

## Chosen: A
All logic in sections.py (a helper `subs(page, ID)` and the widened `confidence`). render.py, the 20,480 cap and the 19,000 line are untouched: no file newly crosses either. The untested name sits in the Confidence cell, which the render already prints, so done line 2's "named in the render" holds.

## Done lines
1. Sub-row counting plus KNOWN-as-not-passing: widened match and denominator; toy rows for DEL-3.n and KNOWN.
2. One untested sub-requirement: score < 100% always (denominator +1, numerator +0) and the ID is named; negative control row with one untested sub-requirement never shows 100%.
3. No subs and no KNOWN: the same arithmetic and the same string as today; toy compares old and new over every current feature (the existing test-follows-adoption checks stay as they are).
4. Whole change: docs check, package check, private scan; a regression row for each new behaviour, each proven red with `regression.py red --break`; the PR lists every feature score that moves, produced by rendering before and after over main's rows.

## Open questions
- Where sub-requirements are declared. Recommended: `- ID.n:` bullets on the feature page named by the principle row's link. DEL-3.1 to 3.10 are not on main yet (v120-del3-text); until that merges only rows keyed `ID.n` count, and no score moves for a feature that has neither.
- A row keyed to a sub-requirement of an ID the page does not declare still counts toward the feature (it is evidence); it is never named untested.
