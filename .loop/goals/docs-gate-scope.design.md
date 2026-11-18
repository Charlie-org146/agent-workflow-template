# Design: docs-gate-scope

## Problem
merge.py's wiki gate (wiki.pending, from release.docs_trouble whole) refuses on every `audit` line, so since v1.0.64 an adopting
repo's DOC-19 (LINKS, HOWTO) and DOC-4 (HOME) findings on pages the goal never changed block every merge. LINKS also flags
a repo's own published sites and its README, which are not history.

## Approaches
1. Move the DOC-19/DOC-4 rules out of the audit (docs check / audit stop reporting them). Loses the rule for goals that edit those pages.
2. Keep the rules everywhere; in the merge gate (wiki.pending) split the lines: a DOC-19/DOC-4 finding on a page the goal's diff
   changed still refuses; one on an untouched page is printed as a FINDING and filed once as an issue on that feature's
   "Backlog: <Feature>" milestone, never twice while one is open. Stale generated blocks and tables (Tests, START.md, REWRITE/STALE
   lines) are not DOC-19/DOC-4 and stay refused. Plus: stands_alone treats the repo's own published sites and README as inside.

## Chosen: 2
- milestones.py `untouched(lines, changed, wiki_dir)`: lines `LINKS|HOME|HOWTO PAGE: DOC-19|DOC-4 ...` whose page file (or skill-doc path)
  is not in `changed` become (kept, filed pages); `file_issue(page, texts)` opens one issue per page via the existing gh helper
  (`post`), marker `<!-- loop-docs-finding PAGE -->` in the body, milestone `backlog(feature)`; any gh failure is a NOTE, never a refusal.
- wiki.py `pending` asks git for the goal's changed wiki pages (`base...head`), calls it, prints each moved line as
  `FINDING ... (not touched by this goal; filed <issue>)`.
- milestones.py `origins(root)`: `public_origins` in .loop/config.json plus scripts/public-origins.json (a list or {"origins": [...]});
  stands_alone skips a hit under one of those origins and the repo's own README (repo root, #anchor, blob/<ref>/README.md).
- milestones.py trimmed (docstrings, messages, no behaviour change) to hold the new code under 20,480.
- merge.py unchanged unless its refusal text needs to name the filed pages (it stays under 19,000).

## Done lines
a) wiki.pending + milestones.untouched + file_issue + toys. b) origins + NEAR + toys. c) rows seen red, Release and Documentation
pages, wiki prepare, entry check. d) size rows.

## Open questions
- Where scripts/public-origins.json lives for adopting repos: the repo root `scripts/` folder, read from the working tree. Recommendation taken.
- Skill-doc findings (path-named) file under "Backlog: Documentation". Recommendation taken.
