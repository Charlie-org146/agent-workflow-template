# Adoption is proven on this machine: a repo set up by setup carries its template version, setup prints a prerequisite checklist and replays the golden first adoption strictly, the operation session adopts several repos in one pass and probes each repo's connectors, private-name patterns can be scoped per repo, and no adoption MIG finding is left that this machine can fix

- Slug: adoption
- Touches: skills/workflow-setup, skills/workflow-monitoring/scripts/board.py, dev/toy, docs, .loop, README.md

## Done lines

Frozen. A wrong done line needs a new goal.

1. A repo set up by setup holds its installed template_version in its config, so update --apply has nothing to stamp
2. setup prints one prerequisite checklist before it writes anything, each failing line with its exact fix
3. The strict adoption replay compares each observed step with dev/toy/adoption-golden.tsv and stops at the first mismatch naming what differs
4. board.py repos can adopt several GitHub repos in one pass and ends with each on the current template version
5. setup lists each followed repo's needed connectors with connected, needs sign-in or missing, and never enables one
6. A private-name pattern can be scoped to named or public repos, and setup explains the list when it seeds it
7. health check reports no adoption MIG finding that this machine can fix, and each one it cannot is named with why

## Verify by hand

<!-- Numbered steps for a person, each with an Expect: line. A release needs this. -->
