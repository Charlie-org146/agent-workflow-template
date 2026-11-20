# Plan: known-red-w11-docs-size

Checked against the code: `origins` (milestones.py), `config_of` (counting.py), `alone` (docs.py), `stands_alone` (prdcopy.py), the `from deployments import` line (criteria.py), `split-check.py` and the two rows all exist as the design says. `milestones.alone` is the only caller path (deployments.py:364); `milestones.origins` is read by the gate-scope toy and by `alone`.

**Build steps.**
1. Trim docstrings and comments in the 11 scripts until each is at most 18,980 bytes (LF); output text and code stay.
2. Move `origins` to counting.py (after `config_of`); milestones.py imports it back.
3. Move `alone` to prdcopy.py (after `stands_alone`), using `counting.origins`; milestones.py imports `alone, stands_alone` from prdcopy; docs.py drops it.
4. criteria.py: one `from deployments import` line naming the four moved names; `link_of`, `link_page`, `owner_words`, `slurp` become assignments from the `deployments` module.

**Test per done line.** Line 1: the row `docs-scripts-under-19000` command and `split-check.py` for size-139 both fail on main (names, size) and pass on the head. Lines 2 and 3: `git diff --stat` shows only the 11 scripts plus goal files; the docs python toys (gate-scope, sync, milestone-sync, audit-head, nongoal, docs-only-bump) and `docs.py check` pass; CI runs the shell toys.

**What could break.** A circular import (checked: every module imports; the toys import them), a toy patching a moved name (split-check's patch scan and a grep find none), text a toy greps in a docstring (a grep for `__doc__` found only argparse descriptions, and the module docstrings that feed them are only reworded in criteria.py and docs.py).

**Out of scope.** size-140 and size-141 (docs.py's import-back, regression.py), behaviour changes, new files.

VERDICT: self-review: plan matches the design and the frozen done lines
