# Plan: DEL-16 on the Delivery page

Checked against the code: `skills/workflow-docs/scripts/criteria.py` (unreview, render, --owner-record), `skills/workflow-regression/scripts/regression.py` (add, red), `skills/workflow-delivery/scripts/routing.py` and `dev/toy/test-agent-routing.py` (the feature's own test), `.loop/regression.tsv` (row `agent-routing`, line 1204) and `.loop/owner-words` record o139 (covers del-16, DEL-16, Delivery) all exist. Delivery.md has 15 requirements; criteria_max is 19.

## Build steps
1. `criteria.py unreview Delivery --user --owner-record o139`: Delivery's Review line becomes Unreviewed; no other requirement changes.
2. Add DEL-16 after DEL-15 in `docs/wiki/Delivery.md`, `**Unreviewed**`, wording and three sub-bullets exactly as in commit d33bd506.
3. In `.loop/regression.tsv`: change the `agent-routing` row's goal from `agent-routing:1` to `DEL-16`; add a `covered` row `done-agent-routing-1` for `agent-routing:1`, naming the `agent-routing` row; add two small rows for this goal's done lines (`regression.py add`, `red` against main).
4. `criteria.py render --tables` from committed data only, then `docs.py check`.
5. Fill Verify by hand, commit.

## Tests per done line
- Done line 1: row `del-16-on-page` greps the page for `DEL-16: **Unreviewed**` and for the Unreviewed Review line; seen failing on main (no DEL-16 there) and passing now.
- Done line 2: row `del-16-linked` checks `.loop/regression.tsv` links the `agent-routing` row to DEL-16 and keeps the covered `done-agent-routing-1` row; seen failing on main, passing now. `workflow-docs check` is run and its result reported.

## What could break
Un-reviewing Delivery makes health/consistency flag an Unreviewed page until the owner stamps; that is intended. A render could rewrite pages it only measures; only `--tables` is used. Known red rows on main stay red and are reported.

## Out of scope
Rewording DEL-16, stamping any review, new routing code, other pages.

No decisions left for the owner except the review stamp, which stays theirs.
