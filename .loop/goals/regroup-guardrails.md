# Guardrails, Health, Operation, and Check-in and board carry the v2 rewrite text through the revision tooling, with Monitoring split into Operation and Check-in and board

- Slug: regroup-guardrails
- Touches: docs/wiki/Guardrails.md, docs/wiki/Health.md, docs/wiki/Monitoring.md, docs/wiki/Operation.md, docs/wiki/Check-in-and-board.md, docs/wiki/Home.md, docs/wiki/Tests.md, .loop/regression.tsv, docs/wiki/Delivery.md, docs/wiki/Regression.md, docs/wiki/Documentation.md
- ETA: 230 active minutes (estimate 182m plus a 25% margin)

## Done lines

Frozen. A wrong done line needs a new goal.

1. Given the Guardrails, Health and Monitoring pages, when this goal merges, then every requirement in the Guardrails, Health, Operation and Check-in and board sections of prd-rewrite-to-10.md (19, 13, 14, 9) has that text on its page as a new revision through the revision tooling, with Operation and Check-in and board added, every Monitoring requirement retired as moved to its new ID, and GRD-20 to GRD-22 and CHK-9 added; HLT-2 is left to prd-principles, and no requirement outside these features changes.
2. Given a moved or renumbered requirement, when the docs and health checks run, then every test row, issue link and How-to item that cited its old ID points at the new ID, the old ID still resolves through its moved-to marker, and Home lists the pages that exist after the split with their milestones and Topic as before.
3. Given this goal's branch, when its lane and checks run, then the Tests tables re-render with zero regression rows added net, each new rule has a row seen failing and passing, wiki.py prepare is clean and entry.py check prints ENTRY OK.
4. Given this goal's diff, when it is compared with main, then no shipped file is added, no script crosses a size line it was under on main, and no page other than Guardrails, Health, Monitoring, Operation, Check-in and board, Home and the Tests page changes.

## Verify by hand

1. Open `docs/wiki/Operation.md` and `docs/wiki/Check-in-and-board.md`.
   Expect: Operation holds OPS-1 to OPS-23 and Check-in and board holds CHK-1 to CHK-9, each with a Revisions table starting at r1.
2. Open `docs/wiki/Monitoring.md`, section Revisions, and read the Retired list.
   Expect: MON-1 to MON-19 each read "moved to" an OPS or CHK ID, and the page has no live requirement.
3. Run `python3 skills/workflow-docs/scripts/criteria.py guard origin/main regroup-guardrails` and `python3 skills/workflow-docs/scripts/docs.py check`.
   Expect: GUARD OK, and no REVISION, IDS, LINK or HOWTO line (the Guardrails CAP line goes once GRD-11, GRD-13 and GRD-14 retire as moved).
4. Open `docs/wiki/Home.md`.
   Expect: rows for Monitoring, Operation and Check-in-and-board, each Build loop, each on milestone 6.
