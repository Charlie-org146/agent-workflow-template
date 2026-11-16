# Plan: eta-preflight

Claims checked against the code: `fit.frozen_fields` builds the freeze fields (size, budget, eta) that `goal.py new` and `batch.py` store on the run
record; `guards.add_set` writes owner-controlled sidecar settings that `auto.eta_seen` and `fit.view` read back (eta_extend, eta_choice use it);
`auto.eta_text` / `eta_over` / `eta_spent` are the ETA cell and the clock; `auto.eta_record` checks an owner-words record; `replan.memory_hold(cfg)`
already is the memory-floor dry run; `private.scan(top, None, texts=...)` scans text with the owner's list and redacts hits; checkin.py builds
Needs you from the live runs; goal.py record auto-approves a pending plan only when `auto_approve` is true. Size headroom (LF bytes): replan 7.4K,
fit 2.3K, auto 1.2K, goal 0.8K, checkin 0.1K; the package is at its 99-file cap, so no new file.

## Steps
1. replan.py: `preflight_new(root, cfg, slug, touches, minutes)` -> {"items": [...]} (plan approval when auto_approve is off; time budget; private-name,
   memory-floor and API-quota items only when the dry run would refuse), with `LOOP_API_QUOTA` as the test stand-in for the gh call.
2. replan.py: `preflight_open(seen)`, `preflight_lines(seen_runs)` (one Needs-you line per goal: items, options, recommendation, the word `recommended`),
   `preflight_answer(g, args, state, why)` (owner record, answers in the sidecar, the clock start), `preflight_pr(g, state)` (second dry run, logs misses).
3. auto.py: `eta_text` says "ETA after your answers (N open)"; `eta_over` is false while open; `eta_spent` counts from the answers.
4. fit.py: freeze stores `preflight`; `cmd_set --preflight` calls `preflight_answer`. goal.py: the `--preflight` flag, the pending-plan auto-approve line, one call in `cmd_pr`.
5. checkin.py: one line adds the pre-flight lines to Needs you (MON-19 ranking keeps working: the line starts with the slug).
6. Toy dev/toy/test-eta-preflight.py through goal.py's real main/cmd_new/cmd_set/cmd_pr; rows seen red with the new code broken.
7. Docs: Guardrails and Monitoring pages, commands.md; Tests tables re-rendered.

## Tests
- Done 1: freeze lists the items; the check-in shows one line with `recommended`; ETA reads "after your answers (N open)" then a clock; a set without a record is refused; a take-all answers everything; negative control: a goal with no open items reads the plain ETA.
- Done 2: the pr dry run logs a missed memory-floor and a missed private-name item; negative controls: an item already on the list is not logged, a clean dry run logs nothing; the real `cmd_pr` path goes through graph.pr_queue.

## What could break
auto.py/checkin.py near the cap (re-measure in LF); every run record without `preflight` must read as before (old goals: no items, plain ETA); eta_spent with no answers must be unchanged; the dry run must never raise (wrapped, a failure means no item).

## Out of scope
Dry-running a repo's own pre-push check; logging every later `goal.py wait` as a missed item; per-item custom answer text beyond the listed options.
