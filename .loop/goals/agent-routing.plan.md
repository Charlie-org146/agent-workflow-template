# Plan: agent-routing

Checked against the code: `flow.py` runs idea/plan/review/qa/ship (in the worker session, or headless through the flow
file's command); build is run by the worker itself after `goal.py step SLUG build`; `role.usage` parses Claude JSON for
tokens; `guards.add_tokens` (aliased in `goal.py`) is the one place `goal.py record` adds a step's tokens; the run
record is `.git/loop/runs/<slug>.json` (`tokens`, `size`). `flow.py`, `goal.py` and `role.py` are within 100 bytes of the
19,000-byte script cap, so the new logic lives in a new `routing.py` and the hooks are one-liners.

## Build steps
1. `skills/workflow-delivery/scripts/routing.py` (under 19,000 bytes): `load()` for `~/.workflow-loop/agents.json`
   (`$LOOP_AGENTS`) with default profiles; `resolve(step, size)`; `available(profile)` (installed through
   `shutil.which`, `.cmd` shim on Windows, plus an optional login probe); `usage(profile, text)` for the claude-json and
   codex-jsonl output formats; `add_tokens(state, step, given)` (wraps `guards.add_tokens` and notes the heavy agent
   in `state["agents"]`); CLI `build SLUG`, `detect [--write]`, `show SLUG`.
2. Hooks: `goal.py` imports `routing` and aliases `add_tokens = routing.add_tokens`; drop the unused `MAX_TRIES`
   line to stay under the cap.
3. `workflow-delivery` SKILL.md and `references/commands.md`: the Build step runs `routing.py build SLUG` after
   `goal.py step`, and the routing entries in the Command map; `workflow-setup` SKILL.md Command map gets `agents-detect`.
4. `dev/toy/test-agent-routing.py`: fake agents; one regression row per behaviour of the done line; Delivery PRD
   requirement DEL-16 with its Tests rows.
5. A real `codex.cmd exec` smoke run by hand (Verify by hand).

## Tests (each seen failing before)
- routed build runs through the Codex command, its tokens and agent land in the record.
- review resolves to the heavy profile even when sizes route small goals to cheap; it moves only when `routes.steps.review` is set.
- the record names both agents (codex for build, claude for review) with token counts.
- the Codex command missing: build falls back to heavy, one `AGENT_FALLBACK` line, record carries the reason.
- a new profile (`local`) added to the file routes with no code change.

## What could break
Scripts over the size cap (checked by the existing row); Windows `.cmd` quoting (prompt goes on stdin); a dirty
worktree after a failed Codex run (the run commits nothing on failure and reports `BUILD FAILED`).

## Out of scope
Routing idea, plan, qa and ship through cheap agents (they stay in the worker session; the config accepts the keys and
`resolve` answers for them), another agent's real run, the machine-setup (#4780) call, cost data for token-diet.
