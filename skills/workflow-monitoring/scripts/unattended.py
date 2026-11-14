#!/usr/bin/env python3
"""MON-18: what the operation session needs in order to keep running unattended.

usage: unattended.py sends [add TO | reset | status]       cross-session sends since the owner's last message
       unattended.py loop [created [--days N] | status]    the check-in loop's expiry (7 days by default)
       unattended.py standing add TEXT [--scope merge] [--goals A,B|all] | check SLUG | revoke ID
       unattended.py selfcheck                             what is missing before an unattended run

The records live in <git common dir>/loop/ (sends.json, checkin-loop.json, standing.tsv).
  sends       the app pauses cross-session messages after 20 sends with no owner message: sessions.py send logs each one,
              the operation session logs its own message-tool sends with `sends add`, an owner message is `sends reset`;
              from 16 the status carries a WARNING
  loop        `loop status` says RECREATE inside the last 24 hours and EXPIRED after the end: the operation session
              re-creates its check-in loop itself, then runs `loop created`
  standing    one instruction replaces a go per merge; only the operation session adds one (a worker is refused), and a
              worker at pr runs `standing check SLUG`: STANDING <id> means go on without another go
  selfcheck   MISSING permission mode (defaultMode default or plan holds cross-session messages for approval), MISSING
              routine rules (permissions.py check, workflow-docs), MISSING main checkout behind origin; CHECK lines are
              what could not be read; SELFCHECK OK or exit 1
"""
import argparse
import datetime
import importlib.util
import json
import os
import subprocess
import sys

CAP, WARN_AT, LOOP_DAYS = 20, 16, 7
HERE = os.path.dirname(os.path.abspath(__file__))


def run(*args, cwd=None):
    done = subprocess.run(["git"] + list(args), cwd=cwd, capture_output=True, text=True, timeout=60)
    return done.returncode, done.stdout.strip()


def common():
    code, out = run("rev-parse", "--git-common-dir")
    return os.path.join(os.path.abspath(out), "loop") if code == 0 and out else ""


def now():
    return datetime.datetime.now(datetime.timezone.utc)


def stamp(when=None):
    return (when or now()).strftime("%Y-%m-%dT%H:%M:%SZ")


def load(path, default):
    try:
        with open(path, encoding="utf-8") as handle:
            return json.load(handle)
    except (OSError, ValueError):
        return default


def save(path, data):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="\n") as handle:
        json.dump(data, handle)


def sent(to=""):
    """Log one send; never raises, so a send does not fail on the log."""
    try:
        path = os.path.join(common(), "sends.json")
        held = load(path, {"since": stamp(), "count": 0})
        held["count"] = int(held.get("count", 0)) + 1
        save(path, held)
    except (OSError, ValueError, subprocess.SubprocessError):
        pass


def sends_status():
    held = load(os.path.join(common(), "sends.json"), {"since": "", "count": 0})
    count = int(held.get("count", 0))
    line = "SENDS %d of %d since %s (%d left)" % (count, CAP, held.get("since") or "the start", max(0, CAP - count))
    return line + ("; WARNING: ask the owner for any message, it resets the count" if count >= WARN_AT else ""), count >= WARN_AT


def loop_status():
    held = load(os.path.join(common(), "checkin-loop.json"), {})
    if not held.get("expires"):
        return "LOOP none recorded: run `loop created` after creating the check-in loop", True
    left = datetime.datetime.strptime(held["expires"], "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=datetime.timezone.utc) - now()
    hours = int(left.total_seconds() // 3600)
    if left.total_seconds() <= 0:
        return "LOOP EXPIRED: re-create the check-in loop now, then run `loop created`", True
    text = "LOOP expires in %dd %dh" % (hours // 24, hours % 24)
    return (text.replace("LOOP expires", "LOOP RECREATE: expires") + ", re-create it before then") if hours < 24 else text, hours < 24


def lines():
    """(the Operation line for Coming up, the Needs-you items) the check-in prints."""
    try:
        sends, warn_sends = sends_status()
        loop, warn_loop = loop_status()
    except (OSError, ValueError, subprocess.SubprocessError):
        return "", []
    rows = [item[0] for item in standing_rows() if item[5] == ""]
    held = "standing %s" % ", ".join(rows) if rows else "no standing instruction"
    out = "- Operation: %s; %s; %s" % (sends.split(";")[0], loop.split(",")[0].replace("LOOP RECREATE: ", "loop "), held)
    needs = (["Send cap near: %s" % sends] if warn_sends else []) + (["Check-in loop: %s" % loop] if warn_loop else [])
    return out, needs


def standing_path():
    return os.path.join(common(), "standing.tsv")


def standing_rows():
    """(id, stamp, scope, goals, text, revoked) per record."""
    try:
        with open(standing_path(), encoding="utf-8") as handle:
            return [(row + [""] * 6)[:6] for row in (line.rstrip("\n").split("\t") for line in handle) if len(row) >= 5]
    except OSError:
        return []


def standing(args):
    rows = standing_rows()
    if args.action == "add":
        if os.environ.get("LOOP_ROLE") == "worker":
            sys.exit("REFUSED: only the operation session records a standing instruction. Nothing was written.")
        if not args.text.strip():
            sys.exit("REFUSED: give the instruction's text. Nothing was written.")
        label = "s%d" % (len(rows) + 1)
        os.makedirs(common(), exist_ok=True)
        with open(standing_path(), "a", encoding="utf-8", newline="\n") as handle:
            handle.write("%s\t%s\t%s\t%s\t%s\t\n" % (label, stamp(), args.scope, args.goals, json.dumps(args.text, ensure_ascii=False)))
        print("STANDING %s recorded for %s: %s" % (label, args.goals, args.scope))
        return 0
    if args.action == "revoke":
        if not any(row[0] == args.text for row in rows):
            sys.exit("REFUSED: no standing instruction %s." % args.text)
        with open(standing_path(), "w", encoding="utf-8", newline="\n") as handle:
            for row in rows:
                handle.write("\t".join(row[:5] + [stamp() if row[0] == args.text else row[5]]) + "\n")
        print("STANDING %s revoked" % args.text)
        return 0
    for row in rows:  # check
        if not row[5] and row[2] == "merge" and (row[3] == "all" or args.text in row[3].split(",")):
            print("STANDING %s: %s" % (row[0], json.loads(row[4])))
            return 0
    print("NO STANDING instruction covers %s: wait for the operation session's go" % args.text)
    return 1


def mode_line():
    top = run("rev-parse", "--show-toplevel")[1] or "."
    for path in (os.path.join(top, ".claude", "settings.local.json"), os.path.join(top, ".claude", "settings.json"),
                 os.path.join(os.path.expanduser("~"), ".claude", "settings.json")):
        mode = (load(path, {}).get("permissions") or {}).get("defaultMode")
        if mode:
            return ("MISSING permission mode: defaultMode is %s, which holds cross-session messages for approval. Fix: acceptEdits or auto" % mode) \
                if mode in ("default", "plan") else ""
    return "CHECK permission mode: no settings file sets defaultMode; make sure this session is not in Default or Plan mode"


def routine_lines():
    path = os.path.join(os.path.dirname(HERE), "..", "workflow-docs", "scripts", "permissions.py")
    if not os.path.exists(path):
        return ["CHECK routine rules: workflow-docs is not installed beside workflow-monitoring"]
    spec = importlib.util.spec_from_file_location("permissions", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    root = run("rev-parse", "--show-toplevel")[1] or "."
    return [("CHECK " if line.startswith("NOTE") else "MISSING routine rules: ") + line.replace("NOTE ", "", 1) for line in module.check(root)]


def main_line():
    gitdir = common()
    main = os.path.dirname(os.path.dirname(gitdir)) if gitdir.endswith(os.path.join(".git", "loop")) else ""
    if not main:
        return ""
    try:
        with open(os.path.join(main, ".loop", "config.json"), encoding="utf-8") as handle:
            base = json.load(handle).get("base") or "main"
    except (OSError, ValueError):
        base = "main"
    if run("fetch", "origin", base, cwd=main)[0] != 0:
        return "CHECK main checkout: origin could not be reached, so it may be behind"
    code, behind = run("rev-list", "--count", "%s..origin/%s" % (base, base), cwd=main)
    return "MISSING main checkout: %s commit(s) behind origin/%s. Fix: ask a free worker to fast-forward it (MON-16)" % (behind, base) \
        if code == 0 and behind.isdigit() and int(behind) > 0 else ""


def selfcheck():
    found = [line for line in [mode_line()] + routine_lines() + [main_line()] if line]
    print("\n".join(found) if found else "SELFCHECK OK")
    return 1 if any(line.startswith("MISSING") for line in found) else 0


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = parser.add_subparsers(dest="cmd", required=True)
    item = sub.add_parser("sends")
    item.add_argument("action", nargs="?", default="status", choices=("add", "reset", "status"))
    item.add_argument("to", nargs="?", default="")
    item = sub.add_parser("loop")
    item.add_argument("action", nargs="?", default="status", choices=("created", "status"))
    item.add_argument("--days", type=int, default=LOOP_DAYS)
    item = sub.add_parser("standing")
    item.add_argument("action", choices=("add", "check", "revoke"))
    item.add_argument("text", nargs="?", default="")
    item.add_argument("--scope", default="merge", choices=("merge",))
    item.add_argument("--goals", default="all")
    sub.add_parser("selfcheck")
    args = parser.parse_args()
    if args.cmd == "selfcheck":
        return selfcheck()
    if args.cmd == "standing":
        return standing(args)
    if args.cmd == "sends":
        if args.action == "add":
            sent(args.to)
        elif args.action == "reset":
            save(os.path.join(common(), "sends.json"), {"since": stamp(), "count": 0})
            print("SENDS reset: 0 of %d" % CAP)
            return 0
        print(sends_status()[0])
        return 0
    if args.action == "created":
        save(os.path.join(common(), "checkin-loop.json"), {"created": stamp(), "expires": stamp(now() + datetime.timedelta(days=args.days))})
    print(loop_status()[0])
    return 0


if __name__ == "__main__":
    sys.exit(main())
