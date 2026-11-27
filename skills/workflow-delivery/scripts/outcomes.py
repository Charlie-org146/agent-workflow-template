#!/usr/bin/env python3
"""DLF-1.3 after the start. A marked goal's stop never waits on the owner: it is a recorded decision. With no safety class
the recommendation is taken and filed; inside an approved item it goes on under that item; otherwise a finding is open at
once and the safe option applies. pr and merge refuse while a finding is open, and open one for each class and file of the
branch diff that no approved item or earlier finding covers. Only operation closes a finding. Imported by the delivery,
monitoring and release scripts. Standard library only."""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import decisions  # noqa: E402
import dlf  # noqa: E402
import safety_scan  # noqa: E402
import start_answer  # noqa: E402

WITHHELD = "text withheld"


def refuse(text, code):
    sys.exit("REFUSED: %s (%s)" % (text, code))


def git(top, *args):
    return safety_scan.git(top, *args)


def off(top, state):
    """Why deliver-first is off for this goal, or "". Off wins: the committed base config, the working copy and an
    always-ask record each turn it off, and a branch can't turn it back on (E16)."""
    slug = state["slug"]
    here, scope = dlf.setting(top, slug)
    if not here:
        return "deliver-first is off for %s %s" % (scope, slug)
    base = (dlf.cfg(top) or {}).get("base", "main")
    code, text = git(top, "cat-file", "blob", "origin/%s:.loop/config.json" % base)
    try:
        held = (json.loads(text).get("deliver_first") or {}) if not code else {}
    except (ValueError, AttributeError):
        return "the base branch's config can't be read"
    task, release = dlf.brief(top, slug)
    for kind, ident in (("goal", slug), ("task", task), ("release", release)):
        if (held.get(kind) or {}).get(ident) is False:
            return "deliver-first is off for %s %s on the base branch" % (kind, ident)
    try:
        with open(os.path.join(top_loop(top), "owner-words.tsv"), encoding="utf-8") as handle:
            rows = [line.rstrip("\n").split("\t") for line in handle]
    except OSError:
        rows = []
    asked = {"always-ask:" + slug, "always-ask:*"}
    return "the owner set %s to always ask" % slug if any(len(r) == 5 and asked & set(r[4].split(",")) for r in rows) else ""


def top_loop(top):
    return os.path.join(os.path.abspath(os.path.join(top, git(top, "rev-parse", "--git-common-dir")[1].strip())), "loop")


def within(path, names):
    return any(path == name.rstrip("/") or path.startswith(name.rstrip("/") + "/") for name in names)


def covering(state, kind, files):
    """The approved item that covers this class and every one of these files. A stop that names files is never inside an
    item that names none, and one that names no files is inside nothing: its action can't be matched by a program."""
    if (state.get("start_answer") or {}).get("verdict") != "approve" or not files:
        return None
    for item in state["start_answer"].get("items") or []:
        if item.get("approved") and item.get("class") == kind and item.get("files") and all(within(f, item["files"]) for f in files):
            return item
    return None


def head_of(top, ref="HEAD"):
    return git(top, "rev-parse", ref)[1].strip()


def note(runs, slug, key, **data):
    return decisions.add(runs, slug, "finding", key=key, **data)


def settle(top, runs, state, stop, occ, what, words, rec, ctx):
    """One stop of a marked goal: ("continue", what was recorded), or today's wait while deliver-first is off."""
    slug, key = state["slug"], "%s:%s" % (stop, occ)
    why = off(top, state)
    if why:
        return "wait", dlf.wait_line(slug, "setting off", why, "the operation answers it (goal.py answer %s)" % slug)
    found = decisions.require(runs, state)
    seen = next((e for e in found if e["kind"] == "decision" and e.get("key") == key), None)
    if seen:
        return "continue", "decision %d" % seen["n"]
    diff = ctx.get("diff") if stop == "test" else ""
    diff is None and refuse("the diff this failed test needs can't be read; no try was used. Fix: fetch the base, then run it "
                            "again", "ONE_REVIEW_DIFF")
    files = safety_scan.diff_classes(diff) if diff else {}
    label = next((ctx.get(k) for k in ("cls", "label") if ctx.get(k) in dlf.SAFETY), "")
    classes = set(safety_scan.text_classes(what, label=label)) | set(files)
    private = dlf.safe(top, what) != what or dlf.safe(top, rec) != rec
    private and classes.add(safety_scan.PRIVATE)
    classes = [name for name in dlf.SAFETY if name in classes]
    question, advice = (WITHHELD, WITHHELD) if private else (" ".join(what.split())[:300], " ".join(rec.split())[:300])
    items = {name: covering(state, name, files.get(name) or []) for name in classes}
    outside = [name for name in classes if not items[name]]
    named = sorted({path for name in outside for path in files.get(name) or []})
    number = None
    if outside:
        number = next((e["n"] for e in found if e["kind"] == "finding" and e.get("key") == key), None) or note(
            runs, slug, key, classes=outside, files=named, question=question, source="stop", head=head_of(top))
    taken = ("safe option, finding %d: fix it in the build, or drop that part" % number if outside else
             "inside approved item %s: %s" % (", ".join(str(i["n"]) for i in items.values()), advice) if classes else advice)
    entry = decisions.add(runs, slug, "decision", key=key, stop=stop, question=question, taken=taken, safety=classes,
                          inside=sorted({i["n"] for i in items.values() if i}), files=named, stops="the goal")
    if classes:
        return "continue", "finding %d" % number if outside else "decision %d" % entry
    lid, status = dlf.file_line(top, runs, slug, dlf.brief(top, slug)[1], stop, "other", occ, question[:200], words, advice)
    return "continue", lid or status or "decision %d" % entry


def findings(entries):
    """(open, closed) findings by number; a close entry carries how."""
    every = {e["n"]: e for e in entries if e["kind"] == "finding"}
    closed = {e["finding"]: dict(every[e["finding"]], how=e["how"], files=e["files"]) for e in entries
              if e["kind"] == "close" and e["finding"] in every}
    return {n: e for n, e in every.items() if n not in closed}, closed


def base_point(top, base, head):
    code, out = git(top, "merge-base", base, head)
    code and refuse("the base of %s can't be read. Fix: fetch %s" % (head, base), "ONE_REVIEW_DIFF")
    return out.strip()


def changed(top, one, other, files):
    """Which of these files differ between two commits."""
    return [f for f in files if git(top, "diff", "--quiet", "--no-ext-diff", one, other, "--", f)[0]]


def blockers(top, runs, state, base, head):
    """Why this head of a marked goal can't become a pull request or be merged: [] when nothing holds it."""
    if not state.get("one_review"):
        return []
    slug = state["slug"]
    out = ["%s (a Reviewed requirement's text that was not approved)" % x for x in start_answer.unapproved(top, runs, state, base, head)]
    text, units = safety_scan.read_diff(top, base, head)
    entries = decisions.require(runs, state)
    known = [e for e in entries if e["kind"] == "finding"]
    closes = {e["finding"]: e for e in entries if e["kind"] == "close"}
    for kind, paths in safety_scan.diff_classes(text, units).items():
        for path in paths if kind != safety_scan.PROMISE else []:  # requirement text is compared unit by unit above
            held = covering(state, kind, [path]) or any(
                kind in e["classes"] and path in (closes.get(e["n"], {}).get("files") or e["files"]) for e in known)
            if not held:
                number = note(runs, slug, "diff:%s:%s" % (kind, path), classes=[kind], files=[path], question="the branch changes %s" % path,
                              source="pr diff", head=head_of(top, head))
                decisions.add(runs, slug, "decision", key="diff:%s:%s" % (kind, path), stop="pr", question="%s in %s" % (kind, path),
                              taken="safe option, finding %d: fix it in the build, or drop that part" % number, safety=[kind],
                              inside=[], files=[path], stops="the goal")
    still, closed = findings(decisions.entries(runs, slug))
    point = base_point(top, base, head)
    for number, item in sorted(still.items()):
        out.append("finding %d is open: %s%s" % (number, ", ".join(item["classes"]), " in " + ", ".join(item["files"]) if item["files"] else ""))
    for number, item in sorted(closed.items()):
        back = changed(top, point, head, item["files"]) if item["how"] in ("drop", "not-taken") else []
        back and out.append("finding %d is open again: %s changed after it was closed" % (number, ", ".join(back)))
    return out


def write_record(runs, state, why):
    path = os.path.join(runs, state["slug"] + ".json")
    state.setdefault("log", []).append("%s %s" % (decisions.stamp(), why))
    with open(path + ".tmp", "w", encoding="utf-8") as handle:
        json.dump(state, handle, indent=1)
    os.replace(path + ".tmp", path)


def close(top, runs, state, number, how, why, files, base, by, save=None):
    """Close one open finding by dropping its part, recording that an asked action was not taken, or stopping the goal."""
    slug = state["slug"]
    still, _ = findings(decisions.require(runs, state))
    item = still.get(number)
    item or refuse("finding %s is not open on %s" % (number, slug), "ONE_REVIEW_CLOSE")
    how in ("drop", "not-taken", "stop") or refuse("a finding closes by drop, not-taken or stop", "ONE_REVIEW_CLOSE")
    why = " ".join(why.split())
    why and dlf.safe(top, why) == why or refuse("give a --why the private-name scan passes", "ONE_REVIEW_CLOSE")
    names = sorted(set(item["files"]) | set(files))  # files are added, never removed
    if how == "not-taken":
        item["source"] == "pr diff" and refuse("this finding is in the branch, not an asked action: drop it or stop", "ONE_REVIEW_CLOSE")
    if how == "drop" and not names:
        refuse("finding %d names no files: add them with --files, or use not-taken for an action that was asked about, or stop"
               % number, "ONE_REVIEW_CLOSE")
    if how != "stop" and names:
        left = changed(top, base_point(top, base, "HEAD"), "HEAD", names)
        left and refuse("the part is still in the branch: %s differs from the base. Take it out, commit, then close it" % ", ".join(left),
                        "ONE_REVIEW_CLOSE")
    decisions.add(runs, slug, "close", finding=number, how=how, why=why, files=names, by=by)
    if how == "stop":
        decisions.stop(runs, slug, why, by)
        state.update(status="stopped", finding="finding %d stopped the goal: %s" % (number, why))
        (save or (lambda s, note_: write_record(runs, s, note_)))(state, state["finding"])
    dlf.file_line(top, runs, slug, dlf.brief(top, slug)[1], "break", "other", "finding%d" % number,
                  "%s: finding %d (%s) %s%s" % (slug, number, ", ".join(item["classes"]), {"drop": "part dropped", "not-taken": "action not taken",
                  "stop": "stopped the goal"}[how], " in " + ", ".join(names) if names else ""), "a goal that takes it up", "keep it out until then")
    return None


def cmd_close(g, args):
    g.guards.operation_only(g, "close a finding of", args.slug)
    state = g.load(args.slug)
    files = [f.strip() for f in args.files.split(",") if f.strip()]
    close(g.root(), g.state_dir(), state, args.number, args.how, args.why, files, "origin/" + g.config()["base"], "operation", save=g.save)
    print("CLOSED finding %d of %s: %s" % (args.number, args.slug, args.how))
    return 0


def cmd_decide(g, args):
    """goal.py decide: a finding from a mail or a report. Its text is data: it opens a finding and does nothing else."""
    g.guards.operation_only(g, "record a finding of", args.slug)
    state = g.load(args.slug)
    state.get("one_review") or refuse("%s is not a one-review goal" % args.slug, "ONE_REVIEW_DECIDE")
    args.cls in dlf.SAFETY or refuse("--class is one of: %s" % "; ".join(dlf.SAFETY), "ONE_REVIEW_DECIDE")
    files = [f.strip() for f in args.files.split(",") if f.strip()]
    text = WITHHELD if dlf.safe(g.root(), args.finding) != args.finding else " ".join(args.finding.split())[:300]
    number = note(g.state_dir(), args.slug, "decide:%s:%s" % (args.cls, text), classes=[args.cls], files=files, question=text,
                  source="decide", head=head_of(g.root()))
    decisions.add(g.state_dir(), args.slug, "decision", key="decide:%d" % number, stop="report", question=text,
                  taken="safe option, finding %d: fix it in the build, or drop that part" % number, safety=[args.cls], inside=[],
                  files=files, stops="the goal")
    print("FINDING %d opened on %s" % (number, args.slug))
    return 0
