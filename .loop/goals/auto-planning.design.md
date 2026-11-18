# auto-planning: design

## Problem
Each round the operation session splits the backlog into releases, sets estimates, ETAs and budgets, and picks a machine
and an agent for each goal by hand, then asks the owner item by item. It should compute the plan from past runs and
settings and send one plan to approve (issue #4779, o103, o116).

## Approaches
1. A new `plan.py` script. Clean, but the package is at its 100-file cap and every monitoring script is at the size cap:
   refused.
2. Fold a `plan` command (with `plan approve`) into `monitor.py` (14 KB, 4.6 KB of room), which already reads the queue,
   the run records and the pool, and reuse `auto.eta_new` for the estimate and ETA. Put the cross-check, which runs an
   agent, in `routing.py` (a `check` command beside `build`), so the profile, fallback and token reading stay in one place.
   Cost: both files grow to just under 19,000 bytes. Risk: the helper code has to stay small.

## Chosen: approach 2
- `monitor.py plan [--machines pc=GB,mac=GB] [--peer-plan FILE] [--peer NAME] [--check]` reads the queue lines that name no
  release and leaves out goals already started (a run record, a pool entry, a `machine:` field, a place in the peer's plan).
  Per goal: release (the next free minor above VERSION's, dependants after what they depend on, at most N per release),
  estimate and hard ETA (`auto.eta_new`, the eta_margin_percent margin), token budget (1.5 times the mean fresh tokens of
  done runs, never above `token_budget`), machine (Windows-only goals to the PC, Mac-lane goals to the Mac, else the
  machine with the most memory left after one 1.5 GB worker per goal already given to it, the local one read with
  `board_status.memory`), agent profile (small goal: the `small` route, else cheap; large: heavy) with one reason. It
  prints the plan and the message for the other machine's operation session, saves the plan JSON under
  `<loop>/plan-round.json` as pending, and writes no queue line, run record or worktree.
- `monitor.py plan approve [--owner-record ID] [SLUG key=value ...]` checks the record is in `owner-words.tsv`, applies the
  line edits to the pending plan, appends `release:`, `machine:` and `agent:` to each queue line and marks the plan approved.
  ETA choices (ship, extend, defer) stay the owner's through `goal.py set`: the plan only proposes ETAs.
- `routing.py check [--text FILE]` resolves the `plan` step's profile (`routes.steps.plan`), runs it read-only on the plan
  text and prints its notes; not installed, not logged in, or a read-only sandbox falls back to Claude with the
  `AGENT_FALLBACK` line. `plan --check` calls it and prints the notes under Cross-check; a failure never blocks the plan.

## What each done line needs
1. `plan` prints the table and writes nothing else; the toy test checks the run folder, queue and pool are unchanged.
2. `plan approve` with a record writes the three fields and the edits; each refusal changes nothing.
3. Toy machines through `--machines` (and `LOOP_MACHINE`) and a toy queue with a Windows-only, a Mac-lane, small and large goal.
4. Started goals (run, pool, machine field, peer plan file) are listed as "left out: already started"; the message block ends the output.
5. A fake second agent profile routed for `plan`; one with a missing command shows the fallback line.

## Open questions
None for the owner: the release size and the 1.5 GB per worker follow existing settings (o118, recommended answers taken).
