#!/usr/bin/env python3
"""Re-plan the goal graph at each check-in to finish soonest (MON-10). Run by operate.py after watch, every pass.

usage: replan.py [plan]       re-read every goal's progress, log what changed and why, print the new changes
       replan.py since ISO    print the changes logged after a time (the check-in lists those since the last one)

What it does, and only this:
- starts: each goal watch starts (dependencies merged, a slot free) is logged with its reason, so no ready goal sits idle unexplained;
- merges: queued goals with the same PRD (first word of `prd:`) and overlapping `touches:` are proposed merged (a goal missing either is never proposed);
- splits: a goal that two or more queued goals wait on, whose queue line names `parts:`, is proposed split so that part can start first;
- merge line: done goals with an open pull request, critical path first (most goals waiting, then longest time left); advisory.
It never stops, restarts or edits a goal or applies a merge or split: the owner does, with board.py retire and a new queue line.
Each change goes once into <git common dir>/loop/replan.log as `<time> <kind> <slugs>: <reason>`; a repeat is not logged or shown again.
"""
import argparse
import atexit
import datetime
import json
import os
import subprocess
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import board_status as bs  # noqa: E402
import graph  # noqa: E402
import auto  # noqa: E402
from auto import loop_dir, top as root  # noqa: E402,F401
import sessions as se  # noqa: E402
os.environ.update(GIT_TERMINAL_PROMPT="0", GH_PROMPT_DISABLED="1", GIT_EDITOR="true", GIT_ASKPASS="true", SSH_ASKPASS="true")  # no prompt ever blocks


def runs(folder):
    out = {}
    for name in sorted(os.listdir(os.path.join(folder, "runs"))) if os.path.isdir(os.path.join(folder, "runs")) else []:
        run = bs.read_json(os.path.join(folder, "runs", name)) if name.endswith(".json") else None
        if isinstance(run, dict) and graph.SLUG.match(str(run.get("slug", ""))):
            out[run["slug"]] = run
    return out


def queue(top):
    try:
        with open(os.path.join(top, ".loop", "queue.md")) as handle:
            return [item for item in map(graph.parse, handle.read().splitlines()) if item and graph.SLUG.match(item["slug"])]
    except OSError:
        return []


def dependents(lines):
    """{slug: set of goals that wait on it, directly or through others}."""
    direct = {}
    for item in lines:
        for dep in item["depends"]:
            direct.setdefault(dep, set()).add(item["slug"])
    out = {}
    for slug in direct:
        seen, todo = set(), list(direct[slug])
        while todo:
            here = todo.pop()
            if here not in seen:
                seen.add(here)
                todo += list(direct.get(here, ()))
        out[slug] = seen
    return out


def proposals(lines, records):
    """[(kind, slugs, reason)] for this pass."""
    out = []
    by = {item["slug"]: item for item in lines}
    for slug, run in sorted(records.items()):
        if run.get("status") in graph.LIVE and slug in by:
            met = ", ".join(by[slug]["depends"]) or "none"
            out.append(("start", slug, "started: dependencies met (%s) and a slot was free" % met))
    queued = [item for item in lines if item["slug"] not in records]
    for i, a in enumerate(queued):
        for b in queued[i + 1:]:
            same = a["prd"] and b["prd"] and a["prd"].split()[0] == b["prd"].split()[0]
            shared = sorted(set(a["touches"]) & set(b["touches"]))
            if same and shared:
                out.append(("merge", "%s+%s" % (a["slug"], b["slug"]), "same PRD %s and shared files %s: propose one goal"
                            % (a["prd"].split()[0], ", ".join(shared[:3]))))
    waits = dependents(lines)
    for item in lines:
        held = sorted(s for s in waits.get(item["slug"], ()) if s not in records)
        live = item["slug"] not in records or (records[item["slug"]].get("status") in graph.LIVE)
        if live and len(held) >= 2 and item["parts"]:
            out.append(("split", item["slug"], "%d goals wait on it (%s); propose starting part %s first"
                        % (len(held), ", ".join(held[:4]), item["parts"][0])))
    line = [slug for slug, run in records.items() if run.get("status") == "done" and not graph.merged(run)]
    if len(line) > 1:
        line.sort(key=lambda slug: (-len(waits.get(slug, ())), slug))
        out.append(("order", ",".join(line), "merge line, critical path first: %s (advisory)" % " > ".join(line)))
    return out


def plan(top=None, at=None):
    """Log this pass's new changes; return them as lines."""
    top = top or root()
    folder = loop_dir(top)
    at = at or datetime.datetime.now(datetime.timezone.utc)
    seen_path = os.path.join(folder, "replan.json")
    seen = bs.read_json(seen_path) or {}
    seen = seen if isinstance(seen, dict) else {}
    records = runs(folder)
    found, _ = graph.read_pool(os.path.join(folder, "session-pool.json"))
    graph.stamp_held(list(records.values()), graph.assigned(found), at, folder)  # true held time (issue 115)
    new = []
    for kind, slugs, reason in proposals(queue(top), records):
        key = "%s %s" % (kind, slugs)
        if seen.get(key) != reason:
            seen[key] = reason
            new.append("%s %s %s: %s" % (at.strftime("%Y-%m-%dT%H:%M:%SZ"), kind, slugs, reason))
    if new:
        os.makedirs(folder, exist_ok=True)
        with open(os.path.join(folder, "replan.log"), "a") as handle:
            handle.write("\n".join(new) + "\n")
        tmp = seen_path + ".%d.tmp" % os.getpid()
        with open(tmp, "w") as handle:
            json.dump(seen, handle, indent=1, sort_keys=True)
        os.replace(tmp, seen_path)
    return new


def open_proposals(top):
    """Merge and split proposals still true now, as '<kind> <slugs>: <reason>', shown at every check-in until acted on."""
    return ["%s %s: %s" % (kind, slugs, reason) for kind, slugs, reason in proposals(queue(top), runs(loop_dir(top)))
            if kind in ("merge", "split")]


def since(top, stamp):
    return auto.since(top, stamp, "replan.log")


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = parser.add_subparsers(dest="cmd")
    sub.add_parser("plan")
    item = sub.add_parser("since")
    item.add_argument("stamp")
    args = parser.parse_args()
    args.cmd == "since" and bs.timed(args.stamp)
    lines = since(root(), args.stamp) if args.cmd == "since" else plan()
    print("\n".join(lines) if lines else "REPLAN: no change")
    return 0



# The goal limits (GRD-2): max_active_goals, plan_pause_percent and min_free_memory_gb decide whether a new goal starts.
# pool.py usage PERCENT records the plan usage; watch.py and checkin.py read the rest. A limit set to 0 is off.


def number(cfg, key, default):
    """A whole number setting; unset gives the default, 0 turns the limit off, anything unreadable gives the default."""
    value = cfg.get(key, default)
    return value if isinstance(value, int) and not isinstance(value, bool) and value >= 0 else default


def active_limit(cfg):
    """Goals live at once: the smaller of `parallel` and `max_active_goals` (default 20); 0 means no limit."""
    caps = [n for n in (graph.parallel_of(cfg), number(cfg, "max_active_goals", 20)) if n]
    return min(caps) if caps else 0


def plan_usage():
    """The account's weekly plan usage in percent, as the operation session recorded it (`pool.py usage N`) in the last 12 hours, else None."""
    try:
        held = se.read(os.path.join(se.base(), "plan-usage.json"), {})
        age = time.time() - graph.parse_at(held["at"]).timestamp()
        return float(held["percent"]) if 0 <= age < 43200 else None
    except (KeyError, TypeError, ValueError, AttributeError, OSError):
        return None


def plan_pause(cfg):
    """Why no new goal starts, or '': weekly plan usage above plan_pause_percent (default 80, 0 turns it off). Unread usage never pauses."""
    limit, used = number(cfg, "plan_pause_percent", 80), plan_usage()
    return "plan usage %g%% is above plan_pause_percent %d%%; no new goal starts until it falls (PLAN_PAUSE)" % (used, limit) if limit and used is not None and used > limit else ""


def memory_hold(cfg):
    """Why no new goal starts, or '': free memory (workflow-regression's memory.free_gb, loaded by path) below min_free_memory_gb (default 4, 0 is off)."""
    need = cfg.get("min_free_memory_gb", 4)
    if isinstance(need, bool) or not isinstance(need, (int, float)) or need <= 0:
        return ""
    try:
        import importlib.util
        spec = importlib.util.spec_from_file_location("memory", os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "workflow-regression", "scripts", "lanes_cli.py"))
        memory = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(memory)
        free = memory.free_gb()
    except Exception:
        return ""
    return "free memory %.1f GB is below min_free_memory_gb %g; no new goal starts (LOW_MEMORY)" % (free, need) if free is not None and free < need else ""


def memory_waits(root_loop, hours=1):
    """The lane waits for memory logged by the last `hours` (<git common dir>/loop/memory-waits.log), newest last."""
    try:
        with open(os.path.join(root_loop, "memory-waits.log")) as handle:
            lines = handle.read().splitlines()
    except OSError:
        return []
    cut = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(time.time() - 3600 * hours))
    return [line for line in lines if line[:20] >= cut]


def cmd_usage(args, cfg):
    se.write(os.path.join(se.base(), "plan-usage.json"), {"percent": args.percent, "at": graph.iso(datetime.datetime.now(datetime.timezone.utc))})
    print("PLAN USAGE %g%% recorded: %s" % (args.percent, plan_pause(cfg) or "no pause"))
    return 0


# The merge slot (GRD-2): a goal whose pr lane has started holds it until it merges or fails, so the merge.py of a goal that
# started its lane later waits for it. graph.pr_queue(op, runs, slug) forwards hold, free and before here.
def folder(runs):
    return os.path.join(os.path.dirname(runs), "pr-slots")


def pr_hold(runs, slug):
    """Take the slot at the lane's start (the first start time stays) and keep it fresh on each call."""
    path = os.path.join(folder(runs), slug)
    os.makedirs(folder(runs), exist_ok=True)
    if not os.path.exists(path):
        with open(path, "w") as handle:
            handle.write(str(time.time_ns()))
    os.utime(path)


def pr_free(runs, slug):
    try:
        os.unlink(os.path.join(folder(runs), slug))
    except OSError:
        pass


def pr_before(runs, slug):
    """The other goal that holds the slot and started its lane before slug's, else "". A holder silent for
    LOOP_MERGE_LOCK_SECONDS (1800) is dropped; a goal with no slot of its own waits for none."""
    limit, held = int(os.environ.get("LOOP_MERGE_LOCK_SECONDS") or 1800), []
    try:
        for name in os.listdir(folder(runs)):
            path = os.path.join(folder(runs), name)
            if time.time() - os.path.getmtime(path) > limit:
                os.unlink(path)
            else:
                held.append((int(open(path).read()), name))
    except (OSError, ValueError):
        pass
    mine = dict((n, j) for j, n in held).get(slug)
    return min([(j, n) for j, n in held if n != slug and j < mine] or [(0, "")])[1] if mine else ""


def pr_wait(runs, slug):
    """merge.py: wait while another goal's pr lane that started first holds the slot, keeping this goal's own fresh, and give
    the slot back when merge.py ends."""
    atexit.register(lambda: pr_free(runs, slug))
    told = ""
    while ahead := pr_before(runs, slug):
        told == ahead or print("WAITING: %s's pr lane started first and holds the merge slot; waiting for it to merge or fail" % ahead)
        told = ahead
        pr_hold(runs, slug)
        time.sleep(float(os.environ.get("LOOP_SLOT_POLL") or 20))


# ---- pre-flight (#4535): the owner inputs a goal can foresee are asked once, at freeze; its hard ETA starts at the answers.
# The record holds {"items": [{id, ask, options, recommend}]}; answers sit in the owner-only sidecar (preflight_answers).
def api_quota(top):
    """GitHub REST requests left, None when unknown or no GitHub remote (LOOP_API_QUOTA stands in for gh in tests)."""
    try:
        if os.environ.get("LOOP_API_QUOTA") is not None:
            return int(os.environ["LOOP_API_QUOTA"])
        if "github.com" not in subprocess.run(["git", "remote", "get-url", "origin"], cwd=top, capture_output=True, text=True).stdout:
            return None
        out = subprocess.run(["gh", "api", "rate_limit", "--jq", ".resources.core.remaining"], cwd=top, capture_output=True, text=True, timeout=20)
        return int(out.stdout.strip()) if out.returncode == 0 else None
    except (OSError, ValueError, subprocess.SubprocessError):
        return None


def private_hits(top, touches):
    """What the private-name list would refuse in the names a goal touches, the pages every pr re-renders and the repo's own
    name (redacted by the scan), or the list's own break; [] when clean, absent or unreadable."""
    try:
        import importlib.util
        spec = importlib.util.spec_from_file_location("pf_private", os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "workflow-delivery", "scripts", "private.py"))
        private = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(private)
        paths = [t for t in touches if not str(t).startswith("github:")] + ["docs/wiki"]
        listed = subprocess.run(["git", "ls-files", "--"] + paths, cwd=top, capture_output=True, text=True).stdout.split()
        found = private.scan(top, None, texts={n: n for n in sorted(set(listed + [os.path.basename(top)]))})
        return found["hits"] if found["state"] == "hit" else [found["note"]] if found["state"] == "broken" else []
    except Exception:
        return []


def dry_items(top, cfg, touches):
    """The guards a goal can run before its push, as pre-flight items; only a dry run that would refuse gives one."""
    items, why, hits, left = [], memory_hold(cfg), private_hits(top, touches), api_quota(top)
    why and items.append({"id": "memory", "ask": why, "options": ["lower min_free_memory_gb to the free memory", "keep the floor"], "recommend": "lower min_free_memory_gb to the free memory"})
    hits and items.append({"id": "private", "ask": "the private-name list would refuse: " + "; ".join(hits[:4]), "options": ["edit the list line", "rename the file"], "recommend": "edit the list line"})
    left is not None and left < 50 and items.append({"id": "quota", "ask": "the GitHub API quota is %d requests; pr steps stall at 0" % left, "options": ["wait for the reset", "go on with local steps"], "recommend": "go on with local steps"})
    return items


def preflight_new(top, cfg, minutes, touches):
    """The freeze list: plan approval (when auto_approve is off), the time budget, then the dry runs that would refuse."""
    items = []
    cfg.get("auto_approve") is not True and items.append({"id": "plan", "ask": "the plan step ends pending and waits for your approval (auto_approve is off)", "options": ["approve ahead", "approve when asked"], "recommend": "approve ahead"})
    items.append({"id": "budget", "ask": "its time budget is %d minutes; held and waiting time may count toward it" % minutes, "options": ["keep", "raise"], "recommend": "keep"})
    return {"items": items + dry_items(top, cfg, touches)}


def preflight_lines(seen):
    """One Needs-you line per goal with open pre-flight items: each item, its options and recommendation, and the take-all word."""
    return ["%s pre-flight, %d open (blocks nothing until its ETA starts): %s; answer \"recommended\" to take every recommendation, or one answer per item" % (
        run["slug"], len(left), "; ".join("%s: %s [%s; recommended: %s]" % (i["id"], i["ask"], " / ".join(i["options"]), i["recommend"]) for i in left))
        for run in seen for left in [auto.eta_open(run)] if left]


def preflight_answer(g, args, state, why):
    """goal.py set --preflight recommended|ID=ANSWER,...: owner words in, the answers into the sidecar; the ETA clock starts at the last one."""
    seen = g.fit.view(state, g.state_dir())
    left, have = auto.eta_open(seen), dict((seen.get("preflight_answers") or {}).get("answers") or {})
    left or g.no("%s has no open pre-flight item; nothing changed." % args.slug)
    rid = auto.eta_record(g, args.owner_record, args.slug, "a pre-flight answer")
    for part in [] if args.preflight == "recommended" else args.preflight.split(","):
        key, _, value = part.partition("=")
        item = next((i for i in left if i["id"] == key.strip()), None)
        if not item or value.strip() not in item["options"]:
            g.no("%r is not an open item with that answer. Fix: %s" % (part, "; ".join("%s=%s" % (i["id"], "|".join(i["options"])) for i in left) or "none are open"))
        have[item["id"]] = value.strip()
    args.preflight == "recommended" and have.update({i["id"]: i["recommend"] for i in left})
    done = not [i for i in left if i["id"] not in have]
    g.guards.add_set(g.state_dir(), args.slug, "preflight_answers", {"answers": have, "record": rid, "spent": bs.active_minutes(state) if done else 0},
                     "set pre-flight answers (record %s): %s" % (rid, why))


def pr_preflight(runs, g, state):
    """Before the pr step the dry runs go again; a refusal that was not on the freeze list is logged as a missed pre-flight item."""
    listed = {i["id"] for i in (state.get("preflight") or {}).get("items") or []} | {m["id"] for m in state.get("missed_preflight") or []}
    for item in dry_items(g.root(), g.config(), state.get("touches") or []):
        if item["id"] not in listed:
            state.setdefault("missed_preflight", []).append({"id": item["id"], "found": item["ask"][:200], "at": graph.iso(datetime.datetime.now(datetime.timezone.utc)),
                                                             "why": "not on the freeze list: it appeared after the goal was frozen and was found at the pr step"})
            g.save(state, "missed pre-flight item %s: %s" % (item["id"], item["ask"][:160]))
            print("MISSED PRE-FLIGHT %s: %s" % (item["id"], item["ask"][:200]))


if __name__ == "__main__":
    sys.exit(main())
