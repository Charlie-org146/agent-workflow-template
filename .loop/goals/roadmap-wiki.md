# Print the work left before v1.0.0 as a Roadmap page in the GitHub wiki, rebuilt by one command from docs/ROADMAP.md, the open issues and the run records, so the owner can fill its Priority column and organize it

- Slug: roadmap-wiki
- Touches: docs/ROADMAP.md, docs/wiki/Roadmap.md, .loop/docs.tsv, skills/workflow-docs/scripts, skills/workflow-health/scripts/issues.py, dev/toy/test-roadmap.py, .loop/regression.tsv, DECISIONS.md

## Done lines

Frozen. A wrong done line needs a new goal.

1. docs/ROADMAP.md holds the v1.0.0 groups (size caps, Windows-safe, regression trust, open defects, adoption, the Unreviewed requirements per page, package rules) as one table per group with issue or goal, one-line outcome, what it blocks, status (in flight, queued or open) and an empty Priority column; the Backlog-milestone issues listed apart as 'after v1.0'; a rollout section (migrate-thermis, migrate-steward, migrate-portfolio, migrate-skillset, in parallel); the goals in flight; the off-machine to-dos
2. One command rebuilds docs/wiki/Roadmap.md from docs/ROADMAP.md, the open issues (gh) and the run records; the page is in .loop/docs.tsv so docs.py check keeps it fresh and docs.py publish owns and publishes it; no reviewed page is edited without the owner's words (wording goes to DECISIONS.md first)
3. A toy on a fake gh and a regression row, each seen red first, prove: a closed issue drops out, status shows in flight, queued or open, Backlog issues sit apart under after v1.0, and Priority is empty

## Verify by hand

<!-- Numbered steps for a person, each with an Expect: line. A release needs this. -->
