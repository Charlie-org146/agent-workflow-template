#!/usr/bin/env python3
"""Email-first (#4785, #4671): each mail asks one question with numbered options and a recommendation, both machines share one
send budget, and a reply such as "1 recommended" is recorded as the owner's words and acted on.

usage: mailbox.py reply QID TEXT [--root DIR]   the operation session runs this with the owner's reply it read; QID is the
                                                 `Question id` line of the mail
       mailbox.py pending [--root DIR]          the questions mailed and not yet answered
       mailbox.py plan-review SLUG | plan-record SLUG FILE|- | plan-accept SLUG N --owner-record ID   the red team's pre-build plan
                    review (HLT-2): the reviewer's input; record its A/R/B<n>/C lines with a timestamp under <git common dir>/loop/redteam/;
                    the owner accepts a principle break by an owner-words.tsv record. goal.py step build refuses on an unaccepted break.

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


def cmd_pending(args):
    asked = read_json(os.path.join(lb.loop_dir(args.root), "mailbox.json"))
    for key in sorted(asked):
        say("%s %s: %s" % (key, asked[key]["slug"], asked[key]["action"][:100]))
    say("%d question(s) waiting for a reply" % len(asked))
    return 0


ASK = ("Red-team this plan against every principle. Reply with lines only, no edits and no decisions: `A: <an unverified assumption>`, "
       "`R: <a risk>`, `B<n>: <how the plan breaks principle n>` (n is its number above) and `C: <a cheaper path>`.")


def sha_of(path):
    try:
        with open(path, "rb") as handle:
            return hashlib.sha1(handle.read().replace(b"\r\n", b"\n")).hexdigest()
    except OSError:
        return ""


def loop_dir(root):
    out = subprocess.run(["git", "rev-parse", "--git-common-dir"], capture_output=True, text=True, cwd=root).stdout.strip() or ".git"
    return os.path.join(os.path.abspath(os.path.join(root, out)), "loop")


def principles(root):
    try:
        with open(os.path.join(root, "docs", "wiki", "Principles.md"), encoding="utf-8") as handle:
            text = handle.read()
    except OSError:
        text = ""
    return text, [int(n) for n in re.findall(r"^## (\d+)\. ", text, re.M)] or list(range(1, 9))


def plan_input(root, slug):
    """The red-team reviewer's input for one goal: its goal file, design and plan, the principles, and the request. Reads only."""
    goals, parts = os.path.join(root, ".loop", "goals", slug), []
    if not os.path.exists(goals + ".plan.md"):
        sys.exit("REFUSED: %s has no plan to red-team. Fix: run the plan step first." % slug)
    for title, path in (("GOAL", goals + ".md"), ("DESIGN", goals + ".design.md"), ("PLAN", goals + ".plan.md")):
        with open(path, encoding="utf-8") as handle:
            parts.append("== %s ==\n%s" % (title, handle.read().strip()))
    return "\n\n".join(["RED-TEAM PLAN INPUT " + slug] + parts + ["== PRINCIPLES ==\n" + principles(root)[0].strip(), ASK])


def plan_parse(text, nums):
    """{'A': [...], 'R': [...], 'C': [...], 'B': [(n, text)]}; refuses a B line with no principle number, or one the principles lack."""
    got = {"A": [], "R": [], "C": [], "B": []}
    for line in str(text or "").splitlines():
        found = re.match(r"^\W*([ARC]|B\s*\d*)\s*:\s*(\S.*)$", line)
        if not found:
            continue
        key, words = found.group(1)[0], found.group(2).strip()
        if key == "B":
            n = re.sub(r"\D", "", found.group(1))
            if not n or int(n) not in nums:
                sys.exit("REFUSED: a principle break must name its principle, B<n> with n one of %s. Fix: send `B<n>: <break>`; nothing was recorded." % nums)
            got["B"].append((int(n), words))
        else:
            got[key].append(words)
    return got


def plan_record(root, slug, text, now=None):
    """Write the findings with a timestamp under <git common dir>/loop/redteam/ (never a repo file); returns the break lines."""
    now, got = now if now is not None else time.time(), plan_parse(text, principles(root)[1])
    folder = os.path.join(loop_dir(root), "redteam")
    os.makedirs(folder, exist_ok=True)
    write_json(os.path.join(folder, "plan-%s-%s.json" % (slug, time.strftime("%Y%m%dT%H%M%SZ", time.gmtime(now)))), {
        "slug": slug, "at": now, "time": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(now)), "assumptions": got["A"], "risks": got["R"],
        "cheaper": got["C"], "breaks": [{"principle": n, "text": w} for n, w in got["B"]],
        "plan_sha": sha_of(os.path.join(root, ".loop", "goals", slug + ".plan.md"))})
    return ["BREAK principle %d: %s" % item for item in got["B"]] or ["NO BREAKS"]


def plan_accept(root, slug, n, record):
    """The operation session's: the owner accepts principle n's break for this goal, by an owner-words.tsv record."""
    try:
        with open(os.path.join(loop_dir(root), "owner-words.tsv"), encoding="utf-8") as handle:
            known = {row.split("\t")[0] for row in handle}
    except OSError:
        known = set()
    if record not in known:
        sys.exit("REFUSED: %s is not an owner-words.tsv record. Fix: the operation session records the owner's words first (sessions.py owner-words)." % record)
    path = os.path.join(loop_dir(root), "redteam", "plan-%s.accept.json" % slug)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    write_json(path, dict(read_json(path), **{str(n): record}))
    return "ACCEPTED principle %d for %s by %s" % (n, slug, record)


def plan_main(argv):
    parser = argparse.ArgumentParser(prog="mailbox.py")
    parser.add_argument("command", choices=["plan-review", "plan-record", "plan-accept"])
    parser.add_argument("slug")
    parser.add_argument("arg", nargs="?", default="")
    parser.add_argument("--owner-record", default="")
    parser.add_argument("--root", default="")
    args = parser.parse_args(argv)
    root = args.root or subprocess.run(["git", "rev-parse", "--show-toplevel"], capture_output=True, text=True).stdout.strip() or os.getcwd()
    if args.command == "plan-review":
        print(plan_input(root, args.slug))
    elif args.command == "plan-record":
        print("\n".join(plan_record(root, args.slug, sys.stdin.read() if args.arg == "-" else open(args.arg, encoding="utf-8").read())))
    else:
        print(plan_accept(root, args.slug, int(args.arg), args.owner_record))
    return 0


def main():
    if sys.argv[1:2] and sys.argv[1].startswith("plan-"):
        return plan_main(sys.argv[1:])
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = parser.add_subparsers(dest="command", required=True)
    one = sub.add_parser("reply")
    one.add_argument("id")
    one.add_argument("text")
    one.set_defaults(func=cmd_reply)
    sub.add_parser("pending").set_defaults(func=cmd_pending)
    for item in sub.choices.values():
        item.add_argument("--root", default="")
    args = parser.parse_args()
    if not args.root:
        top = subprocess.run(["git", "rev-parse", "--show-toplevel"], capture_output=True, text=True)
        args.root = top.stdout.strip() or os.getcwd()
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
