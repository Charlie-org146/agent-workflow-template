#!/usr/bin/env python3
"""One review (DLF-1.3): which goals ask the owner once, at their start.

Imported by the delivery, monitoring and release scripts; it has no command of its own. The `one_review` setting is read
from a committed config, never from a working copy; a missing key reads as off. A marked goal carries a line in its goal
file. adopt marks no goal: it refuses one with any sign of a mark, and records that a start review is required for a goal
first committed where the setting was on. Standard library only.
"""
import argparse
import json
import os
import re
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import decisions  # noqa: E402
os.environ.update(GIT_TERMINAL_PROMPT="0", GH_PROMPT_DISABLED="1", GIT_EDITOR="true", GIT_ASKPASS="true", SSH_ASKPASS="true")

MARK = re.compile(r"^- Review: one[ \t\r]*$", re.M)
HAND = "refs/loop/handover/"
SIGNS = ("one_review", "start_answer")  # signs of a mark; "start_required" alone is worked out again and never dropped


def refuse(text, code="ONE_REVIEW_ADOPT"):
    sys.exit("REFUSED: %s (%s)" % (text, code))


def git(top, *args, data=None):
    try:
        return subprocess.run(["git"] + list(args), cwd=top, input=data, capture_output=True, text=True, timeout=120)
    except (OSError, UnicodeDecodeError, subprocess.SubprocessError) as error:
        refuse("git %s could not be read: %s. Fix: repair the repository, then run it again" % (args[0], error))


def must(top, *args):
    got = git(top, *args)
    got.returncode and refuse("git %s failed, so the history can't be read in full: %s. Fix: fetch the whole history, then "
                              "run it again" % (args[0], got.stderr.strip()[:200]))
    return got.stdout


def blob_at(top, commit, rel):
    """The file's text in a commit, or None when the commit doesn't hold it; anything unreadable refuses."""
    if not must(top, "ls-tree", "--full-tree", commit, "--", rel).strip():
        return None
    return must(top, "cat-file", "blob", "%s:%s" % (commit, rel))


def setting_at(top, commit):
    """The `one_review` setting in that commit's config; no file or no key is off, an unreadable one refuses."""
    text = blob_at(top, commit, ".loop/config.json")
    try:
        found = json.loads(text) if text is not None else {}
    except ValueError:
        refuse("the config of commit %s can't be read, so whether one_review was on is unknown" % commit[:12])
    return isinstance(found, dict) and found.get("one_review") is True


def history_signs(top, refs, rel):
    """Refuse a goal file that carries the mark now or in any commit these refs reach."""
    shallow = must(top, "rev-parse", "--is-shallow-repository").strip()
    shallow == "false" or refuse("this clone is shallow, so the goal file's history can't be read in full. Fix: git fetch --unshallow")
    here = os.path.join(top, rel)
    if os.path.exists(here):
        with open(here, encoding="utf-8", errors="replace") as handle:
            MARK.search(handle.read()) and refuse("%s carries the one-review mark. Fix: hand it over from the machine that holds "
                                                  "its record (machines.py handover)" % rel)
    # --full-history and -m: a mark on a merged side branch, or one removed later, is not simplified away
    for commit in sorted(set(must(top, "log", "--full-history", "-m", "--format=%H", *refs, "--", rel).split())):
        text = blob_at(top, commit, rel)
        text is not None and MARK.search(text) and refuse(
            "%s carried the one-review mark in commit %s. Fix: hand it over from the machine that holds its record" % (rel, commit[:12]))


def local_signs(runs, slug):
    """Refuse a mark's trace left on this machine; return the need for a start review a stale record already holds."""
    for kind, name in decisions.SIDE[:2]:
        path = os.path.join(runs, name.format(slug=slug))
        os.path.exists(path) and refuse("a %s file for %s is already here (%s). Fix: use the record it belongs to" % (kind, slug, path))
    path = os.path.join(runs, slug + ".json")
    if not os.path.exists(path):
        return None
    try:
        with open(path, encoding="utf-8") as handle:
            found = json.load(handle)
        held, required = [key for key in SIGNS if found.get(key)], found.get("start_required")
    except (OSError, ValueError, AttributeError):
        refuse("the run record %s can't be read. Fix: repair it" % path)
    held and refuse("the record of %s here carries %s, so adopt won't replace it" % (slug, ", ".join(held)))
    return required


def handover_signs(top, slug):
    """An origin handover record that carries a mark refuses, however old; only a proven absence passes."""
    ref = HAND + slug
    seen = git(top, "ls-remote", "origin", ref)
    seen.returncode and refuse("origin can't be asked for %s, so it isn't known to be absent. Fix: reach origin, then run it again" % ref)
    if not seen.stdout.strip():
        return None
    must(top, "fetch", "-q", "origin", "+%s:%s" % (ref, ref))
    try:
        found = json.loads(must(top, "cat-file", "blob", ref))
        state, files = found["state"], found.get("files") or {}
        held = [key for key in SIGNS if state.get(key)] + (["a decisions file"] if files.get("decisions") else [])
        required = state.get("start_required")
    except (ValueError, KeyError, TypeError, AttributeError):
        refuse("the handover record %s can't be read. Fix: repair or hand it over again from the machine that holds the goal" % ref)
    held and refuse("the handover record %s carries %s. Fix: take that handover (machines.py take %s)" % (ref, ", ".join(held), slug))
    return required


def first_commit(top, rel):
    added = must(top, "log", "--full-history", "--topo-order", "--reverse", "--diff-filter=A", "--format=%H", "HEAD", "--", rel).split()
    added or refuse("no commit that added %s can be read" % rel)
    return added[0]


def adopt_check(top, slug, runs):
    """What adopt adds to the record: nothing, or that a start review is required. adopt never marks."""
    rel = ".loop/goals/%s.md" % slug
    kept = local_signs(runs, slug)
    history_signs(top, ("HEAD", "FETCH_HEAD"), rel)
    carried = handover_signs(top, slug)
    commit = first_commit(top, rel)
    if setting_at(top, commit):
        return {"start_required": {"why": "first committed in %s, where one_review is on" % commit[:12]}}
    return {"start_required": kept or carried} if kept or carried else {}


def marked_text(text):
    """A new goal file with the mark under its slug line."""
    out, count = re.subn(r"^(- Slug: .*\n)", lambda found: found.group(1) + "- Review: one\n", text, count=1, flags=re.M)
    count == 1 or refuse("the goal file template has no slug line, so the mark can't be written", "ONE_REVIEW_MARK")
    return out


def mark(runs, slug, by):
    """The record fields of a newly marked goal; its ledger is made here, once."""
    os.path.exists(decisions.ledger(runs, slug)) or decisions.create(runs, slug, by=by)
    return {"one_review": {"at": decisions.stamp(), "by": by}}


def committed(top, ref, slug):
    """The goal file as `ref` holds it, or "" when that ref or file is not there."""
    got = git(top, "cat-file", "blob", "%s:.loop/goals/%s.md" % (ref, slug))
    return "" if got.returncode else got.stdout


def frozen_twice(top, ref, slug):
    committed(top, ref, slug) and refuse(
        ".loop/goals/%s.md is already committed. A new goal needs a new slug; to finish a freeze that was cut off, the operation "
        "session runs goal.py recover %s in its worktree" % (slug, slug), "ONE_REVIEW_HALF_FROZEN")


def half_frozen(state):
    """A queued record with no step: its freeze never finished."""
    return state.get("status") == "queued" and state.get("step") == "" and bool(state.get("done_sha"))


def unanswered(state, top=None):
    """Why a goal that is marked, or needs a start review, may not go on; "" once an accepted answer is saved. With `top`,
    the mark committed on the goal's branch counts too, so a record that lost it is still held."""
    slug = state.get("slug")
    held = state.get("one_review") or state.get("start_required")
    if not held and top and slug:
        branch = state.get("branch") or "loop/%s" % slug
        held = MARK.search(committed(top, "refs/heads/" + branch, slug))
    if state.get("start_answer") or not held:
        return ""
    return ("%s needs the owner's start review and no accepted answer is saved. Fix: send it, then goal.py start %s "
            "--owner-record ID" % (slug, slug))


def gate(state, top, step):
    """Before a step is entered: a half-frozen goal takes none, and a marked one doesn't build or open a pr unanswered. A goal
    that only needs a start review (adopted) is held at the merge."""
    half_frozen(state) and refuse("%s was never fully frozen. Fix: the operation session runs goal.py recover %s"
                                  % (state["slug"], state["slug"]), "ONE_REVIEW_HALF_FROZEN")
    if step not in ("build", "pr"):
        return
    why = unanswered(dict(state, start_required=None), top)
    why and refuse(why, "ONE_REVIEW_UNANSWERED")


def _later_life(g, slug, runs):
    """Refuse at any sign that more than the freeze happened to this goal."""
    def no(what):
        refuse("%s can't be recovered: %s. Only a freeze cut off before its record was saved is recovered" % (slug, what),
               "ONE_REVIEW_RECOVER")
    found = None
    path = os.path.join(runs, slug + ".json")
    if os.path.exists(path):
        found = g.load(slug)
        used = [key for key in ("step", "flow", "pid", "session", "worker", "pr", "start_answer") if found.get(key)]
        if found.get("status") != "queued" or used:
            no("its record is %s and carries %s" % (found.get("status"), ", ".join(used) or "no other sign"))
    own = ("%s.json" % slug, "%s.decisions.jsonl" % slug)
    for name in os.listdir(runs) if os.path.isdir(runs) else []:
        if name.startswith(slug + ".") and name not in own and not name.endswith(".lock") and not name.startswith(own[0] + "."):
            no("the file %s is here" % os.path.join(runs, name))
    os.path.exists(os.path.join(runs, "..", "redteam", "plan-%s.json" % slug)) and no("a plan review of it is saved here")
    if os.path.exists(decisions.ledger(runs, slug)):
        [e["kind"] for e in decisions.entries(runs, slug)] == ["mark"] or no("its decisions file has entries after the mark")
    top, branch = g.root(), "loop/" + slug
    seen = git(top, "ls-remote", "origin", "refs/heads/" + branch, HAND + slug)
    seen.returncode and no("origin can't be read (%s)" % seen.stderr.strip()[:200])
    seen.stdout.strip() and no("origin has %s" % ", ".join(line.split()[-1] for line in seen.stdout.splitlines()))
    asked = g.run(["gh", "pr", "list", "--head", branch, "--state", "all", "--json", "number"])
    try:
        prs = json.loads(asked.stdout) if asked.returncode == 0 else None
    except ValueError:
        prs = None
    isinstance(prs, list) or no("the pull requests of %s can't be read" % branch)
    prs and no("%s has a pull request" % branch)
    return found


def recover(g, args):
    """goal.py recover SLUG, operation only: finish a freeze cut off between its commit and its saved record. It keeps the
    mark, rebuilds no approval and imports no owner record, so the start review is still to be asked."""
    slug, branch = args.slug, "loop/" + args.slug
    g.guards.operation_only(g, "recover", slug)
    top, runs, rel = g.root(), g.state_dir(), ".loop/goals/%s.md" % slug
    g.git("branch", "--show-current") == branch or g.no("not on %s. Fix: run this in its worktree." % branch)
    only = (len(must(top, "rev-list", "--parents", "-n", "1", "HEAD").split()) == 2
            and must(top, "log", "-1", "--format=%s").strip() == "Goal: " + slug
            and must(top, "diff-tree", "--no-commit-id", "--name-status", "-r", "HEAD").splitlines() == ["A\t" + rel])
    only or refuse("HEAD is not the freeze commit of %s that adds only %s" % (slug, rel), "ONE_REVIEW_RECOVER")
    git(top, "diff", "--quiet", "HEAD", "--", rel).returncode == 0 or refuse(
        "%s differs from the committed file. Fix: git checkout -- %s" % (rel, rel), "ONE_REVIEW_RECOVER")
    state = _later_life(g, slug, runs)
    text, lines = committed(top, "HEAD", slug), g.done_lines(slug)
    lines or refuse("%s has no done lines" % rel, "ONE_REVIEW_RECOVER")
    if state is None:
        title = re.match(r"# (.*)", text)
        touched = re.search(r"^- Touches: (.*)$", text, re.M)
        touches = [x.strip() for x in touched.group(1).split(",")] if touched and touched.group(1).strip() != "not declared" else []
        goal = title.group(1).strip() if title else slug
        # a lost record's release choice is unknown, so it asks: auto_merge never applies by default here
        state = {"slug": slug, "goal": goal, "status": "running", "step": "", "tries": 0, "flow": {}, "branch": branch,
                 "worktree": top, "touches": touches, "pid": None, "pr": "", "batch": False, "done_sha": g.done_sha(lines),
                 "release": "ask", "waiting": None, "finding": "", "log": []}
        state.update(g.fit.frozen_fields(g, argparse.Namespace(slug=slug, goal=goal), lines, touches))
        g.guards.stamp(state, "idea")
        g.pods and g.pods.stamp(state)
    else:
        state.get("done_sha") == g.done_sha(lines) or refuse("the record's done lines are not the committed ones",
                                                             "ONE_REVIEW_RECOVER")
    if MARK.search(text):
        state.update(mark(runs, slug, "goal.py recover"))
    elif setting_at(top, "HEAD"):
        state["start_required"] = {"why": "frozen where one_review is on, with no mark"}
    state["step"] = "idea"
    g.save(state, "recovered a freeze that was cut off before its record was saved")
    print("RECOVERED %s at idea, release=%s%s" % (slug, state.get("release") or "as set up",
                                                "; its start review is still to be asked" if unanswered(state) else ""))
    return 0
