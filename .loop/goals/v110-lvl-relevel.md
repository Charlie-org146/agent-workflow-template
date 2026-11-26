# Test levels G1 (LVL-1.1, LVL-1.3 tagging, LVL-1.5; owner o980, o985; split TD1749): the level and risk columns, the one-time re-levelling and L0

- Slug: v110-lvl-relevel
- Touches: skills/workflow-regression, skills/workflow-delivery, dev/toy, .loop/regression.tsv, .loop/regression-relevel.tsv, .loop/regression-risk.tsv, .loop/regression-relevel-input.tsv, skills/loop-files.md, listing.json, docs/wiki/Tests.md, .loop/START.md
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

## Notes

Red-team dispositions for the final plan (plan file sha1 27b4c303f4e8): its 26 numbered breaks, named by number, principle and short id. Their text is not repeated here. Item ids point at the goal's build list. Rulings: operation, under the owner record named.

| break | principle | short id | disposition |
|---|---|---|---|
| 1 | 7 | b1p75ca911 | accepted (o1000): fixed in the build, item I1 |
| 2 | 2 | b2p2b24e49 | accepted (o1000): fixed in the build, item I5 |
| 3 | 6 | b3p60d1b76 | accepted (o1000): fixed in the build, item I5 |
| 4 | 6 | b4p6671eeb | limit, accepted (o1000): fixed in the build, items I3 and I17 |
| 5 | 6 | b5p62dfb43 | limit, accepted (o1000): fixed in the build, item I13 |
| 6 | 6 | b6p696c194 | accepted (o1000): fixed in the build, item I2 |
| 7 | 6 | b7p65e9275 | accepted (o1000): fixed in the build, item I9 |
| 8 | 6 | b8p67997c6 | accepted (o1000): fixed in the build, item I10 |
| 9 | 6 | b9p6fa8cdf | limit, accepted (o1000): fixed in the build, item I13 |
| 10 | 2 | b10p2e401c5 | accepted (o1000): fixed in the build, item I16 |
| 11 | 3 | b11p3edf761 | accepted (o1000): fixed in the build under operation's ruling, item I17 |
| 12 | 7 | b12p7f43981 | deliver-first line |
| 13 | 2 | b13p27cd5ff | accepted (o1000): fixed in the build, item I20 |
| 14 | 6 | b14p639c4bf | accepted (o1000): fixed in the build, item I19 |
| 15 | 6 | b15p6293519 | accepted (o1000): fixed in the build, item I20 |
| 16 | 6 | b16p617a4c0 | accepted (o1000): fixed in the build, item I2 |
| 17 | 6 | b17p68f40fd | accepted (o1000): fixed in the build, item I2 |
| 18 | 6 | b18p6eb9245 | limit, accepted (o1000): fixed in the build, items I13 and I8 |
| 19 | 6 | b19p6d58146 | limit, accepted (o1000): fixed in the build, item I3 |
| 20 | 6 | b20p6f14de9 | accepted (o1000): fixed in the build, item I9 |
| 21 | 8 | b21p80640ce | accepted (o1000): fixed in the build under operation's ruling, item I17 |
| 22 | 2 | b22p208bb65 | accepted (o1000): fixed in the build under operation's ruling, item I11 |
| 23 | 2 | b23p2a556df | deliver-first line |
| 24 | 2 | b24p27148ea | limit, accepted (o1000); a deliver-first line goes with it |
| 25 | 7 | b25p7c1a042 | deliver-first line |
| 26 | 1 | b26p110cac9 | deliver-first line |

Correction to the plan, which is not edited: where it says the excuse entry for done-pkg-secret-print-3 names an owner record, the entry names TD2022, which is a top decision and not an owner record.
