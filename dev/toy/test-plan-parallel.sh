#!/bin/bash
# reads: skills/workflow-delivery/scripts/planlevel.py skills/workflow-delivery/scripts/planfault.py skills/workflow-delivery/scripts/fit.py
# DEL-22.3: a plan's reviews run SIDE BY SIDE and the plan is ready when the slowest finishes. The stand-in reviews each wait until EVERY review
# has started, so they can only finish if they ran together (no clock, no barrier timeout). The CONTROL runs the same reviews one at a time and
# none can finish. Per-review stamps are the runner's, bound to the goal; a stamps file for another goal, with a negative duration, or with more
# than 20 reviews is ignored; the per-goal prompt names the level's reviews. Own temp HOME; stand-ins only. usage: test-plan-parallel.sh
set -u
unset LOOP_SESSION_TOOL LOOP_OPERATION_SESSION CLAUDE_CODE_HOST_SESSION_ID CLAUDE_CODE_SESSION_ID CLAUDE_SESSION_ID LOOP_POD_ID
export LOOP_ROLE=worker
here=$(cd "$(dirname "$0")/../.." && pwd)
. "$here/dev/toy/reap.sh"
export HOME=$(mktemp -d) USERPROFILE="$HOME" LOOP_PRIVATE_NAMES=/dev/null
export TMPDIR="$HOME/tmp"; mkdir -p "$TMPDIR"
toy_on_exit 'rm -rf "$HOME"'
d="$HOME/repo"; mkdir -p "$d" && cd "$d" && git init -q -b main && git config user.email t@example.test && git config user.name Toy
: > f && git add -A && git commit -qm base; mkdir -p .git/loop/runs
cat > "$d/review.sh" <<'A'
#!/bin/bash
name=${1:?}; mkdir -p "$FAKE_DIR/rev"; : > "$FAKE_DIR/rev/start-$name"
for _ in $(seq "${WAITS:-100}"); do [ "$(ls "$FAKE_DIR"/rev/start-* | wc -l)" -ge "${REVIEWS:-3}" ] && break; sleep 0.1; done
[ "$(ls "$FAKE_DIR"/rev/start-* | wc -l)" -ge "${REVIEWS:-3}" ] && : > "$FAKE_DIR/rev/end-$name"
A
export FAKE_DIR="$d" REVIEWS=3 PLAN_SCRIPTS="$here/skills/workflow-delivery/scripts" REVIEW="$d/review.sh"
python3 - <<'PY'
import json, os, subprocess, sys, time
sys.path.insert(0, os.environ["PLAN_SCRIPTS"])
import planlevel

fails = []
def check(ok, text):
    print(("PASS: " if ok else "FAIL: ") + text)
    ok or fails.append(text)

d, runs = os.environ["FAKE_DIR"], os.path.join(os.getcwd(), ".git", "loop", "runs")
ends = lambda: len([n for n in os.listdir(d + "/rev") if n.startswith("end-")]) if os.path.isdir(d + "/rev") else 0
names = ["ceo", "dx", "eng"]
# the real runner: all three start at once, the plan is ready when the slowest ends
planlevel.run_reviews(names, ["bash", os.environ["REVIEW"]], "g", runs)
found = json.load(open(os.path.join(runs, "g.plan-reviews.json")))
rows = found["reviews"]
check(ends() == 3, "the runner started every review at once: all three saw the others start and finished")
check(max(r["started"] for r in rows) < min(r["ended"] for r in rows), "the three intervals overlap (the latest start is before the earliest end)")
check(found["ready"] == max(r["ended"] for r in rows) and found["source"] == "runner" and found["goal"] == "g", "ready is the slowest review's end; the stamps are the runner's and bound to the goal")
# the control: one at a time, no review ever sees the others, none finishes
subprocess.run(["rm", "-rf", d + "/rev"])
for n in names:
    subprocess.run(["bash", os.environ["REVIEW"], n], env=dict(os.environ, WAITS="5"))
check(ends() < 3, "control: the same reviews run ONE AT A TIME do not all finish (only the last one can see the others' starts), so the check tells side by side from serial")
# stamps are ignored when they are not this goal's, negative, or too many
def write(goal, rows, attempt="1"):
    json.dump({"version": 1, "goal": goal, "attempt": attempt, "source": "runner", "reviews": rows}, open(os.path.join(runs, "g.plan-reviews.json"), "w"))
good = [{"name": "eng", "started": 10.0, "ended": 20.0}]
planlevel.save("g", {"attempt": "1"})  # the attempt the current ask started
write("g", good)
check(planlevel.stamps_for("g")[1] == good, "stamps for this goal and this attempt are read")
write("g", good, attempt="0")
check(planlevel.stamps_for("g") == ("", []), "stamps from an EARLIER attempt (a stale file with its own ready field) are ignored")
write("other", good)
check(planlevel.stamps_for("g") == ("", []), "stamps bound to ANOTHER goal are ignored")
write("g", [{"name": "eng", "started": 20.0, "ended": 10.0}])
check(planlevel.stamps_for("g") == ("", []), "a negative duration is ignored")
write("g", [{"name": "r%d" % i, "started": 1.0, "ended": 2.0} for i in range(21)])
check(planlevel.stamps_for("g") == ("", []), "more than 20 reviews is ignored")
# the per-goal prompt names the level's reviews and orders them launched together
for level, want in (("small", ["eng"]), ("normal", ["ceo", "dx", "eng"]), ("large", ["ceo", "dx", "eng", "outside"])):
    check(planlevel.reviews_for({"plan": {"level": level}}, {}) == want, "level %s needs %s" % (level, ", ".join(want)))
check(planlevel.reviews_for({}, {}) == [], "a goal frozen before DEL-22 (no plan key) is ordered no review set: it keeps today's prompt")
check(planlevel.reviews_for({"plan": {"level": "large", "rule": "plan info unavailable: OSError"}}, {}) == ["ceo", "dx", "eng", "outside"], "a plan that could not be read is large: the whole set, never fewer")
json.dump({"slug": "g", "worker": "session", "plan": {"level": "normal", "rule": "x"}}, open(os.path.join(runs, "g.json"), "w"))
planlevel.config = lambda top=None: {}
text = planlevel.ask("g", "Review the design.")
check("launch all of them in one message as concurrent subagents" in text and all(n in text for n in ("ceo", "dx", "eng")), "the session prompt names the reviews and orders them launched together")
check("Take its own fallback" not in text, "control: with no refusal the prompt carries no fallback order")
# session plan: reviews stamp their own start and end; record() reads them as SELF-REPORTED; `ready` is a short scripted poll
import fit
import importlib
scripts = os.environ["PLAN_SCRIPTS"]
subprocess.run(["rm", "-f", os.path.join(runs, "s.plan.json")])
cli = lambda *a: subprocess.run([sys.executable, os.path.join(scripts, "planlevel.py")] + list(a), capture_output=True, text=True).stdout
planlevel.save("s", {"names": ["ceo", "eng"], "asked_at": time.time(), "attempt": "A1"})  # what the ask recorded: this attempt's reviews, start and id
check(cli("ready", "s").startswith("WAITING"), "before any review has ended, `ready` prints WAITING (a poll that returns at once)")
cli("stamp", "s", "ceo", "start")
cli("stamp", "s", "ceo", "end")
check(cli("ready", "s").startswith("WAITING"), "control: one of the two reviews has ended and the other has not even started: still WAITING (every named review is waited for)")
cli("stamp", "s", "eng", "start")
cli("stamp", "s", "eng", "end")
check(cli("ready", "s").startswith("READY"), "once EVERY review the ask named has ended, `ready` prints READY")
held = planlevel.sidecar("s")
held["asked_at"] = time.time() - 4000
planlevel.save("s", held)
check(subprocess.run([sys.executable, os.path.join(scripts, "planlevel.py"), "ready", "s"], capture_output=True, text=True).returncode == 0, "READY stays READY after the limit (the reviews did finish)")
planlevel.save("s2", {"names": ["ceo"], "asked_at": time.time() - 4000, "attempt": "B1"})
late = subprocess.run([sys.executable, os.path.join(scripts, "planlevel.py"), "ready", "s2"], capture_output=True, text=True)
check(late.returncode == 3 and late.stdout.startswith("WAITING (0 seconds left"), "a session plan's reviews that never ended: past the limit `ready` exits 3 (a deadline from the ask, not a wait that never ends)")
json.dump({"slug": "s", "worker": "session", "plan": {"level": "normal", "rule": "x"}}, open(os.path.join(runs, "s.json"), "w"))
planlevel.config = lambda top=None: {}
planlevel.ask("s", "base")
new_attempt = planlevel.sidecar("s").get("attempt")
check(new_attempt != "A1" and planlevel.sidecar("s").get("names") == ["ceo", "dx", "eng"] and planlevel.session_stamps("s") == {}, "a new ask (other reviews, the last attempt finished) is a NEW attempt: the old attempt's stamp files are ignored, so `ready` cannot report READY from them")
# an earlier attempt's stamp with an "ended" must not survive: a new `start` begins a fresh row, so `ready` cannot count it
json.dump({"review": "eng", "attempt": "OLD", "started": 1.0, "ended": 2.0}, open(os.path.join(runs, "s.stamp-eng.json"), "w"))
planlevel.save("s", dict(planlevel.sidecar("s"), attempt="NEW", names=["eng"], asked_at=time.time()))
cli("stamp", "s", "eng", "start")
row = json.load(open(os.path.join(runs, "s.stamp-eng.json")))
check(row["attempt"] == "NEW" and "ended" not in row, "a review that starts in a NEW attempt does not inherit the old attempt's 'ended' (it starts a fresh row)")
check(not cli("ready", "s").startswith("READY"), "so `ready` does not report READY from a stale 'ended'")
# stamp refuses names that are not shapes of a goal slug or a review name (no path out of the runs folder, no other goal's file)
before = set(os.listdir(runs))
cli("stamp", "../x", "eng", "start")
cli("stamp", "s", "../../evil", "start")
cli("stamp", "s", "Upper_Case", "start")
check(set(os.listdir(runs)) == before, "a slug or review name with '..', a slash, a capital or an underscore writes nothing")
check(planlevel.limits({"small": {"needs": ["Eng", "ok-name"]}})["small"]["needs"] == ["ok-name"] and "FIX plan_levels.small.needs" in "".join(planlevel.fixes({"small": {"needs": ["Eng"]}})), "a review named in a setting that could never stamp is left out and a FIX line says so")
os.remove(os.path.join(runs, "s.stamp-eng.json"))
planlevel.save("s", dict(planlevel.sidecar("s"), attempt=new_attempt, names=["ceo", "dx", "eng"], asked_at=time.time()))  # back to the attempt the ask made
# a re-render of an UNFINISHED attempt keeps its stamps: one review has started, the prompt is rendered again, nothing is wiped
cli("stamp", "s", "ceo", "start")
planlevel.ask("s", "base")
check(planlevel.sidecar("s").get("attempt") == new_attempt and "ceo" in planlevel.session_stamps("s"), "control: rendering the prompt AGAIN while the attempt is unfinished keeps its attempt and the stamp already written")
# reviews that stamp at the same moment lose nothing: one file per review, one writer each
import threading
def one_review(n):  # a review stamps its own start, then its own end; the three reviews do it at the same moment
    cli("stamp", "s", n, "start")
    cli("stamp", "s", n, "end")
ts = [threading.Thread(target=one_review, args=(n,)) for n in ("ceo", "dx", "eng")]
[t.start() for t in ts]
[t.join() for t in ts]
got = planlevel.session_stamps("s")
check(sorted(got) == ["ceo", "dx", "eng"] and all("started" in v and "ended" in v for v in got.values()), "three reviews stamping their start and end at the same moment from three processes: no stamp is lost and none crashes (one file per review, one writer each)")
# `ready --wait` waits INSIDE the script: a stamp that lands mid-wait ends it
subprocess.run(["rm", "-f"] + [os.path.join(runs, n) for n in os.listdir(runs) if n.startswith("s.stamp-")])
held = planlevel.sidecar("s")
held["names"], held["asked_at"] = ["ceo"], time.time()
planlevel.save("s", held)
cli("stamp", "s", "ceo", "start")
threading.Timer(1.5, lambda: cli("stamp", "s", "ceo", "end")).start()
t0 = time.time()
waited = cli("ready", "s", "--wait", "20")
check(waited.startswith("READY") and 1 <= time.time() - t0 < 15, "`ready s --wait 20` returned READY about 1.5 s in, when the stamp landed mid-wait (the wait is inside the script)")
planlevel.save("legacy", {"names": []})
check(cli("ready", "legacy").startswith("READY (no reviews"), "a goal frozen before DEL-22 (no reviews ordered) is READY at once, never a 30-minute wait")
# the runner path: a SECOND ask (the DEL-22.4 re-ask after a refusal) inside the limit must not accept the first attempt's finished plan-reviews.json
json.dump({"slug": "r", "worker": "session", "plan": {"level": "normal", "rule": "x"}}, open(os.path.join(runs, "r.json"), "w"))
planlevel.save("r", {"names": ["ceo", "dx", "eng"], "asked_at": time.time(), "attempt": "R1"})
json.dump({"version": 1, "goal": "r", "attempt": "R1", "source": "runner", "ready": 5.0, "reviews": [{"name": "eng", "started": 1.0, "ended": 5.0}]}, open(os.path.join(runs, "r.plan-reviews.json"), "w"))
check(planlevel.stamps_for("r")[1], "control: before the re-ask the finished runner file of attempt R1 is read for R1")
planlevel.ask("r", "base")
check(planlevel.sidecar("r").get("attempt") != "R1" and planlevel.stamps_for("r") == ("", []) and not cli("ready", "r").startswith("READY"), "a second ask after a FINISHED runner attempt starts a new attempt: the first attempt's plan-reviews.json is ignored and `ready` waits")
planlevel.save("s", {"names": ["ceo", "eng"], "asked_at": time.time(), "attempt": "A9"})
for n, a, b in (("ceo", 1.0, 2.0), ("eng", 1.0, 3.0)):
    json.dump({"review": n, "attempt": "A9", "started": a, "ended": b}, open(os.path.join(runs, "s.stamp-%s.json" % n), "w"))
class Board:
    def seconds_by_step(self, run, at):
        return {"plan": 60}
fit.monitor = lambda *a, **k: Board()
planlevel.config = lambda top=None: {}
planlevel.record("s", {"slug": "s", "plan": {"level": "normal", "rule": "r"}}, "plan")
rec = planlevel.sidecar("s")["record"]
check(sorted(r["name"] for r in rec["reviews"]) == ["ceo", "eng"] and all(r["source"] == "self-reported" for r in rec["reviews"]), "record() reads the session's stamps and labels them self-reported (not measured)")
planlevel.save("t", {"runner": 4242})
planlevel.config = lambda top=None: {}
planlevel.record("t", {"slug": "t", "plan": {"level": "normal", "rule": "r"}}, "plan")
check("did not finish" in planlevel.sidecar("t")["record"]["cause"], "a runner that wrote no stamps is recorded as 'reviews did not finish' with the pid, not as a bare unknown")
check("ready g --wait 240" in text and "per turn" in text and "never a longer wait" in text, "the session prompt names ONE scripted `ready --wait 240` per turn (the waiting is inside the script), never a longer wait")
# gate 10: a slug with '..' writes nothing ANYWHERE (the parent of runs too), and a 51-character slug (goal.py's longest) can stamp
loop = os.path.dirname(runs)
before_all = (set(os.listdir(runs)), set(os.listdir(loop)))
cli("stamp", "../x", "eng", "start")
cli("stamp", "..", "eng", "start")
check((set(os.listdir(runs)), set(os.listdir(loop))) == before_all, "a slug with '..' writes nothing in runs or in its parent (the old code wrote runs/../x.stamp-eng.json)")
long = "a" * 51
planlevel.save(long, {"names": ["eng"], "asked_at": time.time(), "attempt": "L1"})
cli("stamp", long, "eng", "start")
cli("stamp", long, "eng", "end")
check(cli("ready", long).startswith("READY"), "a goal slug of 51 characters (goal.py's longest) can stamp, so `ready` does not wait out the limit")
cli("stamp", "a" * 52, "eng", "start")
check(not os.path.exists(os.path.join(runs, "a" * 52 + ".stamp-eng.json")), "control: a 52-character slug (not a goal slug) is still refused")
# a late `end` of an OLD attempt: the new attempt has no start for it, so it is refused and ready does not count it
planlevel.save("late", {"names": ["eng"], "asked_at": time.time(), "attempt": "N2"})
out = subprocess.run([sys.executable, os.path.join(scripts, "planlevel.py"), "stamp", "late", "eng", "end"], capture_output=True, text=True)
check(out.returncode == 2 and "refused" in out.stdout and not os.path.exists(os.path.join(runs, "late.stamp-eng.json")), "an `end` with no `start` in this attempt is refused and writes no file")
check(not cli("ready", "late").startswith("READY"), "so `ready` cannot print READY from a late end of an earlier attempt")
cli("stamp", "late", "eng", "start")
cli("stamp", "late", "eng", "end")
check(cli("ready", "late").startswith("READY"), "control: a start then an end in the same attempt still gives READY")
# a plan record that is there but cannot be read is not READY
open(os.path.join(runs, "bad.plan.json"), "w").write("{not json")
badr = subprocess.run([sys.executable, os.path.join(scripts, "planlevel.py"), "ready", "bad"], capture_output=True, text=True)
check(badr.returncode == 3 and badr.stdout.startswith("NOT READY"), "a corrupt plan record prints NOT READY (exit 3), never 'no reviews were ordered'")
check(cli("ready", "never-asked").startswith("READY (no reviews"), "control: no plan record at all (a goal frozen before DEL-22) is still READY at once")
# a new attempt removes the old attempt's stamp files and ALL orphaned tmp files of this goal (the plan record's and the runner's, whatever the pid)
json.dump({"slug": "c", "worker": "session", "plan": {"level": "normal", "rule": "x"}}, open(os.path.join(runs, "c.json"), "w"))
for stale in ("c.stamp-eng.json", "c.plan.json.111.tmp", "c.plan-reviews.json.222.tmp", "other.plan-reviews.json.333.tmp"):
    open(os.path.join(runs, stale), "w").write("x")
planlevel.config = lambda top=None: {}
planlevel.ask("c", "base")
left = set(os.listdir(runs))
check(not ({"c.stamp-eng.json", "c.plan.json.111.tmp", "c.plan-reviews.json.222.tmp"} & left), "a new attempt removes the goal's old stamp file and both kinds of orphaned tmp file")
check("other.plan-reviews.json.333.tmp" in left, "control: another goal's tmp file is left alone")
# twelve runner PROCESSES for ONE goal at once: all finish, the stamps file is whole JSON, no tmp file is left
os.environ["REVIEWS"] = "1"
planlevel.save("twice", {"run": {"names": ["eng"], "command": ["bash", os.environ["REVIEW"]]}, "attempt": "T1"})
ps = [subprocess.Popen([sys.executable, os.path.join(scripts, "planlevel.py"), "run", "twice"], stderr=subprocess.PIPE) for _ in range(12)]
errs = [p.communicate()[1] for p in ps]
check([p.returncode for p in ps] == [0] * 12 and not any(errs), "all twelve runner processes exit 0 with no error (neither lost its tmp file to the other)")
whole = json.load(open(os.path.join(runs, "twice.plan-reviews.json")))
check(whole["goal"] == "twice" and len(whole["reviews"]) == 1 and not [n for n in os.listdir(runs) if n.startswith("twice.") and n.endswith(".tmp")], "two runners writing one goal's stamps at once leave one whole JSON file and no tmp file (each writes a tmp name of its own)")
# a readable but EMPTY plan record is also NOT READY (safe direction: never a false READY)
open(os.path.join(runs, "empty.plan.json"), "w").write("{}")
check(subprocess.run([sys.executable, os.path.join(scripts, "planlevel.py"), "ready", "empty"], capture_output=True, text=True).stdout.startswith("NOT READY"), "an empty {} plan record is NOT READY too, never READY")
# a leveled goal with no plan record, or one with content and no names, is NOT READY; no plan level at all stays READY
json.dump({"slug": "lv", "worker": "session", "plan": {"level": "normal", "rule": "x"}}, open(os.path.join(runs, "lv.json"), "w"))
check(cli("ready", "lv").startswith("NOT READY"), "a leveled goal with NO plan record is NOT READY (never 'no reviews were ordered')")
planlevel.save("lv", {"log_pos": 5})
check(cli("ready", "lv").startswith("NOT READY"), "a leveled goal whose record has content but no names is NOT READY")
json.dump({"slug": "old"}, open(os.path.join(runs, "old.json"), "w"))
check(cli("ready", "old").startswith("READY (no reviews"), "control: a goal with no plan level (frozen before DEL-22) and no record is READY at once")
# a review whose command FAILS is marked failed and `ready` does not call the plan READY
os.environ["REVIEWS"] = "1"
planlevel.save("bad1", {"names": ["eng"], "asked_at": time.time(), "attempt": "F1"})
planlevel.run_reviews(["eng"], ["bash", "-c", "exit 3"], "bad1", runs, "F1")
failed = subprocess.run([sys.executable, os.path.join(scripts, "planlevel.py"), "ready", "bad1"], capture_output=True, text=True)
check(failed.returncode == 3 and failed.stdout.startswith("NOT READY (review failed: eng"), "a review command that exits non-zero gets an end stamp but `ready` prints NOT READY naming it (exit 3), never READY")
planlevel.save("ok1", {"names": ["eng"], "asked_at": time.time(), "attempt": "F2"})
planlevel.run_reviews(["eng"], ["bash", "-c", "exit 0"], "ok1", runs, "F2")
check(cli("ready", "ok1").startswith("READY"), "control: the same run with a command that exits 0 is READY")
open(os.path.join(runs, "unr.json"), "w").write("{not json")
unr = subprocess.run([sys.executable, os.path.join(scripts, "planlevel.py"), "ready", "unr"], capture_output=True, text=True)
check(unr.returncode == 3 and unr.stdout.startswith("NOT READY"), "an unreadable run-state file is NOT READY (exit 3), never READY")
print("ALL PASS" if not fails else "%d FAILED" % len(fails))
sys.exit(1 if fails else 0)
PY
