# Design: merge-private-lane-import (#5306)

## Problem
merge.py loads private.py by file path (autorelease `sibling`). private.pr_result then runs `importlib.import_module("lane")`, but lane.py sits in workflow-delivery/scripts, which is not on sys.path when merge.py runs from workflow-release/scripts. After a private-repo merge this raises ModuleNotFoundError and the release step crashes.

## Approaches
1. Put private.py's own folder on sys.path at import (one line, as goal.py, guards.py, routing.py already do). Cost: about 60 bytes; risk: none, lane.py is always a sibling in a checkout and in an installed skills folder.
2. Load lane by path inside pr_result and cannot(). Cost: more code in two places; risk: drifts.

## Chosen
Approach 1, with matching text trims in private.py's docstrings so the file is not larger than on main (20,297 LF bytes, over 19,000, so net zero or smaller).

## Done lines
1. A toy check in test-merge-guard.sh loads private.py by path with PYTHONPATH unset from a checkout and from an installed copy of skills and imports lane. Folded into the existing merge-guard row, so no new row.
2. Seen red: without the sys.path line the same check prints ModuleNotFoundError.
3. Size and row count: private.py 20,294 vs 20,297; rows 0; no shipped file added; no requirement text changed.

## Open questions
None.
