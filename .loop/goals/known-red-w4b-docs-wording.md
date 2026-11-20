# Two main-red docs-wording rows pass again or are removed with evidence, so the v2.0 gate's full suite has no FAIL outside the known list (TOP-DECISION 57, o195 no waivers, o213)

- Slug: known-red-w4b-docs-wording
- Touches: dev/toy/test-milestone-wording.sh, .loop/regression.tsv, docs/wiki/Documentation.md, docs/wiki/Tests.md
- ETA: 220 active minutes (estimate 176m plus a 25% margin, rough)

## Done lines

Frozen. A wrong done line needs a new goal.

1. Each of these rows passes on the PR head in the CI full-suite shards, or is removed from .loop/regression.tsv with evidence in the PR that the behaviour it tests no longer exists: doc1-sync-pointer milestone-wording-unreviewed
2. No row is added to .loop/regression-known.tsv, and net regression rows are 0 or fewer against main

## Verify by hand

1. Run `bash dev/toy/test-milestone-wording.sh` from the repo root.
   Expect: it prints `PASS milestone-freeform:milestone-wording-unreviewed` and `PASS milestone-freeform:milestone-rows-seen-red`, and no FAIL line.
2. Run `grep -c doc1-sync-pointer .loop/regression.tsv docs/wiki/Documentation.md docs/wiki/Tests.md`.
   Expect: 0 in each file. The row was retired, not waived: DOC-1 revision r2 (2026-11-18) removed the `docs.py sync` sub-bullet it checked, and the sync behaviour now lives in DOC-17. The PR body carries this evidence.
3. Run `git diff main -- docs/wiki` on the PR head.
   Expect: only the removed doc1-sync-pointer Tests lines; no requirement or Reviewed line on any feature page changes.
