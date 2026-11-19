# Every hour and before any release ETA, a fresh-context reviewer session reads the board and both machines' latest STATUS and lists unverified assumptions, work idle capacity could start now, and the single biggest risk to the release time; each item becomes a TOP-DECISION or an ops-findings issue; it never edits, merges or decides (v2.0 per owner o236, TOP-DECISION 95)

- Slug: plan-red-team-v20
- Touches: not declared
- ETA: 220 active minutes (estimate 176m plus a 25% margin, rough)

## Done lines

Frozen. A wrong done line needs a new goal.

1. A red-team command builds the reviewer's input from the board and the latest STATUS per machine and records its three lists with a timestamp; a test proves it reads but never writes repo files, merges or sends decisions
2. It runs hourly and before a release ETA, and each listed item is routed to operation-top as a proposed TOP-DECISION or filed through ops-findings
3. Requirement wording goes to the owner before merge; no new shipped file unless a fold pays for it; net regression rows 0 or fewer

## Verify by hand

<!-- Numbered steps for a person, each with an Expect: line. A release needs this. -->
1. Run `python3 skills/workflow-monitoring/scripts/layers.py redteam input` in this repo.
   Expect: it prints `RED-TEAM INPUT <time>`, the board sections, one `STATUS <machine> (N min old)` line per machine and a request for `A:`, `I:` and exactly one `R:` line.
2. Write `A: assumption one`, `I: idle work one` and `R: the biggest risk` on three lines in a file and run `python3 skills/workflow-monitoring/scripts/layers.py redteam record <file>`.
   Expect: three lines `ROUTE ops-findings: A: ...`, `ROUTE TOP-DECISION (proposed): I: ...` and `ROUTE TOP-DECISION (proposed): R: ...`; `git status` shows no change and one JSON file appears in `.git/loop/redteam/`.
3. Run the record command again with a file holding two `R:` lines.
   Expect: `REFUSED: the reply has 2 R: lines`, and no new file in `.git/loop/redteam/`.
4. Run `python3 skills/workflow-monitoring/scripts/layers.py redteam due`, then again with `--eta <time 30 minutes from now as YYYY-MM-DDTHH:MM:SSZ>`.
   Expect: `RED-TEAM ok: last pass N minutes ago` just after a pass, and `RED-TEAM DUE: the release ETA is in 29 minutes ...` once the last pass is over 20 minutes old.
