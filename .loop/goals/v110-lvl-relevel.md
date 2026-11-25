# Test levels G1 (LVL-1.1, LVL-1.3 tagging, LVL-1.5; owner o980, o985; split TD1749): the level and risk columns, the one-time re-levelling and L0

- Slug: v110-lvl-relevel
- Touches: skills/workflow-regression, skills/workflow-delivery, dev/toy, .loop/regression.tsv
- ETA: 425 active minutes (estimate 339m plus a 25% margin)

## Done lines

Frozen. A wrong done line needs a new goal.

1. Given a row whose level is blank or "L3", when the table is read, then it is refused, naming the row and the three levels.
2. Given a row that guards a Principle 6 requirement with no risk tag, when the table is read, then it is refused, naming the row.
3. Given the 744 rows on main, when re-levelling runs, then 744 rows remain, each with one level from L0 to L2, and the record gives each row's old word, new level and reason.
4. Given a re-levelling whose L0 rows add up to more than 45 seconds, when it is checked, then it is refused, naming the total.
5. Given CBS-1's table with a size that leaves out L1, when settings are read, then it is refused, naming the size and L1.
6. Given the package, when the goal's checks run, then every script stays under 20,480 bytes, no test is loosened, no row turns red, and committed text never names the service repo.

## Verify by hand

<!-- Numbered steps for a person, each with an Expect: line. A release needs this. -->
