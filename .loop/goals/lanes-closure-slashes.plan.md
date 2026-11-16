# Plan: lanes-closure-slashes

1. Rename closure's body to raw_closure and add closure() returning every dep with forward slashes (lanes.py). Done: built.
2. touches() replaces backslashes in its path. Done: built.
3. Toy dev/toy/test-lane-closure-slashes.py feeds both slash forms and a POSIX list. Done: built.
4. Rows lane-closure-slashes and lane-closure-posix-same (defect, linked to #4457), each seen red. Done: built.
5. Re-render the Tests page, check docs, run the lane. Then review, qa, ship, pr.

## Tests
- Done line 1: row lane-closure-slashes (seen red by breaking the normalisation in a HEAD copy, passing after).
- Done line 2: row lane-closure-posix-same (seen red by emptying the deps, passing after); the rows that use lanes.closure run in qa's lane.

## What could break
- A caller that mutates the returned deps set: none found (reads only: hits, config_hit, names_any).
- lanes.py size: 19,651 bytes, under the 20,480 limit.

## Out of scope
config_hit's own normalisation stays; no other lanes behaviour changes.
