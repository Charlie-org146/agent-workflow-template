# Plan: lanes-closure-slashes

1. Rename closure's body to raw_closure and add closure() returning every dep with forward slashes (lanes.py). Done: built.
2. touches() replaces backslashes in its path. Done: built.
3. Toy dev/toy/test-lane-closure-slashes.py feeds both slash forms and a POSIX list. Done: built.
4. Rows lane-closure-slashes and lane-closure-posix-same (defect, linked to #4457), each seen red. Done: built.
5. Re-render the Tests page, check docs, run the lane. Then review, qa, ship, pr.
