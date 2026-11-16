# Each feature has its own How-to-use page from the user's side (runbooks, deployments, URLs, automations), separate from its PRD and the README (owner o60)

- Slug: how-to-use-docs
- Touches: not declared

## Done lines

Frozen. A wrong done line needs a new goal.

1. The Documentation page has a requirement that every feature page has a How-to-use page in the wiki covering, in a general format, what the feature is for, how to run or reach it, its URLs and deployments, its automations and schedules, and its runbooks; docs.py check reports a feature without one, and accepts a How-to-use-<Feature>.md page with no docs.tsv row of its own as mapped to its feature (the #4542 amendment), with a negative control for each.
2. The template's README 'How to use <Feature>' sections and any runbook or deployment text in its feature pages move into per-feature How-to-use pages; each feature page links its How-to-use page, and the README keeps a short start plus links.

## Verify by hand

<!-- Numbered steps for a person, each with an Expect: line. A release needs this. -->
