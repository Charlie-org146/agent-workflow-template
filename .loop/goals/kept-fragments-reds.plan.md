# Plan: kept-fragments-reds

Design: `.loop/goals/kept-fragments-reds.design.md` (condensed; one self-review pass, no findings).

## URGENT, outside this plan

None.

## Implementation plan

Done lines (frozen): (1) each of the seven rows passes on this branch, with a negative control that bites; (2) the goal's result names for each row whether test or code was wrong, the requirement and the evidence, no known-list entry; (3) no shipped file added, no touched script over 19,000 bytes or larger than main, net rows 0, no requirement text change.

### 1. `skills/workflow-docs/scripts/audit.py`
- `keep()` commits with `*docs.identity(root)` (the loop's identity only when user.email is unset); trim the docstring so the file is smaller than main.

### 2. `dev/toy/test-how-to-use.py`
- Drop `git commit -am restamp` after the relock; run the re-stamp fixture with `GIT_CONFIG_GLOBAL=/dev/null` and `user.useConfigOnly` (fails without step 1).

### 3. `skills/workflow-monitoring/scripts/operate.py` and `dev/toy/test-apply-rerender.py`
- `wiki_only()` allows `.loop/kept/*.tsv`; trim docstrings to stay below main's size.
- Negative control: a head that also adds a non-.tsv file under `.loop/kept` stays refused.

## Verification
Run the seven rows' commands; revert steps 1 and 3 to see the controls fail.
