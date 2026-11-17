#!/usr/bin/env python3
"""Phone-first onboarding (#4805): list every setup step that needs a desk, run each once up front, and check that a phone-only
session can start a goal.

usage: desk.py list [--repo DIR]         each desk-only step with its state (done, listed, open)
       desk.py run [--repo DIR]          verify what can be verified, print each open desk step once with how to do it
       desk.py done STEP [STEP ...]      record that you did a desk step (the app's own setting is the truth)
       desk.py check [--repo DIR]        DESK OK when nothing is left at the desk and a phone-only start works; else one GAP line each

A phone over Remote Control can read check-ins and mail, answer, approve and start goals, but the app refuses session starts from
it, so everything the app needs trusted, approved or signed in must be done once at the desk. Steps a file can prove (private
names file, mail.env present, the agent command on the PATH, Codex login) are verified by `run`, never read: only whether the file
exists. The rest are recorded with `done`. The record is machine-local (`$LOOP_DESK_HOME`, else ~/.workflow-loop/desk.json) and
holds step names and times only. With `workers: app` in the repo config a goal waits for a bound session when the app refuses
one, so check lists that too. Writes nothing in the repo.
"""
import argparse
import json
import os
import shutil
import subprocess
import sys
import time

HOME = os.path.expanduser(os.environ.get("LOOP_DESK_HOME") or "~/.workflow-loop")
# (id, what, how, how a file proves it: a path under HOME, or None for a step only the owner can confirm)
STEPS = (
    ("trust-folders", "trust the project folder and the worktree folders in the app",
     "open the repo and its .git/loop/worktrees folder once in the app and choose Trust", None),
    ("permission-modes", "give each scheduled task a permission mode that never asks (bypass)",
     "in the app, set the mode on each task, then machine.py record-task NAME bypass", None),
    ("tool-preapprovals", "pre-approve the tools each scheduled task uses (Run now once)",
     "press Run now on each task and allow its tools, so a scheduled check-in never stops to ask", None),
    ("private-names", "create the private-names file",
     "run `python3 dev/machine.py apply` from the template clone (it writes an empty one)", "private-names"),
    ("mail-env", "put the mail settings in mail.env, outside the repo",
     "run `python3 dev/machine.py apply`, then fill the file it names (keys stay out of the repo)", "mail.env|schedule/mail.env"),
    ("codex-login", "sign in to Codex, if Codex is an agent here",
     "run `codex login` at the desk", "AUTO:codex"),
)


def record_path():
    return os.path.join(HOME, "desk.json")


def load():
    try:
        with open(record_path()) as handle:
            found = json.load(handle)
        return found if isinstance(found, dict) else {}
    except (OSError, ValueError):
        return {}


def save(found):
    os.makedirs(HOME, exist_ok=True)
    with open(record_path(), "w") as handle:
        json.dump(found, handle, indent=1, sort_keys=True)


def proven(proof):
    """True when a file shows the step is done; None when only the owner can say."""
    if proof is None:
        return None
    if proof == "AUTO:codex":
        return True if not shutil.which("codex") else os.path.exists(os.path.expanduser("~/.codex/auth.json"))
    return any(os.path.exists(os.path.join(HOME, part)) for part in proof.split("|"))


def state_of(step, found):
    ok = proven(step[3])
    if ok:
        return "done"
    return "done" if step[0] in found and found[step[0]].get("done") else "listed" if step[0] in found else "open"


def phone_start(repo):
    """Gaps that stop a phone-only session from starting a goal: no agent command, or an app-only worker rule."""
    try:
        with open(os.path.join(repo, ".loop", "config.json")) as handle:
            cfg = json.load(handle)
    except (OSError, ValueError):
        return ["no .loop/config.json: run setup first"]
    out = []
    command = cfg.get("agent_command") or []
    if not command or not shutil.which(str(command[0])):
        out.append("phone-start: agent_command is missing or not on the PATH, so no background worker can start without the app")
    if cfg.get("workers") == "app":
        out.append("phone-start: workers is app, so a goal waits for a bound session when the app refuses a start from the phone; "
                   "clear workers in .loop/config.json for a background worker through agent_command")
    return out


def repo_of(args):
    done = subprocess.run(["git", "-C", args.repo, "rev-parse", "--show-toplevel"], capture_output=True, text=True)
    return done.stdout.strip() or os.path.abspath(args.repo)


def cmd_list(args):
    found = load()
    for step in STEPS:
        print("DESK %s [%s]: %s" % (step[0], state_of(step, found), step[1]))
    return 0


def cmd_run(args):
    found, left = load(), 0
    for step in STEPS:
        now = state_of(step, found)
        if now == "done":
            print("DESK %s: done" % step[0])
            continue
        left += 1
        if now == "open":
            found[step[0]] = {"listed": time.strftime("%Y-%m-%d %H:%M")}
            print("DESK %s: %s. Do: %s. Then: desk.py done %s" % (step[0], step[1], step[2], step[0]))
        else:
            print("DESK %s: still open (listed once already). Then: desk.py done %s" % (step[0], step[0]))
    save(found)
    print("DESK: %d step(s) open at the desk" % left if left else "DESK OK: every desk step is done")
    return 0


def cmd_done(args):
    found, names = load(), [s[0] for s in STEPS]
    bad = [n for n in args.steps if n not in names]
    if bad:
        print("REFUSED: unknown desk step %s; steps are %s. Nothing was recorded." % (", ".join(bad), ", ".join(names)))
        return 2
    for name in args.steps:
        found[name] = {"done": time.strftime("%Y-%m-%d %H:%M")}
    save(found)
    print("RECORDED: %s" % ", ".join(args.steps))
    return 0


def cmd_check(args):
    found, gaps = load(), []
    gaps = ["GAP %s: %s -> %s" % (s[0], s[1], s[2]) for s in STEPS if state_of(s, found) != "done"]
    gaps += ["GAP " + g for g in phone_start(repo_of(args))]
    if gaps:
        print("\n".join(gaps))
        return 1
    print("DESK OK: nothing left to do at the desk; a phone-only session can start a goal")
    return 0


def main(argv):
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = parser.add_subparsers(dest="command", required=True)
    for name, func in (("list", cmd_list), ("run", cmd_run), ("check", cmd_check)):
        item = sub.add_parser(name)
        item.add_argument("--repo", default=".")
        item.set_defaults(func=func)
    item = sub.add_parser("done")
    item.add_argument("steps", nargs="+")
    item.set_defaults(func=cmd_done)
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
