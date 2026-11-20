#!/usr/bin/env python3
"""The one command that runs the operation session's loop, the same way every time, with no model in it.

usage: operate.py <command> [options]

  run [--once] [--poll S] [--max N] [--skill-dir DIR] [--board]
      Each pass fast-forwards the main checkout to origin/<base> (--ff-only; a dirty root is not advanced: "root is dirty: FILES;
      not advanced"; one line when it moved or could not), then runs watch.py watch --once (starts every goal whose dependencies are merged, up to parallel;
      mends and resumes if config allows), board.py board, board_page.py, replan.py (MON-10), auto.py pass (MON-11) and
      pool.py archive (MON-6: ARCHIVE-NOW lines are for its archive tool), prints the check-in (checkin.py) and
      mails its new events (notify.py). The live board prints only for report, dashboard and "where do things stand"
      (MON-4; --board adds it). It waits the gap from `board.py cadence`, less when a worker reports or a goal is queued,
      and stops when nothing is queued, running or waiting, or the cadence is off.
  run --role top|machine   top: one board from every STATUS; machine: STATUS to top, one line
  start     a new operation session's readiness table (session tool, workers, skills, hooks, memory, pool), each row ok or
            its fix; it starts nothing (notify.py ready)
  timer [created]   show the check-in timer for the owner's yes; `created` records it (notify.py timer)
  send SLUG TEXT [--source owner|auto]
      send a worker an answer or follow-up (worker.py send); it sees it the next time it runs goal.py. An answer to a
      waiting question is kept in <git common dir>/loop/answers.jsonl with its source (auto.py reads it)
  claim [--id ID]
      add this session ($CLAUDE_SESSION_ID or --id) to loop/operation.id for the govern hook (MON-7), in this repo and every
      repo it follows (MON-13); several may run at once; refused in a worker

An LLM asked to run the operation session runs `operate.py run` and nothing else. It never merges.
"""
import argparse
import glob
import importlib.util
import json
import os
import re
import subprocess
import sys
import tempfile
import time

os.environ.update(GIT_TERMINAL_PROMPT="0", GH_PROMPT_DISABLED="1", GIT_EDITOR="true", GIT_ASKPASS="true", SSH_ASKPASS="true")
if not sys.stdin or not sys.stdin.isatty():
    os.dup2(os.open(os.devnull, os.O_RDONLY), 0)

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import graph  # noqa: E402
import layers  # noqa: E402
CFG = lambda top: layers.read(os.path.join(top, ".loop", "config.json"))
DONE = "NOTHING LEFT TO OPERATE: no goal is queued, running or waiting. Nothing was merged."


def git(*args):
    done = subprocess.run(["git"] + list(args), capture_output=True, text=True)
    return done.stdout.strip() if done.returncode == 0 else ""


def script(name, *args, cwd=None):
    done = subprocess.run([sys.executable, os.path.join(HERE, name)] + list(args), capture_output=True, text=True, cwd=cwd)
    return done.returncode, done.stdout + done.stderr


def signature(top, common):
    files = glob.glob(os.path.join(common, "loop", "runs", "*.json")) + [os.path.join(top, ".loop", "queue.md")]
    found = {}
    for path in files:
        try:
            found[path] = os.stat(path).st_mtime_ns
        except OSError:
            pass
    return found


ENV = dict(os.environ, GIT_TERMINAL_PROMPT="0", GH_PROMPT_DISABLED="1", GIT_EDITOR="true")


def fgit(root, *args, timeout=60):
    try:
        done = subprocess.run(["git", "-C", root] + list(args), capture_output=True, text=True, timeout=timeout, env=ENV)
    except (OSError, subprocess.TimeoutExpired) as error:
        return 1, str(error)
    return done.returncode, (done.stdout if done.returncode == 0 else done.stderr or done.stdout).strip()


RUNS = ".loop/regression-runs.tsv"


def fast_forward(root, base):
    """merge --ff-only; a dirty RUNS is stashed under a tag and applied back by sha, never a bare pop."""
    tag, sha = "operate-forward-%d" % os.getpid(), ""
    if RUNS in fgit(root, "status", "--porcelain", "--untracked-files=no")[1].replace("\\", "/") and fgit(root, "stash", "push", "-m", tag, "--", RUNS)[0] == 0:
        sha = next((l.split()[0] for l in fgit(root, "stash", "list", "--format=%H %gs")[1].splitlines() if l.endswith(tag)), "")
    code, said = fgit(root, "merge", "--ff-only", "-q", "origin/" + base)
    if sha:
        if fgit(root, "stash", "apply", sha)[0]:
            fgit(root, "checkout", "-q", "HEAD", "--", RUNS)
            said += " (the lane record %s stays in stash entry %s, %s)" % (RUNS, tag, sha[:12])
        else:
            drop = next((l.split()[0] for l in fgit(root, "stash", "list", "--format=%gd %gs")[1].splitlines() if l.endswith(tag)), "")
            drop and fgit(root, "stash", "drop", "-q", drop)
    return code, said


def refresh(common, base="main"):
    common = os.path.abspath(common)
    root = os.path.dirname(common) if os.path.basename(common) == ".git" else ""
    if not root or not os.path.isdir(root):
        return ""
    head = fgit(root, "rev-parse", "--abbrev-ref", "HEAD")[1]
    if head != base:
        return "CHECKOUT NOT FAST-FORWARDED: %s is on %s, not %s; its skills run as they are" % (os.path.basename(root), head or "no branch", base)
    dirty = [l.split(None, 1)[1] for l in fgit(root, "status", "--porcelain", "--untracked-files=no")[1].splitlines() if l.strip() and l.split(None, 1)[1] != RUNS]
    if dirty:
        return "root is dirty: %s; not advanced" % ", ".join(dirty)
    code, said = fgit(root, "fetch", "-q", "origin", base)
    if code:
        return "CHECKOUT NOT FAST-FORWARDED: cannot fetch origin/%s (%s)" % (base, said.splitlines()[0][:80] if said else "no reply")
    behind = fgit(root, "rev-list", "--count", "HEAD..origin/" + base)[1]
    ahead = fgit(root, "rev-list", "--count", "origin/%s..HEAD" % base)[1]
    if behind in ("", "0"):
        return ""
    if ahead not in ("", "0"):
        return "CHECKOUT NOT FAST-FORWARDED: %s has %s commits origin/%s lacks and is %s behind; merge or push by hand" % (base, ahead, base, behind)
    code, said = fast_forward(root, base)
    if code:
        return "CHECKOUT NOT FAST-FORWARDED: %s commits behind origin/%s; git refused (%s)" % (behind, base, said.splitlines()[0][:80] if said else "no reason")
    return "CHECKOUT FAST-FORWARDED %s by %s commits to %s" % (base, behind, fgit(root, "rev-parse", "--short", "HEAD")[1])


def scratch(goal):
    """~/.workflow-loop/scratch/<goal>: unlike /tmp, it survives a restart."""
    path = os.path.join(os.path.expanduser("~"), ".workflow-loop", "scratch", re.sub(r"[^\w.-]", "-", goal))
    os.makedirs(path, exist_ok=True)
    return path


def untrusted(folder):
    """The refusal for FOLDER when ~/.claude.json lists projects and none at or above it is trusted (read only), else ""."""
    try:
        with open(os.path.join(os.path.expanduser("~"), ".claude.json")) as handle:
            known = json.load(handle)["projects"]
        path = os.path.realpath(folder) + "/"
        return "" if any(v.get("hasTrustDialogAccepted") and path.startswith(os.path.realpath(k).rstrip("/") + "/") for k, v in known.items()) else "REFUSED: ask the owner to trust %s (FOLDER_TRUST)." % folder
    except (OSError, ValueError, KeyError, TypeError, AttributeError):
        return ""


def behind_ask(common, base="main"):
    """When the main checkout is behind origin/<base>, a line asks a free worker to move it; '' when current."""
    common = os.path.abspath(common)
    root, mark = os.path.dirname(common), os.path.join(common, "loop", "checkout-behind.txt")
    behind = fgit(root, "rev-list", "--count", "HEAD..origin/" + base)[1] if os.path.basename(common) == ".git" else "0"
    if behind in ("", "0") or not behind.isdigit():
        if os.path.exists(mark):
            os.remove(mark)
        return ""
    free = [item.get("name") or sid for sid, item in sorted((graph.read_pool(os.path.join(common, "loop", "session-pool.json"))[0] or {}).items())
            if isinstance(item, dict) and item.get("state") == "free"]
    line = "the main checkout is %s commits behind origin/%s: ask %s to run git -C %s merge --ff-only origin/%s" % (
        behind, base, free[0] if free else "a free worker (none is free; pool.py add)", root.replace(os.sep, "/"), base)
    os.makedirs(os.path.dirname(mark), exist_ok=True)
    with open(mark, "w") as handle:
        handle.write(line + chr(10))
    return "CHECKOUT BEHIND: " + line


def one_pass(top, common, args):
    who = layers.role(args.role)
    if who == "top":
        print(graph.localize(layers.publish_board(common, CFG(top))))
        script("board_page.py", cwd=top)
        return str(layers.TOP_GAP), True
    moved = refresh(common)
    moved and print(moved)
    ask = behind_ask(common)
    ask and print(ask)
    flags = (["--max", str(args.max)] if args.max else []) + (["--skill-dir", args.skill_dir] if args.skill_dir else [])
    code, said = script("watch.py", "watch", "--once", *flags, cwd=top)
    if code:
        print(graph.localize(said.strip()))
    folder = os.path.join(common, "loop")
    board, before = os.path.join(folder, "board.json"), os.path.join(folder, "board.before.json")
    since = []
    if os.path.exists(board):
        os.replace(board, before)
        since = ["--since", before]
    _, out = script("board.py", "board", *since, cwd=top)
    delay = next((line.split()[1] for line in out.splitlines() if line.startswith("NEXT_DELAY ")), "none")
    if args.board:
        print(graph.localize(out.rstrip()))
    said = "" if who else script("board_page.py", "migrate", cwd=top)[1].strip()
    said and print(graph.localize(said))
    who or script("board_page.py", cwd=top)
    for name, *more in (("replan.py", "plan"), ("auto.py", "pass"), ("pool.py", "archive")):
        code, said = script(name, *more, cwd=top)
        if code or "ARCHIVE-NOW" in said:
            print(graph.localize(said.strip()))
    text = graph.localize(script("checkin.py", cwd=top)[1].rstrip())
    print(layers.one_line(*layers.send(common, CFG(top))) if who == "machine" else text)
    try:
        with open(os.path.join(folder, "checkin.txt"), "w", encoding="utf-8") as handle:
            handle.write(text + chr(10))
    except OSError:
        pass
    said = script("notify.py", "send", cwd=top)[1].strip()
    said and print(said)
    who or script("board_page.py", "checkin", cwd=top)
    try:
        with open(board) as handle:
            busy = bool(json.load(handle).get("open"))
    except (OSError, ValueError):
        busy = False
    return delay, busy


def cmd_start(args):
    print(script("notify.py", "ready", cwd=git("rev-parse", "--show-toplevel"))[1].rstrip())
    return 0


def cmd_timer(args):
    print(script("notify.py", "timer", *([args.created] if args.created else []), cwd=git("rev-parse", "--show-toplevel"))[1].rstrip())
    return 0


def cmd_run(args):
    top = git("rev-parse", "--show-toplevel")
    common = os.path.abspath(git("rev-parse", "--git-common-dir"))
    if os.environ.get("CLAUDE_SESSION_ID"):
        cmd_claim(argparse.Namespace(id=""))
    pod = graph.pod_id()
    if pod:
        os.environ.setdefault("LOOP_POD_ID", pod)
    while True:
        seen = signature(top, common)
        delay, busy = one_pass(top, common, args)
        if not busy:
            print(DONE)
            return 0
        if args.once:
            return 0
        if delay == "none":
            print("CADENCE OFF: the owner turned the loop off. Stop.")
            return 0
        stop, beat = time.time() + int(delay), 0
        while time.time() < stop and signature(top, common) == seen:
            if layers.role(args.role) == "machine" and time.time() - beat >= 30:  # the status file stays under a minute old (TD430)
                beat = time.time()
                layers.beat(common, layers.build(common, CFG(top)))
            time.sleep(args.poll)


def remember(slug, text, source):
    """Keep an answer to a waiting question for auto.py."""
    common = os.path.abspath(git("rev-parse", "--git-common-dir") or ".git")
    try:
        with open(os.path.join(common, "loop", "runs", slug + ".json")) as handle:
            run = json.load(handle)
    except (OSError, ValueError):
        return
    ask = (run.get("waiting") or {}).get("ask") if run.get("status") == "waiting" else ""
    if ask:
        with open(os.path.join(common, "loop", "answers.jsonl"), "a") as handle:
            handle.write(json.dumps({"slug": slug, "key": " ".join(ask.lower().split()), "words": text, "source": source}) + "\n")


def add_id(base, sid):
    """Add sid to <base>/loop/operation.id, keeping the others; an unwritable repo is skipped."""
    path = os.path.join(base, "loop", "operation.id")
    try:
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path) as handle:
            have = {line.strip() for line in handle}
    except OSError:
        have = set()
    if sid not in have:
        try:
            with open(path, "a") as handle:
                handle.write(sid + "\n")
        except OSError:
            pass


def cmd_claim(args):
    """MON-13: this session joins the operation sessions of this repo and every repo it follows."""
    sid = args.id or os.environ.get("CLAUDE_SESSION_ID", "")
    common = os.path.abspath(git("rev-parse", "--git-common-dir") or ".git")
    if os.environ.get("LOOP_ROLE") == "worker" or os.path.realpath(os.getcwd()).startswith(os.path.join(common, "loop", "worktrees") + os.sep):
        sys.exit("REFUSED: a worker can't claim the operation session. Fix: run claim from the main checkout's operation session.")
    if not sid:
        sys.exit("REFUSED: no session id. Fix: operate.py claim --id <this session's id>.")
    import board as bd
    for base in [common] + [base for _, _, base in bd.followed() if base != common]:
        add_id(base, sid)
    print("CLAIMED operation session %s" % sid)
    print("POD %s: set LOOP_POD_ID=%s to keep this pod if the session restarts" % (sid, sid))
    return 0


def cmd_send(args):
    """The inbox carries it; a worker session is also sent it."""
    graph.refuse(graph.load_run(args.slug))
    remember(args.slug, args.text, args.source)
    code, said = script("worker.py", "send", args.slug, args.text)
    print(graph.localize(said.strip()))
    if not code and os.path.exists(os.path.join(HERE, "sessions.py")):
        print(graph.localize(script("sessions.py", "send", args.slug, args.text)[1].strip()))
    return code


def run(args, cwd=None):
    return subprocess.run(args, cwd=cwd, capture_output=True, text=True)


def tems(*args, **kwargs):
    here = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "workflow-release", "scripts")
    sys.path.append(here)
    spec = importlib.util.spec_from_file_location("autorelease", os.path.join(here, "autorelease.py"))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.tems(*args, **kwargs)


def wiki_only(top, old, new):
    """True when NEW descends from OLD by stamps, wiki pages (not SKILL.md), kept fragments and README.md outside its blocks."""
    if run(["git", "merge-base", "--is-ancestor", old, new], cwd=top).returncode:
        return False
    head = run(["git", "symbolic-ref", "--short", "refs/remotes/origin/HEAD"], cwd=top).stdout.strip()
    shown = run(["git", "show", "%s:.loop/config.json" % (head or "origin/main")], cwd=top)
    try:
        folder = (json.loads(shown.stdout).get("wiki_dir") if shown.returncode == 0 else None) or "docs/wiki"
    except (ValueError, AttributeError):
        folder = "docs/wiki"
    page = lambda p: (p.startswith(str(folder).rstrip("/") + "/") and p.endswith(".md") and os.path.basename(p) != "SKILL.md"
                      ) or re.fullmatch(r"[.]loop/kept/[^/]+[.]tsv", p) or (p == "README.md" and readme_blocks_only(top, old, new))
    return tems(top, old, new, allow=page)


def readme_blocks_only(top, old, new):
    bare = lambda ref: re.sub(r"<!-- (settings|automation|template):begin -->\n.*?<!-- \1:end -->\n", "", run(["git", "show", ref + ":README.md"], cwd=top).stdout, flags=re.S)
    return bare(old) == bare(new)


def apply(slug, branch):
    """Re-stamp the pages docs.py check --own calls stale on the goal's branch, in a temporary worktree, while a page's
    reviewed text holds. The pushed commit moves the head by wiki pages only, which merge.py accepts."""
    top = run(["git", "rev-parse", "--show-toplevel"]).stdout.strip()
    tree = tempfile.mkdtemp(prefix="restamp-")
    if run(["git", "fetch", "-q", "origin", branch], top).returncode or run(["git", "worktree", "add", "-q", "--detach", tree, "origin/" + branch], top).returncode:
        return 0
    try:
        with open(os.path.join(tree, ".loop", "config.json")) as handle:
            config = json.load(handle)
        base, folder = config.get("base") or "main", config.get("wiki_dir") or "docs/wiki"
        docs = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "workflow-docs", "scripts")
        stale = lambda: sorted({l.split()[1].rstrip(":") for l in run([sys.executable, os.path.join(docs, "docs.py"), "check", "--own", "origin/" + base], tree).stdout.splitlines() if l.startswith("STALE ")})
        pages = stale()
        again = run([sys.executable, os.path.join(docs, "audit.py"), "rerender", base], tree).stdout.strip()
        pages = stale() if again else pages
        said = "\n".join(x for x in (again, pages and run([sys.executable, os.path.join(docs, "audit.py"), "restamp", slug] + pages, tree).stdout.strip()) if x)
        if said and run(["git", "add", "-A", "--", folder, "README.md"], tree).returncode == 0:
            run(["git", "commit", "-q", "-m", "Wiki: re-render and re-stamp pages for %s" % slug], tree)
            pushed = run(["git", "push", "-q", "origin", "HEAD:refs/heads/" + branch], tree)
            print(said if not pushed.returncode else "NOTE: the re-stamp of %s could not be pushed: %s" % (", ".join(pages), pushed.stderr.strip()[-120:]))
    except (OSError, ValueError):
        pass
    finally:
        run(["git", "worktree", "remove", "--force", tree], top)
    return 0


def cmd_forward(args):
    """merge.py / wiki.py: move this checkout to origin/BASE."""
    line = refresh(fgit(os.getcwd(), "rev-parse", "--path-format=absolute", "--git-common-dir")[1], args.base)
    print(line)
    return 0 if "FAST-FORWARDED" in line else 1


def cmd_scratch(args):
    print(scratch(args.goal))
    return 0


def cmd_wiki_only(args):
    """merge.py: exit 0 when NEW follows OLD by wiki page commits only."""
    return 0 if wiki_only(os.getcwd(), args.old, args.new) else 1


def cmd_apply(args):
    """merge.py: re-stamp the pages stale on origin/BRANCH and push the commit."""
    return apply(args.slug, args.branch)


def main():
    sys.stdout.reconfigure(line_buffering=True)
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = parser.add_subparsers(dest="command", required=True)
    item = sub.add_parser("run")
    item.add_argument("--once", action="store_true")
    item.add_argument("--poll", type=float, default=2)
    item.add_argument("--max", type=int, default=0)
    item.add_argument("--skill-dir", default="")
    item.add_argument("--board", action="store_true", help="also print the live board each pass (where do things stand)")
    item.add_argument("--role", default="", choices=list(layers.ROLES), help="top or machine")
    sub.add_parser("start")
    sub.add_parser("timer").add_argument("created", nargs="?", default="", choices=["", "created"])
    item = sub.add_parser("send")
    item.add_argument("slug")
    item.add_argument("text")
    item.add_argument("--source", default="owner", choices=["owner", "auto"])
    item = sub.add_parser("claim")
    item.add_argument("--id", default="")
    sub.add_parser("forward").add_argument("base")
    sub.add_parser("scratch").add_argument("goal")
    item = sub.add_parser("wiki-only")
    item.add_argument("old")
    item.add_argument("new")
    item = sub.add_parser("apply")
    item.add_argument("slug")
    item.add_argument("branch")
    args = parser.parse_args()
    return globals()["cmd_" + args.command.replace("-", "_")](args)


if __name__ == "__main__":
    sys.exit(main())
