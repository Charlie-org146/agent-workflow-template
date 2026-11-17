# Fix #4892 (govern_hook part): remove __import__ from govern_hook.py's quiet hook so dev/package.py's safety scan passes (package-passes-3800, package-passes); the delivery scripts' 19,000-byte limit stays with trim-scripts-19k (#4653)

- Slug: hotfix-4892
- Touches: skills/workflow-monitoring/scripts/govern_hook.py, .loop/regression.tsv, dev/toy
- ETA: 210 active minutes (estimate 168m plus a 25% margin)

## Done lines

Frozen. A wrong done line needs a new goal.

1. dev/package.py's safety scan passes: skills/workflow-monitoring/scripts/govern_hook.py has no __import__ call, the quiet hook still works, and setup.py --reply-hook still installs it; package-passes-3800 and package-passes pass
2. A defect row (quiet-plain-import-4892) seen failing on the old line and passing now proves govern_hook.py has no __import__ and remember() still writes what held() reads back; no new file is added to the shipped package

## Verify by hand

<!-- Numbered steps for a person, each with an Expect: line. A release needs this. -->
