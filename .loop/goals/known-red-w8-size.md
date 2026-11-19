# Main-red size and caps rows pass again or are removed with evidence, so the v2.0 release gate's full suite has no FAIL outside the known list (TOP-DECISION 52-54, o195 no waivers, o212)

- Slug: known-red-w8-size
- Touches: dev/toy/test-defect.sh, skills/workflow-monitoring/SKILL.md, skills/workflow-release/SKILL.md, skills/workflow-monitoring/scripts/checkin.py, skills/workflow-setup/scripts/setup.py, skills/workflow-regression/scripts/runs.py, skills/workflow-regression/scripts/lanes.py, skills/workflow-regression/scripts/regression.py, skills/workflow-health/scripts/report.py, skills/workflow-health/scripts/rules.py, skills/workflow-health/scripts/automation.py, skills/workflow-health/scripts/controls.py, .loop/regression.tsv, docs/wiki/Tests.md, docs/wiki/Health.md, docs/wiki/Regression.md, docs/wiki/Release.md, docs/wiki/Documentation.md, docs/wiki/Monitoring.md, docs/wiki/Setup.md, skills/workflow-monitoring/scripts/board_lines.py, skills/workflow-regression/references/commands.md, skills/workflow-health/references/commands.md, docs/wiki/Check-in-and-board.md, docs/wiki/How-to-use-Check-in-and-board.md, docs/wiki/How-to-use-Monitoring.md, docs/wiki/How-to-use-Operation.md, docs/wiki/Operation.md, docs/wiki/Principles.md
- ETA: 225 active minutes (estimate 177m plus a 25% margin, rough)

## Done lines

Frozen. A wrong done line needs a new goal.

1. Each of these rows passes on the PR head in the CI full-suite shards, or is removed from .loop/regression.tsv with evidence in the PR that the behaviour it tests no longer exists: size-141 skill-kept skill-size-116 skill-lines-release-4172 scripts-c-health-under-19000 scripts-c-regression-under-19000 docs-release-scripts-under-19000 trim-monitoring-4-size trim-setup-under-19000
2. No row is added to .loop/regression-known.tsv, and net regression rows are 0 or fewer against main

## Verify by hand

<!-- Numbered steps for a person, each with an Expect: line. A release needs this. -->

1. Run `python3 dev/toy/test-trim-monitoring.py` and `python3 -B dev/toy/split-check.py . skills/workflow-regression/scripts/regression.py runs chosen,clean,criteria_ids,criterion_rows,done_lines,lines_of,today path_of`.
   Expect: the first prints PASS lines including `PASS negative control` and exits 0; the second prints nothing and exits 0.
2. Measure the scripts: `python3 -c "import glob; print([f for d in ('health','regression','release') for f in glob.glob('skills/workflow-%s/scripts/*.py' % d) if len(open(f,'rb').read().replace(b'\r\n',b'\n'))>19000])"`, then check `skills/workflow-setup/scripts/setup.py` and `skills/workflow-monitoring/scripts/checkin.py`.
   Expect: `[]`; setup.py is 18,991 bytes and checkin.py 18,096. The workflow-docs scripts stay over until w11 lands.
3. Count the lines of every `skills/*/SKILL.md`.
   Expect: each is under 150 (monitoring 149, release 149).
4. Run `python3 skills/workflow-docs/scripts/docs.py check`, `python3 skills/workflow-docs/scripts/entry.py check` and `python3 skills/workflow-release/scripts/wiki.py prepare known-red-w8-size`.
   Expect: DOCS OK: 16 pages, ENTRY OK and WIKI CURRENT; docs/wiki/Principles.md, .loop/docs.tsv and skills/workflow-health/references/commands.md are identical to main.
