# Design: plan-red-team-v20

## Problem

Nothing today asks a fresh mind, once an hour or before a release ETA, "what are we assuming, what could idle capacity start
now, and what is the one thing most likely to cost us the release time?" The board and each machine's STATUS hold every fact
needed, but the sessions that read them are the ones doing the governing, so they share its blind spots. The goal is a
read-only red-team pass: a command builds a reviewer's input from the board and the latest STATUS per machine, a fresh-context
reviewer session answers with three lists, the command records them with a timestamp, and every item is routed on (to
operation-top as a proposed TOP-DECISION, or filed through ops-findings). The reviewer never edits, merges or decides.

## Approaches

1. **A new script `redteam.py` (rejected).** Cleanest to read, but the package is at its 100-file cap (`dev/package.py`), so a
   new shipped file needs a fold that pays for it. A new file plus a deleted one is churn for no gain, and listing.json must
   name it.
2. **Fold three subcommands into `layers.py` (chosen).** `layers.py` already owns STATUS (`collect`, `board`, `publish_board`),
   is 13.5 KB (cap 19,000 for this goal; health fails at 20,480), has a toy (`dev/toy/test-three-level.py`) and is imported by
   `operate.py`, so no new file, no new import and no change to `operate.py` (20.2 KB, near its cap). Cost: layers.py grows by
   about 4 KB. Risk: the hourly nudge must reach top without touching `operate.py`; see below.
3. **Make the reviewer a background process (rejected).** The owner's rule is sessions, not background processes; and a
   headless agent could not be proven read-only by a test.

## Chosen: `layers.py redteam input | record | due`

- `redteam input` prints the reviewer's input and nothing else: a timestamp, the top board (`board(collect(common))`), each
  machine's latest STATUS as one compact line with its age, and the instruction block. The block asks for exactly three
  lists in a fixed line format (`A:` unverified assumptions, `I:` work idle capacity could start now, `R:` the single biggest
  risk to the release time, one line only) and says the reviewer never edits, merges, sends or decides. It reads only.
- `redteam record FILE|-` parses the reviewer's reply, refuses a reply with no `R:` line or more than one, and records the
  three lists with a UTC timestamp in `<git common dir>/loop/redteam/<stamp>.json` (outside the working tree, so no repo file
  is written). It prints one routing line per item: `A:` items go to **ops-findings** (an unverified assumption is a finding
  until someone verifies it), `I:` and `R:` items go to **operation-top as a proposed TOP-DECISION** (starting idle work and
  taking a release risk are choices for top and the owner). The routes are printed and stored with state `proposed`; the
  machine session forwards them (a session message to top, and the ops-findings filing command that `ops-findings-v20`
  builds). The command itself sends nothing and files nothing, which is what keeps the reviewer's pass provably read-only.
- `redteam due [--eta ISO]` prints `RED-TEAM DUE: <why>` when no pass is recorded, the last one is over 60 minutes old, or a
  release ETA falls within 60 minutes with no pass recorded since 60 minutes before it; else `RED-TEAM ok: last pass N minutes
  ago`. It exits 0 either way.
- Hourly and before-ETA wiring: `publish_board` (the top pass, every 5 minutes, already imported by `operate.py`) appends the
  `due` line to the board text when a pass is due. Top then starts a fresh-context reviewer session whose prompt is the
  output of `redteam input` and whose reply goes to `redteam record`. No change to `operate.py`.

## What each done line needs

1. The command: `input` and `record` above. The test, in `dev/toy/test-three-level.py` (no new file): build STATUS for two
   machines in a temp git common dir, run `input` (it holds both machines and the board, and the three-list instruction),
   run `record` on a sample reply (the JSON holds the three lists and a timestamp), and prove read-only by wrapping
   `open` and `subprocess.run`: the only writes are under `<common>/loop/redteam/`, no repo file changes (file hashes of the
   temp repo equal before and after) and no `git merge`/`push`, `gh` or send call is made. A negative control: a reply with
   two `R:` lines is refused and records nothing.
2. `due` plus the `publish_board` line, tested at 59 and 61 minutes and with an ETA 30 minutes out; routes per kind tested in
   the same toy. The requirement wording (DEL-1) says it runs hourly and before a release ETA and that each item is routed.
3. Requirement wording: one new Unreviewed bullet under DEL-1 in `docs/wiki/Delivery.md`, sent to the owner through
   operation-pc before the merge request (DEL-1 until the Mac's consolidation makes it HLT-2; no new ID). No new shipped
   file: the work folds into `layers.py`. Net regression rows 0: the new checks chain onto the existing DEL-1 row
   `no-done-line-refused` (the repo's usual pattern: a row's command chains `test-three-level.py` greps), `.loop/regression.tsv`
   stays at 1300 rows, then `regression.py red` proves the new check can fail.

## Open questions

- PENDING (owner): the DEL-1 wording, which goes to the owner before merge.
- The exact ops-findings filing command is `ops-findings-v20`'s; this goal prints its routes and does not call it. Confirm the
  name with operation-pc before the merge request.
