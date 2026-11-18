# Release feature: a hard-release gate for every major (issue #4914): version policy, a promotion gate, a freeze after the rc is cut, a snapshot with release/vX and a state report, and revert, with a new Release wiki page and REL-n requirements

- Slug: release-gate
- Touches: skills/workflow-release, docs/wiki, dev/toy/test-release-gate.py, .loop/regression.tsv, .loop/docs.tsv
- ETA: 265 active minutes (estimate 212m plus a 25% margin)

## Done lines

Frozen. A wrong done line needs a new goal.

1. Given a milestone with an open issue the owner has not moved by name, when review.py gate vX runs, then it refuses with GATE REFUSED (issues) naming the issue; an issue with a recorded owner move waiver does not refuse
2. Given a full-suite row that is red with no owner waiver naming an issue, a failing health check, a requirement that is not Reviewed, or a stale wiki page, when review.py gate vX runs, then it refuses and names the row, the check, the requirement or the page; a row waived with an issue does not refuse
3. Given a release candidate with every gate check green and an owner record naming the version, when review.py promote vX runs, then it tags vX.0.0, creates the release/vX branch, publishes the state report as the release and emails it; given any gate refusal it creates no tag, no branch and no release
4. Given a cut release candidate for a major, when a goal that names no gate failure merges into staging, then merge.py refuses with frozen for vX and merges nothing; a goal that names a recorded gate failure is let through
5. Given release/vX, when review.py revert vX runs, then it opens a pull request whose tree is the snapshot's tree on top of main, and it never pushes main
6. A goal's release never bumps a major: the version policy (patch is a fix, minor is a goal inside a milestone, major is a milestone that ships only through the gate) is enforced by release.py refusing a major bump outside promote
7. docs/wiki/Release.md holds requirements REL-1 to REL-8, all Unreviewed, each linked to a regression row seen failing first, workflow-docs check prints DOCS OK, every script stays under 19,000 bytes (checkin.py at or under 19,495) and the shipped file count does not grow

## Verify by hand

<!-- Numbered steps for a person, each with an Expect: line. A release needs this. -->
1. Run `python3 dev/toy/test-release-gate.py`.
   Expect: every line starts with PASS, and it exits 0 (it builds a throwaway repo; nothing real is touched).
2. Run `python3 skills/workflow-release/scripts/review.py gate v2 --no-suite` from a checkout of this repo.
   Expect: it prints GATE REFUSED lines, each naming an issue of milestone v2.0 or an Unreviewed requirement, and exits 1 (the gate refuses a milestone that is not done).
3. Run `grep -n "^- REL-" docs/wiki/Release.md`.
   Expect: eight lines, REL-1 to REL-8, each reading `**Unreviewed**`.
4. Run `python3 skills/workflow-docs/scripts/docs.py check`.
   Expect: it prints `DOCS OK`.
5. Run `python3 -c "import sys;sys.path.insert(0,'skills/workflow-release/scripts');import release;release.bump('1.0.54','major')"`.
   Expect: it stops with `REFUSED (MAJOR_GATE)` naming review.py promote.
