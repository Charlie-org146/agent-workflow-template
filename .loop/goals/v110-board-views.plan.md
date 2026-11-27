# Plan: v110-board-views

Design: `.loop/goals/v110-board-views.design.md` (approach A: a card module beside the old rows).

## Checked against the code
- `board.py`: `collect` and `build` produce `rows` and `deps`; `write` replaces a file with a temp file (no equal-bytes check yet); `followed()` yields name, path, base per repo.
- `board_status.py`: `release_of`, `feature_of`, `goal_line`, `left_time` exist; `goal_line` is the one source of a goal's step minutes, missed/late mark and limit.
- `board_tasks.py`: `tasks` and `task_lines` give each task with state (DEL-23).
- `graph.py`: `machine_name()` gives pc or mac and each run's `machine`.
- `checkin.py`: `last_at` reads `<loop dir>/checkin.json`; `notify.py` sends and keeps `notified.json`.
- `private.py`: `scan(top, base, texts=...)` names a place as `name:line` and `shown_place` masks the word.
- `skills/workflow-setup/scripts/settings.py` holds each setting as (name, scope, default, explanation); `cadence` is there, `board_max_age` and `checkin_every` are not.
- Toys `dev/toy/test-board.sh`, `test-checkin-live.py`, `test-email-notify.py` exist and must stay green.

## Build steps (each: its row red first, then the change)
1. Settings: add `board_max_age` (120) and `checkin_every` (30) to `settings.py`; defaults only, `.loop/config.json` is not changed.
2. `board_cards.py`: `cards(...)` and `group_by(...)`; card fields id, kind, state, eta_of, task, machine, stale, lines.
3. Wire `board.py` (write only if bytes differ), `board_page.py` and `live_board.py` to render the three views; goal lines come from `goal_line` unchanged.
4. Stale: compare each card's state time with `board_max_age`.
5. Private scan before send in `notify.py` and the check-in mail: refuse, name `card:field`, send nothing.
6. Check-in gate in `checkin.py`/`notify.py`: no send when nothing changed; never two closer than `checkin_every`.
7. Per-repo board directory (second adopting repo).
8. Rows in `.loop/regression.tsv`, wiki Tests page, `dev/toy/test-board-views.py`.

## Tests, one row per done line (`board-views-1` to `board-views-7`, level L0, toy `dev/toy/test-board-views.py`)
Line 1: toy repo with one release, two tasks, three goals; counts, task and machine on goal cards, three groupings. Line 2: goal card lines equal old `goal_line` output on the same fixture. Line 3: a second run writes nothing (mtime and bytes), and the toy runs with no model client on its PATH. Line 4: state older than `board_max_age` shows stale. Line 5: text the scan refuses sends nothing and the refusal has the place and not the word. Line 6: unchanged check-in not sent; changed sent; two within `checkin_every` sends one. Line 7: two toy repos, each writes only its own board. Line 8: the package line.

## What could break
`goal_line` consumers (`live_board`, `checkin`, `replan`), the byte-for-byte output of existing board toys, and the notify seen-keys file when the gate lands.

## Out of scope
Anything beyond the eight done lines (OPS-1.10): no new views beyond three, no model summaries, no change to merge or release code.

## Where the build first needs the GitHub token's project permission
Step 2, when `cards` reads release and task items from the GitHub Project (BOARD-1); every toy uses fixtures and no network. Reading it live waits on the owner granting that permission.

Files: skills/workflow-monitoring/scripts/board_cards.py, skills/workflow-monitoring/scripts/board.py, skills/workflow-monitoring/scripts/board_page.py, skills/workflow-monitoring/scripts/live_board.py, skills/workflow-monitoring/scripts/checkin.py, skills/workflow-monitoring/scripts/notify.py, skills/workflow-setup/scripts/settings.py, dev/toy/test-board-views.py, .loop/regression.tsv
Lines: 650
Gates: none
Classes: none
