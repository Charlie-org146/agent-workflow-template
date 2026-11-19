# Two rows red on main pass again: settings-render-tables (dev/render_tables_check.py checks the page that now holds the settings and automation tables, Home or Automation, not the principles-only README; #5031) and runbook-repo (Health's health-round runbook states anthropic_api_key, judge_command and 'not run on the runner' if true, else the toy is aligned; #4120) (TOP-DECISION 17 and 21, o182, o185)

- Slug: main-red-cleanups
- Touches: not declared
- ETA: 240 active minutes (estimate 192m plus a 25% margin, rough)

## Done lines

Frozen. A wrong done line needs a new goal.

1. Given main after v2 (README principles-only with its o170 sentence), when settings-render-tables and runbook-repo run on Linux CI, then both pass, and the known rows citing #5031 and #4120 are removed in the same change.
2. Only render_tables_check.py, Health's runbook section (or test-runbook.sh), their toys and the two known-row lines change; net rows added are zero; #4120 and #5043 are cross-linked so the reply-hook fix doesn't chase runbook-repo twice.

## Verify by hand

<!-- Numbered steps for a person, each with an Expect: line. A release needs this. -->
