# audit-cd-path plan

Checked: `audit.untested` (skills/workflow-docs/scripts/audit.py) built `gone` from `cr.SCRIPT_FILE.findall(rows[name][2])` against the root.

## Build steps
1. `audit.missing(root, command)`; `untested` calls it.
2. Toy `dev/toy/test-audit-cd-path.py`; rows `audit-cd-path-found` and `audit-cd-path-toy`, each seen red against a break that ignores the cd.

## Test per done line
The two rows. Done 1: found passes, missing still reported. Done 2: the toy has the no-cd control.

## What could break
A row `cd $VAR && ...` keeps the old root reading (no folder named $VAR); audit.py stays 14.7 KB.

## Out of scope
Parsing other shell forms (pushd, subshells).

PENDING: none
