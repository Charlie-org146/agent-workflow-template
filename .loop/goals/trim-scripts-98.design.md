# trim-scripts-98 design

## Problem
goal.py, role.py, lane.py (workflow-delivery) and setup.py (workflow-setup) are over 19,000 bytes, and the package holds 99 files
against a headroom of 98 (#138, #352, #3852, #2158, #4497).

## Approaches
1. Simplify the code of each script (local variables for repeated attribute reads, one helper for repeated blocks, merged
   branches), keeping every comment, docstring and printed text; fold the monitoring operation guide into commands.md.
2. Delete comments or relax the cap. Rejected by the owner (o61 (b)): fold to 98 rather than relax.

## Chosen
Approach 1. No .py pair fits under 19,000 bytes (the proctree copies are cmp-checked identical, review.py runs by name), so the fold
is `skills/workflow-monitoring/references/operation.md` into the same skill's `references/commands.md`; every link follows.

## What each done line needs
1. The four scripts at 18,819 to 18,980 bytes; row `trim-setup-under-19000` and the existing delivery and headroom rows pass.
2. The package at 98 files; row `trim-package-98` (headroom plus package gate); the toys that read operation.md now read commands.md.

## Open questions
None.
