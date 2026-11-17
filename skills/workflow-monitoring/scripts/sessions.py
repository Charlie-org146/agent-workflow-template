#!/usr/bin/env python3
"""Worker sessions: each goal runs in its own app session, named "worker · <goal>", and reports by session message.

usage: sessions.py <command> [options]

  assign SLUG               give a frozen goal to a worker session (watch.py does this for every goal it starts)
  bind SLUG ID|self [--name N] [--force] [--cwd DIR]
                            record a session started with the app's own tools; before freezing it records the handoff
                            (ASSIGNED), after goal.py new it binds (BOUND). --force: rebind a session freed from the goal.
                            Prints the WORKER command and the WORKTREE (worker.py)
  free SLUG                 give back a stopped session's goal and slot (FREED, NOTHING TO FREE)
  report SLUG [--step S] [--status running|waiting|merged|failed] [--pr URL] [--ask Q --words W... --recommend W
              --kind K] [--attempt N] [--text T]
                            a worker's step or result. waiting with --ask is a question (auto.py may answer a routine
                            one); without it the pull request waits. merged is checked with gh. An ended goal's session
                            goes back to the pool. Done is final (KEPT), but merged still frees the session.
  send SLUG TEXT            send a worker session the owner's answer or a follow-up (operate.py send does this)
  owner-words TEXT --ids A,B  record the owner's exact message for the IDs it covers (auto.py); not in a worker
  list                      the sessions this repo knows, with their goals

A session tool does the talking: the command in `session_command` (.loop/config.json) or $LOOP_SESSION_TOOL, called as
`TOOL start NAME` (prints the new session's id), `TOOL rename ID NAME` and `TOOL send ID TEXT`. With no tool, or one
that fails or passes its timeout (LOOP_SESSION_TIMEOUT, 30 s), the goal falls back to a background process ("background").
The pool lives in <git common dir>/loop/session-pool.json, read by graph.read_pool, changed under a lock, never
written when unreadable. Nothing here merges.
"""
import argparse
import contextlib
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.modules.setdefault("sessions", sys.modules[__name__])  # as a script, pool.py finds this module
import graph  # noqa: E402
import proctree  # noqa: E402
import worker  # noqa: E402
from worker import HUNG, LAST_ERROR, call, fcntl, git, merged, now, tool  # noqa: E402  (watch.py clears sessions.HUNG)

os.environ.update(GIT_TERMINAL_PROMPT="0", GH_PROMPT_DISABLED="1", GIT_EDITOR="true", GIT_ASKPASS="true", SSH_ASKPASS="true")
if not sys.stdin or not sys.stdin.isatty():
    os.dup2(os.open(os.devnull, os.O_RDONLY), 0)

SLUG = re.compile(r"^[a-z0-9][a-z0-9-]{0,50}$")
SEND = ("You are the worker session for goal {slug}; this replaces any goal you had before. Work only in its worktree: "
        "cd {tree} first, and run every goal.py and flow.py command there with LOOP_ROLE=worker set. Run every flow step "
        "inside this session: flow.py prints IN SESSION and the skill to invoke; run it yourself with the recommended "
        "answer at every question, never push from ship, and record each step with goal.py record. Send the operation "
        "session{to} a session message at each change of step or status, and your result when the goal ends (merged, "
        "failed or waiting, with the pull request).\n\n")
FREE_TRIES = 2  # free sessions tried before a new one


def base():
    return os.path.join(os.path.abspath(git("rev-parse", "--git-common-dir") or ".git"), "loop")


def read(path, empty):
    try:
        with open(path) as handle:
            found = json.load(handle)
        return found if isinstance(found, type(empty)) else empty
    except (OSError, ValueError):
        return empty


def write(path, data):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    temp = path + ".%d.tmp" % os.getpid()
    with open(temp, "w") as handle:
        json.dump(data, handle, indent=2)
    os.replace(temp, path)


class PoolUnreadable(Exception):
    """The pool can't be trusted: nothing may change it."""


def pool_path():
    return os.path.join(base(), "session-pool.json")


def pool():
    found, why = graph.read_pool(pool_path())
    if found is None:
        raise PoolUnreadable(why)
    pool_module().quarantine()  # issue 122
    return found


@contextlib.contextmanager
def locked():
    """One read, change and write of the pool at a time."""
    os.makedirs(base(), exist_ok=True)
    with open(pool_path() + ".lock", "a") as handle:
        fcntl.flock(handle, fcntl.LOCK_EX)
        try:
            yield
        finally:
            fcntl.flock(handle, fcntl.LOCK_UN)


def save_pool(found):
    write(pool_path(), found)


def load(slug):
    return read(os.path.join(base(), "runs", slug + ".json"), {}) if SLUG.match(slug or "") else {}


def save(state, note):
    state["updated"] = now()
    state.setdefault("log", []).append("%s %s" % (state["updated"], note))
    write(os.path.join(base(), "runs", state["slug"] + ".json"), state)
    print("%s %s: %s" % (state["updated"], state["slug"], note))


def pool_module():
    import pool as found  # pool.py imports this module back
    return found


def name_of(slug):
    return "worker · " + slug


def release(slug, found=None, mark=False):
    """Free the goal's busy sessions; return how many (the caller saves a pool it passes in). mark blocks a rebind (--force)."""
    if found is None:
        with locked():
            found = pool()
            count = release(slug, found, mark)
            save_pool(found)
        return count
    count = 0
    for item in found.values():
        if item.get("slug") == slug and item.get("state") == "busy":
            item["state"], count = "free", count + 1
            if mark:
                item.update(freed_from=slug, freed_at=now())
    return count


def assign(state, prompt, cfg):
    """Give the goal to a free session, or a new one; rename it, send it the goal. False: start a background process.
    An unreadable pool raises PoolUnreadable."""
    command, slug = tool(cfg), state["slug"]
    state["worker"], state["worker_why"] = "background", "no session tool is set (session_command)"
    if not command:
        return False
    found, to = pool(), os.environ.get("LOOP_OPERATION_SESSION", "")
    start = load(slug) or state
    before = (start.get("session") or {}).get("id") if start.get("status") in ("failed", "stopped", "queued", "", None) else None
    text = SEND.format(slug=slug, tree=state.get("worktree") or "its worktree", to=" (%s)" % to if to else "") + worker.worker_line(slug) + "\n\n" + prompt
    free = sorted(s for s, item in found.items() if item.get("state") == "free")[:FREE_TRIES]
    sid, reused = None, False
    for sid in free + [None]:
        reused = sid is not None
        sid = sid or call(command, "start", name_of(slug))
        if not sid:
            state["worker_why"] = "the session tool timed out" if HUNG else "the session tool could not start a session"
            break
        with locked():  # claim it before sending
            found = pool()
            if reused and (found.get(sid) or {}).get("state") != "free":
                continue
            found[sid] = {"name": name_of(slug), "slug": slug, "state": "busy", "since": now()}
            save_pool(found)
        if call(command, "rename", sid, name_of(slug)) is not None and call(command, "send", sid, text) is not None:
            break
        state["worker_why"] = ("the session tool timed out on session %s" if HUNG else "the session tool could not reach session %s") % sid
        with locked():
            found = pool()
            found.setdefault(sid, {"name": name_of(slug), "slug": slug})["state"] = "unreachable"
            save_pool(found)
        sid = None
        if HUNG:
            break
    if not sid:
        return False
    with locked():  # an operator's bind during the send wins
        found = pool()
        entry, current = found.get(sid) or {}, load(slug) or state
        if entry.get("slug") != slug or entry.get("state") != "busy" or current.get("bound_at") != start.get("bound_at") or (
                current.get("session") or {}).get("id") not in (None, sid, before):
            if entry.get("slug") == slug and entry.get("state") == "busy":
                entry["state"] = "free"
                save_pool(found)
            print("HANDED %s elsewhere during the send; session %s keeps no claim" % (slug, sid))
            return True
        current.update(worker="session", worker_why="", session={"id": sid, "name": name_of(slug)}, pid=None,
                       status="running", bound_at=now())
        graph.stamp(current)
        save(current, "assigned to session %s (%s)%s" % (sid, name_of(slug), ", reused" if reused else ""))
        state.update(current)
    return True


def config():
    return read(os.path.join(git("rev-parse", "--show-toplevel"), ".loop", "config.json"), {})


def held(slug):
    state = load(slug)
    if not state:
        entry = (graph.assigned(pool()) or {}).get(slug) if SLUG.match(slug or "") else None
        if entry:
            sys.exit("REFUSED: %s is assigned to session %s but not frozen yet. Fix: the worker runs goal.py new %s --here "
                     "in its worktree, then sessions.py bind %s %s." % (slug, entry.get("name") or entry["id"], slug, slug, entry["id"]))
        sys.exit("REFUSED: no run named %s." % slug)
    graph.refuse(state)
    return state


def bad_slug(slug):
    if not SLUG.match(slug or ""):
        sys.exit("REFUSED: bad goal name '%s': use lowercase letters, digits and hyphens, starting with a letter or "
                 "digit, at most 51 characters." % slug)


def alive(pid):
    try:
        proctree.probe(int(pid))
    except PermissionError:
        return True
    except (OSError, ValueError, TypeError):
        return False
    return True


def cmd_assign(args):
    state = held(args.slug)
    if state.get("status") in ("running", "waiting", "done") and (state.get("session") or state.get("pid")):
        sys.exit("REFUSED: %s is %s with a worker; nothing was sent. Fix: free it first (sessions.py free)." % (args.slug, state["status"]))
    if not assign(state, args.text, config()):
        print("BACKGROUND %s: %s" % (args.slug, state["worker_why"]))
        return 1
    return 0


def cmd_owner_words(args):
    """Append the owner's message to owner-words.tsv, print OWNER-WORDS <id> <ids>; refuse a worker, no text or no ids."""
    import auto
    ids = [item.strip() for item in args.ids.split(",") if item.strip()]
    if os.environ.get("LOOP_ROLE") == "worker":
        sys.exit("REFUSED: only the operation session records the owner's words; a worker never does. Nothing was written.")
    if not args.text.strip() or not ids:
        sys.exit("REFUSED: give the owner's exact message and --ids (requirement IDs or page names it covers). Nothing was written.")
    where = auto.owner_words_path()
    os.makedirs(os.path.dirname(where), exist_ok=True)
    count = len(auto.owner_rows())
    with open(where, "a", encoding="utf-8") as handle:
        handle.write("o%d\t%s\t%s\t%s\t%s\n" % (count + 1, auto.stamp(), os.environ.get("LOOP_OPERATION_SESSION") or "operation",
                                              json.dumps(args.text, ensure_ascii=False), ",".join(ids)))
    print("OWNER-WORDS o%d covers %s" % (count + 1, ",".join(ids)))
    return 0


def cmd_bind(args):
    return worker.cmd_bind(sys.modules[__name__], args)


def cmd_free(args):
    bad_slug(args.slug)
    with locked():
        found, state = pool(), load(args.slug)
        graph.refuse(state or {})
        if state.get("pid") and state.get("status") == "running" and alive(state["pid"]):
            sys.exit("REFUSED: %s is running as background pid %s; let it end first." % (args.slug, state["pid"]))
        if state.get("status") == "waiting":
            ask = (state.get("waiting") or {}).get("ask") or "a question"
            sys.exit("REFUSED: %s is waiting on the owner (%s); answer it first. Nothing was changed." % (args.slug, ask))
        count = release(args.slug, found, mark=True)
        save_pool(found)
        slot = state.get("worker") == "session" or bool(count and not state)
        if state.get("worker") == "session":
            state.update(worker="", session=None)
            save(state, "freed %d session(s); slot released" % count)
    if not count and not slot:
        print("NOTHING TO FREE for %s: no busy session and no session run." % args.slug)
    else:
        print("FREED %d session(s) for %s; %s. Free only a session that has stopped: this doesn't stop a worker."
              % (count, args.slug, "slot released" if slot else "slot already free"))
    return 0


def cmd_report(args):
    state = held(args.slug)
    said = args.status
    if pool_module().stale(state, args):  # issue 114
        return 0
    if state.get("status") == "done" and (said in ("", "running", "failed") or (said == "waiting" and args.ask) or graph.merged(state)):
        # done is final (issue 108): record the report only
        text = args.text or "%s: %s" % ((state.get("session") or {}).get("name") or args.slug, said or "report")
        state.setdefault("reports", []).append({"at": now(), "step": args.step or state.get("step") or "-", "status": said or "-", "text": text})
        del state["reports"][:-30]
        if args.hold:
            state["hold_at"] = now()
        save(state, "session report kept (done is final): " + text)
        print("KEPT done for %s: report recorded, status %s not applied (done is final)." % (args.slug, said or "(none)"))
        if said == "merged":  # issue 175
            print("\n".join(pool_module().return_session(args.slug, merged=True)) or "NOTHING TO FREE")
        return 0
    if said in ("merged", "failed") or (said == "waiting" and not args.ask):
        pool()  # check the pool can be written before any change
    if args.hold:
        state["hold_at"] = now()  # #3868
    elif args.step or args.status == "running":
        state.pop("hold_at", None)
    if args.step:
        state["step"] = args.step
    if args.pr:
        state["pr"] = args.pr
    pr, said = state.get("pr", ""), args.status
    ended = said in ("merged", "failed") or (said == "waiting" and not args.ask)
    if said == "waiting" and args.ask:
        old = state.get("waiting") or {}  # the same question again keeps full auto's decision
        state.update(status="waiting", waiting=dict({"auto": old["auto"]} if old.get("auto") and old.get("ask", "").split() == args.ask.split() else {},
                     ask=args.ask, words=args.words or ["go on " + args.slug], at=now(), recommend=args.recommend, kind=args.kind))
    elif said == "failed":
        state.update(status="failed", finding=args.text or state.get("finding") or "the worker session reported failed")
    elif said in ("merged", "waiting"):
        if not pr:
            sys.exit("REFUSED: %s with no pull request. Fix: pass --pr URL." % said)
        state["status"] = "done"  # a report never merges (#3868)
        said = "merged" if merged(pr) else "waiting"
        if said == "waiting" and config().get("auto_merge") is True and state.get("release") != "ask":
            print("NEXT: merge.py %s (a report never merges; the goal's own merge.py or the operation's go does)" % args.slug)
    elif said == "running":
        state["status"] = "running"
    who = (state.get("session") or {}).get("name") or args.slug
    text = args.text or "%s: step %s, %s" % (who, state.get("step") or "-", said or state.get("status"))
    if said == "waiting" and not args.ask:
        text = args.text or "%s reports waiting (%s): its pull request waits for review and merge" % (who, pr)
    state.setdefault("reports", []).append({"at": now(), "step": state.get("step") or "-", "status": said or state.get("status"), "text": text})
    del state["reports"][:-30]
    if said in ("merged", "failed", "waiting"):
        state["report"] = {"status": said, "pr": pr, "text": text, "at": now()}
    save(state, "session report: " + text)  # saved first, so a broken pool can't lose it
    if ended:
        try:
            print("\n".join(pool_module().return_session(args.slug, merged=said == "merged")))
        except PoolUnreadable as error:
            sys.exit("SAVED %s as %s, but its session wasn't freed: the session pool can't be read (%s). Fix: repair "
                     "the pool, then run sessions.py free %s." % (args.slug, state.get("status"), error, args.slug))
    return 0


def cmd_send(args):
    """Send the owner's answer to the goal's worker session; 1 when it has none or can't be reached."""
    state = held(args.slug)
    sid, command = (state.get("session") or {}).get("id"), tool(config())
    if state.get("worker") != "session" or not sid or not command:
        print("NO SESSION for %s: the inbox carries it" % args.slug)
        return 1
    if call(command, "send", sid, " ".join(args.text.split())) is None:
        print("UNREACHED session %s for %s: the inbox carries it (%s)" % (sid, args.slug, LAST_ERROR[0]))
        return 1
    print("SENT to session %s (%s)" % (sid, (state.get("session") or {}).get("name")))
    import unattended; unattended.sent(sid)  # MON-18: counts toward the app's 20-send cap
    return 0


def cmd_list(args):
    for sid, item in sorted(pool().items()):
        print("%s  %s  %s  %s" % (sid, item.get("state"), item.get("name"), item.get("slug")))
    return 0


def main():
    proctree.outcap("sessions.py")  # GRD-15: at most 2,000 characters of output
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = parser.add_subparsers(dest="cmd", required=True)
    item = sub.add_parser("assign")
    item.add_argument("slug")
    item.add_argument("--text", default="")
    item = sub.add_parser("bind")
    item.add_argument("slug")
    item.add_argument("id")
    item.add_argument("--name", default="")
    item.add_argument("--force", action="store_true")
    item.add_argument("--cwd", default="")
    item = sub.add_parser("free")
    item.add_argument("slug")
    item = sub.add_parser("report")
    item.add_argument("slug")
    item.add_argument("--status", default="", choices=["", "running", "waiting", "merged", "failed"])
    for flag in ("--step", "--pr", "--text", "--ask", "--recommend", "--attempt"):
        item.add_argument(flag, default="")
    item.add_argument("--words", action="append", default=[])
    item.add_argument("--hold", action="store_true", help="the goal is held: only its own merge.py or the operation's go merges it")
    item.add_argument("--kind", default="", choices=["", "routine", "destructive", "money", "security", "owner"])
    item = sub.add_parser("send")
    item.add_argument("slug")
    item.add_argument("text")
    item = sub.add_parser("owner-words")
    item.add_argument("text")
    item.add_argument("--ids", default="")
    sub.add_parser("list")
    args = parser.parse_args()
    try:
        return globals()["cmd_" + args.cmd.replace("-", "_")](args)
    except PoolUnreadable as error:
        sys.exit("REFUSED: the session pool %s can't be read (%s). Fix: check it with python3 -m json.tool %s, then "
                 "repair it (moved aside, every held goal is forgotten), and run this again. Nothing was changed." % (pool_path(), error, pool_path()))


if __name__ == "__main__":
    sys.exit(main())
