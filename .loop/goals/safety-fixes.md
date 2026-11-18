# safety-fixes: a routing timeout stops the agent's whole process tree, and full_auto defaults to off in the template (o146)

- Slug: safety-fixes
- Touches: skills/workflow-delivery/scripts/routing.py, skills/workflow-setup/scripts/settings.py, skills/workflow-monitoring/scripts/auto.py, skills/workflow-setup/references/settings.md, skills/workflow-monitoring/references/commands.md, docs/wiki/Home.md, README.md, dev/toy, .loop/regression.tsv, docs/wiki/Delivery.md, docs/wiki/Setup.md, docs/wiki/Tests.md, docs/wiki/Guardrails.md
- ETA: 235 active minutes (estimate 186m plus a 25% margin)

## Done lines

Frozen. A wrong done line needs a new goal.

1. Given a routed build agent that has started a child of its own and then passes its timeout, when routing.py stops it, then the agent and its child are both gone (the agent is started through the proctree helper the flow steps use); one new regression row proves it and fails when the old subprocess.run(timeout) is put back
2. Given a repo adopted from the template with no full_auto key, when settings.py reports the setting, then the default is false and its help text says so; this repo's .loop/config.json keeps full_auto true, and a regression row already in the suite is extended (no new row) to prove both
3. The pull request adds at most 1 regression row net, no new shipped file, leaves every script under 19,000 bytes, adds no reworded Reviewed requirement (MON-11's 'on by default' wording, if it says so, is listed under Needs owner review in the PR), and shows no red row beyond the known main reds

## Verify by hand

<!-- Numbered steps for a person, each with an Expect: line. A release needs this. -->
