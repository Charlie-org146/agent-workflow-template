"""the record step, its gates and the lane caps"""
import glob
import json
import os
import re
import shutil
import subprocess
import sys
os.environ.update(GIT_TERMINAL_PROMPT="0", GH_PROMPT_DISABLED="1", GIT_EDITOR="true", GIT_ASKPASS="true", SSH_ASKPASS="true")


def recorded_gate(args, runs, job):
    """A recorded step isn't rerun by accident (DEL-7); --again clears it and every later step, never tries or tokens."""
    record = os.path.join(runs, args.slug + ".json")
    import fit
    state = _s.goal_state(runs, args.slug)
    if not fit.recorded(state, args.step):
        return
    if not args.again:
        head = state.get("plan_head")
        at = fit.resume_at(state, (_s.git_out("rev-list", "--count", head + "..HEAD") if head else "") not in ("", "0"))
        print("REFUSED (no try used): %s is already recorded (%s). Fix: go on with %s, or rerun it on purpose with "
              "flow.py %s %s --again (ALREADY_RECORDED)" % (args.step, state["flow"][args.step], fit.next_command(state, at),
                                                              args.slug, args.step))
        sys.exit(2)
    if os.path.exists(job) and _s.alive(json.load(open(job)).get("pid") or 0):
        sys.exit("REFUSED (no try used): %s is still running; let it end first (ALREADY_RECORDED)" % args.step)
    cleared = fit.again(state, args.step)
    for step in cleared:
        for end in (".ran", ".asked"):
            path = os.path.join(runs, "%s.%s%s" % (args.slug, step, end))
            if os.path.exists(path):
                os.remove(path)
    state.setdefault("log", []).append("%s rerun %s on purpose: cleared %s" % (_s.now(), args.step, ", ".join(cleared)))
    _s.save(record, state)
    print("AGAIN %s: cleared %s" % (args.step, ", ".join(cleared)))


def over_caps():
    """TEST_CAPS when the full suite is over max_suite_seconds (the base branch's) and this goal adds rows net; else None."""
    top = _s.git_out("rev-parse", "--show-toplevel")
    at = "origin/" + (json.loads(_s.git_out("show", "HEAD:.loop/config.json") or "{}").get("base") or "main")

    def ids(text):
        return {x.split("\t")[0] for x in text.splitlines() if "\t" in x and x[0] != "#"}
    try:
        now = ids(open(os.path.join(top, ".loop", "regression.tsv")).read())
        cfg = json.loads(_s.git_out("show", at + ":.loop/config.json"))
    except (OSError, ValueError):
        return None
    old = ids(_s.git_out("show", at + ":.loop/regression.tsv"))
    net = len(now - old) - len(old - now)
    tests = os.path.join(_s.git_out("rev-parse", "--git-common-dir"), "loop", "tests", "*.json")
    secs = max([d.get("total_seconds") or 0 for d in (json.load(open(f)) for f in glob.glob(tests)) if "--reuse" not in str(d.get("command"))] + [0])
    most = cfg.get("max_suite_seconds", 1900)
    if net > 0 and 0 < most < secs:
        return ("over the test cap (the full suite takes %d s, max_suite_seconds is %d) and this goal adds %d rows net (+%d, -%d)"
                % (secs, most, net, len(now - old), len(old - now)),
                "remove or merge at least %d rows, or the owner raises max_suite_seconds in their own words" % net, "TEST_CAPS")
    return None


def record(state, base):
    part = _s.lane_part(state.get("slug", ""))
    top = _s.git_out("rev-parse", "--show-toplevel")
    if top:
        _s.issues(top)
        _s.results(top)
        changed = [path for path in _s.FILES if _s.git_out("status", "--porcelain", "--", path)]
        criteria = os.path.join(os.path.dirname(_s.REG), "..", "workflow-docs", "scripts", "criteria.py")
        try:
            cfg = json.load(open(os.path.join(top, ".loop", "config.json")))
        except (OSError, ValueError):
            cfg = {}
        cfg = cfg if isinstance(cfg, dict) else {}
        try:
            if changed and os.path.exists(os.path.join(top, ".loop", "docs.tsv")) and os.path.exists(criteria):
                subprocess.run([sys.executable, criteria, "render", "--tables"], cwd=top, capture_output=True, text=True, timeout=300)
                changed += _s.generated(cfg)
            if changed:
                subprocess.run(["git", "add", "--"] + changed, cwd=top, capture_output=True, text=True)
                done = subprocess.run(["git", "commit", "--only", "-q", "-m", "pr: record issue states and the lane's results",
                                       "--"] + changed, cwd=top, capture_output=True, text=True, stdin=subprocess.DEVNULL,
                                      timeout=60)
                if done.returncode:
                    print("NOTE: the bookkeeping commit failed: %s; those files were put back (a new file stays, untracked), so "
                          "the next pr run derives them again" % ((done.stderr or done.stdout).strip().splitlines() or ["?"])[-1])
                    _s.undo(top, changed)
                    sys.exit(_s.NO_PUSH)
        except subprocess.TimeoutExpired as error:
            print("NOTE: the bookkeeping step timed out (%s); nothing more committed" % " ".join(error.cmd[:3]))
            lock = os.path.join(top, _s.git_out("rev-parse", "--git-path", "index.lock"))
            if error.cmd[0] == "git" and os.path.exists(lock):
                os.remove(lock)
            _s.undo(top, changed)
            sys.exit(_s.NO_PUSH)
    state["pr_lane"] = part
    head = _s.git_out("rev-parse", "HEAD")
    state["pr_head"] = head
    state["pr_base"] = _s.git_out("merge-base", head, "origin/" + base) or _s.git_out("rev-parse", "origin/" + base)


def bump_version(g, state, head):
    import sizing
    sizing.at_pr(g, state)
    cfg = g.config()
    name = cfg.get("version_file") or "VERSION"
    path = os.path.join(g.root(), name)
    if not cfg.get("pr_bumps_version") or not os.path.exists(path):
        return head
    version = g.read(path).strip()
    if version != g.git("show", "%s:%s" % (g.base_ref(state), name), check=False).strip():
        return head
    if not re.match(r"^\d+(\.\d+)+$", version):
        g.no("the version %r isn't numbers and dots. Fix: set it by hand." % version)
    parts = version.split(".")
    parts[-1] = str(int(parts[-1]) + 1)
    g.write(path, ".".join(parts) + "\n")
    g.git("add", "--", name)
    g.git("commit", "-m", "Bump version to " + ".".join(parts), "--", name)
    new = g.git("rev-parse", "HEAD")
    g.save(state, "bumped %s to %s" % (name, ".".join(parts)))
    return new


def requirement_gate(g, slug):
    """Refuse pr while a requirement finding is unfiled or criteria.py guard refuses a changed Reviewed requirement."""
    rows = [r for r in g.guards.extra(g.state_dir(), slug)["findings"] if r.get("requirement")]
    loose = {r["text"] for r in rows if not r["filed"]} - {r["text"] for r in rows if r["filed"]}
    tool = os.path.join(g.SKILLS, "workflow-docs", "scripts", "criteria.py")
    done = g.run([sys.executable, tool, "guard", "origin/" + g.config()["base"], slug]) if os.path.exists(tool) else None
    if loose or (done and done.returncode):
        g.no("[FIND-FILE] %s not filed on its Backlog milestone. Fix: run goal.py finding again" % ", ".join(sorted(t.split()[0] for t in loose))
             if loose else (done.stderr or done.stdout).strip())
    state = g.load(slug)
    if state.get("one_review"):  # DLF-1.3: open findings, new uncovered changes and unapproved requirement text
        import outcomes
        more = outcomes.blockers(g.root(), g.state_dir(), state, "origin/" + g.config()["base"], "HEAD")
        more and g.no("no pull request yet: %s. Fix: take out or fix each part; the operation closes a finding (goal.py finding-close); "
                      "use only approved requirement text (ONE_REVIEW_UNAPPROVED)" % "; ".join(more))


def session_reply(state, slug, step, path, runs, flow):
    if state.get("worker") != "session" or not (state.get("session") or {}).get("id"):
        sys.exit("REFUSED: %s names no worker session. Fix: sessions.py bind %s ID, or run the step with flow.py." % (slug, slug))
    early = [s for s in flow[:flow.index(step)] if not str((state.get("flow") or {}).get(s, "")).startswith(("done", "skipped"))]
    if early:
        sys.exit("REFUSED: %s comes before %s: record %s first." % (", ".join(early), step, early[0]))
    base = os.path.join(runs, "%s.%s" % (slug, step))
    if os.path.exists(base + ".asked"):
        os.remove(base + ".asked")
    if os.path.realpath(path) != os.path.realpath(base + ".txt"):
        shutil.copyfile(path, base + ".txt")
    open(base + ".ran", "w").close()
    return base + ".txt"


import role as _s  # noqa: E402
