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
1. Settings: add `board_max_age` (120, minutes, parsed as an int; a non-number uses 120) and `checkin_every` (30, same) as REPO rows in `settings.py`; code reads them with `cfg.get(key, default)`. `fill-repo` then writes them into `.loop/config.json` and `settings.py reference --write` regenerates `.loop/START.md`; see PENDING 1.
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

## Revisions after the review round (one round: ceo, design, engineering, red team; all four said "changes")
- Done line 2: a goal card wraps four sources, not `goal_line` alone: `goal_line` (mark, minutes left, machine), `board_lines.bars` (step minutes), `release_header` and the ETA ledger (missed or late mark and cause), `board_lines.stuck` (the limit). The line-2 toy checks golden text captured from the old board on a fixture that has a missed ETA and a usage-limit hold, made before the change.
- Release and task cards without the GitHub Project: a release card comes from the `queue.md` batch plus its goals' states; a task card from `board_tasks.tasks`. `cards(rows, deps, tasks, batches, at, root)` takes `at` and `root`. A goal in no brief shows task "none"; a replaced task shows in its own group. The GitHub Project read stays out of this goal's build and tests (fixtures only); it is a hand-verify step.
- Machine: from the run's `machine` field (`graph.py:369`); the toy has one goal owned by the other machine and asserts its card does not carry this machine's name.
- Done line 3: `board.json` leaves out `generated` and `next_at` from the equal-bytes comparison (they are written only when something else changed); the same skip applies to `board.html`, the artifact page and `board_page.py`'s `checkin.json` write. The toy pins the clock and compares bytes and mtimes of the whole loop dir across two runs, and a static check that the refresh imports no model client plus a spy that fails on any spawn other than git or gh.
- Done line 4: state time per card kind: goal = its `updated`; task = its newest goal's `updated`; release = its newest goal's `updated`; a card with no time is shown stale. A card at exactly `board_max_age` is not stale (older than means greater than). Toy: no-time card, an exact-age card, a non-number setting.
- Done line 5: the scan runs on the composed body in `notify.py` after `compose` and before `deliver`, releases the claim on a refusal, and fails closed when the scan state is none or broken. Texts are keyed by an opaque `card N field`, never the slug, so the refusal names the place without the word. The toy injects its own test list through the scan's own list setting and never reads the real one.
- Done line 6: one send point, `notify.py send`. "Nothing changed" = the same set of CHANGE lines and event keys as the last send (a stored hash in `notified.json`, not text with timestamps). The last-send time is stored there too. The hard-coded 30 at `notify.py:323` reads `checkin_every`. `cadence` stays as the display gap; this goal does not alias it. `checkin.py` only prints.
- Done line 7: the board is per repo: cards are filtered to the repo being refreshed, and settings (`board_max_age`, `checkin_every`) are read from that repo's config, not from the current directory. The toy gives each of two repos a different value and runs from a third directory.
- Existing pinned toys stay green: `test-board.sh`, `test-board-estimates.sh`, `test-board-held.sh`, `test-board-tz.sh`, `test-live-board.sh`, `test-checkin-live.py`, `test-checkin-view.py`, `test-email-notify.py`, `test-settings.sh`. Rows use the same level and columns as the existing rows (the build reads `.loop/regression.tsv` first). The line estimate rises to 900; the Tests wiki page is rendered by the package line.
- Wording for the build notes: the line-1 toy also checks each card's "whose ETA"; Files adds `board_status.py`, `board_lines.py`, `board_tasks.py`.

## PENDING
PENDING: 1. Committed `.loop/config.json` lines for `board_max_age` and `checkin_every` (fill-repo writes them; the file is skip-worktree here and also in Touches). The operation session decides how that edit is made; the build waits on it for step 1's last part only.
PENDING: 2. The GitHub token's project permission, first needed by the hand-verify step for live release and task cards (not by any toy).
PENDING: 3. `.loop/START.md` is regenerated by `settings.py reference --write` but is not in the frozen Touches; the owner decides whether that file may change.
PENDING: 4. The line estimate rose from 650 to 900 against a 335-minute ETA; the owner decides whether the ETA stands.

## Build notes (wording from the fixes read)
- The line-1 toy asserts each card's "whose ETA" (goal: its own; task: its newest goal's; release: its batch's).
- `checkin_every` wins for sends; `cadence` is only the display gap.
- Each repo's cards go to that repo's own `<git common dir>/loop/board.json` and `board.html`.
- Step 2 first captures the old board's golden text on the line-2 fixture, before any change, in `dev/toy/`.

Files: skills/workflow-monitoring/scripts/board_cards.py, skills/workflow-monitoring/scripts/board.py, skills/workflow-monitoring/scripts/board_page.py, skills/workflow-monitoring/scripts/board_status.py, skills/workflow-monitoring/scripts/board_lines.py, skills/workflow-monitoring/scripts/board_tasks.py, skills/workflow-monitoring/scripts/live_board.py, skills/workflow-monitoring/scripts/checkin.py, skills/workflow-monitoring/scripts/notify.py, skills/workflow-setup/scripts/settings.py, dev/toy/test-board-views.py, .loop/regression.tsv, .loop/START.md
Lines: 900
Gates: none
Classes: none
