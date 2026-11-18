# release-gate plan

Claims checked against the code: `review.py` (6,400 B, imports `release`, has `worker()`, `held()`, `wait()`, `record()`,
`proven()`, `criteria()`), `release.py` (`bump()` is the only version bump point: autorelease.py:189 and cmd_cut:319 call
it; `docs_trouble(top, base, whole=True)`, `doc_rows`, `run`, `git`, `load`), `merge.py` (calls `review.held` before
`gh pr merge`, line ~299), `regression.py run nightly` prints `FAIL|KNOWN|NOTRUN|ENV <id>`, `health.py check` exits 1
when red, `mail.py deliver/settings/secrets`, owner records in `<common>/loop/owner-words.tsv` (id, time, source, text, ids).

## Build steps
1. `review.py`: waiver reader (`.loop/release-waivers.tsv`, record must exist); `issues_check`, `suite_check`,
   `health_check`, `reviews_check`, `docs_check`; `gate_refusals(top, cfg, ver, ref, suite)` returning `[(check, subject)]`
   and recording the subjects in `<common>/loop/gate/vX.json`; CLI `gate`.
2. `review.py`: `frozen(top, cfg, base, slug)` (rc tag without the release tag; a goal passes only if it names a recorded
   subject); `release.bump` refuses major; one hook line in merge.py before the merge.
3. `review.py`: `promote` (operation role, owner record naming the tag, gate, tag, `release/vX`, ff main, move waived
   issues, state report, `gh release create --notes-file`, email through mail.deliver) and `revert`.
4. SKILL.md and commands.md of workflow-release: Command map rows, one short section.
5. Wiki: `Release.md` (REL-1..8, Unreviewed), How-to-use-Release, docs.tsv row, Home row (`docs.py prd`), regression rows
   (one per requirement) via `regression.py add`, seen red via `red --break`, Tests tables re-rendered from committed data.
6. `dev/toy/test-release-gate.py`: legs `issues`, `rows`, `promote`, `freeze`, `revert`, `major`, `sizes`; each with a
   negative leg (the thing the gate must not do).

## Test for each done line
1 -> `issues`; 2 -> `rows`; 3 -> `promote` (tag, branch, report, mail stub; and no tag on a refusal); 4 -> `freeze`;
5 -> `revert`; 6 -> `major`; 7 -> `sizes` + `docs.py check`. Each row is seen red by breaking the function it covers.

## What could break
Script sizes (review.py has ~12 KB, release.py 727 B, merge.py 434 B: the hooks are one or two lines); the later rebase on
release-channels (kept to review.py plus two one-line hooks); real suite time (gate runs the full suite: minutes).

## Out of scope
Staging, rc tagging and promotion of minors and patches (release-channels #4778); auto-planning of version ranges (a
separate goal); waiver creation commands (the owner's record plus a TSV line, written by the operation session).

PENDING: none (recommendations taken under o118).
