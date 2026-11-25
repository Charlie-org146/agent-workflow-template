#!/usr/bin/env python3
"""Deliver first, the release cut (DLF-1.4): the ledger read from the issue's comments, the cut check and the patch-goal conversion,
moved whole from dlf.py to keep each script under its size line."""
import hashlib
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import private  # noqa: E402
from dlf import EVENT, ISSUE, KEY, cfg, comments, find_issue, post, retry, write  # noqa: E402


def post_event(top, runs, slug, rel, key, state, text):
    def do(t):
        number = find_issue(top, rel)
        return post(top, "%s/%d/comments" % (ISSUE, number), "body", t) if number else (False, "no release issue")
    return write(top, runs, slug, "event", "%s\n<!-- dlf-event key=%s state=%s -->" % (text, key, state), do)[0]


def convert(top, runs, slug, rel, key, lid, what, words):
    patch, path = "patch-" + hashlib.sha1(key.encode()).hexdigest()[:8], os.path.join(top, ".loop", "queue.md")
    text = "- slug: %s | level: quick | touches: .loop/findings.md | goal: Settle deliver-first line %s: %s | done: %s is settled: %s\n" % (
        patch, lid, what, lid, words)

    def add(t):
        if "slug: %s |" % patch not in (open(path).read() if os.path.exists(path) else ""):
            open(path, "a").write(t)
        return True, patch
    return write(top, runs, slug, "patch", text, add)[0]


def ledger(top, rel, owner, loop):
    number = find_issue(top, rel)
    rows = comments(top, number) if number else []
    if number is None or rows is None:
        return None
    lines, notes = {}, []
    for r in rows:
        who, body = r["user"]["login"], r["body"]
        mark, event = KEY.search(body), EVENT.search(body)
        if mark and mark[1] not in lines:
            lines[mark[1]] = dict(id=mark[2], goal=mark[1].split("|")[0], text=body.split("\n")[0][4:], state="open", cid=r["id"], key=mark[1])
        for verb, rest in [] if event or mark else re.findall(r"^\s*(accept-all|accept|decline)\b(.*)$", body, re.M):
            ids = re.findall(r"[\w.:-]+", rest)
            if who != owner or not ids:
                notes.append("ignored %s by %s: %s" % (verb, who, "not the owner" if who != owner else "no line ids named"))
            for l in [l for l in lines.values() if l["id"] in ids]:
                if l["cid"] > r["id"]:
                    notes.append("ignored %s of %s: filed after it" % (verb, l["id"]))
                elif who == owner and l["state"] in ("open", "accepted") and not (verb != "decline" and l["state"] != "open"):
                    l["state"], l["at"] = "converted" if verb == "decline" else "accepted", r["created_at"]
            known = [l["id"] for l in lines.values()]
            notes += ["ignored %s of %s: no such id" % (verb, i) for i in ids if who == owner and i not in known]
        if event and event[1] in lines:
            l = lines[event[1]]
            ok = who == loop and event[2] == "closed" and l["state"] == "accepted"
            l["state"] = "closed" if ok else l["state"]
            notes += [] if ok or who == loop and event[2] in ("open", "filed") else ["ignored %s by %s on %s" % (event[2], who, l["id"])]
    return lines, notes, number


def cut(top, runs, rel, owner="", loop=""):
    import glob
    if not os.path.isdir(runs):
        return "read failed: the run-record folder %s can't be read" % os.path.basename(runs)
    owner = owner or cfg(top).get("owner_login") or os.environ.get("LOOP_OWNER_LOGIN", "")
    loop, out = loop or private.gh(top, "api", "user", "-q", ".login")[1].strip(), []
    for f in glob.glob(os.path.join(runs, "*.dlf.json")):
        goal = os.path.basename(f)[:-9]
        retry(top, runs, goal)
        try:
            held = json.load(open(f))
        except (OSError, ValueError):
            out.append("read failed: %s" % os.path.basename(f))
            continue
        queued = [q for q in held.get("queue", []) if q.get("rel") == rel]
        out += ["unfiled: %d line(s) of %s never reached the issue" % (len(queued), goal)] * bool(queued)
        out += ["local: %s holds %d text(s) the private-name scan refused" % (goal, len(held.get("local", [])))] * bool(held.get("local"))
    got = ledger(top, rel, owner, loop)
    if got is None:
        return "\n".join(["read failed: release %s's issue can't be read completely" % rel] + out)
    lines, notes, number = got
    if lines and not owner:
        return "owner acceptance can't be read: owner_login is not set (set LOOP_OWNER_LOGIN, or owner_login in a private config)"
    todo = sorted((l for l in lines.values() if l["state"] == "open"), key=lambda l: (l["goal"], l["cid"]))
    for l in [l for l in lines.values() if l["state"] == "converted"]:
        convert(top, runs, l["goal"], rel, l["key"], l["id"], l["text"], "declined")
        patch = "patch-" + hashlib.sha1(l["key"].encode()).hexdigest()[:8]
        try:
            merged = json.load(open(os.path.join(runs, patch + ".json"))).get("release") == "merged"
        except (OSError, ValueError):
            merged = False
        out += [] if merged else ["converted: %s waits for patch goal %s to merge; merge it, then cut" % (l["id"], patch)]
    if not todo and not out:
        [post_event(top, runs, l["goal"], rel, l["key"], "closed", "%s closed after the accept" % l["id"]) for l in lines.values() if l["state"] == "accepted"]
        return ""
    head = ["Release %s has %d open deliver-first line(s) on issue #%d. Accept them all in one comment, posted as %s:\n  accept-all %s" % (
        rel, len(todo), number, owner, " ".join(l["id"] for l in todo))] * bool(todo)
    for goal in sorted({l["goal"] for l in todo}):
        head += [goal + ":"] + ["  [ ] %s %s" % (l["id"], l["text"]) for l in todo if l["goal"] == goal]
    return "\n".join(head + out + notes + ["accepted %s at %s" % (l["id"], l["at"]) for l in lines.values() if l["state"] == "accepted"])
