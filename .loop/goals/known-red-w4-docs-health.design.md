# Design: known-red-w4-docs-health

## Problem

Eleven regression rows fail on main's full run (44463859531). Each toy test was written against an older docs or health contract, and the product moved on: DOC-18/19 now ask every feature page for a How-to-use page with a System diagram, Home has a diagram block, a routine needs declared permissions, `criteria_trouble` returns `(unmet, left)`, `ORDER` gained a `repo` group, size findings under the limit are WARNs, and CI has no git author and sets GITHUB_ACTIONS.

## Approaches

1. Fix each toy fixture to meet the current contract (tests change, product stays). Low risk, one product fix where the product itself is wrong (the lane prep commit fails without a git author).
2. Remove the rows. Refused: the behaviours still exist and no waiver is allowed.

## Chosen

Approach 1. Product change: `lanekit.prep` commits with a fallback author when git has none. Row stale-groups-defect keeps its guard for Milestones and the old name, and no longer forbids a Release page (Release is a feature again); its description says so.

## Per done line

- Line 1: each of the 11 rows passes in the CI full-suite shards on the PR head. `no-milestone-issue-ok` needs health scripts under 19,000 bytes, which is known-red-w8-size's `scripts-c-health-under-19000`; it goes green once that merges into main and main is merged here.
- Line 2: no row added to regression-known.tsv; net rows 0 (one description changed, none added or removed).

## Open questions

None for the owner.
