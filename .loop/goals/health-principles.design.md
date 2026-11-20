# Design: health-principles

Problem: health prints a PRINCIPLE line per principle but only reds it on a failing group. Nothing is red for a principle with no Reviewed requirement or no rule that can fail, no requirement may sit under no principle unseen, and `health review` has no per-principle view.

Source of truth: docs/wiki/Principles.md Part 1 (generated tables, `## N. Name`, one row per requirement) for the principle to requirement map; references/commands.md "## The principles" for names and groups; the feature pages for Reviewed state; regression.tsv for tests.

Approaches: A. a new script (rejected: package file cap); B. fold a small map reader and checks into rules.py with a one-line call from judge.principles(), plus a per-principle block in review (chosen); C. read the map from condensed.json (rejected: not in the repo).

Verification: negative controls on broken copies (principle emptied, group without rules, requirement outside the map), a toy check that a one-word README difference fails health naming the line, sizes under 19,000 and judge.py at most 18,999, net rows 0 or fewer, each changed row seen red.
