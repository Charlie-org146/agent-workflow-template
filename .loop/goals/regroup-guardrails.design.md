# Design: regroup-guardrails

## Problem
The v2 rewrite (prd-rewrite-to-10.md) regroups four features: Guardrails (19), Health (13), Operation (14) and Check-in and board (9). Monitoring becomes two pages. The text must arrive through the revision tooling (DOC-20) so every earlier wording stays as a numbered revision.

## Approaches
1. Apply every draft row with `criteria.py revise`/`retire`/`migrate`, keep the draft IDs, and give Monitoring's page to Operation by rename. Cost: one script run per requirement; risk: a same-ID move cannot be expressed as a retire.
2. Renumber Operation under a new prefix and retire all MON IDs as moved. Cost: every test row, How-to item and issue link changes ID; risk: an ID changes page and prefix for no gain.

## Chosen
Approach 1. `git mv` Monitoring.md and How-to-use-Monitoring.md to Operation (revision history stays); Check-in-and-board is new. MON-3/4/5/9/14/17/19 retire as moved to CHK-1/1/2/8/5/6/7; MON-n kept on Operation. New IDs (GRD-15..22, HLT-10..13, MON-20/23, CHK-1..9) collide with nothing, so none renumbers. HLT-2 is left to prd-principles. GRD-11/13/14 are not in the draft's Guardrails section, so they stay untouched. The tooling needs an owner record naming the page, so revisions cite o155 (o154 lists only the slugs).

## Done lines
a) revise/retire/migrate rows for all four pages. b) regression.tsv goal column re-pointed (126 rows), How-to items moved, Home, README link, docs.tsv, config topics. c) criteria.py render, wiki.py prepare, entry.py check. d) diff touches only those pages plus the generated files they require.

## Open questions
Guardrails holds 22 live requirements against criteria_max 19 until GRD-11/13/14 retire as moved (to REG-10, REG-14, DEL-17, owned by other goals).
