# implement-v110 byte table (measured in the planning step, LF bytes)

Room is below 19,000 for a script under 19,000 and below 20,480 for one already at or over 19,000. Docstring and comment bytes are what a trim may take; a trim never touches code.

| script | bytes | room | docstring bytes | comment bytes |
|---|---|---|---|---|
| workflow-delivery/scripts/goal.py | 18997 | 3 | 725 | 56 |
| workflow-delivery/scripts/fit.py | 19641 | 839 | 115 | 168 |
| workflow-delivery/scripts/role.py | 19997 | 483 | 1596 | 63 |
| workflow-delivery/scripts/proctree.py | 18995 | 5 | 3501 | 584 |
| workflow-monitoring/scripts/proctree.py | 18995 | 5 | 3501 | 584 |
| workflow-regression/scripts/proctree.py | 18995 | 5 | 3501 | 584 |
| workflow-monitoring/scripts/watch.py | 18990 | 10 | 646 | 171 |
| workflow-monitoring/scripts/batch.py | 18961 | 39 | 1467 | 144 |
| workflow-monitoring/scripts/graph.py | 18987 | 13 | 3113 | 2030 |
| workflow-monitoring/scripts/checkin.py | 18996 | 4 | 424 | 224 |
| workflow-monitoring/scripts/live_board.py | 18942 | 58 | 2472 | 619 |
| workflow-release/scripts/merge.py | 18990 | 10 | 1423 | 255 |
| workflow-release/scripts/release.py | 18994 | 6 | 429 | 92 |
| workflow-release/scripts/review.py | 18988 | 12 | 1471 | 172 |
| workflow-release/scripts/wiki.py | 18994 | 6 | 2725 | 243 |
| workflow-release/scripts/autorelease.py | 18901 | 99 | 1382 | 376 |
| workflow-docs/scripts/sections.py | 11575 | 7425 | 1956 | 98 |
| workflow-docs/scripts/docs.py | 18458 | 542 | 1406 | 70 |
| workflow-docs/scripts/render.py | 18737 | 263 | 574 | 77 |
| workflow-docs/scripts/deployments.py | 19654 | 826 | 1329 | 786 |
| workflow-docs/scripts/criteria.py | 20455 | 25 | 1605 | 242 |
