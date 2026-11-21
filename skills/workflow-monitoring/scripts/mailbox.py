#!/usr/bin/env python3
"""Email-first (#4785, #4671): one question, numbered options and a recommendation per mail; machines share a send
budget; "1 recommended" is recorded as the owner's words.

usage: mailbox.py reply QID TEXT [--root DIR]   reply; QID: mail's `Question id`
       mailbox.py pending [--root DIR]          unanswered mailed questions
       mailbox.py finding TITLE --feature PAGE --found REF [--text WORDS] [--owner-words oN] [--dry-run]
                                                OPS-1: file on "Backlog: PAGE" (else "Other"); REF found it.
                                                Refuses repeats and safety findings without owner's words.

       mailbox.py watch ID --pr N [--arm --head SHA]   watcher job (TD487; ID: the goal's slug): the tick resumes it when checks end;
                                                 green at SHA with --arm runs merge.py ID --go-head SHA once, another head waits, red
                                                 records the checks (--arm: operation)
       mailbox.py tick | install | uninstall | status   300 s launch agent plist (LOOP_AGENTS_DIR); not loaded here;
                                                 tick runs jobs, then checkin.py

notify.py calls compose/claim (mail: workflow-health/mail.py).
compose stores questions (loop/mailbox.json). claim takes an event key and send from the ledger
(refs/loop/mail-ledger, else a file), preventing duplicate mail across machines.
`notify_budget` (20) caps sends per 24 hours. A reply is "<n>", "<n> recommended", "recommended", "approve" or owner's
words; a question about deleting, money, security or private data needs the owner's typed words. The answer goes to the worker via
operate.py send --source owner (else sessions.py owner-words).
"""
import argparse
import hashlib
import json
import os
import plistlib
import re
import subprocess
import sys
import tempfile
import time

os.environ.update(GIT_TERMINAL_PROMPT="0", GH_PROMPT_DISABLED="1", GIT_EDITOR="true", GIT_ASKPASS="true", SSH_ASKPASS="true")

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import live_board as lb  # noqa: E402
import proctree  # noqa: E402
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
    """([option words], recommended index) for an event."""
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
    """The mail body: event, numbered options, reply how-to, question id."""
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
    """Take one event and a send from the shared ledger: True when ours, "sent" when another machine mailed it, "budget"
    when the budget is spent (the event stays unsent; a later check-in tries again)."""
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
    """The open issue a finding repeats: same title, or same IDs and half its words."""
    mine, ids = set(norm(title).split()), ids_of(title)
    for item in open_issues:
        theirs = set(norm(item["title"]).split())
        if norm(item["title"]) == norm(title) or (ids and ids == ids_of(item["title"]) and len(mine & theirs) * 2 >= len(mine | theirs)):
            return item["number"], item["title"]
    return None


def covered(root, record, title, page):
    """True when the owner-words record lists *, ops-findings, the page or an ID."""
    import auto
    row = next((r for r in auto.owner_rows(root) if r[0] == record), None)
    return bool(row) and bool(({"*", "ops-findings", page} | ids_of(title)) & set(row[4].split(",")))


def file_finding(root, args):
    """(exit code, line): file one finding (OPS-1); a refusal files nothing."""
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
    with tempfile.NamedTemporaryFile("w", suffix=".md", delete=False, encoding="utf-8", newline="\n") as f:
        f.write(body)
    try:
        done = gh(["issue", "create", "--title", title, "--label", "backlog,ops-finding", "--milestone", stone, "--body-file", f.name], root)
    finally:
        os.remove(f.name)
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


LABEL = "com.workflow-loop.tick"
MERGE = os.path.join(HERE, "..", "..", "workflow-release", "scripts", "merge.py")


def jobs_dir(root):
    common = subprocess.run(["git", "rev-parse", "--git-common-dir"], cwd=root, capture_output=True, text=True).stdout.strip() or ".git"
    return os.path.join(os.path.abspath(os.path.join(root, common)), "loop", "watchers")


def now():
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


def cmd_watch(args):
    if args.arm:
        proctree.require_operation(args.root, "an armed watcher job")
        if not args.head:
            sys.exit("REFUSED: an armed job names its head (--head SHA).")
    path = os.path.join(jobs_dir(args.root), re.sub(r"[^\w.-]", "_", args.id) + ".json")
    os.makedirs(os.path.dirname(path), exist_ok=True)
    write_json(path, {"id": args.id, "pr": args.pr, "arm": args.arm, "head": args.head, "pod": machines.graph.pod_id(), "state": "waiting", "result": "", "at": now()})
    print("WATCH %s: pull request %d" % (args.id, args.pr))


def gh_json(root, *argv):
    done = subprocess.run(["gh", *argv], cwd=root, capture_output=True, text=True)
    try:
        return json.loads(done.stdout) if done.returncode == 0 else None
    except ValueError:
        return None


def resume(root, path):
    """One watcher job: when its checks end, green arms (if asked), red reports."""
    job = read_json(path)
    if job.get("state") != "waiting" or not isinstance(job.get("pr"), int):
        return
    got = gh_json(root, "pr", "view", str(job["pr"]), "--json", "state,headRefOid,statusCheckRollup")
    checks = [c for c in (got or {}).get("statusCheckRollup") or [] if isinstance(c, dict)]
    if got is None or not checks or any((c.get("status") or "COMPLETED") != "COMPLETED" or c.get("state") in ("PENDING", "EXPECTED") for c in checks):
        return
    if got.get("state") != "OPEN":
        job.update(state="done", result="pull request " + str(got.get("state")).lower())
    else:
        bad = sorted({c.get("name") or c.get("context") or "?" for c in checks if (c.get("conclusion") or c.get("state")) not in ("SUCCESS", "SKIPPED", "NEUTRAL")})
        if bad:
            job.update(state="red", result="red: " + ", ".join(bad))
        elif job.get("arm") and job.get("head") != got["headRefOid"]:
            job["result"] = "head moved to " + got["headRefOid"][:9]
        elif job.get("arm"):  # the job id is the goal's slug
            done = subprocess.run([sys.executable, MERGE, job["id"], "--go-head", job["head"]], cwd=root, capture_output=True, text=True, env=dict(os.environ, LOOP_POD_ID=job.get("pod", "")))
            job.update(state="armed" if done.returncode == 0 else "arm-failed", result=(done.stdout + done.stderr).strip()[-200:])
        else:
            job.update(state="green", result="green at " + got["headRefOid"][:9])
    job["at"] = now()
    write_json(path, job)
    print("WATCHED %s: %s (%s)" % (job["id"], job["state"], job["result"]))


def cmd_tick(args):
    folder = jobs_dir(args.root)
    for name in sorted(os.listdir(folder)) if os.path.isdir(folder) else []:
        if name.endswith(".json"):
            resume(args.root, os.path.join(folder, name))
    for script in ("checkin.py", "board_page.py"):  # read and print only
        subprocess.run([sys.executable, os.path.join(HERE, script)] + ["checkin"] * (script != "checkin.py"), cwd=args.root)
    return 0


def plist_path():
    return os.path.join(os.environ.get("LOOP_AGENTS_DIR") or os.path.expanduser("~/Library/LaunchAgents"), LABEL + ".plist")


def cmd_install(args):
    logs = os.path.join(os.environ.get("LOOP_SCHEDULE_HOME") or os.path.expanduser("~/.workflow-loop/schedule"), "log", "restart-tick.log")
    os.makedirs(os.path.dirname(logs), exist_ok=True)
    os.makedirs(os.path.dirname(plist_path()), exist_ok=True)
    with open(plist_path(), "wb") as handle:
        plistlib.dump({"Label": LABEL, "ProgramArguments": [sys.executable, os.path.abspath(__file__), "tick", "--root", args.root], "WorkingDirectory": args.root,
                       "StartInterval": 300, "StandardOutPath": logs, "StandardErrorPath": logs,
                       "EnvironmentVariables": {"PATH": "/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin"}}, handle)
    print("WROTE %s (not loaded; the owner loads it)" % plist_path())


def cmd_uninstall(args):
    gone = os.path.exists(plist_path())
    if gone:
        os.remove(plist_path())
    print("REMOVED %s (the owner unloads it)" % plist_path() if gone else "NOTHING to remove")


def cmd_status(args):
    loaded = subprocess.run([os.environ.get("LOOP_LAUNCHCTL") or "launchctl", "print", "gui/%d/%s" % (getattr(os, "getuid", lambda: 0)(), LABEL)], capture_output=True).returncode == 0
    print("tick plist: %s; loaded: %s" % ("present" if os.path.exists(plist_path()) else "missing", loaded))


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
    one = sub.add_parser("watch")
    one.add_argument("id")
    one.add_argument("--pr", type=int, required=True)
    one.add_argument("--arm", action="store_true")
    one.add_argument("--head", default="")
    one.set_defaults(func=cmd_watch)
    for name, func in (("tick", cmd_tick), ("install", cmd_install), ("uninstall", cmd_uninstall), ("status", cmd_status)):
        sub.add_parser(name).set_defaults(func=func)
    for item in sub.choices.values():
        item.add_argument("--root", default="")
    args = parser.parse_args()
    if not args.root:
        top = subprocess.run(["git", "rev-parse", "--show-toplevel"], capture_output=True, text=True)
        args.root = top.stdout.strip() or os.getcwd()
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
