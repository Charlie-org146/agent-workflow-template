# Fix five open defects: #3862 monitor.py report on a non-record JSON, #3841 home-folder path in the PR body, #3840 statuses over-claimed, #3839 hardcoded regression.yml in Tests links, #4184 headless claude -p with workers: app

- Slug: defects-a
- Touches: skills/workflow-monitoring/scripts, skills/workflow-delivery/scripts, skills/workflow-docs/scripts, dev/toy, .loop/regression.tsv, docs/wiki

## Done lines

Frozen. A wrong done line needs a new goal.

1. monitor.py report prints the board and does not crash when loop/runs holds a JSON that is not a run record (#3862)
2. goal.py pr never copies a home-folder path from the lane records into the pull request body (#3841)
3. goal.py pr posts only the statuses for checks the lane actually ran (#3840)
4. render.py reads the regression workflow file name from config for its Tests-page links, not a hardcoded regression.yml (#3839)
5. With workers: app, flow.py refuses to start a headless claude -p for an unbound goal and names sessions.py bind (#4184)

## Verify by hand

<!-- Numbered steps for a person, each with an Expect: line. A release needs this. -->
