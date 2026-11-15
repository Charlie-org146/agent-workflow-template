#!/usr/bin/env python3
"""The one command that runs the operation session's loop, the same way every time. No model is in the loop.

usage: operate.py <command> [options]

  run [--once] [--poll S] [--max N] [--skill-dir DIR] [--board]
      Each pass first fast-forwards the main checkout to origin/<base> (refresh below, --ff-only, never a merge commit, uncommitted work
      left alone) and prints one line when it moved or could not. Then: watch.py watch --once (starts every queued goal and batch line whose dependencies are merged, up to
      parallel; mends and resumes if the config allows), board.py board, board_page.py. It prints the check-in every pass, even when nothing changed
      (--board adds the live board and its changes). Then it waits the gap from `board.py cadence`,
      or less: a worker that reports (a run record changes) or a goal added to the queue starts the next pass at once.
      It stops when nothing is queued, running or waiting, or when the cadence is off. --once makes one pass.
      Each pass also runs replan.py (MON-10) and auto.py pass (MON-11), and prints the check-in (checkin.py), not the
      live board: the board prints only for report, dashboard and "where do things stand" (MON-4; --board adds it).
  send SLUG TEXT [--source owner|auto]
      send a worker an answer or a follow-up (worker.py send); the worker's agent sees it the next time it runs goal.py.
      An answer to a waiting question is kept in <git common dir>/loop/answers.jsonl with its source (auto.py reads it)
  claim [--id ID]
      add this session ($CLAUDE_SESSION_ID or --id) to loop/operation.id, for the govern hook (MON-7), in this repo and
      every repo it follows (MON-13); sessions already there stay, so several independent operation sessions may run at
      once and nothing refuses or warns; refused in a worker

An LLM asked to run the operation session runs `operate.py run` and nothing else. It never merges.
"""
import argparse
import glob
import json
import os
import subprocess
import sys
import tempfile
import time

# No terminal, no waiting: a prompt from git or gh must fail, not block.
os.environ.update(GIT_TERMINAL_PROMPT="0", GH_PROMPT_DISABLED="1", GIT_EDITOR="true", GIT_ASKPASS="true", SSH_ASKPASS="true")
if not sys.stdin or not sys.stdin.isatty():
    os.dup2(os.open(os.devnull, os.O_RDONLY), 0)

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import graph  # noqa: E402
DONE = "NOTHING LEFT TO OPERATE: no goal is queued, running or waiting. Nothing was merged."


def git(*args):
    done = subprocess.run(["git"] + list(args), capture_output=True, text=True)
    return done.stdout.strip() if done.returncode == 0 else ""


def script(name, *args, cwd=None):
    done = subprocess.run([sys.executable, os.path.join(HERE, name)] + list(args), capture_output=True, text=True, cwd=cwd)
    return done.returncode, done.stdout + done.stderr


def signature(top, common):
    """What a worker's report or a new queue line changes: the run records, the inbox and the queue file."""
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
    """merge --ff-only; a dirty lane record RUNS is stashed under a tag first and applied back by its sha (never a bare pop),
    left in the stash with a note when it no longer applies."""
    tag, sha = "operate-forward-%d" % os.getpid(), ""
    if RUNS in fgit(root, "status", "--porcelain", "--untracked-files=no")[1].replace("\\", "/") and fgit(root, "stash", "push", "-m", tag, "--", RUNS)[0] == 0:
        sha = next((l.split()[0] for l in fgit(root, "stash", "list", "--format=%H %gs")[1].splitlines() if l.endswith(tag)), "")
    code, said = fgit(root, "merge", "--ff-only", "-q", "origin/" + base)
    if sha:
        if fgit(root, "stash", "apply", sha)[0]:
            fgit(root, "checkout", "-q", "--", RUNS)
            said += " (the lane record %s stays in stash entry %s)" % (RUNS, sha[:12])
        else:
            drop = next((l.split()[0] for l in fgit(root, "stash", "list", "--format=%gd %gs")[1].splitlines() if l.endswith(tag)), "")
            drop and fgit(root, "stash", "drop", "-q", drop)
    return code, said


def refresh(common, base="main"):
    """One line when the main checkout moved or could not, else ''. `common` is the repo's git common dir."""
    common = os.path.abspath(common)
    root = os.path.dirname(common) if os.path.basename(common) == ".git" else ""
    if not root or not os.path.isdir(root):
        return ""  # a bare repo has no checkout to move
    head = fgit(root, "rev-parse", "--abbrev-ref", "HEAD")[1]
    if head != base:
        return "CHECKOUT NOT FAST-FORWARDED: %s is on %s, not %s; its skills run as they are" % (os.path.basename(root), head or "no branch", base)
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


def behind_ask(common, base="main"):
    """The main checkout is current with origin/<base> every pass. When it is behind (the operation session's govern hook blocks
    its own pull), the line asks a free worker to fast-forward it, kept in <loop>/checkout-behind.txt for the check-in; '' when current."""
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
    moved = refresh(common)  # the main checkout, where the skills and hooks run, follows origin (MON-4)
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
    if args.board:  # asked for "where do things stand": the live board and its changes, then the check-in
        print(graph.localize(out.rstrip()))
    said = script("board_page.py", "migrate", cwd=top)[1].strip()  # one migrate-<repo> goal per followed repo behind the template
    said and print(graph.localize(said))
    script("board_page.py", cwd=top)  # board.html and the dashboard keep the live board; the check-in doesn't print it
    for name, *more in (("replan.py", "plan"), ("auto.py", "pass")):
        code, said = script(name, *more, cwd=top)
        if code:
            print(graph.localize(said.strip()))
    print(graph.localize(script("checkin.py", cwd=top)[1].rstrip()))
    script("board_page.py", "checkin", cwd=top)
    try:
        with open(board) as handle:
            busy = bool(json.load(handle).get("open"))
    except (OSError, ValueError):
        busy = False
    return delay, busy


def cmd_run(args):
    top = git("rev-parse", "--show-toplevel")
    common = os.path.abspath(git("rev-parse", "--git-common-dir"))
    if os.environ.get("CLAUDE_SESSION_ID"):
        cmd_claim(argparse.Namespace(id=""))
    pod = graph.pod_id()
    if pod:
        os.environ.setdefault("LOOP_POD_ID", pod)  # watch, auto, send and merge inherit it
    while True:
        seen = signature(top, common)  # before the pass, so a report that lands during it still starts the next one
        delay, busy = one_pass(top, common, args)
        if not busy:
            print(DONE)
            return 0
        if args.once:
            return 0
        if delay == "none":
            print("CADENCE OFF: the owner turned the loop off. Stop.")
            return 0
        stop = time.time() + int(delay)
        while time.time() < stop and signature(top, common) == seen:
            time.sleep(args.poll)


def remember(slug, text, source):
    """Keep an answer to a waiting question (slug, its question key, the words, who answered) for auto.py."""
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
    """Add sid to <base>/loop/operation.id, keeping the sessions already there; a repo that can't be written is skipped."""
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
    """Two layers per pod (MON-13): this session joins the operation sessions of this repo and every repo it follows; the
    others stay, and nothing refuses, because independent operation sessions may run at once."""
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
    """The inbox always carries it; a goal in a worker session is also sent it by session message, which wakes it."""
    graph.refuse(graph.load_run(args.slug))  # another pod's goal is not ours to answer
    remember(args.slug, args.text, args.source)
    code, said = script("worker.py", "send", args.slug, args.text)
    print(graph.localize(said.strip()))
    if not code and os.path.exists(os.path.join(HERE, "sessions.py")):
        print(graph.localize(script("sessions.py", "send", args.slug, args.text)[1].strip()))
    return code


def run(args, cwd=None):
    return subprocess.run(args, cwd=cwd, capture_output=True, text=True)


def wiki_only(top, old, new):
    """True when NEW descends from OLD (the head the pr lane passed) and every commit between only adds or edits .md pages
    in the base branch's wiki folder (wiki_dir from origin/<base>'s config: the branch can't widen it), no SKILL.md."""
    if run(["git", "merge-base", "--is-ancestor", old, new], cwd=top).returncode:
        return False
    head = run(["git", "symbolic-ref", "--short", "refs/remotes/origin/HEAD"], cwd=top).stdout.strip()
    shown = run(["git", "show", "%s:.loop/config.json" % (head or "origin/main")], cwd=top)
    try:
        folder = (json.loads(shown.stdout).get("wiki_dir") if shown.returncode == 0 else None) or "docs/wiki"
    except (ValueError, AttributeError):
        folder = "docs/wiki"
    done = run(["git", "diff", "--raw", "--no-renames", old, new], cwd=top)  # a move shows its source
    rows = [(line.split("\t")[0].split(), line.split("\t")[1:]) for line in done.stdout.split("\n") if line]
    return not done.returncode and bool(rows) and all(
        len(m) == 5 and len(p) == 1 and m[4] in ("A", "M") and m[1] != "120000"  # no symlink
        and p[0].startswith(str(folder).rstrip("/") + "/") and p[0].endswith(".md") and os.path.basename(p[0]) != "SKILL.md"
        for m, p in rows)


def apply(slug, branch):
    """Re-stamp the pages docs.py check --own calls stale on the goal's branch, in a temporary worktree: restamp marks a page
    only while its reviewed text still holds, so a wording change stays refused. The pushed commit moves the head by wiki
    pages only, which merge.py accepts."""
    top = run(["git", "rev-parse", "--show-toplevel"]).stdout.strip()
    tree = tempfile.mkdtemp(prefix="restamp-")
    if run(["git", "fetch", "-q", "origin", branch], top).returncode or run(["git", "worktree", "add", "-q", "--detach", tree, "origin/" + branch], top).returncode:
        return 0
    try:
        with open(os.path.join(tree, ".loop", "config.json")) as handle:
            config = json.load(handle)
        base, folder = config.get("base") or "main", config.get("wiki_dir") or "docs/wiki"
        docs = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "workflow-docs", "scripts")
        pages = sorted({l.split()[1].rstrip(":") for l in run([sys.executable, os.path.join(docs, "docs.py"), "check", "--own", "origin/" + base], tree).stdout.splitlines() if l.startswith("STALE ")})
        said = pages and run([sys.executable, os.path.join(docs, "docfresh.py"), "restamp", slug] + pages, tree).stdout.strip()
        if said and run(["git", "add", "-A", "--", folder], tree).returncode == 0:
            run(["git", "commit", "-q", "-m", "Wiki: re-stamp pages for %s" % slug], tree)
            pushed = run(["git", "push", "-q", "origin", "HEAD:refs/heads/" + branch], tree)
            print(said if not pushed.returncode else "NOTE: the re-stamp of %s could not be pushed: %s" % (", ".join(pages), pushed.stderr.strip()[-120:]))
    except (OSError, ValueError):
        pass
    finally:
        run(["git", "worktree", "remove", "--force", tree], top)
    return 0


def cmd_forward(args):
    """merge.py / wiki.py: move this main checkout to origin/BASE (exit 0 when it moved)."""
    line = refresh(fgit(os.getcwd(), "rev-parse", "--path-format=absolute", "--git-common-dir")[1], args.base)
    print(line)
    return 0 if "FAST-FORWARDED" in line else 1


def cmd_wiki_only(args):
    """merge.py: exit 0 when NEW follows OLD by wiki page commits only."""
    return 0 if wiki_only(os.getcwd(), args.old, args.new) else 1


def cmd_apply(args):
    """merge.py: re-stamp the pages stale on origin/BRANCH (#3867) and push the commit."""
    return apply(args.slug, args.branch)


def main():
    sys.stdout.reconfigure(line_buffering=True)  # a loop that waits must show each pass at once, even into a file
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = parser.add_subparsers(dest="command", required=True)
    item = sub.add_parser("run")
    item.add_argument("--once", action="store_true")
    item.add_argument("--poll", type=float, default=2)
    item.add_argument("--max", type=int, default=0)
    item.add_argument("--skill-dir", default="")
    item.add_argument("--board", action="store_true", help="also print the live board each pass (where do things stand)")
    item = sub.add_parser("send")
    item.add_argument("slug")
    item.add_argument("text")
    item.add_argument("--source", default="owner", choices=["owner", "auto"])
    item = sub.add_parser("claim")
    item.add_argument("--id", default="")
    sub.add_parser("forward").add_argument("base")
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
