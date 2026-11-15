# permissions-committed design

## Problem
`.claude/` is in .gitignore, so the `.claude/settings.json` that AUT-9's setup writes was never committed (settings-in-spec, v0.28.59). A fresh
checkout of main, and every new worktree, has none, so `docs.py check` prints NOT WRITTEN findings and fails. Committing the file as written would
also ship four deny rules (git push, gh pr merge, gh release, regression.py run) that Claude Code applies to every session in the repo, which would
block workers' own pushes and row runs.

## Approaches
1. Commit the file as written (allow and deny). One line of .gitignore. Risk: repo-wide denies block the work the template's own sessions do.
2. Commit allow rules only: .gitignore keeps every other `.claude/` file ignored (`.claude/*` then `!.claude/settings.json`), .loop/permissions.tsv
   keeps only allow rows, settings.json is regenerated from them with `audit.py permissions write`. A routine's "never" stays in its Runbook text.

## Chosen: 2
It fixes the check on fresh checkouts without changing what any session in the repo may do. AUT-9's reviewed text is unchanged (rows still map to
settings, and the CONFLICT check still catches an allow a deny covers). The file holds only generic rules and `~`, no home path, name or secret.

## What each done line needs
1. .gitignore `.claude/*` plus `!.claude/settings.json`; settings.json committed with allow rules only.
2. docs.py check clean on a fresh checkout; rows `perms-settings-tracked` (git ls-files) and `perms-no-repo-deny` (no deny key in the file), each seen red.

## Open questions
None for the owner.
