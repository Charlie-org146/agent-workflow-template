#!/bin/bash
# reads: dev/toy/move-check.py dev/toy/move-manifest.json skills/workflow-delivery/scripts/ skills/workflow-release/scripts/
# The make-room goal, part B: fit, role and routing moved whole functions into fit_budget, role_gate and routing_pick (the
# manifest entries that carry their own base). Runs the move check on them, its negative controls on a copy, the pin rule's
# controls, the same-object proof in both import orders, a lone `python3 -E -s` run of each new module, the --help text and
# the refusal words of head against the base, an exception call of every moved function, and the loader toy (the four
# loaders outside the touches exec fit.py and routing.py without registering them). Part A's one-time proof is pinned to its
# own commit: its rows read that commit, so this toy covers only the moves that carry a base of their own.
# usage: test-make-room.sh [DIR]
set -u
here=$(cd "$(dirname "$0")/../.." && pwd)
GITD=${MR_GIT:-$here}   # the repository the git commands run in (a row runs this toy from an archive of a pinned commit)
export MR_GIT="$GITD"
. "$here/dev/toy/reap.sh"
T=${1:-$(mktemp -d)}; rm -rf "${T:?}"; mkdir -p "$T"
export HOME="$T/home"; mkdir -p "$HOME"; export USERPROFILE="$HOME"
fails=0
ok() { echo "PASS: $1"; }
bad() { echo "FAIL: $1"; fails=$((fails + 1)); }
check() { if eval "$2" 2>/dev/null; then ok "$1"; else bad "$1"; echo "${out:-}" | head -3; fi; }
MC="python3 $here/dev/toy/move-check.py"
MAN="$here/dev/toy/move-manifest.json"
APIN=8680879cf3a0b19f21fcae4cddf79d3d2758766e   # part A's code commit: the pin of its own rows
MOVES=(); while IFS= read -r line; do MOVES+=("$line"); done < <(python3 - "$MAN" <<'PY'
import json, sys
for m in json.load(open(sys.argv[1]))["moves"]:
    if m.get("base"):
        print(m["script"], m["module"], ",".join(m["functions"]), m["base"])
PY
)
STEMS=$(for line in "${MOVES[@]}"; do set -- $line; basename "$1" .py; done | paste -sd, -)
FLOOR=$(python3 - "$MAN" <<'PY'
import json, sys
print(sum(3 * len(m["functions"]) + 9 for m in json.load(open(sys.argv[1]))["moves"] if m.get("base")))
PY
)
BASES=$(for line in "${MOVES[@]}"; do set -- $line; echo "$4"; done | sort -u)
# the historical commits may be missing in a shallow checkout: fetch each by sha, never go green without one
for b in $BASES $APIN $(python3 -c "import json,sys;print(json.load(open(sys.argv[1]))['base'])" "$MAN"); do
  git -C "$GITD" cat-file -e "$b^{commit}" 2>/dev/null || git -C "$GITD" fetch -q origin "$b" 2>/dev/null
  out=$(git -C "$GITD" cat-file -e "$b^{commit}" 2>&1)
  check "the comparison commit ${b:0:9} is present (fetched by sha if the checkout is shallow)" 'git -C "$GITD" cat-file -e "$b^{commit}"'
done
out=$($MC check --only "$STEMS" 2>&1); rc=$?
check "move check: every moved function is ast- and text-identical to the base but for the _s. prefixes, no FAIL, no SKIP" '[ $rc = 0 ] && ! grep -q "^FAIL\|^SKIP" <<<"$out" && [ "$(grep -c "^PASS" <<<"$out")" -ge "$FLOOR" ]'
check "move check: every prefix and every header line is listed by function and line" 'grep -q "^PREFIX role_gate recorded_gate line [0-9]*: _s\." <<<"$out" && grep -q "^PREFIX routing_pick cmd_build line" <<<"$out" && grep -q "^LINE fit path line" <<<"$out" && grep -q "^LINE fit guard line" <<<"$out" && grep -q "^LINE fit export line" <<<"$out" && grep -q "^LINE routing guard line" <<<"$out" && grep -q "^LINE role guard line" <<<"$out"'
# negative controls: a copy of B's files, one break each, the check must fail on exactly that proof
cp_tree() { rm -rf "$T/c"; for line in "${MOVES[@]}"; do set -- $line; mkdir -p "$T/c/$(dirname "$1")"; cp "$here/$1" "$T/c/$1"; cp "$here/$(dirname "$1")/$2.py" "$T/c/$(dirname "$1")/$2.py"; done; }
neg() { cp_tree; python3 - "$T/c/$2" "$3" "$4" <<'PY'
import sys
p, a, b = sys.argv[1:4]
s = open(p).read()
assert a in s, a
open(p, "w").write(s.replace(a, b, 1))
PY
  out=$($MC check --root "$T/c" --only "$STEMS" 2>&1); rc=$?; want=$5; check "negative control: $1" '[ $rc = 1 ] && grep -q "$want" <<<"$out"'; }
G=skills/workflow-delivery/scripts
PATHLINE=$'if os.path.dirname(os.path.abspath(__file__)) not in sys.path:\n    sys.path.append(os.path.dirname(os.path.abspath(__file__)))\n'
GUARD=$'if __name__ in sys.modules:\n    sys.modules.setdefault("fit", sys.modules[__name__])\n'
neg "one byte changed inside a moved body fails that function" $G/fit_budget.py '"Regenerate START.md for "' '"Regenerate START.md for  "' "^FAIL: fit.regen moved"
neg "a dropped re-export fails the script" $G/fit.py "from fit_budget import regen, " "from fit_budget import " "^FAIL: fit re-exports"
neg "a renamed moved function fails" $G/routing_pick.py "def ask(" "def ask_x(" "^FAIL: routing: ask is not moved exactly once"
neg "a new string constant fails the constants proof" $G/routing_pick.py 'return "", 1, str(why)' 'return "x", 1, str(why)' "^FAIL: routing and routing_pick hold the base"
neg "a non-header line in a new module fails the header proof" $G/role_gate.py "def recorded_gate(" $'SIDE = 1\n\n\ndef recorded_gate(' "^FAIL: role_gate: the header"
neg "a g. prefix instead of _s. fails the text proof" $G/routing_pick.py "_s.resolve(" "g.resolve(" "^FAIL: routing.cmd_build moved"
neg "a prefix the derive missed (a bare name left in a moved body) fails the unresolved-global proof" $G/role_gate.py "_s.goal_state(" "goal_state(" "^FAIL: role_gate.recorded_gate has no unresolved global"
neg "fit.py without its guarded registration fails the exact allowlist" $G/fit.py "$GUARD" "" "^FAIL: fit: the rest of the script is the base's plus exactly"
neg "fit.py without its path line fails the exact allowlist" $G/fit.py "$PATHLINE" "" "^FAIL: fit: the rest of the script is the base's plus exactly"
neg "role.py with a plain, unguarded registration fails the exact allowlist (it is guarded like fit.py and routing.py)" $G/role.py $'if __name__ in sys.modules:\n    sys.modules.setdefault("role", sys.modules[__name__])\n' $'sys.modules.setdefault("role", sys.modules[__name__])\n' "^FAIL: role: the rest of the script is the base's plus exactly"
neg "an import with an alias added to a new module fails the header proof (import sys as json)" $G/routing_pick.py $'import json\n' $'import json\nimport sys as json\n' "^FAIL: routing_pick: the header"
neg "a second definition of a moved name fails the header proof (a default that runs code)" $G/routing_pick.py "def usage(" $'def usage(profile, text=print(123)):\n    pass\n\n\ndef usage(' "^FAIL: routing_pick: the header"
out=$($MC check --only totally-missing 2>&1); rc=$?; check "negative control: --only with a stem that names no move fails (it cannot pass by checking nothing)" '[ $rc = 1 ] && grep -q "^FAIL: --only names no move" <<<"$out"'
neg "a second path line in routing.py (it has one already) fails the exact allowlist" $G/routing.py "import guards  # noqa" "${PATHLINE}import guards  # noqa" "^FAIL: routing: the rest of the script is the base's plus exactly"
# a stray statement in one of part A's scripts: the exact allowlist is tighter than part A's, never looser
rm -rf "$T/c2"; mkdir -p "$T/c2/$G"; cp "$here/$G/flow.py" "$here/$G/flow_steps.py" "$T/c2/$G/"
out=$($MC check --root "$T/c2" --only flow 2>&1); rc=$?; check "part A's flow entry passes on a copy of its two files" '[ $rc = 0 ]'
python3 - "$T/c2/$G/flow.py" <<'PY'
import sys
s = open(sys.argv[1]).read()
a = "from flow_steps import"
assert a in s
open(sys.argv[1], "w").write(s.replace(a, "STRAY = 1\n" + a, 1))
PY
out=$($MC check --root "$T/c2" --only flow 2>&1); rc=$?; check "negative control: a stray statement in a part A script fails the exact allowlist" '[ $rc = 1 ] && grep -q "^FAIL: flow: the rest of the script is the base" <<<"$out"'
# the pin rule and the manifest rules, on throwaway copies of dev/toy (move-check.py beside a manifest of their own): no env var
mc_copy() { # NAME PYTHON: a copy of dev/toy holding move-check.py and the manifest edited by PYTHON (m is the manifest, pin the part A pin)
  mkdir -p "$T/mc-$1/dev/toy"; cp "$here/dev/toy/move-check.py" "$T/mc-$1/dev/toy/"
  python3 - "$MAN" "$T/mc-$1/dev/toy/move-manifest.json" "$2" "$APIN" <<'PY'
import json, sys
m, pin = json.load(open(sys.argv[1])), sys.argv[4]
exec(sys.argv[3])
json.dump(m, open(sys.argv[2], "w"))
PY
}
mc_copy a $'for x in m["moves"]:\n    if x["module"] == "flow_steps":\n        x["module"] = "flow_steps_x"'
out=$(python3 "$T/mc-a/dev/toy/move-check.py" check --pin $APIN --only flow 2>&1); rc=$?
check "pin rule: one of part A's modules absent at part A's pin shows FAIL (no skip without a later own base)" '[ $rc = 1 ] && grep -q "^FAIL" <<<"$out" && ! grep -q "^SKIP" <<<"$out"'
out=$($MC check --pin $APIN --only fit 2>&1); rc=$?
check "pin rule: B's move under part A's pin prints SKIP, and a pinned run in which every selected move skipped FAILs: nothing was checked under this pin" '[ $rc = 1 ] && grep -q "^SKIP: fit: added after this pin" <<<"$out" && grep -q "^FAIL: nothing was checked under this pin" <<<"$out"'
out=$($MC check --pin $APIN 2>&1); rc=$?
check "pin rule: under part A's pin the full check passes: part A's moves are checked, B's three print SKIP, no FAIL" '[ $rc = 0 ] && [ "$(grep -c "^SKIP" <<<"$out")" = 3 ] && ! grep -q "^FAIL" <<<"$out"'
mc_copy c $'for x in m["moves"]:\n    if x["module"] == "fit_budget":\n        x["base"] = pin'
out=$(python3 "$T/mc-c/dev/toy/move-check.py" check --pin $APIN --only fit 2>&1); rc=$?
check "pin rule: the same move with a base at the pin does not skip: its absent module FAILs" '[ $rc = 1 ] && grep -q "^FAIL" <<<"$out" && ! grep -q "^SKIP" <<<"$out"'
mc_copy d 'm["moves"] = []'
out=$(python3 "$T/mc-d/dev/toy/move-check.py" check --pin $APIN 2>&1); rc=$?
check "negative control: a manifest with no moves fails with a named message (it cannot pass by checking nothing)" '[ $rc = 1 ] && grep -q "^FAIL: the manifest holds no moves" <<<"$out"'
mc_copy e 'del m["base"]'
out=$(python3 "$T/mc-e/dev/toy/move-check.py" check --only flow 2>&1); rc=$?
check "negative control: a move that names no base, with no base in the manifest either, fails with a named message" '[ $rc = 1 ] && grep -q "^FAIL: flow: the move names no base" <<<"$out"'
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
# the base trees (one per base), for the --help text, the refusal words, the exception calls and the loader toy
for b in $BASES; do mkdir -p "$T/base/${b:0:9}" && git -C "$GITD" archive "$b" skills dev/toy/make.sh dev/toy/repo | tar -x -C "$T/base/${b:0:9}"
  check "the base tree of ${b:0:9} was archived" '[ -f "$T/base/${b:0:9}/skills/workflow-delivery/scripts/fit.py" ]'; done
for line in "${MOVES[@]}"; do set -- $line; rel=$1; stem=$(basename "$rel" .py); bt="$T/base/${4:0:9}"
  h=$(cd "$here/$(dirname "$rel")" && python3 "$stem.py" --help 2>&1 | sed "s#$here#ROOT#g"); b=$(cd "$bt/$(dirname "$rel")" && python3 "$stem.py" --help 2>&1 | sed "s#$bt#ROOT#g")
  out="$(diff <(echo "$b") <(echo "$h") | head -3)"
  check "$stem.py --help prints the same text as the base" '[ -n "$h" ] && [ "$h" = "$b" ]'
done
BT="$T/base/$(echo $BASES | head -n1 | cut -c1-9)"
words() { # the exit code and the words of one command in a toy repo, the tree's path written as ROOT; KIND: plain|recorded|here|surface
  tree=$1; role=$2; kind=$3; shift 3; r="$T/r$$"; rm -rf "$r"; mkdir -p "$r"; "$here/dev/toy/make.sh" "$r" >/dev/null 2>&1
  cwd="$r/repo"; S="$tree/skills/workflow-delivery/scripts"
  case $kind in
    recorded|surface)
      (cd "$r/repo" && mkdir -p .loop && echo '{"base": "main"}' > .loop/config.json && git add -A && git commit -qm cfg && git push -q origin main) >/dev/null 2>&1
      slug=zz; [ $kind = surface ] && slug=zz2
      (cd "$r/repo" && git worktree add -q -b loop/$slug "$r/repo/.git/loop/worktrees/$slug" main) >/dev/null 2>&1; cwd="$r/repo/.git/loop/worktrees/$slug"
      if [ $kind = recorded ]; then
        (cd "$cwd" && LOOP_FLOW="$r/flow.json" LOOP_ROLE=worker python3 "$S/goal.py" new zz --here --goal g --touches skills --done "Given a, when b, then c.") >/dev/null 2>&1
        python3 - "$r/repo/.git/loop/runs/zz.json" <<'PY'
import json, sys
d = json.load(open(sys.argv[1])); d.setdefault("flow", {})["plan"] = "done: x"; json.dump(d, open(sys.argv[1], "w"))
PY
      fi;;
    here) mkdir -p "$r/repo/.git/loop/worktrees";;
  esac
  (cd "$cwd" && LOOP_FLOW="$r/flow.json" LOOP_ROLE=$role timeout 120 python3 "$tree/$1" "${@:2}" 2>&1 < /dev/null; echo "exit $?") | sed "s#$r#TOY#g; s#$tree#ROOT#g"; }
refuse() { # LABEL KIND ROLE MARKER SCRIPT ARGS: the same words and exit code on head and base, the marker in the words
  label=$1; kind=$2; role=$3; marker=$4; shift 4
  hw=$(words "$here" "$role" "$kind" "$@"); bw=$(words "$BT" "$role" "$kind" "$@")
  out="$(diff <(echo "$bw") <(echo "$hw") | head -3)"
  check "refusal words, exit code and marker are the same on head and base: $label" '[ -n "$hw" ] && [ "$hw" = "$bw" ] && grep -q "$marker" <<<"$hw"'
}
D=skills/workflow-delivery/scripts
refuse "fit.py owed, no goal file" plain worker "NO_GOAL_FILE" $D/fit.py owed nosuch
refuse "routing.py build, an unknown goal" plain worker "no goal named" $D/routing.py build nosuch
refuse "routing.py build outside a worker" plain none "NOT_WORKER" $D/routing.py build nosuch
refuse "flow.py plan on a goal whose state records plan (recorded_gate)" recorded worker "ALREADY_RECORDED" $D/flow.py zz plan
refuse "goal.py new --here in the repo's main checkout (main_here)" here worker "main checkout" $D/goal.py new zz --here --goal g --touches skills --done "Given a, when b, then c."
refuse "goal.py new with a touches entry that is no GitHub surface (frozen_fields)" surface worker "isn't a GitHub surface" $D/goal.py new zz2 --here --goal g --touches github:nosuch --done "Given a, when b, then c."
# an unhandled exception inside every moved function, called with its required arguments (each a stand-in that raises on first use):
# the last traceback line is the same on head and base, and the traceback holds the moved function's own frame
cat > "$T/exc.py" <<'PY'
import contextlib, importlib, inspect, io, sys, traceback
tree, stem, funcs = sys.argv[1], sys.argv[2], sys.argv[3].split(",")
sys.path.insert(0, tree)
mod = importlib.import_module(stem)


def boom(*a, **k):
    raise RuntimeError("boom")


class Boom:
    def __getattr__(self, name):
        raise RuntimeError("boom")
    __call__ = __iter__ = __getitem__ = __contains__ = __len__ = boom


for f in funcs:
    fn = getattr(mod, f)
    need = [p for p in inspect.signature(fn).parameters.values() if p.default is p.empty and p.kind in (p.POSITIONAL_ONLY, p.POSITIONAL_OR_KEYWORD)]
    try:
        with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
            got = fn(*[Boom() for _ in need])
        print("%s\treturned\t%s\tframe=1" % (f, repr(got)[:60]))
    except BaseException:
        tb = traceback.format_exc()
        print("%s\traised\t%s\tframe=%d" % (f, tb.strip().splitlines()[-1][:120], int(any(l.strip().endswith("in " + f) for l in tb.splitlines() if l.lstrip().startswith("File")))))
PY
for line in "${MOVES[@]}"; do set -- $line; stem=$(basename "$1" .py); dir="$(dirname "$1")"; bt="$T/base/${4:0:9}"
  hl=$(cd "$T/elsewhere" && timeout 300 python3 -E -s "$T/exc.py" "$here/$dir" "$stem" "$3" 2>&1); bl=$(cd "$T/elsewhere" && timeout 300 python3 -E -s "$T/exc.py" "$bt/$dir" "$stem" "$3" 2>&1)
  out="$(diff <(echo "$bl") <(echo "$hl") | head -3)"
  n=$(tr ',' '\n' <<<"$3" | wc -l | tr -d ' ')
  check "$stem: all $n moved functions end the same on head and base, each with its own frame in the traceback" '[ "$(wc -l <<<"$hl" | tr -d " ")" = "$n" ] && [ "$hl" = "$bl" ] && ! grep -q "frame=0\|ModuleNotFoundError\|ImportError" <<<"$hl"'
done
# the loader toy: the four loaders outside the touches (board_lines.py and mend.py load fit.py as "fit", autorelease.py as
# "delivery_fit", monitor.py loads routing.py as "routing"; role.py is loaded the same way in the toy: nothing loads it so today, but a
# registration without its guard would raise KeyError there) exec the file without registering it. Complete trees, one
# interpreter per load; the lazy import must succeed; every module imported lies inside its own tree
cat > "$T/lt.py" <<'PY'
import importlib.util, io, os, sys, contextlib
tree, name, rel = sys.argv[1:4]
path = os.path.join(tree, rel)
if rel.endswith("role.py"):
    sys.path.insert(0, tree)  # role.py imports its siblings at load time and puts no folder on the path itself
spec = importlib.util.spec_from_file_location(name, path)
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)
out = []
with contextlib.redirect_stdout(io.StringIO()):
    if rel.endswith("fit.py"):
        out += ["monitor:" + type(m.monitor("auto", True)).__name__, "budget:%r" % (m.budget_of({"token_budget": 5}),),
                "eta:" + m.eta_line({"eta": {"minutes": 3, "basis": "b"}}), "verdicts:%r" % (m.verdicts("VERDICT: a: b\nVERDICT: c: d"),),
                "owed:%r" % (m.owed(os.getcwd(), ""),)]
    elif rel.endswith("role.py"):
        out += ["after:%r" % (m.after("plan"),), "moved:%s" % all(callable(getattr(m, f)) for f in ("recorded_gate", "record", "over_caps", "requirement_gate"))]
    else:
        out += ["usage:%r" % (m.usage({"output": "claude-json"}, '{"result": "r", "usage": {"input_tokens": 1, "output_tokens": 2}}'),),
                "exe:%s" % (type(m.exe("python3")).__name__,)]
files = {n: getattr(x, "__file__", "") or "" for n, x in sys.modules.items() if n in ("fit", "fit_budget", "routing", "routing_pick", "role", "role_gate", "fit_auto", "fit_pool", name)}
tree = os.path.realpath(tree)
out.append("inside:%s" % all(os.path.realpath(p).startswith(tree) for p in files.values() if p))
print("\n".join(out))
print("extra:sibling:%s" % any(n in files for n in ("fit_budget", "routing_pick", "role_gate")))
PY
mkdir -p "$T/lt/head"; cp -R "$here/skills" "$T/lt/head/skills"; 
for pair in "fit fit.py" "delivery_fit fit.py" "routing routing.py" "role role.py" "delivery_role role.py"; do set -- $pair
  hl=$(cd "$T/elsewhere" && python3 -E -s "$T/lt.py" "$T/lt/head/skills/workflow-delivery/scripts" "$1" "$2" 2>&1); bl=$(cd "$T/elsewhere" && python3 -E -s "$T/lt.py" "$BT/skills/workflow-delivery/scripts" "$1" "$2" 2>&1)
  out="$(diff <(grep -v '^extra:' <<<"$bl") <(grep -v '^extra:' <<<"$hl") | head -4)"
  check "loader toy: $2 loaded as '$1' without registration gives the base's results, its lazy import works, every imported module lies in its tree, and the sibling module loaded" '[ "$(grep -v "^extra:" <<<"$hl")" = "$(grep -v "^extra:" <<<"$bl")" ] && grep -q "inside:True" <<<"$hl" && grep -q "^extra:sibling:True" <<<"$hl" && ! grep -q "Traceback\|Error" <<<"$hl" && { [ "$2" != fit.py ] || grep -q "^monitor:module" <<<"$hl"; }'
done
for f in $(python3 - "$MAN" <<'PY'
import json, sys
for m in json.load(open(sys.argv[1]))["moves"]:
    if m.get("base"):
        print(m["script"], m["script"].rsplit("/", 1)[0] + "/" + m["module"] + ".py")
PY
); do out="$f $(wc -c < "$here/$f")"; check "$f is at most 13,000 bytes and under 20,480" '[ "$(wc -c < "$here/$f")" -le 13000 ]'; done
check "move-check.py stays inside its byte budget (at most 18,500)" '[ "$(wc -c < "$here/dev/toy/move-check.py")" -le 18500 ]'
[ "$fails" = 0 ] && echo "ALL PASS" || { echo "$fails FAILED"; exit 1; }
