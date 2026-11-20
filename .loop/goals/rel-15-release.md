# The release adds no second pass through the checks (REL-15, second of three goals; it follows rel-15-queue). Today autorelease.py finish() (lines 366 to 373) pushes the release commit to main or opens a release PR through merge.advance, so every merged goal is followed by a commit or pull request that re-enters CI or the queue. The goal moves the release to CI on push to main, by tag: a workflow creates the tag and the GitHub release (adopt release-please, https://github.com/googleapis/release-please, or run gh release create --generate-notes in a workflow, https://cli.github.com/manual/gh_release_create; the goal names the one it chose and its link, per principle 7), so no release commit and no release PR is made. It says on the Release page what happens to VERSION and CHANGELOG.md (who writes them, in which pull request) and keeps health's version checks true. It depends on rel-15-queue being merged

- Slug: rel-15-release
- Touches: skills/workflow-release/scripts/autorelease.py, .github/workflows, docs/wiki/Release.md
- ETA: 345 active minutes (estimate 275m plus a 25% margin)

## Done lines

Frozen. A wrong done line needs a new goal.

1. Given a goal's pull request merged by merge.py, when the release publishes, then a workflow on push to main creates the tag and the GitHub release, and no release commit is pushed to main and no release pull request is opened, so nothing after the merge needs a lane or a CI run; a toy case proves autorelease.py finish() pushes no commit and opens no pull request
2. Given the Release feature page, then it names the tool it adopted with its link, and says what happens to VERSION and CHANGELOG.md (who writes them and in which pull request) and that the wiki publish after the merge is outside REL-15's 5 minutes, and the docs check passes
3. Given health and the existing release checks, when they run after the change, then they pass with the new flow, and the goal adds no regression row that fails on current main

## Verify by hand

<!-- Numbered steps for a person, each with an Expect: line. A release needs this. -->
