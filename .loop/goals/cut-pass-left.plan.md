# Plan: cut-pass-left

Built as designed: review.py gets proven(), left_text() and criteria() (the loop moved out of release.py); release.py's criteria_trouble delegates and the cut prints and writes the LEFT section; dev/toy/test-cut-pass-left.py (6 checks); three rows tied to DEL-5, seen red. release.py 17,890 and review.py 6,269 bytes LF; no new file.

## Tests
current-commit PASS skipped and older rerun; forced stop lists LEFT with count; negative control nothing LEFT.

## What could break
release.py and review.py import each other (lazy import in the cut, as wiki does); the cut now reruns more rows than before (PASS only counts on the current commit) and lists what the stop left.

## Out of scope
Per-dependency PASS (a PASS valid until a file the row reads changes): the lane's deps live in the regression skill.

PENDING: none
