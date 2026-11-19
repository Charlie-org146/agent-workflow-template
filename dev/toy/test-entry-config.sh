#!/bin/bash
# windows: ok
# reads: skills/workflow-docs/scripts/entry.py skills/workflow-docs/scripts/counting.py
# Test that entry.py renders START.md from the committed .loop/config.json when a local skip-worktree edit holds the file
# (DOC-1): in a linked worktree min_free_memory_gb 2.0 is set against the committed 3.0; write must show 3.0 and check must pass.
# usage: test-entry-config.sh   (ENTRY=path overrides the entry.py under test)
set -u
unset LOOP_SESSION_TOOL LOOP_OPERATION_SESSION LOOP_BATCH
here=$(cd "$(dirname "$0")/../.." && pwd)
entry=${ENTRY:-$here/skills/workflow-docs/scripts/entry.py}
t=$(mktemp -d); trap 'git -C "$here" worktree remove --force "$t/w" >/dev/null 2>&1; rm -rf "$t"' EXIT
git -C "$here" worktree add -q --detach "$t/w" HEAD || exit 1
[ -n "${ENTRY:-}" ] && ENTRY=$(cd "$(dirname "$ENTRY")" && pwd)/$(basename "$ENTRY")
cd "$t/w"; git config user.email t@example.test; git config user.name Toy
sed -i 's/"min_free_memory_gb": 3.0/"min_free_memory_gb": 2.0/' .loop/config.json
git update-index --skip-worktree .loop/config.json
grep -q '"min_free_memory_gb": 2.0' .loop/config.json || { echo "FAIL: setup"; exit 1; }
fails=0; ok() { echo "PASS: $1"; }; bad() { echo "FAIL: $1"; fails=$((fails + 1)); }
cd /; python3 "$entry" write --repo "$t/w" >/dev/null 2>&1
grep -q 'min_free_memory_gb` | 3.0 |' "$t/w/.loop/START.md" && ok "skip-worktree edit: START.md shows the committed 3.0" || bad "START.md shows the local edit"
python3 "$entry" check --repo "$t/w" 2>&1 | tail -1 | grep -qx "ENTRY OK" && ok "skip-worktree edit: entry check passes" || bad "entry check fails"
git -C "$t/w" update-index --no-skip-worktree .loop/config.json
python3 "$entry" write --repo "$t/w" >/dev/null 2>&1
grep -q 'min_free_memory_gb` | 2.0 |' "$t/w/.loop/START.md" && ok "negative control: an ordinary edit still renders" || bad "an ordinary edit is ignored"
[ "$(tr -d '\r' < "$entry" | wc -c)" -le "$(git -C "$here" show origin/main:skills/workflow-docs/scripts/entry.py | tr -d '\r' | wc -c)" ] && ok "entry.py is no larger than main's" || bad "entry.py grew past main"
[ $fails -eq 0 ] && echo "ALL PASS"
