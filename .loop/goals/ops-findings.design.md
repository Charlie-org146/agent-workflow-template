# Design: the operation layer files its own findings

## Problem

Top and machine sessions meet process problems while scheduling, merging and deciding (tonight: #5167 to #5181). They were
filed by hand, with no rule on duplicates, safety or where they land, and the check-in never said what was filed. The
delivery loop already has its own findings (`goal.py finding`, `milestone.py leftovers`); this must stay separate from it.

## Approaches

1. A new script `finding.py` in workflow-monitoring. Cleanest, but the package is at its 100-file cap, so it needs a fold
   elsewhere; risk: a size or file-count row goes red.
2. A `finding` command in `layers.py` (top and machine session logic, 13.5 KB), logging to `findings.log` in the git common
   loop folder, which `checkin.py` reads through `auto.since` (the way Auto-answered works). No new shipped file; cost: both
   scripts stay under 19,000 bytes only if the code is tight. Chosen.

## What each done line needs

1. `layers.py finding TITLE --feature PAGE --found REF`: refuses a missing `--found` and private values; reads the open
   issues first (an unreadable list files nothing); refuses a repeat (same normalised title, or the same IDs in the title with
   half its words); makes `Backlog: <PAGE>` ("Other" when no page matches) if missing; files an issue labelled `backlog` and
   `ops-finding` whose body names REF. Negative controls: a repeat by title, a repeat by IDs.
2. The check-in prints `Findings filed (operation layer):` from `findings.log` since the last check-in. A finding in a
   safety class (`auto.CLASSES`) is refused unless `--owner-words oN` names an owner record that lists `*`, `ops-findings`,
   the page or an ID in the title. Negative controls: no words, words that list other IDs.
3. Requirement OPS-24 (Operation page, Unreviewed) goes to the operation session before the commit is pushed; it merges only
   after the v2.0 tag; no new shipped file; one regression row added and two folded into one (net 0).

## Open questions

None for the owner. Note: the safety classes are broad (`grant`, `delete`, `release` match), so such findings need the
owner's words; a standing record listing `ops-findings` covers them all.
