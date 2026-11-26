"""the agent build, detect and check commands"""
import json
import os
import subprocess
import sys
os.environ.update(GIT_TERMINAL_PROMPT="0", GH_PROMPT_DISABLED="1", GIT_EDITOR="true", GIT_ASKPASS="true", SSH_ASKPASS="true")


def cmd_build(args):
    _s.role.guard("routing.py build", args.slug)
    runs = _s.RUNS()
    state = _s.role.goal_state(runs, args.slug)
    if not state:
        sys.exit("REFUSED: no goal named %s. Fix: run this in the goal's worktree." % args.slug)
    pick = _s.resolve("build", "small" if (state.get("size") or {}).get("small") else "large")
    prof, here = pick["prof"], pick["profile"] == (_s.load()["routes"].get("fallback") or "heavy")
    if pick["warning"]:
        print(pick["warning"])
    if here:
        _s.update(args.slug, "build", _s.entry(pick["profile"], prof, why=pick["fallback"]))
        print("BUILD %s: build it yourself in this session (%s, %s)" % (args.slug, pick["agent"], pick["model"]))
        return 0
    base = [_s.exe(prof["command"][0])] + list(prof["command"][1:])
    base += [prof["model_flag"], prof["model"]] if prof.get("model") and prof.get("model_flag") else []
    prompt = _s.BUILD.format(files=_s.brief(args.slug), slug=args.slug, branch=subprocess.run(["git", "branch", "--show-current"], capture_output=True, text=True).stdout.strip())
    stdin = prompt if prof.get("prompt") == "stdin" else None
    git = lambda *a: subprocess.run(["git"] + list(a), cwd=_s.top(), capture_output=True, text=True)
    before = git("status", "--porcelain").stdout
    try:
        done = tree_run(base + ([] if stdin else [prompt]), stdin, int(prof.get("limit") or 2700), _s.top())
        out, code = done.stdout, done.returncode
    except (OSError, subprocess.SubprocessError) as why:
        out, code = "", 1
        done = type("Done", (), {"stderr": str(why)})
    text, spent = usage(prof, out)
    failed = bool(code or "STEP: failed" in text)
    item = _s.entry(pick["profile"], prof, spent)
    changed = git("status", "--porcelain").stdout != before
    walled = not changed and any(mark in out + (getattr(done, "stderr", "") or "") for mark in _s.WALLS)
    if walled:
        item["fallback"] = "%s can't write here: its sandbox is read-only" % pick["agent"]
    elif failed or not changed:
        item["error"] = " ".join((getattr(done, "stderr", "") or text or "it changed no file").split())[-160:]
    _s.update(args.slug, "build", item)
    print("BUILD %s: ran on %s (%s), %s tokens" % (args.slug, pick["agent"], pick["model"], (spent["in"] + spent["out"]) if spent else "unread"))
    if walled:
        print("AGENT_FALLBACK build: %s; using %s (%s). Full access is never switched on without the owner's OK." % (
            item["fallback"], _s.load()["profiles"]["heavy"].get("agent"), "heavy"))
        print("BUILD %s: build it yourself in this session" % args.slug)
        return 0
    if failed or not changed:
        print("BUILD FAILED on %s: %s" % (pick["agent"], item["error"]))
        print("Fix: git status shows what it left; build it yourself in this session, or git checkout . to start over.")
        return 1
    git("add", "-A")
    who = [] if git("config", "user.email").stdout.strip() else ["-c", "user.name=workflow-loop", "-c", "user.email=loop@localhost"]  # CI has no author
    git(*who + ["commit", "-qm", "Build via %s: %s" % (pick["agent"], args.slug)])
    print("COMMITTED the %s build" % pick["agent"])
    print("NEXT: check the diff and the tests, fill in Verify by hand, then flow.py %s review" % args.slug)
    return 0


def cmd_detect(args):
    cfg = _s.load()
    ready = {}
    for name, prof in cfg["profiles"].items():
        why = _s.unavailable(prof)
        ready[name] = not why
        print("AGENT %s (%s): %s" % (name, prof.get("agent"), "installed and logged in" if not why else "missing: " + why))
    if args.write:
        target = _s.path()
        try:
            with open(target, encoding="utf-8") as handle:
                held = json.load(handle)
        except (OSError, ValueError):
            held = {}
        held = held if isinstance(held, dict) else {}
        held["profiles"] = dict(held.get("profiles") or {}, **{n: p for n, p in cfg["profiles"].items() if n not in (held.get("profiles") or {})})
        if "routes" not in held:
            held["routes"] = {"steps": {}, "sizes": {"small": "cheap"} if ready.get("cheap") else {}, "gated": ["review"], "fallback": "heavy"}
        os.makedirs(os.path.dirname(target), exist_ok=True)
        with open(target, "w", encoding="utf-8", newline="\n") as handle:
            json.dump(held, handle, indent=2)
            handle.write("\n")
        print("WROTE %s (private; never committed)" % target)
    return 0


def tree_run(argv, stdin, limit, cwd=None):
    """subprocess.run(timeout=) kills only the child; a timed-out agent loses its whole tree (DEL-8)."""
    kid = subprocess.Popen(argv, cwd=cwd, stdin=subprocess.PIPE if stdin else subprocess.DEVNULL, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                           text=True, encoding="utf-8", errors="replace", start_new_session=True)
    try:
        out, err = kid.communicate(stdin, timeout=limit)
    except subprocess.TimeoutExpired:
        _s.proctree.kill(kid.pid)
        kid.communicate(timeout=10)  # a stray holder of the pipe can't hang the stop
        raise
    return subprocess.CompletedProcess(argv, kid.returncode, out, err)


def ask(prof, prompt):
    """(reply text, return code, stderr) from running the profile's agent once on a prompt, no shell."""
    base = [_s.exe(prof["command"][0]) or prof["command"][0]] + list(prof["command"][1:])
    base += [prof["model_flag"], prof["model"]] if prof.get("model") and prof.get("model_flag") else []
    stdin = prompt if prof.get("prompt") == "stdin" else None
    try:
        done = tree_run(base + ([] if stdin else [prompt]), stdin, int(prof.get("limit") or 900))
    except (OSError, subprocess.SubprocessError) as why:
        return "", 1, str(why)
    return usage(prof, done.stdout)[0], done.returncode, done.stderr


def cmd_check(args):
    """The plan step's second agent reads the plan on stdin and prints notes; one that is missing, fails or can't write falls back to Claude."""
    pick, cfg = _s.resolve("plan", "large"), _s.load()
    heavy = cfg["routes"].get("fallback") or "heavy"
    if pick["warning"]:
        print(pick["warning"])
    if pick["profile"] == heavy and not pick["fallback"]:
        print("NOTE: no second agent is routed for the plan step (routes.steps.plan); no cross-check ran")
        return 0
    prompt = _s.CHECK + sys.stdin.read()
    text, code, err = ask(pick["prof"], prompt) if not pick["fallback"] else ("", 0, "")
    if not pick["fallback"] and (code or not text.strip() or any(mark in text + err for mark in _s.WALLS)):
        print("AGENT_FALLBACK plan: %s failed or can't write here; using %s (%s)" % (pick["agent"], cfg["profiles"][heavy].get("agent"), heavy))
        pick["fallback"] = "failed"
    if pick["fallback"]:
        pick = dict(pick, prof=cfg["profiles"][heavy], agent=cfg["profiles"][heavy].get("agent"))
        text, code, err = ask(pick["prof"], prompt)
    print("Notes from %s:" % pick["agent"])
    print(text.strip() or "none (%s)" % (" ".join(err.split())[-120:] or "no reply"))
    return 0


def usage(profile, text):
    """(reply text, {in, out, tokens} or None) from agent output: claude-json, codex-jsonl or text."""
    kind = profile.get("output")
    try:
        if kind == "claude-json":
            data = json.loads(text)
            use = data["usage"]
            ins = int(use.get("input_tokens") or 0) + int(use.get("cache_creation_input_tokens") or 0)
            return str(data.get("result") or ""), {"in": ins, "out": int(use.get("output_tokens") or 0)}
        if kind == "codex-jsonl":
            ins = outs = 0
            reply, seen = "", False
            for line in text.splitlines():
                try:
                    event = json.loads(line)
                except ValueError:
                    continue
                item = event.get("item") or {}
                if event.get("type") == "item.completed" and item.get("type") == "agent_message":
                    reply = str(item.get("text") or "")
                if event.get("type") == "turn.completed":
                    use, seen = event.get("usage") or {}, True
                    ins += int(use.get("input_tokens") or 0) - int(use.get("cached_input_tokens") or 0) + int(use.get("cache_write_input_tokens") or 0)
                    outs += int(use.get("output_tokens") or 0)
            return reply, ({"in": ins, "out": outs} if seen else None)
    except (ValueError, KeyError, TypeError, AttributeError):
        pass
    return text, None


import routing as _s  # noqa: E402
