# implement-v110 byte table (final, LF bytes; measured at the build's end)

Each script the build changed: size on the merge base, size now, room left (below 19,000 for a script that started under it, below 20,480 otherwise).

| script | base | now | room left |
|---|---|---|---|
| workflow-delivery/scripts/fit.py | 19641 | 20068 | 412 |
| workflow-delivery/scripts/goal.py | 18997 | 18979 | 21 |
| workflow-delivery/scripts/proctree.py | 18995 | 18877 | 123 |
| workflow-delivery/scripts/role.py | 19997 | 20407 | 73 |
| workflow-docs/scripts/criteria.py | 20455 | 20402 | 78 |
| workflow-docs/scripts/deployments.py | 19654 | 20424 | 56 |
| workflow-docs/scripts/docs.py | 18458 | 18714 | 286 |
| workflow-docs/scripts/milestones.py | 19242 | 20403 | 77 |
| workflow-docs/scripts/render.py | 18737 | 18998 | 2 |
| workflow-docs/scripts/sections.py | 11575 | 18993 | 7 |
| workflow-monitoring/scripts/live_board.py | 18942 | 18765 | 235 |
| workflow-monitoring/scripts/proctree.py | 18995 | 18877 | 123 |
| workflow-regression/scripts/proctree.py | 18995 | 18877 | 123 |
| workflow-release/scripts/autorelease.py | 18901 | 18993 | 7 |
| workflow-release/scripts/brief.py | new | 18948 | 52 |
| workflow-release/scripts/merge.py | 18990 | 18969 | 31 |
| workflow-release/scripts/release.py | 18994 | 18921 | 79 |
| workflow-release/scripts/review.py | 18988 | 18943 | 57 |
