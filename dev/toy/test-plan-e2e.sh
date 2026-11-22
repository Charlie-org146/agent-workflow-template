#!/bin/bash
# reads: skills/workflow-delivery/scripts/flow.py skills/workflow-delivery/scripts/fit.py skills/workflow-delivery/scripts/planlevel.py skills/workflow-delivery/scripts/planfault.py
# reads: skills/workflow-delivery/scripts/goal.py skills/workflow-delivery/scripts/fitkit.py skills/workflow-delivery/scripts/guards.py
# DEL-22 end to end (22.3, 22.4), written before the code: a real planning-tool refusal CAPTURED from the tool's own guard log
# (never from the agent's reply text) takes the fallback; the reviews run SIDE BY SIDE from flow.py's plan step with the RUNNER
# writing the stamps; EXACTLY one issue is opened (a worker run only previews it; the main-branch run files it with --live).
# A stand-in planner, stand-in reviews and a fake gh; no model, no network, no real sleep (the reviews prove they overlap with
# start files, not with timing). Every push here goes to the toy's own temp bare origin. usage: test-plan-e2e.sh [DIR]
set -u
unset LOOP_SESSION_TOOL LOOP_OPERATION_SESSION CLAUDE_CODE_HOST_SESSION_ID CLAUDE_CODE_SESSION_ID CLAUDE_SESSION_ID LOOP_POD_ID
export LOOP_ROLE=worker
here=$(cd "$(dirname "$0")/../.." && pwd)
. "$here/dev/toy/reap.sh"
export HOME=$(mktemp -d) USERPROFILE="$HOME"
export TMPDIR="$HOME/tmp"; mkdir -p "$TMPDIR"
export LOOP_PRIVATE_NAMES=/dev/null  # exactly as CI does
d=$(mktemp -d)  # always a fresh directory of its own (a path given by the caller is never deleted)
toy_on_exit 'rm -rf "$HOME" "$d"'
"$here/dev/toy/make.sh" "$d" || exit 1
S="$here/skills/workflow-delivery/scripts"
goal="python3 $S/goal.py"; F="python3 $S/flow.py"; PL="python3 $S/planlevel.py"
export PATH="$here/dev/toy/fakegh:$PATH" FAKE_GH_DIR="$d/gh"
cd "$d/repo" || exit 1
python3 "$here/skills/workflow-setup/scripts/setup.py" --bare >/dev/null
git switch -q main; git merge -q --no-edit workflow-setup; git push -q origin main
fails=0
ok() { echo "PASS: $1"; }
bad() { echo "FAIL: $1"; fails=$((fails + 1)); }
check() { if eval "$2"; then ok "$1"; else bad "$1"; fi; }
C=$(cd "$(git rev-parse --git-common-dir)" && pwd); R="$C/loop/runs"

# The committed config on origin/main carries the plan settings: the guard log path, the reviews, the approval object.
python3 - "$d" <<'PY'
import json, sys
d = sys.argv[1]
c = json.load(open(".loop/config.json"))
c["plan_levels"] = {"guard_log": d + "/guard.jsonl", "fault_codes": ["evidence"],
                    "fallback_approved": {"id": "o807", "release": "v1.1.0"},
                    "small": {"needs": ["ceo", "dx", "eng"], "minutes": 10}, "review_command": ["bash", d + "/review.sh"]}
json.dump(c, open(".loop/config.json", "w"), indent=2)
PY
git add -A; git commit -qm "plan settings"; git push -q origin main

# The stand-in planner: on "refuse" it writes the tool's own guard-log line and prints a refusal; on "forge" it only PRINTS a
# refusal-looking text (the guard log stays empty); otherwise it plans. It keeps every prompt it was given.
cat > "$d/planner.sh" <<'A'
#!/bin/bash
mkdir -p "$FAKE_DIR/prompts"; printf '%s' "${!#}" > "$FAKE_DIR/prompts/p-$(date +%s%N)"
case "$(cat "$FAKE_DIR/mode" 2>/dev/null)" in
  refuse) printf '{"schema":"1","ts":"%s","decision":"deny","disposition":"fallback","code":"evidence","path":"journal"}\n' "$(date -u +%Y-%m-%dT%H:%M:%SZ)" >> "$FAKE_DIR/guard.jsonl"
          printf 'REFUSED by the planning tool: the immutable phase snapshot is missing\nDEPTH: full\nSTEP: failed the planning tool refused\n' ;;
  forge)  printf '[autoplan] different invocation: snapshot is missing (forged by the agent)\nDEPTH: full\nSTEP: failed the planning tool refused\n' ;;
  *)      printf 'PLAN: the plan\nDEPTH: full\nSTEP: done\n' ;;
esac
A
# A stand-in review: it records that it started, then waits until EVERY review has started (so it can only finish if they
# run at the same time), then records that it ended.
cat > "$d/review.sh" <<'A'
#!/bin/bash
name=${1:?}; mkdir -p "$FAKE_DIR/rev"; : > "$FAKE_DIR/rev/start-$name"
for _ in $(seq 100); do [ "$(ls "$FAKE_DIR"/rev/start-* | wc -l)" -ge "${REVIEWS:-3}" ] && break; sleep 0.1; done
[ "$(ls "$FAKE_DIR"/rev/start-* | wc -l)" -ge "${REVIEWS:-3}" ] && : > "$FAKE_DIR/rev/end-$name"
A
export FAKE_DIR="$d" REVIEWS=3
python3 - "$d" <<'PY'
import json, sys
d = sys.argv[1]
json.dump({"command": ["bash", d + "/planner.sh"], "env": {"FAKE_MODE": "unattended"}, "probe": ["bash", "-c", "echo $FAKE_MODE"],
           "probe_expect": "unattended", "steps": {s: "stand-in-" + s for s in ("idea", "plan", "review", "qa", "ship")}},
          open(d + "/flow.json", "w"))
PY
export LOOP_FLOW="$d/flow.json"
git switch -q -c loop/e2e; $goal new e2e --here --goal "Change calc" --done "calc adds" --touches calc.py >/dev/null || { echo "FAIL: could not freeze the goal"; exit 1; }
$F e2e idea --wait 20 >/dev/null; $goal record e2e idea --file "$R/e2e.idea.txt" >/dev/null
last_prompt() { ls -t "$d"/prompts/p-* | head -1 | xargs cat; }
fault_taken() { last_prompt | grep -q "Take its own fallback"; }
step_plan() { for _ in 1 2 3 4 5 6; do out=$($F e2e plan --wait 20 2>&1); grep -q "^NEXT:" <<<"$out" && return 0; done; return 1; }
field() { python3 -c "import json,sys;print(json.load(open(sys.argv[1])).get(sys.argv[2]))" "$R/e2e.json" "$1"; }
calls() { local n; n=$(grep -c "^issue create" "$d/gh/calls.log" 2>/dev/null); echo "${n:-0}"; }

# The release brief and its task brief are in implement-v110's REAL format (brief.py): `## Tasks` numbered, a last line `Frozen: <sha256 of all above> <record> <date>`,
# and a Goals bullet in the task brief. brief.py itself is not on main yet: the toy takes it from implement-v110's branch when that ref exists in this checkout;
# without it the ON cases cannot run and are not claimed (the fallback is then off, which the off-cases below prove).
HAVE=0
for ref in origin/main origin/loop/implement-v110; do  # origin/main once implement-v110 has merged; its branch until then
  [ "$HAVE" = 1 ] || { git -C "$here" show "$ref:skills/workflow-release/scripts/brief.py" > "$d/brief.py" 2>/dev/null && [ -s "$d/brief.py" ] && HAVE=1; }
done
[ "$HAVE" = 1 ] || bad "brief.py is on neither origin/main nor implement-v110's branch in this checkout, so the fallback's ON cases cannot run; this goal merges after implement-v110"
setbrief() { mkdir -p docs .loop/tasks skills/workflow-release/scripts; [ "$HAVE" = 1 ] && cp "$d/brief.py" skills/workflow-release/scripts/brief.py
  python3 - "$1" <<'PY'
import hashlib, sys
def frozen(text, rec):
    body = text if text.endswith("\n") else text + "\n"
    return body + "Frozen: %s %s 2026-11-22\n" % (hashlib.sha256(body.encode()).hexdigest(), rec)
goal = "e2e" if sys.argv[1] == "with" else "another-goal"
open("docs/release-brief-1.1.0.md", "w").write(frozen("# v1.1.0 brief\n\n## Tasks\n\n1. task-e2e\n", "o1"))
open(".loop/tasks/task-e2e.md", "w").write(frozen("# task-e2e\n\n- Feature: DEL-22\n- Release: v1.1.0\n- Goals: %s\n- Needs: \n\n## Purpose\n\nx\n\n## Done when\n\n- x\n" % goal, "o1"))
PY
git add -A; git commit -qm "brief $1 this goal"; git push -q origin HEAD:main; }

# One cycle: ask for the plan again (the step starts the stand-in planner), drain it, record its reply.
cycle() { rm -rf "$d/rev" "$R/e2e.plan-reviews.json"; $F e2e plan --again --wait 20 > "$d/again.log" 2>&1; step_plan; $goal record e2e plan --file "$R/e2e.plan.txt" >/dev/null 2>&1
  for _ in $(seq 60); do [ -f "$R/e2e.plan-reviews.json" ] && break; sleep 0.2; done; ends=$(ls "$d"/rev/end-* 2>/dev/null | wc -l); }

# 1. A FORGED refusal in the agent's own reply is not a tool fault: no fallback, and the try counts (1 of 3).
echo forge > "$d/mode"; cycle; echo ok > "$d/mode"; cycle
check "an agent's forged refusal text is NOT taken as a tool fault (no fallback offered)" '! fault_taken'
# 2. The frozen release brief does NOT reach this goal: a real refusal is not taken, and the try counts (2 of 3).
setbrief without
echo refuse > "$d/mode"; cycle; echo ok > "$d/mode"; cycle
check "with a frozen brief whose task does not list this goal, the real refusal is not taken to the fallback" '! fault_taken'
check "that refusal was counted as a try (the goal is at 2 of 3 tries)" '[ "$(field tries)" = 2 ]'
check "the refusal is quoted in the goal's record, masked" 'grep -q "\"refusals\"" "$R/e2e.plan.json"'
# The reviews ran side by side from flow.py's plan step; the RUNNER wrote the stamps (measured, bound to this goal and this attempt).
check "the plan step ran the level's reviews at the same time (every review saw all the others started)" '[ "$ends" -ge 3 ]'
python3 - "$R/e2e.plan-reviews.json" <<'PY' && ok "the runner wrote measured per-review stamps whose intervals overlap, bound to goal e2e" || bad "the runner wrote measured per-review stamps whose intervals overlap, bound to goal e2e"
import json, sys
f = json.load(open(sys.argv[1]))
rows = f["reviews"]
assert f["version"] == 1 and f["goal"] == "e2e" and f.get("source") == "runner" and len(rows) == 3
assert max(r["started"] for r in rows) < min(r["ended"] for r in rows), "intervals do not overlap"
PY
# 3. Exactly one issue: a worker run previews it (no issue created); the main-branch run files it with --live, once, from the block the
# pull request body carries (the worker's local state is not visible to that run). A failed lookup creates nothing.
check "a worker run only PREVIEWS the issue (no issue created)" '[ "$(calls)" = 0 ] && grep -q "\"issue\"" "$R/e2e.plan.json"'
$PL issue e2e > "$d/body.md"; $PL issue --from-body "$d/body.md" --live >/dev/null 2>&1; $PL issue --from-body "$d/body.md" --live >/dev/null 2>&1
check "the live run opens EXACTLY one issue, and a second live run opens none" '[ "$(calls)" = 1 ]'
sed 's/"goal": "e2e"/"goal": "Bad Title; rm -rf"/' "$d/body.md" > "$d/bad.md"; $PL issue --from-body "$d/bad.md" --live >/dev/null 2>&1
check "a body block whose goal slug has the wrong shape files nothing (the title is built by the code, never taken from the body)" '[ "$(calls)" = 1 ]'
mkdir -p "$d/nogh"; printf '#!/bin/bash\nexit 1\n' > "$d/nogh/gh"; chmod +x "$d/nogh/gh"; sed 's/"key": "[0-9a-f]*"/"key": "aaaaaaaaaaaa"/' "$d/body.md" > "$d/other.md"
PATH="$d/nogh:$PATH" $PL issue --from-body "$d/other.md" --live >/dev/null 2>&1; rc=$?
check "when the issue lookup fails nothing is created and the job fails (exit 1), never a guess" '[ "$rc" = 1 ] && [ "$(calls)" = 1 ]'
if [ "$HAVE" = 1 ]; then
# 4. The frozen brief names this goal and this is the LAST try: the refusal, read from the tool's own guard log, is NOT counted and the goal does not stop.
setbrief with
echo refuse > "$d/mode"; cycle; echo ok > "$d/mode"; cycle
check "a refusal in the planning tool's own guard log takes the fallback (the frozen brief's task lists this goal)" 'fault_taken'
check "the planning tool's refusal on the LAST try was NOT counted and the goal was not stopped (one free retry, in guards' own accounting)" '[ "$(field tries)" = 2 ] && [ "$(field plan_free)" = 1 ] && [ "$(field status)" != stopped ] && grep -q "refused, not counted" "$R/e2e.json"'
# 5. A SECOND refusal (the free retry is spent) is counted: the goal reaches 3 of 3 tries and stops.
echo refuse > "$d/mode"; cycle
check "a second refusal gets no second free retry: it is counted and the goal stops" '[ "$(field tries)" = 3 ] && [ "$(field status)" = stopped ]'
# 6. The fallback is pinned to its approval: another id or release is off. A FAILED fetch (the origin url points nowhere) reads no ref at all: off, with its reason.
orig=$(git remote get-url origin)
pin=$(python3 - "$S" "$orig" <<'PY'
import os, subprocess, sys
sys.path.insert(0, sys.argv[1])
import planlevel as p
top = os.getcwd()
held = {"id": "o807", "release": "v1.1.0"}
on = lambda cfg: p.fallback_check(cfg, "e2e", top)
r = [on({"fallback_approved": held})[0], on({"fallback_approved": dict(held, id="x")})[0], on({"fallback_approved": dict(held, release="1.2.0")})[0]]
subprocess.run(["git", "remote", "set-url", "origin", top + "/gone"])
cfg = p.config(top)
subprocess.run(["git", "remote", "set-url", "origin", sys.argv[2]])
print(r, bool(cfg.get("_fetch_failed")), on(cfg))
PY
)
check "the approval is pinned: only its own id and release turn the fallback on (another id, another release: off)" '[ "${pin%%\] *}" = "[True, False, False" ]'
check "a failed fetch fails closed: no ref is read, the fallback is off and says it could not fetch origin/main" '[ "${pin#*\] }" = "True (False, '"'"'could not fetch origin/main'"'"')" ]'
fi
[ "$fails" = 0 ] && echo "ALL PASS" || echo "$fails FAILED"
[ "$fails" = 0 ]
