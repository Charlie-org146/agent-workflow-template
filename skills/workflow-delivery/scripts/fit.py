#!/usr/bin/env python3
"""What a goal decides at freeze and reads later (DEL-5 to DEL-8): size, depth, budget, `goal.py set`, `queue`, the PR body and `fit.py owed`."""
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


def spent_tokens(run):
    value = run.get("tokens") if isinstance(run.get("tokens"), dict) else {}
    steps = [n for key, n in value.items() if key != "total" and isinstance(n, int) and not isinstance(n, bool)]
    if steps:
        return sum(steps)
    total = value.get("total")
    return total if isinstance(total, int) else 0


def tokens_text(run):
    value = run.get("tokens") if isinstance(run.get("tokens"), dict) else {}
    return "%s tokens" % format(spent_tokens(run), ",") if any(isinstance(n, int) and n for n in value.values()) else "tokens unread"


def active_minutes(state, at=None, cfg=None):
    try:
        return monitor("board_log", True).active_minutes(state, at, cfg)
    except Exception:
        return 0


def monitor(name, paths=False):
    path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "workflow-monitoring", "scripts", name + ".py")
    paths and sys.path.insert(0, os.path.dirname(path))
    spec = importlib.util.spec_from_file_location("fit_" + name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def budget_stop(slug, state, runs, cfg, at=None, save=None):
    seen = view(state, runs)
    held, source = budget(seen, cfg)
    if seen.get("eta") or seen.get("eta_extend"):
        auto, spent = monitor("auto", True), active_minutes(state, at, cfg)
        if auto.eta_over(seen, spent):
            save and auto.eta_wait(state, spent, save)
            sys.exit("REFUSED: %dm spent, past the ETA of %dm; no new step starts and the goal waits for the owner: ship now, extend "
                     "once, or defer. Fix: the operation session runs goal.py set %s --eta-choice ship|defer or --eta-extend N, "
                     "with --owner-record ID (ETA_PAST)" % (spent, auto.eta_minutes(seen), slug))
    for name, spent in (("minutes", active_minutes(state, at, cfg)),("tokens", spent_tokens(state))):
        if held[name] and spent >= held[name]:
            sys.exit("REFUSED: %d %s spent, at the %s budget of %d (%s); no new step starts. Fix: goal.py set %s --budget-%s N "
                     "--why ... from the operation session (BUDGET_%s)" % (spent, name, name.rstrip("s"), held[name], source, slug, name, name.upper()))


def run_saver(runs):
    def save(state, note):
        state.setdefault("log", []).append("%s %s" % (time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()), note))
        path = os.path.join(runs, state["slug"] + ".json")
        with open(path + ".tmp", "w") as handle:
            json.dump(state, handle, indent=2)
        os.replace(path + ".tmp", path)
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


def cmd_show(g, args):
    state = g.load(args.slug)
    state["resume_at"] = resume_at(state, g.guards.moved_since_plan(g, state))
    state["minutes"] = {"charged": active_minutes(state, None, g.config()), "wall": monitor("board_log", True).wall_minutes(state)}
    print(json.dumps(state, indent=2))


def keep(g, state, step, text):
    state.setdefault("verdicts", {})[step] = verdicts(text)
    if step == "plan":
        state["plan_head"] = g.git("rev-parse", "HEAD")


def nag(g, args):
    tool = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "workflow-docs", "scripts", "entry.py")
    if not os.path.exists(tool):
        return print("NOTE: entry.py is missing, so the template version was not checked. Fix: reinstall the skills", file=sys.stderr)
    seen = g.run([sys.executable, tool, "lag", "--new", args.slug, "--repo", g.root()])
    sys.stdout.write(seen.stdout)
    sys.stderr.write(seen.stderr)
    seen.returncode == 3 and sys.exit(2)


def bind_here(g, slug):
    tool = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "workflow-monitoring", "scripts", "sessions.py")
    if os.environ.get("CLAUDE_CODE_HOST_SESSION_ID") and os.path.exists(tool):
        done = g.run([sys.executable, tool, "bind", slug, "self"])
        print(done.stdout + done.stderr, end="")


def frozen_fields(g, args, lines, touches):
    bad = [t for t in touches if surface(t) is None]
    if bad:
        g.no("%s isn't a GitHub surface. Fix: one of github:%s" % (", ".join(bad), ", github:".join(SURFACES)))
    if says_bump(args.goal):
        print("WARN: the goal text says %s; the operation records it with goal.py set %s --bump %s --why ..." % (
            says_bump(args.goal), args.slug, says_bump(args.goal)))
    held = budget_of(g.config())
    return {"size": size_of(lines, touches, g.root()), "budget": held,
            "eta": monitor("auto", True).eta_new(g.root(), args.slug, lines, touches, held["minutes"], g.config()),
            "preflight": monitor("replan", True).preflight_new(g.root(), g.config(), held["minutes"], touches)}


def plan_ahead(state, runs, step):
    """The owner answered the pre-flight plan item 'approve ahead' (#4535): a pending plan takes the recommended answers."""
    return step == "plan" and view(state, runs).get("preflight_answers", {}).get("answers", {}).get("plan") == "approve ahead"


def eta_line(fields):
    eta = fields.get("eta") or {}
    return "%d active minutes (%s)" % (eta.get("minutes", 0), eta.get("basis", "none"))


def pr_open(g, state, base, info, body):
    for wait in (2, 5, 0):
        pushed = g.run(["git", "push", "-u", "origin", state["branch"]])
        if not pushed.returncode:
            break
        time.sleep(wait)
    if pushed.returncode:
        g.no("push failed:\n" + pushed.stderr)
    if info.get("state") == "OPEN":
        return info["url"]
    path = g.state_path(state["slug"]) + ".body"
    g.write(path, body)
    done = g.run(["gh", "pr", "create", "--base", base, "--head", state["branch"], "--title", state["goal"][:70], "--body-file", path], check=True)
    return done.stdout.strip().splitlines()[-1]


def pr_text(g, state):
    import guards, private, role
    base, cfg = g.base_ref(state), g.config()
    body = pr_body(g.read(g.goal_file(state["slug"])), view(state, g.state_dir()), cfg, role.setting_of(cfg),
                          "", regen_warnings(g.root(), base))
    found = private.scan(g.root(), base, {"pr-title": state["goal"][:70], "pr-body": body})
    stop = private.refusal(found, base) or private.cannot(g.root(), base)
    if stop:
        guards.refuse_no_try(state, stop[0], stop[1], stop[2], g.save)
    if found["state"] == "none":
        state.setdefault("log", []).append("%s %s" % (guards.now(), found["note"]))
    return body.replace("\n## Result\n", "\n## Result\n\n" + found["note"] + "\n", 1)


VERDICT = re.compile(r"^\W*VERDICT:\s*(.+?)\s*$", re.M)


def verdicts(text):
    return [" ".join(item.split())[:200] for item in VERDICT.findall(text or "")][:12]


def step_line(step, seen):
    flow = seen.get("flow") or {}
    tokens = (seen.get("tokens") or {}).get(step)
    line = "\n- %s: %s" % (step, flow.get(step, "not run"))
    if isinstance(tokens, int) and tokens:
        line += " (%s tokens)" % format(tokens, ",")
    for item in ((seen.get("verdicts") or {}).get(step) or []):
        line += "\n  - verdict: " + item
    return line


def regen_warnings(top, base):
    def git(*args):
        done = subprocess.run(["git"] + list(args), cwd=top, capture_output=True, text=True)
        return done.stdout if done.returncode == 0 else ""
    gone = [line for line in git("diff", "--name-only", "--diff-filter=D", "--no-renames", base + "...HEAD").splitlines() if line]
    scripts = [p for p in git("ls-files").splitlines() if p.endswith((".py", ".sh")) or p.startswith(".github/workflows/")]
    found = []
    for path in gone:
        named = git("grep", "-l", "-F", path, "--", *scripts).split() if scripts else []
        for script in named:
            found.append("WARN: %s names %s, which this goal deletes; it may write it back. Fix: update or delete %s in "
                         "this goal, or ask the operation session to widen touches" % (script, path, script))
    return found


def pr_body(goal_text, seen, cfg, setting, scan_note, warnings, base_note=""):
    depth, why = depth_for(setting, seen)
    held, source = budget(seen, cfg)
    parts = ["%dm" % held["minutes"] if held["minutes"] else "", "%s tokens" % format(held["tokens"], ",") if held["tokens"] else ""]
    body = goal_text + "\n## Result\n\nSkill flow:" + "".join(step_line(step, seen) for step in STEPS) + "\n"
    body += seen.get("pr_lane", "")
    body += "\nReview depth: %s (%s).\n" % (depth, why)
    body += "Budget: %s (%s); spent: %s.\n" % (", ".join(p for p in parts if p) or "none set", source, tokens_text(seen))
    body += scan_note + "\n"
    surfaces = [t for t in (seen.get("touches") or []) if t.startswith("github:")]
    if surfaces:
        body += "GitHub surfaces this goal changes: %s.\n" % ", ".join(surfaces)
    if base_note:
        body += base_note + "\n"
    if warnings:
        body += "\n" + "\n".join("- " + w for w in warnings) + "\n"
    return body


def off_rows(text):
    bad, un = re.findall(r"^FAIL (\S+)", text, re.M), re.findall(r"^UNPROVEN ([^\s:]+)", text, re.M)
    return un if un and not bad and set(un) <= set(re.findall(r"^SKIPPED (\S+)", text, re.M)) else []


def off_line(text):
    return "\nLANE_OWED %s: skipped on this platform and never seen failing" % ", ".join(off_rows(text))


def off_reply(lane_line):
    m = re.search(r"^LANE_OWED (.+?):", lane_line, re.M)
    return m and ("%s\nPENDING: waiting for off-platform proof of %s. On a Linux or Mac runner run regression.py red ID --break "
                  "CMD for each, then here regression.py red ID --off-platform --runner NAME --commit SHA; then answer go on\nSTEP: pending\n"
                  % (lane_line, m.group(1))) or ""


def pr_fail(g, state, head, line, ids):
    wait = off_reply(line)
    if wait:
        print(re.sub(r"answer go on\s*STEP: pending", "run pr again", wait).strip())
        return 1
    g.private.pr_result(g.root(), g.config()["base"], head, state["branch"], False)
    g.failed_try(state, "regression lane failed: " + (", ".join(ids) or line.splitlines()[-1][:200]), "build",
                 "fix the failing rows, commit, then run pr again")
    return 1


def main_here(g, args):
    gitdir, common = (os.path.realpath(g.git("rev-parse", flag)) for flag in ("--git-dir", "--git-common-dir"))
    if gitdir == common and os.path.isdir(os.path.join(common, "loop", "worktrees")):
        g.no("--here in the repo's main checkout would leave it on a loop branch. Fix: git worktree add -b loop/%s "
             "%s origin/main, then run goal.py new there" % (args.slug, os.path.join(common, "loop", "worktrees", args.slug).replace(os.sep, "/")))


def owed(root, text):
    try:
        mod = monitor("pool")
    except Exception:
        return []
    return mod.pr_owed(None, root, text)


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
