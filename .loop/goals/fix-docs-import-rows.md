# Row docs-import-rows-pass passes on main again (Fixes #5619): it calls regression.py run on sync-propose and sync-template-redirect, which rows-600-c (cc39d98bf) removed or merged, so it exits 1. Point it at the rows that now hold those checks (found from cc39d98bf's diff), or drop the names whose checks are gone, saying which and why

- Slug: fix-docs-import-rows
- Touches: .loop, docs
- ETA: 385 active minutes (estimate 306m plus a 25% margin)

## Done lines

Frozen. A wrong done line needs a new goal.

1. Given main with this fix, then regression.py run docs-import-rows-pass passes, and every name it runs is a row in regression.tsv
2. Given the pull request, then its body says Fixes #5619, names where each removed row's check went, adds no row, and docs.py check and criteria.py render --check pass
3. Given this goal's diff, then no file is added to the package (100 files), no script newly crosses 19,000 bytes, and the private scan is clean

## Verify by hand

<!-- Numbered steps for a person, each with an Expect: line. A release needs this. -->
