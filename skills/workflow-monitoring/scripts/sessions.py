#!/usr/bin/env python3
"""Worker sessions: each goal runs in its own app session, "worker · <goal>", and reports by session message.

usage: sessions.py <command> [options]

  assign SLUG               give a frozen goal to a free (archived) session, never a new one
  bind SLUG ID|self [--name N] [--force] [--cwd DIR]
                            record an app-started session: ASSIGNED before freezing, BOUND after goal.py new.
                            --force rebinds a freed session. Prints WORKER and WORKTREE
  free SLUG                 give back a stopped session's goal and slot
  report SLUG [--step S] [--status running|waiting|merged|failed] [--pr URL] [--ask Q --words W... --recommend W
              --kind K] [--attempt N] [--text T]
                            a worker's step or result (a counted send). waiting with --ask is a question (auto.py may answer a routine
                            one); without it the pull request waits. merged is checked with gh; an ended goal's session
                            returns to the pool. Done is final (KEPT).
  send SLUG[,SLUG...] TEXT  send the owner's answer: one counted message per worker session
  owner-words TEXT --ids A,B [--from top|peer] [--delegated TDn --doc2 rN]  record the owner's exact message (delegated: the asking words) for its IDs
  list                      sessions and goals

The `session_command` (.loop/config.json) or $LOOP_SESSION_TOOL talks: `TOOL rename ID NAME` and `TOOL send ID TEXT`. With no tool,
or one that fails or times out (LOOP_SESSION_TIMEOUT, 30 s), the goal runs in the background. The pool
(<git common dir>/loop/session-pool.json) changes under a lock and is never written unreadable. Nothing here merges.
"""
import argparse
import contextlib
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.modules.setdefault("sessions", sys.modules[__name__])
import graph  # noqa: E402
import moved_mon  # noqa: E402
import proctree  # noqa: E402
import worker  # noqa: E402
from worker import HUNG, LAST_ERROR, call, fcntl, git, merged, now, tool  # noqa: E402

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
FREE_TRIES = 2
NEW = "a new session needs the owner's typing: wake an archived session or free one"


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
    pass


def pool_path():
    return os.path.join(base(), "session-pool.json")


def reserved():
    """Ids in loop/operation.id (#5616)."""
    import govern_hook
    return govern_hook.operation_ids(os.path.dirname(base()))


def pool():
    found, why = graph.read_pool(pool_path())
    if found is None:
        raise PoolUnreadable(why)
    pool_module().quarantine()
    return found


@contextlib.contextmanager
def locked():
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
    moved_mon.steps().commit(os.path.join(base(), "runs", state["slug"] + ".json"), state, state["updated"])
    print("%s %s: %s" % (state["updated"], state["slug"], note))


def pool_module():
    import pool as found  # pool.py imports this module back
    return found


def name_of(slug):
    return "worker · " + slug


def release(slug, found=None, mark=False):
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
    """Wake a free session for the goal, never start one. False: none or unreachable."""
    command, slug = tool(cfg), state["slug"]
    state["worker"], state["worker_why"] = "background", "no session tool is set (session_command)"
    if not command:
        return False
    found, to = pool(), os.environ.get("LOOP_OPERATION_SESSION", "")
    start = load(slug) or state
    before = (start.get("session") or {}).get("id") if start.get("status") in ("failed", "stopped", "queued", "", None) else None
    text = SEND.format(slug=slug, tree=state.get("worktree") or "its worktree", to=" (%s)" % to if to else "") + worker.worker_line(slug) + "\n\n" + prompt
    free = sorted(s for s, item in found.items() if item.get("state") == "free" and s not in reserved())[:FREE_TRIES]
    state["worker_why"], sid = NEW, None
    for sid in free:
        with locked():
            found = pool()
            if (found.get(sid) or {}).get("state") != "free":
                sid = None
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
    with locked():
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
        save(current, "assigned to session %s (%s)%s" % (sid, name_of(slug), ", woken"))
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
    import operate
    why = state.get("worktree") and operate.untrusted(state["worktree"])
    why and sys.exit(why)
    if not assign(state, args.text, config()):
        print("%s %s: %s" % ("REFUSED" if state["worker_why"] == NEW else "BACKGROUND", args.slug, state["worker_why"]))
        return 1
    return 0


cmd_owner_words = moved_mon.cmd_owner_words


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
    if pool_module().stale(state, args):
        return 0
    if said:
        import unattended; unattended.sent("operation")
    if state.get("status") == "done" and (said in ("", "running", "failed") or (said == "waiting" and args.ask) or graph.merged(state)):
        text = args.text or "%s: %s" % ((state.get("session") or {}).get("name") or args.slug, said or "report")
        state.setdefault("reports", []).append({"at": now(), "step": args.step or state.get("step") or "-", "status": said or "-", "text": text})
        del state["reports"][:-30]
        if args.hold:
            state["hold_at"] = now()
        save(state, "session report kept (done is final): " + text)
        print("KEPT done for %s: report recorded, status %s not applied (done is final)." % (args.slug, said or "(none)"))
        if said == "merged":
            print("\n".join(pool_module().return_session(args.slug, merged=True)) or "NOTHING TO FREE")
        return 0
    if said in ("merged", "failed") or (said == "waiting" and not args.ask):
        pool()
    if args.hold:
        state["hold_at"] = now()
    elif args.step or args.status == "running":
        state.pop("hold_at", None)
    if args.step:
        state["step"] = args.step
    if args.pr:
        state["pr"] = args.pr
    pr, said = state.get("pr", ""), args.status
    ended = said in ("merged", "failed") or (said == "waiting" and not args.ask)
    if said == "waiting" and args.ask:
        old = state.get("waiting") or {}
        state.update(status="waiting", waiting=dict({"auto": old["auto"]} if old.get("auto") and old.get("ask", "").split() == args.ask.split() else {},
                     ask=args.ask, words=args.words or ["go on " + args.slug], at=now(), recommend=args.recommend, kind=args.kind))
    elif said == "failed":
        state.update(status="failed", finding=args.text or state.get("finding") or "the worker session reported failed")
    elif said in ("merged", "waiting"):
        if not pr:
            sys.exit("REFUSED: %s with no pull request. Fix: pass --pr URL." % said)
        state["status"] = "done"
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
    save(state, "session report: " + text)
    if ended:
        try:
            print("\n".join(pool_module().return_session(args.slug, merged=said == "merged")))
        except PoolUnreadable as error:
            sys.exit("SAVED %s as %s, but its session wasn't freed: the session pool can't be read (%s). Fix: repair "
                     "the pool, then run sessions.py free %s." % (args.slug, state.get("status"), error, args.slug))
    return 0


def cmd_send(args):
    """One message per session; 1 if one is not reached."""
    import unattended
    command, by, code = tool(config()), {}, 0
    for slug in args.slug.split(","):
        state = held(slug)
        sid = (state.get("session") or {}).get("id")
        if state.get("worker") != "session" or not sid or not command:
            print("NO SESSION for %s: the inbox carries it" % slug)
            code = 1
        else:
            by.setdefault(sid, []).append((slug, state["session"].get("name")))
    for sid, found in by.items():
        goals = ", ".join(x[0] for x in found)
        if call(command, "send", sid, ("[%s] " % goals) * (len(found) > 1) + " ".join(args.text.split())) is None:
            print("UNREACHED session %s for %s: the inbox carries it (%s)" % (sid, goals, LAST_ERROR[0]))
            code = 1
            continue
        print("SENT to session %s (%s)" % (sid, found[0][1]))
        unattended.sent(sid)
    return code


def cmd_list(args):
    for sid, item in sorted(pool().items()):
        print("%s  %s  %s  %s" % (sid, item.get("state"), item.get("name"), item.get("slug")))
    return 0


def main():
    proctree.outcap("sessions.py")  # GRD-15
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
    item.add_argument("--from", dest="via", default="owner", choices=["owner", "top", "peer"], help="top: relayed owner words (not safety classes); peer: refused")
    item.add_argument("--delegated", default="", help="TDn: a delegated record (DOC-2)")
    item.add_argument("--doc2", default="", help="DOC-2's revision, rN")
    sub.add_parser("list")
    args = parser.parse_args()
    try:
        return globals()["cmd_" + args.cmd.replace("-", "_")](args)
    except PoolUnreadable as error:
        sys.exit("REFUSED: the session pool %s can't be read (%s). Fix: check it with python3 -m json.tool %s, then "
                 "repair it (moved aside, every held goal is forgotten), and run this again. Nothing was changed." % (pool_path(), error, pool_path()))


if __name__ == "__main__":
    sys.exit(main())
