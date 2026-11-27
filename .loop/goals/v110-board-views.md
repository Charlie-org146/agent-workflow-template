# Task 18 goal 2, The board, three views (owner o1095): one card per release, task and goal, filled by a script with no model call, views by release, by task and by goal (BOARD-1, 2, 3, 5, 7 and 8).

- Slug: v110-board-views
- Review: one
- Touches: skills/workflow-monitoring, skills/workflow-setup, .loop/config.json, dev/toy, .loop/regression.tsv, .loop/START.md, skills/loop-files.md, .loop/regression-relevel.tsv, docs/wiki/How-to-use-Setup.md, docs/wiki/Tests.md
- ETA: 335 active minutes (estimate 267m plus a 25% margin)

## Done lines

Frozen. A wrong done line needs a new goal.

1. Given a toy repo with one release, two tasks and three goals, when the board refresh runs, then the board holds one card for each, showing its state and whose ETA it is, each goal's card names its task and its machine, and the views by release, by task and by goal each list those cards grouped that way.
2. A goal's card shows every line the board showed for that goal before, such as its step minutes, a missed or late mark with its cause, and the limit that holds it back.
3. The refresh makes no model call, and a second run with nothing changed writes nothing.
4. A card whose state is older than `board_max_age` shows as stale.
5. Given text the private-name scan refuses, when the refresh would send it, then nothing is sent, and the refusal names the place without the word.
6. Given a check-in due with nothing changed since the last one, then none is sent; given a change, then one is sent, and no two are closer than `checkin_every`.
7. Given a second toy repo that adopted the template, when its refresh runs, then its cards go to its own board.
8. The standard package line.

## Verify by hand

<!-- Numbered steps for a person, each with an Expect: line. A release needs this. -->
