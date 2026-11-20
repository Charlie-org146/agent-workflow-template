# Size rows follow GRD-20 as approved: scripts warn at 19,000 bytes and fail at 20,480 (TD412, approved by operation-top under owner delegation DOC-2, o486; the approved README's GRD-20 r4 says 'scripts warn at 19,000 bytes and fail at 20,480 (Agensi's 20 KB)'). Five regression rows still FAIL a script over 19,000 and so fail on main since tonight's approved merges (#5472, #5482): est-module-size (issue 5495), size-141 (5493), trim-monitoring-4-size (5497), scripts-c-health-under-19000 (5498) and size-budget (5494). Each becomes: a WARN line naming each script over 19,000 (still visible in health) and FAIL only over 20,480, with a negative control that a file over 20,480 still fails; their descriptions state the approved figures. Also diagnose no-milestone-issue-ok (issue 5496; the health report's Docs group fails): fix it in this goal if it is small and one cause, otherwise report the cause for its own goal. Small fix: the rows' commands and toys only, no shipped script grows

- Slug: size-rows-follow-grd20
- Touches: .loop/regression.tsv, dev/toy
- ETA: 460 active minutes (estimate 368m plus a 25% margin)

## Done lines

Frozen. A wrong done line needs a new goal.

1. Given main's scripts (several between 19,000 and 20,480 bytes, none over), when the five rows run, then each passes and prints a WARN line naming every script over 19,000; and given a fixture script of 20,481 bytes, then each row's check fails (negative control)
2. Given the five rows, then each row's description states 'warn at 19,000, fail at 20,480' (each 400 characters or less), the row count is unchanged, and no shipped script under skills/ grows
3. Given no-milestone-issue-ok, then either it passes on this branch with the one cause fixed and named in the pull request, or the pull request names its cause with the failing line and it is left for its own goal; and docs.py check, criteria.py render --check and role.py over_caps pass

## Verify by hand

<!-- Numbered steps for a person, each with an Expect: line. A release needs this. -->
1. Run `python3 dev/toy/size-check.py --control 'skills/*/scripts/*.py'`.
   Expect: PASS negative control (20,481 bytes fails, 20,480 only warns), then one WARN line per script over 19,000 and exit 0.
2. Run `bash dev/toy/test-estimates.sh module_size` and `python3 dev/toy/test-trim-monitoring.py`.
   Expect: a WARN line for each file over 19,000, and PASS for the 20,481-byte negative control.
