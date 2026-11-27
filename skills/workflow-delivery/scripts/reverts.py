#!/usr/bin/env python3
"""DLF-1.3's one-line revert. Each decision made in the owner's place is listed with one command and what it stops. A revert
only stops work: it undoes no safety fix, brings back no dropped part and reopens no safety item. A decision that let named
files go on is reverted by taking them out; any other stops the goal. After the merge nothing is taken back: the revert is
filed, and named files hold every release until their removal is in the commit released. Standard library only."""
import argparse
import hashlib
import json
import os
import shlex
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import decisions  # noqa: E402
import dlf  # noqa: E402
import outcomes  # noqa: E402
QUIET_ENV = dict(GIT_TERMINAL_PROMPT="0", GH_PROMPT_DISABLED="1", GIT_EDITOR="true", GIT_ASKPASS="true", SSH_ASKPASS="true")  # for our own subprocess calls only

GOAL_PY = os.path.join(os.path.dirname(os.path.abspath(__file__)), "goal.py")


def refuse(text, code="ONE_REVIEW_REVERT"):
    sys.exit("REFUSED: %s (%s)" % (text, code))


def effect(entry):
    """("files", names) when the decision let named files go on under an approved item, else ("stop", [])."""
    return ("files", entry["files"]) if entry.get("inside") and entry.get("files") else ("stop", [])


def says(entry):
    kind, files = effect(entry)
    return "takes out " + ", ".join(files) if kind == "files" else "stops the goal"


def listing(top, runs, state):
    """[(line, command)] for every decision made for this goal; the command runs as printed and stands on its own line."""
    slug, out = state["slug"], []
    for entry in decisions.require(runs, state):
        if entry["kind"] == "decision":
            line = "%s #%d: %s -> %s. Reverting it %s." % (slug, entry["n"], entry.get("question"), entry.get("taken"), says(entry))
            out.append((line, "cd %s && LOOP_ROLE=operation python3 %s revert %s %d" % (shlex.quote(top), shlex.quote(GOAL_PY), slug, entry["n"])))
    return out


def merged(top, state, base):
    if state.get("release") in ("merged", "cut"):
        return True
    if state.get("pr_head") and outcomes.git(top, "merge-base", "--is-ancestor", state["pr_head"], base)[0] == 0:
        return True
    if not state.get("pr"):
        return False
    try:  # a squash or hand merge leaves no ancestor behind
        got = subprocess.run(["gh", "pr", "view", state["pr"], "--json", "state"], cwd=top, capture_output=True, text=True, timeout=60,
                             env=dict(os.environ, **QUIET_ENV))
        known = json.loads(got.stdout)["state"] if got.returncode == 0 else ""
    except (OSError, ValueError, KeyError, TypeError, subprocess.SubprocessError):
        known = ""
    known or refuse("whether %s merged can't be told, and a revert differs after a merge. Fix: reach GitHub, then run it again" % state["pr"])
    return known == "MERGED"


def removal_name(slug, number):
    return ("undo-%s" % slug)[:44].rstrip("-") + "-%d" % number


def queue_removal(g, slug, number):
    """RT16: the removal goal is queued by the revert itself; its start review is that revert command."""
    held = next((r for r in holds(g.root()) if r["slug"] == slug and r["decision"] == number), None)
    if not held:
        return
    name, files = held["removal_goal"], held["files"]
    try:
        g.fit.cmd_queue(g, argparse.Namespace(slug=name, goal="Take out what decision %d of %s let into %s" % (number, slug, ", ".join(files)),
                                              done=[held.get("removal_done") or removal_line(slug, number, files)],
                                              touches=",".join(files), depends_on="", release=""))
    except SystemExit as stop:
        print("NOT QUEUED %s: %s. Queue it by hand under that name; the release hold stands" % (name, stop.code))


def removal_line(slug, number, files):
    return "%s no longer carries the change decision %d of %s let in" % (", ".join(files), number, slug)


def start_by_revert(runs, slug, done_sha):
    """The start answer of the removal goal a revert queued: that goal only (its done line), once, while the removal is
    pending, for the held files and their classes."""
    path = os.path.join(runs, "..", "release-holds.jsonl")
    rows = hold_rows_at(path)
    spent = {(r["slug"], r["decision"]) for r in rows if r["op"] in ("clear", "started")}
    for row in rows:
        queued = row["op"] == "hold" and row.get("removal_goal") == slug and (row["slug"], row["decision"]) not in spent
        if queued and hashlib.sha256(("1. " + (row.get("removal_done") or removal_line(row["slug"], row["decision"], row["files"]))).encode()).hexdigest() == done_sha:
            with open(path, "a", encoding="utf-8") as handle:
                handle.write(json.dumps({"op": "started", "slug": row["slug"], "decision": row["decision"], "goal": slug,
                                         "at": decisions.stamp()}, sort_keys=True) + "\n")
            items = [{"n": n, "class": kind, "action": "take the reverted change out", "files": row["files"], "recommend": "approve",
                      "approvable": True, "approved": True, "by": "revert"} for n, kind in enumerate(row.get("classes") or [], 1)]
            record = "revert:%s:%d" % (row["slug"], row["decision"])
            return {"record": record, "at": row["at"], "verdict": "approve", "text": "goal.py revert %s %d" % (row["slug"], row["decision"]),
                    "items": items}
    return None


def holds_file(top):
    return os.path.join(outcomes.top_loop(top), "release-holds.jsonl")


def hold_rows_at(path):
    try:
        with open(path, encoding="utf-8") as handle:
            return [json.loads(line) for line in handle if line.strip()]
    except FileNotFoundError:
        return []
    except (OSError, ValueError):
        refuse("the release holds can't be read (%s). Fix: repair the file" % path, "ONE_REVIEW_HOLD")


def hold_rows(top):
    return hold_rows_at(holds_file(top))


def add_hold(top, row):
    with open(holds_file(top), "a", encoding="utf-8") as handle:
        handle.write(json.dumps(dict(row, at=decisions.stamp()), sort_keys=True) + "\n")


def holds(top):
    """The pending removals, one per reverted decision that has no removal commit yet."""
    rows = hold_rows(top)
    cleared = {(r["slug"], r["decision"]) for r in rows if r["op"] == "clear"}
    return [r for r in rows if r["op"] == "hold" and (r["slug"], r["decision"]) not in cleared]


def release_check(top, commit):
    """Every local release path calls this with the commit it releases: each reverted part's removal must be in it."""
    why = ["%s #%d (%s) has no removal yet" % (r["slug"], r["decision"], ", ".join(r["files"])) for r in holds(top)]
    why += ["%s #%d's removal %s is not in this commit" % (r["slug"], r["decision"], r["commit"][:12]) for r in hold_rows(top)
            if r["op"] == "clear" and outcomes.git(top, "merge-base", "--is-ancestor", r["commit"], commit)[0]]
    why and refuse("no release: %s. Fix: merge the removal, then goal.py hold-clear SLUG N --commit SHA" % "; ".join(why),
                   "ONE_REVIEW_HOLD")


def shipped(top, state, base):
    """The newest commit known to hold what is being reverted: a removal comes after it."""
    return outcomes.git(top, "rev-parse", "--verify", "--quiet", base + "^{commit}")[1].strip() or state.get("pr_head") or ""


def clear_hold(top, slug, number, commit, by):
    held = next((r for r in holds(top) if r["slug"] == slug and r["decision"] == number), None)
    held or refuse("no pending removal for %s #%s" % (slug, number), "ONE_REVIEW_HOLD")
    code, full = outcomes.git(top, "rev-parse", "--verify", "--quiet", commit + "^{commit}")
    full = full.strip()
    touches = not code and outcomes.git(top, "diff", "--quiet", "--no-ext-diff", full + "^1", full, "--", *held["files"])[0] == 1
    was = held.get("shipped")
    later = touches and (not was or full != was and not outcomes.git(top, "merge-base", "--is-ancestor", was, full)[0]
                         and outcomes.git(top, "diff", "--quiet", "--no-ext-diff", was, full, "--", *held["files"])[0] == 1)
    later or refuse("%s is not a commit after the merge that changes %s" % (commit, ", ".join(held["files"])), "ONE_REVIEW_HOLD")
    add_hold(top, {"op": "clear", "slug": slug, "decision": number, "commit": full, "by": by})


def revert(top, runs, state, number, by, base, met="", cannot="", save=None):
    """Revert one listed decision. A repeat changes nothing."""
    slug = state["slug"]
    found = decisions.require(runs, state)
    entry = next((e for e in found if e["kind"] == "decision" and e["n"] == number), None)
    entry or refuse("%s has no decision %s; goal.py revert takes a number from the check-in's list" % (slug, number))
    done = next((e for e in found if e["kind"] == "revert" and e["decision"] == number), None)
    kind, files = effect(entry)
    note = " ".join((met or cannot).split())
    note and dlf.safe(top, note) != note and refuse("give words the private-name scan passes")
    if met or cannot:
        done and done["effect"] == "files" or refuse("that records on a revert that takes files out; revert %d first" % number)
    if met:
        left = outcomes.changed(top, outcomes.base_point(top, base, "HEAD"), "HEAD", files)
        left and refuse("%s still differs from the base; take it out first" % ", ".join(left))
        decisions.add(runs, slug, "met", decision=number, why=note, by=by)
        return print("RECORDED %s #%d: the done lines are still met" % (slug, number))
    cut_off = done and (done["effect"] == "stop" and not decisions.stopped(found) or done["effect"] == "after-merge" and done["files"]
                        and not any(r["op"] == "hold" and (r["slug"], r["decision"]) == (slug, number) for r in hold_rows(top)))
    if done and not cannot and not cut_off:
        return print("%s #%d was already reverted by %s; nothing changed" % (slug, number, done.get("by")))
    rel = dlf.brief(top, slug)[1]
    if cut_off and done["effect"] == "after-merge":
        add_hold(top, {"op": "hold", "slug": slug, "decision": number, "files": done["files"], "classes": entry.get("safety") or [],
                       "removal_goal": removal_name(slug, number), "removal_done": removal_line(slug, number, done["files"]),
                       "shipped": shipped(top, state, base)})
        return print("REVERTED %s #%d: the release hold that was missing is in place" % (slug, number))
    kind = "stop" if cut_off else kind

    def file(what, words):
        dlf.file_line(top, runs, slug, rel, "break", "other", "revert%d%s" % (number, "stop" if cannot else ""), what, words, "keep it out")

    if not done and merged(top, state, base):
        decisions.add(runs, slug, "revert", decision=number, effect="after-merge", files=entry.get("files") or [], by=by)
        entry.get("files") and add_hold(top, {"op": "hold", "slug": slug, "decision": number, "files": entry["files"],
                                              "classes": entry.get("safety") or [], "removal_goal": removal_name(slug, number),
                                              "removal_done": removal_line(slug, number, entry["files"]), "shipped": shipped(top, state, base)})
        file("%s #%d reverted after its merge: %s" % (slug, number, ", ".join(entry.get("files") or []) or "no named files"),
             "a removal goal for the reverted part")
        return print("REVERTED %s #%d after its merge: what merged or shipped is not taken back.%s" % (slug, number, " Releases (the "
                     "manual cut, the automatic release and promote) hold until the removal of %s is in." %
                     ", ".join(entry["files"]) if entry.get("files") else " It is recorded only."))
    if cannot or kind == "stop":
        done or decisions.add(runs, slug, "revert", decision=number, effect="stop", files=[], by=by)
        why = "decision %d was reverted by %s%s" % (number, by, ": " + note if note else "")
        decisions.stop(runs, slug, why, by)
        state.update(status="stopped", finding=why)
        (save or (lambda s, text: outcomes.write_record(runs, s, text)))(state, why)
        file("%s stopped: %s" % (slug, why), "a new goal if the work is still wanted")
        return print("REVERTED %s #%d: the goal stops without merging" % (slug, number))
    decisions.add(runs, slug, "revert", decision=number, effect="files", files=files, by=by)
    file("%s #%d reverted: %s comes out" % (slug, number, ", ".join(files)), "a goal that takes it up")
    print("REVERTED %s #%d: take %s out. pr and merge hold until the branch has no change there and goal.py revert %s %d --met WHY "
          "records the done lines are still met; if they can't be, --cannot WHY stops the goal" % (slug, number, ", ".join(files), slug, number))


def cmd_revert(g, args):
    g.guards.operation_only(g, "revert a decision of", args.slug)
    g.pods and g.pods.merge_lock(os.path.dirname(os.path.dirname(g.state_dir())))  # the lock merge holds (RT8): a revert waits for it
    before = len(holds(g.root()))
    revert(g.root(), g.state_dir(), g.load(args.slug), args.number, "operation", "origin/" + g.config()["base"], args.met, args.cannot, save=g.save)
    len(holds(g.root())) > before and queue_removal(g, args.slug, args.number)
    return 0


def cmd_hold_clear(g, args):
    g.guards.operation_only(g, "clear a release hold of", args.slug)
    clear_hold(g.root(), args.slug, args.number, args.commit, "operation")
    print("CLEARED the hold of %s #%d" % (args.slug, args.number))
    return 0
