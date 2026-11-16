# audit-cd-path design

## Problem
`audit.untested()` reports "test no longer matches" for a regression row whose command is `cd sub && bash test.sh`, because it
looks for test.sh from the repo root (#4502).

## Approaches
1. A small `audit.missing(root, command)`: when the command starts `cd DIR &&` (or `;`) and DIR is a folder under the root, read each
   named script from DIR. Cost: one function. Risk: a cd target that is not a folder here (a variable) keeps the old root reading.
2. Parse the whole shell command. Rejected: far more than the bug needs.

## Chosen
Approach 1.

## What each done line needs
1. `missing` reads from the cd folder; a missing script is still reported. 2. `dev/toy/test-audit-cd-path.py` runs found, missing and
no-cd control; rows `audit-cd-path-found` and `audit-cd-path-toy`, seen red.

## Open questions
None.
