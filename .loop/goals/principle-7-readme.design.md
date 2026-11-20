# principle-7-readme: design

## Problem
The template README, wiki Home and Principles page show six principles and no record of what each requirement follows. Owner records o474 and o475 (Operation's TD221) ask for a seventh principle, "Standard, not home-made", three requirements under it, and a Follows column on every Part 1 table, live tonight.

## Approaches
1. Edit the three pages by hand. Cheap, but 43 rows times three pages is error-prone and the docs check would not hold the column in place.
2. Make the one principle list (`commands.md`, "The principles") and `pageformat.py` the single source: add row 7 to the list, add the Follows column to the checked table header with an empty-cell check, then regenerate the three pages' Part 1 from the references draft with a throwaway script. Chosen: the check and the pages cannot drift, and the negative controls live in the existing toy tests.

## Choices
- Follows cell = specific name, source links and verdict. Verdicts follow the references draft; REG-7 and DOC-1 read "adapted" (strict-read correction); the strict-read rows (HLT-7, MCH-5, CHK-1, AUT-5, INT-7, DEL-1) show the recommended replacement marked v2.0 planned; REL-13 shows its rewritten text marked v2.0 planned. No requirement text changes for them.
- New IDs: DOC-24 (Documentation) and DEL-21 (Delivery), Unreviewed, each with an r1 revision row approved under owner delegation (DOC-2 r4). The HLT-2 bullet goes in by `criteria.py revise HLT-2` with owner record o474.
- Principle 7 maps to the health group `references`, which does not exist yet, so health prints `PRINCIPLE 7 ... UNREAD (references)` exactly as it does for principle 6 until the reference rule is built.
- The diagram is `docs/wiki/principle-09-standard-not-home-made.svg` (docs, not part of the shipped package).
- `pageformat.py` stays under 19,000 bytes (18,994) by turning two one-line functions into lambdas.
- DOC-19's "stands alone" check rejects links outside the repo, so the Follows sources' origins go in `public_origins`; DOC-24 would make the Documentation page's 24th ID, so `criteria_max` goes from 23 to 24.

## Open questions
- HLT-2's old sentence says "six principles"; see PENDING in the plan.
