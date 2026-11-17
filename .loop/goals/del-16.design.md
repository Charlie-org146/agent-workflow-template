# Design: DEL-16 on the Delivery page

## Problem
agent-routing (v1.0.49) wrote requirement DEL-16, "Each step runs on the agent the config picks", on `docs/wiki/Delivery.md`, then took it out (commit d33bd506) because Delivery is Reviewed and editing it needs an un-review. Its regression row was left linked to the done line `agent-routing:1`, so no requirement names the feature on the wiki.

## Approaches
1. Re-add the original wording verbatim, un-review the Delivery page and DEL-16 only through the owner's record o139, leave both Unreviewed, relink the existing row to DEL-16. Cost: one page edit, one row relink, one covered row. Risk: low; the wording is the owner-visible text agent-routing already wrote.
2. Reword DEL-16 and add new tests. Cost: new wording needs a new review and new red proofs. Risk: changes what the owner approved to write, and this goal was only asked to put it on the page.

## Chosen
Approach 1. The wording is taken unchanged from `git show d33bd506 -- docs/wiki/Delivery.md`. The page is at 15 requirements, so DEL-16 fits under criteria_max 19. Only the Delivery page review line is un-reviewed (`criteria.py unreview Delivery --user --owner-record o139`); the other Reviewed requirements keep their seals. DEL-16 is written as `**Unreviewed**` and not stamped here. The owner stamps it.

## What each done line needs
1. The Delivery page holds DEL-16 with the original three sub-bullets, marked Unreviewed, and the page's Review line reads Unreviewed.
2. The existing `agent-routing` regression row (seen red 2026-11-17, `dev/toy/test-agent-routing.py`) gets goal `DEL-16`; a `covered` row `done-agent-routing-1` keeps the done line `agent-routing:1` linked to it. `criteria.py render` refreshes the Tests tables from committed data only, and `workflow-docs check` prints DOCS OK.

## Open questions
None for the owner beyond the review stamp, which stays theirs.
