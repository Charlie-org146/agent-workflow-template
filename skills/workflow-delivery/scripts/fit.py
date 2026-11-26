#!/usr/bin/env python3
"""What a goal decides at freeze and reads later (DEL-5 to DEL-8): size, depth, budget, set, queue, the PR body, owed."""
import hashlib
import importlib.util
import json
import os
import re
import subprocess
import sys
import time

os.environ.update(GIT_TERMINAL_PROMPT="0", GH_PROMPT_DISABLED="1", GIT_EDITOR="true", GIT_ASKPASS="true", SSH_ASKPASS="true")

STEPS = ("idea", "plan", "review", "qa", "ship")
NOT_AREAS = ("docs/", ".loop/", "dev/toy/", "test/", "tests/")
SURFACES = ("wiki", "milestones", "projects", "releases", "labels", "issues")
SMALL_DONE = 3


def deadline(held):
    import lanekit  # lazy: other skills load fit.py by path, where lanekit is not importable
    if "markers" not in held:
        return held["started"] + held["limit"], "past its time limit of %ds" % held["limit"]
    began = lanekit.mtime(held["rc"] + ".started")
    if began:
        return began + lanekit.lane_limit(held)[0], "past its time limit of %ds (%s)" % lanekit.lane_limit(held)
    if held.get("prep_by"):  # before the first row the preparation budget rules
        return held["prep_by"], "past its preparation budget"
    at = held["started"]
    if os.path.exists(held["rc"] + ".queued"):
        at = max(at, lanekit.last_change(held.get("pool") or lanekit.lanes_dir()))
    return at + 4 * held["limit"], "queued or planning past %ds" % (4 * held["limit"])


def surface(path):
    if not path.startswith("github:"):
        return ""
    name = path[len("github:"):]
    return name if name in SURFACES else None


def area(path, top=None):
    clean = path.strip().strip("/")
    if not clean or surface(path) != "" or any((clean + "/").startswith(item) for item in NOT_AREAS):
        return None
    parts = clean.split("/")
    if len(parts) >= 2:
        return "/".join(parts[:2])
    return clean if top and os.path.isdir(os.path.join(top, clean)) else None


def size_of(done_lines, touches, top=None):
    count = len(done_lines)
    if not touches:
        return {"small": False, "why": "large: no touches declared"}
    if any(surface(t) not in ("", None) for t in touches):
        return {"small": False, "why": "large: it touches GitHub (%s)" % ", ".join(t for t in touches if t.startswith("github:"))}
    areas = sorted({a for a in (area(t, top) for t in touches) if a})
    small = count <= SMALL_DONE and len(areas) <= 1
    return {"small": small, "why": "%s: %d done line%s, %s" % (
        "small" if small else "large", count, "" if count == 1 else "s",
        "%d areas (%s)" % (len(areas), ", ".join(areas)) if len(areas) > 1 else "one area" if areas else "no code area")}


def sidecar(runs, slug):
    try:
        with open(os.path.join(runs, slug + ".extra.json")) as handle:
            found = json.load(handle)
    except (OSError, ValueError):
        return {}
    got = found.get("set") if isinstance(found, dict) else None
    return got if isinstance(got, dict) else {}


def view(state, runs=None):
    merged = dict(state or {})
    if runs and merged.get("slug"):
        merged.update(sidecar(runs, merged["slug"]))
    return merged


def depth_for(setting, seen):
    over = seen.get("depth_override")
    if isinstance(over, dict) and over.get("depth") in ("full", "condensed"):
        return over["depth"], "owner override: %s" % (over.get("why") or "set per goal")
    if setting != "condensed":
        return "full", "review_depth full holds every goal to full"
    size = seen.get("size") if isinstance(seen.get("size"), dict) else None
    if not size:
        return "full", "large: frozen before goals were sized"
    return ("condensed" if size.get("small") else "full"), size.get("why") or ""


def budget_of(cfg):
    def number(key):
        value = (cfg or {}).get(key)
        return value if isinstance(value, int) and not isinstance(value, bool) and value > 0 else 0
    return {"minutes": number("time_budget_minutes"), "tokens": number("token_budget")}


def budget(seen, cfg):
    held = seen.get("budget")
    if isinstance(held, dict):
        return {"minutes": int(held.get("minutes") or 0), "tokens": int(held.get("tokens") or 0)}, "the goal's budget"
    return budget_of(cfg), "the repo settings"


def tokens():
    import proctree
    return proctree


def spent_tokens(run, live=False):
    value = run.get("tokens") if isinstance(run.get("tokens"), dict) else {}
    tok = tokens()
    steps = [tok.fresh(n) for key, n in value.items() if key != "total"]
    total = value.get("total")
    return (sum(steps) if any(steps) else total if isinstance(total, int) else 0) + (tok.live(run) if live else 0)


def tokens_text(run):
    value = run.get("tokens") if isinstance(run.get("tokens"), dict) else {}
    return "%s tokens" % format(spent_tokens(run), ",") if any(tokens().fresh(n) for n in value.values()) else "tokens unread"


def active_minutes(state, at=None, cfg=None):
    try:
        return monitor("board_log", True).active_minutes(state, at, cfg)
    except Exception:
        return 0


def wall_minutes(state):
    try:
        return monitor("board_log", True).wall_minutes(state)
    except Exception:  # no workflow-monitoring beside this skill
        return 0


def monitor(name, paths=False):
    path = tool("workflow-monitoring", "scripts", name + ".py")
    paths and sys.path.insert(0, os.path.dirname(path))
    spec = importlib.util.spec_from_file_location("fit_" + name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def budget_stop(slug, state, runs, cfg, at=None, save=None):
    import dlf  # the rule moved there whole (DLF-1.2)
    try:
        import goal
        top = goal.root()
    except (SystemExit, Exception):
        top = ""
    return dlf.budget_stop(slug, state, runs, cfg, at, save, top)


def branch_diff(g):
    try:
        done = subprocess.run(["git", "diff", "origin/%s...HEAD" % (g.config().get("base") or "main")], cwd=g.root(), capture_output=True, text=True, timeout=60)
    except (OSError, subprocess.TimeoutExpired, SystemExit):
        return None
    return None if done.returncode else done.stdout


def breaks(g, state, left):
    import dlf
    slug = state["slug"]
    for i, b in enumerate(left):
        got = dlf.settle(g.root(), g.state_dir(), slug, "break", "b%dp%s%s" % (i + 1, b["principle"], hashlib.sha1(b["text"].encode()).hexdigest()[:6]), "red-team break of principle %s: %s" % (b["principle"], b["text"]),
                     "notify.py plan-accept %s %s --owner-record ID" % (slug, b["principle"]), "accept", paths=state.get("touches") or (), cls=b.get("class", ""), diff=branch_diff(g))
        if got[0] == "wait":
            return got[1]
    return ""


def run_saver(runs):
    def save(state, note):
        import goal
        goal.save(state, note)
    return save


def recorded(state, step):
    return str((state.get("flow") or {}).get(step, "")).startswith(("done", "skipped"))


def resume_at(state, moved=None):
    left = [step for step in STEPS if not recorded(state, step)]
    if not left:
        return "pr"
    if left[0] == "review" and recorded(state, "plan"):
        return "review" if moved else "build"
    return left[0]


def next_command(state, step):
    slug = state.get("slug", "SLUG")
    return {"pr": "goal.py pr %s" % slug, "build": "goal.py step %s build, then flow.py %s review" % (slug, slug)}.get(
        step, "flow.py %s %s" % (slug, step))


def again(state, step):
    later = list(STEPS[STEPS.index(step):])
    cleared = [s for s in later if s in (state.get("flow") or {})]
    for key in ("flow", "depth", "verdicts"):
        held = state.get(key)
        if isinstance(held, dict):
            for s in later:
                held.pop(s, None)
    return cleared


def says_bump(goal):
    found = re.search(r"\b(minor|major)\b", goal or "", re.I)
    return found.group(1).lower() if found else ""


SET_AFTER_RECORD = "SET_AFTER_RECORD"


def cmd_set(g, args):
    import guards
    guards.operation_only(g, "set", args.slug)
    state = g.load(args.slug)
    if not (args.depth or args.bump or args.budget_minutes is not None or args.budget_tokens is not None or args.eta_extend or args.eta_choice or getattr(args, "preflight", "")):
        g.no("nothing to set. Fix: give --depth, --bump, --budget-minutes, --budget-tokens, --eta-extend, --eta-choice or --preflight")
    why = " ".join(args.why.split())
    if args.depth and any(recorded(state, s) for s in ("plan", "review")):
        done = [s for s in ("review", "plan") if recorded(state, s)][-1]
        g.no("%s is already recorded, so a new depth wouldn't bind it; nothing changed. Fix: goal.py set first, then "
             "flow.py %s %s --again (%s)" % (done, args.slug, done, SET_AFTER_RECORD))
    if args.bump and state.get("release") in ("cut", "merged"):
        g.no("%s's release has started; nothing changed (%s)" % (args.slug, SET_AFTER_RECORD))
    runs = g.state_dir()
    if args.depth:
        guards.add_set(runs, args.slug, "depth_override", {"depth": args.depth, "why": why}, "set depth %s: %s" % (args.depth, why))
    if args.bump:
        guards.add_set(runs, args.slug, "bump", args.bump, "set bump %s: %s" % (args.bump, why))
    if args.budget_minutes is not None or args.budget_tokens is not None:
        held, _ = budget(view(state, runs), g.config())
        was = dict(held)
        if args.budget_minutes is not None:
            held["minutes"] = max(0, args.budget_minutes)
        if args.budget_tokens is not None:
            held["tokens"] = max(0, args.budget_tokens)
        if any(was[k] and (not held[k] or held[k] > was[k]) for k in was):
            held["record"] = monitor("auto", True).eta_record(g, args.owner_record, args.slug, "raising a budget")
        elif (view(state, runs).get("budget") or {}).get("record"):
            held["record"] = view(state, runs)["budget"]["record"]  # a lowering keeps the record that raised it: used once
        guards.add_set(runs, args.slug, "budget", held, "set budget %dm, %d tokens: %s" % (held["minutes"], held["tokens"], why))
    if args.eta_extend or args.eta_choice:
        args.eta_extend and args.eta_choice and g.no("give --eta-extend or --eta-choice, not both")
        monitor("auto", True).eta_set(g, args, state, why)
    getattr(args, "preflight", "") and monitor("replan", True).preflight_answer(g, args, state, why)
    print("SET %s: %s" % (args.slug, ", ".join(
        "%s=%s" % (k, v) for k, v in sidecar(runs, args.slug).items())))
    return 0


def cmd_queue(g, args):
    return monitor("batch").cmd_queue(g, args)


def cmd_adopt(g, args):
    return monitor("batch").cmd_adopt(g, args)


def keep(g, state, step, text):
    state.setdefault("verdicts", {})[step] = verdicts(text)
    if step == "plan":
        state["plan_head"] = g.git("rev-parse", "HEAD")


def tool(*parts):
    return os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", *parts)


VERDICT = re.compile(r"^\W*VERDICT:\s*(.+?)\s*$", re.M)


if os.path.dirname(os.path.abspath(__file__)) not in sys.path:
    sys.path.append(os.path.dirname(os.path.abspath(__file__)))
if __name__ in sys.modules:
    sys.modules.setdefault("fit", sys.modules[__name__])
from fit_budget import regen, nag, bind_here, frozen_fields, plan_ahead, eta_line, pr_open, pr_text, verdicts, step_line, regen_warnings, pr_body, off_rows, off_line, off_reply, pr_fail, main_here, owed, cmd_show  # noqa: E402,F401


if __name__ == "__main__":
    if len(sys.argv) == 3 and sys.argv[1] == "owed":
        top = subprocess.run(["git", "rev-parse", "--show-toplevel"], capture_output=True, text=True).stdout.strip()
        try:
            with open(os.path.join(top, ".loop", "goals", sys.argv[2] + ".md")) as handle:
                left = owed(top, handle.read())
        except OSError:
            print("REFUSED: no goal file for %s on this branch. Fix: run it from the goal's worktree (NO_GOAL_FILE)" % sys.argv[2])
            sys.exit(2)
        print("\n".join("OWED %s: no defect test seen failing and passing" % ref for ref in left) or "NONE OWED")
        sys.exit(1 if left else 0)
    print("usage: fit.py owed SLUG   the issues and findings a goal fixes that still lack a defect test")
    sys.exit(0 if sys.argv[1:] in ([], ["-h"], ["--help"]) else 2)
