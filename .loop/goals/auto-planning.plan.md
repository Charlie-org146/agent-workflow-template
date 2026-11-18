# auto-planning: plan

Checked against the code: `monitor.py` (parse_queue, runs, pool, loop_dir, config, main), `auto.eta_new`, `graph.parse`/`graph.size`/`graph.assigned`,
`board_status.memory`, `routing.py` (resolve, load, exe, unavailable, usage, entry, WALLS, main), `fit.size_of` (SMALL_DONE 3) all exist.

## Build steps
1. `monitor.py`: add `plan` (and `plan approve`): backlog = queue lines with no `release:` and no `machine:`, minus goals with a run
   record, a pool entry or a slug in the peer plan file; release = next minor above VERSION, 6 goals per release, a goal after its
   dependencies; estimate and hard ETA from `auto.eta_new`; token budget from past runs; machine; agent profile; reason; pending
   plan JSON in `<loop>/plan-round.json`; message block for the other operation session; `approve` checks `owner-words.tsv`.
2. `routing.py`: add `check` (second agent's notes on the plan text, read-only; fallback to Claude with `AGENT_FALLBACK`), and `plan --check` calls it.
3. `dev/toy/test-auto-planning.py`: one toy repo, five checks, one per done line.
4. Docs: a MON-10 sub-bullet and two Monitoring PRD sentences (un-review via the operation session, o130), `commands.md` and SKILL.md command map, regression rows seen red, wiki tables re-rendered from committed data.

## Tests
One regression row per done line (category criterion, link auto-planning:N), each seen failing before the change (script missing) and passing now.

## Could break
Script sizes (monitor.py and routing.py stay under 19,000 bytes), an unreadable pool or run folder (plan treats an unknown pool as "nothing assigned" and says so), Windows paths (toy runs on native Windows).

## Out of scope
Starting goals from the plan (watch does that after approval), re-planning running goals (MON-10 replan.py), sending the message itself (the operation session does, with SendMessage), ETA choices (owner's, o115).
