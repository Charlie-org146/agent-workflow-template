# Re-land three-level-ops (reverted from v1.0.72 because it merged without MERGE-GO) in its proper order, ported onto the regrouped Monitoring/OPS/CHK pages, with its reply-hook change proven on Linux

- Slug: three-level-ops-reland
- Touches: not declared
- ETA: 295 active minutes (estimate 234m plus a 25% margin, rough)

## Done lines

Frozen. A wrong done line needs a new goal.

1. The content of three-level-ops (PR #5048: the three layers in the Monitoring spec, operate.py top and machine roles, the enforced defaults with their checks, reply_hook.py machine mode) is on this branch again, ported onto the pages regroup-regression and regroup-guardrails produce, within criteria_max, with requirement changes made as new revisions through the revision tooling
2. The reply-hook machine-mode test row is shown red then green on Linux CI (both runs cited in the PR), and the PR's Linux CI shows no reply-hook, guards-resume or mon15 row newly red compared with main (those five are main's own reds, #5043)
3. Nothing else changes; net test rows grow by at most 11

## Verify by hand

<!-- Numbered steps for a person, each with an Expect: line. A release needs this. -->
