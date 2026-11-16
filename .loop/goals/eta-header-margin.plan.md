# Plan: eta-header-margin

Claims checked against the code: `bs.release_header(release, items, at)` (board_status.py) builds the header from each item's `left`; checkin.py builds the items
at the Dependencies block from `bs.left_time` and calls it through `grouped`; `auto.eta_minutes/eta_open/eta_start/eta_spent/eta_seen` hold the hard-ETA arithmetic
(eta_open and eta_start came with eta-preflight); `auto.ETA_MARGIN` is read only by `eta_new` and by test-hard-eta.py; settings.py's table is rendered into Home;
`fit.frozen_fields` calls `eta_new`. LF sizes: checkin 20,090 (cap 20,480), auto 19,519, board_status 17,766, settings 18,988, fit 18,701.

## Steps
1. auto.py: drop the constant; add `eta_margin(cfg)` (percent 0 to 300, default 25, bad values read as 25) and `eta_left(seen, at)`; `eta_new(..., cfg=None)` uses the margin and names the percent in its basis.
2. fit.py: `frozen_fields` passes `g.config()`.
3. settings.py: row `eta_margin_percent` (repo, 25).
4. checkin.py: each started goal's item gets `hard=auto.eta_left(auto.eta_seen(g["root"], r), at)`.
5. board_status.py: `release_header` takes the latest of the hard values, falls back to `left` per goal with no hard ETA, and appends `; hard ETA for N, estimate for M` only when a hard value was used.
6. test-hard-eta.py's constant check becomes the default-margin check; toy dev/toy/test-eta-header-margin.py renders `checkin.render` for both done lines; rows seen red.
7. Docs: `docs.py audit` re-renders Home's settings table and the Tests tables; re-stamp pages changed only by code; commands.md/operation docs mention the setting where the ETA is described.

## Tests
- Done 1: a board with one goal at a hard ETA (frozen, 60 min) and one estimated goal (no ETA): the header takes the later of the two and says "hard ETA for 1, estimate for 1"; negative controls: no hard ETA reads as today, a goal with open pre-flight items counts as estimated.
- Done 2: 40 percent moves a goal's hard ETA (estimate x 1.4), the default gives today's value, a nonsense value falls back to 25.

## What could break
test-checkin-view.py asserts the exact header counts (no hard ETA: unchanged text); eta_new callers pass no cfg (default 25); checkin.py stays under 20,480 bytes; the Home settings table must be re-rendered (settings-render-fresh).

## Out of scope
Showing a goal's hard ETA in the board page or the dashboard; per-release ETA settings.
