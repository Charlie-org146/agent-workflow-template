# regression-trust, v1.0.0 group 3: the regression lanes and rows can be trusted: #3908, #3907, #3911 and #531 are each fixed with a toy or row seen red, or closed with proof that they are already fixed

- Slug: regression-trust
- Touches: skills/workflow-regression/ skills/workflow-delivery/

## Done lines

Frozen. A wrong done line needs a new goal.

1. #3911: a regression row that ends in grep -q no longer hides a failing toy's output, so the lane shows the failure's text, not a bare FAIL, and a row or toy proves it (seen red)
2. #531: after a base merge into a goal branch, the goal's own new and changed rows run first in the qa, ship and pr lanes, before reach rows, shown by a toy or row seen red
3. #3908 and #3907: each is fixed with a toy or row seen red, or closed with proof it is already fixed; any closure carries the proof
4. every new row or toy uses shell-neutral commands, and a lane starts only at 3.0 GB or more of free commit memory; a reviewed page's wording change is drafted and sent to operation, never edited

## Verify by hand

<!-- Numbered steps for a person, each with an Expect: line. A release needs this. -->
1. Run `python3 dev/toy/test-lane-order.py`, `python3 dev/toy/test-lane-fail-text.py` and `python3 dev/toy/test-owed-close.py`. Expect: every line starts with PASS and each exits 0.
2. Read the SELECTED lines at the top of a lane log after a base merge. Expect: rows marked `new row` come before the rows marked `reaches`.
3. Run a lane with a failing row that ends in `| grep -q` (for example the toy's). Expect: the row's own text appears under its FAIL line, not a bare FAIL.
