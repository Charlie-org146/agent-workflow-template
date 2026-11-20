# The template README, wiki Home and Principles page show seven principles with a Follows column, live on GitHub tonight: principle 7 Standard, not home-made, its three requirements, and a Follows column on every Part 1 table (owner o474, o475; TD221)

- Slug: principle-7-readme
- Touches: README.md, docs/wiki, skills/workflow-docs/scripts, skills/workflow-health/scripts, dev/toy
- ETA: 305 active minutes (estimate 242m plus a 25% margin)

## Done lines

Frozen. A wrong done line needs a new goal.

1. README.md, docs/wiki/Home.md and the Principles page say seven principles; principle 7 is Standard, not home-made with this sentence exactly: Every requirement follows a specific, named industry tool, standard or production system with a proven record, and uses that tool itself wherever one can run here; where it can't, it copies the proven design and says why. It has its diagram and a table of its three requirements, marked v2.0 planned where unbuilt.
2. The three new requirement texts (Documentation, Delivery, and a bullet on HLT-2 in Health) are on their pages exactly as approved in TD221, with the next free requirement IDs reported
3. Every Part 1 table gains a Follows column filled from the references draft: the specific name, its source link and the verdict; the seven strict-read rows show the recommended replacement marked v2.0 planned; REL-13 shows its rewritten text marked v2.0 planned
4. docs check and health's principle list accept the seventh principle and the Follows column byte for byte with the README sentence, with negative controls: a README missing principle 7, or a row with an empty Follows cell, fails
5. No new shipped file, scripts at or under 19,000 bytes or no larger than on main, net regression rows 0, and no requirement text changes beyond the three new texts

## Verify by hand

<!-- Numbered steps for a person, each with an Expect: line. A release needs this. -->

1. Open `README.md` and read its seven sections. Expect: section 7 is "Standard, not home-made", with the one sentence, its diagram and a table of DOC-24, DEL-21 and HLT-2, each marked v2.0 (planned); every other table has a Follows column.
2. Run `python3 skills/workflow-docs/scripts/docs.py check`. Expect: `DOCS OK: 16 pages`.
3. Run `python3 skills/workflow-health/scripts/health.py check | grep '^PRINCIPLE'`. Expect: seven lines, with principles 6 and 7 reading UNREAD.
4. In a scratch copy of `README.md`, delete a Follows cell, then delete the whole section 7, and run the docs check on each. Expect: the first fails with "a Follows cell", the second with "section '7. Standard, not home-made'".
5. Open the wiki Home and Principles pages. Expect: the same seven sections and Follows column, and HLT-2's text shows "seven principles".

