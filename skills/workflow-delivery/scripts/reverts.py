#!/usr/bin/env python3
"""DLF-1.3's one-line revert. Each decision made in the owner's place is listed with one command and what it stops. A revert
only stops work: it undoes no safety fix, brings back no dropped part and reopens no safety item. A decision that let named
files go on is reverted by taking them out; any other stops the goal. After the merge nothing is taken back: the revert is
filed, and named files hold every release until their removal is in the commit released. Standard library only."""
import json
import os
import shlex
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import decisions  # noqa: E402
import dlf  # noqa: E402
import outcomes  # noqa: E402

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
    return bool(state.get("pr_head")) and outcomes.git(top, "merge-base", "--is-ancestor", state["pr_head"], base)[0] == 0


def holds_file(top):
    return os.path.join(outcomes.top_loop(top), "release-holds.jsonl")


def hold_rows(top):
    try:
        with open(holds_file(top), encoding="utf-8") as handle:
            return [json.loads(line) for line in handle if line.strip()]
    except FileNotFoundError:
        return []
    except (OSError, ValueError):
        refuse("the release holds can't be read (%s). Fix: repair the file" % holds_file(top), "ONE_REVIEW_HOLD")


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


def clear_hold(top, slug, number, commit, by):
    held = next((r for r in holds(top) if r["slug"] == slug and r["decision"] == number), None)
    held or refuse("no pending removal for %s #%s" % (slug, number), "ONE_REVIEW_HOLD")
    code, full = outcomes.git(top, "rev-parse", "--verify", "--quiet", commit + "^{commit}")
    full = full.strip()
    touches = not code and outcomes.git(top, "diff", "--quiet", "--no-ext-diff", full + "^1", full, "--", *held["files"])[0] == 1
    touches or refuse("%s is not a commit that changes %s" % (commit, ", ".join(held["files"])), "ONE_REVIEW_HOLD")
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
    if done and not cannot:
        return print("%s #%d was already reverted by %s; nothing changed" % (slug, number, done.get("by")))
    rel = dlf.brief(top, slug)[1]

    def file(what, words):
        dlf.file_line(top, runs, slug, rel, "break", "other", "revert%d%s" % (number, "stop" if cannot else ""), what, words, "keep it out")

    if not done and merged(top, state, base):
        decisions.add(runs, slug, "revert", decision=number, effect="after-merge", files=entry.get("files") or [], by=by)
        entry.get("files") and add_hold(top, {"op": "hold", "slug": slug, "decision": number, "files": entry["files"]})
        file("%s #%d reverted after its merge: %s" % (slug, number, ", ".join(entry.get("files") or []) or "no named files"),
             "a removal goal for the reverted part")
        return print("REVERTED %s #%d after its merge: what merged or shipped is not taken back.%s" % (slug, number, " Releases (the "
                     "manual cut, the automatic release and promote) hold until the removal of %s is in: queue that goal." %
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
    revert(g.root(), g.state_dir(), g.load(args.slug), args.number, "operation", "origin/" + g.config()["base"], args.met, args.cannot, save=g.save)
    return 0


def cmd_hold_clear(g, args):
    g.guards.operation_only(g, "clear a release hold of", args.slug)
    clear_hold(g.root(), args.slug, args.number, args.commit, "operation")
    print("CLEARED the hold of %s #%d" % (args.slug, args.number))
    return 0
