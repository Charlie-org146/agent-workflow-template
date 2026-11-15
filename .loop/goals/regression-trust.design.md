# Design: regression-trust

## Problem

Four open issues erode trust in the regression lanes. I read each against the code on origin/main (v0.28.61):
- #531: after a base merge, nearly every row "reaches" the goal file, and `tiers.plan` sorts only the root runners and "names" rows last (tiers.py:277), so reach rows sit with the goal's own new rows and fill the 15-minute budget first.
- #3911: when a row ending in `| grep -q PATTERN` fails inside a lane, the lane prints a bare `FAIL id`. The text that explains it exists (rowtail makes the quiet stage loud, defect 3789) but is only used for issue bodies, never for the lane's own output (runs.py:206 prints the row's raw text, which is empty).
- #3907: `runs.owed_clear` (runs.py:315) prints "OWED CLEARED id: close its issue" but never closes the other-machine to-do issue it holds in column 4.
- #3908: asks that skill-governs-line's and adopt-set-3's proofs be recorded as owed. Both rows are already seen failing (skill-says-governs and skill-kept 2026-11-13, adopt-set-3 2026-11-08), there is no `.loop/regression-owed.tsv`, and a row seen failing owes nothing (runs.owed_record refuses it). Already fixed.

## Approaches

**A. One change per issue, each with its own toy row.** #531: rank the plan order new, failure, changed, reaches, then root runner and names. #3911: compute the row's loud tail first and print it in the lane. #3907: `owed_clear` closes the issue with a comment when live (gh stubbed in the toy). #3908: close with proof. Cost: four small edits plus four toys. Risk: low; each is in one function.

**B. A new "trust" module.** Gathers the ordering, tails and owed handling. Cost: a new file in a package at its file cap (99 of 99). Rejected.

## Chosen: A

It keeps each fix small and testable, and adds no file to the package. The toys are shell-neutral Python.

## What each done line needs

1. #3911: a toy runs `runs.execute` with `reuse` on a failing grep -q row and checks the lane's stderr holds the row's own text.
2. #531: a toy builds a todo list with reach, new, failure and root rows and checks the new and failure rows come first.
3. #3908 and #3907: #3907 gets a toy with a stubbed gh that sees `issue close` on the recorded issue; #3908 is closed with the proof lines.
4. Shell-neutral toys; lane start memory gate of 3.0 GB is operation's setting (min_free_memory_gb), checked in config, not built here. Reviewed page wording: none expected; if needed it goes to operation as a sentence.

## Open questions

- Whether #3907 should close the issue only when live (a token is set). Recommended: yes, as `owed_issue` opens it only when live.
- The exact order of the "changed" and "failure" kinds. Recommended: new, failure, other changed, reaches, then picks.
