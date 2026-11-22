# implement-v110 byte table (final, LF bytes; measured at the build's end)

Planning-time room and trims are in the plan's byte list. Here: each script the build touched, its size on the merge base, its size now, and the room left (below 19,000 for a script that started under it, below 20,480 otherwise).

| script | base | now | room left |
|---|---|---|---|
| workflow-delivery/scripts/goal.py | 18997 | 18979 | 21 |
| workflow-delivery/scripts/fit.py | 19641 | 20464 | 16 |
| workflow-delivery/scripts/role.py | 19997 | 20176 | 304 |
| workflow-delivery/scripts/proctree.py | 18995 | 18877 | 123 |
| workflow-monitoring/scripts/proctree.py | 18995 | 18877 | 123 |
| workflow-regression/scripts/proctree.py | 18995 | 18877 | 123 |
| workflow-monitoring/scripts/live_board.py | 18942 | 18765 | 235 |
| workflow-release/scripts/merge.py | 18990 | 18969 | 31 |
| workflow-release/scripts/release.py | 18994 | 18921 | 79 |
| workflow-release/scripts/review.py | 18988 | 18943 | 57 |
| workflow-release/scripts/autorelease.py | 18901 | 18989 | 11 |
| workflow-release/scripts/brief.py | new | 14700 | 4300 |
| workflow-docs/scripts/sections.py | 11575 | 18979 | 21 |
| workflow-docs/scripts/docs.py | 18458 | 18590 | 410 |
| workflow-docs/scripts/criteria.py | 20455 | 20479 | 1 |
