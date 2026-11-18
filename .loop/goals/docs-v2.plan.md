# Plan: docs-v2

Checked against the code: `milestones.py` holds `howto_items`, `kinds`, `delivered`, `blocks`, `part`, `unlisted` (How-to-use
checks, called from `deployments.howto`); `pageformat.home` and `pageformat.frontdoor` own the Home and README rules;
`operate.py:314` already calls `audit.py rerender` (#4632); `deployments.howto_runbook` holds #4666; toys
`dev/toy/test-how-to-use.py`, `test-how-to-kinds.py`, `test-apply-rerender.py` exist with rows doc18-*, doc19-*, apply-rerender-*.

## Build steps
1. Free bytes: shorten comments/docstrings in deployments.py so call-site growth leaves it no bigger than main (20,095), and keep
   milestones.py under 19,000. No script grows past its current size except milestones.py. No new file.
2. milestones.py: `diagram(name, how, table)`, `stands_alone(page, text)`, skill/schedule names added to `unlisted`.
3. deployments.howto: call `diagram` and the new `unlisted` names; docs.py page loop (or criteria) calls `stands_alone` for
   every wiki page except Tests, and for skill docs (`skills/*/SKILL.md`, `references/*.md`, `loop-files.md`).
4. pageformat.home: accept one `## System diagram` section with a fenced block between the table and the generated blocks;
   report a missing diagram or a part (operation session, workers, steps, staging and production, machines, routines) it lacks.
5. Content, by a script from committed data (`tmp` scratch outside the repo): a `### System diagram` in each How-to-use page
   built from its What's delivered table; strip issue/pull/commit/Actions link wrappers to plain text in wiki pages and skill
   docs; replace other-repo and machine-path mentions; draft the Home diagram by hand. Never touch Monitoring.md:56, auto.py:39,
   the Roadmap line, or the Home/README `How to use` heading rule (#4809, private-lines-v1051).
6. Rule wording: DOC-19 sub-bullets (diagram, stands alone, skills/schedules) and DOC-4 (Home may carry the diagram), all
   Unreviewed; DECISIONS.md entry for the scoped decisions. Commands.md line for the new FORMAT lines.
7. Toys: extend `test-how-to-kinds.py` (diagram, skill, schedule negatives) and a new `dev/toy/test-stands-alone.py`? Not a
   shipped file (dev/ is not in the package): stands-alone and Home diagram negatives per class. Rows added with
   `regression.py add`, each seen red (`red`). Re-render Tests tables from committed data only.
8. Verify by hand; `docs.py check`, `audit`, `entry.py write`, package check (100 files), size rows.

## Tests per done line
1. rows stands-alone-url/issue/foreign/path/home-diagram (negatives) and stands-alone-repo-passes.
2. rows diagram-missing-row, diagram-extra-part, diagram-passes.
3. rows unlisted-skill, unlisted-schedule, unlisted-listed-passes.
4-6. existing doc19 item rows, runbook-plain/runbook-scheduled rows, apply-rerender-* rows run in the lane, unchanged.

## What could break
- Home and Roadmap are strict generated formats; render must keep a hand-written diagram section.
- Reviewed pages: Delivery/Monitoring/etc. Reviewed lines may contain issue links; stripping a link wrapper changes reviewed
  text and trips LOCKED. Mitigation: check which lines are Reviewed first; ask operation-pc for un-review (o130) only if needed.
- Script size caps; the known-red size rows.

## Out of scope
README rewrite (#4809), trimming pages for agent loading (size target), removing issue numbers, Notion sync.

PENDING: none (recommendations taken under o118)
