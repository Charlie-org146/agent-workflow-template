# Plan: results-render

## Build steps

Each name below exists on main (checked): `lanekit.prep`, `lanekit.mend`, `lanekit.BOOKKEEPING`/`FILES`, `role.record`, `role.results`, `lanes_cli.merge_runs`, `render.refresh`/`generated`/`tests_page`, `autorelease.push_release_commit`/`STAMPS`.

1. `render.py`: add `fold(root)`: read `.loop/lane-results/*.tsv`, keep per row id the entry with the greatest (date, head, flaky), write the union into `.loop/regression-runs.tsv` in sorted id order, delete the fragments; `pending(root)` is true while any fragment exists. `generated`/`tests_page` check and `refresh` treat the Tests tables as the release's job while `pending`.
2. `lanes_cli.py`: `merge_runs` writes `.loop/lane-results/<slug>.tsv` (slug from branch `loop/<slug>`, else the short head), no row lock, no runs.tsv; docstring trimmed by about 1,000 bytes; file ends at or under 19,000.
3. `lanekit.py`: `prep` drops `criteria.py render --tables` and the runs.tsv commit path; `BOOKKEEPING`/`FILES` name `.loop/lane-results/`; `mend` drops its Tests.md and runs.tsv union branches; file ends at or under 19,000.
4. `role.py` (not in the goal's touches; asked operation-pc): `record` stops rendering the tables; commits the fragment with issues.tsv; trimmed under 19,000.
5. `autorelease.py`: `push_release_commit` runs `fold`, the Tests render, `entry.py write` and the front-page blocks in the release worktree before the commit, adds them to the files committed; `STAMPS` allows `.loop/lane-results/`; the file does not grow (trim to pay). `wiki.py`: `rerender` stays; only trimmed if touched.
6. `dev/toy/test-lanes.sh`: add a toy that builds three fragments and three edits of one page, merges the branches in all six orders, runs the fold and the render, compares the six trees byte for byte, and runs docs.py check on the result. It extends an existing row's assertion, so net regression rows are 0.

## Tests

- Done line 1: the six-order toy above, seen red by `regression.py red <row> --break` (make the fold order-dependent).
- Done line 2: the same toy: after the release step no fragment remains, runs.tsv holds all three, `docs.py check` passes.
- Done line 3: byte counts of each touched script against main and 19,000 (printed by the toy's last step), `regression.tsv` row count equal to main's, no change under `docs/wiki` requirement text.

## What could break

Many toys assert today's behaviour: lanes that re-render Tests pages or append runs.tsv (test-flaky.sh, test-lane-control.sh, test-merge-guard.sh, test-release.sh, test-summary.sh, test-runs-column.sh, test-reopened.sh, test-suite-time.sh, others that name regression-runs.tsv). They are bash toys that skip on Windows, so only CI shows them; each affected one is updated in the same change if it fails. The docs check on a PR head with a pending fragment must still fail a hand-edited Tests table; the toy covers a hand edit once no fragment is pending.

## Out of scope

kept-fragments (the page stamps, pc-w2); any change to requirement text; the health scripts; a new shipped file.

PENDING: none
