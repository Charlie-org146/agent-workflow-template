# home-stale plan

Checked against the code: `docs.py problems()` (the per-page loop and `netless`), `render.refresh`/`front`/`repo_of`/`topics_of`, `pageformat.home` (DOC-4), `counting.config_of` (read by `render.settings_block`, `template_line`, `counting.entries`, `deployments.topics_of`, `milestones`) all exist.

## Build steps
1. `render.home_fresh(root, names)`: Home exists, `refresh(root, True)` lists no Home.md block, and `pageformat.home` finds no DOC-4 trouble.
2. `docs.py problems()`: after the UNWRITTEN check, `continue` for Home when `home_fresh`.
3. `counting.config_of`: read `HEAD:.loop/config.json` when `git ls-files -v` marks it `S` (skip-worktree).
4. Toy `dev/toy/test-home-stale.sh` (clears, control, kept) and three rows: home-stale-clears, home-stale-control (DOC-4), home-kept-config (DOC-15); each proved red with `regression.py red --break`. Done lines covered by done-home-stale-1 and -2.
5. Re-render the Documentation and Tests tables; DECISIONS entry.

## Tests per done line
1. clears + control: with the fix removed (`red --break`) the README/config case reports STALE Home; with `home_fresh` always true the control fails.
2. The toy itself, with DOC-4 asserted on the generated Home; kept-config row proves the guard and its control.

## What could break
Hand-written Home text: DOC-4 already refuses any line outside the features table, so `home_fresh` is false for it. A repo with a skip-worktree config now renders from HEAD (the intended change). `docs.py` and `counting.py` stay under the 20,480 byte cap.

## Out of scope
A kept stamp on Home, `audit.py restamp` changes, and Home rows for other generated pages.
