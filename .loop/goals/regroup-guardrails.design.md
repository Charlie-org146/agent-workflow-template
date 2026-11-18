# Design: regroup-guardrails

## Problem
The v2 rewrite (prd-rewrite-to-10.md) regroups four features: Guardrails (19), Health (13), Operation (14) and Check-in and board (9). Monitoring becomes two pages. The text must arrive through the revision tooling (DOC-20) so every earlier wording stays as a numbered revision.

## Approaches
1. Rename Monitoring to Operation and keep the MON IDs. Cost: one script run per requirement; risk: a same-ID move cannot be expressed as a retire, and guard refuses the vanished page.
2. New OPS IDs on a new page, every MON ID retired as moved. Cost: every test row and How-to item changes ID; risk: none for the checks.

## Chosen
Approach 2 in a narrowed form, after review showed `criteria.py guard` refuses a Reviewed requirement that vanishes from its page: Monitoring.md stays, every MON-1..19 retires as moved to its new ID (OPS-n on the new Operation page, CHK-n on the new Check-in-and-board page, keeping the draft's numbers). Operation and Check-in-and-board are new pages. New IDs (GRD-15..22, HLT-10..13, MON-20/23, CHK-1..9) collide with nothing, so none renumbers. HLT-2 is left to prd-principles. GRD-11/13/14 are not in the draft's Guardrails section, so they stay untouched. The tooling needs an owner record naming the page, so revisions cite o155 (o154 lists only the slugs).

## Done lines
a) revise/retire/migrate rows for all four pages. b) regression.tsv goal column re-pointed (126 rows), How-to items moved, Home, README link, docs.tsv, config topics. c) criteria.py render, wiki.py prepare, entry.py check. d) diff touches only those pages plus the generated files they require.

## Open questions
Guardrails holds 22 live requirements against criteria_max 19 until GRD-11/13/14 retire as moved (to REG-10, REG-14, DEL-17, owned by other goals).
