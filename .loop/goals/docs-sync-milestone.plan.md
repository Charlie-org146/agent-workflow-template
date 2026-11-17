# docs-sync-milestone: plan

Checked against the code: `prdcopy.sync` (the `issue create` loop with `--milestone page`), `milestones.repo_side` (lists state=all, returns ({title: text}, {title: number}, why)), `prd.out` (runs `$LOOP_GH`, never raises) all exist as the design says.

## Build steps

1. `skills/workflow-docs/scripts/milestones.py`: add `backlog(page)`, cached per run: list with `repo_side()`, create `Backlog: <page>` with `gh api -X POST` when absent, return "" when gh can neither list nor create.
2. `skills/workflow-docs/scripts/prdcopy.py`: the delta-issue loop tries `--milestone Backlog: <page>` then no milestone; the bare page name is gone.
3. `dev/toy/test-docs-sync.py`: fake gh answers `gh api .../milestones` (GET seeded with a bare `Sensor` milestone, POST recorded and remembered); three checks: lands on Backlog: Sensor created first, bare name never used, an existing Backlog: Sensor is not made twice.
4. `.loop/regression.tsv`: `sync-delta-posted` widened to those PASS lines, seen red 2026-11-17 (the table is at its cap: no row added).
5. `skills/workflow-docs/references/commands.md`: the sync line names `Backlog: PAGE`; `docs.py render` refreshes the wiki Tests table.

## Tests per done line

- Done 1: `a delta issue lands on the milestone Backlog: Sensor, created first when it is missing` and `a Backlog: Sensor milestone that exists is used again, not created twice`, failing on the old prdcopy.py (verified), passing now (24 PASS, 0 FAIL).
- Done 2: `a bare-name milestone is never used for a delta issue, even when it exists`, same proof.

## What could break

- A repo whose gh cannot list milestones falls back to no milestone (the delta issue is still filed): covered by `with no working gh the delta is shown`.
- One extra gh list call per page per run, only when a delta issue is opened.
- Row cap: no net rows added.

## Out of scope

The reviewed DOC-17 wording ("the feature's milestone"), the milestone-sync delta issues in milestones.py, and moving existing delta issues off a bare-name milestone.

VERDICT: self: plan covers both done lines; no decision for the owner
DEPTH: full
STEP: done
