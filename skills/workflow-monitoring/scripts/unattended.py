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
              routine rules (audit.py permissions check, workflow-docs), MISSING main checkout behind origin; CHECK lines are
              what could not be read; SELFCHECK OK or exit 1
"""
import argparse
import datetime
import glob
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile

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
        if not common():
            return
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
    try:
        left = datetime.datetime.strptime(held["expires"], "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=datetime.timezone.utc) - now()
    except (KeyError, ValueError, TypeError):
        return "LOOP none recorded: run `loop created` after creating the check-in loop", True
    hours = int(left.total_seconds() // 3600)
    if left.total_seconds() <= 0:
        return "LOOP EXPIRED: re-create the check-in loop now, then run `loop created`", True
    text = "LOOP expires in %dd %dh" % (hours // 24, hours % 24)
    return (text.replace("LOOP expires", "LOOP RECREATE: expires") + ", re-create it before then") if hours < 24 else text, hours < 24


def lines():
    """(the Operation line for Coming up, the Needs-you items) the check-in prints."""
    if not common():
        return "", []
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
            try:
                print("STANDING %s: %s" % (row[0], json.loads(row[4])))
            except ValueError:
                print("STANDING %s" % row[0])
            return 0
    print("NO STANDING instruction covers %s: wait for the operation session's go" % args.text)
    return 1


def mode_line():
    top = run("rev-parse", "--show-toplevel")[1] or "."
    for path in (os.path.join(top, ".claude", "settings.local.json"), os.path.join(top, ".claude", "settings.json"),
                 os.path.join(os.path.expanduser("~"), ".claude", "settings.json")):
        held = load(path, {})
        mode = ((held.get("permissions") if isinstance(held, dict) else None) or {}).get("defaultMode")
        if mode:
            return ("MISSING permission mode: defaultMode is %s, which holds cross-session messages for approval. Fix: acceptEdits or auto" % mode) \
                if mode in ("default", "plan") else ""
    return "CHECK permission mode: no settings file sets defaultMode; make sure this session is not in Default or Plan mode"


def routine_lines():
    path = os.path.join(os.path.dirname(HERE), "..", "workflow-docs", "scripts", "audit.py")
    if not os.path.exists(path):
        return ["CHECK routine rules: workflow-docs is not installed beside workflow-monitoring"]
    root = run("rev-parse", "--show-toplevel")[1] or "."
    done = subprocess.run([sys.executable, path, "permissions", "check", "--repo", root], capture_output=True, text=True, timeout=120)
    return [("CHECK " if line.startswith("NOTE") else "MISSING routine rules: ") + line.replace("NOTE ", "", 1)
            for line in done.stdout.splitlines() if line.strip() and line != "PERMISSIONS OK"]


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


KINDS = (("mail", r"e-?mail|inbox|gmail"), ("calendar", r"calendar"), ("files", r"file store|dropbox|drive"),
         ("notify", r"notification channel|slack|push notification"))
HOME = os.path.expanduser("~/.workflow-loop")


def need(name, ok, fix):
    return "OK %s" % name if ok else "MISSING %s. Fix: %s" % (name, fix)


def symlinks():
    folder = tempfile.mkdtemp()
    try:
        os.symlink(HERE, os.path.join(folder, "l"))
        return os.path.islink(os.path.join(folder, "l"))
    except (OSError, NotImplementedError):
        return False
    finally:
        shutil.rmtree(folder, ignore_errors=True)


def prerequisites():
    """SET-11: what this machine needs before setup writes anything, each gap with its exact fix."""
    gh = shutil.which("gh")
    signed = bool(gh) and subprocess.run([gh, "auth", "status"], capture_output=True).returncode == 0
    return [need("git", shutil.which("git"), "install git"), need("python3", sys.version_info >= (3, 8), "install Python 3.8 or newer"),
            need("gh installed", gh, "install the GitHub CLI"),
            need("gh signed in", signed, "run gh auth login --web: it prints a one-time code you can enter from a phone"),
            need("real symlinks", symlinks(), "on Windows turn on Developer Mode, or run the install with MSYS=winsymlinks:nativestrict"),
            need("platform", sys.platform in ("darwin", "linux", "win32"), "use macOS, Linux or Windows"),
            "OK private-name list" if os.path.exists(os.environ.get("LOOP_PRIVATE_NAMES") or os.path.join(HOME, "private-names")) else
            "NOTE private-name list: none. Fix: add ~/.workflow-loop/private-names; @public or @repos=a,b scopes a line"]


def followed():
    try:
        with open(os.path.join(HOME, "repos"), encoding="utf-8") as handle:
            return [x.strip() for x in handle if x.strip()]
    except OSError:
        return []


def connectors():
    """SET-14: each connector a followed repo's PRDs name, probed read-only ($LOOP_CONNECTOR_PROBE KIND: exit 0 connected, 3 needs
    sign-in, else missing). Never attaches or enables one."""
    probe, found = os.environ.get("LOOP_CONNECTOR_PROBE", "").split(), []
    for path in followed():
        pages = glob.glob(os.path.join(path, "docs", "wiki", "*.md"))
        text = " ".join(open(page, encoding="utf-8", errors="replace").read() for page in pages)
        for kind, pattern in KINDS:
            if re.search(pattern, text, re.I):
                code = subprocess.run(probe + [kind], capture_output=True).returncode if probe else None
                found.append(("OK %s %s: connected" % (os.path.basename(path), kind)) if code == 0 else
                             "MISSING %s %s: %s. Fix: the owner attaches or signs in to %s with the narrowest access" % (
                                 os.path.basename(path), kind, "needs sign-in" if code == 3 else "missing", kind))
    return found


def observed(step):
    """(ok, what this machine shows) for one golden step; steps 1 to 7 can be read from here."""
    repos, gaps = followed(), [x for x in (prerequisites() if step == 1 else connectors() if step == 6 else []) if x[0] == "M"]
    if step in (1, 6):
        return not gaps, "; ".join(gaps) or "no gap"
    if step == 2:
        bad = [p for p in repos if not os.path.exists(os.path.join(p, ".git"))]
        return bool(repos) and not bad, "%d followed repo(s), not a git repo: %s" % (len(repos), ", ".join(bad) or "none")
    if step == 3:
        names = os.environ.get("LOOP_PRIVATE_NAMES") or os.path.join(HOME, "private-names")
        try:
            with open(names, encoding="utf-8") as handle:
                patterns = [x for x in handle if x.strip() and x.strip()[0] != "#"]
        except OSError:
            patterns = []
        have = os.path.exists(os.environ.get("LOOP_FLOW") or os.path.join(HOME, "flow.json"))
        return bool(patterns) and have and symlinks(), "%d private pattern(s), flow file %s, symlinks %s" % (len(patterns), have, symlinks())
    if step == 4:
        version = load(os.path.join(os.path.dirname(os.path.dirname(HERE)), "workflow-package.json"), {}).get("version") or ""
        held = lambda p: load(os.path.join(p, ".loop", "config.json"), {}).get("template_version") or ""
        old = [os.path.basename(p) for p in repos if not held(p) or (version and held(p) != version)]
        return bool(repos) and not old, "installed %s; unknown or older: %s" % (version or "none (a checkout)", ", ".join(old) or "none")
    if step == 5:
        top = os.path.dirname(os.path.dirname(common())) if common() else "."  # the operation repo: the main checkout
        try:
            with open(os.path.join(top, ".claude", "settings.local.json"), encoding="utf-8") as handle:
                text = handle.read()
        except OSError:
            text = ""
        counts = [text.count(name) for name in ("reply_hook.py", "govern_hook.py")]
        return counts == [1, 1], "reply hook %d, govern hook %d" % tuple(counts)
    if step == 7:
        runs = glob.glob(os.path.join(common(), "runs", "*.json"))
        back = [os.path.basename(p)[:-5] for p in runs if load(p, {}).get("worker") == "background" and load(p, {}).get("status") == "running"]
        return not back, "background worker(s) running: %s" % (", ".join(back) or "none")
    return False, "needs the live operation session: run operate.py run --once and compare its five parts"


def replay(golden):
    """SET-11: walk the golden first adoption (dev/toy/adoption-golden.tsv), stop at the first mismatch with what differs and the
    step's fix; a looser result never passes."""
    try:
        with open(golden, encoding="utf-8") as handle:
            steps = [x.rstrip("\n").split("\t") for x in handle if x.strip() and x[0] != "#"]
    except OSError:
        print("NO GOLDEN: %s is missing. Fix: pass --golden FILE" % golden)
        return 1
    for number, check, want, fix in steps:
        ok, seen = observed(int(number))
        if not ok:
            print("STEP %s MISMATCH %s: golden: %s. Observed: %s. Fix: %s" % (number, check, want, seen, fix))
            return 2 if number == "8" else 1
        print("STEP %s OK %s: %s" % (number, check, seen))
    print("REPLAY OK: every step matches the golden")
    return 0


def template_version(dest):
    """A repo's template_version on its newest setup or update branch, else in its working tree."""
    refs = run("for-each-ref", "--sort=-committerdate", "--format=%(refname:short)", "refs/heads/workflow-setup", "refs/heads/workflow-update-*", cwd=dest)[1]
    shown = run("show", "%s:.loop/config.json" % refs.split("\n")[0], cwd=dest)[1] if refs else ""
    return (json.loads(shown) if shown else load(os.path.join(dest, ".loop", "config.json"), {})).get("template_version") or "unknown"


def adopt(args):
    """SET-12: --recent N lists my GitHub repos by last push; names are cloned into one folder, followed, set up or updated, each
    ending with its template_version. No branch is merged."""
    gh = os.environ.get("LOOP_GH", "gh").split()
    if args.recent:
        done = subprocess.run(gh + ["repo", "list", "--limit", str(args.recent), "--json", "nameWithOwner,isPrivate,pushedAt", "--jq",
                                    r'.[] | "\(.nameWithOwner) \(if .isPrivate then "private" else "public" end) \(.pushedAt)"'], capture_output=True, text=True)
        print(done.stdout.strip() or "NO REPOS: " + done.stderr.strip()[:120])
        return done.returncode
    folder, setup = os.path.abspath(os.path.expanduser(args.into)), os.path.join(HERE, "..", "..", "workflow-setup", "scripts")
    os.makedirs(folder, exist_ok=True)
    for name in args.path:
        dest = os.path.join(folder, name.split("/")[-1])
        done = subprocess.run(gh + ["repo", "clone", name, dest], capture_output=True, text=True) if not os.path.isdir(dest) else None
        if done and done.returncode:
            print("FAILED %s: clone: %s" % (name, done.stderr.strip()[:120]))
            continue
        os.makedirs(HOME, exist_ok=True)
        if dest not in followed():
            with open(os.path.join(HOME, "repos"), "a", encoding="utf-8") as handle:
                handle.write(dest + "\n")
        known = os.path.exists(os.path.join(dest, ".loop", "config.json"))
        done = subprocess.run([sys.executable, os.path.join(setup, "update.py" if known else "setup.py"), "--repo", dest] + (["--apply"] if known else []),
                              capture_output=True, text=True)
        print("ADOPTED %s: %s exit %d, template_version %s" % (name, "update" if known else "setup", done.returncode, template_version(dest)))
    return 0


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
    sub.add_parser("prerequisites")
    sub.add_parser("connectors")
    item = sub.add_parser("replay")
    item.add_argument("--golden", default="")
    args = parser.parse_args()
    if args.cmd in ("prerequisites", "connectors"):
        found = prerequisites() if args.cmd == "prerequisites" else connectors() or ["NO CONNECTORS: no followed repo's PRDs name one"]
        print("\n".join(found))
        return 1 if any(x.startswith("MISSING") for x in found) else 0
    if args.cmd == "replay":
        return replay(args.golden or os.path.join(run("rev-parse", "--show-toplevel")[1] or ".", "dev", "toy", "adoption-golden.tsv"))
    if not common():
        sys.exit("REFUSED: not inside a git repository. Nothing was written.")
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
