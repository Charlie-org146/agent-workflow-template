# Design: budget-default-240

Problem: a goal's default active-time budget is 120 minutes; the owner wants 240 (o19: "Yes, let's do your thing.", covering time_budget_minutes and Guardrails). Three places carry the number: this repo's `.loop/config.json`, the settings table default (`skills/workflow-setup/scripts/settings.py`, rendered into `references/settings.md`, Home.md and START.md), and a test row that pins 120.

Approach A: change only this repo's config. Cheap, but new repos and the reference still say 120, so the done line fails.
Approach B (chosen): change the config, the settings table default and everything rendered from it, and the pinned test value; add one regression row that fails if the default goes back to 120.

Done line needs: config 240; settings.py default 240; settings.md, Home.md settings row and START.md re-rendered (settings.py reference --write, entry.py write, docs check); test-budget-enforce.py expectation moved to 240; one new row proven red.
Left alone: DECISIONS.md history text, SET-2 wording, the Guardrails requirements (the default is not stated in a requirement; the page needs a re-stamp only if docs check says so, under o19).
Open questions: none.
