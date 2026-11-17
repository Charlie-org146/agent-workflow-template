# full-auto-all: full auto takes every recommended answer unless the decision is a safety class (#4831)

- Slug: full-auto-all
- Touches: skills/workflow-monitoring, skills/workflow-docs, skills/workflow-health, docs/wiki/Monitoring.md, docs/wiki/Guardrails.md, .loop/regression.tsv, dev/toy
- ETA: 250 active minutes (estimate 198m plus a 25% margin)

## Done lines

Frozen. A wrong done line needs a new goal.

1. Given waiting questions of kinds routine, owner (an un-review, a row cap, a budget) and security, when auto.py pass runs with full_auto on, then the first two are answered with their recommendation and logged with --source auto, the o118 rule record and revert words, and the security one still waits under Needs you
2. Destructive, money, security, private-data, steward-merge and always-ask questions are never auto-answered: a regression row proves it, with a negative control that goes red when the safety guard is removed
3. Every auto answer carries the standing rule record id (health checks it), and single-use owner records (pre-flight budget items, page un-reviews) no longer force the owner to answer a non-safety question by hand; changed requirement wording still goes back to Unreviewed without blocking the goal
4. The PR adds no new shipped file and its body shows the owner the token-diet MON-5 and Guardrails/Monitoring requirement diff, left Unreviewed (not stamped)

## Verify by hand

<!-- Numbered steps for a person, each with an Expect: line. A release needs this. -->

1. Run `python3 dev/toy/test-full-auto-all.py`.
   Expect: every line starts with PASS (an owner un-review, a row cap and a budget are answered; the security question and every safety class wait; the negative control line says the guard-less question is answered).
2. Run `echo "Raise criteria_max from 18 to 19?" | python3 skills/workflow-monitoring/scripts/auto.py decide-text --kind owner --recommend yes`.
   Expect: it prints AUTO.
3. Run `echo "Print the API key into the log?" | python3 skills/workflow-monitoring/scripts/auto.py decide-text --kind owner --recommend yes`.
   Expect: it prints WAITS: safety class security: api key.
4. Open `docs/wiki/Monitoring.md`.
   Expect: MON-11 and MON-5 both read Unreviewed (nothing was stamped), and MON-11 names the standing rule and the safety classes.

