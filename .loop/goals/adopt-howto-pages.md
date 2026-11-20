# Known-red-zero group D (TD493): every adopt-fixture toy and set1-docs-format ends 'UNWRITTEN How-to-use-<Feature>', so adoption leaves a docs-format gap; rows adopt-fixture-bare-agent, adopt-fixture-ci-gitignore, adopt-fixture-existing-checks, adopt-fixture-feature-milestones, set1-docs-format and setup-fit. Fix it where setup writes those pages, at the cause, then take the 6 rows off the known list

- Slug: adopt-howto-pages
- Touches: skills, dev/toy, .loop
- ETA: 445 active minutes (estimate 355m plus a 25% margin)

## Done lines

Frozen. A wrong done line needs a new goal.

1. Given an adopted fixture repo, then no How-to-use page is left UNWRITTEN and the 4 adopt-fixture toys and set1-docs-format pass
2. Given .loop/regression-known.tsv on this branch, then the 6 rows are off it, each passing, and nothing is added
3. Given this goal's diff, then the package stays at 100 files, no script newly crosses 19,000 bytes, package.py --static, docs.py check and render --check pass, and each fixed row has a red proof

## Verify by hand

<!-- Numbered steps for a person, each with an Expect: line. A release needs this. -->
