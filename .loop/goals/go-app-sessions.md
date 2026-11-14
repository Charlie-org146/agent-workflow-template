# Under a pod setting workers: app, watch.py go and watch freeze a goal and hand it to sessions.py assign or bind and never launch a background process; watch.py runs() skips run-folder files that are not goal records

- Slug: go-app-sessions
- Touches: docs

## Done lines

Frozen. A wrong done line needs a new goal.

1. With workers: app a goal that no app session could take stays frozen and queued for bind, with no process launched, and says so
2. Without the setting the background fallback is unchanged
3. A non-dict .json file (a list) in the runs folder no longer crashes watch.py runs()

## Verify by hand

<!-- Numbered steps for a person, each with an Expect: line. A release needs this. -->
