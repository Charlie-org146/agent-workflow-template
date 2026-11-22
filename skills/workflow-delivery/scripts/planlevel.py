#!/usr/bin/env python3
"""DEL-22 Fast plans: a goal's plan level, its limits, side-by-side reviews, and the planning tool's own faults.

  planlevel.py issue SLUG                 print the issue block a tool fault previewed (a worker never files it; the pull request body carries it)
  planlevel.py issue --from-body FILE --live   main's Actions run: file the issue named by the block in a pull request body, once
  planlevel.py run SLUG                   (detached by flow.py) run the level's reviews side by side and write the stamps
  planlevel.py stamp SLUG REVIEW start|end   a session review marks its own start or end (shown as self-reported)
  planlevel.py ready SLUG [--wait N]      READY once every review has ended; WAITING (seconds left); NOT READY (a review failed, or a record cannot be read; plan anyway, say so) (N up to 240)

Every hook calls this module lazily inside try, so a fault here never stops a goal or the board (fit.py loads without it).
"""
import hashlib
import json
import os
import re
import subprocess
import sys
import threading
from planstamps import median, ready, session_stamps, stamps_for
from planfault import block, brief_goals, fallback_check, fallback_on, faults, issue, mask, quote_of
import time

LEVELS = {"small": {"needs": ["eng"], "minutes": 10}, "normal": {"needs": ["ceo", "dx", "eng"], "minutes": 30},
          "large": {"needs": ["ceo", "dx", "eng", "outside"], "minutes": 45}}
SAFETY = ("guard", "hook", "permission", "private", "lane")
MAX_REVIEWS = 20
NAME = r"[a-z0-9][a-z0-9-]{0,50}"  # a goal slug (goal.py's SLUG allows 51 characters) or a review name
RUNNER_LIMIT = 1900  # a review's own limit is 1800 s
ID = re.compile(r"[A-Z]{2,4}-[0-9]+")


def git(*args, cwd=None, timeout=30):
    done = subprocess.run(["git"] + list(args), capture_output=True, text=True, cwd=cwd, timeout=timeout)
    return done.stdout if done.returncode == 0 else ""


def runs_dir():
    return os.path.join(os.path.abspath(git("rev-parse", "--git-common-dir").strip() or ".git"), "loop", "runs")


def config(top=None):
    """plan_levels from origin/main's committed config, after a bounded fetch that rewrites the remote-tracking ref (GRD-4):
    a locally moved ref, the working tree and a worker-named base are never read. Any failure gives {} (defaults, fallback off); a failed fetch says so."""
    try:
        if subprocess.run(["git", "fetch", "-q", "origin", "+refs/heads/main:refs/remotes/origin/main"], cwd=top, capture_output=True, timeout=20).returncode:
            return {"_fetch_failed": True}  # a failed fetch reads no ref at all: defaults, fallback off
        found = json.loads(git("show", "origin/main:.loop/config.json", cwd=top)).get("plan_levels")
        return found if isinstance(found, dict) else {}
    except (OSError, ValueError, subprocess.SubprocessError):
        return {"_fetch_failed": True}


def limits(cfg):
    out = {}
    for name, base in LEVELS.items():
        over = cfg.get(name) if isinstance(cfg.get(name), dict) else {}
        needs = over.get("needs") if isinstance(over.get("needs"), list) else base["needs"]
        mins = over.get("minutes") if isinstance(over.get("minutes"), int) and not isinstance(over.get("minutes"), bool) and over.get("minutes") > 0 else base["minutes"]
        needs = [str(n) for n in needs if re.fullmatch(NAME, str(n))]  # a review that could never stamp is left out (fixes() says so)
        out[name] = {"needs": (needs or base["needs"])[:MAX_REVIEWS], "minutes": mins}
    return out


def fixes(cfg):
    """One FIX line per bad plan_levels value (it names the key and the default it falls back to); a typo never silently restores a default."""
    out = []
    for name, base in LEVELS.items():
        over = cfg.get(name) if isinstance(cfg, dict) else None
        if isinstance(over, dict) and "minutes" in over and not (isinstance(over["minutes"], int) and not isinstance(over["minutes"], bool) and over["minutes"] > 0):
            out.append("FIX plan_levels.%s.minutes: not a positive whole number; the default %d is used" % (name, base["minutes"]))
        if isinstance(over, dict) and "needs" in over and not (isinstance(over["needs"], list) and over["needs"] and all(re.fullmatch(NAME, str(n)) for n in over["needs"])):
            out.append("FIX plan_levels.%s.needs: not a list of review names (lowercase letters, digits, dashes); the invalid ones are left out" % name)
    return out


def level_of(lines, touches, top, cfg=None):
    """One decision table, first match wins; pure given the tree at freeze. Returns {"level", "rule"}."""
    import fitkit
    words = [w.lower() for w in ((cfg or {}).get("safety_words") if isinstance((cfg or {}).get("safety_words"), list) else SAFETY)]
    areas = sorted({a for a in (fitkit.area(t, top) for t in touches) if a})
    if not touches:
        return {"level": "large", "rule": "no touches"}
    if any(fitkit.surface(t) not in ("", None) for t in touches):
        return {"level": "large", "rule": "touches GitHub"}
    if len(areas) > 1:
        return {"level": "large", "rule": "%d areas" % len(areas)}
    for word in words:
        if any(word in text.lower() for text in list(touches) + list(lines)):
            return {"level": "large", "rule": "safety word " + word}
    named = [m for line in lines for m in ID.findall(line)]
    if areas and named:
        return {"level": "normal", "rule": "one area, names " + named[0]}
    return {"level": "small", "rule": "one area, no ID" if areas else "no code area"}


def sidecar(slug):
    path = os.path.join(runs_dir(), slug + ".plan.json")
    try:
        with open(path) as handle:
            held = json.load(handle)
        return held if isinstance(held, dict) else {}
    except (OSError, ValueError):
        return {}


def save(slug, held):
    path = os.path.join(runs_dir(), slug + ".plan.json")
    tmp = "%s.%d.tmp" % (path, os.getpid())
    with open(tmp, "w") as handle:
        json.dump(held, handle, indent=1)
    os.replace(tmp, path)


def reviews_for(state, cfg):
    plan = state.get("plan")
    if not isinstance(plan, dict):  # a goal frozen before DEL-22 keeps today's prompt: no review set is ordered for it
        return []
    return limits(cfg)[plan.get("level") if plan.get("level") in LEVELS else "large"]["needs"]  # a level that cannot be read is large, never lighter


def run_reviews(names, command, slug, runs, attempt=None):
    """Start every review at once (a thread each, its own process), wait for the slowest, and write the stamps: the runner's, measured."""
    rows, outs = [{} for _ in names], [""] * len(names)

    def one(i):
        rows[i]["name"], rows[i]["started"] = names[i], time.time()
        try:
            done = subprocess.run(list(command) + [names[i]], capture_output=True, text=True, timeout=1800)
            outs[i] = done.stdout
            rows[i]["failed"] = done.returncode != 0
        except (OSError, subprocess.SubprocessError) as why:
            outs[i], rows[i]["failed"] = "review %s did not run: %s" % (names[i], type(why).__name__), True
        rows[i]["ended"] = time.time()
    threads = [threading.Thread(target=one, args=(i,)) for i in range(len(names))]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()
    stamps = {"version": 1, "goal": slug, "attempt": attempt or str(int(rows[0]["started"] * 1000)), "source": "runner", "reviews": rows,
              "ready": max(r["ended"] for r in rows), "failed": [r["name"] for r in rows if r.get("failed")], "outputs": [o.strip()[:2000] for o in outs]}
    path = os.path.join(runs, slug + ".plan-reviews.json")
    tmp = "%s.%d.tmp" % (path, os.getpid())  # a tmp name of its own, removed with the rest on a new attempt
    with open(tmp, "w") as handle:
        json.dump(stamps, handle, indent=1)
    os.replace(tmp, path)
    return outs


def ask(slug, base):
    """The plan prompt for this goal; the fault check runs here, at the next ask after a failed plan."""
    top = git("rev-parse", "--show-toplevel").strip() or "."
    cfg = config(top)
    runs = runs_dir()
    try:
        with open(os.path.join(runs, slug + ".json")) as handle:
            state = json.load(handle)
    except (OSError, ValueError):
        state = {}
    held = sidecar(slug)
    new, pos = faults(cfg, held)
    held["log_pos"] = pos
    text = base
    if new:
        quote = quote_of(new[-1])  # None when the private list is broken: a marked entry stands in, never the words
        held.setdefault("refusals", []).append(quote if quote is not None else "<masked: quote withheld, private list broken>")
        key = hashlib.sha256((slug + (quote if quote is not None else json.dumps(new[-1], sort_keys=True))).encode()).hexdigest()[:12]
        held["issue"] = {"key": key, "goal": slug}
    on, why = fallback_check(cfg, slug, top)  # ONE read of origin/main gives the decision and its reason
    held["fallback_why"] = "" if on else "fallback off: " + (mask(why) or "reason withheld (the private list is broken)")
    held["fallback"] = bool(held.get("fallback")) or (bool(new) and on)
    if held["fallback"]:
        text += " The planning tool refused (its guard log is quoted in the goal's record). Take its own fallback: plan by hand with every review at full depth, and say so in the reply."
    names = reviews_for(state, cfg)
    unfinished = not set(names) <= {n for n, v in session_stamps(slug).items() if v.get("ended")} and not stamps_for(slug)[1]  # neither a finished session attempt nor a finished runner attempt
    open_now = held.get("names") == names and held.get("asked_at") and time.time() - held["asked_at"] < RUNNER_LIMIT and unfinished
    if not open_now:  # a new ask is a new attempt (the last one's stamps are not this one's); a re-render of an unfinished attempt keeps its stamps
        held["names"], held["asked_at"], held["attempt"] = names, time.time(), str(int(time.time() * 1000))
        for old in os.listdir(runs):  # the last attempt's stamp files and any orphaned tmp files of this goal go with it
            if old.startswith(slug + ".stamp-") or (old.startswith((slug + ".plan.json.", slug + ".plan-reviews.json.")) and old.endswith(".tmp")):
                try:
                    os.remove(os.path.join(runs, old))
                except OSError:
                    pass
    command = cfg.get("review_command")
    if not names:
        pass
    elif state.get("worker") != "session" and isinstance(command, list) and command:
        held["run"] = {"names": names, "command": command}
        alive = False
        try:  # a recorded pid counts only if it is alive AND started inside the runner's own time limit (a reused pid does not block a new runner)
            os.kill(int(held.get("runner", 0)), 0)
            alive = bool(held.get("runner")) and time.time() - held.get("runner_at", 0) < RUNNER_LIMIT
        except (OSError, ValueError):
            pass
        if not alive:
            held["runner_at"] = time.time()
            save(slug, held)
        alive or held.update(runner=subprocess.Popen([sys.executable, os.path.abspath(__file__), "run", slug], start_new_session=True, stdin=subprocess.DEVNULL,
                         stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, cwd=top).pid)
        text += " The level's reviews (%s) are running side by side now; their outputs and stamps appear in %s.plan-reviews.json when the slowest finishes (its ready field). Do not wait inside one turn: run `python3 planlevel.py ready %s --wait 240` once per turn (a script that waits up to 4 minutes inside itself and prints READY, WAITING with the seconds left, or NOT READY), at most 30 minutes in all; on NOT READY (a review failed or a record cannot be read) or if it never prints READY, plan anyway and say so." % (", ".join(names), slug, slug)
    else:
        text += " Run these reviews side by side: launch all of them in one message as concurrent subagents, each marking its own start and end with planlevel.py stamp, and wait for the slowest across short turns (one `python3 planlevel.py ready %s --wait 240` per turn, never a longer wait): " % slug + ", ".join(names) + "."
    held["asked"] = time.time()
    save(slug, held)
    return text


def record(slug, state, step):
    """On a recorded plan: clear the fallback order, compare the measured minutes with the level's limit (detect-only), store each review's
    seconds, and flag a review past twice the median of at least three earlier ones of the same name (the last 50 plans)."""
    if step != "plan":
        return
    held = sidecar(slug)
    held["fallback"] = False
    level = (state.get("plan") or {}).get("level") or "large"
    cfg = config()  # one read (one git fetch) for the limit and the fix lines
    limit = limits(cfg).get(level, LEVELS["large"])["minutes"]
    source, rows = stamps_for(slug)
    if not rows:  # a session plan: the reviews marked their own start and end with `stamp` (self-reported)
        mine = session_stamps(slug)
        rows = [{"name": n, "started": v["started"], "ended": v["ended"]} for n, v in mine.items() if isinstance(v.get("started"), (int, float)) and isinstance(v.get("ended"), (int, float)) and 0 <= v["ended"] - v["started"] < 1e6][:MAX_REVIEWS]
        source = "self" if rows else ""
    mins = seen = None
    try:
        import fit
        seen = fit.monitor("board_status", True).seconds_by_step(state, time.time()).get("plan")
        mins = round(seen / 60.0, 1) if isinstance(seen, (int, float)) else None
    except Exception:
        mins = seen = None
    past = {}
    plans = [n for n in os.listdir(runs_dir()) if n.endswith(".plan.json") and n != slug + ".plan.json"]
    for name in sorted(plans, key=lambda n: os.path.getmtime(os.path.join(runs_dir(), n)))[-50:]:  # the last 50 PLANS, chosen before reading
        if True:
            try:
                with open(os.path.join(runs_dir(), name)) as handle:
                    for r in (json.load(handle).get("record") or {}).get("reviews", []):
                        past.setdefault(r["name"], []).append(r["seconds"])
            except (OSError, ValueError, KeyError, TypeError, AttributeError):
                continue
    reviews = []
    for r in rows:
        secs = round(r["ended"] - r["started"], 1)
        before = past.get(r["name"], [])[-50:]
        reviews.append({"name": r["name"], "seconds": secs, "source": "measured" if source == "runner" else "self-reported",
                        "flag": len(before) >= 3 and secs > 2 * median(before), "failed": bool(r.get("failed"))})
    cause = "cause unknown"
    if not reviews and held.get("runner"):
        cause = "reviews did not finish (a runner was started, pid %s, and wrote no stamps)" % held["runner"]
    slow = "slowest review " + max(reviews, key=lambda r: r["seconds"])["name"] if reviews else cause
    held["fix"] = fixes(cfg)
    held["record"] = {"level": level, "limit": limit, "minutes": mins, "missed": isinstance(seen, (int, float)) and seen > limit * 60, "cause": slow, "reviews": reviews}
    save(slug, held)


def note(slug, state):
    """The board text for one goal: its level and rule, then what the recorded plan took."""
    plan = state.get("plan")
    if not isinstance(plan, dict):
        return "no plan recorded"
    held = sidecar(slug).get("record")
    head = "plan level %s (%s)" % (plan.get("level"), plan.get("rule"))
    if not held:
        return head
    line = "%s; took %s of %s min" % (head, "not reported" if held["minutes"] is None else held["minutes"], held["limit"])
    if held["missed"]:
        line += "; MISSED: " + held["cause"]
    for r in held["reviews"]:
        line += "\n      %s %ss, tokens not reported (%s)%s" % (r["name"], r["seconds"], r["source"], ("  FLAG: past twice its usual" if r["flag"] else "") + ("  FAILED: its command exited non-zero" if r.get("failed") else ""))
    for fix in sidecar(slug).get("fix") or []:
        line += "\n      " + fix
    if sidecar(slug).get("fallback_why"):
        line += "\n      " + sidecar(slug)["fallback_why"]
    return line


def fault_now(slug):
    """True when the planning tool's own guard log holds a new denial that names its fallback AND the approval covers this goal's release. Read-only:
    the offset moves only at the next ask, which then files the quote and the issue block."""
    top = git("rev-parse", "--show-toplevel").strip() or "."
    cfg = config(top)
    try:
        with open(os.path.join(runs_dir(), slug + ".json")) as handle:
            state = json.load(handle)
    except (OSError, ValueError):
        return False
    return bool(faults(cfg, sidecar(slug))[0]) and fallback_on(cfg, slug, top)


def run(slug):
    held = sidecar(slug)
    spec = held.get("run") or {}
    if not spec.get("names") or not spec.get("command"):
        return 1
    run_reviews(spec["names"], spec["command"], slug, runs_dir(), held.get("attempt"))
    return 0


def main():
    args = sys.argv[1:]
    if args[:1] == ["issue"] and "--from-body" in args:
        with open(args[args.index("--from-body") + 1]) as handle:
            return issue(None, "--live" in args, handle.read())
    if args[:1] == ["issue"] and len(args) == 2:
        return issue(args[1], False)
    if args[:1] == ["run"] and len(args) == 2:
        return run(args[1])
    if args[:1] == ["stamp"] and len(args) == 4 and args[3] in ("start", "end") and re.fullmatch(NAME, args[1]) and re.fullmatch(NAME, args[2]):
        attempt = sidecar(args[1]).get("attempt")
        path = os.path.join(runs_dir(), "%s.stamp-%s.json" % (args[1], args[2]))
        try:
            with open(path) as handle:
                row = json.load(handle)
        except (OSError, ValueError):
            row = {}
        if row.get("attempt") != attempt:  # a file of an earlier attempt starts over: its old "ended" must not survive
            row = {}
        if args[3] == "end" and not isinstance(row.get("started"), (int, float)):  # an end with no start in THIS attempt (a late stamp of an old one) is refused
            print("refused: %s has no start in this attempt of %s" % (args[2], args[1]))
            return 2
        row.update(review=args[2], attempt=attempt)
        row["started" if args[3] == "start" else "ended"] = time.time()
        tmp = "%s.%d.tmp" % (path, os.getpid())  # one writer per review file, and a tmp name of its own
        with open(tmp, "w") as handle:
            json.dump(row, handle)
        os.replace(tmp, path)
        return 0
    if args[:1] == ["ready"] and len(args) in (2, 4) and (len(args) == 2 or args[2] == "--wait"):
        return ready(args[1], min(int(args[3]), 240) if len(args) == 4 and args[3].isdigit() else 0)
    print(__doc__.strip())
    return 0 if args in ([], ["-h"], ["--help"]) else 2


if __name__ == "__main__":
    sys.exit(main())
