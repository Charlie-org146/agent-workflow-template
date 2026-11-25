<!-- /autoplan restore point: kept locally (untracked) -->
# Plan: v110-pkg-secret-print

Design: the idea step's design (recorded done, condensed, in session), under the owner's o1082 (urgent security repair) and the freeze record o1003, with the operation's required scope TD1844 and its rulings TD1845. The done lines are frozen and kept as they are (TD1844).

## URGENT, outside this plan

Rotation or log removal for anything the 90-day search finds is the owner's decision (done line 3). The search only lists; it never deletes a log, edits an issue or rotates a key.

## Size

Files: dev/package.py, dev/toy/test-package-no-echo.py, dev/toy/test-setup-fit.sh, dev/test-package.sh, .loop/regression.tsv
Lines: 420
Gates: none changed. The safety check refuses the same files, for the same matches, with the same exit status and failure count; only the text of its failure lines changes.
Classes: private: the change decides what a failure line may say about a private-name match (the pattern, the matched text and a matching file name are never printed); what is matched, and the private list itself, are unchanged

Five files: three hand-edited scripts (`dev/package.py`; `dev/toy/test-setup-fit.sh`, approved TD1847; `dev/test-package.sh`, joined by TD1849), the one new toy (approved TD1845) and new regression rows. `dev/` is not part of the shipped package (the package is `skills`, `listing.json`, `README.md` and `LICENSE`), so done line 4's 20,480-byte limit reads against the shipped scripts, following the precedent rows dlf-done-3-sizes and make-room-b-5-sizes, and this goal edits none of them. Tool-regenerated records (run records, `.loop/regression-runs.tsv`) are not hand edits and are not in Files. No change to the scheduled workflow, its generator or the lane script (TD1845): the fix is at the source, so every path that replays the checker's output is clean.

Overlap: no other open goal hand-edits `dev/package.py` (operation, 08:16). Cover and one more goal add rows to `.loop/regression.tsv`, which counts as an overlap only against G1 (TD1752); at this goal's main merge the new rows may need re-placing next to theirs, which the merge does by keeping every line from both sides and re-running the rows.

Reading order for the build: the implementation sections below, then the accepted blocks in phase order (CEO, DX, Eng). A later item supersedes an earlier one where they differ: W1 over section 1's withheld wording, Y1 over S6's and section 1's `#k`, Y2 over V5 and W2, Y4 over the original check order, and Y8 over W3's and S12's paths.

## Implementation plan

Done lines (frozen): (1) a shipped file with a credential-shaped string or a private-prefix match makes the safety check (full or --static) refuse naming the file, the line number and the kind of match, printing no part of the matched text, shown by a toy seen red on today's code; (2) that check failing inside the pull-request workflow leaves no part of the matched text in its log; (3) the pull-request workflow runs of the last 90 days are searched and the goal's record lists each run that printed a match by run id and kind only; (4) every script under 20,480 bytes, no test loosened, no row red, committed text never names the service repo.

### 1. What the checker prints (done line 1, required item a)

Operation rulings: TD1844 (items a-d required), TD1845 (source-only fix, the one new toy, the search as a command), TD1847 08:30 (`dev/toy/test-setup-fit.sh` approved as a hand-edited file; no locator for name matches; withheld tails), TD1849 08:37 (`dev/test-package.sh` joins the repair).

In `dev/package.py`:

- Safety lines read `FAIL Safety: <kind> in <where>, line <n>`.
  - `<kind>` is the built-in group's name (secret; obfuscation or encoded text; instruction aimed at the agent; dangerous command) or `private prefix #<k>`. k is the 1-based position in the list `private_prefixes()` returns. The pattern is never printed.
  - `<where>` comes from a helper `where(rel, private)`. It returns the path, unless the path itself matches a private prefix or any built-in pattern. Then it returns `a path matching private prefix #<k>` (lowest matching k) or `a path matching <kind>`, with no path, hash or other locator, because a hash of a tracked path can be reversed over the tracked paths.
  - `<n>` is `text.count("\n", 0, match.start()) + 1`.
- A path that matches private prefixes prints one line, `FAIL Safety: private prefix #<k> in a path`, naming the lowest k. Today it prints one line per matching prefix, so the `REFUSED` count drops for a path matching several prefixes; every other count is unchanged.
- Item a, as TD1844 words it ("no private pattern or matching file name printed"), governs over done line 1's "naming the file" where a path matches. The build record and the PR body name TD1844 (a) as the authority.
- Every other rule's failure text goes through `fail(rule, text, source=None)`. Before printing, `fail()` runs the built-in lists and the private list over `text`, and over `source`, the uncut text the line was cut from. On any hit it prints `FAIL <rule>: (withheld: the line held a Safety match; run the check locally to see it)`. The callers pass `source`:
  - the Scripts rule passes the whole stderr (its line keeps only the last 200 characters);
  - the Version rule passes the whole VERSION text (its line keeps only 20);
  - the Disclosure rule passes the whole file text, so any host or command line from a file holding a Safety match is withheld.
  - Lines with no hit are byte-identical to today, so rows that grep them (for example the hang toy's Scripts and TIMEOUT lines) keep passing.
- The TIMEOUT and STOPPED lines print the `waiting on` label straight from the signal handler, not through `fail()`. So `wait_on()` cleans the label when it is set: a label holding a hit becomes `a shipped script (name withheld) --help`.
- No slice, repr or length of matched text is printed anywhere.

Bytes: dev/package.py: now 22,593, after about 23,600, left about -3,120 to 20,480. Note: `dev/` is not shipped, and done line 4 is read as the shipped package's scripts, following the precedent rows dlf-done-3-sizes and make-room-b-5-sizes, which measure `skills/` only. The file is already over 20,480 on main. The build measures the real size.

### 2. The toy (done lines 1 and 2, required items a and b)

`dev/toy/test-package-no-echo.py`, the one new file (TD1845), about 8,000 B. One mode argument per run:

| Mode | Checker run | Cases | Row |
|---|---|---|---|
| `static` | `--static` | one sample per built-in group and one private sample, each in its own shipped file; a private sample as a URL host (Disclosure) | pkg-no-echo-static (done line 1) |
| `pr-log` | the exact command of the pull-request workflow's checker step, read from `.github/workflows/regression-pr.yml` at run time, on the sample tree | the `static` cases | pkg-no-echo-pr-log (done line 2) |
| `full` | full (`--help` pass and ZIP) | the `static` cases; a shipped script whose `--help` fails with a source line holding a sample (Scripts tail); a private-named script that hangs, run with a short `--timeout` (TIMEOUT label) | pkg-no-echo-full (done line 1) |
| `names` | `--static` | a private-named path, a private-named folder, a path holding a built-in match, and a Safety match inside a private-named file | pkg-no-echo-names (item a) |
| `tail` | `--static` | the `static` output put through `runs.shown`, the helper the scheduled run's FAIL note, job summary and issue body are built from (part of output the `static` check already covers) | pkg-no-echo-tail (item b) |

- **Tree.** A minimal temporary tree under `mktemp`: README.md, LICENSE, listing.json, VERSION and one skill folder with a SKILL.md, plus the case files inside that skill. It is made a git repo with every file added, like `test-package-static.py`, so the tracked-file path is exercised. `--out` always points inside the `mktemp` folder. Full mode on this tree takes seconds, so every mode fits a pull-request land row; the build records each mode's measured time.
- **Samples.** A sample is the matched text. Each match is at least 12 characters and is built at run time from split parts, so no committed text holds a credential-shaped string. File and folder names share no 6-character window with any sample. The private prefix is a made-up toy word, written to a temporary flow file passed through `LOOP_FLOW`, with a temporary `HOME`. The baseline run uses the same `LOOP_FLOW` and `HOME`.
- **Expected lines.** The toy imports `dev/package.py` by spec and, in-process, runs each pattern list and the toy private list over each case file. That gives every (kind, line) pair the checker reports: each matching pattern, first match per file, no dedupe. The toy formats the expected lines itself with its own format strings, never the checker's helper.
- **Checks, per mode.**
  - The exit status is a refusal, and every expected Safety line is present.
  - After the expected Safety lines and the final REFUSED line are removed, no Safety line remains.
  - No remaining text, nor the withheld notices' surroundings, holds a 6-character window of any sample, the private pattern, a private-named path or its basename (case-insensitive for the private ones). As a second filter, a window counts only if it is absent from the same mode's run on the tree without the case files.
- **Ending.** The toy ends with `ALL PASS` or names each failing check by name only (it never prints a sample), and removes only its own `mktemp` folder.

Seen red: the build runs every mode against today's `dev/package.py` (origin/main) first and records the failing check names and counts. After the fix every mode passes.

### 3. Rows and the two edited toys (done lines 1, 2 and 4)

Rows are added through `regression.py add --goal ... --describe ...`:
- pkg-no-echo-static: land, criterion, goal v110-pkg-secret-print:1.
- pkg-no-echo-full: land, criterion, :1.
- pkg-no-echo-names: land, criterion, :1.
- pkg-no-echo-pr-log: land, criterion, :2.
- pkg-no-echo-tail: land, criterion, :2.
- pkg-secret-print-4-sizes: land, criterion, :4, `! find skills -name '*.py' -size +20479c | grep -q .` (strictly under 20,480, which is the limit the checker itself enforces).
- done-pkg-secret-print-3: covered, workflow, :3, "proved by the search recorded in the goal's run record".

Each toy row's red proof is `regression.py red <id> --break "git checkout <base> -- dev/package.py"`, run after the toy and the fix are committed (base = the branch's merge base with main).

- `dev/toy/test-setup-fit.sh` (TD1847). Its assertion of the old private-prefix line (nightly row setup-fit) changes to the new form. The toy's flow list has two entries and the appended text matches the second, so it expects `private prefix #2 in <path>, line <n>`, with path and line worked out at run time from the toy's own data. It adds a check, ignoring case, that neither the toy's prefix pattern nor the appended text appears in the output, so the assertion gets stricter, never looser. The PR body shows the old and new assertion lines in the toy's own words only (never a real pattern), and the new check seen red on f7f86150d. If the deliver-first safety check flags it as a loosened test, it goes to the operation with the diff.
- `dev/test-package.sh` (TD1849). Its committed credential-shaped sample is built at run time from parts, so no committed line matches a token shape. Its assertion (the secret refusal) stays unchanged, and the build shows the script passing before and after. No history rewrite (TD1763). Everything is reported by file and kind only. Whether it was a real token, and secret scanning, are the owner's.

Every other existing row's command and assertion is unchanged. Before the review, the build runs singly from the clean environment the package rows, setup-fit, and the worker rules' cheap rows (pods-size, package-*, adopt-set-*, listing-names-every-command, release-static-rules, home-guard-catches-leak, docs-import-rows-pass, sync-check-preview). It records each result line (done line 4).

### 4. The 90-day search (done line 3, required item c)

A build-time command, not a new script, run once by the worker on the Mac. Its sources are what TD1844 item (c) requires, "pages by date, covers PR runs, scheduled runs and the regression issue bodies, reports by run id or issue number and kind only, and names unreadable days". Two expansions are accepted: the main-red issues the operation named on 08:14, and issue edit histories (P1).

- **Runs.** Listed through the API by created-date window; a window returning 1,000 runs is split until each returns fewer. It keeps runs of every workflow that ran the checker in the 90 days, by path: the pull-request workflow, the scheduled regression workflow, the release workflow, and any renamed or deleted file. The health workflow, deleted inside the window, is checked for checker runs. The record lists each path searched.
- **Logs.** Every attempt's log is fetched with `gh api .../runs/<id>/attempts/<n>/logs` into Python memory and unzipped there, with no log file written. On 403 or 429 it backs off as the response's retry header says. Progress (run ids, attempts and kinds only) is checkpointed to a local untracked file so the search can resume.
- **Issues.** The regression and main-red issues' bodies, comments and edit histories (GraphQL `userContentEdits`).
- **Counting.** Every checker output line (`FAIL <rule>:`, `TIMEOUT:`, `STOPPED:`) is scanned in memory with the built-in lists and the private list and classified by kind; a line that holds a hit but can't be classified counts as `unparsed`. Each line is tagged by the job step or row that printed it. The direct checker step and real-tree package rows are counted; toy-row lines (the toys' own samples) are listed separately. Job summaries have no read API. The scheduled run prints the same FAIL note to its log first, and the record says so.
- **Unreadable.** Each window or run whose log can't be read (past retention, or refused) is named, with a count.
- **Where the list goes.** "The goal's record" is read as the goal's run record (`.git/loop/runs/v110-pkg-secret-print.json`, through the build record). The operation and the owner can read it. It is not committed text, because a public run id or issue number points straight at a log or issue holding a match. The PR body carries counts only. If the operation rejects this reading at the gate, the build stops at this step and asks where the list goes; it never commits run ids on its own.

### 5. The two named files (required item d)

The build inspects `.loop/goals/hotfix-4892.md` and `dev/toy/test-setup-fit.sh`, on the base version before any edit, with the checker's own lists and with the private list where it is present (the Mac's flow file). It records each hit by kind and line only in the goal's run record, and gives counts by kind in the PR body. The hotfix goal file is not edited; `dev/toy/test-setup-fit.sh` changes only as section 3 says. Any other follow-up goes to the operation.

### 6. Going beyond the done lines

The PR body names what goes beyond the frozen done lines, each with its check:
- item a: `names` mode;
- item b: `tail` mode;
- item c: the search's counts;
- item d: the inspection's counts;
- the other-rule withholding and the TIMEOUT label: `full` and `static` cases;
- the edits to the two existing scripts (TD1847, TD1849).

## Checks the build runs

- Every toy mode seen red on today's code, then green.
- The seven new rows: the five toy rows red before the fix (`regression.py red --break`) and green after; the size row green; the covered row pointing at the run record.
- setup-fit's new check seen red on f7f86150d, then green; `dev/test-package.sh` passing before and after.
- The single-row set from the worker rules, from the clean environment, before review.
- `python3 dev/package.py --static` on the branch, its output read only for its last line (it passes on the real tree).
- A grep of the diff for the service repo's name and for any credential-shaped literal (none).


<!-- autoplan-accepted:ceo -->
- X1: a private-matching path prints one line naming the lowest k, `FAIL Safety: private prefix #<k> in a path`, with no locator; Safety lines name files through `where()`, which also hides a path holding a built-in match; verified by `names` mode (row pkg-no-echo-names).
- X2/S5: the toy removes the expected Safety lines (computed in-process per case file, formatted by the toy itself) and the REFUSED line, requires no other Safety line, and finds no 6-character window of any sample, private pattern or private-named path in the rest, with a same-mode clean baseline (same LOOP_FLOW and HOME) as a second filter; verified by every mode red on today's code and green after the fix.
- C1: `fail(rule, text, source=None)` withholds any non-Safety failure line whose text or uncut source holds a built-in or private match (Scripts passes whole stderr, Version the whole VERSION text, Disclosure the whole file text); `wait_on()` cleans the TIMEOUT/STOPPED label; lines with no hit are byte-identical; verified by `static` (URL host), `full` (failing --help traceback, hanging private-named script) and the unchanged hang toy.
- S1 (TD1847): dev/toy/test-setup-fit.sh expects `private prefix #2 in <path>, line <n>` (path and line worked out at run time) and checks, ignoring case, that neither its prefix pattern nor its appended text appears; seen red on f7f86150d, green after; the PR body shows old and new assertion lines in the toy's own words only.
- S2: TD1844 (a), "no private pattern or matching file name printed", governs over done line 1's "naming the file" for matching paths; named as the authority in the build record and PR body.
- S9: seven rows (five toy rows land, pkg-secret-print-4-sizes with `-size +20479c`, done-pkg-secret-print-3 covered/workflow), each with its goal field; red proofs by `regression.py red --break "git checkout <base> -- dev/package.py"` after the toy and fix are committed.
- S11: the 90-day search by split date windows over every workflow path that ran the checker (pull-request, scheduled regression, release, renamed/deleted, health checked), every attempt's log in memory with backoff and a resumable ids-and-kinds checkpoint, issues' bodies, comments and edit histories, every checker output line scanned and tagged by step or row with toy-row lines listed apart, unreadable windows named.
- S12: the run-id list lives in the goal's run record, not committed text, with counts only in the PR body; if the operation rejects this reading at the gate, the build stops at that step and asks.
- S14 (TD1849): dev/test-package.sh builds its credential-shaped sample at run time from parts, keeps its secret-refusal assertion unchanged, passes before and after, no history rewrite, reported by file and kind only.
- D4: done line 4 is read as the shipped package's scripts, following precedent rows dlf-done-3-sizes and make-room-b-5-sizes; dev/package.py (after about 23,600 B) is not shipped.
- V1 (native F1 + Codex 1, both High): the PR body ends with owner actions, as counts only: runs and issue edits still readable that hold a match (log deletion and edit redaction are the owner's); runs in which a private pattern itself was printed (replacing the private list is the owner's); the credential-shaped sample in dev/test-package.sh and whether a provider's scanning may already have flagged it (validity and rotation are the owner's, time-sensitive). The gate summary carries the same lines to the operation. Nothing is deleted, edited or rotated by the build.
- V2 (native F9 + Codex 2): the environment contract is stated in the build record: in CI the private list is absent by design (a private list in public CI would itself leak), so CI runs can hold only built-in matches; private-kind protection and private-kind historical hits are local only (live lanes, local rows). The search reports private-kind counts with that note. No fail-closed private check in CI.
- V3 (native F7, F8 + Codex 4): the search starts with a count pass (runs and attempts per window and workflow, no log fetch), records the estimate and an ETA, and sends it to the operation before fetching; over budget goes to the operation. The run record keeps the exact command text, the detector version (the commit of dev/package.py whose lists were used), the coverage limits, and three separate counts: confirmed hits, unreadable (unknown, never clean), and not assessed. Windows past log retention are expected to be unreadable.
- V4 (native F4): the toy's private prefix word is at least 12 characters; any forbidden string shorter than 6 characters is checked whole, not by windows.
- V5 (native F5): `main()` gets a top-level handler: an uncaught exception's message goes through the same scan, and is printed as the withheld notice on a hit; a `full`-mode toy case forces an exception carrying a private-named path.
- V6 (native F6): the PR body states dev/package.py's size before and after, and the done-line-4 reading with its precedent rows.
- V7 (native F10, F11): when `where()` hides a path, the Safety line keeps its line number, because a line number in a file whose path is hidden narrows nothing a reader can open; whole failure lines are withheld instead of masking part of them, because partial masking leaks through length and surrounding text. Both reasons are written into the code comment above the helpers.
- V8 (native F3): the operation confirms at the gate that TD1844 (a) governs over done line 1's "naming the file" for matching paths, and that confirmation goes into the run record.
- V9 (Codex 5, partly): the no-window check runs over the entire captured output of each run, including any withheld notice; the `pr-log` mode runs the pull-request workflow's exact checker command. A synthetic run of the workflow itself on GitHub needs a push, so it is not part of the build.
<!-- /autoplan-accepted:ceo -->

<!-- autoplan-accepted:dx -->
- W1 (both voices): the withheld notice reads `FAIL <rule>: withheld: a line from <where> held a <kind> match. Find it locally with the lists in dev/package.py and your leak_prefixes, fix it, then rerun (see --help, Safety output)`, with `<where>` from `where()`; for a private-hidden path, `--help` states that `#k` is entry k of `leak_prefixes` in `$LOOP_FLOW` (default `~/.workflow-loop/flow.json`). No local reveal flag (taste T3); verified by `static` and `names` modes asserting the notice's form and that it holds no sample window.
- W2 (both voices): an uncaught exception prints `ERROR (unexpected): <exception type>: <message>` to stderr and exits 4; the message and the traceback are printed only when they hold no built-in or private hit, otherwise `withheld (it held a <kind> match)` replaces them; verified by the `full`-mode forced-exception case (exit 4, stderr, no sample window).
- W3 (native CAP6): the 90-day search caps retries at 5 per request and sets a total wall-clock budget recorded in its ETA; 404/410 counts as unreadable (past retention); 401 or a scope 403 stops with `gh auth refresh -s repo,actions:read` as the fix line; the checkpoint file is `.git/loop/runs/v110-pkg-secret-print.search.json` (untracked, inside the git dir), kept until the operation's word.
- W4 (native High): `pr-log` mode copies `dev/package.py` into `<tmp>/dev/`, asserts the copy exists, and runs the workflow's checker command with cwd `<tmp>`; the command is every `run:` line in `.github/workflows/regression-pr.yml` holding `dev/package.py`, which must all be identical (the toy fails by name if none or they differ).
- W5: the toy prints `usage: test-package-no-echo.py {static|pr-log|full|names|tail}` to stderr and exits 2 on a missing or unknown mode; each failure prints `FAIL <mode>/<case>: <check>` with made-up case labels that share no window with any sample, plus expected and found Safety-line counts.
- W6: the hang case runs with `PACKAGE_CHILD_SECONDS=30` and `--timeout 3`, so the run-level TIMEOUT label fires first; the toy's own run is bounded and recorded.
- W7 (both voices' redaction boundary): `note_shell()` prints its names through `where()`; `private_prefixes()`'s load-failure NOTE prints a fixed line (`NOTE: no leak_prefixes loaded (the flow file is missing or unreadable); only the built-in scans ran`) without the path; a path holding only a built-in match is not refused (unchanged) but is hidden by `where()`; verified by a `static` case with an unreadable flow file and a `names` case with a built-in-matching path.
- W8 (both voices; taste T4): `dev/package.py`'s docstring (its `--help` text) gains a "Safety output" section: the line forms, the kinds as stable codes, `#k` lookup, the withheld recovery sequence, exit codes 0/1/3/4, the CI/local contract, and an output-change note (Safety form, the collapsed count for multi-prefix paths, withheld notices, exit 4); the PR body repeats the output-change note.
- W9: FAIL lines stay on stdout (existing rows grep stdout), and the size row's `find -size` measures on-disk bytes (LF on Linux CI); both noted in the build record.
<!-- /autoplan-accepted:dx -->

<!-- autoplan-accepted:eng -->
- Y1 (native H1, M2 + Codex 3): `main()` loads the private list once, before any check, into one module global of compiled patterns; `#k` is the 1-based raw position in the flow file's `leak_prefixes` array; an entry that is not a non-empty string or does not compile is skipped with a fixed NOTE naming it by index only; every helper reads the global; the NOTE line now comes first in the output (recorded in the build record).
- Y2 (Codex 3, native Low): the top-level handler catches `Exception` (not `BaseException`), prints `ERROR (unexpected): <type>` and the message or the withheld wording through the scan, and falls back to the constant line `ERROR (unexpected): details withheld` if the scan itself raises; exit 4, stderr; verified by a `full` case forcing an exception with a private-named path and a `static` case with a malformed private entry.
- Y3 (native M1 + Codex 4): Disclosure keeps a map from each host or command to the files it came from; a failing value is withheld when any of its files holds a Safety or private match (source = those files' joined text) and names `where()` of its first file; verified by the `static` URL-host case with the same value in a clean file and a matching file.
- Y4 (Codex 2, taste T5): `check_safety` runs before `check_scripts`, so a hanging or failing script can't stop the run before Safety findings are printed; each `full` case runs on its own tree with its own expected outcome (Scripts tail: exit 1; hang: Safety lines then TIMEOUT, exit 3; exception: exit 4).
- Y5 (Codex 5, native Low): each case file names its designated kind and line in the toy's own table, and the toy fails if that (kind, line) is missing, before adding any further pairs derived from the checker's lists; plus one fixed count per built-in group as a cross-check that no list shrank unnoticed.
- Y6 (native M3, M4): no sample shares a 6-character window with the checker's fixed text (kind names, notice templates, TIMEOUT, NOTE and REFUSED lines), checked by the toy at start; each mode's seen-red record and each `regression.py red --break` must show the no-window check among the failing checks, not only the format check.
- Y7 (Codex 1, native Low): the historical counter counts every old-format Safety line by its form (`FAIL Safety: <group> in ` or `private prefix ` before ` in `) as one exposure of that kind, without re-matching the excerpt; for other checker lines and their following lines up to the next known line form, it scans with the lists and records `possible <kind>`; `userContentEdits` diffs are scanned; each window's fetch time is recorded.
- Y8 (Codex 6, native M7): the search's checkpoint and its id list live in `$(git rev-parse --git-common-dir)/loop/runs/v110-pkg-secret-print.search.json`; the run record holds only counts and that path, so no renderer reads the ids; the build confirms one board render and one check-in render hold none of them.
- Y9 (native M5, M6, M8): `pr-log` runs the workflow line under `bash -c` with `sys.executable`'s folder first on PATH, `LOOP_FLOW` unset and a temporary HOME with no flow file; the build lists, by file name, the toys that call `dev/package.py` and echo its output or their fixtures on failure (no edits); the operation confirms the done-line-4 reading (D4) at the gate with V8, and the size row's `+20479c` matches the checker's own `>=` limit.
<!-- /autoplan-accepted:eng -->
## Review record

Plan step: /autoplan, unattended, in session (worker spare-worker-a), run loop-v110-pkg-secret-print-20261125-082107, on plan commit c530e954b. Scope detection: UI no; DX yes (term count 15). Phases: CEO, DX, Eng. Gate answers come from the operation (TD1627, o960); nothing here approves.

### CEO phase: Step 0

System audit. origin/main f7f86150d. No commit since 2026-11-24 touches `dev/package.py` or the new toy (already-done: none). No TODOS.md in this repo: deferrals go to NOT in scope and to the operation. The design-doc finder returned `docs/designs/skill-size.md`, an unrelated repo design (script size), so it is not used. The ship policy file is absent, so it's the default one PR. The branch decision log is empty. Taste references: `dev/toy/test-package-static.py` (loads `dev/package.py` by spec, runs it on a temporary tree, PASS/FAIL lines) is the pattern to follow. A toy that prints what it checks for is the pattern to avoid, since this toy must never print a sample.

0A Premise challenge.

| Premise | Claim | Receipt | Verdict |
|---|---|---|---|
| P1 | Safety failures print a slice of the match | dev/package.py:331, :337 (`match.group(0)[:40]`) | verified |
| P2 | The private branches print the pattern itself, and the file-name branch prints the matching path | dev/package.py:324, :331 (`%r` of the prefix) | verified |
| P3 | Every Safety failure goes through one print | dev/package.py:147-149 `fail()` | verified |
| P4 | The pull-request workflow runs the static check in public | .github/workflows/regression-pr.yml:58, :84 | verified |
| P5 | CI has no private list, so only the built-in groups fire there | dev/package.py:308-317 (missing flow file returns []) | verified |
| P6 | The scheduled and live paths replay the row's own output | .github/workflows/regression.yml:456-461, :607-610, :617-636; skills/workflow-regression/scripts/runs.py:44 | verified |
| P7 | `dev/` is outside the shipped package | dev/package.py:33 `SHIPPED` | verified |
| P8 | The run list stops at 1,000 rows | `gh run list` measured 2026-11-25 (1000 rows reach back only to 11-18) | verified [measured: gh, 2026-11-25] |
| P9 | Log retention may cut the 90 days short | GitHub default 90 days, repo setting not read | unverified (the build reads it or names unreadable windows) |

unverified=1. Real problem: credential-shaped text or private names can reach public logs, summaries and issue bodies through the checker's own failure line. Target outcome: the checker never prints match text, and the owner learns which past runs printed any, by kind only. Do-nothing cost: every future match in a pull request publishes up to 40 characters of a secret, and past exposure stays unknown, so rotation can't be decided.

0B Existing code leverage. Single choke point (`fail()` and three format calls in `check_safety`): fix there, at the root, not in each replay path (one guard in the shared function). The toy reuses `test-package-static.py`'s load-by-spec and temporary-tree pattern, and `runs.shown` for the tailed path. Rows are added through `regression.py add` and `red`, not by hand. The search uses `gh run list --created` and `gh run view --log`. No rebuild anywhere.

REALITY: premise-table pass 9 premises, unverified=1 (P9 retention) dev/package.py:331
REALITY: already-done pass no origin/main commit since 2026-11-24 on the named files (git log origin/main at f7f86150d) dev/package.py:319
REALITY: surface-check pass --root/--static, regression.py add/red, gh run list --created/--limit, gh run view --log, runs.shown verified dev/package.py:445
REALITY: binding-decisions pass branch decision log empty; binding rulings are o1003, TD1844, TD1845 as cited in the plan .loop/goals/v110-pkg-secret-print.plan.md:3
REALITY: numbers pass 22,593 B [measured: wc]; about 200 B net [estimated]; 1,000-row cap [measured: gh]; 90 days [done line 3] dev/package.py:1
REALITY: deferred-asks pass no linked issue; TD1844 items a-d are all in the plan .loop/goals/v110-pkg-secret-print.plan.md:3
REALITY: pr-count pass no ship policy file, default one PR, one PR planned .loop/goals/v110-pkg-secret-print.plan.md:1

0C Dream state.
```
  CURRENT STATE                    THIS PLAN                          12-MONTH IDEAL
  checker prints 40 chars of a     failure lines name kind, place,    no check anywhere in the loop
  match, the private pattern and   line only; toy + 4 rows hold it;   echoes matched text; one shared
  matching names into public       past exposure listed by run id     "never echo" rule every checker
  logs; past exposure unknown      and kind for the owner             and lane replay passes through
```
This plan moves toward the ideal for the one checker that runs in public CI. The shared rule across every checker is outside this goal (TD1845).

0D. No approach choice is needed: the source fix is settled by TD1845. The alternatives (a redactor in each replay path; a redactor in the workflow generator) were declined there, since they fix symptoms in three places and leave local output dirty.

0E Mode: SELECTIVE EXPANSION (autoplan override). Planned changes: 3 files (1 edit, 1 new, 1 rows) [measured from the Files line]. Approved decisions: o1003 (freeze), TD1844 (a-d required), TD1845 (source-only, new toy, search as a command).

0F/0G Selective expansion. HOLD checks first: 3 files and no new service, so the complexity check passes. Minimum change = the three format calls + the helper + the toy + rows; all of it is required by done lines 1, 2 and 4 and items a and b; nothing is deferrable without failing a done line. Cherry-pick candidates (auto-decided by the six principles; none expands Files):
- X1 No locator at all for a file-name match. The plan's 8-hex path hash can be reversed by hashing every tracked path (a few hundred), so it would still tie a file to "private prefix #k". Effort S, risk low. In blast radius, removes a residual leak: ACCEPTED (P1, P2). A file-name match prints only `private prefix #<k> in a file name`. The operator finds it locally with the private list. A content match inside such a file prints `in a file whose name matches private prefix #<k>, line <n>`. Item a is stricter than done line 1's "naming the file", and TD1844 makes it required, so it governs there.
- X2 Toy compares against a clean baseline run: a 6-character window of a sample counts only if it is absent from the same run on the tree without samples, so kind labels and paths can't cause false reds. Effort S: ACCEPTED (P1).
- X3 Redact the `Scripts` rule's stderr tail (dev/package.py:304), a different leak class (a script's own --help output, not matched text). Effort S, same file. First deferred as taste; re-decided ACCEPTED after spec review 1 showed done line 1's full mode covers it (see the accepted block).
- X4 A generic redactor in the scheduled workflow generator: declined by TD1845, NOT in scope.
- X5 Deleting or editing old logs and issues: the owner's rotation decision (URGENT section), NOT in scope.
- Delight scan (none taken; all outside the goal): a `--locate` local flag that prints the hidden path for the operator; a count of past matches on the board; a shared `noecho` helper for other checkers; a row asserting the workflow file still runs `--static`; a summary line "N Safety failures, kinds: …".

10x check: the 10x version is a loop-wide "no echo" contract every checker and every replay path obeys, with one toy per checker. This plan builds the first instance of that contract at its highest-exposure point.

0I Temporal interrogation.
```
  HOUR 1 (foundations):  where every Safety print is (3 calls + fail()); the private list
                         comes from LOOP_FLOW; the toy runs with a temporary HOME
  HOUR 2-3 (core logic): line number from match.start(); a file-name match also suppresses
                         the path in later content lines of the same file
  HOUR 4-5 (integration): runs.shown imports actions/completion/lanes: the toy puts the
                         scripts folder on sys.path; full mode runs every script's --help
                         (slow, about 1-2 min) and needs no network
  HOUR 6+ (polish/tests): seen red against origin/main's package.py; regression.py red
                         on the four rows; the 90-day search's window loop and its
                         unreadable list
```
Effort: human ~1 day / CC ~2 h for code, toy and rows; the 90-day search ~1 h, mostly waiting on log downloads. Feasibility blockers: none.

### CEO phase: dual voices

Native CEO voice (Claude subagent, input ceo d2c0d8ce): approve with changes; High F1 (published exposure stays live), F7 (search budget); Medium F2 (standard tools not named), F3 (done-line override needs confirmation), F4 (short prefixes), F5 (uncaught exceptions), F6 (size reading visible), F8 (search command not kept), F9 (no private list in CI), F10 (line number exposure), F12 (provider may have flagged the token); Low F11.
Codex CEO voice (codex, completed): FINDINGS; High 1 (exposure remediation ownership), 2 (private-list configuration per environment), 3 (structured allowlisted diagnostics instead of pattern-recognition), 4 (search coverage limits); Medium 5 (validation shares assumptions), 6 (versioned audit command).

```
CEO DUAL VOICES — CONSENSUS TABLE:
  Dimension                            Claude  Codex  Consensus
  1. Premises valid?                   mostly  no     DISAGREE (Codex: CI private config unproven) -> V2
  2. Right problem to solve?           yes     yes*   CONFIRMED (*plus remediation ownership, V1)
  3. Scope calibration correct?        yes     no     DISAGREE (Codex: split fix from search) -> TASTE T1
  4. Alternatives sufficiently explored? no    no     CONFIRMED gap (standard tools; allowlisted output) -> TASTE T2
  5. Competitive/market risks covered? no      no     CONFIRMED gap (published exposure, provider scanning) -> V1
  6. 6-month trajectory sound?         partly  no     CONFIRMED gap (search not repeatable) -> V3
```

Decisions: V1-V9 accepted (accepted block). TASTE T1: Codex recommends shipping the output fix independently of the search. Splitting the goal would change the frozen done lines (a new goal), and only Codex recommends it, so it is not a user challenge. Auto-decided: one goal, with the build ordered so the fix, toy and rows are committed first and the search runs after (P6). The operation may split. TASTE T2: allowlisted structured diagnostics (Codex 3), and standard tools such as log masking, secret scanning and scanners (native F2), are the 12-month direction. They are outside TD1845's source-only ruling, so they go to the operation as a follow-up. Declined: Codex 6's versioned audit script, because TD1845 rules the search a command, not a script; V3 keeps the command text and provenance in the run record instead.

### CEO phase: review sections

Section 1 Architecture.
```
  PR / scheduled / release workflow ----runs----> dev/package.py (main)
                                                     |
             check_* rules --text,source--> fail() --scan(built-in lists, private list)--> print line | withheld notice
             check_safety --kind,rel,match--> where(rel) + line no. --> "FAIL Safety: <kind> in <where>, line <n>"
             wait_on(label) --scan--> TIMEOUT/STOPPED label
             main() top-level handler --scan--> exception message
  runs.shown / regression.yml FAIL note / issue body  <-- replay the printed output (unchanged)
  toy (5 modes) --imports by spec--> expected lines; --subprocess--> real checker on mktemp tree
```
The coupling is new: `fail()` now depends on the pattern lists, which live in the same file. Single point: the scan. If it raised, the checker would crash and refuse; that fails safe, because nothing is printed and the run is red. Rollback: revert the one commit; the old prints come back, which is the known leak. Value test: the search report's consumer is the owner, for rotation. No finding beyond V5.

Section 2 Error and rescue.
```
  CODEPATH              | WHAT CAN GO WRONG                 | RESCUE                          | USER SEES
  fail() scan           | regex error on odd text           | none needed: re pure, no I/O    | normal line
  where()               | private list empty (CI)           | built-in check only             | path printed
  wait_on() label       | label holds a hit                 | label replaced                  | "name withheld"
  main() handler        | uncaught exception w/ private text| scanned, withheld on hit (V5)   | withheld notice
  private_prefixes()    | flow file unreadable              | NOTE line, [] (today)           | NOTE line
  search: log fetch     | 403/429, 410 past retention       | backoff; unreadable count       | record line
  search: count pass    | over budget                       | stop, ask operation (V3)        | ETA message
```
No silent catch-all is added. Gap closed by V5.

Section 3 Security. Threats:
- Matched text in public logs (High likelihood, High impact): mitigated by C1 and the Safety format.
- Private pattern or name in logs (Medium, High): mitigated by X1 and `where()`.
- Path-hash reversal (Medium, Medium): mitigated by X1 (no locator).
- Already-published exposure (High, High): not mitigable by code; V1 goes to the owner.
- The search itself copying matched text to disk (Low, High): in-memory only, no file written (S11).
- The toy committing a credential-shaped literal (Low, Medium): samples built at run time.
- dev/test-package.sh's literal (present, unknown): S14 plus an owner line.
No new input surface, endpoint, secret or dependency.

Section 4 Data flow and edge cases.
```
  file text -> pattern match -> (kind, rel, line) -> where() -> line -> stdout -> workflow log -> tail -> issue
     shadow: empty file (no match, no line); undecodable bytes (decoded with replace, line count still valid);
             match on line 1 (count 0 -> 1); several prefixes on one path (lowest k, one line);
             tail cut at 200/20 chars (source scan, C1); signal mid-run (wait_on label already clean)
```
Async ordering: the signal handler reads `waiting["on"]`, which is clean at assignment, so either order is safe. No interaction UI.

Section 5 Code quality. The fix lives at one choke point plus two helpers; three call sites change; no new class. Naming: `where`, `fail(source=)`. Complexity is low. Over-engineering risk is the top-level handler (V5): kept to about 6 lines.

Section 6 Tests.
```
  NEW THING                    TEST                         HAPPY        FAILURE              EDGE
  Safety line format           static, names modes          kind/line    old format = red     multi-prefix path
  fail() withholding           static (URL host), full      no hit equal hit withheld         cut tail (source)
  wait_on() label              full (hanging script)        clean label  private name hidden  --timeout short
  main() handler               full (forced exception)      -            message withheld     -
  PR log path                  pr-log mode                  exact cmd    -                    -
  tail path                    tail mode                    runs.shown   -                    400-char cut
  setup-fit edit               row setup-fit                #2 line      old assert red       case-insensitive
  dev/test-package.sh          its own run                  unchanged    -                    -
  sizes                        pkg-secret-print-4-sizes     under 20,480 -                    exactly 20,480
```
no_claim: the toy runs on a minimal tree, so it does not prove the real tree's other rules. The existing package rows cover those (release-static-rules, package-passes). Flakiness: no network, no time dependence; the hang case uses a short timeout with a margin.

Section 7 Performance. Each run scans failure text once more: negligible. The toy makes 10 checker runs on a minimal tree, measured in the build. The search is the slow path (thousands of log downloads), and V3's count pass bounds it.

Section 8 Observability. The checker's own lines are the observability; the withheld notice says how to see the detail locally. The search's record carries counts, coverage limits and the command text (V3).

Section 9 Deployment. There is no deploy: the fix takes effect on the next run after merge. The risk window is open pull requests whose branches carry the old checker; their runs keep the old prints until they merge main. Noted for the owner. Rollback is a single revert.

Section 10 Long-term. Debt: the checker now carries two output paths (Safety format and withholding). Reversibility 5/5. Path dependency: the allowlisted-output direction (T2) would replace `fail()`'s scan later. The 1-year question: the code comment above the helpers explains why (V7).

Section 11: SKIPPED (no UI scope).

NOT in scope:
- generic redactor in the workflow generator (TD1845);
- deleting or editing past logs and issues, and rotation (the owner's, V1);
- allowlisted diagnostics and standard scanners (T2, to the operation);
- a versioned audit script (TD1845);
- a synthetic GitHub workflow run (needs a push).

What already exists:
- `fail()` is the choke point;
- `test-package-static.py`'s by-spec pattern is reused;
- `runs.shown` is reused;
- `regression.py add/red` adds and proves the rows;
- `gh api` serves the search.

Dream state delta: the highest-exposure checker becomes no-echo and past exposure becomes known. The loop-wide contract (T2) stays open.

Error and rescue registry: 7 rows, 0 critical gaps (above). Failure modes registry: 7 rows, 0 critical gaps (every row is rescued or fails safe, and each has a test or record line).

```
  +====================================================================+
  |            MEGA PLAN REVIEW — COMPLETION SUMMARY                   |
  +====================================================================+
  | Mode selected        | SELECTIVE EXPANSION                         |
  | System Audit         | choke point fail(); CI has no private list; |
  |                      | setup-fit and test-package.sh affected      |
  | Step 0               | X1, X2 accepted; 3 spec reviews (6/10 each) |
  | Section 1  (Arch)    | 1 issue found (V5)                          |
  | Section 2  (Errors)  | 7 error paths mapped, 0 GAPS after V5       |
  | Section 3  (Security)| 7 issues found, 3 High (mitigated or owner) |
  | Section 4  (Data/UX) | 6 edge cases mapped, 0 unhandled            |
  | Section 5  (Quality) | 0 issues found                              |
  | Section 6  (Tests)   | Diagram produced, 0 gaps                    |
  | Section 7  (Perf)    | 1 issue found (search budget, V3)           |
  | Section 8  (Observ)  | 0 gaps found                                |
  | Section 9  (Deploy)  | 1 risk flagged (open PRs on old checker)    |
  | Section 10 (Future)  | Reversibility: 5/5, debt items: 1           |
  | Section 11 (Design)  | SKIPPED (no UI scope)                       |
  +--------------------------------------------------------------------+
  | NOT in scope         | written (5 items)                           |
  | What already exists  | written                                     |
  | Dream state delta    | written                                     |
  | Error/rescue registry| 7 rows, 0 CRITICAL GAPS                     |
  | Failure modes        | 7 total, 0 CRITICAL GAPS                    |
  | TODOS.md updates     | 0 items (no TODOS.md; T2 to the operation)  |
  | Scope proposals      | 5 proposed, 3 accepted (EXP + SEL)          |
  | CEO plan             | written                                     |
  | Outside voice        | codex completed                             |
  | Lake Score           | N/A                                         |
  | Diagrams produced    | 5 (architecture, error map, data flow,      |
  |                      | test map, dream state)                      |
  | Stale diagrams found | 0                                           |
  | Unresolved decisions | 0 (T1, T2, V8 and S12 go to the gate)       |
  | Reality rows         | 7/7 rows, 1 unverified                      |
  +====================================================================+
```

<!-- AUTONOMOUS DECISION LOG -->
## Decision Audit Trail

| # | Phase | Decision | Classification | Principle | Rationale | Rejected |
|---|-------|----------|----------------|-----------|-----------|----------|
| 1 | CEO | Mode SELECTIVE EXPANSION | Mechanical | override | autoplan rule | other modes |
| 2 | CEO | X1 no locator for private-matching paths | Mechanical | P1 P2 | hash reversible over tracked paths | 8-hex path hash |
| 3 | CEO | X2 clean-baseline filter | Mechanical | P1 | false reds | raw window scan |
| 4 | CEO | X3 withhold Scripts tail (folded into C1) | Mechanical | P1 P2 | done line 1 covers full mode | defer |
| 5 | CEO | 0H documents approved, continue to 0I | Mechanical | P6 | both inputs reflect decisions | revise |
| 6 | CEO | Spec fixes S1-S14, C1, D4 | Mechanical | P1 P5 | spec reviews 1-3 | - |
| 7 | CEO | V1-V9 from dual voices | Mechanical | P1 P2 | both or one voice, in blast radius | - |
| 8 | CEO | T1 one goal, fix committed before search | Taste | P6 | splitting changes frozen done lines | split goal (Codex) |
| 9 | CEO | T2 allowlisted output / standard tools to the operation | Taste | P3 | outside TD1845 | adopt now |
| 10 | CEO | Versioned audit script declined | Mechanical | P4 | TD1845 rules a command | script file |
| 11 | DX | Mode DX POLISH, persona agent/maintainer, target Champion | Mechanical | override, P5, P6 | autoplan rules | expansion |
| 12 | DX | W1-W9 accepted | Mechanical | P1 P5 | agent-ready error contract, correctness of pr-log | - |
| 13 | DX | T3 no local reveal flag | Taste | P1 (security) | local output reaches issue bodies via live lanes | --show-withheld (native) |
| 14 | DX | T4 docs in --help docstring, wiki page to the operation | Taste | P5 | no sixth hand-edited file | wiki page now |
| 15 | Eng | Scope accepted as-is, Y1-Y9 accepted | Mechanical | P5 P1 | both voices' findings, in blast radius | - |
| 16 | Eng | Y4 Safety before script checks (reorder) | Taste | P1 | Codex: a hanging script hides matches; native silent on order | keep order, accept TIMEOUT-only refusal |

### DX phase (DX POLISH)

Product type: CLI tool (`dev/package.py`, a release checker run by people, agents and CI) plus its regression toy. Persona (auto-decided, P6): an AI coding agent or maintainer running the checker unattended in a lane or in pull-request CI. It reads output literally, can't ask, and output it prints may be published (CI log, job summary, issue body).

```
TARGET DEVELOPER PERSONA
Who:       an agent or maintainer running dev/package.py (directly, through a package row, or in PR CI)
Context:   a release check fails, or a toy row goes red, and the output may be public
Tolerance: one rerun; it needs the next safe command from the output itself
Expects:   to learn which rule failed, in which file and line, without the output leaking anything
```

Empathy narrative (from the plan and the code as it stands): "My PR check went red. The log says `FAIL Safety: secret in skills/x/scripts/y.py, line 41`. Good: I open line 41 and see the token I pasted, and the log didn't repeat it. Next, a Disclosure line says withheld and tells me to run the check locally, but locally it's withheld too. Which file? I'm stuck until I grep every file myself. Then a toy row fails with a bare check name, and I can't tell which mode or case." Observed: the current output format (dev/package.py:147-149, :331-337). Predicted: the confusion over the withheld notice and the toy's failure names (the plan's text as written before this phase).

Competitive benchmark (no web research; reference knowledge only): gitleaks and trufflehog report rule id, file and line, and redact the secret by default (gitleaks `--redact`); GitHub secret scanning reports type and location, never echoing the value to a public log. This checker after the fix matches that shape (kind, file, line, no value). TTHW, from a checkout to a safe refusal on a sample: 1 command, under 1 minute [estimated]. Target: Champion (< 2 min), auto-decided (P5). Magical moment: the failing line names the exact file and line, and the public log shows no secret; the vehicle is the existing CLI output (DX POLISH, no new surface).

Dual voices. Native DX (Claude subagent, input dx 9e7c6061): CAP6 on the withheld fix line, the exception handler's trace, exit and channel, and the search's retry bound and auth handling; High: `pr-log` mode would run the real repo or skip silently, and hidden paths have no lookup; Medium: note_shell prints names, behavior for a path holding a built-in match, toy failure labels, toy usage, hang timing, reading the workflow line, codes and anchors, channel, size-row bytes. Codex DX (completed): High: the withheld recovery instruction doesn't work, and the config warning bypasses redaction (private_prefixes() prints the flow path); Medium: no quickstart or docs, and no upgrade contract for changed output.

```
DX DUAL VOICES — CONSENSUS TABLE:
  Dimension                           Claude  Codex  Consensus
  1. Getting started < 5 min?          yes     yes*   CONFIRMED (*undocumented) -> W8
  2. API/CLI naming guessable?         partly  yes    DISAGREE (#k lookup) -> W1, W8
  3. Error messages actionable?        no      no     CONFIRMED gap -> W1, W2, W3
  4. Docs findable & complete?         no      no     CONFIRMED gap -> W8
  5. Upgrade path safe?                n/a     no     DISAGREE (output-change note) -> W8
  6. Dev environment friction-free?    partly  partly CONFIRMED (pr-log, hang timing) -> W4, W6
```

Decisions: W1-W9 accepted (accepted block). TASTE T3: the native voice's local `--show-withheld` reveal flag is declined, because local output reaches public issue bodies through live lanes (`runs.shown`), so a reveal flag would reopen the leak. Codex's recovery sequence is taken instead. TASTE T4: the troubleshooting and output-change notes go in `dev/package.py`'s docstring, which is its `--help` text, not a new wiki page (no sixth hand-edited file); a wiki page is offered to the operation as a follow-up.

Pass 1 Getting started: 7 -> 8. One command (`python3 dev/package.py --static`); the gap is that its Safety output and exit codes aren't documented. W8 puts them in `--help`.
Pass 2 CLI design: 6 -> 8. `#k` gets a stated lookup (W1); the toy gets a usage line and exit 2 (W5); flags are unchanged.
Pass 3 Errors (agent-ready-v1):
```
ERROR PATH MATRIX (agent-ready-v1)
Path              | Class      | what | fix  | recovery | code | context | trace | redaction | channel | Cap
Safety line       | validation | pass | pass(W1)| pass  | pass(kind)| pass | N/A   | pass      | stdout+exit 1 (gap noted) | -
withheld notice   | validation | pass(W1)| pass(W1)| pass(W1)| pass | pass(where) | N/A | pass | stdout+exit 1 | -
TIMEOUT/STOPPED   | runtime    | pass | pass | pass(existing) | pass | pass | N/A | pass | stdout+exit 3 | -
unexpected error  | unexpected | pass(W2)| pass(W2)| pass(W2)| pass(exit 4)| pass | pass(W2) | pass | stderr+exit 4 | -
search fetch      | dependency | pass | pass(W3)| pass(W3)| pass | pass | N/A | pass | record | -
```
Before this phase: CAP6 (withheld fix, unexpected trace, search recovery), so 6/10; after W1-W3: 8/10. Channel: FAIL lines stay on stdout because existing rows grep stdout; the gap is noted.
Pass 4 Docs: 4 -> 7. W8 documents the output forms, kinds, `#k` lookup, withheld recovery, exit codes and the CI/local contract in `--help`. A wiki page is T4's follow-up.
Pass 5 Upgrade: 5 -> 7. W8 adds an output-change note (in `--help` and the PR body): the Safety line form, the collapsed count for multi-prefix paths, withheld notices, exit 4. Legacy unsafe output is not kept.
Pass 6 Dev environment: 6 -> 8. W4 fixes `pr-log`; W6 sets the hang timing; CI and Mac both run the toy (no network).
Pass 7 Community: N/A for an internal checker; the repo's issue flow (regression rows file issues) is the channel. 5/10, unchanged, no finding in scope.
Pass 8 Measurement: 6 -> 7. The build records each toy mode's time; TTHW is measured once in the build by a fresh run of `--static` on the sample tree.

DX journey map:
```
STAGE        | DEVELOPER DOES                         | FRICTION                       | STATUS
1. Discover  | sees a red PR check / package row      | which rule, file, line         | fixed (Safety form)
2. Install   | none (python3 in the repo)             | -                              | ok
3. Hello     | python3 dev/package.py --static        | output forms undocumented      | fixed (W8)
4. Real use  | fixes the file and line named          | hidden path: which file?       | fixed (W1 lookup)
5. Debug     | reads a withheld notice                | "run locally" was a dead end   | fixed (W1)
6. Upgrade   | scripts parsing old output             | changed forms                  | fixed (W8 note)
```
First-time report: T+0:00 the PR check is red; T+0:20 it reads `FAIL Safety: secret in <file>, line 41`; T+0:40 it opens the line and removes the value; T+1:00 it reruns `--static`, which passes. With a withheld line: T+1:30 it reads `--help`'s withheld section; T+2:30 it greps the named file with the lists and fixes it.

DX scorecard:
```
| Getting Started 8 | API/CLI 8 | Error Messages 8 | Documentation 7 | Upgrade 7 | Dev Env 8 | Community 5 | Measurement 7 |
TTHW < 1 min (Champion) | Magical moment: designed via the existing CLI output | Product: CLI tool | Mode: DX POLISH | Overall DX 7.3 -> from 5.6
```
DX implementation checklist: every error path meets the agent-ready contract (W1-W3); `--help` documents the output forms and recovery (W8); the toy has a usage line (W5); the pr-log mode runs the real workflow command on the sample tree (W4); the output-change note is in the PR body (W8); it works in CI without configuration (the toy is self-contained).

### Eng phase

Step 0 Scope Challenge. Proposed changed files: 5 (3 hand edits, 1 new toy, rows) [measured from Files]; new classes/services: 0. Below the complexity gate, so no structure question. Existing code per sub-problem:
- `fail()` (dev/package.py:147) is the choke point.
- `check_safety` (:319) holds the Safety formats.
- `wait_on`/`stop` print the label.
- `private_prefixes` (:308) loads the list.
- `runs.shown` (skills/workflow-regression/scripts/runs.py:44) does the tailing.
- `regression.py add/red` adds and proves the rows.
- `test-package-static.py` is the by-spec toy pattern.

Minimum change = the plan as amended; nothing is deferrable without failing a done line or a TD1844 item. No TODOS.md in the repo. Distribution: no new artifact. Result: scope accepted as-is.

| Premise | Claim | Receipt | Verdict |
|---|---|---|---|
| E1 | check_scripts runs before check_safety | dev/package.py:469-471 | verified |
| E2 | check_disclosure aggregates values into sets, losing the file | dev/package.py:355 | verified (native M1, Codex 4) |
| E3 | private entries are not validated as patterns | dev/package.py:313 | verified |
| E4 | the two workflow checker lines are identical | .github/workflows/regression-pr.yml:58, :84 | verified |
| E5 | in a linked worktree `.git` is a file | worktree root `.git` | verified (Codex 6) |
| E6 | test-package.sh echoes checker output on a miss | dev/test-package.sh:9 | verified (native M6) |

unverified=0.
REALITY: premise-table pass 6 premises, unverified=0 dev/package.py:469
REALITY: already-done pass last dev/package.py commit is 35a789cc8 (cap lift), no echo fix on origin/main f7f86150d dev/package.py:319
REALITY: surface-check pass --root, --static, --timeout, --out; regression.py add/red; gh api runs/attempts/logs dev/package.py:445
REALITY: binding-decisions pass o1003, TD1844, TD1845, TD1847, TD1849 cited; branch decision log empty .loop/goals/v110-pkg-secret-print.plan.md:3
REALITY: numbers pass 22,593 B [measured]; about 23,600 B after [estimated]; 10 checker runs in the toy [derived from the mode table] dev/package.py:1
REALITY: deferred-asks pass no linked issue; TD1844 a-d all mapped to checks .loop/goals/v110-pkg-secret-print.plan.md:3
REALITY: pr-count pass one PR, no ship policy file .loop/goals/v110-pkg-secret-print.plan.md:1

Dual voices. Native Eng (Claude subagent, input eng 9d65a5ca): sound with fixes; High H1 (the private list is needed before check_safety, so load it once), H2 (two withheld-notice forms); Medium M1 (Disclosure provenance), M2 (invalid private entries crash, and k numbering), M3 (samples sharing windows with the checker's own text), M4 (seen-red must show the no-window check failing), M5 (pr-log environment), M6 (toys echoing output), M7 (run ids reaching renderers), M8 (confirm D4 at the gate); Low (independent per-group counts, catch Exception not BaseException, absolute local paths, tail adds little, the 85-90-day expiry window, edit diffs). Codex Eng (completed): High 1 (historical search must recognize old Safety lines by form, plus continuation lines), 2 (full mode: a hanging script stops before Safety is reported; each case needs its own expected exit), 3 (the exception handler must not depend on the failed sanitizer); Medium 4 (Disclosure provenance), 5 (the oracle shrinks with the implementation), 6 (checkpoint path invalid in a worktree).

```
ENG DUAL VOICES — CONSENSUS TABLE:
  Dimension                           Claude  Codex  Consensus
  1. Architecture sound?               yes*    no     DISAGREE (*with H1/H2; Codex: ordering, provenance) -> Y1, Y3
  2. Test coverage sufficient?         no      no     CONFIRMED gap (oracle independence, seen-red proof) -> Y5, Y6
  3. Perf risks + budget/bench named?  yes     yes    CONFIRMED (toy modes timed; search count pass)
  4. Security threats covered?         partly  partly CONFIRMED gap (historical recognition, run-id spread) -> Y7, Y8
  5. Error paths handled?              no      no     CONFIRMED gap (bad private entry, handler fallback) -> Y2
  6. Deployment risk manageable?       yes     yes    CONFIRMED (single revert)
```

Section 1 Architecture.
```
  main()
   ├─ load_private() once ──> PRIVATE (compiled, raw-indexed; bad entries -> fixed NOTE by index)
   ├─ check_frontmatter / inventory / listing / files ──> fail(rule, text, source)
   ├─ check_safety  (moved before check_scripts) ──> where() + line ──> "FAIL Safety: <kind> in <where>, line <n>"
   ├─ check_scripts ──> wait_on(label) [label scanned] ──> fail("Scripts", tail, source=stderr)
   ├─ check_disclosure ──> value -> {files} map ──> fail(..., source=joined file texts, where=first file)
   ├─ note_shell ──> where()
   └─ except Exception ──> safe_message() [constant-text fallback if scanning fails] ──> stderr, exit 4
  fail() ──scan(PRIVATE + built-in lists)──> line | W1 withheld notice
```
Design-twice: no new module or public surface, so one line: the helpers stay private to dev/package.py. Red flags: none (one owner per piece of state; PRIVATE has a single loader).

Section 2 Code quality.
- [INFORMATIONAL] (confidence: 9/10) dev/package.py:355: Disclosure loses provenance; fixed by Y3.
- [INFORMATIONAL] (confidence: 8/10) dev/package.py:308: list loaded inside check_safety only; fixed by Y1.
No duplicated behavior beyond the one scan helper shared by fail(), where(), wait_on() and the handler.

Section 3 Tests. The coverage diagram:
```
CODE PATHS                                          USER FLOWS (agent/maintainer reading output)
[+] dev/package.py                                  [+] PR check red
  ├── check_safety format     [GAP->static,names]     ├── [GAP->pr-log] the workflow line's output
  ├── where()                 [GAP->names]            └── [GAP->tail] the scheduled replay
  ├── fail() scan + source    [GAP->static,full]    [+] Local run
  ├── wait_on() label         [GAP->full hang]        ├── [GAP->full] the hanging private-named script
  ├── load_private() bad entry[GAP->static]           └── [GAP->static] unreadable flow file NOTE
  ├── Disclosure provenance   [GAP->static URL host]
  ├── handler + fallback      [GAP->full exception]
  └── note_shell where()      [GAP->names]
[+] dev/toy/test-setup-fit.sh  [★★ existing; GAP->new #2 + absence check]
[+] dev/test-package.sh        [★★ existing; unchanged assertion]
COVERAGE after plan: every new path has a mode; Y5 adds independent per-fixture checks; Y6 makes seen-red prove the no-window check.
```
Test plan artifact: written locally (eng-review test plan, 2026-11-25 09:02), outside the repo.

Section 4 Performance. The toy makes 10 checker runs on a minimal tree, measured in the build. Scanning each failure line once more against compiled patterns is negligible. The search's slow path is bounded by the count pass, the retry cap and the budget (V3, W3).

Failure modes registry:
```
  CODEPATH            | FAILURE MODE                         | RESCUED? | TEST?        | USER SEES?          | LOGGED?
  load_private        | bad pattern entry                    | Y (skip) | static case  | fixed NOTE by index | stdout
  fail() scan         | scan raises                          | Y (Y2)   | full case    | constant notice     | stderr
  check_scripts       | hanging child with Safety in tree    | Y (Y4)   | full hang    | Safety lines, then TIMEOUT | stdout
  disclosure          | value from clean and matching files  | Y (Y3)   | static URL   | withheld notice     | stdout
  handler             | exception carrying private text      | Y (W2)   | full exc.    | exit 4, withheld    | stderr
  search              | old line fragment not re-matching    | Y (Y7)   | record check | counted by form     | record
  search checkpoint   | worktree .git is a file              | Y (Y8)   | build run    | path from git dir   | record
```
Critical gaps: 0.

NOT in scope (Eng):
- a public structured-output mode (T2);
- editing the 20+ toys that call the checker (M6 lists them only);
- Windows CRLF size measurement;
- a synthetic GitHub run.

What already exists: the choke point, the by-spec toy pattern, runs.shown, regression.py add/red, gh api.

Worktree parallelization: sequential implementation, no parallelization opportunity (one primary module).

Completion summary:
- Step 0: scope accepted as-is.
- Reality rows: 7/7, 0 unverified.
- Findings: Architecture 2, Code Quality 2, Test 2 gaps (oracle, seen-red), Performance 0.
- Failure modes: 0 critical gaps.
- Unresolved decisions: 0 in this review (V8, D4 and S12 go to the gate).
- Outside voice: codex completed.
- Parallelization: 1 lane, sequential.
- Lake Score: N/A.

<!-- autoplan-baseline-edits:ceo {"sourceSha256":"ce36a593128d30d2db45773c071385e111f3a914500b530714776c46e8f93cb2","replacements":[{"oldText":"### 1. The failure line (done line 1, required item a)\n\nIn `dev/package.py`'s safety check, every Safety failure line becomes:\n\n`FAIL Safety: <kind> in <where>, line <n>`\n\n- `<kind>` is the built-in group's name (secret; obfuscation or encoded text; instruction aimed at the agent; dangerous command) or `private prefix #<k>`, where k is the entry's position in the private list. The pattern is never printed.\n- `<where>` is the shipped path, unless the path itself matches any private prefix. Then `<where>` is `a file whose name matches private prefix #<k>`, with no path, hash or other locator (a hash of a tracked path can be reversed by hashing every tracked path). The operator finds the file locally with the private list.\n- `<n>` is the 1-based line of the match's start, counted from the decoded text.\n- A file-name match on its own prints `FAIL Safety: private prefix #<k> in a file name`. Required item a is stricter than done line 1's \"naming the file\" and governs here (TD1844).\n- No slice, repr or length of the matched text is printed anywhere, and nothing else in the safety check echoes file content.\n\nOne small helper builds the line from (kind, rel, text, match). The three existing format strings call it. The failure list keeps one entry per failure as today, so the count and the exit status are unchanged.\n\nBytes: dev/package.py: now 22,593, after about 22,800, left about -2,320 to 20,480; note: `dev/` is not shipped, so no package limit applies; the file is already over 20,480 on main; the change replaces three format expressions and adds the helper (about 200 B net); the build measures the real size and states it in the build record\n\n### 2. The toy (done lines 1 and 2, required items a and b)\n\n`dev/toy/test-package-no-echo.py` (new file, approved TD1845, about 6,500 B):\n\n- Builds a temporary tree under `mktemp` from the shipped files of the checkout (like the existing static-check toy) and adds one shipped text file holding one sample for each built-in group and one for a made-up private prefix, each on a known line, plus one file whose name matches the made-up prefix.\n- Every sample is built at run time from split parts, so no committed text holds a credential-shaped string. The private prefix is a made-up toy word written to a temporary flow file passed through `LOOP_FLOW`, with a temporary `HOME`, so no real private name is read or written.\n- Runs the real `dev/package.py --root <tree>` twice, with `--static` and without (full).\n- For each run, it checks the exit status is a refusal and that there is one Safety line per sample, naming the right kind, path (or path hash) and line number.\n- It checks that the combined stdout and stderr holds no window of 6 or more characters of any sample (case-insensitive for the private one), not the private pattern, and not the matching file's name. A window counts only if it is absent from the same run on the tree without the samples (a clean baseline), so kind labels and paths can't cause a false red.\n- (b) It feeds the same captured output through the regression skill's own last-lines helper (`runs.shown`, the helper the scheduled run's FAIL note, job summary and issue body are built from) and checks the result the same way.\n- It ends with `ALL PASS` or names each failing check, and removes only its own `mktemp` folder.\n\nSeen red: before the fix, the build runs the toy against today's `dev/package.py` (from origin/main) and records its failing lines by check name only (the toy never prints a sample). The record says how many checks failed and which ones. After the fix it passes in both modes.\n\n### 3. Rows (done lines 1, 2 and 4)\n\nAdded through `regression.py add` and marked red with `regression.py red` on the pre-fix code, each `land` level:\n\n- `pkg-no-echo-static`: the toy's `--static` half (done line 1).\n- `pkg-no-echo-full`: the full half (done line 1).\n- `pkg-no-echo-names`: no private pattern and no matching file name (item a).\n- `pkg-no-echo-tail`: the tailed output used by the scheduled path holds none of the samples (done line 2, item b).\n\nNo existing row's command or assertion changes. Before the review the build runs, singly and from the clean environment, the package rows and the cheap rows the worker rules name (pods-size, package-*, adopt-set-*, listing-names-every-command, release-static-rules, home-guard-catches-leak, setup-fit, docs-import-rows-pass, sync-check-preview). It records each result line, so that no row turns red (done line 4).\n\n### 4. The 90-day search (done line 3, required item c)\n\nA build-time command, not a new script, run once by the worker on the Mac. Its output never leaves the machine except as described below:\n\n- Lists the pull-request workflow's runs and the scheduled regression workflow's runs created in the last 90 days, by 7-day windows, because the list call stops at 1,000 rows. It also reports each window's count.\n- For each run, fetches its log straight into an in-memory counter that keeps only the run id and the kind from lines of the checker's Safety form. For an old-format private line it keeps only `private prefix`. It never writes a raw log line to disk, never prints one, and keeps no matched text.\n- Reads the regression issues (open and closed, every label the scheduled run files) and the main-red issues the same way, keeping the issue number and the kind only.\n- Names each window or run whose log could not be read (past retention, or refused) as unreadable, with a count.\n- Writes the list (run id or issue number, kind) and the unreadable windows to the goal's local, untracked record under `.git/loop/`. The operation gives that list to the owner for the rotation decision. The PR body carries only the counts (runs searched, runs with a match by kind, issues with a match by kind, unreadable windows), never a run id or issue number that points at a log holding a match.\n\n### 5. The two named files (required item d)\n\nThe build inspects `.loop/goals/hotfix-4892.md` and `dev/toy/test-setup-fit.sh` with the checker's own patterns, and with the private list where it is present (the Mac's flow file). It records each hit by kind and line only in the goal's local record, and gives counts by kind in the PR body. It edits neither file: any follow-up goes to the operation.\n\n### 6. Going beyond the done lines\n\nThe PR body names items a, b, c and d as going beyond the frozen done lines (TD1844), each with its check: a and b by the toy's checks and the two rows; c by the search's counts; d by the inspection's counts.\n\n## Checks the build runs\n\n- The toy seen red on today's code, then green, in both modes.\n- The four new rows red before the fix, green after.\n- The single-row set from the worker rules, from the clean environment, before review.\n- `python3 dev/package.py --static` on the branch, its output read only for its last line (it passes on the real tree).\n- A grep of the diff for the service repo's name and for any credential-shaped literal (none).","newText":"### 1. What the checker prints (done line 1, required item a)\n\nOperation rulings: TD1844 (items a-d required), TD1845 (source-only fix, the one new toy, the search as a command), TD1847 08:30 (`dev/toy/test-setup-fit.sh` approved as a hand-edited file; no locator for name matches; withheld tails), TD1849 08:37 (`dev/test-package.sh` joins the repair).\n\nIn `dev/package.py`:\n\n- Safety lines read `FAIL Safety: <kind> in <where>, line <n>`.\n  - `<kind>` is the built-in group's name (secret; obfuscation or encoded text; instruction aimed at the agent; dangerous command) or `private prefix #<k>`. k is the 1-based position in the list `private_prefixes()` returns. The pattern is never printed.\n  - `<where>` comes from a helper `where(rel, private)`. It returns the path, unless the path itself matches a private prefix or any built-in pattern. Then it returns `a path matching private prefix #<k>` (lowest matching k) or `a path matching <kind>`, with no path, hash or other locator, because a hash of a tracked path can be reversed over the tracked paths.\n  - `<n>` is `text.count(\"\\n\", 0, match.start()) + 1`.\n- A path that matches private prefixes prints one line, `FAIL Safety: private prefix #<k> in a path`, naming the lowest k. Today it prints one line per matching prefix, so the `REFUSED` count drops for a path matching several prefixes; every other count is unchanged.\n- Item a, as TD1844 words it (\"no private pattern or matching file name printed\"), governs over done line 1's \"naming the file\" where a path matches. The build record and the PR body name TD1844 (a) as the authority.\n- Every other rule's failure text goes through `fail(rule, text, source=None)`. Before printing, `fail()` runs the built-in lists and the private list over `text`, and over `source`, the uncut text the line was cut from. On any hit it prints `FAIL <rule>: (withheld: the line held a Safety match; run the check locally to see it)`. The callers pass `source`:\n  - the Scripts rule passes the whole stderr (its line keeps only the last 200 characters);\n  - the Version rule passes the whole VERSION text (its line keeps only 20);\n  - the Disclosure rule passes the whole file text, so any host or command line from a file holding a Safety match is withheld.\n  - Lines with no hit are byte-identical to today, so rows that grep them (for example the hang toy's Scripts and TIMEOUT lines) keep passing.\n- The TIMEOUT and STOPPED lines print the `waiting on` label straight from the signal handler, not through `fail()`. So `wait_on()` cleans the label when it is set: a label holding a hit becomes `a shipped script (name withheld) --help`.\n- No slice, repr or length of matched text is printed anywhere.\n\nBytes: dev/package.py: now 22,593, after about 23,600, left about -3,120 to 20,480. Note: `dev/` is not shipped, and done line 4 is read as the shipped package's scripts, following the precedent rows dlf-done-3-sizes and make-room-b-5-sizes, which measure `skills/` only. The file is already over 20,480 on main. The build measures the real size.\n\n### 2. The toy (done lines 1 and 2, required items a and b)\n\n`dev/toy/test-package-no-echo.py`, the one new file (TD1845), about 8,000 B. One mode argument per run:\n\n| Mode | Checker run | Cases | Row |\n|---|---|---|---|\n| `static` | `--static` | one sample per built-in group and one private sample, each in its own shipped file; a private sample as a URL host (Disclosure) | pkg-no-echo-static (done line 1) |\n| `pr-log` | the exact command of the pull-request workflow's checker step, read from `.github/workflows/regression-pr.yml` at run time, on the sample tree | the `static` cases | pkg-no-echo-pr-log (done line 2) |\n| `full` | full (`--help` pass and ZIP) | the `static` cases; a shipped script whose `--help` fails with a source line holding a sample (Scripts tail); a private-named script that hangs, run with a short `--timeout` (TIMEOUT label) | pkg-no-echo-full (done line 1) |\n| `names` | `--static` | a private-named path, a private-named folder, a path holding a built-in match, and a Safety match inside a private-named file | pkg-no-echo-names (item a) |\n| `tail` | `--static` | the `static` output put through `runs.shown`, the helper the scheduled run's FAIL note, job summary and issue body are built from (part of output the `static` check already covers) | pkg-no-echo-tail (item b) |\n\n- **Tree.** A minimal temporary tree under `mktemp`: README.md, LICENSE, listing.json, VERSION and one skill folder with a SKILL.md, plus the case files inside that skill. It is made a git repo with every file added, like `test-package-static.py`, so the tracked-file path is exercised. `--out` always points inside the `mktemp` folder. Full mode on this tree takes seconds, so every mode fits a pull-request land row; the build records each mode's measured time.\n- **Samples.** A sample is the matched text. Each match is at least 12 characters and is built at run time from split parts, so no committed text holds a credential-shaped string. File and folder names share no 6-character window with any sample. The private prefix is a made-up toy word, written to a temporary flow file passed through `LOOP_FLOW`, with a temporary `HOME`. The baseline run uses the same `LOOP_FLOW` and `HOME`.\n- **Expected lines.** The toy imports `dev/package.py` by spec and, in-process, runs each pattern list and the toy private list over each case file. That gives every (kind, line) pair the checker reports: each matching pattern, first match per file, no dedupe. The toy formats the expected lines itself with its own format strings, never the checker's helper.\n- **Checks, per mode.**\n  - The exit status is a refusal, and every expected Safety line is present.\n  - After the expected Safety lines and the final REFUSED line are removed, no Safety line remains.\n  - No remaining text, nor the withheld notices' surroundings, holds a 6-character window of any sample, the private pattern, a private-named path or its basename (case-insensitive for the private ones). As a second filter, a window counts only if it is absent from the same mode's run on the tree without the case files.\n- **Ending.** The toy ends with `ALL PASS` or names each failing check by name only (it never prints a sample), and removes only its own `mktemp` folder.\n\nSeen red: the build runs every mode against today's `dev/package.py` (origin/main) first and records the failing check names and counts. After the fix every mode passes.\n\n### 3. Rows and the two edited toys (done lines 1, 2 and 4)\n\nRows are added through `regression.py add --goal ... --describe ...`:\n- pkg-no-echo-static: land, criterion, goal v110-pkg-secret-print:1.\n- pkg-no-echo-full: land, criterion, :1.\n- pkg-no-echo-names: land, criterion, :1.\n- pkg-no-echo-pr-log: land, criterion, :2.\n- pkg-no-echo-tail: land, criterion, :2.\n- pkg-secret-print-4-sizes: land, criterion, :4, `! find skills -name '*.py' -size +20479c | grep -q .` (strictly under 20,480, which is the limit the checker itself enforces).\n- done-pkg-secret-print-3: covered, workflow, :3, \"proved by the search recorded in the goal's run record\".\n\nEach toy row's red proof is `regression.py red <id> --break \"git checkout <base> -- dev/package.py\"`, run after the toy and the fix are committed (base = the branch's merge base with main).\n\n- `dev/toy/test-setup-fit.sh` (TD1847). Its assertion of the old private-prefix line (nightly row setup-fit) changes to the new form. The toy's flow list has two entries and the appended text matches the second, so it expects `private prefix #2 in <path>, line <n>`, with path and line worked out at run time from the toy's own data. It adds a check, ignoring case, that neither the toy's prefix pattern nor the appended text appears in the output, so the assertion gets stricter, never looser. The PR body shows the old and new assertion lines in the toy's own words only (never a real pattern), and the new check seen red on f7f86150d. If the deliver-first safety check flags it as a loosened test, it goes to the operation with the diff.\n- `dev/test-package.sh` (TD1849). Its committed credential-shaped sample is built at run time from parts, so no committed line matches a token shape. Its assertion (the secret refusal) stays unchanged, and the build shows the script passing before and after. No history rewrite (TD1763). Everything is reported by file and kind only. Whether it was a real token, and secret scanning, are the owner's.\n\nEvery other existing row's command and assertion is unchanged. Before the review, the build runs singly from the clean environment the package rows, setup-fit, and the worker rules' cheap rows (pods-size, package-*, adopt-set-*, listing-names-every-command, release-static-rules, home-guard-catches-leak, docs-import-rows-pass, sync-check-preview). It records each result line (done line 4).\n\n### 4. The 90-day search (done line 3, required item c)\n\nA build-time command, not a new script, run once by the worker on the Mac. Its sources are what TD1844 item (c) requires, \"pages by date, covers PR runs, scheduled runs and the regression issue bodies, reports by run id or issue number and kind only, and names unreadable days\". Two expansions are accepted: the main-red issues the operation named on 08:14, and issue edit histories (P1).\n\n- **Runs.** Listed through the API by created-date window; a window returning 1,000 runs is split until each returns fewer. It keeps runs of every workflow that ran the checker in the 90 days, by path: the pull-request workflow, the scheduled regression workflow, the release workflow, and any renamed or deleted file. The health workflow, deleted inside the window, is checked for checker runs. The record lists each path searched.\n- **Logs.** Every attempt's log is fetched with `gh api .../runs/<id>/attempts/<n>/logs` into Python memory and unzipped there, with no log file written. On 403 or 429 it backs off as the response's retry header says. Progress (run ids, attempts and kinds only) is checkpointed to a local untracked file so the search can resume.\n- **Issues.** The regression and main-red issues' bodies, comments and edit histories (GraphQL `userContentEdits`).\n- **Counting.** Every checker output line (`FAIL <rule>:`, `TIMEOUT:`, `STOPPED:`) is scanned in memory with the built-in lists and the private list and classified by kind; a line that holds a hit but can't be classified counts as `unparsed`. Each line is tagged by the job step or row that printed it. The direct checker step and real-tree package rows are counted; toy-row lines (the toys' own samples) are listed separately. Job summaries have no read API. The scheduled run prints the same FAIL note to its log first, and the record says so.\n- **Unreadable.** Each window or run whose log can't be read (past retention, or refused) is named, with a count.\n- **Where the list goes.** \"The goal's record\" is read as the goal's run record (`.git/loop/runs/v110-pkg-secret-print.json`, through the build record). The operation and the owner can read it. It is not committed text, because a public run id or issue number points straight at a log or issue holding a match. The PR body carries counts only. If the operation rejects this reading at the gate, the build stops at this step and asks where the list goes; it never commits run ids on its own.\n\n### 5. The two named files (required item d)\n\nThe build inspects `.loop/goals/hotfix-4892.md` and `dev/toy/test-setup-fit.sh`, on the base version before any edit, with the checker's own lists and with the private list where it is present (the Mac's flow file). It records each hit by kind and line only in the goal's run record, and gives counts by kind in the PR body. The hotfix goal file is not edited; `dev/toy/test-setup-fit.sh` changes only as section 3 says. Any other follow-up goes to the operation.\n\n### 6. Going beyond the done lines\n\nThe PR body names what goes beyond the frozen done lines, each with its check:\n- item a: `names` mode;\n- item b: `tail` mode;\n- item c: the search's counts;\n- item d: the inspection's counts;\n- the other-rule withholding and the TIMEOUT label: `full` and `static` cases;\n- the edits to the two existing scripts (TD1847, TD1849).\n\n## Checks the build runs\n\n- Every toy mode seen red on today's code, then green.\n- The seven new rows: the five toy rows red before the fix (`regression.py red --break`) and green after; the size row green; the covered row pointing at the run record.\n- setup-fit's new check seen red on f7f86150d, then green; `dev/test-package.sh` passing before and after.\n- The single-row set from the worker rules, from the clean environment, before review.\n- `python3 dev/package.py --static` on the branch, its output read only for its last line (it passes on the real tree).\n- A grep of the diff for the service repo's name and for any credential-shaped literal (none)."}]} -->

<!-- autoplan-accepted:ceo -->
- X1: a private-matching path prints one line naming the lowest k, `FAIL Safety: private prefix #<k> in a path`, with no locator; Safety lines name files through `where()`, which also hides a path holding a built-in match; verified by `names` mode (row pkg-no-echo-names).
- X2/S5: the toy removes the expected Safety lines (computed in-process per case file, formatted by the toy itself) and the REFUSED line, requires no other Safety line, and finds no 6-character window of any sample, private pattern or private-named path in the rest, with a same-mode clean baseline (same LOOP_FLOW and HOME) as a second filter; verified by every mode red on today's code and green after the fix.
- C1: `fail(rule, text, source=None)` withholds any non-Safety failure line whose text or uncut source holds a built-in or private match (Scripts passes whole stderr, Version the whole VERSION text, Disclosure the whole file text); `wait_on()` cleans the TIMEOUT/STOPPED label; lines with no hit are byte-identical; verified by `static` (URL host), `full` (failing --help traceback, hanging private-named script) and the unchanged hang toy.
- S1 (TD1847): dev/toy/test-setup-fit.sh expects `private prefix #2 in <path>, line <n>` (path and line worked out at run time) and checks, ignoring case, that neither its prefix pattern nor its appended text appears; seen red on f7f86150d, green after; the PR body shows old and new assertion lines in the toy's own words only.
- S2: TD1844 (a), "no private pattern or matching file name printed", governs over done line 1's "naming the file" for matching paths; named as the authority in the build record and PR body.
- S9: seven rows (five toy rows land, pkg-secret-print-4-sizes with `-size +20479c`, done-pkg-secret-print-3 covered/workflow), each with its goal field; red proofs by `regression.py red --break "git checkout <base> -- dev/package.py"` after the toy and fix are committed.
- S11: the 90-day search by split date windows over every workflow path that ran the checker (pull-request, scheduled regression, release, renamed/deleted, health checked), every attempt's log in memory with backoff and a resumable ids-and-kinds checkpoint, issues' bodies, comments and edit histories, every checker output line scanned and tagged by step or row with toy-row lines listed apart, unreadable windows named.
- S12: the run-id list lives in the goal's run record, not committed text, with counts only in the PR body; if the operation rejects this reading at the gate, the build stops at that step and asks.
- S14 (TD1849): dev/test-package.sh builds its credential-shaped sample at run time from parts, keeps its secret-refusal assertion unchanged, passes before and after, no history rewrite, reported by file and kind only.
- D4: done line 4 is read as the shipped package's scripts, following precedent rows dlf-done-3-sizes and make-room-b-5-sizes; dev/package.py (after about 23,600 B) is not shipped.
- V1 (native F1 + Codex 1, both High): the PR body ends with owner actions, as counts only: runs and issue edits still readable that hold a match (log deletion and edit redaction are the owner's); runs in which a private pattern itself was printed (replacing the private list is the owner's); the credential-shaped sample in dev/test-package.sh and whether a provider's scanning may already have flagged it (validity and rotation are the owner's, time-sensitive). The gate summary carries the same lines to the operation. Nothing is deleted, edited or rotated by the build.
- V2 (native F9 + Codex 2): the environment contract is stated in the build record: in CI the private list is absent by design (a private list in public CI would itself leak), so CI runs can hold only built-in matches; private-kind protection and private-kind historical hits are local only (live lanes, local rows). The search reports private-kind counts with that note. No fail-closed private check in CI.
- V3 (native F7, F8 + Codex 4): the search starts with a count pass (runs and attempts per window and workflow, no log fetch), records the estimate and an ETA, and sends it to the operation before fetching; over budget goes to the operation. The run record keeps the exact command text, the detector version (the commit of dev/package.py whose lists were used), the coverage limits, and three separate counts: confirmed hits, unreadable (unknown, never clean), and not assessed. Windows past log retention are expected to be unreadable.
- V4 (native F4): the toy's private prefix word is at least 12 characters; any forbidden string shorter than 6 characters is checked whole, not by windows.
- V5 (native F5): `main()` gets a top-level handler: an uncaught exception's message goes through the same scan, and is printed as the withheld notice on a hit; a `full`-mode toy case forces an exception carrying a private-named path.
- V6 (native F6): the PR body states dev/package.py's size before and after, and the done-line-4 reading with its precedent rows.
- V7 (native F10, F11): when `where()` hides a path, the Safety line keeps its line number, because a line number in a file whose path is hidden narrows nothing a reader can open; whole failure lines are withheld instead of masking part of them, because partial masking leaks through length and surrounding text. Both reasons are written into the code comment above the helpers.
- V8 (native F3): the operation confirms at the gate that TD1844 (a) governs over done line 1's "naming the file" for matching paths, and that confirmation goes into the run record.
- V9 (Codex 5, partly): the no-window check runs over the entire captured output of each run, including any withheld notice; the `pr-log` mode runs the pull-request workflow's exact checker command. A synthetic run of the workflow itself on GitHub needs a push, so it is not part of the build.
<!-- /autoplan-accepted:ceo -->

<!-- autoplan-accepted:dx -->
- W1 (both voices): the withheld notice reads `FAIL <rule>: withheld: a line from <where> held a <kind> match. Find it locally with the lists in dev/package.py and your leak_prefixes, fix it, then rerun (see --help, Safety output)`, with `<where>` from `where()`; for a private-hidden path, `--help` states that `#k` is entry k of `leak_prefixes` in `$LOOP_FLOW` (default `~/.workflow-loop/flow.json`). No local reveal flag (taste T3); verified by `static` and `names` modes asserting the notice's form and that it holds no sample window.
- W2 (both voices): an uncaught exception prints `ERROR (unexpected): <exception type>: <message>` to stderr and exits 4; the message and the traceback are printed only when they hold no built-in or private hit, otherwise `withheld (it held a <kind> match)` replaces them; verified by the `full`-mode forced-exception case (exit 4, stderr, no sample window).
- W3 (native CAP6): the 90-day search caps retries at 5 per request and sets a total wall-clock budget recorded in its ETA; 404/410 counts as unreadable (past retention); 401 or a scope 403 stops with `gh auth refresh -s repo,actions:read` as the fix line; the checkpoint file is `.git/loop/runs/v110-pkg-secret-print.search.json` (untracked, inside the git dir), kept until the operation's word.
- W4 (native High): `pr-log` mode copies `dev/package.py` into `<tmp>/dev/`, asserts the copy exists, and runs the workflow's checker command with cwd `<tmp>`; the command is every `run:` line in `.github/workflows/regression-pr.yml` holding `dev/package.py`, which must all be identical (the toy fails by name if none or they differ).
- W5: the toy prints `usage: test-package-no-echo.py {static|pr-log|full|names|tail}` to stderr and exits 2 on a missing or unknown mode; each failure prints `FAIL <mode>/<case>: <check>` with made-up case labels that share no window with any sample, plus expected and found Safety-line counts.
- W6: the hang case runs with `PACKAGE_CHILD_SECONDS=30` and `--timeout 3`, so the run-level TIMEOUT label fires first; the toy's own run is bounded and recorded.
- W7 (both voices' redaction boundary): `note_shell()` prints its names through `where()`; `private_prefixes()`'s load-failure NOTE prints a fixed line (`NOTE: no leak_prefixes loaded (the flow file is missing or unreadable); only the built-in scans ran`) without the path; a path holding only a built-in match is not refused (unchanged) but is hidden by `where()`; verified by a `static` case with an unreadable flow file and a `names` case with a built-in-matching path.
- W8 (both voices; taste T4): `dev/package.py`'s docstring (its `--help` text) gains a "Safety output" section: the line forms, the kinds as stable codes, `#k` lookup, the withheld recovery sequence, exit codes 0/1/3/4, the CI/local contract, and an output-change note (Safety form, the collapsed count for multi-prefix paths, withheld notices, exit 4); the PR body repeats the output-change note.
- W9: FAIL lines stay on stdout (existing rows grep stdout), and the size row's `find -size` measures on-disk bytes (LF on Linux CI); both noted in the build record.
<!-- /autoplan-accepted:dx -->

<!-- autoplan-accepted:eng -->
- Y1 (native H1, M2 + Codex 3): `main()` loads the private list once, before any check, into one module global of compiled patterns; `#k` is the 1-based raw position in the flow file's `leak_prefixes` array; an entry that is not a non-empty string or does not compile is skipped with a fixed NOTE naming it by index only; every helper reads the global; the NOTE line now comes first in the output (recorded in the build record).
- Y2 (Codex 3, native Low): the top-level handler catches `Exception` (not `BaseException`), prints `ERROR (unexpected): <type>` and the message or the withheld wording through the scan, and falls back to the constant line `ERROR (unexpected): details withheld` if the scan itself raises; exit 4, stderr; verified by a `full` case forcing an exception with a private-named path and a `static` case with a malformed private entry.
- Y3 (native M1 + Codex 4): Disclosure keeps a map from each host or command to the files it came from; a failing value is withheld when any of its files holds a Safety or private match (source = those files' joined text) and names `where()` of its first file; verified by the `static` URL-host case with the same value in a clean file and a matching file.
- Y4 (Codex 2, taste T5): `check_safety` runs before `check_scripts`, so a hanging or failing script can't stop the run before Safety findings are printed; each `full` case runs on its own tree with its own expected outcome (Scripts tail: exit 1; hang: Safety lines then TIMEOUT, exit 3; exception: exit 4).
- Y5 (Codex 5, native Low): each case file names its designated kind and line in the toy's own table, and the toy fails if that (kind, line) is missing, before adding any further pairs derived from the checker's lists; plus one fixed count per built-in group as a cross-check that no list shrank unnoticed.
- Y6 (native M3, M4): no sample shares a 6-character window with the checker's fixed text (kind names, notice templates, TIMEOUT, NOTE and REFUSED lines), checked by the toy at start; each mode's seen-red record and each `regression.py red --break` must show the no-window check among the failing checks, not only the format check.
- Y7 (Codex 1, native Low): the historical counter counts every old-format Safety line by its form (`FAIL Safety: <group> in ` or `private prefix ` before ` in `) as one exposure of that kind, without re-matching the excerpt; for other checker lines and their following lines up to the next known line form, it scans with the lists and records `possible <kind>`; `userContentEdits` diffs are scanned; each window's fetch time is recorded.
- Y8 (Codex 6, native M7): the search's checkpoint and its id list live in `$(git rev-parse --git-common-dir)/loop/runs/v110-pkg-secret-print.search.json`; the run record holds only counts and that path, so no renderer reads the ids; the build confirms one board render and one check-in render hold none of them.
- Y9 (native M5, M6, M8): `pr-log` runs the workflow line under `bash -c` with `sys.executable`'s folder first on PATH, `LOOP_FLOW` unset and a temporary HOME with no flow file; the build lists, by file name, the toys that call `dev/package.py` and echo its output or their fixtures on failure (no edits); the operation confirms the done-line-4 reading (D4) at the gate with V8, and the size row's `+20479c` matches the checker's own `>=` limit.
<!-- /autoplan-accepted:eng -->
