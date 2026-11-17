# changelog-v plan

## Claims checked
- `release_trouble` exists at skills/workflow-docs/scripts/audit.py:39; the heading regex is on line 48 and requires the
  tag's own `v`; the gh fallback is `gh release view` on line 49.
- dev/toy/test-docs-command.sh section 4 already runs a tag with no note (v9.9.9) and a `## v9.9.9` heading, with a
  fake gh logging to `$FAKE_GH_DIR/calls.log`.

## Build steps
1. audit.py line 48: match `^##\s+\[?v?<version>\b` where `<version>` is the tag minus its leading `v`.
2. dev/toy/test-docs-command.sh section 4: add tag v9.9.8 with a `## [9.9.8]` heading in CHANGELOG.md; assert no RELEASE
   line and no `release view v9.9.8` in calls.log (PASS line `changelog-bracket-no-gh`); assert tag v9.9.7 with no heading
   still prints RELEASE and calls `gh release view v9.9.7` (PASS line `changelog-no-heading-gh-fallback`).
3. Two regression rows `changelog-v-1`, `changelog-v-2` (goal `changelog-v:1`, `changelog-v:2`), seen red first by running the
   test against the old regex.
4. The table is over its 1200 cap, so retire two duplicate rows (net 0): `machine-status-floor` and `machine-status-pod`,
   goal-done-line copies of `mon16-memory-floor` and `mon17-this-pod-only` (same command, same description).
5. Re-render the Tests tables (docs.py/criteria.py render).

## What could break
- `\b` after the version also matches `1.2.3.4`; same as before. A heading `## v1.2.3` still matches.
- Retiring the two rows drops their Tests entries; the requirement rows keep MON-16 and MON-17 covered.

## Out of scope
Parsing CHANGELOG into a version set; touching the gh fallback.

DEPTH: full
