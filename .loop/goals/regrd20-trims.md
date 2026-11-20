# #5375 (merged 05:53) reindented guards.py, private.py and role.py to fit under 20,480 bytes, which the approved GRD-20 refuses ('Reformatting a whole file only to fit') (TD460). Restore each file's original indentation and stay under 20,480 bytes by real trims only (dead code, duplicate helpers, shorter messages that keep their meaning), with the AST comparison in the PR showing behaviour is unchanged apart from the named trims

- Slug: regrd20-trims
- Touches: skills/workflow-delivery
- ETA: 405 active minutes (estimate 322m plus a 25% margin)

## Done lines

Frozen. A wrong done line needs a new goal.

1. Given guards.py, private.py and role.py on this branch, then each uses the indentation it had before #5375 and is under 20,480 bytes
2. Given the pull request, then it lists each trim with its reason and shows an AST comparison against main proving no other change, and no line is reformatted only to save bytes
3. Given this branch, then every regression row that runs these three scripts passes, and docs.py check and criteria.py render --check pass

## Verify by hand

<!-- Numbered steps for a person, each with an Expect: line. A release needs this. -->
