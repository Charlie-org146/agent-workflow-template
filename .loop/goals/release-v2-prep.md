# Prepare main for the v2.0.0 release (owner o698, o699; Operation TD643, TD646, TD647): VERSION reads 2.0.0, REG-4 records with a dated note that v2.0 shipped with the row count and known-red list on main at release, and health goes green by adding only v2fix-bundle-2's three defect rows for #88, #5635 and #5638, whose fixes are already on main. Nothing else from v2fix-bundle-2 or any other branch. Fixes #5695, #5696, #5697

- Slug: release-v2-prep
- Touches: VERSION, docs/wiki, README.md, .loop/regression.tsv
- ETA: 325 active minutes (estimate 260m plus a 25% margin)

## Done lines

Frozen. A wrong done line needs a new goal.

1. Given VERSION on this branch, then it reads exactly 2.0.0
2. Given REG-4's text, then it carries a dated revision line (DOC-2) saying v2.0 shipped with the regression table's actual row count on this branch and the known-red list as of the release, citing owner records o698 and o699, and no other requirement text changes
3. Given the rows for #88 (linked as issues/88), defect-5635-settings-default and defect-5638-reconcile-wording, taken from loop/v2fix-bundle-2 with nothing else from it, then each passes on this branch run alone twice and health.py check on this branch reads 0 fail
4. Given this goal's diff, then only VERSION, REG-4's page and its rendered copies, those three rows in .loop/regression.tsv with their rendered Tests lines, and the goal's own records change, the docs check passes and the private scan is clean

## Verify by hand

<!-- Numbered steps for a person, each with an Expect: line. A release needs this. -->
