#!/bin/bash
# Proof of one governing process: two level 0 goals, started by one process, each built by a stand-in agent (a script) in
# its own worktree. It starts no real claude agent, so it needs no login, network or quota. gh is faked. usage: test-govern.sh [DIR]
set -u
unset LOOP_SESSION_TOOL LOOP_OPERATION_SESSION  # a toy test never reaches a real session tool
unset LOOP_ROLE  # these tests act as the operation session
here=$(cd "$(dirname "$0")/../.." && pwd)
. "$here/dev/toy/reap.sh"
T=${1:-$(mktemp -d)}; rm -rf "$T"; mkdir -p "$T";
W="python3 $here/skills/workflow-monitoring/scripts/watch.py"
M="python3 $here/skills/workflow-monitoring/scripts/monitor.py"
export PATH="$here/dev/toy/fakegh:$PATH" FAKE_GH_DIR="$T/gh"
"$here/dev/toy/make.sh" "$T" || exit 1
export LOOP_FLOW="$T/flow.json"
cd "$T/repo" || exit 1
h=$(mktemp -d); HOME=$h USERPROFILE=$h python3 "$here/skills/workflow-setup/scripts/setup.py" --bare >/dev/null  # its private settings go to a throwaway home
git switch -q main; git merge -q --ff-only workflow-setup
C=$(cd "$(git rev-parse --git-common-dir)" && pwd); export COMMON="$C"
# A stand-in agent (a script, as the other toys use), run in the goal's own worktree: it writes the module and its test,
# commits, opens the pull request through the faked gh and marks the goal done, as the real agent's flow ends.
cat > "$T/agent.sh" <<'A'
#!/bin/bash
prompt=${!#}
slug=$(grep -oE 'Slug: [a-z0-9-]+' <<<"$prompt" | head -1 | cut -d' ' -f2)
[ -n "$slug" ] || slug=$(grep -oE 'goal [a-z0-9-]+ in this git' <<<"$prompt" | head -1 | cut -d' ' -f2)
mod=${slug//-/_}
printf 'def f(values):\n    return sorted(values)[len(values) // 2]\n' > "$mod.py"
printf 'import %s\nassert %s.f([3, 1, 2]) == 2\n' "$mod" "$mod" > "test_$mod.py"
git add -A; git commit -qm "Add $mod"
gh pr create --title "Add $mod" --body "built by the stand-in agent" >/dev/null
python3 - "$COMMON/loop/runs/$slug.json" "$slug" <<'PY'
import json, sys
s = json.load(open(sys.argv[1])); s.update(status="done", step="release", pr="https://example.test/pull/" + sys.argv[2])
json.dump(s, open(sys.argv[1], "w"))
PY
A
python3 - "$T/agent.sh" <<'PY'
import json, sys
c = json.load(open(".loop/config.json"))
c["agent_command"] = ["bash", sys.argv[1]]
json.dump(c, open(".loop/config.json", "w"), indent=2)
PY
git commit -qam "Agent command"
# The origin is rebuilt from the fixture after that commit (no push): the same refs the push left, main only, and HEAD on main.
rm -rf "$T/origin.git"; git clone -q --bare --single-branch --branch main "$PWD" "$T/origin.git"
git fetch -q origin; git branch -q --set-upstream-to=origin/main main
fails=0
ok() { echo "PASS: $1"; }
bad() { echo "FAIL: $1"; fails=$((fails + 1)); }
field() { python3 -c "import json,sys;print(json.load(open(sys.argv[1])).get(sys.argv[2]))" "$C/loop/runs/$1.json" "$2"; }

head0=$(git rev-parse HEAD); files0=$(git ls-files -o --exclude-standard | sort | grep -v '^.loop/')
$W go "Add stats_a.py with median(values)" --done "stats_a.median([3, 1, 2]) returns 2, proved by test_stats_a.py" --touches "stats_a.py,test_stats_a.py" --slug stats-a --skill-dir "$here/skills"
$W go "Add stats_b.py with mode(values)" --done "stats_b.mode([1, 2, 2]) returns 2, proved by test_stats_b.py" --touches "stats_b.py,test_stats_b.py" --slug stats-b --skill-dir "$here/skills"
$W watch --interval 5 --skill-dir "$here/skills" | tee "$T/watch.out"
$M report

for s in stats-a stats-b; do
  [ "$(field $s status)" = done ] && ok "$s done" || bad "$s is $(field $s status)"
  [ "$(field $s level)" = None ] && ok "$s has no level" || bad "$s level"
  [ -n "$(field $s pr)" ] && [ "$(field $s pr)" != None ] && ok "$s has a pull request" || bad "$s pr"
  [ "$(field $s judge)" = None ] && ok "$s ran no judge" || bad "$s judged"
  [ -f "$C/loop/worktrees/$s/${s/-/_}.py" ] && ok "$s built in its own worktree" || bad "$s worktree"
done
[ "$(field stats-a worktree)" != "$(field stats-b worktree)" ] && ok "two worktrees" || bad "same worktree"
[ "$(git rev-parse HEAD)" = "$head0" ] && ok "governing checkout: no commit" || bad "governor committed"
[ ! -e stats_a.py ] && [ ! -e stats_b.py ] && [ -z "$(git status --porcelain -- '*.py')" ] && ok "governing checkout: no code" || bad "governor wrote code"
[ "$(grep -c '^pr create' "$FAKE_GH_DIR/calls.log")" = 2 ] && ok "two pull requests, each from its branch" || bad "pr count"
started=$(grep -c 'launched agent' "$T/watch.out"); echo "launched in watch output: $started (go launched them)"
[ "$fails" = 0 ] && echo "ALL PASS" || { echo "$fails FAILED"; exit 1; }
