#!/usr/bin/env python3
"""Deliver first (DLF-1): the stop table, the filing routine and ledger, the budget rule, the cut check and the setting.

A goal does not wait for the owner unless the stop is on the safety list. Every other stop becomes a line, one comment on the
release's one deliver-first issue; every text written outside the run record passes the private-name scan inside write()."""
import hashlib
import json
import os
import re
import sys
import urllib.parse

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import private  # noqa: E402

LABEL, ISSUE = "deliver-first", "repos/{owner}/{repo}/issues"
KEY = re.compile(r"<!-- dlf key=(\S+) id=(\S+) -->")
EVENT = re.compile(r"<!-- dlf-event key=(\S+) state=(\w+) -->")


def mem(runs, slug):
    try:
        got = json.load(open(os.path.join(runs, slug + ".dlf.json")))
    except (OSError, ValueError):
        got = {}
    return {"lines": {}, "queue": [], "local": [], "cap": "", **(got if isinstance(got, dict) else {})}


def keep(runs, slug, held):
    path = os.path.join(runs, slug + ".dlf.json")
    json.dump(held, open(path + ".tmp", "w"), indent=1)
    os.replace(path + ".tmp", path)


def write(top, runs, slug, kind, text, do):
    """The one door out: scan the text, then do(text). A text that fails the scan stays in the run record and is not written."""
    got = private.scan(top, None, texts={kind: text})
    if got["state"] not in ("clean", "off"):
        held = mem(runs, slug)
        held["local"].append({"kind": kind, "text": text, "why": got["state"]})
        keep(runs, slug, held)
        return False, "kept local: the private-name scan said %s" % got["state"]
    return do(text)


def pages(top, path):
    """Every page of a GitHub list, or None when a read fails: a failed read is never an empty list."""
    code, out = private.gh(top, "api", "--paginate", "--slurp", path)
    try:
        got = None if code else json.loads(out)
    except ValueError:
        got = None
    return [x for p in got for x in (p if isinstance(p, list) else [p])] if isinstance(got, list) else None


def find_issue(top, rel):
    """The release's issue number (the lowest with its label), 0 when a complete read lists none, None when the read fails."""
    rows = pages(top, "%s?state=all&per_page=100&labels=%s" % (ISSUE, urllib.parse.quote("%s:%s" % (LABEL, rel))))
    rows = None if rows is None else [r for r in rows if "pull_request" not in r]
    return None if rows is None else min([r["number"] for r in rows], default=0)


def comments(top, number):
    rows = pages(top, "%s/%d/comments?per_page=100" % (ISSUE, number))
    return None if rows is None else sorted(rows, key=lambda r: r["id"])


def post(top, path, field, text, *more):
    code, out = private.gh(top, "api", "-X", "POST", path, "-f", "%s=%s" % (field, text), *more)
    return not code, out


def ensure_issue(top, runs, slug, rel):
    """Find the release issue or create it once; after creating, keep the lowest number and close our duplicate."""
    number = find_issue(top, rel)
    if number != 0:
        return number
    body = "Lines the goals of release %s filed instead of waiting for the owner. One comment a line; accept with a comment: " \
           "accept-all <id> <id> ...\n<!-- dlf-issue -->" % rel
    ok, out = write(top, runs, slug, "issue", body, lambda t: post(top, ISSUE, "title", "Deliver-first lines: %s" % rel, "-f", "body=" + t,
                                                                  "-f", "labels[]=%s:%s" % (LABEL, rel)))
    if not ok:
        return None
    mine, lowest = json.loads(out)["number"], find_issue(top, rel)
    if lowest and lowest != mine:
        private.gh(top, "api", "-X", "PATCH", "%s/%d" % (ISSUE, mine), "-f", "state=closed")
        return lowest
    return mine


def line_text(lid, slug, stop, subject, what, words, rec, key):
    return '[ ] %s %s | %s | %s - %s; settle with: "%s"; recommend: %s\n<!-- dlf key=%s id=%s -->' % (
        lid, slug, stop, subject, what, words, rec, key, lid)


def file_line(top, runs, slug, rel, stop, subject, occ, what, words, rec):
    """File one line, found or created by its key (goal|stop|subject|occurrence). Returns (id, status): status is '' when filed,
    'queued' when the issue can't be reached (filing retries later), 'local' when the scan kept the text in the run record."""
    key = "|".join((slug, stop, subject, re.sub(r"[^A-Za-z0-9_.:-]", "-", str(occ))[:40]))
    held = mem(runs, slug)
    if key in held["lines"]:
        return held["lines"][key], ""
    item = dict(stop=stop, subject=subject, occ=occ, what=what, words=words, rec=rec, rel=rel)
    number = ensure_issue(top, runs, slug, rel)
    rows = comments(top, number) if number else None
    if rows is None:
        if not number and mem(runs, slug)["local"]:
            return "", "local"
        held = mem(runs, slug)
        held["queue"] = [q for q in held["queue"] if q["rel"] != rel or q["occ"] != occ or q["stop"] != stop] + [item]
        keep(runs, slug, held)
        return "", "queued"
    for row in rows:
        mark = KEY.search(row["body"])
        if mark and mark[1] == key:
            held["lines"][key] = mark[2]
            keep(runs, slug, held)
            return mark[2], ""
    n = 1 + sum(1 for k in held["lines"] if k.startswith("%s|%s|" % (slug, stop)))
    lid = "%s-%s-%d" % (slug, stop, n)
    ok, out = write(top, runs, slug, "line", line_text(lid, slug, stop, subject, what, words, rec, key),
                    lambda t: post(top, "%s/%d/comments" % (ISSUE, number), "body", t))
    if not ok and out.startswith("kept local"):
        return "", "local"
    if not ok and not any((KEY.search(r["body"]) or [0, 0])[1] == key for r in comments(top, number) or []):
        held["queue"] = held["queue"] + [item]  # the write failed and a re-read shows no line: file it at the next step
        keep(runs, slug, held)
        return "", "queued"
    held["lines"][key] = lid
    keep(runs, slug, held)
    return lid, ""


def retry(top, runs, slug):
    """Re-file the lines queued while the issue was out of reach (each step and the cut call this)."""
    held = mem(runs, slug)
    todo, held["queue"] = held["queue"], []
    keep(runs, slug, held)
    return [file_line(top, runs, slug, q["rel"], q["stop"], q["subject"], q["occ"], q["what"], q["words"], q["rec"]) for q in todo]


def post_event(top, runs, slug, rel, key, state, text):
    def do(t):
        number = find_issue(top, rel)
        return post(top, "%s/%d/comments" % (ISSUE, number), "body", t) if number else (False, "no release issue")
    return write(top, runs, slug, "event", "%s\n<!-- dlf-event key=%s state=%s -->" % (text, key, state), do)[0]


def cap_line(top, runs, slug, rel, spend, estimate, old, new):
    what = 'reached its 2x cap at %d of %d (budget %d, now %d)' % (spend, estimate, old, new)
    return file_line(top, runs, slug, rel, "cap", "other", "cap", what, "accept to continue or decline to queue a patch goal",
                     "keep working at the cap")


def convert(top, runs, slug, rel, key, lid, what, words):
    """A declined line becomes a patch goal: one queue line with a stable slug derived from the line key (a resume adds no second)."""
    patch = "patch-" + hashlib.sha1(key.encode()).hexdigest()[:8]
    path = os.path.join(top, ".loop", "queue.md")
    text = "- slug: %s | level: quick | touches: .loop/findings.md | goal: Settle deliver-first line %s: %s | done: The line %s is settled: %s\n" % (
        patch, lid, what, lid, words)

    def add(t):
        if "slug: %s |" % patch not in open(path).read():
            open(path, "a").write(t)
        return True, patch
    return write(top, runs, slug, "patch", text, add)[0]
