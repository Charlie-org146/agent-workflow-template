# The check-in shows the work as a queue: what is building now, then what is queued in order, each with progress and ETA

- Slug: queue-view
- Touches: skills/workflow-monitoring/scripts/checkin.py, skills/workflow-monitoring/scripts/board_lines.py, skills/workflow-monitoring/scripts/live_board.py, docs/wiki/Check-in-and-board.md, docs/wiki/How-to-use-Check-in-and-board.md, dev/toy/test-queue-view.py, .loop/regression.tsv
- ETA: 335 active minutes (estimate 267m plus a 25% margin)

## Done lines

Frozen. A wrong done line needs a new goal.

1. Given a repo with goals running and goals queued, when checkin.py prints the Dependencies section, then each repo has two blocks: "Building now" (each running goal with its PR, session, step, progress and ETA) and "Queue, in order" (each queued goal with its position, the goal, what it waits for, and its ETA to start)
2. Given a running goal and a queued goal, when the check-in prints, then the running goal appears only under "Building now" and the queued goal only under "Queue, in order", never in both
3. Given queue.md with dependencies, a slot limit and the run records, then the queue order, the waits-for text and the ETA to start come from the loop's own queue code (queue.md order, graph.ready and the dependency graph), not from text typed by hand
4. Given any goal in either block, then its row shows an ETA, or "ETA unknown: <why>" naming what is missing, and never a blank or an invented time
5. Given the Check-in-and-board page, then the requirement for the check-in layout (CHK-1, formerly MON-5) is revised through criteria.py with owner record o294 to name the two blocks, and the How-to page describes them and how to read the ETA
6. Given a fixture repo with 2 running and 3 queued goals, when dev/toy/test-queue-view.py runs the check-in, then both blocks show with the 2 running goals and the 3 queued goals in queue order with their waits and ETAs; with a negative control that a goal moved from queued to running leaves the queue block and enters the building block, and a goal with no estimate prints ETA unknown with its reason
7. Given this goal's diff, then no shipped file is added, no touched script is over 19,000 LF bytes (or larger than on main if main is already over), net regression rows add at most one, the check-in's other sections and the reply hook's checks are unchanged, and no requirement text changes beyond the CHK-1 revision

## Verify by hand

<!-- Numbered steps for a person, each with an Expect: line. A release needs this. -->
