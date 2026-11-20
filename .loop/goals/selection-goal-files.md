# A goal's own record files stop counting as code for test selection (issue 5398; DEL-17 only the tests the change reaches): today a change to .loop/goals/<slug>.md or .loop/kept/<slug>.tsv selects every row whose script reads the .loop/ folder, so a typical pull request selects 1,268 of 1,299 rows and the 5-minute PR CI runs only about 171 of them. Paths under .loop/goals/ and .loop/kept/ (and the goal's other record files) select only the rows whose command or declared reads name that exact file or folder, and count as no effect for the root runners. A real code change next to them still selects all of its own rows. lanes.py and lanes_cli.py are the likely files; neither may end larger than on main (real trims, no reformat). If it adds a regression row, it builds it but pushes only after rows-600-a is on main (the row cap is 1300, main has 1299), with a red proof. Lane prep and the caps guard before the push; no local lane

- Slug: selection-goal-files
- Touches: skills/workflow-regression/scripts/lanes.py, skills/workflow-regression/scripts/lanes_cli.py
- ETA: 400 active minutes (estimate 320m plus a 25% margin)

## Done lines

Frozen. A wrong done line needs a new goal.

1. Given a diff that changes only a goal file under .loop/goals/ and a kept fragment under .loop/kept/, when lanes_cli.py affected selects rows, then it selects fewer than 20 rows and reruns no root runner
2. Given a row whose command or declared reads name a file under .loop/goals/ or .loop/kept/, when that file changes, then the row is still selected, and a real code change next to the record files still selects all of its own rows
3. Given this goal's diff, then lanes.py and lanes_cli.py are no larger than on main, a toy case or row proves D1 and D2 with a negative control, any new row has its red proof, and the docs check passes

## Verify by hand

<!-- Numbered steps for a person, each with an Expect: line. A release needs this. -->
