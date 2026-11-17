<!-- workflow-docs -->
# How to use Release

## What it's for

A major version (a milestone) ships only through a hard gate: every milestone issue closed, the full regression suite green, health green, every requirement Reviewed by you and no stale page. After the release candidate is cut only gate fixes enter, and promotion leaves a tag, a snapshot branch and a state report you can revert to (owner records o144 and o145).

### What's delivered

| Component | Kind | What it is | How a user uses it |
|---|---|---|---|
| `review.py gate` | Command | Runs the five gate checks on a release candidate and prints `GATE PASS` or one `GATE REFUSED` line per failure, naming the issue, row, requirement or page. | `python3 skills/workflow-release/scripts/review.py gate v2`. |
| `review.py promote` | Command | Promotes a major: gate, tag `vX.0.0`, branch `release/vX`, main moved, state report published and mailed. | `python3 skills/workflow-release/scripts/review.py promote v2 --owner-record ID`. |
| `review.py revert` | Command | Opens a pull request that puts main back on the `release/vX` snapshot. | `python3 skills/workflow-release/scripts/review.py revert v2`. |
| `release-waivers.tsv` | API/file contract | The owner's waivers for the gate, kept in the git folder outside the repo. | The operation session adds a line after you name the issue or row in your own words. |

## How to reach or run it

Say these to the agent in the operation session; each feature page has the exact commands.

| You say | What happens |
|---|---|
| "Can v2 ship?" | The gate runs on the release candidate and lists every reason it would refuse, or prints `GATE PASS v2.0`. |
| "Move issue 7 to v2.1" | After your words are recorded, a `moved` waiver names the issue, and promotion moves it to the later milestone. |
| "Waive row stale-found, issue 9" | A `red` waiver names the row and its issue; the gate stops refusing that row. |
| "Promote v2" | If your words name `v2.0.0` and every check passes, it tags `v2.0.0`, keeps `release/v2`, moves main and mails the state report. |
| "Go back to v2" | A pull request puts main's tree back on `release/v2`; you merge it. |

Each requirement and how it is delivered:

- REL-1: A version number says what changed, and a major ships only through the gate. Example, from the rel-major-refused test: given a goal whose release would bump a major, when release.py bumps the version, then it refuses naming review.py promote.
- REL-2: Every issue on the milestone is closed, or the owner moved it by name. Example, from the rel-open-issue-refused test: given a milestone with an open issue, when the gate runs, then it refuses naming the issue.
- REL-3: The full regression suite passes on the release candidate, and each known-red row is fixed or waived with an issue. Example, from the rel-red-row-refused test: given a known-red row with no waiver, when the gate runs, then it refuses naming the row.
- REL-4: Health passes, every requirement is Reviewed by the owner, and no wiki page is stale. Example, from the rel-checks-refused test: given a requirement that is not Reviewed, when the gate runs, then it refuses naming the requirement and its page.
- REL-5: Once the release candidate is cut, only fixes for gate failures enter staging. Example, from the rel-freeze-refuses test: given a cut release candidate, when a goal naming no gate failure merges, then merge.py refuses with frozen for vX.0.0.
- REL-6: Promoting a major tags it, keeps a snapshot branch and sends a state report. Example, from the rel-promote-snapshot test: given every check green and an owner record naming the version, when promote runs, then the tag, the branch, the release notes and the mail all exist.
- REL-7: `revert vX` puts main back on the snapshot through a pull request. Example, from the rel-revert-pr test: given release/vX, when revert runs, then a pull request to main carries the snapshot's tree.
- REL-8: Promotion and every waiver are the owner's words, never a worker's or a peer session's. Example, from the rel-owner-only test: given a worker, when it runs promote, then it is refused and nothing changes.

### Command: review.py gate
- **Command:** `python3 skills/workflow-release/scripts/review.py gate vX [--ref REF] [--no-suite]`
- **Dry run:** the gate only reads, except that it saves its refusals to the git folder for the freeze; `--no-suite` skips the suite and health.
- **Reads:** the milestone's issues (gh), a throwaway checkout of REF (default: the newest `vX.0.0-rc.N` tag, else `origin/staging`, else the base), the waivers and the owner-words records.
- **Writes:** `loop/gate/vX.json` in the git folder.
- **Exit codes:** 0 on `GATE PASS`; 1 with one `GATE REFUSED vX.0 (check): subject` line per failure.

### Command: review.py promote
- **Command:** `python3 skills/workflow-release/scripts/review.py promote vX --owner-record ID [--ref REF]`
- **Dry run:** none; a refused gate or owner record changes nothing.
- **Reads:** the same as the gate, and the owner-words record, which must name `vX.0.0`.
- **Writes:** tag `vX.0.0`, branch `release/vX`, main (fast-forward only), a GitHub release carrying the state report, and the report file `loop/gate/vX.0.0.md`; it mails the report when the machine's mail.env is set up.
- **Exit codes:** 0 when promoted (an `EMAIL not sent` line says the mail did not go); 1 on a gate refusal; nonzero with `OWNER_RECORD`, `REVIEW_ROLE` or `PROMOTE_PUSH`.

### Command: review.py revert
- **Command:** `python3 skills/workflow-release/scripts/review.py revert vX`
- **Dry run:** none.
- **Reads:** branch `release/vX` and the base.
- **Writes:** a branch `revert/vX-STAMP` and a pull request to the base; never the base itself.
- **Exit codes:** 0 with `REVERT PR`; nonzero when `release/vX` does not exist or the caller is a worker.

### API/file contract: release-waivers.tsv
- **Path:** `loop/release-waivers.tsv` in the git folder (outside the repo).
- **Fields:** `kind`, `subject`, `detail`, `owner record`: `moved`, `#7`, `v2.1`, `o12` or `red`, `row-id`, `#9`, `o13`.
- **Example:** `red	stale-found	#9	o13`
- **Writer:** the operation session, only after the owner's words naming the subject are recorded.
- **Reader:** `review.py gate` and `promote`; a line whose record is missing or does not name the subject waives nothing.

## URLs and deployments

- Wiki: [Release](https://github.com/jcl2018/agent-workflow-template/wiki/Release)
- Releases: https://github.com/jcl2018/agent-workflow-template/releases

## Links

- PRD page: [Release](Release)
- Backlog: [Backlog: Release](https://github.com/jcl2018/agent-workflow-template/milestones)
