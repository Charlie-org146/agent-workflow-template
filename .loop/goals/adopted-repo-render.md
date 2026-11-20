# The template's page render works for an adopted repo (TD420 item 3, TD421; approved by operation-top under owner delegation DOC-2, o486; it unblocks an adopted repo whose README has no DEL-19). (a) sections.fresh() rewrites 'What this is' from DEL-19 on a Delivery page; when the repo has no DEL-19 it leaves that section exactly as written. (b) When no row of a principle table has a Follows tag, the Adoption cells and the table's Adoption line read 'not measured: no references recorded yet', never 0%, and an empty Confidence reads 'not measured: no data yet'. (c) The regression row shard-balance's description says eight shards, not six, matching #5502 (TD421: a false statement on main). The template's own pages render exactly as today. Small fix: sections.py and the render code it calls, one toy, one row description

- Slug: adopted-repo-render
- Touches: skills/workflow-docs/scripts, dev/toy, .loop/regression.tsv
- ETA: 425 active minutes (estimate 338m plus a 25% margin)

## Done lines

Frozen. A wrong done line needs a new goal.

1. Given a copy with no DEL-19 and a hand-written What this is paragraph, when render.py blocks runs, then the paragraph is unchanged; and given the template itself (DEL-19 present), then What this is renders from DEL-19 exactly as on main (negative control)
2. Given a principle table whose rows carry no Follows tag, then every Adoption cell and the table's Adoption line read 'not measured: no references recorded yet' and an empty Confidence reads 'not measured: no data yet'; and given the template's own tables (Follows present), then the percentages render exactly as on main (negative control)
3. Given this goal's diff, then only sections.py or the render module it calls, one toy, the shard-balance row's description (now eight shards) and the goal's record files change, every script stays under 20,480 bytes, and docs.py check and criteria.py render --check pass on the template

## Verify by hand

<!-- Numbered steps for a person, each with an Expect: line. A release needs this. -->
1. Run `bash dev/toy/test-docs-sections.sh | grep -E "no DEL-19|negative control: with DEL-19|ALL PASS"`.
   Expect: PASS for a repo with no DEL-19 (What this is kept, rows with no Follows tag read "not measured", never 0%), PASS for the negative control with DEL-19 and tags (percentages stay), and ALL PASS.
2. Run `python3 skills/workflow-docs/scripts/criteria.py render --check`.
   Expect: TABLES OK, so the template's own README, Home and Principles render exactly as before.
