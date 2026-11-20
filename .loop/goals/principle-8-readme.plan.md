# principle-8-readme: plan

1. `commands.md`: add principle 8 (group `honesty`) to "The principles" and say principles 6, 7 and 8 read UNREAD until their groups exist. `pageformat.py` and `judge.py` read that list, so the README check, the Principles page check and health's PRINCIPLE lines follow with no script change. Toy tests: `test-health-prd.sh` expects eight PRINCIPLE lines with 6, 7 and 8 UNREAD; `test-docs-format.sh` adds negative controls (README missing principle 8, principle 8's sentence off by a word; the empty Follows cell control already covers the new rows). Done: both toys pass, apart from the health toy's migration-control rows, which fail the same way on main.
2. Requirements: `criteria.py revise` for CHK-1, DEL-17, OPS-1, HLT-2, HLT-4 and OPS-2 with owner record o482, one `(v2.0 planned)` bullet each, exactly as approved; HLT-2 also says eight principles and "6, 7 and 8 ... Honesty". Done: six REVISED lines; each requirement reads Unreviewed with a new revision row.
3. Pages: section 8 (sentence, diagram, seven-row table with the Follows column; REG-9 listed unchanged) on README, Home and Principles from the approved draft by a throwaway script; the six new bullets and HLT-2's count in every Part 2 row that shows them; "eight" in the README and Principles intros and in the Principles HLT-2 summary; the principle 8 diagram and the overview diagram's count.
4. Config: `public_origins` lists the five new Follows origins (DOC-19), so `docs.py check` finds no link outside the repo.
5. Re-stamp: `entry.py write` and `docs.py audit` with the 2.0 floor dropped, `audit.py restamp` for pages the config change touched, `wiki.py prepare` last; put the 2.0 floor and skip-worktree back; never commit it.
6. Size and rows: no script changed, no new shipped file, regression rows unchanged (net 0).

Self-review (one pass): (a) the approved texts are compared byte for byte by the generator, which asserts each new bullet equals the draft's summary text; (b) the new bullets all carry "(v2.0 planned)" and their own ID tag, like their neighbours; (c) HLT-2 was already Unreviewed, so its revision changes nothing about its review state; (d) no requirement text changes beyond the six bullets and HLT-2's count.

Out of scope, by the goal's own brief: the honesty group, the ETA and evidence build (eta-commitments, evidence-claims, stall-watch, send-budget), the red-team code, and the reply hook that refuses a claim with no evidence.

Known trade-offs: `.loop/config.json` and `.loop/START.md` change for `public_origins` (the draft's sources cannot be linked otherwise); the six revised requirements are Unreviewed until the owner re-reviews, as expected; HLT-2 appears in principles 2, 7 and 8 on purpose.
