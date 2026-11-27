#!/usr/bin/env python3
"""DLF-1.3's one question, at a goal's start. The message holds the frozen done lines, the numbered safety items, one code
and the only answer forms. goal.py start-items records operation's items, start-review shows the message, and start
accepts one owner record whose words are exactly one of those forms. What was approved is copied into the run record, so
later checks compare against that copy and never a record number alone. Standard library only."""
import hashlib
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import decisions  # noqa: E402
import safety_scan  # noqa: E402
import start_review  # noqa: E402

DELEGATED, RELAYED = "operation-top:delegated:", "operation-top"


def refuse(text, code):
    sys.exit("REFUSED: %s (%s)" % (text, code))


def check_files(top, files):
    """An item names exact files, or an existing folder inside a skill's scripts folder (RT1)."""
    isinstance(files, list) and all(isinstance(f, str) for f in files) or refuse("an item's files are a list of paths", "ONE_REVIEW_ITEMS")
    for path in files:
        clean = path.rstrip("/")
        outside = (not clean or os.path.isabs(path) or any(part in ("..", ".", "") for part in clean.split("/")) or "*" in clean
                   or re.fullmatch(r"skills(/[^/]+(/scripts)?)?", clean))
        folder = path.endswith("/") or os.path.isdir(os.path.join(top, clean))
        outside and refuse("%r is not one file or folder of this repository; an action outside it names no files" % path, "ONE_REVIEW_ITEMS")
        if folder and not (os.path.isdir(os.path.join(top, clean)) and re.match(r"skills/[^/]+/scripts/.+", clean)):
            refuse("%r: a folder is named only when it exists inside a skill's scripts folder; name exact files" % path, "ONE_REVIEW_ITEMS")


def checked(top, rows):
    isinstance(rows, list) or refuse("the items file holds a JSON list", "ONE_REVIEW_ITEMS")
    out = []
    for row in rows:
        known = isinstance(row, dict) and row.get("class") in safety_scan.dlf.SAFETY
        known or refuse("each item names one of these classes: %s" % "; ".join(safety_scan.dlf.SAFETY), "ONE_REVIEW_ITEMS")
        action = " ".join(str(row.get("action", "")).split())
        files = row.get("files", [])
        check_files(top, files)
        recommend = row.get("recommend", "")
        recommend in ("approve", "refuse") or refuse("each item recommends approve or refuse", "ONE_REVIEW_ITEMS")
        action or refuse("an item states one concrete action; a class with none is listed by the scan itself", "ONE_REVIEW_ITEMS")
        item = {"class": row["class"], "action": action, "files": files, "recommend": recommend, "approvable": True}
        change = [row.get(key) for key in ("page", "id", "text")]
        if any(change):
            all(isinstance(v, str) and v.strip() for v in change) and row["class"] == safety_scan.PROMISE or refuse(
                "a requirement change names its page, ID and exact new text, as a change to what a feature promises", "ONE_REVIEW_ITEMS")
            item.update(page=change[0], id=change[1], text=change[2].rstrip("\n"))
        out.append(item)
    return out


def numbered(g, state, rows):
    """Operation's items, then one unapprovable line for each class the scan found that no item covers."""
    slug = state["slug"]
    lines = g.done_lines(slug)
    touches = g.guards.touches_of(g.state_dir(), state)
    hits = safety_scan.text_classes(" ".join([state.get("goal", "")] + lines), paths=touches)
    items = [dict(item, by="scan" if item["class"] in hits else "operation") for item in rows]
    items += [{"class": name, "action": "", "files": [], "recommend": "refuse", "approvable": False, "by": "scan"}
              for name in hits if name not in [item["class"] for item in rows]]
    return [dict(item, n=number) for number, item in enumerate(items, 1)]


def code_of(state, items):
    return hashlib.sha256(json.dumps([state.get("done_sha"), items], sort_keys=True).encode()).hexdigest()[:6]


def forms(slug, code, items):
    out = ["approve start %s %s" % (slug, code)]
    items and out.append("approve start %s %s except N,N" % (slug, code))
    return out + ["reject start %s %s" % (slug, code)]


def message(g, state):
    review = state["start_review"]
    out = ["START REVIEW %s: %s" % (state["slug"], state.get("goal", "")), "Done lines (frozen):"] + g.done_lines(state["slug"])
    out.append("Safety items:" if review["items"] else "Safety items: none found, none added.")
    for item in review["items"]:
        where = ", ".join(item["files"]) or "no repository files"
        what = "%s (%s); recommended: %s" % (item["action"], where, item["recommend"]) if item["approvable"] else "not approvable: no concrete action"
        out.append("%d. %s: %s [%s]" % (item["n"], item["class"], what, "found by the scan" if item["by"] == "scan" else "added by operation"))
        item.get("text") and out.append("   new text of %s on %s:\n   %s" % (item["id"], item["page"], item["text"].replace("\n", "\n   ")))
    out += ["Answer with exactly one of:"] + ["  " + form for form in forms(state["slug"], review["code"], review["items"])]
    out.append("Without an answer the goal can have its idea and plan, but it doesn't build. A refused item takes the safe option.")
    return "\n".join(out)


def final(state):
    state.get("start_answer") and refuse("%s already has its start answer; a start review is answered and accepted once, and its "
                                         "items are final" % state["slug"], "ONE_REVIEW_ANSWERED")


def wanted(state):
    state.get("one_review") or state.get("start_required") or refuse(
        "%s is not marked and needs no start review here" % state["slug"], "ONE_REVIEW_ANSWER")


def cmd_items(g, args):
    g.guards.operation_only(g, "record the start items of", args.slug)
    state = g.held(args.slug)
    final(state)
    try:
        with open(args.file, encoding="utf-8") as handle:
            rows = json.load(handle)
    except (OSError, ValueError) as error:
        refuse("the items file can't be read: %s" % error, "ONE_REVIEW_ITEMS")
    items = numbered(g, state, checked(g.root(), rows))
    code = code_of(state, items)
    if (state.get("start_review") or {}).get("code") != code:
        state["start_review"] = {"items": items, "code": code, "at": decisions.stamp()}
        g.save(state, "start review items recorded, code %s" % code)
    text = message(g, state)
    print(text)
    send(g, state, text)  # only now: the items are final for this code
    return 0


def send(g, state, text):
    """Hand the message to the one mail sender, which mails each code once, tries a refused or over-budget one again, and
    keeps one that may have gone out. A text the private-name scan doesn't pass is never stored for mailing (DX D12)."""
    review, slug = state["start_review"], state["slug"]
    scan = g.private.scan(g.root(), None, texts={"start review": text})["state"]
    if scan not in ("clean", "off", "none"):
        return print("NOT MAILED %s: the private-name scan said %s; show it with goal.py start-review %s" % (slug, scan, slug))
    if review.get("mail") != text:
        review["mail"] = text
        g.save(state, "start review message ready, code %s" % review["code"])
    sender = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "workflow-monitoring", "scripts", "notify.py")
    done = g.run([sys.executable, sender, "start-mail", slug, "--root", g.root()])
    said = (done.stdout + done.stderr).strip()
    print(said or "NOT MAILED %s: the mail sender said nothing (exit %d)" % (slug, done.returncode))


def cmd_show(g, args):
    state = g.load(args.slug)
    if not state.get("start_review"):
        print("%s has no start review yet. Next: the operation session runs goal.py start-items %s --file ITEMS.json "
              "(a list of {class, action, files, recommend}; [] when there is none)." % (args.slug, args.slug))
        return 1
    print(message(g, state))
    answer = state.get("start_answer")
    answer and print("Answered by %s: %s" % (answer["record"], answer["text"]))
    return 0


def owner_row(g, rid):
    try:
        with open(os.path.join(os.path.dirname(g.state_dir()), "owner-words.tsv"), encoding="utf-8") as handle:
            rows = [line.rstrip("\n").split("\t") for line in handle]
        found = [row for row in rows if len(row) == 5 and row[0] == rid]
        return (found[0][1], found[0][2], json.loads(found[0][3])) if len(found) == 1 else None
    except (OSError, ValueError):
        return None


def judge(g, state, rid):
    """(verdict, refused item numbers, words, who) of an acceptable record; any other record refuses and stays unused."""
    review, slug = state["start_review"], state["slug"]

    def no(why):
        refuse("%s: %s. The record was not used. The current code is %s; answer with one of: %s" % (
            rid, why, review["code"], " | ".join(forms(slug, review["code"], review["items"]))), "ONE_REVIEW_ANSWER")

    review["code"] == code_of(state, review["items"]) or no("the recorded items changed; record them again")
    row = owner_row(g, rid)
    row or no("no such owner-words record")
    at, who, words = row
    found = re.fullmatch(r"(approve|reject) start %s ([0-9a-f]{6})(?: except (\d+(?: ?, ?\d+)*))?" % re.escape(slug), str(words).strip())
    found and not (found.group(1) == "reject" and found.group(3)) or no("its words are not one of the answer forms")
    found.group(2) == review["code"] or no("its code is not the current one")
    at > review["at"] or no("it is not later than the message")
    who.startswith(DELEGATED) and no("a delegated record never answers a start review")
    review["items"] and who.startswith(RELAYED) and no("with safety items the answer is the owner's own words, not a relayed record")
    refused = sorted({int(n) for n in found.group(3).replace(" ", "").split(",")}) if found.group(3) else []
    approvable = [item["n"] for item in review["items"] if item["approvable"]]
    set(refused) <= set(approvable) or no("except names an item that is not there or can't be approved")
    for path in sorted(os.listdir(g.state_dir())):  # one answer, one goal
        other = path[:-5] if path.endswith(".json") and path.count(".") == 1 else ""
        if other and other != slug:
            held = g.load(other).get("start_answer") or {}
            held.get("record") == rid and no("it already answered %s" % other)
    return found.group(1), refused, str(words).strip()


def commit_mark(g, state):
    """The mark goes into the committed goal file once, and onto origin when the branch is there; a failed push leaves the
    answer unaccepted, and the same record is tried again (DX D14)."""
    top, slug, branch = g.root(), state["slug"], state.get("branch") or "loop/" + state["slug"]
    g.git("branch", "--show-current") == branch or refuse("not on %s. Fix: run this in the goal's worktree" % branch, "ONE_REVIEW_ANSWER")
    if not start_review.MARK.search(start_review.committed(top, "HEAD", slug)):
        path = g.goal_file(slug)
        g.write(path, start_review.marked_text(g.read(path)))
        g.git("commit", "-m", "Goal: %s takes one review" % slug, "--", path)
    seen = start_review.git(top, "ls-remote", "origin", "refs/heads/" + branch)
    seen.returncode and refuse("origin can't be read, so it is unknown whether %s is there. Fix: reach origin, then run this "
                               "again with the same record" % branch, "ONE_REVIEW_PUSH")
    if not seen.stdout.strip():
        return
    scan = g.private.scan(top, "origin/" + g.config()["base"])["state"]
    scan in ("clean", "off") or refuse("the private-name scan said %s, so the mark was not pushed and the answer is not accepted. "
                                       "Fix it, then run this again with the same record" % scan, "ONE_REVIEW_PUSH")
    pushed = g.run(["git", "push", "origin", branch])
    pushed.returncode and refuse("the push failed, so the answer is not accepted: %s. Run this again with the same record"
                                 % pushed.stderr.strip()[:300], "ONE_REVIEW_PUSH")


def cmd_start(g, args):
    g.guards.operation_only(g, "answer the start review of", args.slug)
    state, slug, rid = g.held(args.slug), args.slug, args.owner_record
    final(state)
    wanted(state)
    state.get("start_review") or refuse("%s has no start review yet. Fix: goal.py start-items %s --file ITEMS.json" % (slug, slug),
                                        "ONE_REVIEW_ANSWER")
    verdict, refused, words = judge(g, state, rid)
    commit_mark(g, state)
    runs = g.state_dir()
    state.update({} if state.get("one_review") else start_review.mark(runs, slug, "goal.py start"))
    os.path.exists(decisions.ledger(runs, slug)) or decisions.create(runs, slug, by="goal.py start")
    items = [dict(item, approved=verdict == "approve" and item["approvable"] and item["n"] not in refused)
             for item in state["start_review"]["items"]]
    if not any(e["kind"] == "start" and e.get("record") == rid for e in decisions.entries(runs, slug)):
        decisions.add(runs, slug, "start", record=rid, verdict=verdict)
        for item in items:
            verdict == "approve" and not item["approved"] and decisions.add(
                runs, slug, "refused-item", item=item["n"], safety=item["class"], files=item["files"],
                taken="not approved: the safe option applies to it, in the build or dropped and filed")
        verdict == "reject" and decisions.stop(runs, slug, "the start review was rejected", rid)
    state["start_answer"] = {"record": rid, "at": decisions.stamp(), "code": state["start_review"]["code"], "verdict": verdict,
                             "text": words, "items": items}
    if verdict == "reject":
        state.update(status="stopped", finding="the start review was rejected (%s)" % rid)
    g.save(state, "start review %sd by %s" % (verdict.rstrip("e") + "e", rid))
    if verdict == "reject":
        print("REJECTED %s: stopped for good. Fix: retire it; a changed goal is a new one." % slug)
    else:
        left = [str(item["n"]) for item in items if not item["approved"]]
        print("STARTED %s: %d of %d items approved%s. Nothing more is asked of the owner at this start." % (
            slug, len(items) - len(left), len(items), "; not approved: " + ", ".join(left) if left else ""))
    return 0
