# Each step runs on the agent the config picks: Claude for heavy steps, Codex or another agent for cheap ones, with Claude fallback and run records naming agent, model and tokens.

- Slug: agent-routing
- Touches: not declared
- ETA: 195 active minutes (estimate 155m plus a 25% margin, rough)

## Done lines

Frozen. A wrong done line needs a new goal.

1. Given a config that routes build to Codex and review to Claude, when a small goal runs, then its build step runs through the Codex command, review runs on Claude, the run record names both agents and their token counts, and removing Codex from the machine makes build fall back to Claude with a one-line warning.

## Verify by hand

<!-- Numbered steps for a person, each with an Expect: line. A release needs this. -->
1. Run `python3 dev/toy/test-agent-routing.py`.
   Expect: every line starts with PASS and the last line is `PASS: agent-routing`.
2. Run `python3 skills/workflow-delivery/scripts/routing.py detect`.
   Expect: one `AGENT` line for `heavy` (claude) and one for `cheap` (codex), each saying installed and logged in, or `missing:` with the reason.
3. Run `python3 skills/workflow-delivery/scripts/routing.py resolve review --size small`, then `resolve build --size small` with `LOOP_AGENTS` pointing at a file holding `{"routes": {"sizes": {"small": "cheap"}}}`.
   Expect: review prints `ROUTE review: heavy (claude, ...)` and build prints `ROUTE build: cheap (codex, ...)`.
4. Write a file with `{"profiles": {"cheap": {"command": ["no-such-agent", "exec"]}}, "routes": {"steps": {"build": "cheap"}}}`, point `LOOP_AGENTS` at it and run `resolve build`.
   Expect: one line starting `AGENT_FALLBACK build: codex isn't installed; using claude (heavy)`.
