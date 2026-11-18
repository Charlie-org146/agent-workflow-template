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

1. Run `python3 dev/toy/test-three-level.py`.
   Expect: every line is PASS and the last line is ALL PASS.
2. Open the Operation and Check-in-and-board wiki pages and read OPS-1, OPS-2, OPS-11, OPS-16, OPS-23, CHK-1 and CHK-2.
   Expect: each has one added sub-bullet about the three layers, STATUS, the safety rules, busy machines, the one-token tool list, the 5-minute board or the machine one-line check-in, and each is Unreviewed with a new revision row.
3. Open the two Linux CI runs cited in the pull request for the row reply-hook-scope.
   Expect: the first (reply_hook.py at main's version) prints FAIL reply-hook-scope on the machine-mode check; the second (the re-landed version) prints PASS reply-hook-scope.

