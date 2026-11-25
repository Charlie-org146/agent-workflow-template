# Plan: v110-pkg-secret-print

Design: the idea step's design (recorded done, condensed, in session), under the owner's o1082 (urgent security repair) and the freeze record o1003, with the operation's required scope TD1844 and its rulings TD1845. The done lines are frozen and kept as they are (TD1844).

## URGENT, outside this plan

Rotation or log removal for anything the 90-day search finds is the owner's decision (done line 3). The search only lists; it never deletes a log, edits an issue or rotates a key.

## Size

Files: dev/package.py, dev/toy/test-package-no-echo.py, .loop/regression.tsv
Lines: 220
Gates: none changed. The safety check refuses the same files, for the same matches, with the same exit status and failure count; only the text of its failure lines changes.
Classes: private: the change decides what a failure line may say about a private-name match (the pattern, the matched text and a matching file name are never printed); what is matched, and the private list itself, are unchanged

Three files: one hand-edited script, the one new toy (approved by the operation, TD1845) and new regression rows. `dev/` is not part of the shipped package (the package is `skills`, `listing.json`, `README.md` and `LICENSE`), so done line 4's 20,480-byte limit reads against the shipped scripts, and this goal edits none of them. Tool-regenerated records (run records, `.loop/regression-runs.tsv`) are not hand edits and are not in Files. No change to the scheduled workflow, its generator or the lane script (TD1845): the fix is at the source, so every path that replays the checker's output is clean.

Overlap: no other open goal hand-edits `dev/package.py` (operation, 08:16). Cover and one more goal add rows to `.loop/regression.tsv`, which counts as an overlap only against G1 (TD1752); at this goal's main merge the new rows may need re-placing next to theirs, which the merge does by keeping every line from both sides and re-running the rows.

## Implementation plan

Done lines (frozen): (1) a shipped file with a credential-shaped string or a private-prefix match makes the safety check (full or --static) refuse naming the file, the line number and the kind of match, printing no part of the matched text, shown by a toy seen red on today's code; (2) that check failing inside the pull-request workflow leaves no part of the matched text in its log; (3) the pull-request workflow runs of the last 90 days are searched and the goal's record lists each run that printed a match by run id and kind only; (4) every script under 20,480 bytes, no test loosened, no row red, committed text never names the service repo.

### 1. The failure line (done line 1, required item a)

In `dev/package.py`'s safety check, every Safety failure line becomes:

`FAIL Safety: <kind> in <where>, line <n>`

- `<kind>` is the built-in group's name (secret; obfuscation or encoded text; instruction aimed at the agent; dangerous command) or `private prefix #<k>`, where k is the entry's position in the private list. The pattern is never printed.
- `<where>` is the shipped path, unless the path itself matches any private prefix. Then `<where>` is `a file whose name matches private prefix #<k> (path hash <8 hex>)`: the first 8 hex digits of the SHA-256 of the path, so the operator can find it locally (`git ls-files` piped through the same hash) without the name being printed.
- `<n>` is the 1-based line of the match's start, counted from the decoded text.
- A file-name match on its own prints `FAIL Safety: private prefix #<k> in a file name (path hash <8 hex>)`.
- No slice, repr or length of the matched text is printed anywhere, and nothing else in the safety check echoes file content.

One small helper builds the line from (kind, rel, text, match). The three existing format strings call it. The failure list keeps one entry per failure as today, so the count and the exit status are unchanged.

Bytes: dev/package.py: now 22,593, after about 22,800, left about -2,320 to 20,480; note: `dev/` is not shipped, so no package limit applies; the file is already over 20,480 on main; the change replaces three format expressions and adds the helper (about 200 B net); the build measures the real size and states it in the build record

### 2. The toy (done lines 1 and 2, required items a and b)

`dev/toy/test-package-no-echo.py` (new file, approved TD1845, about 6,500 B):

- Builds a temporary tree under `mktemp` from the shipped files of the checkout (like the existing static-check toy) and adds one shipped text file holding one sample for each built-in group and one for a made-up private prefix, each on a known line, plus one file whose name matches the made-up prefix.
- Every sample is built at run time from split parts, so no committed text holds a credential-shaped string. The private prefix is a made-up toy word written to a temporary flow file passed through `LOOP_FLOW`, with a temporary `HOME`, so no real private name is read or written.
- Runs the real `dev/package.py --root <tree>` twice, with `--static` and without (full).
- For each run, it checks the exit status is a refusal and that there is one Safety line per sample, naming the right kind, path (or path hash) and line number.
- It checks that the combined stdout and stderr holds no window of 6 or more characters of any sample (case-insensitive for the private one), not the private pattern, and not the matching file's name.
- (b) It feeds the same captured output through the regression skill's own last-lines helper (`runs.shown`, the helper the scheduled run's FAIL note, job summary and issue body are built from) and checks the result the same way.
- It ends with `ALL PASS` or names each failing check, and removes only its own `mktemp` folder.

Seen red: before the fix, the build runs the toy against today's `dev/package.py` (from origin/main) and records its failing lines by check name only (the toy never prints a sample). The record says how many checks failed and which ones. After the fix it passes in both modes.

### 3. Rows (done lines 1, 2 and 4)

Added through `regression.py add` and marked red with `regression.py red` on the pre-fix code, each `land` level:

- `pkg-no-echo-static`: the toy's `--static` half (done line 1).
- `pkg-no-echo-full`: the full half (done line 1).
- `pkg-no-echo-names`: no private pattern and no matching file name (item a).
- `pkg-no-echo-tail`: the tailed output used by the scheduled path holds none of the samples (done line 2, item b).

No existing row's command or assertion changes. Before the review the build runs, singly and from the clean environment, the package rows and the cheap rows the worker rules name (pods-size, package-*, adopt-set-*, listing-names-every-command, release-static-rules, home-guard-catches-leak, setup-fit, docs-import-rows-pass, sync-check-preview). It records each result line, so that no row turns red (done line 4).

### 4. The 90-day search (done line 3, required item c)

A build-time command, not a new script, run once by the worker on the Mac. Its output never leaves the machine except as described below:

- Lists the pull-request workflow's runs and the scheduled regression workflow's runs created in the last 90 days, by 7-day windows, because the list call stops at 1,000 rows. It also reports each window's count.
- For each run, fetches its log straight into an in-memory counter that keeps only the run id and the kind from lines of the checker's Safety form. For an old-format private line it keeps only `private prefix`. It never writes a raw log line to disk, never prints one, and keeps no matched text.
- Reads the regression issues (open and closed, every label the scheduled run files) and the main-red issues the same way, keeping the issue number and the kind only.
- Names each window or run whose log could not be read (past retention, or refused) as unreadable, with a count.
- Writes the list (run id or issue number, kind) and the unreadable windows to the goal's local, untracked record under `.git/loop/`. The operation gives that list to the owner for the rotation decision. The PR body carries only the counts (runs searched, runs with a match by kind, issues with a match by kind, unreadable windows), never a run id or issue number that points at a log holding a match.

### 5. The two named files (required item d)

The build inspects `.loop/goals/hotfix-4892.md` and `dev/toy/test-setup-fit.sh` with the checker's own patterns, and with the private list where it is present (the Mac's flow file). It records each hit by kind and line only in the goal's local record, and gives counts by kind in the PR body. It edits neither file: any follow-up goes to the operation.

### 6. Going beyond the done lines

The PR body names items a, b, c and d as going beyond the frozen done lines (TD1844), each with its check: a and b by the toy's checks and the two rows; c by the search's counts; d by the inspection's counts.

## Checks the build runs

- The toy seen red on today's code, then green, in both modes.
- The four new rows red before the fix, green after.
- The single-row set from the worker rules, from the clean environment, before review.
- `python3 dev/package.py --static` on the branch, its output read only for its last line (it passes on the real tree).
- A grep of the diff for the service repo's name and for any credential-shaped literal (none).

## Review record

(filled by the plan step)
