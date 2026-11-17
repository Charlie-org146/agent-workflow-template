# Fix #4859: dev/toy/test-defect.sh runs with a sandboxed HOME so defect-owed, pr-body-no-checks and worker-runs-release pass on CI and never touch the real HOME

- Slug: hotfix-4859
- Touches: dev/toy/test-defect.sh, .loop/regression-known.tsv, .loop/regression.tsv
- ETA: 180 active minutes (estimate 141m plus a 25% margin)

## Done lines

Frozen. A wrong done line needs a new goal.

1. bash dev/toy/test-defect.sh runs under a temporary HOME and USERPROFILE, so a run never reads or writes the real HOME
2. The regression rows defect-owed, pr-body-no-checks and worker-runs-release pass, and a negative control shows a poisoned real HOME is never read or written
3. Rows doc19-item-missing, judge-key-old and link-unread-never-pass are fixed if they share the cause, otherwise named in the pull request body; fixed rows are not left in .loop/regression-known.tsv

## Verify by hand

<!-- Numbered steps for a person, each with an Expect: line. A release needs this. -->

1. Run `grep -n "real_home" dev/toy/test-defect.sh`.
   Expect: the first line exports a temporary HOME and USERPROFILE, and the `home-sandbox` case checks that HOME is not the real one.
2. On Linux or macOS run `bash dev/toy/test-defect.sh home-sandbox`.
   Expect: it exits 0 and prints nothing, and `~/.workflow-loop` is not touched.
