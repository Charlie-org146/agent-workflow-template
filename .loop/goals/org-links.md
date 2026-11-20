# CI fails the row defect-categories (and every row that runs criteria.py render --check in a repo copy) for main itself since the repository moved to a GitHub organization, because the committed generated links name the old owner but CI's checkout has the new origin (found 2026-11-20 by the principle-3-clock worker: with origin set to the organization URL, render --check prints STALE docs/wiki/Home.md (automation block), STALE README.md (template block) and STALE docs/wiki/Tests.md). This goal adds the organization origin to public_origins in .loop/config.json alongside the old one (approved by operation-top under owner delegation (DOC-2, o486), as in TD331; the old name stays until a later goal replaces the 58 files that name it), and, in this goal's worktree only, sets origin to the organization URL, runs criteria.py render and commits the three rewritten files. Generated links only: no script, test, workflow or setting changes. The Mac's other checkouts get the same remote after it merges (local, not committed)

- Slug: org-links
- Touches: .loop/config.json, README.md, docs/wiki/Home.md, docs/wiki/Tests.md
- ETA: 345 active minutes (estimate 275m plus a 25% margin)

## Done lines

Frozen. A wrong done line needs a new goal.

1. Given .loop/config.json, then public_origins lists the organization origin (https://github.com/Charlie-org146) as well as the old one, and nothing else in the file changes
2. Given a repo copy whose origin is https://github.com/Charlie-org146/agent-workflow-template.git, when criteria.py render --check runs, then it prints TABLES OK (rc 0), and README.md, docs/wiki/Home.md and docs/wiki/Tests.md are the re-rendered files; the row defect-categories passes with that origin
3. Given this goal's diff, then only .loop/config.json, README.md, docs/wiki/Home.md, docs/wiki/Tests.md and the goal's own record files change, and the docs check passes

## Verify by hand

1. In a copy of the repo whose origin is https://github.com/Charlie-org146/agent-workflow-template.git, run `python3 skills/workflow-docs/scripts/criteria.py render --check`.
   Expect: it prints TABLES OK and exits 0.
2. Run `grep -c Charlie-org146 README.md docs/wiki/Home.md docs/wiki/Tests.md`.
   Expect: each file shows at least one generated link to the organization (the hand-written wiki links in the README still use the old name, which GitHub redirects).
