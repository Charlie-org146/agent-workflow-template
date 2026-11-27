#!/bin/bash
# reads: skills/loop-files.md skills/workflow-setup/scripts/settings.py
# reads: skills/workflow-setup/scripts/setup.py skills/workflow-monitoring/scripts/graph.py
# reads: skills/workflow-delivery/scripts/flow.py
# Proves the settings: one table, both halves written by setup, parallel 0 unlimited, settings read fresh each run.
# No model is called. usage: test-settings.sh [DIR]
set -u
unset LOOP_SESSION_TOOL LOOP_OPERATION_SESSION  # a toy test never reaches a real session tool
unset LOOP_ROLE
here=$(cd "$(dirname "$0")/../.." && pwd)
. "$here/dev/toy/reap.sh"
T=${1:-$(mktemp -d)}; rm -rf "${T:?}"; mkdir -p "$T"
fails=0
ok() { echo "PASS: $1"; }
bad() { echo "FAIL: $1"; fails=$((fails + 1)); }
check() { if eval "$2"; then ok "$1"; else bad "$1"; fi; }
SET="python3 $here/skills/workflow-setup/scripts/settings.py"
"$here/dev/toy/make.sh" "$T" >/dev/null || exit 1
export HOME="$T/home"; mkdir -p "$HOME"; unset LOOP_FLOW LOOP_HEALTH
export USERPROFILE="$HOME"
ref=$($SET reference)
missing=""
for k in parallel cadence board_max_age checkin_every auto_approve auto_merge pr_bumps_version version_file routines regression_cron step_limit token_budget mend max_tries resume_on_limit base wiki_dir risky_paths command allowed_tools model steps overrides rules repos; do
  grep -q "^| \`$k\` | .* | .[A-Za-z0-9]" <<<"$ref" || missing="$missing $k"
done
check "the reference lists every repo and private setting with a default and a line" '[ -z "$missing" ]'
saved=$(sed -n '/^# Settings reference$/,$p' "$here/skills/loop-files.md")
check "the saved reference is the generated one" '[ "$ref" = "$saved" ]'
check "parallel 0 means unlimited and is the default" 'grep -q "^| .parallel. | .0. | Workers running at once; 0 means unlimited" <<<"$ref"'
check "the reference lists none of the four retired size keys (o988)" '! grep -qE "^\| .(criteria_max|max_regression_rows|health_script_bytes|health_skill_lines). \|" <<<"$ref"'
check "this repo commits parallel 0" '[ "$(python3 -c "import json;print(json.load(open(\"$here/.loop/config.json\"))[\"parallel\"])")" = 0 ]'

cd "$T/repo" || exit 1
python3 "$here/skills/workflow-setup/scripts/setup.py" >/dev/null || true  # a bare agent_command is a gap, not a refusal (exit 0)
all=$(python3 - <<PY
import json, sys
sys.path.insert(0, "$here/skills/workflow-setup/scripts")
import settings
c = json.load(open(".loop/config.json"))
print(all(k in c for k, *_ in settings.keys("repo")) and c["parallel"] == 0)
PY
)
check "setup writes none of the four retired size keys" '[ "$(python3 -c "import json;c=json.load(open(\".loop/config.json\"));print(any(k in c for k in (\"criteria_max\",\"max_regression_rows\",\"health_script_bytes\",\"health_skill_lines\")))")" = False ]'
check "setup writes every repo setting, parallel 0" '[ "$all" = True ]'
python3 - <<'PY'
import json
c = json.load(open(".loop/config.json")); c.update(criteria_max="many", max_regression_rows=3, health_script_bytes=2000, health_skill_lines=10)
json.dump(c, open(".loop/config.json", "w"))
PY
# d5a: a config still carrying the four retired keys (o988) loads; setup, health and docs ignore them with no finding and no refusal
fr=$(python3 "$here/skills/workflow-setup/scripts/settings.py" fill-repo --repo . 2>&1); frc=$?
hc=$(python3 "$here/skills/workflow-health/scripts/health.py" check 2>&1); hrc=$?
dc=$(python3 "$here/skills/workflow-docs/scripts/docs.py" check 2>&1)
check "a config carrying the four retired keys loads, and setup, health and docs run with no error" '[ $frc = 0 ] && [ $hrc != 2 ] && ! grep -qE "REFUSED|Traceback|criteria_max|max_regression_rows|health_script_bytes|health_skill_lines" <<<"$fr$hc$dc"'
# an adopted repo keeps the old _help line too: its START.md rows must not list a retired key as if it still capped anything (o988)
rows=$(python3 - "$here" <<'PY'
import json, sys
sys.path.insert(0, sys.argv[1] + "/skills/workflow-docs/scripts")
import entry
c = json.load(open(".loop/config.json")); c["_help"] = dict(c.get("_help") or {}, criteria_max="docs check and health fail a page over it")
print(" ".join(k for k, _, _ in entry.settings(c)))
PY
)
check "an adopted config with leftover retired keys and their old _help line gets no START.md row for any of them" '! grep -qwE "criteria_max|max_regression_rows|health_script_bytes|health_skill_lines" <<<"$rows" && grep -qw "max_suite_seconds" <<<"$rows"'
check "setup writes the private half outside the repo, owner only" '[ -f "$HOME/.workflow-loop/flow.json" ] && [ "$(stat -f %Lp "$HOME/.workflow-loop/flow.json" 2>/dev/null || stat -c %a "$HOME/.workflow-loop/flow.json")" = 600 ] && grep -q "_help" "$HOME/.workflow-loop/flow.json" && [ -f "$HOME/.workflow-loop/health.json" ] && [ -f "$HOME/.workflow-loop/repos" ] && ! git ls-files | grep -q flow.json'
python3 - <<'PY'
import json, os
p = os.path.expanduser("~/.workflow-loop/flow.json"); d = json.load(open(p)); d["limit"] = 99; json.dump(d, open(p, "w"))
PY
git switch -q main; git merge -q --no-edit workflow-setup
$SET fill-private >/dev/null
check "a value already set is kept" 'grep -q "\"limit\": 99" "$HOME/.workflow-loop/flow.json"'

# The effect of changing a setting: read fresh each run.
count() { python3 - "$here" <<'PY'
import json, sys
sys.path.insert(0, sys.argv[1] + "/skills/workflow-monitoring/scripts")
import graph
goals = [{"slug": s, "depends": []} for s in "abcd"]
start, held = graph.ready(goals, {}, graph.parallel_of(json.load(open(".loop/config.json"))))
print(len(start), len(held))
PY
}
setp() { python3 -c "
import json,sys
c=json.load(open('.loop/config.json'))
c.pop('parallel') if sys.argv[1]=='none' else c.update(parallel=int(sys.argv[1]))
json.dump(c,open('.loop/config.json','w'))" "$1"; }
setp 2; check "parallel 2 starts two of four" '[ "$(count)" = "2 2" ]'
setp 0; check "parallel 0 starts all four" '[ "$(count)" = "4 0" ]'
setp none; check "no parallel setting starts all four" '[ "$(count)" = "4 0" ]'
setp 1; check "parallel 1 starts one, read again on the next run" '[ "$(count)" = "1 3" ]'

# A step's overrides beat the flow's defaults.
cmd=$(python3 - "$here" <<'PY'
import sys
sys.path.insert(0, sys.argv[1] + "/skills/workflow-delivery/scripts")
import flow
spec = {"command": ["agent"], "model": "m1", "allowed_tools": ["Bash"], "overrides": {"qa": {"model": "m2"}}}
print(" ".join(flow.step_command(spec, "qa")), "|", " ".join(flow.step_command(spec, "plan")))
PY
)
check "a step override replaces the default model and tools stay" '[ "$cmd" = "agent --allowedTools=Bash --model=m2 | agent --allowedTools=Bash --model=m1" ]'

[ $fails -eq 0 ] && echo "ALL PASS" || { echo "$fails FAILED"; exit 1; }
