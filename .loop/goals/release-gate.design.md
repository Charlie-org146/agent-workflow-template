# release-gate design

## Problem
Goals keep landing fixes while a release is being deployed, so quality drifts. A major (a milestone) needs a hard
gate: nothing ships until the milestone's issues, the full regression suite, health, the owner's reviews and the docs
are all settled, nothing but gate fixes enters after the rc is cut, and a snapshot exists to go back to. release-channels
(#4778, the Mac) supplies staging, `vX.Y.Z-rc.N` tags and promotion of minors and patches; it is not on main yet.

## Approaches
1. **A new script `gate.py`.** Clean home, but the package is at its 100-file cap, so it is not allowed.
2. **Fold the gate into `skills/workflow-release/scripts/review.py`** (6.4 KB, ~12 KB of room under 19,000), with one small
   hook in `merge.py` (freeze) and one in `release.py` (no major bump from a goal). Chosen: the gate is a review of the
   release state, review.py already runs in the operation role, and release-channels edits release.py and merge.py, so
   keeping 95% of the change in review.py keeps the later rebase small.
   Cost: review.py's docstring and SKILL.md describe two things; risk: size, held by tests of the byte counts.

## Chosen design
- `review.py gate vX [--ref REF] [--no-suite]`: runs five checks against REF (default: the newest `vX.0.0-rc.N` tag, else
  `staging`, else the base) and prints `GATE PASS vX` or one `GATE REFUSED vX (<check>): <subject>` line per failure
  (checks `issues`, `suite`, `health`, `reviews`, `docs`). The subjects (issue number, row id, requirement id, page) are
  recorded in `<git common dir>/loop/gate/vX.json`, which the freeze reads.
  - issues: open issues on milestone `vX.0` (gh); an issue passes only with a `moved` waiver.
  - suite: `regression.py run nightly` in a throwaway worktree of REF; every FAIL/NOTRUN/ENV row refuses; every KNOWN
    (known-red) row refuses unless a `red` waiver names an issue.
  - health: `health.py check` in that worktree; non-zero exit refuses.
  - reviews: every `- ID: **Unreviewed**` requirement on a page in docs.tsv refuses (the milestone's features are every
    feature page; Home, Roadmap and Tests hold no requirements).
  - docs: `release.docs_trouble(top, base, whole=True)` lines refuse.
- Waivers: `.loop/release-waivers.tsv`, `kind<TAB>subject<TAB>issue<TAB>owner record`. A waiver counts only when its
  owner-words record exists (written by the operation session) and its issue is given. That is how "the owner moved it
  by name" and "the owner waived it with an issue" are made checkable.
- `review.py promote vX --owner-record ID [--ref REF]`: operation role only; the record's ids must name `vX.0.0`. Runs the
  gate; on a refusal it writes nothing. On a pass it tags `vX.0.0`, creates `release/vX` at the same commit, fast-forwards
  main to it, moves `moved`-waived issues to the next milestone, writes the state report (requirements and review state,
  suite result, health, closed issues, changes since the last major), publishes it as the GitHub release notes and emails
  it through workflow-health's `mail.deliver`. No mail secret on the machine prints `EMAIL not sent: <why>` and the
  report path; it never fails the promotion after the tag exists.
- Freeze: a major is frozen from its first `vX.0.0-rc.N` tag until `vX.0.0` exists. `review.frozen()` is called by
  merge.py before a merge into staging: a goal that names no recorded gate subject in its goal file is refused
  `frozen for vX`; with no gate record yet everything is refused. Inactive when there is no rc tag.
- Version policy: `release.py` refuses a major bump (cut `--bump major`, or the goal's recorded bump) with
  "major ships only through review.py promote".
- `review.py revert vX`: branch `revert/vX-<stamp>` holds one commit whose tree is `release/vX`'s, parent `origin/main`; a
  PR to main is opened. Nothing is pushed to main.
- Docs: new `Release` wiki page (REL-1..REL-8, Unreviewed), How-to-use-Release, Home row, docs.tsv row, milestone link,
  one regression row per requirement, tests in `dev/toy/test-release-gate.py` (in-process, gh and git stubbed or toy repo).

## What each done line needs
1. issues check + waiver reader. 2. suite/health/reviews/docs checks, waiver for rows. 3. promote + report + email stub.
4. frozen() + merge.py hook. 5. revert. 6. release.py major refusal. 7. page, rows, sizes (a byte-count test).

## Open questions (recommendation taken, o118)
- Which pages are "the milestone's features": every page in docs.tsv that holds requirements (stricter, simplest).
- Mail secrets live in Actions only, so promote from a PC prints EMAIL not sent unless the secrets are in the environment.
- release-channels' promote of minors and patches is untouched; its promote should call `review.gate_refusals()` for a major.
