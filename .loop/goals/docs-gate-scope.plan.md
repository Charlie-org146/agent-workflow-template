# Plan: docs-gate-scope

Checked against the code: wiki.pending (wiki.py:56) calls release.docs_trouble(whole=True), which prints docs.py audit lines
(`LINKS|HOME|HOWTO PAGE: DOC-N ...` are not in audit.REWRITE, so they print as their kind); merge.py:279 refuses on any returned line;
milestones.py already has `post`, `backlog`, `stands_alone`, `alone`; dev/toy/test-merge-stale-own.py is the model for a throwaway-repo toy.

## Build steps
1. Trim milestones.py (docstrings, long messages) by about 1.5 KB with no behaviour change; run test-stands-alone.py, test-how-to-use.py.
2. milestones.py: `origins`, README and own-site handling in `stands_alone`/`alone`; `untouched` and `file_issue`.
3. wiki.py `pending`: the changed-pages diff, call `untouched`, print FINDING lines; keep under 20,480.
4. dev/toy/test-docs-gate-scope.py (throwaway repo, fake gh via LOOP_GH): untouched page filed and passes, changed page refuses, no second issue,
   stale generated line still refuses; own-site and README links pass, outside link still fails.
5. regression rows (each seen red), Release.md and Documentation.md wording (Unreviewed), regenerate Tests tables, entry.py write.
6. Size rows, wiki prepare, docs check, entry check; Verify by hand.

## Tests per done line
a) gate-untouched-passes, gate-files-once, gate-changed-refuses, gate-stale-block-refuses. b) links-own-origin-passes, links-readme-passes,
links-outside-fails. c/d) existing size rows.

## What could break
- Reviewed requirement lines: new wording is Unreviewed bullets only; do not edit Reviewed text (ask the owner via operation-pc).
- Script size: wiki.py 19,319 and milestones.py 19,347 already past 19,000; neither may pass 20,480.

## Out of scope
Moving DOC-19 checks, changing lane (check --own) scope, private page content.
