# kept-fragments: design

## Problem
A goal that changes code a wiki page maps to must leave a commit on that page, or `docs.py check` says STALE (docs.problems
counts commits to the mapped code since the page's last commit). The lane does it with a stamp: audit.py `relock` and
`restamp_own` rewrite the page's `Review:` line with `<!-- kept GOAL@SHA -->`, and for a How-to page append the same line at
the end. Two goals that re-stamp one page edit the same line, so they conflict (TD228, TD231). This is part (a) of the split of
generated-on-main; the Tests tables, run results and release render are (b), the guard and migration (c).

## Approaches
1. Keep the stamp on the page but derive its sha at merge time. Still edits a shared line on every branch. Rejected.
2. The towncrier shape: the stamp is a line in the goal's own `.loop/kept/<slug>.tsv` (`page<TAB>sha`); freshness counts a
   commit that adds the page's name there as a commit of the page. Chosen.

## Chosen
- audit.py: `relock`'s kept branches (Unreviewed, Reviewed with no hash movement) and the How-to branch call one helper
  `keep(root, slug, pages)` that appends `page<TAB>sha` to `.loop/kept/<slug>.tsv` and commits just that file
  ("Kept: <slug>"), leaving every page untouched. The prd hash rewrite for an owner relock is unchanged (not a stamp).
- docs.py `problems`: `seen` also holds the shas of commits that added the page's name to `.loop/kept/` (`git log -G`), so the
  page is judged fresh from that commit on. Old `<!-- kept -->` markers stay legal (prd.REVIEW) and stay valid by their commit.
- A page whose fragment is missing and whose code moved is STALE as before (negative control).
- No requirement text changes; no new shipped file (`.loop/kept/` is data).

## What each done line needs
1. A toy: three fixture branches stamp the same page; merge in all orders; no conflict; `docs.py check` output is equal.
2. A toy: page with fragment and no marker is fresh; same page without the fragment is STALE.
3. Size: audit.py (18,909), docs.py (18,470), criteria.py (18,980) each end no larger; the marker-writing code is deleted to pay
   for `keep`. Net rows 0 (assertions folded into an existing docs row).

## Open questions (recommended answers taken)
- The fragment commit is made by `keep` itself so lanekit.prep (part b) sees a clean tree; no lanekit change here.
- Fragments are not deleted at release in (a); (b) does that with the render.
- If criteria.py needs no change, it stays untouched.
