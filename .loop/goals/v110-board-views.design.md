# Design: v110-board-views (task 18 goal 2)

## Problem
The board (`board.py`, `board_page.py`, `board_status.py`, `board_tasks.py`, `live_board.py`, `checkin.py`) lists goal runs and a task list, but has no
single card model: releases and tasks are not cards, a goal card does not name its task or machine, and there are no views grouped by release, task or goal.
`board_max_age` (stale marks) and `checkin_every` (the gap between check-ins) do not exist as settings. A check-in is sent by `notify.py` with no
"nothing changed" rule beyond its seen-keys file.

## Approaches
A. One new module `board_cards.py` builds a list of plain card records (release, task, goal) from data the board already collects (`board.build` rows and
   deps, `board_tasks.tasks`, `board_status.release_of`), and three pure group functions (by release, by task, by goal). `board.py`, `board_page.py`
   and `checkin.py` render them. A goal card keeps every line `goal_line` prints today. Cost: one new file (~250 lines) plus small edits; risk: low,
   because the existing lines stay as they are and the card only wraps them.
B. Rewrite `board.build` to emit cards directly and drop the old row shape. Cost: touches every consumer (`live_board`, `checkin`, `board_page`, `replan`);
   risk: high, since done line 2 needs old lines byte for byte.

## Chosen: A
Pure data in, text out: no model call (line 3), and the refresh writes a file only when its bytes differ from the one on disk, so a second run with nothing
changed writes nothing.

## What each done line needs
1. `board_cards.cards(rows, deps, tasks, releases, machines)` returns one card per release, task and goal with state and "whose ETA" (the goal's, the task's,
   the release's). A goal card carries `task` and `machine`. `group_by("release"|"task"|"goal")` lists them. Toy: a repo with one release, two tasks, three goals.
2. The goal card's lines are `board_status.goal_line(...)` unchanged (step minutes, missed/late mark and cause, limit). A toy compares the card against the
   line the old board printed for the same fixture.
3. No import of a model client; the toy fails if the refresh spawns anything but git/gh. Second run: `write()` skips when the new text equals the file.
4. New setting `board_max_age` (minutes, default 120, declared in `skills/workflow-setup/scripts/settings.py` with its explanation, so `.loop/config.json`
   is NOT changed). A card whose state time is older shows `stale`.
5. Before any send, `notify.py` and the check-in mail path call the private-name scan (`private.py scan` machinery) on the outgoing text; on a refusal
   nothing is sent and the output names the place (card id and field), never the word.
6. New setting `checkin_every` (minutes, default 30, in `settings.py`; read like `cadence`). A check-in due with no change since `checkin.json` is not sent;
   with a change one is sent; none sooner than `checkin_every` after the last.
7. The board path is taken from the repo being refreshed (`followed()` already yields name, path, base), so a second adopting repo's cards go to its own
   board directory; a toy with two repos checks neither writes the other's files.
8. The standard package line (tests, rows in `.loop/regression.tsv` seen red first, wiki Tests page rendered).

## Open questions
- `board_max_age` and `checkin_every` defaults: 120 and 30 are taken (30 matches today's `cadence`).
- Where the "machine" of a goal comes from: the session pool's `machine` field if present, else this machine's name. Taken as recommended.
- The build first needs the GitHub token's project permission when it reads or writes the GitHub Project items for release and task cards (the project
  read in BOARD-1); every toy uses fixtures and needs none.
