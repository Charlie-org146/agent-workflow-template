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
