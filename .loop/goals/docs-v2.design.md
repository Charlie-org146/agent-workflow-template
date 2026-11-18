# Design: docs-v2

## Problem
Four of the six issues (#4632, #4657, #4666 and most of #4677) already landed on main (apply-rerender, howto-per-requirement,
howto-kinds); only their proofs and one gap (a feature page naming a skill or schedule its How-to-use page doesn't list) remain.
The new work is #4698 (a System diagram per How-to-use page, checked against the delivered table) and #4784 (wiki and skill
docs stand alone: no history links, no other-repo names, no machine paths, a whole-system diagram on Home).

## Approaches
1. A new check module plus rewritten pages. Cleanest, but the package is at its 100-file cap and every workflow-docs script is
   within 1.5 KB of the 20,480-byte cap, so a new file or any growth of docs.py, criteria.py, deployments.py is refused.
2. Put the new checks in `milestones.py` beside `howto_items`, `kinds` and `unlisted` (the existing How-to-use checks, 3 KB of
   room), call them from `deployments.howto` and the page loop, and pay for the call sites by trimming deployments.py.
   Pages are rewritten by a script from committed data.

## Chosen: 2
- `milestones.diagram(name, how, rows)`: the page's `### System diagram` holds one fenced block; each delivered row (Kind, Component)
  is a box `[Kind: Component | where it runs]`, a `Legend:` line is required, a box with no row or a row with no box is named.
- `milestones.stands_alone(page, lines)`: outside a Deployments table, a URL fails unless it is this repo's own milestone,
  releases or wiki page (navigation, not history); an issue, pull, commit, Actions link, any other host or repo, an
  `owner/repo#N` reference or a machine path (a Windows or Unix home folder) fails naming the page and line. The generated
  Tests page cites CI evidence and is exempt. Issue numbers stay as plain text; issue links lose their link.
- Home: a `## System diagram` section (one fenced diagram: operation session, workers, steps, staging/production, machines,
  routines, with legend and guard marks) between the features table and the generated blocks; `pageformat.home` allows it, and
  its check names a part the diagram lacks. DOC-4 wording follows (Unreviewed).
- `milestones.unlisted` extends from commands to skills (`/workflow-x`) and schedules (cron in backticks).
- DOC-19 gains sub-bullets for the diagram, stands-alone and skill/schedule rules, each with test rows seen red;
  #4632/#4657/#4666 get no new code: their existing rows are cited in the PR.

## Done lines
1. #4784: stands_alone + Home diagram check + pages scrubbed, toy with negative controls per class.
2. #4698: diagram check + 9 diagrams + DOC-19 sub-bullet + rows.
3. #4677: unlisted skill/schedule + rows; Kind rows cited.
4-6. #4657, #4666, #4632: existing rows run in the lane and pass; docs check clean.

## Open questions
- #4809 (the Mac) rewrites the DOC-4/Home rule too: this goal edits `pageformat.home` for the diagram section only and rebases
  on whichever merges first. Recommendation taken: proceed.
- Tests.md exempt from the link rule (generated evidence). Recommendation taken.
