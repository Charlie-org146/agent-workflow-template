# Design: agent-routing

## Problem
A goal runs only on Claude: app worker sessions, and `agent_command` for headless runs. Cheap steps (small builds, lane
reruns, summaries) cost heavy-model tokens. The owner wants a config that picks the agent per step and per goal size,
with Claude kept for heavy work and review, Codex first, other agents later by adding one profile.

## Approaches
1. **Routing module in delivery, private agents file (chosen).** One new `skills/workflow-delivery/scripts/routing.py`
   reads `~/.workflow-loop/agents.json` (`$LOOP_AGENTS`): `profiles` (command, model, cost per million tokens, an
   optional login probe) and `routes` (`steps`, `sizes`, `fallback`). `resolve()` picks a profile, checks the agent is
   installed and logged in, else falls back to `heavy` with a one-line `AGENT_FALLBACK` warning. A step routed off
   Claude runs headless through the profile's command, with the prompt on stdin (Windows `.cmd` shims mangle multi-line
   arguments), `codex.cmd` resolved through `shutil.which`. Cost: one script, small hooks in `flow.py`/`goal.py`.
   Risk: Codex's output format differs; parsed in one place and covered by a test with a fake agent.
2. **Add a second `agent_command` per step to `.loop/config.json`.** Smaller, but repo-level (profiles hold machine
   facts such as what is installed), no size routing, no fallback, no onboarding. Rejected.

## Chosen shape
- Config: `profiles.heavy` (Claude) and `profiles.cheap` (Codex) by default; `routes.steps[step]` beats
  `routes.sizes[size]` beats `heavy`. Review is always `heavy` unless `routes.steps.review` is set explicitly (the
  config saying otherwise). Adding an agent is one profile entry plus a route; no code change.
- Run: `goal.py build SLUG` runs the build through its routed profile (commit included); `flow.py` uses the routed
  profile's command for idea, plan, qa and ship when it is not heavy; heavy steps stay in the worker session.
- Record: the run record gains `agents[step] = {profile, agent, model, tokens, cost_usd, fallback?}`; heavy
  in-session steps are noted at `goal.py record` with the tokens reported. Step tokens still add into `tokens`, so the
  token budget counts every agent.
- Onboarding: `routing.py detect [--write]` asks which agents are installed and logged in and writes the profiles into
  the private file; `workflow-setup` lists it as its `agents-detect` ask. Machine setup (#4780) calls the same command later.

## Done line needs
1. Routing config -> `resolve()`, a headless run of the build through the Codex command, a heavy review, the record
   naming both agents with token counts, and the Codex-missing fallback with its one-line warning. A test drives all of
   it with fake agent scripts, plus one real `codex exec` smoke run by hand.

## Open questions
- Size routes use the goal's frozen size (`small` or not); a finer scale waits for token-diet data.
- The cost-per-token numbers are the owner's to set; the defaults are public list prices and only feed the record.
