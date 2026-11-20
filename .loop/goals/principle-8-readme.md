# The template README, wiki Home and Principles page show eight principles; principle 8 Honest, verified and on time, with six new bullets on existing requirements (owner words, 20:53 PT 2026-11-19, TD242); lands right after the merge queue and kept-migration, ahead of every other v2.0 goal

- Slug: principle-8-readme
- Touches: README.md, docs/wiki, skills/workflow-docs/scripts, skills/workflow-health/scripts, dev/toy, .loop/requirements
- ETA: 325 active minutes (estimate 257m plus a 25% margin)

## Done lines

Frozen. A wrong done line needs a new goal.

1. README.md, docs/wiki/Home.md and the Principles page say eight principles; principle 8 is titled Honest, verified and on time with this sentence exactly: Every claim the loop makes is backed by evidence it just read, every report and plan is checked by an adversarial reviewer before you rely on it, and every ETA is a commitment: a miss is recorded with its cause, never quietly moved. It has its diagram and a seven-row table (CHK-1, DEL-17, OPS-1, HLT-2, HLT-4, OPS-2, REG-9) with the Follows column, marked v2.0 planned where unbuilt
2. The six new bullets land exactly as approved by the owner on their existing requirements (CHK-1, DEL-17, OPS-1, HLT-2, HLT-4, OPS-2; no new requirement ID, no new feature; REG-9 listed unchanged), marked v2.0 planned where unbuilt, each through criteria.py revise with the owner-words record
3. docs check and health's principle list accept the eighth principle with negative controls: a README missing principle 8, or a row with an empty Follows cell, fails; HLT-2's seven principles count becomes eight and principle 8 prints UNREAD until its checks exist
4. No new shipped file, scripts at or under 19,000 bytes or no larger than on main, net regression rows 0, and no requirement text changes beyond the six bullets and the HLT-2 count

## Verify by hand

<!-- Numbered steps for a person, each with an Expect: line. A release needs this. -->

1. Open `README.md` and read its eight sections. Expect: section 8 is "Honest, verified and on time", with the one sentence, its diagram and a table of CHK-1, DEL-17, OPS-1, HLT-2, HLT-4, OPS-2 and REG-9, each with a Follows cell, the six new rows marked v2.0 (planned).
2. Run `python3 skills/workflow-docs/scripts/docs.py check`. Expect: `DOCS OK: 16 pages`.
3. Run `python3 skills/workflow-health/scripts/health.py check | grep '^PRINCIPLE'`. Expect: eight lines, with principles 6, 7 and 8 reading UNREAD.
4. In a scratch copy of `README.md`, delete the whole section 8, then change one word of its sentence, and run the docs check on each. Expect: the first fails with "section '8. Honest, verified and on time'", the second with "its sentence and a table".
5. Open the wiki Home and Principles pages and the Check in and board, Delivery, Operation and Health pages. Expect: Home and Principles show the same eight sections, each of the six requirements ends with its new "(v2.0 planned)" bullet and reads Unreviewed, and HLT-2's text shows "eight principles".
