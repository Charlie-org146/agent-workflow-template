# hard-eta: plan

Checked against the code: fit.py has frozen_fields (freeze), budget_stop (called by cmd_step and flow.py) and cmd_set (operation-only, goal.py set); guards.add_set writes the per-goal sidecar; auto.py holds owner_words_path and owner_words_add and the full-auto answers; checkin.py builds All sessions and Needs you; lean.py reads every run record for health's Hygiene rules and controls.py holds one fixture per rule; the Guardrails page is Reviewed with GRD-1 to GRD-12; proctree.py's TEMPLATE exists as an identical copy in delivery and monitoring.

Ordered build steps:
1. Room: move cmd_queue and cmd_adopt from fit.py to batch.py (fit keeps two forwarders); trim goal.py, checkin.py, lean.py and controls.py comments so each hook fits under 19,000 LF bytes. No file is added: the package stays at 99.
2. auto.py gets the ETA code: eta_new (estimate_full high end for the new goal's size, times 1.25, rounded up to 5 minutes, at least 30; fallback the time budget), eta_over, eta_ask (the three-choice waiting object), eta_gate (record check: an owner-words.tsv record covering the slug, unused by another ETA or budget change), eta_set (--eta-extend N, --eta-choice ship|defer) and eta_rows for health.
3. fit.py: frozen_fields records eta; budget_stop refuses past the ETA with ETA_PAST and stores the ask; cmd_set takes --eta-extend, --eta-choice and --owner-record, and a budget raise needs the record. goal.py: argparse flags, the goal file's ETA line (TEMPLATE in both proctree.py copies).
4. checkin.py: the left column shows each goal's ETA clock time; a goal past its ETA is a Needs-you item with the three choices; the full-auto answerer never answers an ETA ask.
5. Health: eta rules in lean.py (no ETA: WARN; extended without a record: FAIL; overrun not under Needs you: FAIL) and one control each in controls.py; settings and Home mention nothing new (no new setting).
6. Docs: Guardrails requirement GRD-13 (and sub-bullets) under owner record o52 via criteria.py, its Tests rows; START.md, SKILL.md command maps and references/commands.md for goal.py set's flags; DECISIONS.md.
7. Tests: dev/toy/test-hard-eta.py (freeze records the ETA and goal file line, a step past the ETA is refused with the ask, an extension without a record is refused, a budget raise without a record is refused, ship and defer enact, health rows with controls); regression rows seen red with `regression.py red`.

Test for each done line: line 1 by the freeze and check-in toy cases, line 2 by the gate, record and Needs-you cases, line 3 by the health rules and their controls; every row is seen failing before its code (red proof) and passing after.

What could break: the many toys that call `goal.py set --budget-minutes` without a record (they now need one or lower the budget); scripts near 19,000 bytes; the check-in's layout the reply hook checks (only cell text and Needs-you lines change); a toy that counts package files.

Out of scope: a per-repo eta_margin setting (the margin is a constant 25 percent), the release ETA as a clock time and fix-round counting (#4512 items 3 and 4: follow-ups), and any change to the time budget's default.

PENDING: none
