#!/bin/bash
# windows: ok
# reads: skills/workflow-docs/scripts/entry.py skills/workflow-docs/scripts/counting.py
# Test that entry.py renders START.md from the committed .loop/config.json when a local skip-worktree edit holds the file
# (DOC-1): in a linked worktree min_free_memory_gb 2.0 is set against the committed 3.0; write must show 3.0 and check must pass.
# Every worktree, identity write and fixture commit happens in this run's own clone of the checkout, under its temp folder;
# the checkout is only read, and the last two checks prove it.
# usage: test-entry-config.sh   (ENTRY=path overrides the entry.py under test)
set -u
unset LOOP_SESSION_TOOL LOOP_OPERATION_SESSION LOOP_BATCH
for v in ${!GIT_@}; do case $v in GIT_CONFIG_*|GIT_CEILING_DIRECTORIES) ;; *) unset "$v" ;; esac; done
here=$(cd "$(dirname "$0")/../.." && pwd)
entry=${ENTRY:-$here/skills/workflow-docs/scripts/entry.py}
die() { echo "FAIL: setup ($1)"; exit 1; }
t=$(mktemp -d) && [ -d "$t" ] || die "no temp folder"
trap 'rm -rf "$t"' EXIT
who="toy-$(basename "$t")"; mail="$who@example.test"  # only this run writes these
probe() {  # $1 = a repo: the name and email entries of its shared config, one per line; fails when git cannot read them
  local key out rc
  for key in user.name user.email; do
    out=$(git -C "$1" config --local --get-all "$key"); rc=$?
    [ $rc -le 1 ] || return 1  # 1 is "no such entry"
    [ -z "$out" ] || printf '%s\n' "$out" | sed "s/^/$key /"
  done
}
before=$(probe "$here") || die "the checkout's config cannot be read"
head=$(git -C "$here" rev-parse --verify -q 'HEAD^{commit}') || die "no HEAD commit"
# --no-local copies through git itself, so a repack of the shared object store while it runs cannot break it
git -c advice.detachedHead=false clone -q --no-local "$here" "$t/repo" || die "clone"
git -C "$t/repo" remote remove origin || die "clone origin"
git -C "$t/repo" worktree add -q --detach "$t/w" "$head" || die "worktree"
[ -n "${ENTRY:-}" ] && ENTRY=$(cd "$(dirname "$ENTRY")" && pwd)/$(basename "$ENTRY")
cd "$t/w" || die "cd"
git config user.email "$mail" && git config user.name "$who" || die "identity"
sed 's/"min_free_memory_gb": 3.0/"min_free_memory_gb": 2.0/' .loop/config.json > "$t/config.new" && mv "$t/config.new" .loop/config.json
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
mkdir -p "$t/src"; git -C "$here" archive origin/main skills | tar -x -C "$t/src"
merge_two() {  # $1 = the entry.py that writes START.md, $2 = a name for the worktree
  local m="$t/$2"; git -C "$t/repo" worktree add -q --detach "$m" "$head" || return 2
  ( cd "$m" || exit 3
    git config user.email "$mail" && git config user.name "$who" || exit 3
    add() { python3 -c "import json,sys; c=json.load(open('.loop/config.json')); l=c['public_origins']; l.insert(0, sys.argv[1]) if sys.argv[2] == 'top' else l.append(sys.argv[1]); open('.loop/config.json', 'w').write(json.dumps(c, indent=2, ensure_ascii=False) + '\n')" "$1" "$2"
      python3 "$3" write --repo "$m" >/dev/null 2>&1; git commit -qam "add $1" >/dev/null 2>&1 || exit 3; }
    python3 "$1" write --repo "$m" >/dev/null 2>&1; git commit -qam base >/dev/null 2>&1
    base=$(git rev-parse HEAD); add https://one.example top "$1"; one=$(git rev-parse HEAD)
    git checkout -q --detach "$base"; add https://two.example end "$1"
    [ "$one" != "$base" ] && [ "$(git rev-parse HEAD)" != "$base" ] || exit 3  # two real commits, or the merge proves nothing
    git merge -q --no-edit "$one" >/dev/null 2>&1 ) ; local rc=$?
  git -C "$m" merge --abort >/dev/null 2>&1; return $rc
}
merge_two "$entry" new; rc=$?
if [ $rc -eq 0 ]; then
  ok "two branches adding different public_origins entries merge with no conflict"
  python3 "$entry" write --repo "$t/new" >/dev/null 2>&1; python3 "$entry" check --repo "$t/new" 2>&1 | tail -1 | grep -qx "ENTRY OK" && ok "the merged START.md regenerates and passes entry check" || bad "entry check fails after the merge"
elif [ $rc -eq 3 ]; then bad "setup (fixture commit)"; else bad "the merge conflicts"; fi
merge_two "$t/src/skills/workflow-docs/scripts/entry.py" old; rc=$?
if [ $rc -eq 1 ]; then ok "negative control: main's one-line list conflicts"; elif [ $rc -eq 3 ]; then bad "setup (fixture commit)"; else bad "negative control: main's entry.py did not conflict"; fi
# Line 4: the checkout is as it was. Each probe also has to find this run's own entries in the clone, so a probe that sees
# nothing cannot pass. A message says only found or changed; it never prints a name or an address.
read=ok; after=$(probe "$here") || read=failed; cloned=$(probe "$t/repo") || read=failed
seen=found; printf '%s\n' "$cloned" | grep -qF "user.name $who" && printf '%s\n' "$cloned" | grep -qF "user.email $mail" || seen="not found"
there="not found"; printf '%s\n' "$after" | grep -qF "$who" && there=found
same=unchanged; [ "$before" = "$after" ] || same=changed
line="the checkout's config holds neither name nor email of this run"
if [ "$read" = ok ] && [ "$seen" = found ] && [ "$there" = "not found" ] && [ "$same" = unchanged ]; then ok "$line"
else bad "$line (git read: $read; this run's entries in the clone: $seen, in the checkout: $there; the checkout's name and email entries: $same)"; fi
leaf=$(basename "$t")
read=ok; mine=$(git -C "$here" worktree list --porcelain) || read=failed; theirs=$(git -C "$t/repo" worktree list --porcelain) || read=failed
seen=found; printf '%s\n' "$theirs" | grep -q "/$leaf/w\$" || seen="not found"  # the linked one: the clone's own path has the leaf too
there="not found"; printf '%s\n' "$mine" | grep -qF "/$leaf/" && there=found
line="no worktree of this run is registered in the checkout"
if [ "$read" = ok ] && [ "$seen" = found ] && [ "$there" = "not found" ]; then ok "$line"
else bad "$line (git read: $read; this run's worktrees in the clone: $seen, in the checkout: $there)"; fi
[ $fails -eq 0 ] && echo "ALL PASS"
