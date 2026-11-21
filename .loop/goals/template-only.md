# The loop ships only as the GitHub template (TD554, the owner's words in operation-top; the repo's template setting is on): the requirement text from operation-top's readme-drafts/pending-folds.md item 5 goes in as drafted (SET-10 one versioned template, no skills package; GRD-20 keeps the 19,000 warn and 20,480 fail limits and drops the package rules and file cap; SET-1 gains automatic template update PRs); the release stops building or stamping the package and stays a tag release; the package-only gates and rows retire (package-passes, package-passes-3800, package-gate-head, trim-package-98, package-rows-tracked, package-headroom-held, and any row that only enforces the 100-file cap or listing.json), every script-size row stays; listing.json and dev/package.py go only if nothing else reads them

- Slug: template-only
- Touches: README.md, docs, skills, dev, .loop, .github
- ETA: 210 active minutes (estimate 167m plus a 25% margin)

## Done lines

Frozen. A wrong done line needs a new goal.

1. Given the pull request, then the README and pages carry item 5's text as drafted, the release makes a tag release with no package, and each retired row is gone from regression.tsv and the known list with the reason
2. Given every script-size row, then it still runs and passes, a script at 20,481 still fails (negative control), and nothing that reads listing.json or dev/package.py is left broken (listed with what was kept or removed)
3. Given this goal's diff, then docs.py check and criteria.py render --check pass, no script newly crosses 19,000 bytes, every script stays under 20,480, and the private scan is clean

## Verify by hand

<!-- Numbered steps for a person, each with an Expect: line. A release needs this. -->
