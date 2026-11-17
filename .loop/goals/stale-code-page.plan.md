# stale-code-page plan

Checked: audit.relock(root, slug, only) already re-stamps a Reviewed page whose reviewed text is unchanged (`slug and not moved`) and a How-to-use page by a kept marker; operate.apply lists pages from `docs.py check --own`. lanekit.prep already commits generated page changes before the rows run. Sizes: audit.py 16.8k, lanekit.py 19.1k (hard cap 20,480).

## Build steps
1. audit.py: `restamp_own(root, slug)` lists the STALE pages of `docs.py check --own origin/BASE` and relocks them; relock stamps an Unreviewed page with a kept marker while the page is as committed; CLI `audit.py restamp-own SLUG`.
2. lanekit.prep: run `restamp-own` with the branch's slug after the Tests tables render, so the pages ride in the prep commit.
3. Toy test-stale-code-page.py (Reviewed, Unreviewed, wording-changed negative control) and rows stale-code-page-reviewed, -unreviewed, -wording, each seen red; command reference line.

## Test per done line
Done 1: the toy's first four checks (page stale before, re-stamped in the prep commit, fresh and clean after). Done 2: the negative control.

## What could break
A prep that stamps a page with moved wording (relock refuses: `not moved`); a prep that fails on a missing origin/BASE ref (the subprocess output is ignored, nothing re-stamped); lanekit.py size.

## Out of scope
operate.py apply and merge.py's own re-stamp, which stay as they are.

PENDING: none
