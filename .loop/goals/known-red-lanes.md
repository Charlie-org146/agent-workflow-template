# The lanes regression rows pass again on main: script headers name their rows, and a batch.py change reruns only the rows it reaches

- Slug: known-red-lanes
- Touches: not declared
- ETA: 290 active minutes (estimate 232m plus a 25% margin, rough)

## Done lines

Frozen. A wrong done line needs a new goal.

1. Row lanes-headers passes: lanes_cli check reports 0 header findings (today 21 findings in 15 scripts whose rows name missing dev/toy/test-x.sh files)
2. Row lanes-repo-narrow passes: a change to batch.py reruns only the land rows its import closure really reaches (today 879 of 1233 with 197 ALWAYS), the closure widened via watch.py narrowed without dropping a real dependency, with a negative control
3. Every row this goal fixes leaves .loop/regression-known.tsv; nothing else changes; net test rows grow by at most 0

## Verify by hand

<!-- Numbered steps for a person, each with an Expect: line. A release needs this. -->

1. Run `python3 skills/workflow-regression/scripts/lanes_cli.py check`.
   Expect: it prints nothing and exits 0 (it printed 21 findings before).
2. Run `python3 skills/workflow-regression/scripts/lanes_cli.py affected skills/workflow-monitoring/scripts/batch.py | head -1 | cut -c1-40`.
   Expect: `AFFECTED 4xx of 1233 rows`, well under half (it printed 879 before).
3. Run `bash dev/toy/test-narrow.sh 2>&1 | grep -E "Python test|ALL PASS|FAILED"`.
   Expect: two `PASS: a Python test's ...` lines and `ALL PASS`.
4. Run `grep -c "lanes-headers\|lanes-repo-narrow" .loop/regression-known.tsv`.
   Expect: 0.
