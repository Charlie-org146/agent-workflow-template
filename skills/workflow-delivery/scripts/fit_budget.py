"""the regen, pull request and owed text of a goal"""
import json
import os
import re
import sys
import time


def regen(g, slug):
    # #5317
    if g.git("ls-files", ".loop/START.md"):
        g.run([sys.executable, _s.tool("workflow-docs", "scripts", "entry.py"), "write"])
        files = g.git("diff", "--name-only", "--", "CLAUDE.md", "AGENTS.md", ".loop/START.md").split()
        files and g.git("commit", "-m", "Regenerate START.md for " + slug, "--", *files)
    done = g.run([sys.executable, _s.tool("workflow-release", "scripts", "wiki.py"), "prepare", slug, "--commit"])
    done.returncode and print("NOTE: stale page: " + done.stdout)
    return g.git("rev-parse", "HEAD")


def nag(g, args):
    entry = _s.tool("workflow-docs", "scripts", "entry.py")
    if not os.path.exists(entry):
        return print("NOTE: entry.py is missing, so the template version was not checked. Fix: reinstall the skills", file=sys.stderr)
    seen = g.run([sys.executable, entry, "lag", "--new", args.slug, "--repo", g.root()])
    sys.stdout.write(seen.stdout)
    sys.stderr.write(seen.stderr)
    seen.returncode == 3 and sys.exit(2)


def bind_here(g, slug):
    bind = _s.tool("workflow-monitoring", "scripts", "sessions.py")
    if os.environ.get("CLAUDE_CODE_HOST_SESSION_ID") and os.path.exists(bind):
        done = g.run([sys.executable, bind, "bind", slug, "self"])
        print(done.stdout + done.stderr, end="")


def frozen_fields(g, args, lines, touches):
    bad = [t for t in touches if _s.surface(t) is None]
    if bad:
        g.no("%s isn't a GitHub surface. Fix: one of github:%s" % (", ".join(bad), ", github:".join(_s.SURFACES)))
    if _s.says_bump(args.goal):
        print("WARN: the goal text says %s; the operation records it with goal.py set %s --bump %s --why ..." % (
            _s.says_bump(args.goal), args.slug, _s.says_bump(args.goal)))
    held = _s.budget_of(g.config())
    return {"size": _s.size_of(lines, touches, g.root()), "budget": held,
            "eta": _s.monitor("auto", True).eta_new(g.root(), args.slug, lines, touches, held["minutes"], g.config()),
            "preflight": _s.monitor("replan", True).preflight_new(g.root(), g.config(), held["minutes"], touches)}


def plan_ahead(state, runs, step):
    return step == "plan" and _s.view(state, runs).get("preflight_answers", {}).get("answers", {}).get("plan") == "approve ahead"


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
    body = pr_body(g.read(g.goal_file(state["slug"])), _s.view(state, g.state_dir()), cfg, role.setting_of(cfg),
                          "", regen_warnings(g, base))
    found = private.scan(g.root(), base, {"pr-title": state["goal"][:70], "pr-body": body})
    stop = private.refusal(found, base) or private.cannot(g.root(), base)
    if stop:
        guards.refuse_no_try(state, stop[0], stop[1], stop[2], g.save)
    if found["state"] == "none":
        state.setdefault("log", []).append("%s %s" % (guards.now(), found["note"]))
    return body.replace("\n## Result\n", "\n## Result\n\n" + found["note"] + "\n", 1)


def verdicts(text):
    return [" ".join(item.split())[:200] for item in _s.VERDICT.findall(text or "")][:12]


def step_line(step, seen):
    flow = seen.get("flow") or {}
    spent = _s.tokens().fresh((seen.get("tokens") or {}).get(step))
    line = "\n- %s: %s" % (step, flow.get(step, "not run"))
    if spent:
        line += " (%s tokens)" % format(spent, ",")
    for item in ((seen.get("verdicts") or {}).get(step) or []):
        line += "\n  - verdict: " + item
    return line


def regen_warnings(g, base):
    git = lambda *args: g.git(*args, check=False)
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
    depth, why = _s.depth_for(setting, seen)
    held, source = _s.budget(seen, cfg)
    parts = ["%dm" % held["minutes"] if held["minutes"] else "", "%s tokens" % format(held["tokens"], ",") if held["tokens"] else ""]
    body = goal_text + "\n## Result\n\nSkill flow:" + "".join(step_line(step, seen) for step in _s.STEPS) + "\n"
    body += seen.get("pr_lane", "")
    body += "\nReview depth: %s (%s).\n" % (depth, why)
    body += "Budget: %s (%s); spent: %s.\n" % (", ".join(p for p in parts if p) or "none set", source, _s.tokens_text(seen))
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
        mod = _s.monitor("pool")
    except Exception:
        return []
    return mod.pr_owed(None, root, text)


def cmd_show(g, args):
    state = g.load(args.slug)
    state["resume_at"] = _s.resume_at(state, g.guards.moved_since_plan(g, state))
    state["minutes"] = {"charged": _s.active_minutes(state, None, g.config()), "wall": _s.wall_minutes(state)}
    for step, held in (state.get("tokens") or {}).items():  # first, so the output cap never cuts them
        if isinstance(held, dict):
            print("TOKENS %s: %s, %s calls, %s, peak context %s" % (step, ", ".join("%s %s" % (k, format(int(held.get(k) or 0), ",")) for k in (
                "input", "cache_read", "cache_write", "output", "reported") if held.get(k)), held.get("calls", 0), held.get("model") or "?",
                format(int(held.get("peak") or 0), ",")))
    print(json.dumps(state, indent=2))


import fit as _s  # noqa: E402
