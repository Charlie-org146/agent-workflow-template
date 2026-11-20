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
# SET-2: two branches that each add a different public_origins entry merge with no conflict in the regenerated START.md; main's entry.py
# (it prints the whole list on one line) is the negative control and must conflict.
mkdir -p "$t/old"; git -C "$here" archive origin/main skills | tar -x -C "$t/old"
merge_two() {  # $1 = the entry.py that writes START.md, $2 = a name for the worktree
  local m="$t/$2"; git -C "$here" worktree add -q --detach "$m" HEAD || return 2
  ( cd "$m" && git config user.email t@example.test && git config user.name Toy
    add() { python3 -c "import json,sys; c=json.load(open('.loop/config.json')); l=c['public_origins']; l.insert(0, sys.argv[1]) if sys.argv[2] == 'top' else l.append(sys.argv[1]); open('.loop/config.json', 'w').write(json.dumps(c, indent=2, ensure_ascii=False) + '\n')" "$1" "$2"
      python3 "$3" write --repo "$m" >/dev/null 2>&1; git commit -qam "add $1"; }
    python3 "$1" write --repo "$m" >/dev/null 2>&1; git commit -qam base; git branch -q base
    git checkout -q -b one base; add https://one.example top "$1"
    git checkout -q -b two base; add https://two.example end "$1"
    git merge -q --no-edit one >/dev/null 2>&1 ) ; local rc=$?
  git -C "$m" merge --abort >/dev/null 2>&1; return $rc
}
merge_two "$entry" new && ok "two branches adding different public_origins entries merge with no conflict" || bad "the merge conflicts"
python3 "$entry" write --repo "$t/new" >/dev/null 2>&1; python3 "$entry" check --repo "$t/new" 2>&1 | tail -1 | grep -qx "ENTRY OK" && ok "the merged START.md regenerates and passes entry check" || bad "entry check fails after the merge"
merge_two "$t/old/skills/workflow-docs/scripts/entry.py" old && bad "negative control: main's entry.py merged cleanly" || ok "negative control: main's one-line list conflicts"
[ "$(tr -d '\r' < "$entry" | wc -c)" -le "$(git -C "$here" show origin/main:skills/workflow-docs/scripts/entry.py | tr -d '\r' | wc -c)" ] && ok "entry.py is no larger than main's" || bad "entry.py grew past main"
[ $fails -eq 0 ] && echo "ALL PASS"
