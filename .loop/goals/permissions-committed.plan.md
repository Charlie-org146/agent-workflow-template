# permissions-committed plan

Checked: .gitignore line `.claude/` ignores the folder; `audit.py permissions write` merges allow and deny rows of .loop/permissions.tsv into
.claude/settings.json; docs.py check calls entry.perm_check, which reports NOT WRITTEN for each row missing from settings.

## Build steps
1. .gitignore: `.claude/` becomes `.claude/*` plus `!.claude/settings.json`.
2. .loop/permissions.tsv: delete the deny rows (health-round and regression-round: git push, gh pr merge, gh release, regression.py run).
3. Regenerate .claude/settings.json from the allow rows (`audit.py permissions write`) and commit it.
4. .loop/regression.tsv: `perms-settings-tracked` (git ls-files --error-unmatch) and `perms-no-repo-deny` (no "deny" key), each seen red.
5. DECISIONS.md: a short note that AUT-9's text is unchanged and why denies are not written repo-wide.

## Tests
perms-settings-tracked (break: git rm --cached) and perms-no-repo-deny (break: add a deny rule), both AUT-9; docs.py check clean in a fresh clone.

## What could break
Another repo that wants repo-wide denies still can: the tool writes deny rows when a repo declares them; only this repo declares none.

## Out of scope
Per-routine deny scope (Claude Code project settings cannot scope a deny to one routine; filed as backlog already).
