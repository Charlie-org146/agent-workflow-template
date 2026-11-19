# Plan: merge-private-lane-import (#5306)

Checked against the code: autorelease.py `sibling("private")` loads private.py by path; private.pr_result and private.cannot call `importlib.import_module("lane")`; lane.py is a sibling in skills/workflow-delivery/scripts.

## Build steps
1. private.py: add `sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))` after the imports (same line goal.py, guards.py, routing.py use).
2. private.py: trim docstring text so the LF size is not above main's 20,297.
3. dev/toy/test-merge-guard.sh: add a check that loads private.py by path with PYTHONPATH unset, from a checkout and from a copy of skills, and imports lane. It runs under the existing row merge-guard-base-head, so net rows are 0.

## Tests per done line
1. The new check passes from both folders (LANE OK twice, no ModuleNotFoundError).
2. Seen red: with step 1 removed the same check prints ModuleNotFoundError for both folders (run by hand before the fix).
3. wc -c shows private.py 20,294 vs 20,297; regression.tsv unchanged; no file added.

## What could break
A sys.path insert could shadow a module: the folder only holds delivery's own scripts, already on the path in every other script there. Out of scope: trimming private.py to 19,000 (goal trim-delivery-a).

Review (full): design and plan read against private.py, autorelease.py and the toy; the toy is skipped on native Windows (reap.sh), so the check was run standalone here and runs in CI.
