# Plan: regroup-guardrails

Checked against the code: `criteria.py revise|retire|migrate` live in skills/workflow-docs/scripts/milestones.py (revise() rejects a retire target equal to its own ID, revcheck() is per page), the owner-record lookup reads `<git dir>/loop/owner-words.tsv` and needs the page or ID in the record's list (o155 has it, o154 does not).

## Build steps
1. git mv Monitoring.md and How-to-use-Monitoring.md to Operation; retitle; write the Check-in-and-board page.
2. Add the draft's new requirements (GRD-15..22, HLT-10..13, MON-20/23, CHK-1..9) and run `criteria.py migrate --owner-record o155` per page for their r1 rows.
3. `criteria.py revise` each existing requirement whose draft text differs (GRD 11, HLT 8, MON 10); `retire --as moved:CHK-n` for MON-3/4/5/9/14/17/19.
4. Re-point regression.tsv goal column; docs.tsv, config topics, Home rows, README link; How-to pages (new items, moved items, new page).
5. `criteria.py render`, `entry.py write`, `docs.py check`, then repair toy tests that read the renamed or revised Monitoring page.

## Tests per done line
a) docs.py check passes revcheck (REV-ROW/IDS) for the four pages. b) docs.py check LINK/HOWTO/FORMAT clean; old IDs resolve through Retired markers. c) the lane's affected rows, render clean, wiki.py prepare clean, entry.py check ENTRY OK. d) `git diff --stat origin/main` lists only the allowed pages and generated files.

## What could break
Toy tests that read docs/wiki/Monitoring.md or assert MON requirements Reviewed (test-batch, test-checkin-view, test-operate, test-pods, test-runbook); the Guardrails page is over criteria_max 19 until GRD-11/13/14 retire elsewhere.

## Out of scope
HLT-2 (prd-principles), Setup.md, requirements outside these features, moving detail text to How-to pages.
