# Design: row-cap-1300

## Problem
The regression table holds 1,205 rows against a `max_regression_rows` cap of 1,200 (the built-in default; `.loop/config.json` sets no override). A goal that adds rows is refused at qa (TEST_CAPS), which blocks token-diet and every goal that adds rows. The owner approved 1300 (owner records o118, o119).

## Approaches
1. Add `"max_regression_rows": 1300` to `.loop/config.json` (this repo's override) and regenerate the three tables the config feeds (START.md, README.md, wiki Home.md). Cost: one key plus regenerated tables. Risk: none to other repos; the template default stays 1200.
2. Change the built-in default (settings.py, lean.py, role.py, two docs) to 1300. Cost: six files and a default change for every adopting repo. Risk: widens scope beyond this repo's need; the owner approved only this repo's cap.

## Chosen
Approach 1: the smallest change that meets the goal, and what the owner approved.

## What the done line needs
- `.loop/config.json` holds `max_regression_rows: 1300`, so `goal.py` TEST_CAPS reads 1300 from main once merged.
- `entry.py write` regenerates START.md; `docs.py render` regenerates README.md and Home.md settings tables, showing 1300 (Home marks it overridden).

## Open questions
None.
