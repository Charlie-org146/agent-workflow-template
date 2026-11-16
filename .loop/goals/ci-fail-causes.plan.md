# Plan: ci-fail-causes

1. actions.py: print the failure block; set TOY_SKIP_FILE per row and read it (done, with toy cases and rows seen red).
2. Group run 43814023230's 85 failing rows into .loop/goals/ci-fail-causes.groups.md and comment it on #4516.
3. File one issue per group on v1.1 (#4553 to #4560); row ci-groups-complete keeps the groups file complete.

Out of scope: fixing the filed groups.
