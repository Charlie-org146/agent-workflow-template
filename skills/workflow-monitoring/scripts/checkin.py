#!/usr/bin/env python3
"""The check-in (MON-4, MON-5): what operate.py prints each pass, in the one layout the reply hook checks. usage: checkin.py [--since ISO]
Headline, All sessions, Re-plan, Auto-answered, Archived, Dependencies (per repo: Building now, Queue in order with ETAs, then goals by
release and feature), Needs you (numbered, MON-19), Coming up. --since defaults to the last check-in (<git common dir>/loop/checkin.json).
"""
import argparse
import datetime
import json
import os
import re
import sys
import textwrap

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import auto
import board as bd
import board_status as bs
import board_lines
from board_lines import gather, shown
import govern_hook
import graph
import live_board as lb
import machines
import mend
import notify
import pool as pl
import replan
import unattended
import board_page
from board_status import feature_of, goal_line, release_of

MARK = {"running": "running", "held": "holding", "waiting": "waiting", "failed": "stuck", "stopped": "stuck",
        "silent": "silent", "done": "awaiting merge", "queued": "queued"}


def cell(text, size=48):
    return lb.plain(text, size).replace("|", "/") or "-"


def quoted(words):
    return " / ".join('"%s"' % w for w in words)


def last_at(root):
    return (bs.read_json(os.path.join(lb.loop_dir(root), "checkin.json")) or {}).get("at")


def grouped(blocks, at=None, tags=None, loop=None):
    out, edges, marks = [], [], {name: {item["slug"]: item.get("mark") for item in items} for name, items in blocks}
    key = lambda item: (item.get("release") or "no release", item.get("feature") or "no feature")
    every = {}
    for _, items in blocks:
        for item in items:
            every.setdefault(key(item)[0], []).append(item)
    for name, items in blocks:
        local = [dict(item, depends=[d for d in item.get("depends") or [] if "/" not in d]) for item in items]
        out += ["== %s ==" % (name if len(name) <= 54 else name[:51] + "...")]
        out += board_lines.render(local)[:-2] if items else ["- (none)"]
        out += board_lines.queue_view(items, at) if at else []
        out += ["%s -> %s" % (dep, item["slug"]) for item in local for dep in item["depends"]]
        out += ["owner item: #%d %s needs you" % (tags[name, item["slug"]], item["slug"]) for item in items if (name, item["slug"]) in (tags or {})]
        for release in sorted({key(item)[0] for item in items}):
            out += ["-- %s --" % bs.release_header(release, every[release], at, loop)] + [board_lines.roll(every[release], at)] * bool(at)
            for feature in sorted({key(item)[1] for item in items if key(item)[0] == release}):
                out += ["  %s:" % feature]
                for item in items:
                    out += ["    " + goal_line(item)] + board_lines.bars(item, at) * bool(at) if key(item) == (release, feature) else []
        left = [item["left"] for item in items if item.get("left")]
        out += ["expected finish %s (about %s)" % ((at + datetime.timedelta(seconds=max(left))).astimezone().strftime("%H:%M"), board_page.span(max(left)))] if left and at else []
        edges += [(name, item["slug"], dep.partition("/")[0], dep.partition("/")[2]) for item in items
                  for dep in item.get("depends") or [] if "/" in dep]
    if edges:
        out += ["Between repos"]
        for name, slug, repo, goal in edges:
            mark = marks.get(repo, {}).get(goal, 0)
            out.append("%s/%s <- %s/%s %s" % (name, slug, repo, goal, "(unknown)" if mark == 0 else "[%s]" % board_lines.MARKS.get(mark, " ")))
    out += ["", board_lines.LEGEND]
    return [row for line in out for row in (textwrap.wrap(line, board_lines.WIDTH, subsequent_indent="    ") or [""])]


def others(followed, root, at, stamp, broken=None):
    """The pod's other repos, gathered; one that can't be read is skipped, or added to `broken`."""
    out = []
    for name, path, _ in followed:
        if os.path.realpath(path) != os.path.realpath(root):
            try:
                out.append(gather(path, at, stamp))
            except Exception as error:
                broken is None or broken.append((name, lb.plain(type(error).__name__, 40)))
    return out


def expected(root=None, at=None):
    root = bs.git("rev-parse", "--show-toplevel", cwd=root or None) or root
    at = at or datetime.datetime.now(datetime.timezone.utc)
    stamp, here = last_at(root), os.getcwd()
    os.chdir(root)
    try:
        followed = bd.followed()
    finally:
        os.chdir(here)
    return [(g["name"], item["slug"]) for g in [gather(root, at, stamp)] + others(followed, root, at, stamp) for item in g["live"] + g["queue"]]


def render(root=None, at=None, stamp=None):
    root = root or bs.git("rev-parse", "--show-toplevel")
    at = at or datetime.datetime.now(datetime.timezone.utc)
    stamp = stamp or last_at(root) or "0000"
    mine = gather(root, at, stamp)
    folder, cfg, runs, found, why, taken, states, live, queue = (mine[k] for k in (
        "folder", "cfg", "runs", "found", "why", "taken", "states", "live", "queue"))
    broken = []
    pod = [mine] + others(bd.followed(), root, at, stamp, broken)
    ready, _ = graph.ready(queue, {r["slug"]: r for r in runs}, graph.parallel_of(cfg), taken, why)
    counts = lambda *names: sum(g["states"][r["slug"]] in names for g in pod for r in g["live"] if not graph.foreign(r))
    pool_line = pl.status_line(found or {}, cfg) if found is not None else "pool: unreadable"
    out = ["%d running, %d waiting on you, %d queued; %s" % (counts("running", "held", "silent"),
                                                            counts("waiting", "failed", "stopped"), sum(len(g["queue"]) for g in pod), pool_line),
           *machines.lines(root, cfg, bs.machine_line(cfg))]
    for g in pod:
        out += ["%s%s: %d goal%s, last activity %s" % (name, " (%s)" % machine if machine else "", n, "" if n == 1 else "s",
                                                      last.astimezone().strftime("%H:%M") if last else "unknown")
                for name, (n, last, machine) in sorted(g["away"].items())]
    out += ["",
           "All sessions", "| session | repo | for | status | progress | left | latest |", "|---|---|---|---|---|---|---|"]
    for g in pod:
        for run in g["live"]:
            step = lb.current(run)
            left = bs.left_time(run, g["runs"], at)
            out.append("| %s | %s | %s | %s | %s %d/8 | %s | %s |" % (
                cell(lb.worker_of(run, g["taken"]), 30), g["name"], cell(bs.intro(run.get("goal"), run["slug"]), 70), MARK.get(g["states"][run["slug"]], g["states"][run["slug"]]),
                lb.FLOW[step], step + 1, ("?" if left is None else board_page.span(left)) + ", " + auto.eta_text(auto.eta_seen(g["root"], run), at), cell(lb.latest_report(run) or run.get("next"), 60)))
    if not any(g["live"] for g in pod):
        out.append("| - | %s | nothing running | - | - | - | - |" % mine["name"])
    changes = replan.since(root, stamp)
    decided = auto.since(root, stamp)
    open_now = replan.open_proposals(root)
    if changes or open_now:
        out += ["", "Re-plan (since the last check-in, then proposals still open):"] + ["- " + line[21:] for line in changes[-8:]]
        out += ["- open: %s" % line for line in open_now if not any(line in c for c in changes)][:6]
    if decided:
        out += ["", "Auto-answered (full auto):"]
        for line in decided[-8:]:
            parts = [p.strip() for p in line.split(" | ")]
            if len(parts) >= 6:
                out.append('- %s: "%s" -> %s; revert: operate.py send %s "<other words>" (rule %s)' % (parts[1], parts[3][:60], parts[4], parts[1], parts[5].split()[-1]) if parts[2] == "AUTO"
                           else "- %s waits for you: %s" % (parts[1], parts[5]))
    filed = auto.since(root, stamp, "findings.log")  # OPS-1: what the operation layer filed since the last check-in
    if filed:
        out += ["", "Findings filed (operation layer):"] + ["- " + line[23:] for line in filed[-8:]]
    given = [r for r in auto.owner_rows(root) if r[2].startswith("operation-top:delegated:") and r[1] > stamp]  # DOC-2 (o664): each delegated record, once
    if given:
        out += ["", "Delegated approvals (DOC-2, since the last check-in):"] + ["- %s %s %s %s: %s" % (r[0], r[2].split(":")[2], r[2].split(":")[4], r[4], " ".join(json.loads(r[3]).split()[:14])) for r in given[-8:]]
    gone = mend.archived_since(folder, stamp)
    if gone:
        out += ["", "Archived (worker sessions freed):"] + ["- " + line for line in gone[-8:]]
    blocks = []
    for g in pod:
        held = {w["slug"]: why for w, why in graph.ready(g["queue"], {r["slug"]: r for r in g["runs"]}, graph.parallel_of(g["cfg"]), g["taken"], g["why"])[1]}
        item = lambda r, **kw: dict(slug=r["slug"], machine=r.get("machine") or graph.machine_name(), release=release_of(g["root"], r["slug"]),
                                    feature=feature_of(g["root"], r.get("goal"), r), **kw)
        items = [item(r, mark=g["states"][r["slug"]] if g["states"][r["slug"]] != "done" else "awaiting merge", depends=list(r.get("waits_on") or []),
                      owner=graph.foreign(r), left=bs.left_time(r, g["runs"], at), hard=auto.eta_left(auto.eta_seen(g["root"], r), at),
                      row="%s | %s | %s %d/8" % ("PR " + r["pr"].rsplit("/", 1)[-1] if r.get("pr") else "no PR yet", cell(lb.worker_of(r, g["taken"]), 30), lb.FLOW[lb.current(r)], lb.current(r) + 1),
                      bars=board_lines.progress(g["root"], r["slug"], r, lb.current(r), [])) for r in g["live"]]
        blocks.append((g["name"], items + [item(q, mark="queued", depends=q["depends"], left=bs.left_time(dict(q, status="queued"), g["runs"], at), why=held.get(q["slug"]), bars=board_lines.progress(g["root"], q["slug"], None, 0, q["done"])) for q in g["queue"]]))
    out += ["", "Dependencies"]
    spot = len(out)
    out += ["", "Needs you"]
    needs, readonly = [], []
    owned = lambda prefix, run: "- %s%s asks (owned by %s, read-only here)" % (prefix, run["slug"], graph.foreign(run))
    for run in live:
        state, ask = states[run["slug"]], run.get("waiting") or {}
        run.get("review_wait") and needs.append("%s: merge waiting on review; review.py record %s" % (run["slug"], run["slug"]))
        if line := bs.stalled_line(run, state, at, cfg, lb.worker_of(run, taken)):
            needs.append(line)
        elif graph.foreign(run):
            readonly += [owned("", run)] * (state == "waiting")
        elif state == "waiting":
            words = ask.get("words") or ["go on " + run["slug"]]
            rec = ask.get("recommend") or words[0]
            needs.append("%s asks: %s; options: %s; recommended: %s" % (run["slug"], lb.plain(ask.get("ask"), 160), quoted(words), rec))
        elif state == "silent":
            needs.append("%s: its worker has sent nothing for %dm; look at its session" % (
                run["slug"], graph.silent_for(run, at) // 60))
        elif state == "held":
            needs.append("%s is held with no worker; give it a session (sessions.py bind %s ID)" % (run["slug"], run["slug"]))
    needs += replan.preflight_lines([auto.eta_seen(root, r) for r in live]) + notify.timer_lines(folder, bd.cadence_of(os.path.dirname(folder), cfg.get("cadence")))
    stuck = board_lines.stuck(live, cfg.get("resume_on_limit") is True)
    needs += [" ".join(line.split()) for line in stuck if line.startswith("- ")]
    for hold in ready and (replan.plan_pause(cfg), replan.memory_hold(cfg)):
        hold and needs.append("%d ready goal(s) wait: %s" % (len(ready), hold))
    waited = replan.memory_waits(folder)
    if waited:
        needs.append("%d lane wait(s) for memory in the last hour; the last: %s" % (len(waited), waited[-1][21:140]))
    if ready and replan.active_limit(cfg) and sum(states[r["slug"]] != "merged" for r in live) >= replan.active_limit(cfg):
        needs.append("%d ready goal(s) wait: %d goals are live, at max_active_goals/parallel %d (ACTIVE_GOALS)" % (len(ready), len(live), replan.active_limit(cfg)))
    if found is not None:
        needs += [line[2:] for line in pl.ask_lines(found, cfg, len(ready)) if line.startswith("- ")]
        needs += ["archive session %s with the app (pool above pool_size)" % (item.get("name") or sid)
                  for sid, item in sorted(found.items()) if item.get("state") == "archive"]
    elif why:
        needs.append(graph.pool_fix(why))
    for sid, item in sorted((found or {}).items()):
        old = bs.read_json(os.path.join(folder, "runs", "%s.json" % item.get("slug"))) if item.get("state") == "busy" else None
        if isinstance(old, dict) and old.get("status") == "retired":
            needs.append("%s is retired but session %s is still busy; free it with pool.py return %s" % (
                old["slug"], item.get("name") or sid, old["slug"]))
    if os.path.exists(os.path.join(folder, "session-pool.bad.json")):
        needs.append("malformed session-pool entries were set aside in session-pool.bad.json; look and delete it")
    cfg_path = os.path.join(root, ".loop", "config.json")
    if os.path.exists(cfg_path) and bs.read_json(cfg_path) is None:
        needs.append(".loop/config.json can't be read, so every setting is at its default; fix the JSON (python3 -m json.tool)")
    _, fails, cause = govern_hook.health(os.path.dirname(folder))
    if fails:
        needs.append("the govern hook let %d call(s) through on an error (last: %s); fix it, then check govern-hook.log"
                     % (fails, lb.plain(cause, 80)))
    for g in pod[1:]:
        for run in g["live"]:
            ask = run.get("waiting") or {}
            if g["states"][run["slug"]] == "waiting":
                readonly.append(owned(g["name"] + "/", run)) if graph.foreign(run) else needs.append("%s/%s asks: %s; options: %s" % (
                    g["name"], run["slug"], lb.plain(ask.get("ask"), 160), quoted(ask.get("words") or ["go on"])))
    needs += ["%s: can't be read (%s); the other repos are shown" % item for item in broken]
    operation, asks = unattended.lines()
    needs += asks
    try:
        needs += [line for line in open(os.path.join(folder, "checkout-behind.txt")).read().splitlines()[:1] if line]
    except OSError:
        pass
    keys = lambda name, slug: slug if name == mine["name"] else "%s/%s" % (name, slug)
    edges = {keys(n, i["slug"]): [d if "/" in d else keys(n, d) for d in i["depends"]] for n, items in blocks for i in items}
    needs, tags = graph.rank(needs, edges, {keys(n, i["slug"]) for n, items in blocks for i in items if i["mark"] != "queued"})
    out[spot:spot] = grouped(blocks, at, {(n, i["slug"]): tags[keys(n, i["slug"])] for n, items in blocks for i in items if keys(n, i["slug"]) in tags}, folder)
    out += ["%d. %s" % (i, text) for i, text in enumerate(needs, 1)] or ["Nothing needs you"]
    out += readonly
    out += ["", "Coming up"] + ([operation] if operation else [])
    for run in live:
        if states[run["slug"]] == "done":
            out.append("- %s: its pull request waits for merge (you: review %s)" % (run["slug"], run.get("pr") or "it"))
        elif states[run["slug"]] in ("running", "silent", "held"):
            out.append("- %s: %s" % (run["slug"], lb.next_line(run)))
    try:
        owed = [line.split("	") + [""] * 4 for line in open(os.path.join(root, ".loop", "regression-owed.tsv")) if line.strip()]
    except OSError:
        owed = []
    out += ["- off-machine to-do: %s red proof owed on %s since %s %s" % (c[0], c[2], c[1], c[3].strip()) for c in owed]
    out += ["- " + line for line in bd.unread()]  # a stamp with no time zone or no time is named here, never guessed
    paused = board_lines.paused(live)
    out.append("- " + (paused or "next check-in in %s minutes" % (cfg.get("cadence") or 30)))
    return lb.fit(out, 100)


HEAD = re.compile(r"^[\s>#*_`-]*([A-Za-z ]+?)[\s:*_`]*(?:\(\d+\))?\s*$")
NEXT = ("needs you", "coming up")


def head(line):
    return (HEAD.match(line) or [None, ""])[1].strip().lower()


def body(text):
    lines, start = str(text or "").splitlines(), None
    for i, line in enumerate(lines):
        name = head(line)
        if start is None and name == "dependencies":
            start = i + 1
        elif start is not None and name in NEXT:
            return "\n".join(lines[start:i])
    return None if start is None else "\n".join(lines[start:])


def blocks(section):
    found, name = {"": []}, ""
    for line in section.splitlines():
        head = re.match(r"^\s*==\s*(.+?)\s*==\s*$", line)
        name = head.group(1) if head else name
        found.setdefault(name, []).append("" if head else line)
    return {key: re.sub(r"-\s*\n\s*", "-", "\n".join(rows)) for key, rows in found.items()}


def unranked(text):
    items, inside = [], False
    for line in str(text or "").splitlines():
        name = head(line)
        inside = name == "needs you" or (inside and name != "coming up")
        if inside and re.match(r"\s*\d+\.\s", line):
            items.append(line)
        elif inside and items and name != "needs you" and not line.lstrip().startswith("-"):
            items[-1] += " " + line.strip()
    held = [re.search(r"holds up[^\[\]]*?\((\d+) goals?\)|blocks nothing", item, re.I) for item in items]
    counts = [int(m.group(1) or 0) for m in held if m]
    if not all(held):
        return ["Needs you item %s does not say what it holds up, or 'blocks nothing' (MON-19)" % ", ".join(
            str(n) for n, m in enumerate(held, 1) if not m)]
    return [] if counts == sorted(counts, reverse=True) else ["Needs you is not sorted with the item holding up the most goals first (MON-19)"]


def missing(text, cwd=None):
    section = body(text)
    if section is None:
        return []
    parts = blocks(section)
    return ["%s/%s" % (repo, slug) for repo, slug in expected(cwd or None)
            if not re.search(r"(?<![\w-])%s(?![\w-])" % re.escape(slug), parts.get(repo if len(repo) <= 54 else repo[:51] + "...", parts.get("") if len(parts) == 1 else "") or "")]


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--since", default="")
    args = parser.parse_args()
    args.since and bs.timed(args.since, "--since %r")
    lines = render(stamp=args.since or None)
    print("\n".join(lines))
    try:  # an op-tokens.tsv row (proctree.op_append) and what the quiet hook compares with; never fail a check-in
        import proctree
        top = bs.git("rev-parse", "--show-toplevel")
        proctree.op_append(top)
        govern_hook.remember(proctree.common(top), "\n".join(lines))
    except Exception:
        pass
    return 0


if __name__ == "__main__":
    sys.exit(main())
