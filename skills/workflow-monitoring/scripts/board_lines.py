#!/usr/bin/env python3
"""What the live board draws, in one module: the Dependencies graph and queue blocks (issues 94, 123), the Issues lines (issue 97), pull
request states (MON-9: asked in parallel, a MERGED answer kept in <git common dir>/loop/pr-states.json) and the budget, depth and
private-name lines (DEL-8, DEL-6, DEL-9). Imported by live_board.py, board.py, pool.py and checkin.py, not run.

  [>] running   [=] holding or paused   [ ] queued   [?] waiting on you   [!] stuck
"""
import concurrent.futures
import datetime
import importlib.util
import json
import os
import re
import shutil
import subprocess
import sys
import time
import board_page
import board_status as bs
import graph

os.environ.update(GIT_TERMINAL_PROMPT="0", GH_PROMPT_DISABLED="1", GIT_EDITOR="true", GIT_ASKPASS="true", SSH_ASKPASS="true")

WIDTH = 60
MARKS = {"running": ">", "held": "=", "paused": "=", "holding": "=", "awaiting merge": "=", "done": "=", "queued": " ",
         "waiting": "?", "failed": "!", "stopped": "!", "stuck": "!", "silent": "!", "freezing": ">", "merged": "x"}
LEGEND = "[>] running [=] holding [ ] queued [?] you [!] stuck"


def box(node, cut):
    return "[%s] %s%s%s" % (MARKS.get(node.get("mark"), " "), node["slug"], " owned by " + node["owner"] if node.get("owner") else "",
                            " (cycle)" if node["slug"] in cut else "")


def pack(pieces, width, gap="  "):
    """Pieces side by side, wrapped at width; a longer piece stands alone."""
    lines, line = [], ""
    for piece in pieces:
        if line and len(line) + len(gap) + len(piece) > width:
            lines.append(line)
            line = ""
        line = piece if not line else line + gap + piece
    return lines + ([line] if line else [])


def cycled(nodes):
    """Slugs that can reach themselves through what they wait on."""
    by = {node["slug"]: node["depends"] for node in nodes}

    def reach(start):
        seen, todo = set(), list(by[start])
        while todo:
            slug = todo.pop()
            if slug not in seen:
                seen.add(slug)
                todo += by.get(slug, [])
        return seen

    return {slug for slug in by if slug in reach(slug)}


def render(items, width=WIDTH):
    """Dependencies lines; items are dicts of slug, mark and depends."""
    if not items:
        return ["- (none)"]
    known = {node["slug"] for node in items}
    nodes = [dict(node, depends=[d for d in node.get("depends") or [] if d in known]) for node in items]
    cut = cycled(nodes)
    bands = board_page.levels(nodes)
    out = pack([box(node, cut) for node in bands[0]], width) if bands else []
    for band in bands[1:]:
        out += ["  |", "  v"]
        for node in band:
            line = "%s <- %s" % (box(node, cut), ", ".join(node["depends"]))
            out += pack([line], width)
    return out + ["", LEGEND]


BUILD = ("running", "holding", "silent")


def eta(at, sec, why="no estimate"):
    """An ETA cell: clock time and span, now, or unknown with its reason."""
    return "ETA unknown: " + why if sec is None else "ETA " + ("%s (about %s)" % ((at + datetime.timedelta(seconds=sec)).astimezone().strftime("%H:%M"), board_page.span(sec)) if sec else "now")


def progress(root, slug, run, step, lines):
    """(done, total, by_rows) per frozen done line: its passing linked rows, else its flow steps."""
    path = os.path.join((run or {}).get("worktree") or root, ".loop")
    try:
        found = re.findall(r"(?m)^\d+\. ", open(os.path.join(path, "goals", slug + ".md")).read().split("## Done lines")[1].split("\n## ")[0])
    except (OSError, IndexError):
        found = lines
    try:
        ran = {c[0]: c[1] for c in (l.split("\t") for l in open(os.path.join(path, "regression-runs.tsv"))) if len(c) > 1}
        tied = [c for c in (l.split("\t") for l in open(os.path.join(path, "regression.tsv"))) if len(c) > 3]
    except OSError:
        ran, tied = {}, []
    rows = [[c[0] for c in tied if c[3].strip() == "%s:%d" % (slug, n)] for n in range(1, len(found) + 1)]
    return [(sum(ran.get(i) == "PASS" for i in r), len(r), 1) if r else (step, 8, 0) for r in rows]


def bar(done, total):
    return "[%s]" % ("#" * (8 * done // total)).ljust(8, "-")


def bars(item, at):
    """A goal's lines: a bar per frozen done line, with done/total and the goal's ETA."""
    return ["      d%d %s %d/%d%s %s" % (n, bar(d, t), d, t, "" if rows else " by step", eta(at, item.get("left"), item["slug"] + " has no estimate"))
            for n, (d, t, rows) in enumerate(item.get("bars") or [], 1)]


def roll(items, at):
    """A release's roll-up: its goals' done lines and its finish."""
    lines = [x for i in items for x in i.get("bars") or []]
    open_ = [i for i in items if i.get("mark") != "merged"]
    gap = [i["slug"] for i in open_ if i.get("left") is None]
    return "  roll-up %s %d/%d done lines, %s" % (bar(sum(d == t for d, t, _ in lines), len(lines) or 1), sum(d == t for d, t, _ in lines), len(lines),
                                                  eta(at, None if gap else max([i["left"] for i in open_] or [0]), ", ".join(gap) + " has no estimate"))


def queue_view(items, at):
    """One repo's Building now and Queue, in order; a queued goal starts when its needs end."""
    run, wait = [i for i in items if i["mark"] in BUILD], [i for i in items if i["mark"] == "queued"]
    end = {i["slug"]: i.get("left") for i in run}
    out = ["Building now:"] + ["  %s | %s | %s" % (i["slug"], i.get("row", ""), eta(at, i.get("left"), "no step estimate yet")) for i in run] + ["  nothing is building"] * (not run) + ["Queue, in order:"]
    for n, q in enumerate(wait, 1):
        deps = [d for d in q["depends"] if d in end]
        full = str(q.get("why")).startswith("slots full")
        need = deps or ([i["slug"] for i in run] if full else [])
        times = [end[d] for d in need]
        start = None if None in times else (min if full and not deps else max)(times or [0])
        end[q["slug"]] = None if None in (start, q.get("left")) else start + q["left"]
        out.append("  %d. %s | waits for: %s | %s" % (n, q["slug"], q.get("why") or "nothing, starts next", eta(at, start, ", ".join(d for d in need if end[d] is None) + " has no estimate")))
    return out + ["  (none queued)"] * (not wait)


LIMIT = re.compile(r"usage limit|rate limit|limit reached|hit your (?:weekly |daily )?limit|out of (?:usage|credits)|quota", re.I)
RESET = re.compile(r"(?:resets?|reset at|until|try again (?:at|after))\s+(?:at\s+)?([A-Z][a-z]{2,8}\.? \d{1,2},? \d{1,2}(?::\d\d)?\s*(?:[ap]m)?|\d{1,2}(?::\d\d)?\s*[ap]m|\d\d:\d\d(?: UTC)?)", re.I)
CAUSES = [
    ("limit", LIMIT, "usage limit"),
    ("permission", re.compile(r"permission|not allowed|denied|unauthori[sz]ed|forbidden", re.I), "a permission was refused"),
    ("tests", re.compile(r"\btests? (?:failed|red)|lane (?:failed|red)|\bFAIL\b|regression", re.I), "its tests failed"),
    ("tries", re.compile(r"3 failed tries|tries used up|stopped after", re.I), "it used up its tries"),
    ("crash", re.compile(r"ended without finishing|traceback|crash|killed|exit code|no STEP", re.I), "its worker ended early"),
]
LIVE = ("running", "waiting", "failed", "stopped")


def text_of(run):
    return " ".join(str(x) for x in ((run.get("report") or {}).get("text"), run.get("finding")) if x)


def cause(run):
    said = text_of(run)
    for key, pattern, words in CAUSES:
        if pattern.search(said):
            found = RESET.search(said) if key == "limit" else None
            return key, words, found.group(1).strip() if found else ""
    return "other", "it %s; see its log" % (run.get("status") or "stopped"), ""


def stuck(runs, auto_resume=False):
    groups = {}
    for run in runs:
        if run.get("status") in ("failed", "stopped"):
            key, _, until = cause(run)
            groups.setdefault((key, until) if key == "limit" else key, []).append(run)
    out = []
    for key, members in groups.items():
        _, words, until = cause(members[0])
        slugs = [run["slug"] for run in members]
        if isinstance(key, tuple):
            when = " until " + until if until else " until the limit resets"
            out.append("- usage limit: %d goal%s paused%s" % (len(slugs), "" if len(slugs) == 1 else "s", when))
            out.append("    %s" % ", ".join(slugs))
            if auto_resume:
                out.append("    fix: none needed; they resume by themselves after the reset")
            else:
                out.append('    fix: after the reset, type "resume <goal>" for each (resume_on_limit is off)')
        elif len(slugs) > 1:
            out.append("- %d goals stopped: %s" % (len(slugs), words))
            out.append("    %s" % ", ".join(slugs))
            out.append('    fix: look at one, then type "resume <goal>" for each')
        else:
            out.append("- %s is %s: %s" % (slugs[0], members[0].get("status"), words))
            out.append('    fix: look at the problem, then type "resume %s"' % slugs[0])
    return out


def paused(runs):
    live = [run for run in runs if run.get("status") in LIVE]
    if not live or any(run.get("status") not in ("failed", "stopped") or cause(run)[0] != "limit" for run in live):
        return ""
    until = next((cause(run)[2] for run in live if cause(run)[2]), "")
    return "paused until " + (until or "the usage limit resets")


TIMEOUT = float(os.environ.get("LOOP_PR_TIMEOUT", "3"))
WORKERS = 16


def cache_path(root):
    try:
        common = subprocess.run(["git", "rev-parse", "--git-common-dir"], cwd=root, capture_output=True, text=True, timeout=5).stdout.strip()
    except (OSError, subprocess.SubprocessError):
        return ""
    return os.path.join(os.path.abspath(os.path.join(root, common)), "loop", "pr-states.json") if common else ""


def load(path):
    try:
        with open(path) as handle:
            found = json.load(handle)
        return found if isinstance(found, dict) else {}
    except (OSError, ValueError):
        return {}


def save(path, found):
    try:
        os.makedirs(os.path.dirname(path), exist_ok=True)
        tmp = "%s.%d.tmp" % (path, os.getpid())
        with open(tmp, "w") as handle:
            json.dump(found, handle, indent=1, sort_keys=True)
        os.replace(tmp, path)
    except OSError:
        pass


def ask(url, root):
    try:
        done = subprocess.run(["gh", "pr", "view", url, "--json", "state", "-q", ".state"], cwd=root, capture_output=True,
                              text=True, timeout=TIMEOUT)
        out = done.stdout.strip() if done.returncode == 0 else ""
        got = str(json.loads(out).get("state", "") if out.startswith("{") else out).upper()
        return got if got in ("MERGED", "CLOSED", "OPEN") else ""
    except (OSError, ValueError, AttributeError, subprocess.SubprocessError):
        return ""


def fresh(entry):
    return isinstance(entry, dict) and entry.get("state") == "MERGED"


def lookup(urls, root):
    if not shutil.which("gh"):
        return {url: "" for url in urls}
    path, now = cache_path(root), time.time()
    cache = load(path) if path else {}
    out = {url: cache[url]["state"] for url in urls if fresh(cache.get(url))}
    todo = [url for url in dict.fromkeys(urls) if url not in out]
    if todo:
        with concurrent.futures.ThreadPoolExecutor(max_workers=min(WORKERS, len(todo))) as pool:
            for url, got in zip(todo, pool.map(lambda u: ask(u, root), todo)):
                out[url] = got
                if got == "MERGED":
                    cache[url] = {"state": got, "at": now}
        if path:
            save(path, cache)
    return out


HEALTH_TTL = int(os.environ.get("LOOP_HEALTH_TTL", "900"))
REFRESH = r"""
import json, os, re, subprocess, sys, time
script, path = sys.argv[1], sys.argv[2]
try:
    out = subprocess.run([sys.executable, script, "check"], capture_output=True, text=True, timeout=600).stdout
    got = re.search(r"^HEALTH: (not green|green)", out, re.M)
    tmp = path + ".%d.tmp" % os.getpid()
    json.dump({"verdict": got.group(1) if got else "unknown", "at": time.time()}, open(tmp, "w"))
    os.replace(tmp, path)
finally:
    try:
        os.remove(path + ".lock")
    except OSError:
        pass
"""


def health(root, script):
    path = cache_path(root).replace("pr-states.json", "health-verdict.json")
    if not path:
        return "unknown"
    found = load(path)
    age = time.time() - float(found.get("at") or 0)
    if age > HEALTH_TTL and os.path.exists(script):
        try:
            if os.path.exists(path + ".lock") and time.time() - os.path.getmtime(path + ".lock") > 900:
                os.remove(path + ".lock")
            os.close(os.open(path + ".lock", os.O_CREAT | os.O_EXCL | os.O_WRONLY))
            subprocess.Popen([sys.executable, "-c", REFRESH, script, path], cwd=root, stdin=subprocess.DEVNULL,
                             stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, start_new_session=True)
        except OSError:
            pass
    if not found.get("verdict"):
        return "unknown (checking)"
    minutes = int(age // 60)
    return "%s, %s ago" % (found["verdict"], "%dm" % minutes if minutes < 120 else "%dh" % (minutes // 60))


def states(runs, root, merged=lambda run: False):
    wanted = {run["slug"]: run["pr"] for run in runs if run.get("status") == "done" and run.get("pr") and not merged(run)}
    found = lookup(list(wanted.values()), root)
    return {slug: found.get(url, "") for slug, url in wanted.items()}


def state(url, root):
    return lookup([url], root).get(url, "") if url else ""


# ---- budget, decided depth and private-name Issues lines (DEL-8, DEL-6, DEL-9)
FIT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "workflow-delivery", "scripts", "fit.py")
LIST = "~/.workflow-loop/private-names"
SHOWN = "$HOME/.workflow-loop/private-names"


def load_fit():
    """workflow-delivery's fit module, or None when it is missing or broken."""
    if not os.path.exists(FIT):
        return None
    try:
        spec = importlib.util.spec_from_file_location("fit", FIT)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module
    except Exception:
        return None


fit = load_fit()


def mega(n):
    """3.0M, 0.4M, 25k or 500: a small budget never reads as 0.0M."""
    return "%.1fM" % (n / 1e6) if n >= 100000 else "%dk" % round(n / 1000) if n >= 1000 else "%d" % n


def spent(run, at):
    """(whole minutes, tokens) a goal has spent so far."""
    return int(sum(bs.seconds_by_step(run, at).values()) // 60), fit.spent_tokens(run)


def line(run, cfg, at, runs=None):
    """The budget line for one goal, or '' without fit."""
    if fit is None:
        return ""
    held, _ = fit.budget(fit.view(run, runs), cfg)
    minutes, tokens = spent(run, at)
    seconds = sum(bs.seconds_by_step(run, at).values())
    halves, over = [], []
    if held["minutes"] > 0:
        halves.append("%dm of %dm" % (minutes, held["minutes"]))
        over += ["OVER time"] if seconds > held["minutes"] * 60 else []
    if fit.tokens_text(run) == "tokens unread":
        halves.append("tokens unread")
    elif held["tokens"] > 0:
        halves.append("%s of %s tokens" % (mega(tokens), mega(held["tokens"])))
        over += ["OVER tokens"] if tokens >= held["tokens"] else []
    return "budget: " + (", ".join(halves + over) if halves else "none set")


def depth(run, setting, runs=None):
    """The depth the goal is held to and why, or '' without fit."""
    if fit is None:
        return ""
    found, why = fit.depth_for(setting, fit.view(run, runs))
    return "%s (%s)" % (found, why) if why else found


def missing_list():
    given = os.environ.get("LOOP_PRIVATE_NAMES")
    return not os.path.exists(given if given else os.path.expanduser(LIST))


def issues(root, runs=()):
    """Issues lines: the missing list, then each local finding."""
    out = []
    if fit is not None and missing_list():
        out += ["- no private-name list: every push and merge stops (create %s; an empty file passes, o675)" % SHOWN,
                "    fix: write one pattern per line to %s (or point $LOOP_PRIVATE_NAMES at a file)" % SHOWN]
    for run in runs:
        wait = " ".join(str(run.get("release_pr_waiting") or "").split())
        if wait and not run.get("release_url"):
            out += ["- %s: the release pull request waits: %s" % (run["slug"], wait[:200]),
                    "    fix: run merge.py %s again once its checks pass; it merges the release PR and creates the release" % run["slug"]]
        if run.get("review_wait") and not run.get("release_url"):
            out += ["- %s: merge waiting on review (review_hold is on)" % run["slug"],
                    "    fix: the operation session reads the diff, then runs review.py record %s and merge.py %s" % (run["slug"], run["slug"])]
        text = " ".join(str(run.get("finding_error") or "").split())
        if text:
            said, _, fix = text.partition(". Fix: ")
            out += ["- %s: a finding stayed local: %s" % (run["slug"], said[:200]),
                    "    fix: %s" % (fix[:200] or "remove what the scan found, then push the finding commit")]
    return out


def shown(run):
    return bool(run.get("goal") and run.get("status")) and run["status"] != "stopped" and run.get("release") != "leave"


def tasks(root, runs, at, gone=()):  # DEL-23
    import live_board as lb
    by, rows = {r["slug"]: r for r in runs}, lb.task_rows(root)
    ids = {t["slug"]: t for t in rows}
    end = lambda s: s in gone or graph.merged(by.get(s))
    st = lambda s: by[s].get("status")
    live = lambda s: s in by and not end(s) and st(s) != "queued"

    def hop(s):
        for _ in range(5): s = ids.get(s, {}).get("by") or s
        return s

    for t in rows:
        g = t["goals"]
        t["state"] = "replaced" if t["by"] else "done" if g and all(map(end, g)) else "running" if any(live(s) and st(s) not in ("waiting", "failed", "stopped") for s in g) else "waiting" if any(map(live, g)) else "queued"
    cut = cycled([dict(slug=t["slug"], depends=[hop(s) for s in t["needs"]]) for t in rows])
    for t in rows:
        bad = [ids[s]["name"] if s in ids else s + " (no brief)" for s in map(hop, t["needs"]) if s not in ids or ids[s]["state"] != "done"]
        if t["state"] == "queued" and (bad or t["slug"] in cut):
            t["state"], t["note"] = "waiting", t["note"] + "; " * bool(t["note"]) + ("cycle" * (t["slug"] in cut) or "needs " + ", ".join(bad))
        g, mine = t["goals"], [s for s in t["goals"] if live(s)]
        left = [bs.left_time(by[s], runs, at, root) for s in mine]
        t["eta"] = "-" if not mine else "awaiting merge" if all(st(s) == "done" for s in mine) else "?" if None in left else board_page.span(max(left))
        t["done"] = sum(map(end, g))
        t["goals"] = [(s, "finished" if end(s) else "not started" if not live(s) else "awaiting merge" if st(s) == "done" else lb.FLOW[lb.current(by[s])]) for s in g]
    return rows

def gather(root, at, stamp=None):
    import live_board as lb  # lazy: live_board imports this module
    folder, cfg = lb.loop_dir(root), bs.read_json(os.path.join(root, ".loop", "config.json")) or {}
    runs = lb.load(root)
    found, why = graph.read_pool(os.path.join(folder, "session-pool.json"))
    taken = graph.assigned(found)
    landed = states(runs, root, graph.merged)
    stat = {r["slug"]: "merged" if landed.get(r["slug"]) == "MERGED" else "held" if (s := graph.classify(r, taken, at, cfg)) == "silent" and r.get("step") == "pr" else s for r in runs}
    since = graph.parse_at(stamp)
    new = lambda r: stat[r["slug"]] == "merged" and bool(since) and (graph.parse_at(r.get("updated")) or since) > since
    live = [r for r in runs if (stat[r["slug"]] != "retired" and (stat[r["slug"]] != "merged" or new(r))) and shown(r)]
    away = {}
    for r in live:
        if graph.foreign(r):
            count, last, _ = away.get(graph.foreign(r), (0, None, ""))
            away[graph.foreign(r)] = (count + 1, max([t for t in (last, graph.last_spoke(r)) if t] or [None]), r.get("machine") or "")
    live = [r for r in live if not graph.foreign(r)]
    return dict(away=away, name=os.path.basename(root), root=root, cfg=cfg, folder=folder, runs=runs, found=found, why=why, taken=taken,
                states=stat, live=live, queue=bs.queued(root, runs))
