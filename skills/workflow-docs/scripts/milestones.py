#!/usr/bin/env python3
"""Milestone sync (DOC-17): a repo's GitHub milestones against an external Milestones page, both ways, opt-in.

Called by `docs.py sync`; there is no command of its own. A repo opts in by setting `milestones_source` in .loop/config.json to
a `url:<link>` or `mcp:<server>:<resource>` source (read as prd.read_link reads a PRD source); with none, nothing is read,
printed or called. A milestone is its title and `state | due`, `open | due 2026-12-01`, `closed | no due`: on the page one
line `- TITLE: state | due` each (split on the last `: `), on GitHub from `gh api repos/{owner}/{repo}/milestones`. What both
sides last agreed on is kept in .loop/milestones.md (and its .base); each side is compared with it, so:

  an addition or change on one side   DELTA milestones: TITLE the repo|the source changed (repo: ... | source: ...)
  a milestone that differs on both    CONFLICT milestones: TITLE both sides changed (...)
  a milestone only on the repo        the page is out of date: closed is the same as absent on the page

Nothing is overwritten. Each delta is posted once as a GitHub issue and once as a comment on the page (the PRD writer,
$LOOP_PRD_WRITER), kept in the same ledger as the PRD deltas under `milestones:TITLE`. `docs.py sync --accept
milestones:TITLE=repo|source` writes that side's text to the other: `source` creates, edits or closes the GitHub milestone
(a milestone only on the repo is closed), `repo` has the writer `replace TITLE` (adds when absent) or `remove TITLE` on the
page. A side that cannot be reached prints `not connected`, changes nothing and exits 0; --dry-run only reports (exit 1 on
a delta); --open leaves listing the ledger to audit.sync."""
import json
import os
import re
from os.path import join

import counting
import criteria as cr
import prd
from criteria import put, sha
from prd import out as post

KEY = "milestones:"
LINE = re.compile(r"^[-*] (.+): ((?:open|closed) \| (?:no due|due \d{4}-\d\d-\d\d))$")
API = "repos/{owner}/{repo}/milestones"


def parse(text):
    """{title: 'state | due'} of the `- TITLE: state | due` lines; the first of a repeated title wins."""
    found = {}
    for raw in text.splitlines():
        match = LINE.match(raw.strip())
        if match and "\t" not in match.group(1):
            found.setdefault(match.group(1).strip(), match.group(2))
    return found


def repo_side():
    """({title: text}, {title: number}, None) of the repo's milestones, or (None, None, why)."""
    ok, text = post("LOOP_GH", "api", API + "?state=all&per_page=100", "--paginate")
    if not ok:
        return None, None, text[:100]
    have, nums, at, decoder = {}, {}, 0, json.JSONDecoder()
    try:
        while at < len(text):
            if text[at].isspace():
                at += 1
                continue
            page, at = decoder.raw_decode(text, at)
            for item in page:
                title, state, due = item["title"], item["state"], item.get("due_on")
                if isinstance(title, str) and "\t" not in title and state in ("open", "closed"):
                    have[title.strip()] = "%s | %s" % (state, "due " + due[:10] if due else "no due")
                    nums[title.strip()] = item["number"]
    except (ValueError, TypeError, KeyError, AttributeError):
        return None, None, "gh printed something that is not a list of milestones"
    return have, nums, None


def to_repo(title, number, text):
    """(ok, why) of making the repo's milestone `title` read `text`: created, or edited by its number."""
    state, _, due = text.partition(" | ")
    args = ["-f", "title=" + title, "-f", "state=" + state, "-F" if due == "no due" else "-f", "due_on=null" if due == "no due" else "due_on=%sT00:00:00Z" % due[4:]]
    return post("LOOP_GH", "api", "-X", "PATCH" if number else "POST", "%s/%s" % (API, number) if number else API, *args)


def sync(root, args):
    source = counting.config_of(root).get("milestones_source")
    if not isinstance(source, str) or not source.startswith(("url:", "mcp:")):
        held = counting.ledger(root)  # a repo that dropped its source keeps no milestone rows, and none is listed
        if not args.dry_run and any(k.startswith(KEY) for k in held):
            counting.ledger(root, {k: v for k, v in held.items() if not k.startswith(KEY)})
        return 0
    if args.open:
        return 0
    dry, path = args.dry_run, join(root, ".loop", "milestones.md")
    body, why = prd.read_link(source)
    if body is None:
        print("not connected: milestones (%s): %s" % (source, why))
        return 0
    want = parse(body)
    have, nums, why = repo_side()
    if have is None:
        print("not connected: milestones (gh): %s" % why)
        return 0
    if not want:
        print("SKIPPED milestones: no `- TITLE: state | due` line in the source")
        return 0
    gone = [t for t in have if t not in want and have[t].startswith("closed")]
    for title in gone:
        want[title] = have[title]
    if os.path.exists(path):
        with open(path, encoding="utf-8") as handle:
            mine = handle.read()
        if not mine.startswith(cr.SYNC_MARK):
            print("SKIPPED milestones: .loop/milestones.md is not sync's own")
            return 0
        agreed = parse(mine)
    else:
        agreed = {t: x for t, x in have.items() if want.get(t) == x}
    start, held = dict(agreed), counting.ledger(root)
    for item in (a for a in args.accept if not dry and a.startswith(KEY)):
        title, _, side = item[len(KEY):].rpartition("=")
        r, s = have.get(title), want.get(title)
        if r == s or side not in ("repo", "source"):
            print("NO DELTA milestones: %s" % title)
            continue
        keep = (s or r.replace("open", "closed", 1)) if side == "source" else r
        ok, why = to_repo(title, nums.get(title), keep) if side == "source" else post("LOOP_PRD_WRITER", source, "replace" if r else "remove", title, input=r or "")
        if not ok:
            print("not connected: milestones (%s): %s" % ("gh" if side == "source" else source, why[:100]))
            continue
        for held_side in (have, want, agreed):
            if keep:
                held_side[title] = keep
            else:
                held_side.pop(title, None)
        row = held.pop(KEY + title, None)
        if row:
            post("LOOP_GH", "issue", "close", row[1], "--comment", "Accepted: %s." % side)
        print("ACCEPTED milestones: %s, the %s's text" % (title, side))
    found = []
    for title in sorted(set(have) | set(want)):
        r, s, a = have.get(title), want.get(title), agreed.get(title)
        if r == s:
            if title in gone:  # closed and not on the page: nothing agreed, so a reopen is the repo's change alone
                agreed.pop(title, None)
            else:
                agreed[title] = r
        else:
            found.append((title, "both sides" if (r != a) == (s != a) else "the repo" if r != a else "the source", r, s))
    for title in [t for t in agreed if t not in have and t not in want]:
        del agreed[title]
    for title, side, r, s in found:
        print("%s milestones: %s %s changed (repo: %s | source: %s)" % ("CONFLICT" if side == "both sides" else "DELTA", title, side, r or "-", s or "-"))
    print("MILESTONES: %d in step, %d with a delta" % (len(have.keys() | want.keys()) - len(found), len(found)))
    if dry:
        return 1 if found else 0
    for key in [k for k in held if k.startswith(KEY) and k[len(KEY):] not in [f[0] for f in found]]:
        post("LOOP_GH", "issue", "close", held.pop(key)[1], "--comment", "Resolved.")
    for title, side, r, s in found:
        key, text = KEY + title, "Delta in milestones %s: %s changed.\nRepo: %s\nSource: %s\nAccept one: docs.py sync --accept milestones:%s=repo|source" % (
            title, side, r or "-", s or "-", title)
        row = held.get(key) or [side, "", "0", ""]
        if row[1] and row[3] != sha(text):
            post("LOOP_GH", "issue", "comment", row[1], "--body", text)
            row[2] = "0"
        elif not row[1]:
            ok, made = post("LOOP_GH", "issue", "create", "--title", "DELTA milestones %s: %s changed" % (title, side), "--body", text)
            if not ok:
                print("not connected: milestones %s (gh): %s" % (title, made[:100]))
                continue
            row[1] = made.split("\n")[-1]
        if row[2] != "1":
            ok, why = post("LOOP_PRD_WRITER", source, "comment", input=text)
            row[2] = "1" if ok else "0"
            print("POSTED milestones %s: %s%s" % (title, row[1], "" if ok else " (not connected to %s: %s)" % (source, why[:80])))
        held[key] = [side, row[1], row[2], sha(text)]
    counting.ledger(root, held)
    if agreed != start or not os.path.exists(path):
        put(path, source, agreed, {t: sha(x) for t, x in agreed.items()})
    return 0
