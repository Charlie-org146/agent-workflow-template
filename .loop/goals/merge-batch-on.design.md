# Design: merge-batch-on

## Problem
merge.py refuses two or three ready goals with "several goals need --batch and merge_batch true" because the template's `.loop/config.json` leaves `merge_batch` at its default, false. The owner said "turn on merge_batch for the template" (record o256).

## Approaches
1. Set `"merge_batch": true` in `.loop/config.json`, then regenerate START.md and the wiki Home settings block. Cost: one config line plus two generated renders. Risk: low; `--batch` is still opt-in per merge, and the setting only permits it.
2. Leave the config and pass an override at merge time. Cost: every merge needs the override. Risk: the next operator hits the same refusal. Rejected.

## Chosen
Approach 1: it is what the owner asked for, and the setting is repo-level by design.

## Done lines
1. merge.py with `--batch` on 2-3 goals stops refusing once `merge_batch` is true in the config on main; the config line gives that.
2. `settings.py show` lists merge_batch true (layer repo); START.md and the wiki Home settings block render it (both regenerated, docs audit OK).

## Open questions
None.
