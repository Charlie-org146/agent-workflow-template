# Design: v1-go-no-go

Problem: decide whether v1.0.0 goes and prepare it. The short checks on origin/main v0.28.92 all pass (health green, package builds, docs OK, no entry lag, unique row ids, pr lanes clean).

Approaches: (1) cut a major bump of this goal's pull request as a draft release; (2) hand-edit VERSION and CHANGELOG. Chosen: 1, through workflow-release, so the changelog and notes follow the repo's habit.

Done lines: line 1 is the check results, sent to operation; line 2 is the draft only, nothing published.

Open questions: none.
