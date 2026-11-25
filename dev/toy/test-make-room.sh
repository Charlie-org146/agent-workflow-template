#!/bin/bash
# reads: dev/toy/move-check.py dev/toy/move-manifest.json skills/workflow-delivery/scripts/ skills/workflow-release/scripts/
# The make-room goal (part A): goal, flow, lane and merge moved whole functions into goal_steps, flow_steps, lane_run and
# merge_steps. Runs the move check, six negative controls on a copy, the same-object proof in both import orders, a lone
# `python3 -E -s` run of each new module from another folder, the --help text and the refusal words of head against the base.
# usage: test-make-room.sh [DIR]
set -u
here=$(cd "$(dirname "$0")/../.." && pwd)
GITD=${MR_GIT:-$here}   # the repository the git commands run in (a row runs this toy from an archive of a pinned commit)
. "$here/dev/toy/reap.sh"
T=${1:-$(mktemp -d)}; rm -rf "${T:?}"; mkdir -p "$T"
export HOME="$T/home"; mkdir -p "$HOME"; export USERPROFILE="$HOME"
fails=0
ok() { echo "PASS: $1"; }
bad() { echo "FAIL: $1"; fails=$((fails + 1)); }
check() { if eval "$2" 2>/dev/null; then ok "$1"; else bad "$1"; echo "${out:-}" | head -3; fi; }
MC="python3 $here/dev/toy/move-check.py"
MAN="$here/dev/toy/move-manifest.json"
base=$(python3 -c "import json,sys;print(json.load(open(sys.argv[1]))['base'])" "$MAN")
# the historical commit may be missing in a shallow checkout: fetch it by sha, never go green without it
git -C "$GITD" cat-file -e "$base^{commit}" 2>/dev/null || git -C "$GITD" fetch -q origin "$base" 2>/dev/null
out=$(git -C "$GITD" cat-file -e "$base^{commit}" 2>&1)
check "the comparison base commit is present (fetched by sha if the checkout is shallow)" 'git -C "$GITD" cat-file -e "$base^{commit}"'
out=$($MC check 2>&1); rc=$?
check "move check: every moved function is ast- and text-identical to the base but for the _s. prefixes, no FAIL, no SKIP" '[ $rc = 0 ] && ! grep -q "^FAIL\|^SKIP" <<<"$out" && [ "$(grep -c "^PASS" <<<"$out")" -ge 60 ]'
check "move check: every prefix is listed by function and line" 'grep -q "^PREFIX goal_steps cmd_record line [0-9]*: _s\." <<<"$out" && grep -q "^PREFIX merge_steps base_moved line" <<<"$out"'
MOVES=(); while IFS= read -r line; do MOVES+=("$line"); done < <(python3 - "$MAN" <<'PY'
import json, os, sys
for m in json.load(open(sys.argv[1]))["moves"]:
    print(m["script"], m["module"], ",".join(m["functions"]))
PY
)
# negative controls: a copy of the eight files, one break each, the check must fail on exactly that proof
cp_tree() { rm -rf "$T/c"; for line in "${MOVES[@]}"; do set -- $line; mkdir -p "$T/c/$(dirname "$1")"; cp "$here/$1" "$T/c/$1"; cp "$here/$(dirname "$1")/$2.py" "$T/c/$(dirname "$1")/$2.py"; done; }
neg() { cp_tree; python3 - "$T/c/$2" "$3" "$4" <<'PY'
import sys
p, a, b = sys.argv[1:4]
s = open(p).read()
assert a in s, a
open(p, "w").write(s.replace(a, b, 1))
PY
  out=$($MC check --root "$T/c" 2>&1); rc=$?; want=$5; check "negative control: $1" '[ $rc = 1 ] && grep -q "$want" <<<"$out"'; }
G=skills/workflow-delivery/scripts
neg "one byte changed inside a moved body fails that function" $G/goal_steps.py "slug, step = args.slug, args.step" "slug, step = args.slug, args.step  " "^FAIL: goal.cmd_record moved"
neg "a dropped re-export fails the script" $G/goal.py "from goal_steps import cmd_record" "from goal_steps import cmd_pr, round_stop  #" "^FAIL: goal re-exports"
neg "a renamed moved function fails" $G/lane_run.py "def wait_for(" "def wait_for_x(" "^FAIL: lane: wait_for is not moved exactly once"
neg "a new string constant fails the constants proof" $G/flow_steps.py "return found.group(1).strip()" 'return found.group(1).strip() or "extra"' "^FAIL: flow and flow_steps hold the base"
neg "a non-header line in a new module fails the header proof" skills/workflow-release/scripts/merge_steps.py "def advance(" 'SIDE = 1


def advance(' "^FAIL: merge_steps: the header"
neg "a g. prefix instead of _s. fails the text proof" $G/goal_steps.py "_s.guards.waiting_gate" "g.guards.waiting_gate" "^FAIL: goal.cmd_record moved"
neg "a prefix the derive missed (a bare name left in a moved body) fails the unresolved-global proof" $G/goal_steps.py "_s.fit.keep(" "fit.keep(" "^FAIL: goal_steps.cmd_record has no unresolved global"
# the same objects whichever side is imported first, and each module alone from another folder with python -E -s
for line in "${MOVES[@]}"; do set -- $line; dir="$here/$(dirname "$1")"; stem=$(basename "$1" .py); funcs=$3
  for order in "$2 $stem" "$stem $2"; do
    out=$(cd "$dir" && python3 -c "
import importlib, sys
a, b = sys.argv[1].split()
importlib.import_module(a); importlib.import_module(b)
s, m = sys.modules['$stem'], sys.modules['$2']
assert all(getattr(s, f) is getattr(m, f) for f in '$funcs'.split(','))" "$order" 2>&1); rc=$?
    check "$stem: importing '$order' gives the same function objects" '[ $rc = 0 ]'
  done
  mkdir -p "$T/lone/$stem/scripts" "$T/elsewhere"; cp -R "$dir"/. "$T/lone/$stem/scripts/"
  out=$(cd "$T/elsewhere" && python3 -E -s "$T/lone/$stem/scripts/$2.py" --help 2>&1); rc=$?
  check "$2.py runs alone with python -E -s from another folder and prints nothing" '[ $rc = 0 ] && [ -z "$out" ]'
done
# the base tree, for the --help text and the refusal words
mkdir -p "$T/base" && git -C "$GITD" archive "$base" skills dev/toy/make.sh dev/toy/repo | tar -x -C "$T/base"
words() { # the exit code and the words of one command in a toy repo, the tree's path written as ROOT
  tree=$1; shift; r="$T/r$$"; rm -rf "$r"; mkdir -p "$r"; "$here/dev/toy/make.sh" "$r" >/dev/null 2>&1
  (cd "$r/repo" && LOOP_ROLE=${ROLE:-worker} timeout 120 python3 "$tree/$1" "${@:2}" 2>&1 < /dev/null; echo "exit $?") | sed "s#$tree#ROOT#g; s#$r#TOY#g"; }
for line in "${MOVES[@]}"; do set -- $line; rel=$1; stem=$(basename "$rel" .py)
  h=$(cd "$here/$(dirname "$rel")" && python3 "$stem.py" --help 2>&1 | sed "s#$here#ROOT#g"); b=$(cd "$T/base/$(dirname "$rel")" && python3 "$stem.py" --help 2>&1 | sed "s#$T/base#ROOT#g")
  out="$(diff <(echo "$b") <(echo "$h") | head -3)"
  check "$stem.py --help prints the same text as the base" '[ -n "$h" ] && [ "$h" = "$b" ]'
done
for cmd in "skills/workflow-delivery/scripts/goal.py record nosuch plan --file x" "skills/workflow-delivery/scripts/goal.py pr nosuch" "skills/workflow-delivery/scripts/flow.py nosuch plan" "skills/workflow-delivery/scripts/lane.py status nosuch qa" "skills/workflow-release/scripts/merge.py nosuch"; do
  set -- $cmd; hw=$(words "$here" "$@"); bw=$(words "$T/base" "$@")
  out="$(diff <(echo "$bw") <(echo "$hw") | head -3)"
  check "refusal words and exit code are the same on head and base: ${cmd#skills/*/scripts/}" '[ -n "$hw" ] && [ "$hw" = "$bw" ]'
done
words_h=$(ROLE=none words "$here" skills/workflow-delivery/scripts/flow.py nosuch plan); words_b=$(ROLE=none words "$T/base" skills/workflow-delivery/scripts/flow.py nosuch plan)
out="$(diff <(echo "$words_b") <(echo "$words_h") | head -3)"
check "the NOT_WORKER refusal (a step outside a worker) has the same words and exit code on head and base" '[ -n "$words_h" ] && [ "$words_h" = "$words_b" ] && grep -q "NOT_WORKER" <<<"$words_h"'
# an unhandled exception inside a moved function: the last traceback line (type and message) is the same on head and base
for line in "${MOVES[@]}"; do set -- $line; stem=$(basename "$1" .py); first=${3%%,*}
  last() { (cd "$1/$(dirname "$2")" && python3 -c "import $3 as m; m.$4(object())" 2>&1 | tail -1 | sed "s#$1#ROOT#g"); }
  hl=$(last "$here" "$1" "$stem" "$first"); bl=$(last "$T/base" "$1" "$stem" "$first")
  out="head: $hl base: $bl"
  check "$stem.$first: an unhandled exception ends in the same type and message on head and base, from inside the moved function" '[ -n "$hl" ] && [ "$hl" = "$bl" ] && ! grep -q "ModuleNotFoundError\|ImportError" <<<"$hl"'
done
for f in $(python3 - "$MAN" <<'PY'
import json, sys
for m in json.load(open(sys.argv[1]))["moves"]:
    print(m["script"], m["script"].rsplit("/", 1)[0] + "/" + m["module"] + ".py")
PY
); do out="$f $(wc -c < "$here/$f")"; check "$f is at most 13,000 bytes and under 20,480" '[ "$(wc -c < "$here/$f")" -le 13000 ]'; done
[ "$fails" = 0 ] && echo "ALL PASS" || { echo "$fails FAILED"; exit 1; }
