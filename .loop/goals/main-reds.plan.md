# Plan: main-reds

Use the authorized condensed review. Keep the frozen done lines and one PR.

1. Run the named rows on this base and retain output. Reuse existing tests and helpers. Inspect already landed changes for #4660, #4695, #4683 and #4772; add defect links and mutation proof if they already work. Do not rewrite correct implementations.
2. Fix the duplicate issues.about definition collision (#4896): retain a distinct name for the pure savings subject normalizer and update all its one-argument callers, preserving the feature resolver. Repair out-of-date How-to and README fixtures against the current DOC-5/DOC-19 contract, without weakening checks.
3. Fix canonical requirement discovery in defects.defined (#4865), counting actual requirement definitions rather than How-to references. Add positive and negative fixture controls that still reject two real definitions. Run the consistency rule and its controls.
4. Apply the same no-terminal-prompt environment guard to routing.py that peer subprocess scripts use (#4901). The reported DEL-10 check is about GIT_TERMINAL_PROMPT, so preserve agent routing and process execution semantics. Prove the static check fails on the old source and passes with the guard.
5. Ignore routine logs under routines/logs in the normal Home guard (#4858), while strict mode still sees them. Preserve ordinary settings, arbitrary schedule entries and registry leak checks (#4683), plus legitimate concurrent lane tickets. Extend the safe fixture-only Home guard tests.
6. Verify update.commit already stops and waits for its git process tree on interruption (#4772). Exercise the real hook-signal row and mutation-proof its cleanup; fix only if it still fails. Preserve platform guards and index restoration.
7. Verify release_trouble optional-v headings and docs sync Backlog milestone selection (#4660/#4695) using existing test-release-heading.py and test-docs-sync.py. Record defect rows linked to those issues and prove the relevant mutation causes each to fail.
8. Assemble the toy SMTP credential from runtime pieces in test-machine.sh (#4758). Retain a dynamic output-leak check for the full value and a fixture regression that rejects a literal SMTP_PASSWORD assignment in source. Run machine-mailer.
9. Add defect rows for all nine issue links, seen red via regression.py red on committed HEAD with a real old-code reversion/mutation. A row may carry several links only where it proves each. Update owned known-red entries only if any exist. Keep script edits below 19000 bytes, package files at most 100; trim comments in changed scripts where needed. Existing unrelated size failures remain outside scope.
10. Fill Verify by hand, run affected tests, review diff, commit, run qa and ship through flow.py, merge origin/main, and create the PR only through goal.py pr. Stop with the required MERGE-REQUEST report. Respect the private-scan merge waiting condition and local skip-worktree configuration.

## Lane environment
Every lane command uses env -u CLAUDECODE -u CLAUDE_CODE_HOST_SESSION_ID -u CLAUDE_CODE_SESSION_ID -u CLAUDE_CODE_SESSION_ATTENDED -u CLAUDE_CODE_CHILD_SESSION. Wait for the lane to finish.

## Test mapping
- Done 1: test-rows.sh DEL-10; judge-key-old; doc19-item-missing; link-unread-never-pass; consistency controls and a fixture with canonical and How-to IDs.
- Done 2: test-home-guard.py guard with routine-log and strict negative controls; toys-no-leak-schedule; setup-refusal-writes-120 with the commit-hook interruption.
- Done 3: test-release-heading.py; sync-delta-posted; machine-mailer plus a static credential-literal check.
- All defect rows: regression.py red with restoration of old behavior; then green on clean committed HEAD. Never file or close unrelated GitHub issues.

## Risks and scope
The issues.about collision affects several callers; inspect all of them. Do not exclude genuine duplicate requirements. Home exclusions must not hide configuration leaks. Group cancellation must finish before rollback. Test fixtures must match required docs without weakening their negative controls. Existing tests can be slow; avoid repeating whole fixtures just to grep several rows. No new packaged script, no private list edits, no config commit, no unrelated PC-owned work. Files in another owner's area are changed only for these nine issues.

## Review
One independent design spec round completed without blocking findings. The independent lighter engineering review found no blockers; it confirmed the two affected savings callers, the prompt-environment guard, canonical-definition filtering, and existing partial fixes. The SMTP source check must participate in the defect row; preserve existing Backlog reuse and strict Home controls. No UI phase applies. Developer experience changes are limited to correcting existing failure reports and retaining current command contracts.
