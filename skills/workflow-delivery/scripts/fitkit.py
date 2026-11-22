#!/usr/bin/env python3
"""Helpers moved whole and unchanged out of fit.py so every script DEL-22 touches ends under 19,000 bytes; no logic of its own."""
import json
import os
import re
import time

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


def next_command(state, step):
    slug = state.get("slug", "SLUG")
    return {"pr": "goal.py pr %s" % slug, "build": "goal.py step %s build, then flow.py %s review" % (slug, slug)}.get(
        step, "flow.py %s %s" % (slug, step))


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


def off_rows(text):
    bad, un = re.findall(r"^FAIL (\S+)", text, re.M), re.findall(r"^UNPROVEN ([^\s:]+)", text, re.M)
    return un if un and not bad and set(un) <= set(re.findall(r"^SKIPPED (\S+)", text, re.M)) else []


def off_reply(lane_line):
    m = re.search(r"^LANE_OWED (.+?):", lane_line, re.M)
    return m and ("%s\nPENDING: waiting for off-platform proof of %s. On a Linux or Mac runner run regression.py red ID --break "
                  "CMD for each, then here regression.py red ID --off-platform --runner NAME --commit SHA; then answer go on\nSTEP: pending\n"
                  % (lane_line, m.group(1))) or ""


def main_here(g, args):
    gitdir, common = (os.path.realpath(g.git("rev-parse", flag)) for flag in ("--git-dir", "--git-common-dir"))
    if gitdir == common and os.path.isdir(os.path.join(common, "loop", "worktrees")):
        g.no("--here in the repo's main checkout would leave it on a loop branch. Fix: git worktree add -b loop/%s "
             "%s origin/main, then run goal.py new there" % (args.slug, os.path.join(common, "loop", "worktrees", args.slug).replace(os.sep, "/")))
