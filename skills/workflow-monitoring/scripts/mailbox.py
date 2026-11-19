#!/usr/bin/env python3
"""Email-first (#4785, #4671): each mail asks one question with numbered options and a recommendation, both machines share one
send budget, and a reply such as "1 recommended" is recorded as the owner's words and acted on.

usage: mailbox.py reply QID TEXT [--root DIR]   the operation session runs this with the owner's reply it read; QID is the
                                                 `Question id` line of the mail
       mailbox.py pending [--root DIR]          the questions mailed and not yet answered
       mailbox.py finding TITLE --feature PAGE --found REF [--text WORDS] [--owner-words oN] [--dry-run]
                                                OPS-25: file a finding of top or a machine session, without asking, as an ops-finding
                                                issue on "Backlog: PAGE" ("Other" if no page matches); REF is the TOP-DECISION or
                                                record that found it. Refuses a repeat of an open issue and a safety-class finding
                                                with no owner's words.

notify.py calls compose and claim for each new event (it mails through workflow-health's mail.py; this file never reads mail or a
secret). compose gives the body and remembers the question in <git common dir>/loop/mailbox.json. claim takes the event's key
and one send from the shared ledger, a git ref on origin both machines read (refs/loop/mail-ledger when `machine_sync` is on; else a local file),
so a second machine never mails an event the first one did, and no more than `notify_budget` (flow file, default 20) go out in
24 hours. A reply is "<n>", "<n> recommended", "recommended" or "approve" (the option numbered, or the recommended one), or the
owner's own words. A question about deleting, money, security or private data refuses a bare number or "approve": it needs the
owner's own typed words, which are recorded and sent as written. The answer goes to the worker through operate.py send --source
owner; a question with no goal goes to sessions.py owner-words.
"""
import argparse
import hashlib
import json
import os
import re
import subprocess
import sys
import time

os.environ.update(GIT_TERMINAL_PROMPT="0", GH_PROMPT_DISABLED="1", GIT_EDITOR="true", GIT_ASKPASS="true", SSH_ASKPASS="true")

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import live_board as lb  # noqa: E402
import machines  # noqa: E402

LEDGER = "refs/loop/mail-ledger"
FIXED = {"stopped": (["resume it", "retire it"], 0), "past ETA": (["ship now", "extend once", "defer"], 0),
         "released": (["noted, nothing to do"], 0)}
RISKY = re.compile(r"\b(delete|destroy|wipe|force[- ]push|reset --hard|rm -rf|secrets?|tokens?|passwords?|credentials?|api keys?|"
                   r"mail\.env|private|pay|payment|billing|purchase|spend|money|cost|\$\d)", re.I)
BARE = re.compile(r"^\W*(?:option\s*)?(\d+)?\W*(?:recommended|approve|approved|yes|ok|go)?\W*$", re.I)


def qid(key):
    return "q-" + hashlib.sha1(key.encode()).hexdigest()[:8]


def read_json(path):
    try:
        with open(path) as handle:
            found = json.load(handle)
        return found if isinstance(found, dict) else {}
    except (OSError, ValueError):
        return {}


def write_json(path, data):
    temp = path + ".tmp"
    with open(temp, "w") as handle:
        json.dump(data, handle, indent=1, sort_keys=True)
    os.replace(temp, path)


def options(kind, action):
    """([option words], index of the recommended one) for an event."""
    if kind in FIXED:
        return FIXED[kind]
    found = re.search(r"options?:\s*([^;\[]+)", action)
    words = re.findall(r'"([^"]+)"', found.group(1)) if found else []
    rec = re.search(r"recommended:\s*([^;\[]+)", action)
    if not words:
        return ["approve", "hold"], 0
    want = rec.group(1).strip().strip('"').lower() if rec else ""
    return words, next((i for i, w in enumerate(words) if w.lower() == want), 0)


def compose(folder, key, kind, slug, action, repo):
    """The mail body: the event, numbered options with the recommendation, how to reply, the question id. Remembers the question."""
    words, rec = options(kind, action)
    qa = qid(key)
    pending = read_json(os.path.join(folder, "mailbox.json"))
    pending[qa] = {"slug": slug, "kind": kind, "options": words, "recommended": rec, "risky": bool(RISKY.search(action)), "action": action[:300]}
    write_json(os.path.join(folder, "mailbox.json"), pending)
    rows = ["%d. %s%s" % (i, w, " (recommended)" if i - 1 == rec else "") for i, w in enumerate(words, 1)]
    return "\n".join([action, "", "Repo: %s. Goal: %s. Event: %s." % (repo, slug, kind), "", "Reply with a number:"] + rows + [
        "", 'Reply "1", "1 recommended" or "approve" to take an option. A step that deletes, spends money or touches security or '
        "private data needs your own words typed in the reply.", "Question id: " + qa]) + "\n"


def ledger(folder, cwd=None):
    """(data, token) from origin's ledger ref, or the local file."""
    if machines.shared(cwd):
        data, sha = machines.read_ref(LEDGER, cwd)
        return data or {}, sha
    return read_json(os.path.join(folder, "mail-ledger.json")), ""


def budget_of(flow):
    try:
        return int(read_json(os.path.expanduser(flow)).get("notify_budget", 20))
    except (TypeError, ValueError):
        return 20


def claim(folder, key, flow, cwd=None, release=False):
    """Take one event and one send from the shared ledger: True when it is ours to mail, "sent" when another machine mailed the
    event, "budget" when the budget is spent (the event stays unsent, so a later check-in tries again)."""
    for _ in range(4):
        data, token = ledger(folder, cwd)
        sent, times = data.setdefault("sent", {}), [t for t in data.get("times", []) if time.time() - t < 86400]
        if release:
            sent.pop(key, None)
        elif key in sent:
            return "sent"
        elif len(times) >= budget_of(flow):
            return "budget"
        else:
            sent[key], times = machines.me(), times + [time.time()]
        data["times"] = times
        if machines.shared(cwd):
            if machines.write_ref(LEDGER, data, token, cwd):
                return True
        else:
            write_json(os.path.join(folder, "mail-ledger.json"), data)
            return True
    return "budget"


def gh(args, root):
    try:
        return subprocess.run(["gh"] + args, cwd=root, capture_output=True, text=True, timeout=60)
    except (OSError, subprocess.SubprocessError) as error:
        return subprocess.CompletedProcess(args, 127, "", str(error))


def norm(title):
    return " ".join(re.sub(r"[^a-z0-9#-]+", " ", str(title).lower()).split())


def ids_of(title):
    return set(re.findall(r"#\d+|\b[A-Z]{2,5}-\d+\b", str(title)))


def repeat_of(title, open_issues):
    """The open issue a finding repeats: same normalised title, or same IDs in the title and half its words."""
    mine, ids = set(norm(title).split()), ids_of(title)
    for item in open_issues:
        theirs = set(norm(item["title"]).split())
        if norm(item["title"]) == norm(title) or (ids and ids == ids_of(item["title"]) and len(mine & theirs) * 2 >= len(mine | theirs)):
            return item["number"], item["title"]
    return None


def covered(root, record, title, page):
    """True when the owner-words record lists *, ops-findings, the page or an ID in the title."""
    import auto
    row = next((r for r in auto.owner_rows(root) if r[0] == record), None)
    return bool(row) and bool(({"*", "ops-findings", page} | ids_of(title)) & set(row[4].split(",")))


def file_finding(root, args):
    """(exit code, line): file one finding of the operation layer (OPS-25); nothing is filed when any check refuses."""
    import auto
    title, text, home = " ".join(args.title.split())[:90], " ".join(args.text.split()), os.path.expanduser("~")
    if not title or not args.found.strip():
        return 2, "REFUSED: give a title and --found (the TOP-DECISION or record that found it). Nothing was filed."
    if (len(home) > 1 and home in title + text) or re.search(r"[\w.+-]+@[\w-]+\.[\w.-]+", title + text):
        return 2, "REFUSED: the finding holds a private value. Nothing was filed."
    try:
        with open(os.path.join(root, ".loop", "docs.tsv"), encoding="utf-8") as handle:
            pages = [l.split("\t")[0].strip() for l in handle if l.strip() and l[0] != "#"]
    except OSError:
        pages = []
    page = next((p for p in pages if p.lower() == args.feature.strip().lower() and p != "Home"), "Other")
    for name, found in auto.CLASSES.items():
        if found.search(title + " " + text) and not (args.owner_words and covered(root, args.owner_words, title, page)):
            return 2, "REFUSED: safety class %s needs the owner's words (--owner-words oN listing %s or an ID in the title). Nothing was filed." % (name, page)
    done = gh(["issue", "list", "--state", "open", "--limit", "500", "--json", "number,title"], root)
    try:
        same = repeat_of(title, json.loads(done.stdout)) if not done.returncode else 0
    except ValueError:
        same = 0
    if same == 0:
        return 1, "REFUSED: could not read the open issues, so nothing was filed (%s)" % done.stderr.strip()[:100]
    if same:
        return 1, "REFUSED: repeats open issue #%d (%s). Nothing was filed." % same
    stone = "Backlog: " + page
    if args.dry_run:
        return 0, "WOULD file on %s: %s (found by %s; dry run)" % (stone, title, args.found)
    subprocess.run([sys.executable, os.path.join(HERE, "..", "..", "workflow-health", "scripts", "milestone.py"), "new", stone, "--live"],
                   cwd=root, capture_output=True, text=True, timeout=60)  # kept when it exists
    for label in ("backlog", "ops-finding"):
        gh(["label", "create", label, "--description", "Filed by the operation layer"], root)
    body = "<!-- loop-ops-finding %s -->\n\n%s\n\nFound by %s (operation layer).\n" % (hashlib.sha1(norm(title).encode()).hexdigest()[:12], text or title, args.found)
    done = gh(["issue", "create", "--title", title, "--label", "backlog,ops-finding", "--milestone", stone, "--body", body], root)
    if done.returncode:
        return 1, "FAILED: %s" % done.stderr.strip()[:160]
    number = re.search(r"/issues/(\d+)", done.stdout)
    line = "FILED #%s on %s: %s (found by %s)" % (number.group(1) if number else "?", stone, title, args.found)
    with open(os.path.join(auto.loop_dir(root), "findings.log"), "a", encoding="utf-8") as handle:
        handle.write("%s | %s\n" % (auto.stamp(), line))
    return 0, line


def say(text):
    print("MAILBOX: " + text)


def cmd_reply(args):
    folder = lb.loop_dir(args.root)
    asked = read_json(os.path.join(folder, "mailbox.json")).get(args.id)
    if not asked:
        say("REFUSED: no mailed question %s. Nothing was recorded." % args.id)
        return 2
    text, words = args.text.strip(), asked["options"]
    found = BARE.match(text)
    if found and re.search(r"\w", text):
        index = int(found.group(1)) - 1 if found.group(1) else asked["recommended"]
        if asked["risky"]:
            say("REFUSED: %s is about a step that deletes, spends money or touches security or private data; reply with your own "
                "words, not a number or approve. Nothing was recorded." % args.id)
            return 2
        if not 0 <= index < len(words):
            say("REFUSED: %s has options 1 to %d. Nothing was recorded." % (args.id, len(words)))
            return 2
        text = words[index]
    if not text:
        say("REFUSED: an empty reply. Nothing was recorded.")
        return 2
    slug = asked["slug"]
    if os.path.exists(os.path.join(folder, "runs", slug + ".json")):
        cmd = [sys.executable, os.path.join(HERE, "operate.py"), "send", slug, text, "--source", "owner"]
    else:
        cmd = [sys.executable, os.path.join(HERE, "sessions.py"), "owner-words", text, "--ids", args.id]
    done = subprocess.run(cmd, capture_output=True, text=True, cwd=args.root)
    if done.returncode:
        say("FAILED: %s" % (done.stdout + done.stderr).strip()[-200:])
        return 1
    pending = read_json(os.path.join(folder, "mailbox.json"))
    pending.pop(args.id, None)
    write_json(os.path.join(folder, "mailbox.json"), pending)
    say("RECORDED %s as the owner's words (%s) and sent them to %s" % (args.id, "own words" if text not in words else text, slug))
    return 0


def cmd_finding(args):
    code, line = file_finding(args.root, args)
    say(line)
    return code


def cmd_pending(args):
    asked = read_json(os.path.join(lb.loop_dir(args.root), "mailbox.json"))
    for key in sorted(asked):
        say("%s %s: %s" % (key, asked[key]["slug"], asked[key]["action"][:100]))
    say("%d question(s) waiting for a reply" % len(asked))
    return 0


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = parser.add_subparsers(dest="command", required=True)
    one = sub.add_parser("reply")
    one.add_argument("id")
    one.add_argument("text")
    one.set_defaults(func=cmd_reply)
    sub.add_parser("pending").set_defaults(func=cmd_pending)
    one = sub.add_parser("finding")
    one.add_argument("title")
    for name in ("feature", "found", "text", "owner-words"):
        one.add_argument("--" + name, default="")
    one.add_argument("--dry-run", action="store_true")
    one.set_defaults(func=cmd_finding)
    for item in sub.choices.values():
        item.add_argument("--root", default="")
    args = parser.parse_args()
    if not args.root:
        top = subprocess.run(["git", "rev-parse", "--show-toplevel"], capture_output=True, text=True)
        args.root = top.stdout.strip() or os.getcwd()
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
