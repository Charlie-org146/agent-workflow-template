# Guardrails, Health, Operation, and Check-in and board carry the v2 rewrite text through the revision tooling, with Monitoring split into Operation and Check-in and board

- Slug: regroup-guardrails
- Touches: docs/wiki/Guardrails.md, docs/wiki/Health.md, docs/wiki/Monitoring.md, docs/wiki/Operation.md, docs/wiki/Check-in-and-board.md, docs/wiki/Home.md, docs/wiki/Tests.md, .loop/regression.tsv
- ETA: 230 active minutes (estimate 182m plus a 25% margin)

## Done lines

Frozen. A wrong done line needs a new goal.

1. Given the Guardrails, Health and Monitoring pages, when this goal merges, then every requirement in the Guardrails, Health, Operation and Check-in and board sections of prd-rewrite-to-10.md (19, 13, 14, 9) has that text on its page as a new revision through the revision tooling, with Operation and Check-in and board added, every Monitoring requirement retired as moved to its new ID, and GRD-20 to GRD-22 and CHK-9 added; HLT-2 is left to prd-principles, and no requirement outside these features changes.
2. Given a moved or renumbered requirement, when the docs and health checks run, then every test row, issue link and How-to item that cited its old ID points at the new ID, the old ID still resolves through its moved-to marker, and Home lists the pages that exist after the split with their milestones and Topic as before.
3. Given this goal's branch, when its lane and checks run, then the Tests tables re-render with zero regression rows added net, each new rule has a row seen failing and passing, wiki.py prepare is clean and entry.py check prints ENTRY OK.
4. Given this goal's diff, when it is compared with main, then no shipped file is added, no script crosses a size line it was under on main, and no page other than Guardrails, Health, Monitoring, Operation, Check-in and board, Home and the Tests page changes.

## Verify by hand

<!-- Numbered steps for a person, each with an Expect: line. A release needs this. -->
