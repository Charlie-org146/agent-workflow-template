# docs-sync-milestone: design

## Problem

`docs.py sync` files each new PRD delta as a GitHub issue with `--milestone <page>`, the bare page name (`prdcopy.py`). Since the backlog-milestones goal the standing milestone for a page is `Backlog: <page>`; the bare name is a delivery milestone (or absent), so delta issues land in the wrong place or fail to attach (#4695).

## Approaches

1. Change the string to `"Backlog: " + page` and rely on it existing. Cheapest, but gh refuses an unknown milestone and the issue then falls back to none, so on a repo that has not run `milestone.py backlog --live` the delta has no home.
2. Add `milestones.backlog(page)`, which lists the repo's milestones (`repo_side`, state=all) and creates `Backlog: <page>` when missing, once per run; `prdcopy.sync` passes its result to `--milestone`, and falls back to no milestone only when gh can neither list nor create it. Small cost: one list call and at most one create call per page per run, only when a delta issue is opened.

## Chosen

Approach 2. It keeps the done lines true on any repo and reuses the milestone listing already in `milestones.py`. The bare page name is never passed, whether or not a milestone of that name exists. The milestone-sync delta issues (milestones.py) are about milestones, not a page, and are unchanged.

## Done lines

1. Lands on `Backlog: <page>`, created if missing: `backlog()` and the `--milestone` argument; test `a delta issue lands on the milestone Backlog: Sensor, created first when it is missing` (fake gh logs the POST before the issue create).
2. Bare name never used: test seeds a bare `Sensor` milestone and asserts no `--milestone Sensor` and no `title=Sensor` call.

Regression: the existing `sync-delta-posted` row is widened to the three PASS lines (no row added: the table is at its cap). Red proof: the three new checks fail on the old `prdcopy.py`.

## Open questions

None. The reviewed DOC-17 wording says "the feature's milestone"; it is left as written (changing it needs the owner's review).
