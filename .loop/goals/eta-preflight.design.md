# Design: eta-preflight (#4535)

## Problem
A goal's hard ETA (GRD-14, #4512) is only fair if the goal can run without waiting, but most waits seen on a busy day were owner inputs that were
knowable at freeze: a plan approval, a guard refusing every push, a memory floor above the free memory, an empty API quota, a time budget that
counted waiting. They were asked only when the goal reached them, so each pushed the goal past its ETA.

## Approaches
1. **A pre-flight list on the run record, shown as one Needs-you line, answered with owner words, with the ETA clock starting at the answers.**
   Freeze computes the list (`replan.preflight_new`): plan approval (when auto_approve is off), the time budget, and the dry runs: the private-name
   scan on the file names the goal will touch and the pages every pr re-renders, the memory floor against free memory, the GitHub API quota; a
   dry run appears as an item only when it would refuse. The answers live in the owner-controlled sidecar (`guards.add_set`, like eta_extend),
   `goal.py set --preflight recommended|ID=ANSWER --owner-record`; the check-in prints one line per goal; `auto.eta_text` reads "ETA after
   your answers (N open)" while any item is open, `eta_over` stays false, and the clock counts from the moment the last item was answered.
   At the pr step the same dry runs run again; a refusal that was not in the list is logged as a missed pre-flight item.
2. **Block the goal on a wait at freeze** (use `goal.py wait`). Rejected: it stops goals that could do their first steps, and a worker's
   `wait` cannot carry several items or a take-all word.

## Chosen
Approach 1. Code goes into replan.py (the module with room: no new file, the package is at its file cap); auto.py, fit.py, goal.py and
checkin.py get one or two lines each, because they sit within 1 KB of the 20 KB script cap.

## Done lines
- Done 1: `preflight_new` at freeze, the Needs-you line in the check-in, the one word "recommended", `eta_text` "after your answers (N open)",
  the clock starting at the answers. Toy: freeze through goal.py's real `new`, the check-in line, the ETA text, `goal.py set --preflight`.
- Done 2: `preflight_pr` before the pr queue join runs the private-name scan and the memory floor again; a finding not on the list is logged
  (`missed_preflight` on the record, and one line in the log) with why it was not foreseen; negative controls: a clean dry run and an item that
  was on the list log nothing. Toy runs goal.py's real `cmd_pr` path up to the queue join through graph.pr_queue (last night's pr_join slip).

## Open questions
- A repo's own pre-push check cannot be dry-run safely (it is arbitrary code); out of scope, filed as a backlog line.
- A worker's later `goal.py wait` is not logged as a missed item yet (goal.py has no room): backlog.
