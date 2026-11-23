# Renumber the principles 1 to 8 with the principle 3 split, names and numbers only (v1.1.0 task 5, part 1a)

- Slug: v110-fast-renumber
- Touches: docs/wiki, docs, README.md, dev/toy, .loop/regression.tsv, skills/workflow-delivery/references/commands.md, skills/workflow-health/references/commands.md
- ETA: 275 active minutes (estimate 219m plus a 25% margin)

## Done lines

Frozen. A wrong done line needs a new goal.

1. Given the docs, then the "principles renumber 1 to 8" with principle 3 Fast, 4 Cheap and 5 Small as in frozen-source-final-1742 ("Today's 4 Private, 5 Reproducible and 6 Autonomous become 6, 7 and 8"; "GRD-20 moves here", to 5 Small); every other feature sits under the principle the page names, except OPS-16, which stays where it is until the owner's answer; no principle sentence is changed; every reference to an old principle number is updated; and docs.py check passes.
2. Given the health check, then it is not red after the renumbering.
3. Given the package, then every script stays under 20,480 bytes and none newly crosses 19,000, new files stay within MAX_FILES (a new file under skills/ only after the release-gate change allows it), no test is loosened, no existing row turns red, and committed text never names the service repo.

## Verify by hand

1. Open the Principles page (docs/wiki/Principles.md) and README.md.
   Expect: eight principles, in order 1 Guided, 2 Sensed, 3 Fast, 4 Cheap, 5 Small, 6 Private and guarded, 7 Reproducible, portable and adoptable, 8 Autonomous and human-friendly; the sections say "eight".
2. Run `python3 skills/workflow-docs/scripts/docs.py check --base origin/main --own`.
   Expect: DOCS OK: 16 pages.
3. Run `python3 skills/workflow-health/scripts/health.py check` in a clean clone.
   Expect: eight PRINCIPLE lines; 4 Cheap reads UNREAD (none); principles 7 and 8 each carry a "has no Reviewed requirement" FAIL (accepted, see PR notes).

## PR notes

Authority: owner records o750 and o756 (DEL-28 "Every step has a token budget", the DEL-17 Tokens move, GRD-8 and GRD-15 now "moved to DEL-28", the OPS-16 move to Reproducible, DOC-26's six-feature allowance), o757 (GRD-7 is about CI minutes and stays on DEL-17; it overrides o756's GRD-7 clause), o764 (red-team breaks accepted), o791 and o792 (the reviews of DEL-17 and DEL-28 in the feature format). Operation rulings: TD831, TD834, TD1007 (DEL-28 redone on main's migrated format, structure only), TD1010. No done line covers the DEL-28 work: o756 is its authority, and its ids name v110-fast-renumber.

Text checks: DEL-17 without its Tokens line equals, line for line, the text the owner reviewed (seal 59e467e1); DEL-28 holds exactly the moved Tokens line (seal 5c225018). Both are Reviewed 2026-11-22.

Accepted health result (TD1010): two new FAIL rows, "principle 7 has no Reviewed requirement" and "principle 8 has no Reviewed requirement" (the split adds two principles; main's migration cleared every Reviewed mark, so principles 2 to 6 show the same FAIL on main); Cheap reads UNREAD (its groups are `none`; a feature for Cheap is the next goal). New WARN: DEL-28 has no regression row (no row added).

Known, outside this change: toy lines test-docs-format.sh:207 and 211-213 and test-health-prd.sh:50 and 52 pin names or sentences in no live list and are red on main too; docs/wiki/flows/DEL-28.svg is a retitled copy of DEL-17's figure and still draws the clock; the principle 04 and 05 figures are retitled copies of the old one; DEL-28's Follows is DEL-17's cell (not about tokens; for the owner, DEL-21).

Review (recorded): two findings fixed in 155f8cc6e (README "eight sections"; the DEL-17 summary row drops the moved Tokens sentence and GRD-8). The named specialists, the QA pass and web research were not run (text-only change).
