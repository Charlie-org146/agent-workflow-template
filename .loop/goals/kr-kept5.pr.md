# kr-kept5: clear known-red rows entry-committed-config and plan-cache-key

Written with the file tool under owner rule o685 (the push hook matches only prose in this file).

## Root causes

### entry-committed-config (Refs #5352)

Two faults in `dev/toy/test-entry-config.sh`, both in the toy. The product (`entry.py`) was right.

1. Setup used GNU-only `sed -i 's/.../.../' FILE`. BSD sed on macOS reads the expression as the backup suffix and the
   file name as the script. It fails with `invalid command code .` and the toy stops at `FAIL: setup` before any check
   runs. The edit is now a portable `python3 -c` string replace. The same `grep` setup check still proves the edit
   happened.
2. The SET-2 negative control archived `origin/main`'s entry.py. It expected that copy to print `public_origins` on one
   line and so to conflict. Since d5d021101 merged, main's entry.py prints a list as a count too, so the control could
   never conflict again and always failed. The control is now a fixed mutant: the entry.py under test with its
   list-as-count branch removed. If that branch is not found to remove, the toy fails instead of skipping the control.
   The control must still conflict (exit 1), which is as strict as before and no longer depends on what main holds.

### plan-cache-key (Refs #5372)

A product fault in `skills/workflow-regression/scripts/narrow.py` `warm()`. `lanes.names_table()` (added in a3c698224)
computes the closure of `python3 skills/workflow-regression/scripts/regression.py` in the plan's shared cache.
`narrow.store()` saves every cached closure, so the plan file also holds that runner closure, which is not a row.
`warm()` printed `miss (partial M of N)` with M = `len(rows)`, the number of every saved closure. So a nightly plan after
a land plan said `partial 13 of 13` instead of `partial 12 of 13`. M now counts only the rows this plan needs that the
file holds (`want & set(rows)`), as skills/loop-files.md documents ("The file held M of the N rows this plan needs").
The hit test is unchanged (`have == want` is `want <= set(rows)`). The toy's expectation is unchanged. One docstring in
narrow.py was trimmed so the file stays under the 19,000-byte health warning.

## Rows

- entry-committed-config: passes run alone twice (rc 0, rc 0).
- plan-cache-key: passes run alone twice (rc 0, rc 0).
- Both known lines are removed from .loop/regression-known.tsv.
- Net rows: 0. No row is added, removed or changed.

## Checks

- `bash dev/toy/test-plan-cache.sh all`: ALL PASS (87 PASS).
- `bash dev/toy/test-tiers.sh`: ALL PASS.
- `bash dev/toy/test-narrow.sh`: 2 FAILED, the same PASS/FAIL set as on origin/main, which fails the same two check-reads
  cases. They are unrelated to this change.
- `docs.py check`: DOCS OK. `criteria.py render --check`: TABLES OK. `dev/package.py --static`: PASS.

Refs #5352
Refs #5372
