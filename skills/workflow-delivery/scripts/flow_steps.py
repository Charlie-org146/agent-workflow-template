"""the step runner and the prompt builders"""
import json
import os
import re
import shutil
import subprocess
import sys
import time
os.environ.update(GIT_TERMINAL_PROMPT="0", GH_PROMPT_DISABLED="1", GIT_EDITOR="true", GIT_ASKPASS="true", SSH_ASKPASS="true")


def in_session(args, runs, reply, base):
    """A worker session runs the step's skill itself; flow.py only names it, then hands the reply to goal.py record."""
    try:
        state = json.loads(_s.read(os.path.join(runs, args.slug + ".json")))
    except (OSError, ValueError):
        state = {}
    if state.get("worker") != "session":
        return False
    asked = base + ".asked"
    fresh = os.path.exists(asked) and os.path.exists(reply) and os.path.getmtime(reply) >= os.path.getmtime(asked)
    text = _s.read(reply) if fresh else ""
    if not re.search(r"^\W*STEP:\s*(done|skipped|pending|failed)\b", text, re.M | re.I):
        if not os.path.exists(asked):
            if os.path.exists(reply):
                os.replace(reply, reply + ".last")
            _s.role.begin(os.path.join(runs, args.slug + ".json"), args.step)
        open(asked, "a").close()
        skill, text = step_prompt(_s.flow(), args)
        _s.proctree.outcap_free(True)  # the step's prompt is read whole
        print("IN SESSION %s: no headless agent; run %s yourself in this session." % (
            args.step, "delivery's built-in routine" if skill == _s.BUILTIN else "the %s skill" % skill))
        print(text)
        if args.step in _s.BUDGETED:
            print("TIME BUDGET: %d minutes for this step. At the limit, stop, finish what you have, and add a line "
                  "`BUDGET: left: <what you did not do>` before the DEPTH line; an overrun is recorded." % _s.lanekit.minutes(
                      _s.repo_config(), "step_budget_minutes"))
        print("Write its reply, ending with the DEPTH line and then the STEP line, to %s, then run this same command again." % reply)
        _s.proctree.outcap_free(False)
        return True
    if args.step in _s.BUDGETED:
        mins = _s.lanekit.minutes(_s.repo_config(), "step_budget_minutes")
        if os.path.getmtime(reply) - os.path.getmtime(asked) > mins * 60:
            _s.lanekit.hit(runs, args.slug, args.step, "step", mins, _s.lanekit.left_of(text))
    os.remove(asked)
    open(base + ".ran", "w").close()
    print("\n".join(re.findall(r"^\W*(?:PENDING|STEP): .*", text, re.M)))
    print("NEXT: goal.py record %s %s --file %s" % (args.slug, args.step, reply))
    return True


def start(args, runs, reply, job):
    spec = _s.flow()
    env = unattended(spec, args.step)
    command = step_command(spec, args.step)
    cfg = _s.repo_config()
    state = _s.role.goal_state(runs, args.slug)
    _s.fit.budget_stop(args.slug, state, runs, cfg)
    if not shutil.which(command[0]):
        sys.exit("REFUSED: the flow's command %s isn't on this machine." % command[0])
    top = _s.git("rev-parse", "--show-toplevel")
    prompt = step_prompt(spec, args)[1]
    if os.path.exists(reply):
        os.replace(reply, reply + ".last")
    if os.path.basename(command[0]) == "claude" and not any(part.startswith("--output-format") for part in command):
        command += ["--output-format", "json"]
    with open(reply, "w") as out, open(reply + ".err", "w") as err:
        child = subprocess.Popen(command + [prompt], cwd=top, stdin=subprocess.DEVNULL, stdout=out, env=env,
                                 stderr=err, start_new_session=True)
    _s.role.begin(os.path.join(runs, args.slug + ".json"), args.step)
    with open(job, "w") as handle:
        limit = spec.get("limit") or int(cfg.get("step_limit") or 0) or args.limit
        if args.step in _s.BUDGETED:
            limit = _s.lanekit.seconds(cfg, "step_budget_minutes", limit)
        json.dump({"pid": child.pid, "pstart": _s.lanekit.pstart(child.pid), "started": time.time(), "limit": limit}, handle)
    print("FLOW %s: running your %s skill unattended" % (args.step, args.step))
    print("RUNNING: run this same command again")


def runnable(spec, headless):
    """Refuse up front, before any step starts, when a mapped step can't run in this mode: a named skill needs the probe,
    a headless step needs the command. A built-in step needs no probe: delivery's own build and pr steps already run
    under the same command and prompt rules, and the command's allowed tools set the real limit."""
    gaps = []
    for step in _s.STEPS:
        skill = _s.skill_of(spec, step)
        if skill and skill != _s.BUILTIN and not spec.get("probe"):
            gaps.append("%s (%s) has no probe" % (step, skill))
        if skill and headless and not spec.get("command"):
            gaps.append("%s runs headless and the flow has no command" % step)
    if gaps:
        sys.exit("REFUSED: the flow can't run every step: %s (FLOW_UNRUNNABLE). Fix: add \"probe\" and \"command\" to %s, "
                 "or map those steps to \"built-in\"; no step was started." % ("; ".join(gaps), _s.FLOW_FILE))


def unattended(spec, step):
    """The probe must print probe_expect under the flow's environment, or no step starts: a skill run by a person's
    rules could push, so it never runs here. A built-in step needs no probe (see runnable)."""
    env = dict(os.environ, **{key: str(value) for key, value in (spec.get("env") or {}).items()})
    if _s.skill_of(spec, step) == _s.BUILTIN:
        return env
    probe = [os.path.expanduser(part) for part in spec["probe"]]
    try:
        out = subprocess.run(probe, capture_output=True, text=True, env=env, timeout=60).stdout
    except (OSError, subprocess.SubprocessError):
        out = ""
    if (spec.get("probe_expect") or "unattended") not in out:
        sys.exit("REFUSED: the flow's probe didn't print %r, so its skills wouldn't run unattended. Fix: set their "
                 "unattended mode under \"env\" in the flow file." % (spec.get("probe_expect") or "unattended"))
    return env


def step_prompt(spec, args):
    skill = _s.skill_of(spec, args.step)
    text = _s.PROMPT.format(skill=skill, step=args.step, slug=args.slug, branch=_s.git("branch", "--show-current"),
                         purpose=_s.PURPOSE[args.step].format(slug=args.slug, lane=_s.role.lane_text()),
                         note="The owner said: " + args.note + "\n" if args.note else "",
                         depth=_s.depth_rule(args.step, _s.role.goal_state(_s.RUNS(), args.slug), _s.RUNS())).rstrip()
    if skill == _s.BUILTIN:
        head, rest = text.split("\n", 1)
        text = "%s\nThe routine:\n%s\n%s" % (head.replace("Use the built-in skill for", "Run delivery's built-in routine for"),
                                             routine(args.step), rest)
    return skill, text


def step_command(spec, step):
    """The flow command with this step's allowed tools and model: a step's override beats the flow's own default."""
    over = (spec.get("overrides") or {}).get(step) or {}
    tools, model = over.get("allowed_tools") or spec.get("allowed_tools"), over.get("model") or spec.get("model")
    return [os.path.expanduser(part) for part in spec["command"]] + (["--allowedTools=" + ",".join(tools)] if tools else []) \
        + (["--model=" + model] if model else [])


def routine(step):
    try:
        text = _s.read(_s.ROUTINES)
    except OSError:
        text = ""
    found = re.search(r"^## %s\n(.*?)(?=^## |\Z)" % step, text, re.M | re.S)
    if not found:
        sys.exit("REFUSED: no %s section in %s (FLOW_SECTION_MISSING). Fix: reinstall workflow-delivery." % (step, _s.ROUTINES))
    return found.group(1).strip()


import flow as _s  # noqa: E402
