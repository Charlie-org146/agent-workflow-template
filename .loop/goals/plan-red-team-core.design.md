# Design: plan-red-team-core

## Problem

A plan is only checked by the session that wrote it. The owner wants an adversarial reviewer, fresh in context, to attack each
goal's plan before build against every principle (docs/wiki/Principles.md, eight of them), and a second, hourly pass over the
board and both machines' STATUS. The reviewer must never edit, merge or decide; a principle break must stop the build until the
plan changes or the owner accepts the break in their own words. The package is at its 100-file cap and layers.py, goal.py and
guards.py sit at or over the 19,000-byte line, so every part folds into an existing script.

## Approaches

1. **Everything in layers.py (rejected).** One home, but layers.py is 18.4 KB with the hourly pass; the plan review and the
   gate would break its cap, and ops-findings shares that cap.
2. **Hourly pass stays in layers.py; plan review commands go in mailbox.py (8.9 KB, room); the build gate is one function in
   guards.py behind one line in goal.py's `step` (chosen).** The reviewer's commands are monitoring-side (the machine session
   starts the reviewer), the gate is delivery-side and reads a plain JSON record, so delivery imports nothing from monitoring.
   Cost: goal.py and guards.py are already over 19,000, so the gate's bytes are paid by trimming their prose (net 0).
3. **A new `redteam.py` per skill (rejected).** The package is at its file cap.

## Chosen

- `mailbox.py plan-review SLUG` prints the reviewer's input: the goal's done lines, design and plan, the eight principles, and the
  request for lines `A:` (unverified assumption), `R:` (risk), `B<n>:` (a break of principle n, 1 to 8) and `C:` (a cheaper path).
  It reads only.
- `mailbox.py plan-record SLUG FILE|-` parses the reply (refuses a `B` with no or an unknown principle number) and writes
  `<git common dir>/loop/redteam/plan-<slug>-<stamp>.json` with a timestamp, the plan's sha1, and the four lists. It prints the
  breaks. It writes nothing in the working tree, merges and sends nothing.
- `mailbox.py plan-accept SLUG N --owner-record ID` (the operation session's) writes `plan-<slug>.accept.json` mapping principle N
  to an owner-words.tsv record id; it refuses an id that record does not hold.
- The gate: `guards.plan_gate` runs at `goal.py step SLUG build`. The newest review of the goal whose plan sha equals the plan
  file's current sha blocks the step (`REFUSED (no try used)`, exit 2) while any of its breaks has no accept record in
  owner-words.tsv. A changed plan sha, or no review at all, does not block (a changed plan prints that the red team should rerun).
- The hourly pass (`layers.py redteam input|record|due`, already built): routes print the ops-findings filing command
  `python3 skills/workflow-monitoring/scripts/mailbox.py finding TITLE --feature PAGE --found REF`.

## What each done line needs

1. plan-review and plan-record plus a test (in test-three-level.py, no new file) that wraps `open` and `subprocess.run` and proves
   only `loop/redteam/` is written, repo files unchanged, no merge, push, gh, send or commit; negative control: an unknown
   principle number is refused and nothing is recorded.
2. The gate: a break blocks (negative control 1: no block when the plan sha changed; negative control 2: no block when every break
   has an owner record; control 3: a made-up record id does not unblock); each proven red once.
3. The hourly pass exists; its routes name the ops-findings command. Tests as built.
4. Wording: two bullets under HLT-2 (a pre-build plan review, b hourly board pass), sent to operation-pc before any page is
   written; no new ID; no new file; regression rows stay 1300 (checks chain onto existing rows).

## Open questions

- PENDING: the HLT-2 wording (a) and (b), which the owner approves before merge.
