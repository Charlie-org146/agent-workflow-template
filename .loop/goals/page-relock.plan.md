# page-relock plan

1. `skills/workflow-docs/scripts/relock.py` (new, since prd.py and criteria.py are near the limit): `owned()` and `relock()` and a CLI. `prd.trouble` calls `owned` when only R moved, so the check no longer reports LOCKED. Both confirmed to exist.
2. `relock` re-stamps the review line and appends `auto-relock: all lines owner-reviewed` to reviews.tsv.
3. Toy `dev/toy/test-page-relock.py` and row `page-relock` (DOC-2), seen red.
4. Name the command in SKILL.md and references/commands.md; render Tests and START.md.

Could break: pages with all lines owner-reviewed and only R moved no longer report LOCKED. Out of scope: wiring relock into the merge flow (delivery files), and edits to the owner-locked Documentation requirements.
