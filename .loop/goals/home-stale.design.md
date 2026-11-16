# home-stale design

## Problem
A repo whose `.loop/docs.tsv` maps code paths (README.md, a script, `.loop/config.json`) to Home sees `docs.py check` call Home STALE whenever a goal changes one of them, and nothing a goal can do clears it: Home is fully generated, so a fresh render writes no change; `audit.py restamp` skips Home (no Review line); a kept stamp fails DOC-4. `merge.py` then refuses every such goal (#4608). Separately, `wiki.py prepare` and `criteria.py render` read the worktree's `.loop/config.json`, so a value kept locally with `git update-index --skip-worktree` ends up in committed Home and README blocks.

## Approaches
1. **Home is fresh when its render is unchanged** (chosen). In `docs.py problems()`, skip the commit-count staleness for Home when `render.home_fresh` says its generated blocks match a fresh render and it passes DOC-4. Cost: one small function in render.py, two lines in docs.py. Risk: a DOC-4 Home holds only generated text (the features table is checked by DOC-4 itself), so nothing hand-written can go stale unseen; a Home unlike its render still fails.
2. A kept stamp on Home that `restamp` writes. Cost: DOC-4 must accept a stamp line on Home, `audit.py` must stamp a page without a Review line, and every mapped-path change needs the restamp. Risk: a new line on Home and a step to forget.

For the kept config: read a skip-worktree `.loop/config.json` as committed at HEAD in `counting.config_of`, the one reader every generated block uses. Rejected: refusing when it differs (blocks the goal for a value the owner meant to keep local).

## What each done line needs
1. A fixture repo whose Home maps README.md and `.loop/config.json`: changing either with Home's render unchanged leaves no STALE Home; a Home unlike its render still fails (rows home-stale-clears, home-stale-control).
2. The toy `dev/toy/test-home-stale.sh` runs it, shows DOC-4 passing, and also covers the kept-config guard with a control (home-kept-config).

## Open questions
None for the owner. Home in this repo already maps README.md, FINDINGS.md and DECISIONS.md, so this change dogfoods the fix.
