#!/usr/bin/env python3
"""Hold one goal's record: done lines, flow steps, PR.

usage: goal.py <command> <slug> [options]

  new SLUG --here --goal TEXT --done LINE [--touches A,B] [--release R]
  queue SLUG --goal TEXT --done LINE [--touches A,B] [--depends-on A,B]
  step SLUG NAME [--note TEXT] [--tokens N]
  record SLUG STEP --file REPLY [--in-session] [--tokens N|unknown]
  pr SLUG
step, record, pr: workers only.
  wait SLUG --ask TEXT --words W [--words W]
  answer SLUG
  finding SLUG TEXT [--requirement ID]
  resume SLUG --why T [--by W]
  touches SLUG --add PATH --why T
  set SLUG [--depth D] [--bump B] [--budget-minutes N] [--budget-tokens N] [--eta-extend N] [--eta-choice ship|defer]
          [--owner-record ID] --why T
  show SLUG
"""
import argparse
import hashlib
import importlib.util
import json
import os
import re
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import lanekit, guards, fit, private, routing, dlf  # noqa: E402,E401
fcntl = lanekit.fcntl
import role
from proctree import FLOW, NO_FLOW, TEMPLATE, flow_set, outcap  # noqa: E402,F401

ME = sys.modules.setdefault("goal", sys.modules[__name__])
SKILLS = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..")
try:
    _spec = importlib.util.spec_from_file_location("pods_graph", os.path.join(SKILLS, "workflow-monitoring", "scripts", "graph.py"))
    pods = importlib.util.module_from_spec(_spec)
    _spec.loader.exec_module(pods)
except Exception:
    pods = None

os.environ["GIT_TERMINAL_PROMPT"] = "0"
if not sys.stdin or not sys.stdin.isatty():
    os.dup2(os.open(os.devnull, os.O_RDONLY), 0)

MAX_TRIES = 3
SLUG = re.compile(r"^[a-z0-9][a-z0-9-]{0,50}$")
def no(text):
    sys.exit("REFUSED: " + text)


def run(args, cwd=None, check=False):
    done = subprocess.run(args, cwd=cwd, capture_output=True, text=True)
    if check and done.returncode:
        no("%s: %s" % (" ".join(args), done.stderr.strip()))
    return done


def git(*args, check=True):
    return run(["git"] + list(args), check=check).stdout.strip()


def read(path):
    with open(path) as handle:
        return handle.read()


def write(path, text, mode="w"):
    with open(path, mode) as handle:
        handle.write(text)


now = guards.now


def state_dir():
    common = os.path.abspath(git("rev-parse", "--git-common-dir"))
    path = os.path.join(common, "loop", "runs")
    os.makedirs(path, exist_ok=True)
    return path


def state_path(slug):
    return os.path.join(state_dir(), slug + ".json")


SEEN = {}


def load(slug):
    try:
        state = json.loads(read(state_path(slug)))
    except OSError:
        no("no goal named %s. Fix: start it with new." % slug)
    SEEN[slug] = json.dumps(state)
    return state


def save(state, note=None):
    state["updated"] = now()
    if note:
        state.setdefault("log", []).append("%s %s" % (state["updated"], note))
    path, slug = state_path(state["slug"]), state["slug"]
    with open(path + ".lock", "w") as lock:
        fcntl.flock(lock, fcntl.LOCK_EX)
        try:
            disk = json.loads(read(path))
        except (OSError, ValueError):
            disk = {}
        was = json.loads(SEEN.get(slug, "{}"))
        merged = dict(disk, **{k: v for k, v in state.items() if k not in was or was[k] != v})
        merged = {k: v for k, v in merged.items() if k in state or k not in was}
        have = disk.get("log") or []
        merged["log"] = have + [line for line in state.get("log") or [] if line not in have]
        role.report(disk, merged, state["updated"])
        if merged.get("one_review") or os.path.exists(path[:-5] + ".decisions.jsonl"):
            pods.keep_stop(path, merged)
        temp = path + ".tmp"
        write(temp, json.dumps(merged, indent=2))
        os.replace(temp, path)
    state.clear()
    state.update(merged)
    SEEN[slug] = json.dumps(merged)


def root():
    return git("rev-parse", "--show-toplevel")


def config():
    path = os.path.join(root(), ".loop", "config.json")
    try:
        return json.loads(read(path))
    except (OSError, ValueError):
        no("no readable .loop/config.json. Fix: run workflow-setup and merge its branch.")


def goal_file(slug):
    return os.path.join(root(), ".loop", "goals", slug + ".md")


def done_lines(slug):
    try:
        return guards.done_lines(ME, root(), slug)
    except OSError:
        no("no goal file for %s here. Fix: run this from the goal's worktree." % slug)


def done_sha(lines):
    return hashlib.sha256("\n".join(lines).encode()).hexdigest()


def frozen(state):
    if done_sha(done_lines(state["slug"])) != state["done_sha"]:
        fail_stop(state, "The done lines changed after they were frozen. A wrong done line needs a new goal.")


def held(slug):
    state = load(slug)
    frozen(state)
    return state


def base_ref(state):
    base = config()["base"]
    if run(["git", "rev-parse", "--verify", "--quiet", "origin/" + base]).returncode == 0:
        return "origin/" + base
    return base


def fail_stop(state, text):
    guards.fail_stop(ME, state, text)


def failed_try(state, why, step="build", fix="fix it, then run the step again"):
    queue("free", state["slug"])
    guards.failed_try(ME, state, why, step, fix)


cmd_wait = lambda args: guards.cmd_wait(ME, args)
cmd_answer = lambda args: guards.cmd_answer(ME, args)
cmd_adopt = lambda args: fit.cmd_adopt(ME, args)
cmd_queue = lambda args: fit.cmd_queue(ME, args)
cmd_set = lambda args: fit.cmd_set(ME, args)
cmd_touches = lambda args: guards.cmd_touches(ME, args)


def valid(args):
    SLUG.match(args.slug) or no("bad slug. Fix: lowercase letters, digits and dashes.")
    args.done or no("no done lines. Fix: give at least one --done.")
    flow_set() or no(NO_FLOW)


def cmd_new(args):
    slug = args.slug
    if not args.here:
        no("one session governs. Fix: use workflow-monitoring go, or --here if no agent can run it.")
    valid(args)
    fit.main_here(ME, args)
    if os.path.exists(state_path(slug)):
        no("%s already exists. Fix: pick a new slug." % slug)
    cfg = config()
    review = fit.start_review()
    review.frozen_twice(root(), "HEAD", slug)
    fit.nag(ME, args)
    touches = [item.strip() for item in args.touches.split(",") if item.strip()]
    branch = "loop/" + slug
    current = git("branch", "--show-current")
    if current == cfg["base"]:
        git("switch", "-c", branch)
    elif current != branch:
        no("on branch %s. Fix: go to %s or %s first." % (current, cfg["base"], branch))
    lines = ["%d. %s" % (index, " ".join(line.split())) for index, line in enumerate(args.done, 1)]
    fields = fit.frozen_fields(ME, args, lines, touches)
    path = goal_file(slug)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    text = TEMPLATE.format(goal=" ".join(args.goal.split()), slug=slug,
                           touches=", ".join(touches) or "not declared", eta=fit.eta_line(fields), done="\n".join(lines))
    one = review.setting_at(root(), "HEAD")  # the committed setting, never the working copy's
    write(path, review.marked_text(text) if one else text)
    git("add", path)
    git("commit", "-m", "Goal: %s" % slug, "--", path)
    state = {"slug": slug, "goal": args.goal, "status": "running", "step": "idea", "tries": 0, "flow": {},
             "branch": branch, "worktree": root(), "touches": touches, "pid": None, "pr": "",
             "batch": bool(os.environ.get("LOOP_BATCH")), "done_sha": done_sha(lines),
             "release": args.release, "waiting": None, "finding": "", "log": []}
    state.update(fields)
    one and state.update(review.mark(state_dir(), slug, "goal.py new"))
    guards.stamp(state, "idea")
    pods and pods.stamp(state)
    save(state, "frozen %d done lines" % len(lines))
    print("FROZEN %s branch=%s step=idea" % (slug, branch))
    fit.bind_here(ME, slug)
    return 0


def revoked_stop(slug):
    """TSK-1.3: a revoked workaround restores the wait, enforced for step, record and pr: every revoked fix must have merged; a fix whose run
    record is absent, torn or of an odd shape counts as unmerged. Exit 3, never a traceback."""
    try:
        state = load(slug)
    except (OSError, ValueError, SystemExit):
        return  # an unknown or unreadable goal is the command's own refusal
    fixes = state.get("schedule_revoked_fixes") if isinstance(state, dict) else None
    for fix in fixes if isinstance(fixes, list) else []:
        try:
            merged = bool(pods and os.path.exists(state_path(fix)) and pods.merged(load(fix)))
        except (Exception, SystemExit):
            merged = False
        merged or sys.exit(print("REFUSED: %s waits for %s to merge: its workaround was revoked. Fix: let %s merge, then run this again (SCHED_REVOKED)" % (slug, fix, fix), file=sys.stderr) or 3)


def cmd_step(args):
    state = load(args.slug)
    fit.start_review().gate(state, root(), args.name)
    args.name == "build" and guards.plan_gate(ME, state)
    fit.budget_stop(args.slug, state, state_dir(), config(), save=save)
    state["step"] = args.name
    if args.tokens:
        fit.tokens().add(state, args.name, args.tokens)
    save(state, args.name + (": " + args.note if args.note else ""))
    print("STEP %s %s" % (args.slug, args.name))
    return 0


def next_step(state):
    left = [step for step in FLOW if step not in state.get("flow", {})]
    return "flow.py %s %s" % (state["slug"], left[0]) if left else "pr"


def nxt(args, state):
    return "NEXT: " + ("build, then " * (args.step == "plan")) + next_step(state)


def queue(op, *args):
    return pods.pr_queue(op, state_dir(), *args) if pods else ""


cmd_finding = lambda args: guards.cmd_finding(ME, args)
cmd_show = lambda args: fit.cmd_show(ME, args)


def cmd_resume(args):
    pods and pods.refuse(load(args.slug) or {})
    return guards.cmd_resume(ME, args)


def main():
    outcap("goal.py")
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = parser.add_subparsers(dest="command", required=True)
    def add(name, func, *options):
        item = sub.add_parser(name)
        item.add_argument("slug")
        item.set_defaults(func=func)
        for flag, kinds in options:
            item.add_argument(flag, **kinds)
    goal = (("--goal", {"required": True}), ("--done", {"action": "append", "default": []}),
            ("--touches", {"default": ""}), ("--release", {"default": ""}))
    add("new", cmd_new, *goal, ("--here", {"action": "store_true"}))
    add("queue", cmd_queue, *goal, ("--depends-on", {"default": ""}))
    add("adopt", cmd_adopt)
    add("recover", lambda args: fit.start_review().recover(ME, args))
    add("start-items", lambda args: fit.start_answer().cmd_items(ME, args), ("--file", {"required": True}))
    add("start-review", lambda args: fit.start_answer().cmd_show(ME, args))
    add("start", lambda args: fit.start_answer().cmd_start(ME, args), ("--owner-record", {"required": True}))
    add("finding-close", lambda args: fit.outcomes().cmd_close(ME, args), ("number", {"type": int}), ("--how", {"required": True, "choices": ("drop", "not-taken", "stop")}),
        ("--why", {"required": True}), ("--files", {"default": ""}))
    add("revert", lambda args: fit.reverts().cmd_revert(ME, args), ("number", {"type": int}), ("--met", {"default": ""}), ("--cannot", {"default": ""}))
    add("hold-clear", lambda args: fit.reverts().cmd_hold_clear(ME, args), ("number", {"type": int}), ("--commit", {"required": True}))
    add("decide", lambda args: fit.outcomes().cmd_decide(ME, args), ("--finding", {"required": True}), ("--class", {"dest": "cls", "required": True}), ("--files", {"default": ""}))
    add("step", cmd_step, ("name", {}), ("--note", {"default": ""}), ("--tokens", {"type": int, "default": 0}))
    add("record", cmd_record, ("step", {"choices": FLOW}), ("--file", {"required": True}), ("--in-session", {"action": "store_true"}),
        ("--tokens", {"default": ""}))
    add("wait", cmd_wait, ("--ask", {"required": True}), ("--words", {"action": "append", "required": True}))
    add("finding", cmd_finding, ("text", {}), ("--requirement", {"default": ""}))
    add("resume", cmd_resume, ("--why", {"required": True}), ("--by", {"default": "operation session"}))
    add("touches", cmd_touches, ("--add", {"required": True}), ("--why", {"required": True}))
    add("set", cmd_set, ("--depth", {"choices": ("full", "condensed")}), ("--bump", {"choices": ("minor", "major")}),
        ("--budget-minutes", {"type": int}), ("--budget-tokens", {"type": int}), ("--eta-extend", {"type": int}),
        ("--eta-choice", {"choices": ("ship", "defer")}), ("--preflight", {"default": ""}), ("--owner-record", {"default": ""}), ("--why", {"required": True}))
    for name, func in (("pr", cmd_pr), ("answer", cmd_answer), ("show", cmd_show)):
        add(name, func)
    args = parser.parse_args()
    if args.command in ("step", "record", "pr"):
        role.guard(args.command, args.slug)
        role.inbox(os.path.abspath(git("rev-parse", "--git-common-dir")), args.slug)
    args.command in ("step", "record", "pr") and revoked_stop(args.slug)
    return args.func(args)


add_tokens = routing.add_tokens


from goal_steps import cmd_record, cmd_pr, round_stop  # noqa: E402,F401


if __name__ == "__main__":
    sys.exit(main())
