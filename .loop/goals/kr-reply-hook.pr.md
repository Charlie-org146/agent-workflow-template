# kr-reply-hook: known-red rows reply-hook-blocks and reply-hook-checkin-123 cleared

Refs #4549 (reply-hook-blocks) and #4547 (reply-hook-checkin-123), the issues the known list names for these rows.

This file was written with the file tool, as the goal's instruction note o685 allows.

Both rows run the same toy, `dev/toy/test-reply-hook.sh`, and each reads a list of its PASS lines. On main the toy printed 7 FAIL lines, all about a reply "in the check-in layout": the layout fixture was stale, and one product check had a gap.

## Root cause 1 (toy): the "good" reply no longer met the check-in layout

`reply_hook.py check` grew two requirements after the toy's good reply was written (`board_status.check_view`):
- MON-5: a `Machine:` line before All sessions.
- MON-14: each repo block in Dependencies groups its goals under a release header (`-- <release> release ETA ... --`) and a feature line, and each goal line carries a marker, a time and a machine.

The toy's good reply had neither, so `check passes a reply in the check-in layout` failed, and so did the six PASS lines that start from that reply (Nothing needs you, headings ignoring case and count, a one-line fence, a Markdown-bold heading, the Stop hook letting a layout reply through, and `last_assistant_message`).

Fix: the fixture reply gets a Machine line and a release, feature and marker block in its Dependencies graph; the one-line-fence case now appends its fence after the new last graph line. No assertion changed, and every reply built from the good one is still derived from it.

## Root cause 2 (product): a reply with a Machine line and no headline passed

Once the fixture had a Machine line, the toy's existing check `check finds no headline line` went red. That was a real gap in `reply_hook.problems`: it reported a missing headline only when a section was the very first line, so a reply of Machine line then sections (no headline) passed. Seen red first, on the toy's own check, then fixed.

Fix: `problems` counts the lines before the first section that are not the Machine line or a last-activity line; none is "no headline line", more than one is "more than one line before the first section". The first-section-at-line-0 case is the same as none, so nothing else changes. `reply_hook.py` is 18,672 bytes (was 18,670).

## Proof
- `test-reply-hook.sh` ALL PASS (7 FAIL lines before).
- `regression.py run reply-hook-blocks` and `regression.py run reply-hook-checkin-123` each passed twice, outside any sandbox, with the session's CLAUDE, ANTHROPIC and LOOP variables unset.
- Both known lines are removed from `.loop/regression-known.tsv`.
- Nearest toys for the touched scripts: test-checkin-view.py, test-reply-repo-blocks.py, test-reply-deps.py, test-three-level.py, test-hook-count.py, test-hooks-once.py, test-blockers-first.py, test-token-diet.py and test-adoption-proof.py pass. `test-machine-status.py` fails the same three checks on main (two memory-floor cases and the Machine-and-pod-lines headline case); this goal does not touch it, and hrt-monitor's commit e7ec9da66 carries its toy fixes.

## Rows
Net rows: 0. No row was added, removed or changed; only the toy fixture, `reply_hook.py` and the known list changed.
