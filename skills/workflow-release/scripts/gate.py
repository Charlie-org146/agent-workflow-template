#!/usr/bin/env python3
"""The main-red hold on every local release door (DEL-17.5), and two helpers moved here byte for byte.

`hold(top, slug="", auto=0)` is "" with no open issue labelled main-red, else the refusal naming the lowest-numbered one;
without auto it exits with the refusal (release.py cut, review.py promote), with auto it returns the text (autorelease.py
finish records it as release_error). The rule is the same as release.yml's hold step. gh is read-only, 30 s a call, 70 s for the whole gate, two tries; gh's own text is never
printed, only its class and exit code, so a failure never leaks a token. verify_steps and left_text moved from
release.py and review.py (both re-export them)."""
import json
import os
import re
import subprocess
import sys
import time

os.environ.setdefault("GIT_TERMINAL_PROMPT", "0")  # no prompt ever blocks a git or gh call
TIMEOUT, DEADLINE, LABEL = 30, 70, "main-red"


def one(text, size):
    """One printable line of at most size characters."""
    return "".join(ch for ch in str(text) if ch.isprintable())[:size]


def gh(args, top, end):
    """(stdout, None) or (None, class and exit code); a class never carries gh's own text."""
    fault = "timeout"
    for _ in range(2):
        left = end - time.monotonic()
        if left <= 0:
            break
        try:
            done = subprocess.run(["gh"] + args, cwd=top, capture_output=True, text=True, timeout=min(TIMEOUT, left))
        except (OSError, subprocess.TimeoutExpired) as error:
            fault = "timeout" if isinstance(error, subprocess.TimeoutExpired) else "gh not installed"
            continue
        if done.returncode == 0:
            return done.stdout, None
        text = done.stderr.lower()
        fault = "auth" if "auth" in text or "login" in text else "permission" if "403" in text or "permission" in text else "bad reply"
        fault += ", gh exit code %d" % done.returncode
    return None, fault


def repo_of(top):
    """owner/name of the github.com repository the origin names: read from its effective, push and configured addresses (a mirror's or an alias's
    address does not change where the project's main-red issues live); "" when none names one or they name different repositories."""
    names = set()
    for cmd in (["git", "remote", "get-url", "origin"], ["git", "remote", "get-url", "--push", "origin"], ["git", "config", "--get", "remote.origin.url"]):
        done = subprocess.run(cmd, cwd=top, capture_output=True, text=True)
        found = re.fullmatch(r"(?:https://(?:[^@/]+@)?|ssh://git@|git@)github\.com[:/]([\w.-]+/[\w.-]+?)(?:\.git)?/?", done.stdout.strip())
        names.add(found.group(1)) if found else None
    return names.pop() if len(names) == 1 else ""


def tip_of(top):
    try:
        base = json.load(open(os.path.join(top, ".loop", "config.json"))).get("base", "main")
    except (OSError, ValueError):
        base = "main"
    for ref in ("origin/" + base, base):
        done = subprocess.run(["git", "rev-parse", ref], cwd=top, capture_output=True, text=True)
        if done.returncode == 0:
            return done.stdout.strip()
    return ""


def main_red(top):
    """("none", ""), ("open", "N: title") for the lowest-numbered open main-red issue, or ("unreadable", why)."""
    try:
        return read_red(top)
    except Exception as error:  # noqa: BLE001 (anything unexpected is unreadable, never a pass)
        if os.environ.get("LOOP_DEBUG"):
            import traceback
            traceback.print_exc()
        return "unreadable", "unexpected %s" % type(error).__name__


def read_red(top):
    end, repo = time.monotonic() + DEADLINE, repo_of(top)
    if not repo:
        return "unreadable", "origin is not a github.com remote"
    out, why = gh(["issue", "list", "--repo", repo, "--state", "open", "--label", LABEL, "--limit", "200", "--json", "number,title"], top, end)
    try:
        issues = sorted(json.loads(out), key=lambda i: i["number"]) if why is None else []
        if not isinstance(json.loads(out) if why is None else [], list) or not all(isinstance(i["number"], int) for i in issues):
            raise TypeError("not a list of issues")
    except (ValueError, KeyError, TypeError):
        return "unreadable", "bad reply"
    if why:
        return "unreadable", why
    if len(issues) >= 200:
        return "unreadable", "200 or more open issues, a truncated list"
    if not issues:
        return "none", ""
    closed, tip = set(), tip_of(top)
    if tip:
        out, why = gh(["pr", "list", "--repo", repo, "--search", tip, "--state", "merged", "--json", "closingIssuesReferences"], top, end)
        if why:
            return "unreadable", "closing references of the merged pull request: " + why
        try:
            closed = {int(r["number"]) for p in json.loads(out) for r in p.get("closingIssuesReferences") or []}
        except (ValueError, KeyError, TypeError):
            return "unreadable", "closing references: bad reply"
    held = [i for i in issues if i["number"] not in closed]
    return ("open", "%d: %s" % (held[0]["number"], one(held[0]["title"], 80))) if held else ("none", "")


def hold(top, slug="", auto=0):
    """"" when no door is held; else the refusal (exits with it unless auto)."""
    state, what = main_red(top)
    if state == "none":
        return ""
    again = "release.py cut %s" % slug if slug else "review.py promote"
    if state == "unreadable":
        fix = ("gh auth login, or set GH_TOKEN for the session" if what.startswith("auth") else "point the origin remote at a github.com repository" if "origin" in what
               else "resolve the fixed main-red issues so fewer than 200 are open" if "200" in what else "rerun with LOOP_DEBUG=1 and report the trace" if what.startswith("unexpected")
               else "check the network and the gh login")
        text = ("(MAIN_RED_UNREADABLE) the merge is done; the release is held, main-red issues cannot be read (%s). Fix: %s. Then run merge.py %s again (hold=main-red:unreadable)." % (what, fix, slug) if auto
                else "REFUSED (MAIN_RED_UNREADABLE) cannot read main-red issues (%s). Nothing was released or changed. Fix: %s. Then run %s again." % (what, fix, again))
    elif auto:
        text = ("(MAIN_RED) the merge is done; the release is held by open issue %s. Fix: the owner or the goal that filed it resolves it once main is green; "
                "an automated session never does (hold=main-red:%s). Then run merge.py %s again; it does not merge twice."
                % (what.replace(": ", ' "', 1) + '"', what.split(":")[0], slug))
    else:
        text = ("REFUSED (MAIN_RED): issue %s is open. Nothing was released or changed. Fix: the owner, or the goal that filed it, "
                "resolves it once main is repaired and green; an automated session never does (hold=main-red:%s). Then run %s again. "
                "See docs/wiki/How-to-use-Release.md" % (what.replace(": ", ' "', 1) + '"', what.split(":")[0], again))
    if auto:
        return text
    sys.exit(text)


def verify_steps(top, slug):
    try:
        text = open(os.path.join(top, ".loop", "goals", slug + ".md")).read()
    except OSError:
        return ""
    part = text.partition("## Verify by hand")[2].split("\n## ", 1)[0]
    part = re.sub(r"<!--.*?-->", "", part, flags=re.S).strip()
    steps = re.split(r"^\s*\d+\.\s+(?=\S)", part, flags=re.M)[1:]
    return part if steps and all(re.search(r"Expect:\s*\S", step) for step in steps) else ""


def left_text(left):
    """The cut's LEFT section: the count and the ids, or ''."""
    return "\n## LEFT\n\nLEFT %d rows were not run before the cut's stop: %s\n" % (len(left), ", ".join(left)) if left else ""
