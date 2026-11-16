# Design: sweep-health

## Problem
About 60 auto-filed "health: ..." issues have no milestone, so v1.0.0 cannot clear. Many cover findings main has since fixed (scripts trimmed, pages re-reviewed, settings filled); the rest are real. The sweep must close the first kind with proof and group the second kind where one person can read it, without fixing anything.

## Approaches
1. Close by hand: read each issue, check it against `health.py check`, `gh issue close` with a comment. Cost: slow, error prone across ~110 issues, and the proof is typed rather than produced by health. Risk: closing something health would reopen.
2. Use health's own re-check path: `health.py preview` lists, per issue, what `file` would open, update, close or reopen; `health.py file --group G` applies it for one group and closes an issue only when its own rule ran and no longer finds it. Cost: it can also open or update issues. Risk: it closes a finding whose rule was skipped on this machine, and it opens new issues for findings not yet filed.

## Chosen
Approach 2, group by group, after reading the preview. The groups whose preview only closes and updates (size, consistency, docs, traceability, requirements, performance) are filed with `file --group`. Adoption is not: its preview would close the Mac-only task finding (#3822, a rule skipped on this PC) and reopen a finding the owner keeps on purpose, so the adoption closes are made one issue at a time with `gh issue close` and the passing line, and #3822 stays open. New findings that `file` opens land on a Backlog milestone, which v1.0.0 does not count, and are listed on the tracking issue. Regression: issues are not filed (`--group regression` is never used; pool-09 owns them).

## What each done line needs
1. `health.py check` and `preview` run on current main (the worktree is origin/main); the closes come from `file --group` output and, for adoption, per-issue comments quoting the health line that no longer appears.
2. One new tracking issue; one summary comment grouped by cause (size by script owner, consistency usage-readme, MIG, docs locked, requirements rows, traceability, Home format), marking those scripts-b (PR #4278) and scripts-c will close.
3. No mail, no digest, no `file --review`, no edit to scripts or pages; the only file in the diff is the sweep record under docs/.
4. Counts (closed, still open by group, expected with scripts-b and scripts-c) are in the record, the tracking issue and the report.

## Open questions
None for the owner. The 3 FAIL lines in the check are findings to list, not to fix here.
