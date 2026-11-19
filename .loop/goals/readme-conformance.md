# Every requirement bullet in the consolidated README (requirements-consolidate) is audited against the code, tests, docs and adopter migration, and a gap table records each as done, partial or missing with evidence and the goal that closes it; the 38 issues moved to v2.0 are each mapped to a README bullet as a gap, closed by a named goal, or proposed for close; the v2.0 gate waits on zero gaps (owner o236; TOP-DECISION 95, 97, 121)

- Slug: readme-conformance
- Touches: .loop/readme-gap-table.md, .loop/readme-issues-map.md
- ETA: 220 active minutes (estimate 175m plus a 25% margin, rough)

## Done lines

Frozen. A wrong done line needs a new goal.

1. A gap table in .loop/ lists every README requirement bullet with status done, partial or missing, the evidence (file and line, test row or doc page) and the closing goal for each gap, built first from requirements-consolidate's pushed tip and re-run as a delta after it merges
2. Each of the 38 issues moved to v2.0 is mapped to a README bullet and marked a gap, closed by a named goal, or proposed for close with a reason; the close list goes to operation-top in one message for the owner's words
3. It changes no requirement text, adds no shipped file, and net regression rows are 0 or fewer

## Verify by hand

<!-- Numbered steps for a person, each with an Expect: line. A release needs this. -->

1. Open `.loop/readme-gap-table.md`. Expect: a result line (226 bullets: 137 done, 63 partial, 25 missing, 1 n/a), 20 gap clusters, and one row per bullet with status, evidence and the cluster that closes each gap.
2. Pick two gap rows (DEL-19.2 and MCH-1.7) and check their evidence: `git grep -n "standing\|requirement" skills/workflow-delivery/scripts/goal.py` and `git grep -n -F '"--body"' skills/*/scripts/merge.py skills/*/scripts/milestones.py skills/*/scripts/prdcopy.py`. Expect: no freeze check for a Reviewed requirement in goal.py; five `--body` calls in the three scripts.
3. Open `.loop/readme-issues-map.md`. Expect: all 38 issues (#5219 to #5229 in one table, the other 27 in a second) each with a README bullet or `none`, a state (gap, closed by a named goal, close proposed, README silent) and a reason, then a close list.
4. Run `python3 skills/workflow-docs/scripts/docs.py check` and `git diff --stat origin/main -- . ':!.loop'`. Expect: DOCS OK; no change outside `.loop/` (no shipped file, no requirement text).

