# The check-in shows each release's work as progress bars: one bar per frozen done line of each goal, with done/total and an ETA, and a roll-up bar and ETA for the release

- Slug: release-progress
- Touches: skills/workflow-monitoring/scripts/checkin.py, skills/workflow-monitoring/scripts/board_lines.py, docs/wiki/Check-in-and-board.md, docs/wiki/How-to-use-Check-in-and-board.md, dev/toy/test-release-progress.py, .loop/regression.tsv
- ETA: 335 active minutes (estimate 267m plus a 25% margin)

## Done lines

Frozen. A wrong done line needs a new goal.

1. Given releases with goals, when checkin.py prints a repo's block, then under each release each goal shows one text progress bar per frozen done line (the owner's sub-steps), each with done/total and an ETA, and each release shows a roll-up bar over all its goals' done lines with the release ETA
2. Given a goal's done line, then its bar comes from real data, never typed by hand: the regression rows linked to that line (goal slug:N) that last passed over the rows linked; a line with no linked row shows its goal's recorded flow-step progress, marked as by step
3. Given any bar, then it shows done/total and an ETA, or "ETA unknown: <why>" naming what is missing, and never a blank or an invented time
4. Given the check-in printed in a terminal, then the bars are plain text of at most 60 columns (no colour, no images), so they read in a terminal and wherever the check-in text is shown, such as the board's Dependencies text
5. Given the Check-in-and-board page, then the check-in requirement CHK-1 is revised through criteria.py with an owner record naming CHK-1 and release-progress to name the bars, and the How-to page describes them and how to read done/total and the ETA
6. Given a fixture repo with 2 releases and 3 goals, when dev/toy/test-release-progress.py runs the check-in, then each goal shows a bar per done line, each release a roll-up bar, with a negative control that a done line with no linked row reads by step, and a goal with no estimate prints ETA unknown with its reason
7. Given this goal's diff, then no shipped file is added, no touched script is over 19,000 LF bytes (or larger than on main if main is already over), net regression rows add at most one, the check-in's other sections and the reply hook's checks are unchanged, and no requirement text changes beyond the CHK-1 revision

## Verify by hand

<!-- Numbered steps for a person, each with an Expect: line. A release needs this. -->
