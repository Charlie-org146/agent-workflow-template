# Plan: merge-batch-on

## Build steps

1. `.loop/config.json`: add `"merge_batch": true` after `max_merge_rounds` (done; the setting exists in `skills/workflow-setup/scripts/settings.py`, default false, and `skills/workflow-release/scripts/merge.py:273` reads it for the `--batch` refusal).
2. Regenerate the renders: `entry.py write` (START.md settings table) and `docs.py audit` (wiki Home settings block). Done.
3. Add one regression row `merge-batch-config-on` (goal REL-13, level land) that asserts the config line, seen red with `red --break` setting it false.

## Tests

- Done line 1 (merge.py stops refusing): the config row `merge-batch-config-on` plus the existing `merge-batch-split` row for the `--batch` path itself; the refusal at merge.py:273 only fires when the setting is false.
- Done line 2 (settings show, START.md, Home render): the same row also checks `settings.py show`; `entry.py write` and `docs.py audit` print no FIXED line on rerun.

## What could break

`merge.py` merges 2-3 goals as one with `--batch`; a failing batch splits to name the culprit (row `merge-batch-split`). The rows table is at 1299 of 1300, so exactly one row is added and none more.

## Out of scope

Any change to merge.py or the batch logic; a flow setting; other settings.

PENDING: none
