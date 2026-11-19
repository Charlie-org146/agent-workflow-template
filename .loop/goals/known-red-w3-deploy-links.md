# The deploy and docs-link regression rows that are red on main in the full run 44463859531 pass again: deploy-doc14-reviewed deploy-not-locked deploy-section-optional deploy-table-refused deployments-counts-pages home-topic-column link-page-passes link-unread-never-pass doc19-readme-links del-16-on-page. Each is fixed, or removed with evidence that the behaviour it tests is gone; none is moved to the known list (owner: "No waivers u can do it").

- Slug: known-red-w3-deploy-links
- Touches: not declared
- ETA: 280 active minutes (estimate 221m plus a 25% margin, rough)

## Done lines

Frozen. A wrong done line needs a new goal.

1. Each of these rows passes on the PR head in the CI full-suite shards, or is removed from .loop/regression.tsv with evidence in the PR that the behaviour it tests no longer exists: deploy-doc14-reviewed deploy-not-locked deploy-section-optional deploy-table-refused deployments-counts-pages home-topic-column link-page-passes link-unread-never-pass doc19-readme-links del-16-on-page
2. No row is added to .loop/regression-known.tsv, and net regression rows are 0 or fewer against main

## Verify by hand

<!-- Numbered steps for a person, each with an Expect: line. A release needs this. -->
