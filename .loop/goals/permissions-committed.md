# Fresh checkouts of the template repo carry .claude/settings.json with only the allow rules its routines need, so the AUT-9 permissions check passes everywhere and no Claude session in the repo is denied git push, gh pr merge, gh release or regression runs

- Slug: permissions-committed
- Touches: .gitignore, .claude/settings.json, .loop/permissions.tsv, .loop/regression.tsv, DECISIONS.md

## Done lines

Frozen. A wrong done line needs a new goal.

1. .gitignore keeps every .claude/ file ignored except .claude/settings.json (.claude/* plus !.claude/settings.json) and .claude/settings.json is committed holding allow rules only, with no home path, user name, secret or machine-specific value
2. docs.py check prints no PERMISSIONS finding on a fresh checkout; a regression row seen red first proves settings.json is tracked and a second proves it holds no deny rule

## Verify by hand

<!-- Numbered steps for a person, each with an Expect: line. A release needs this. -->
