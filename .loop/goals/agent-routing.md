# Each step runs on the agent the config picks: Claude for heavy steps, Codex or another agent for cheap ones, with Claude fallback and run records naming agent, model and tokens.

- Slug: agent-routing
- Touches: not declared
- ETA: 195 active minutes (estimate 155m plus a 25% margin, rough)

## Done lines

Frozen. A wrong done line needs a new goal.

1. Given a config that routes build to Codex and review to Claude, when a small goal runs, then its build step runs through the Codex command, review runs on Claude, the run record names both agents and their token counts, and removing Codex from the machine makes build fall back to Claude with a one-line warning.

## Verify by hand

<!-- Numbered steps for a person, each with an Expect: line. A release needs this. -->
