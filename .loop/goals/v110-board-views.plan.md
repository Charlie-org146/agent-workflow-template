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

## Build notes (wording from the fixes read)
- The line-1 toy asserts each card's "whose ETA" (goal: its own; task: its newest goal's; release: its batch's).
- `checkin_every` wins for sends; `cadence` is only the display gap.
- Each repo's cards go to that repo's own `<git common dir>/loop/board.json` and `board.html`.
- Step 2 first captures the old board's golden text on the line-2 fixture, before any change, in `dev/toy/`.

## Round 2 revisions (full depth; ceo, design, engineering and red team again all said "changes"; this section wins over the design file and over round 1 where they differ)
Signature and sources (the design file's `cards(rows, deps, tasks, releases, machines)` and "goal_line alone" are replaced): `cards(rows, deps, tasks, batches, at, root)`.
- Line 2, the real sources: `goal_line` (mark, minutes left, machine); `board_lines.bars` (step minutes); `auto.eta_text` and `auto.eta_wait` (a goal's missed or late mark and cause, `auto.py:278-292`, called at `checkin.py:133`); `board_lines.cause(run)` for that goal's own limit text (the grouped `stuck` block stays on the board where it is, and each goal card shows its own cause line only). `auto.py` joins Files, read-only unless a read-only variant is needed.
- Line 3, no ledger writes: the release card never calls `release_header` in a way that writes `etas.jsonl`; it reads the ledger only (`loop=None`). The second-run toy compares every file under the loop dir (`board.json`, `board.html`, artifact page, `checkin.json`, `etas.jsonl`, `handoff.md`, `notified.json`, `runs/*.json`) by bytes and mtime, with the real clock and a pinned one, and covers `cmd_send` and `handoff` as well as `board`. `board.write` is the one skip: for JSON it drops `generated` and `next_at` before comparing and rewrites only on a real change; other files compare by bytes. `checkin.json` keeps its `at` and is written only when a check-in is actually shown. `cmd_send` saves `notified.json` only when it changed. The new `cards` key goes after the existing keys in `board.json`; `test-live-board.sh` and `test-checkin-live.py` run unchanged to prove nothing moved.
- Line 4, state time per state: running or waiting goal = its `updated`; done or merged goal = its merge or done time and never stale; queued goal, unstarted release and a card with no time = never stale (shown "no time"); a task or release = the newest `updated` among its goals still in the runs, else never stale. Older than means greater than `board_max_age` minutes. A non-number setting = 120.
- Membership: a goal's task is the first non-replaced brief that lists it, else "none"; a goal's release is `release_of` from `queue.md`, and a brief's own `release:` line is shown on its task card without overriding the goal's. A release with no running goal has state "idle"; the release state set is idle, running, waiting, done. A goal in no batch lists under "no release" with no release card.
- Line 5, scan coverage: the scan runs on every outgoing unit: the mail subject, each body line and the HTML form in `notify.py send` (after `compose`, before `deliver`; a refusal releases the claim and leaves no `mailing` key in `notified.json`), and on `board.html`, `board.json` and the artifact page before they are published. Places are opaque (`subject`, `body N`, `page N`), never a slug. "off" (a comments-only list) passes by design; `none` and `broken` refuse. Toys put the test word in the slug, the repo name and a task name, inject their own test list, and drive `cmd_send` end to end, asserting `deliver` was never called and the refusal text omits the word.
- Line 6, the send point: the check-in goes out as one more event kind ("checkin") in `notify.py send`, built from the CHANGE lines and event keys. Only that kind is gated: no send when its hash equals the last send's (stored in `notified.json`), and none closer than `checkin_every` to the last send's time (also stored there). Start reviews, stopped or past-ETA mails and owner questions are exempt and never held; a held check-in stays unsent and is retried. The "30" at `notify.py:323` is help text and is changed to read `checkin_every`.
- Line 7, one board per repo: `build` runs per repo and each repo's board holds only its own cards, written under that repo's common dir; settings are read from that repo's config with that repo's base, never from the current directory; the toy gives two repos different `board_max_age` and `checkin_every` and runs from a third directory. The existing multi-repo board toys stay green because the combined digest is left as it is and the per-repo board files are added beside it.
- Machine: the run's `machine` field, else `graph.machine_name()` for a run with none; the toy covers a goal with no `machine`.
- Settings files: adding the two REPO rows turns `test-settings.sh` red until `skills/loop-files.md` (the saved reference) and the key list in `test-settings.sh` are regenerated; both join Files, with `.loop/START.md` (now in Touches by TD2412). `.loop/config.json` gets only the goal's two new lines, committed after `git update-index --no-skip-worktree`, auto_approve restored, the diff shown to the operation session first (TD2412).
- Release and task cards come from `queue.md` batches and `board_tasks.tasks`, a deliberate reading of BOARD-1; the live GitHub Project read is a hand-verify step, needed at verify only (TD2412); delivery fills the Verify-by-hand section.
- Tests: rows `board-views-1` to `board-views-7`; line 8 is the package line and has no row of its own. The golden text for line 2 is captured from `board.py` output with the clock pinned, on a fixture with a missed ETA and a usage-limit hold, before any change.

## PENDING
PENDING: 1. (answered by TD2412) the committed `.loop/config.json` lines for the two settings: commit only those two lines after `git update-index --no-skip-worktree`, and show the diff to the operation session first.
PENDING: 2. (answered by TD2412) the GitHub token's project permission is needed at verify only.
PENDING: 3. (answered by TD2412) `.loop/START.md` is now in Touches. New: `skills/loop-files.md` is also regenerated by the settings reference and is not in Touches.
PENDING: 4. The line estimate rose from 650 to 1000 against a 335-minute ETA; the owner decides (extend once, or cut the per-repo-settings toy); the extension waits for the owner's words (TD2412).

Files: skills/workflow-monitoring/scripts/board_cards.py, skills/workflow-monitoring/scripts/board.py, skills/workflow-monitoring/scripts/board_page.py, skills/workflow-monitoring/scripts/board_status.py, skills/workflow-monitoring/scripts/board_lines.py, skills/workflow-monitoring/scripts/board_tasks.py, skills/workflow-monitoring/scripts/live_board.py, skills/workflow-monitoring/scripts/checkin.py, skills/workflow-monitoring/scripts/notify.py, skills/workflow-setup/scripts/settings.py, dev/toy/test-board-views.py, .loop/regression.tsv, .loop/START.md, skills/workflow-monitoring/scripts/auto.py, skills/loop-files.md, dev/toy/test-settings.sh
Lines: 1000
Gates: none
Classes: none
