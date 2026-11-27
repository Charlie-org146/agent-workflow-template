#!/usr/bin/env python3
"""One review (DLF-1.3): which goals ask the owner once, at their start.

Imported by the delivery, monitoring and release scripts; it has no command of its own. The `one_review` setting is read
from a committed config, never from a working copy; a missing key reads as off. A marked goal carries a line in its goal
file. adopt marks no goal: it refuses one with any sign of a mark, and records that a start review is required for a goal
first committed where the setting was on. Standard library only.
"""
import json
import os
import re
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import decisions  # noqa: E402

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


def unanswered(state):
    """Why a goal that is marked, or needs a start review, may not go on; "" once an accepted answer is saved."""
    if state.get("start_answer") or not (state.get("one_review") or state.get("start_required")):
        return ""
    return ("%s needs the owner's start review and no accepted answer is saved. Fix: send it, then goal.py start %s "
            "--owner-record ID" % (state.get("slug"), state.get("slug")))
