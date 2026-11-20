# Plan: known-red-w4b-docs-wording

Checked against the code: dev/toy/test-milestone-wording.sh holds the HLT-4 check (the `key == "HLT-4"` branch) and its header comment; .loop/regression.tsv holds the `doc1-sync-pointer` row; docs/wiki/Health.md HLT-4 no longer says "on no milestone"; docs/wiki/Documentation.md DOC-1 has no `docs.py sync` line, DOC-17 does.

**Build steps.**
1. Remove the HLT-4 "on no milestone" check and fix the header comment in dev/toy/test-milestone-wording.sh.
2. Delete the `doc1-sync-pointer` line from .loop/regression.tsv; the lane re-renders the Tests tables (Documentation, Tests) on its own.

**Test per done line.** Line 1: the toy's two python blocks print CLEAN locally and `bash -n` passes; CI runs the row. The removed row's behaviour is gone: DOC-1 has no sync sub-bullet since r2. Line 2: `git diff` adds no line to regression-known.tsv; net rows are -1.

**What could break.** A page or toy that names `doc1-sync-pointer` (grep: only generated Tests tables and the old wiki-current plan); a "requirement has no test" rule for DOC-1 (DOC-1 keeps many other rows).

**Out of scope.** Any requirement or Reviewed text.

VERDICT: self-review: plan matches the design and the frozen done lines
