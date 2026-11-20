# Part 0b (TD231): each lane writes .loop/lane-results/<slug>.tsv instead of appending .loop/regression-runs.tsv and re-rendering the Tests tables; the release commit on main renders the Tests tables, regression-runs.tsv, .loop/START.md, Home and the settings rows from the merged tree and fragments (towncrier)

- Slug: results-render
- Touches: skills/workflow-delivery/scripts/lanekit.py, skills/workflow-regression/scripts/lanes_cli.py, skills/workflow-release/scripts/autorelease.py, skills/workflow-docs/scripts/render.py, skills/workflow-release/scripts/wiki.py, .loop/lane-results/, dev/toy/test-lanes.sh, .loop/regression.tsv
- ETA: 255 active minutes (estimate 202m plus a 25% margin)

## Done lines

Frozen. A wrong done line needs a new goal.

1. Given three fixture PRs that each run a lane and touch the same feature page, when they merge in any order, then no conflict, and after the release step the tree is byte-identical whichever order
2. Given the release step on main, then it renders every generated file, removes fragments already rendered, and docs.py check passes on main after it
3. Given this goal's diff, then no shipped file is added, no touched script is over 19,000 bytes or larger than on main (trim to pay), net regression rows are 0, and no requirement text changes

## Verify by hand

<!-- Numbered steps for a person, each with an Expect: line. A release needs this. -->
