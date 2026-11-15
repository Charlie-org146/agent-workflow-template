# Keep a repo's GitHub milestones and an external Milestones page in step both ways, opt in per repo, the way ext-two-way does it for PRDs: each side can add to it and a difference between them is reported, never silently overwritten (issue 4186). The template code is generic and names no Notion page or id; every file stays at or under 19,000 bytes and the package at 98 files or fewer

- Slug: milestone-sync
- Touches: skills/workflow-docs/scripts, dev/toy/test-milestone-sync.py, .loop/regression.tsv, .loop/docs.tsv, DECISIONS.md

## Done lines

Frozen. A wrong done line needs a new goal.

1. With an external Milestones source set for a repo, one command compares the repo's GitHub milestones with that source: an addition or change on either side is raised as a delta and applied to the other side only through the same reviewed path DOC-17 uses for PRDs, and a milestone that differs on both sides is reported as a conflict and never overwritten
2. A repo with no external Milestones source raises and shows nothing, and the template code names no Notion page, id or repo (only the opted-in repo's own config holds a source)
3. A toy on a fake connector and fake gh, each case seen red first, proves one change from each side, one conflict and one repo with no source; no script goes over 19,000 bytes and the package stays at 98 files or fewer

## Verify by hand

<!-- Numbered steps for a person, each with an Expect: line. A release needs this. -->
