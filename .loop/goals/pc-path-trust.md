# Windows worktree paths are trusted under a trusted repo root (patch for MCH-1; fixes #5722)

- Slug: pc-path-trust
- Touches: skills/workflow-monitoring, dev/toy, .loop/regression.tsv, docs
- ETA: 325 active minutes (estimate 260m plus a 25% margin)

## Done lines

Frozen. A wrong done line needs a new goal.

1. Given a trusted repo root and a worktree under it with Windows-style paths (backslashes, any drive-letter case), then untrusted() treats the worktree as trusted; the prefix is built with os.sep, and both sides go through os.path.normcase
2. Given a folder outside the trusted root, or a sibling path that only shares a prefix string (for example agent-workflow-template2), then it is still refused (negative control)
3. Given macOS and Linux paths, then behaviour is unchanged
4. Given the change, then checks green (docs, package, private-name), no existing row turns red, no test loosened, no new file under skills/

## Verify by hand

<!-- Numbered steps for a person, each with an Expect: line. A release needs this. -->
1. On a Windows machine where the repository root is trusted in the app, start a new goal and bind it to a worker session with `python3 skills/workflow-monitoring/scripts/sessions.py bind SLUG SESSION`.
   Expect: the bind goes through and prints the session name; it does not print REFUSED or FOLDER_TRUST for the new worktree under the trusted root.
2. On the same machine, bind a goal whose worktree is outside the trusted root.
   Expect: it prints `REFUSED: ask the owner to trust` followed by that folder and `(FOLDER_TRUST)`.
3. This step needs a person on a Windows machine; the tests here only simulate Windows paths. The loop cannot reach done for MCH-1 on Windows without it, and the release refuses a goal with no Verify by hand step.

## PR notes

What this changes: the folder-trust test in the operation script now builds both sides of its prefix test with normcase and os.sep, so on Windows a worktree under a trusted root is trusted (fixes #5722). The script grows by 11 bytes (20,455 to 20,466, under the 20,480 fail line). A new toy section runs the real function with Windows path functions on any host; one regression row, now a defect row linked to #5722, was seen failing on the unedited script (3 of its cases) and passes now; the Tests tables are regenerated.

Open for the owner (not decided here):
- One review finding is open, owner-level: on a Windows directory flagged case-sensitive, normcase folds two directories that differ only in case into one trusted entry (Codex adversarial pass 1, rated High, blocks). It follows from done line 1 itself ("both sides go through os.path.normcase") and the issue's own fix, so it cannot change in this goal. Accept the risk, or open a goal for per-directory case detection.
- The other forward-slash prefix checks (lanes_cli.py, operate.py line 328, pool.py) are issue 5740. Not touched here.
- The fail-open read (an unreadable trust file answers "trusted") is issue 5741, its own security fix. Unchanged here.
- Accepted by the owner, with records o722 and o723: the Windows proof is simulated (Windows path functions on a POSIX host, never run on Windows, so the requirement's confidence is not raised), no Windows runner exists, and the refusal text is unchanged.
- The plan step's PENDING lines were marked AUTO-APPROVED by the tool; that is issue 5733 and those lines are not approvals. They were deferrals now resolved above.

Verify by hand is in this file: a person on a Windows machine binds a new goal under a trusted root and expects no folder-trust refusal.

Lane history for the earlier head ad8ddf1840d69e3fbeb25e920bae2e8efa037d42 (this pull request's head is later; its own lane lines are in the run record). Each lane ran in a fresh clone detached at the head, as a worker, with the session variables cleared; operation.id was the same four lines before and after each.
- qa lane: "LANE qa AFFECTED 16/16 in 900s", state pass. ship lane: "LANE ship AFFECTED 16/16 in 900s", state pass. Both stopped at the 15-minute budget with 16 of 635 selected rows run and 619 left to the scheduled full suite.
- First pr lane failed on readme-commands-in-command-map: "LANE pr AFFECTED 17/17 in 981s", then LANE_FAIL. The row printed 19 passing sub-checks and then "timed out after 105.5 seconds"; it and runbook-registry (a known-red row, #5343) were killed by SIGTERM (pids 73044 and 61953). Three lanes were running at once with 49 percent of memory free. Alone, at the same head, the row first died to SIGTERM after 277.7 s while other goals' toys were running (the same row passes on origin/main in 199.3 s under that load); on a quiet Mac (no lane, toy or regression run, checked with ps just before) it passed alone in 186.3 s.
- Second pr lane (quiet Mac) failed on hlt1-same-answer although the toy printed ALL PASS: "LANE pr AFFECTED 30/30 in 900s", then "LANE_FAIL hlt1-same-answer". Alone on the quiet Mac that row passed in 7.8 s at the head and 7.5 s on origin/main. The operation session files it as a flaky row.
- Third pr lane passed at that head: "LANE pr AFFECTED 16/16 in 900s", "ran 16 of 635 rows; LEFT 619 to the scheduled full suite", 14 passed, 2 known, 0 failed. ps at its start: 0 matching processes, 56 percent free. ps halfway not captured.
