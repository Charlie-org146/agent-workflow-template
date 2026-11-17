# Plan: row-cap-1300

Built against the design (approach 1).

## Claims checked
- `.loop/config.json` sets no `max_regression_rows`; the default 1200 lives in settings.py:61, lean.py:138 and role.py:261 (`cfg.get(key, default)`), so a config key overrides it for this repo only.
- `entry.py write` (workflow-docs) regenerates `.loop/START.md`; `criteria.py render` regenerates the Settings blocks on Home.md and README.md, marking a setting overridden when it differs from the default.

## Build steps
1. Add `"max_regression_rows": 1300` to `.loop/config.json`.
2. Run `entry.py write` and `criteria.py render` (after dropping the lane memory floor edit, restoring it after).
3. Commit config.json, START.md, README.md, Home.md. Nothing else changes.

## Test for the done line
No new regression row: the table is over its 1200 cap on main and TEST_CAPS reads origin/main's config, so a row added here would be refused at qa (net +1). The done line is proved instead by commands that fail on main and pass on the branch: `docs.py audit` (no STALE Settings / START), a grep that START.md, README.md and Home.md show 1300, and `role.py` over_caps reading the branch config as 1300.

## What could break
- A stale render: audit would print STALE; rerun render.
- Nothing reads the key as a string; the value is an int like `max_suite_seconds`.

## Out of scope
Changing the built-in default (settings.py, lean.py, role.py), other settings, token-diet's own changes.
