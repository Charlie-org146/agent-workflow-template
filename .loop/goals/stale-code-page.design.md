# Design: stale-code-page

## Problem
A goal's code change makes the wiki pages that map that code stale. The pr and ship lanes judge the docs rows (`review-findings-skill-lines`, `settings-render-fresh`) before anything re-stamps those pages, so the goal loses a try; today only the operation session can re-stamp, and only through `operate.py apply` on a pushed branch (#4442). A page whose Review line is Unreviewed could not be re-stamped at all.

## Approaches
1. The lane prep, which already commits the re-rendered Tests tables before the rows run, also runs `audit.py restamp-own SLUG`: it lists the pages `docs.py check --own` calls stale and relocks them (the same relock `operate.py apply` uses). The pages ride in the prep commit. Cost: one new audit.py function and a call in lanekit.prep. Risk: stamping a page whose wording changed, which relock already refuses.
2. Make `goal.py pr` call operate.py apply itself. Rejected: it needs a pushed branch and the operation session's role.

## Chosen
Approach 1, for Reviewed pages (stamp refreshed only while the reviewed text still matches) and for Unreviewed pages (a `kept` marker, as for How-to-use pages, only while the page is as committed).

## What each done line needs
1. The prep re-stamps a Reviewed and an Unreviewed page that only mapped code staled, in its commit, so docs check --own is clean before the rows run (toy, rows stale-code-page-reviewed and -unreviewed).
2. A Reviewed page whose reviewed wording changed is not re-stamped and stays stale (negative control, row stale-code-page-wording).

## Open questions
None.
