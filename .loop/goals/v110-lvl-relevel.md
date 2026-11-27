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

Work in a throwaway copy: `git clone . /tmp/lvl-try && cd /tmp/lvl-try && git remote set-url --push origin DISABLED`. Never push from it.

1. Run `python3 skills/workflow-regression/scripts/regression.py levels --check`.
   Expect: a line starting `valid:` with the row count and the L0 seconds, under 45.
2. In `.loop/regression-relevel.tsv`, empty the third cell (level) of the `eta-freeze` line and change the fourth cell (risk) of the `grd6-head-moved` line to `none`. Run `python3 skills/workflow-regression/scripts/regression.py sync`, then `git checkout -- .loop`.
   Expect: `LEVELS_BAD_LEVEL eta-freeze` naming L0, L1 or L2, and `LEVELS_NO_RISK grd6-head-moved`.
3. In `.loop/config.json`, add `"levels": ["L0"]` to the `medium` row of `checks_by_size`. Commit it, run `git update-ref refs/remotes/origin/main HEAD && git symbolic-ref refs/remotes/origin/HEAD refs/remotes/origin/main`, then run `python3 -c "import sys; sys.path.insert(0, 'skills/workflow-delivery/scripts'); import sizing; sys.excepthook = lambda k, e, t: print(e.args[0]); sizing.read_table()"`.
   Expect: a line with `SIZING_BAD_LEVELS` naming size medium and L1.

## Notes

Red-team dispositions for the final plan (plan file sha1 27b4c303f4e8): its 26 numbered breaks, named by number, principle and short id. Their text is not repeated here. Item ids point at the goal's build list. Rulings: operation, under the owner record named.

| break | principle | short id | disposition |
|---|---|---|---|
| 1 | 7 | b1p75ca911 | accepted (o1000): fixed in the build, item I1 |
| 2 | 2 | b2p2b24e49 | accepted (o1000): fixed in the build, item I5 |
| 3 | 6 | b3p60d1b76 | accepted (o1000): fixed in the build, item I5 |
| 4 | 6 | b4p6671eeb | accepted (o1000): a limit. The approval record number is checked on our machines before merge, where the records are kept |
| 5 | 6 | b5p62dfb43 | accepted (o1000): a limit. The approval record number is checked on our machines before merge, where the records are kept |
| 6 | 6 | b6p696c194 | accepted (o1000): fixed in the build, item I2 |
| 7 | 6 | b7p65e9275 | accepted (o1000): fixed in the build, item I9 |
| 8 | 6 | b8p67997c6 | accepted (o1000): fixed in the build, item I10 |
| 9 | 6 | b9p6fa8cdf | accepted (o1000): a limit. The approval record number is checked on our machines before merge, where the records are kept |
| 10 | 2 | b10p2e401c5 | accepted (o1000): fixed in the build, item I16 |
| 11 | 3 | b11p3edf761 | accepted (o1000): fixed in the build under operation's ruling, item I17 |
| 12 | 7 | b12p7f43981 | deliver-first line |
| 13 | 2 | b13p27cd5ff | accepted (o1000): fixed in the build, item I20 |
| 14 | 6 | b14p639c4bf | accepted (o1000): fixed in the build, item I19 |
| 15 | 6 | b15p6293519 | accepted (o1000): fixed in the build, item I20 |
| 16 | 6 | b16p617a4c0 | accepted (o1000): fixed in the build, item I2 |
| 17 | 6 | b17p68f40fd | accepted (o1000): fixed in the build, item I2 |
| 18 | 6 | b18p6eb9245 | accepted (o1000): a limit. The approval record number is checked on our machines before merge, where the records are kept |
| 19 | 6 | b19p6d58146 | accepted (o1000): a limit. The approval record number is checked on our machines before merge, where the records are kept |
| 20 | 6 | b20p6f14de9 | accepted (o1000): fixed in the build, item I9 |
| 21 | 8 | b21p80640ce | accepted (o1000): fixed in the build under operation's ruling, item I17 |
| 22 | 2 | b22p208bb65 | accepted (o1000): a deliver-first line |
| 23 | 2 | b23p2a556df | deliver-first line |
| 24 | 2 | b24p27148ea | accepted (o1000): a limit. No broken table reaches main past the PR check and the release run; a deliver-first line covers the scheduled run's reading |
| 25 | 7 | b25p7c1a042 | deliver-first line |
| 26 | 1 | b26p110cac9 | deliver-first line |

Correction to the plan, which is not edited: where it says the excuse entry for done-pkg-secret-print-3 names an owner record, the entry names TD2022, which is a top decision and not an owner record.

Pull request notes:

- The new level and risk rules apply to this repository's re-levelled table.
- Adding a defect row with an issue or pull request address now reads that address's labels (gh, signed in). On a re-levelled table, `add --level covered` takes `--covers`; the other documented `add` commands work as before.
- A covered row's record names the rows that prove it. It does not say they prove every word of its line, and this goal computes no proven state.
- The one re-levelling kept all 745 rows, each at L0, L1 or L2 (L0: 3 rows, 0.5 s of 45). The build record beside this file holds its command, output and counts. All 149 linked addresses are this repository's, and none of its label names holds security, private or privacy.
- Left to later goals: running rows by level and using a size's levels (G2), the scheduled run (G3), and retiring the old words and the draft state column (G4). Until then a side record file holds each row's level in place of a table column.
- To make room under the packaged-script limit, the work is in five new modules in workflow-regression and one in workflow-delivery, and three functions moved whole: split, merge_runs and mend.
- Deliver-first: the advised remove command doesn't take an orphaned pinned-tag line; that line is removed by hand.
