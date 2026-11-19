# Plan: regroup-guardrails

Checked against the code and reviewed by an independent reader: `criteria.py revise|retire|migrate|guard` are in skills/workflow-docs/scripts/milestones.py; revise() rejects a retire target equal to its own ID, revcheck() is per page, guard() uses `git diff --no-renames` so a vanished page refuses every Reviewed requirement on it. The owner-record lookup reads `<git dir>/loop/owner-words.tsv` and needs the page or ID in the record's list (o155 has it, o154 does not). migrate needs `--page` for pages outside the original nine.

## Build steps
1. Write the Operation page (OPS-n) and the Check-in-and-board page (CHK-n) from the draft text; `migrate --owner-record o155 --page P` gives each its r1 row.
2. Revise GRD-1..10 and 12, HLT-1, 3..9 (not HLT-2); add GRD-15..22 and HLT-10..13.
3. Retire MON-1..19 on Monitoring.md as moved to OPS-n or CHK-n; Monitoring.md stays so guard sees every ID accounted for.
4. Re-point the regression.tsv goal column (MON to OPS or CHK); docs.tsv, config topics, Home rows, README link; How-to pages; repair the toy tests that read the Monitoring page; re-record the mon5 wording row red.
5. `criteria.py render`, `entry.py write`, `docs.py check`, `criteria.py guard`.

## Tests per done line
a) guard prints GUARD OK and docs.py check has no REVISION or IDS finding. b) no LINK or HOWTO finding; MON ids resolve through moved-to markers. c) lane rows pass, render clean, wiki.py prepare clean, entry.py check ENTRY OK. d) the diff lists the allowed pages plus files the checks require (docs.tsv, config topics, README link, START.md, How-to pages, toy tests that read the renamed page).

## What could break
Guardrails stays over criteria_max 19 until GRD-11/13/14 retire as moved (REG-10, REG-14, DEL-17 from other goals): the pull request is held until those merge. Toy tests that read pages are skipped on Windows and were adjusted by reading.

## Out of scope
HLT-2 (prd-principles), Setup.md, Roadmap.md, requirements outside these features, moving detail text to How-to pages, criteria_max.
