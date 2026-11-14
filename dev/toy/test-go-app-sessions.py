#!/usr/bin/env python3
# windows: ok
# reads: skills/workflow-monitoring/scripts/watch.py skills/workflow-monitoring/scripts/graph.py skills/workflow-monitoring/scripts/sessions.py
"""go-app-sessions (#4040): with `workers: app` in .loop/config.json, a goal that no app session took (sessions.assign says
False) stays queued and says it waits for sessions.py bind, and no background process is launched; without the setting
the background fallback is unchanged. watch.runs() skips run-folder files that are not goal records (a stray issues.json
list crashed it). Stand-ins replace the freeze, the session tool and the launch: no process, no network. usage: test-go-app-sessions.py"""
import json
import os
import sys
import tempfile

here = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(here, "..", "..", "skills", "workflow-monitoring", "scripts"))
os.environ["LOOP_ROLE"] = "worker"
import watch  # noqa: E402

failed = []


def check(ok, text):
    print(("PASS: " if ok else "FAIL: ") + text)
    if not ok:
        failed.append(text)


class Args:
    max = 0
    skill_dir = ""


def round_with(cfg):
    """(launches, saved states, the goal's state) for one start_round under cfg, with every outside call replaced."""
    launches, saved = [], []
    state = {"slug": "g", "goal": "g", "status": "queued", "worker": "background", "worktree": "/nowhere", "log": []}
    goal = {"slug": "g", "goal": "g"}
    watch.plan = lambda limit: ([goal], [])
    watch.taken = lambda: set()
    watch.freeze = lambda g, c: state
    watch.go_prompt = lambda *a: "prompt"
    watch.save = lambda s, note=None: saved.append(note)
    watch.launch = lambda s, prompt, c: launches.append(s["slug"])
    watch.sessions.assign = lambda s, prompt, c: False  # no session could be started or reached
    watch.sessions.HUNG.clear()
    watch.start_round(Args, cfg)
    return launches, saved, state


launches, saved, state = round_with({"workers": "app", "agent_command": ["claude", "-p"]})
check(not launches, "workers app: a goal no session took launches no background process")
check(state["worker"] == "app" and "sessions.py bind g" in state["worker_why"], "workers app: the goal says it waits for sessions.py bind")
check(state["status"] == "queued" and any("workers: app" in (n or "") for n in saved), "workers app: it stays queued and the wait is logged")
launches, saved, state = round_with({"agent_command": ["claude", "-p"]})
check(launches == ["g"], "no setting: the background fallback still launches the goal")
launches, saved, state = round_with({"workers": "background", "agent_command": ["claude", "-p"]})
check(launches == ["g"], "any other value of workers keeps the background fallback")

with tempfile.TemporaryDirectory() as folder:
    json.dump({"slug": "real", "status": "running"}, open(os.path.join(folder, "real.json"), "w"))
    json.dump([{"number": 1}], open(os.path.join(folder, "issues.json"), "w"))
    json.dump("text", open(os.path.join(folder, "word.json"), "w"))
    open(os.path.join(folder, "broken.json"), "w").write("{")
    watch.loop_dir = lambda name: folder
    watch.record_path = lambda slug: os.path.join(folder, slug + ".json")
    try:
        got = [s["slug"] for s in watch.runs()]
    except Exception as error:  # noqa: BLE001
        got = "raised %r" % error
    check(got == ["real"], "runs() skips a list, a string and broken JSON in the runs folder and keeps the goal (got %s)" % (got,))
sys.exit(1 if failed else 0)
