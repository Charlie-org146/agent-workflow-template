# scripts-b design

Twelve workflow-docs and workflow-release scripts were over 19,000 LF bytes (merge.py 20,459 the largest); render.py and counting.py also failed docs-block-split at 18,432.

Approach A (chosen): tighten docstrings and comments, merge duplicated code, inline one-use helpers, no behaviour or message change. Approach B (split code into new files) rejected: the package is at its file cap. Cost: small, risk: a changed import, so each script's importers were grepped and the toys that read them run.

Each done line: 1 is held by the new row docs-release-scripts-under-19000 (seen red); 2 by the toys of both skills, docs-block-split and the package gate. Open questions: none. Note: 14 shell toys skip on Windows and run in the lane.
