# Design: eta-header-margin (#4519, #4528)

## Problem
Two follow-ups of the hard ETA (GRD-14, #4512). (1) The check-in's release header says when a release will finish from the goals' time-left estimates
(`left`), while each started goal now carries a hard ETA the owner holds it to; the header can promise a time the goals are allowed to overrun, or one they
are forbidden to pass. (2) The 25 percent margin over the estimate is a constant in auto.py, so a repo cannot tune its hard ETAs.

## Approaches
1. **Per-goal `hard` seconds on the check-in's items, the header takes the latest of them.** `auto.eta_left(seen, at)` gives each started goal's remaining hard ETA
   (None for a goal with no ETA or with open pre-flight items, whose ETA has not started); checkin.py puts it on the item; `board_status.release_header` takes the
   latest of the hard values and the estimates of goals without one, and appends "hard ETA for N, estimate for M" only when a hard ETA was used, so a board with
   none reads exactly as before. The margin: `eta_margin_percent` (default 25, 0 to 300) in settings.py, read by `auto.eta_margin(cfg)` in `eta_new`; the basis text names the percent.
2. **Compute the header from the run records inside board_status.** Rejected: board_status would load the sidecar and the pre-flight state itself, duplicating auto.eta_seen.

## Chosen
Approach 1: auto.py already owns the hard-ETA arithmetic; checkin.py (400 bytes of headroom) gains one expression.

## Done lines
- Done 1: `eta_left`, `hard` on items, the header text. Toy renders a throwaway repo through `checkin.render` (the real check-in) with one hard-ETA goal and one estimated goal,
  and a board with no hard ETAs (negative control: the header text is unchanged).
- Done 2: `eta_margin_percent` in the settings table (Home renders it), read by `eta_new` through `frozen_fields`. Toy: 40 percent moves a goal's hard ETA, the default gives today's value.

## Open questions
None: queued goals have no hard ETA until frozen, so the header keeps using the estimate for them (as it counts them "not started").
