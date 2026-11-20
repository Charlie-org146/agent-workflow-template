#!/usr/bin/env python3
"""The three layers (MON-2, MON-5, MON-11): top (the owner's one session), machine (one operation session per machine), worker.

usage: layers.py status [--force]   a machine: send its STATUS to top when it changed or 30 minutes passed (prints the one line)
       layers.py board              top: build the one board from every machine's latest STATUS and publish it
       layers.py defaults           the seven enforced defaults, each `ok` or `FIX: ...` (never changes a setting)
       layers.py redteam input|record FILE|-|due [--eta ISO]   the red-team pass (HLT-2): the reviewer's input; record its three lists
                                    (A: assumptions, I: idle work, R: the one biggest risk) with routes; is a pass due

STATUS is one JSON message per machine in <git common dir>/loop/status/<machine>.json, also published as
refs/loop/status/<machine> when `machine_sync` is on. It carries: the machine, its time, main per repo, one line per worker (step,
status, PR number, ETA), the merges, the parked and idle sessions each with a reason, and needs-owner items with the exact
words and a recommendation. Each ETA it states goes in the ETA ledger (etas.jsonl). Top is the only role that publishes the board; a machine prints one line. Imported by operate.py.

Red-team (HLT-2): every hour and within an hour of a release ETA, a fresh-context reviewer is given `redteam input` (the board and
each machine's latest STATUS) and answers `A:`, `I:` and `R:` lines. `redteam record` stores them with a timestamp in
<git common dir>/loop/redteam/ (never a repo file) and prints one route per item: A to ops-findings, I and R to operation-top as a
proposed TOP-DECISION. It never edits, merges, files or sends. The ETA is --eta or loop/release-eta.json ({"at": epoch}).
"""
import calendar
import datetime
import hashlib
import json
import os
import re
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import graph  # noqa: E402
import machines  # noqa: E402

REF, STALE_SECONDS, TOP_GAP = "refs/loop/status/", 30 * 60, 300
ROLES = ("", "top", "machine")


def role(given=""):
    """'top', 'machine' or '' (today's loop): --role first, else $LOOP_OP_ROLE."""
    found = (given or os.environ.get("LOOP_OP_ROLE") or "").strip().lower()
    return found if found in ROLES else ""


def read(path):
    return machines.read_json(path)


def write(path, data):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    tmp = "%s.%d.tmp" % (path, os.getpid())
    with open(tmp, "w") as handle:
        json.dump(data, handle, sort_keys=True, indent=1)
    os.replace(tmp, path)


def number(url):
    found = re.search(r"(\d+)\s*$", str(url or ""))
    return int(found.group(1)) if found else 0


def root_of(common):
    return os.path.dirname(common) if os.path.basename(common) == ".git" else os.getcwd()


def eta_at(root, run, now):
    """The epoch a running or waiting goal's hard ETA names (to the 5 minutes), None when it has none left."""
    import auto
    at = datetime.datetime.fromtimestamp(now, datetime.timezone.utc)
    left = auto.eta_left(auto.eta_seen(root, run), at) if run.get("status") in ("running", "waiting") else None
    return round((now + left) / 300) * 300 if left else None


def eta_sweep(common, now=None):
    """The ETA ledger's round: record each goal's ETA, settle every layer's open ETAs (a done goal is the event)."""
    import auto
    root, loop, now, events, state = root_of(common), os.path.join(common, "loop"), now or time.time(), {}, {}
    for name in sorted(os.listdir(os.path.join(loop, "runs"))) if os.path.isdir(os.path.join(loop, "runs")) else []:
        run = read(os.path.join(loop, "runs", name)) if name.endswith(".json") else {}
        if not run.get("slug"):
            continue
        slug, names = run["slug"], eta_at(root, run, now)
        state[slug] = " (the goal is at %s, %s)" % (run.get("step"), run.get("status"))
        if run.get("status") == "done":
            events["goal", slug] = events["status", slug] = calendar.timegm(time.strptime(str(run["updated"])[:19], "%Y-%m-%dT%H:%M:%S")) if run.get("updated") else now
        if names:
            auto.bs.eta_say(loop, "goal", slug, (run.get("session") or {}).get("name") or "goal.py", (run.get("eta") or {}).get("basis") or "", names, now)
            auto.bs.eta_say(loop, "status", slug, "machine " + machines.me(), "STATUS to top", names, now)
    for e in auto.bs.eta_fold(loop).values():
        if e["layer"] == "board" and e["goals"] and all(("goal", g) in events for g in e["goals"]):
            events["board", e["key"]] = max(events["goal", g] for g in e["goals"])
    return auto.eta_settle(loop, events, now, lambda e: state.get(e["key"], ""))


def build(common, cfg, now=None):
    """This machine's STATUS as data, from its run records and session pool."""
    folder, workers, merges, parked, idle, needs = os.path.join(common, "loop"), [], [], [], [], []
    root, now = root_of(common), now if now is not None else time.time()
    for name in sorted(os.listdir(os.path.join(folder, "runs"))) if os.path.isdir(os.path.join(folder, "runs")) else []:
        run = read(os.path.join(folder, "runs", name)) if name.endswith(".json") else {}
        if not run.get("slug") or graph.foreign(run) or run.get("external"):
            continue
        slug, status, pr = run["slug"], run.get("status"), number(run.get("pr"))
        if status in ("running", "waiting", "failed", "stopped", "done") and not (status == "done" and run.get("step") == "release"):
            workers.append({"slug": slug, "step": run.get("step"), "status": status, "pr": pr, "eta": eta_at(root, run, now)})
        if status == "done" and run.get("step") == "release":
            merges.append({"slug": slug, "pr": pr})
        ask = run.get("waiting") or {}
        if status == "waiting" and ask.get("ask"):
            needs.append({"slug": slug, "words": ask.get("ask"), "recommend": ask.get("recommend") or "", "options": ask.get("words") or []})
        if status in ("failed", "stopped") or run.get("held"):
            parked.append({"slug": slug, "reason": "%s at %s" % (status if status in ("failed", "stopped") else "held", run.get("step") or "no step")})
    pool = graph.read_pool(os.path.join(folder, "session-pool.json"))[0] or {}
    for sid, item in sorted(pool.items()):
        if isinstance(item, dict) and item.get("state") == "free":
            idle.append({"session": item.get("name") or sid, "reason": "free in the pool, no ready goal"})
    base = cfg.get("base") or "main"
    main = {os.path.basename(root): machines.sh("rev-parse", "--short", "origin/" + base, cwd=root) or "unknown"}
    return {"machine": machines.me(), "at": now, "main": main, "workers": workers,
            "merges": merges, "parked": parked, "idle": idle, "needs_owner": needs}


def fingerprint(status):
    return hashlib.sha1(json.dumps({k: v for k, v in status.items() if k != "at"}, sort_keys=True).encode()).hexdigest()


def send(common, cfg, force=False, now=None):
    """Send STATUS to top on change and every 30 minutes; returns (STATUS, 'sent'|'no change')."""
    now = now if now is not None else time.time()
    status, mark = build(common, cfg, now), os.path.join(common, "loop", "status-sent.json")
    mark_role(common)
    eta_sweep(common, now)
    last = read(mark)
    if not force and last.get("sha") == fingerprint(status) and now - float(last.get("at") or 0) < STALE_SECONDS:
        return status, "no change"
    write(os.path.join(common, "loop", "status", status["machine"] + ".json"), status)
    write(mark, {"sha": fingerprint(status), "at": now})
    if machines.shared():
        machines.write_ref(REF + status["machine"], status, machines.read_ref(REF + status["machine"])[1])
    return status, "sent"


LINE = re.compile(r"^\W*\d{1,2}:\d{2}\b.*\b(STATUS sent|no change)\b", re.I)


def mark_role(common, sid=""):
    """Record that this operation session runs as a machine, for reply_hook.py's machine mode."""
    sid = sid or os.environ.get("CLAUDE_SESSION_ID", "")
    if re.match(r"^[A-Za-z0-9_-]{1,128}$", sid):
        write(os.path.join(common, "loop", "reply-hook", sid + ".role"), {"role": "machine"})


def machine_reply(text, common, now=None):
    """MON-5 machine mode: what a machine session's check-in is missing. It is one line, the time then 'STATUS sent' or
    'no change', and it is only right once STATUS went to top within 30 minutes."""
    lines = [l for l in str(text or "").splitlines() if l.strip()]
    if len(lines) != 1 or not LINE.match(lines[0]):
        return ["a machine check-in is one line: the time, then 'STATUS sent' or 'no change'"]
    path = os.path.join(common, "loop", "status", machines.me() + ".json")
    try:
        sent = (now if now is not None else time.time()) - os.path.getmtime(path) <= STALE_SECONDS + 300
    except OSError:
        sent = False
    return [] if sent else ["STATUS has not gone to top in the last 30 minutes; run layers.py status first"]


def one_line(status, said, now=None):
    now = now if now is not None else time.time()
    return "%s %s: STATUS %s, %d worker%s" % (time.strftime("%H:%M", time.localtime(now)), status["machine"],
                                            "sent" if said == "sent" else "no change", len(status["workers"]),
                                            "" if len(status["workers"]) == 1 else "s")


def collect(common):
    """Every machine's latest STATUS: the local status folder, then each published ref (the newer wins)."""
    found, folder = {}, os.path.join(common, "loop", "status")
    for name in sorted(os.listdir(folder)) if os.path.isdir(folder) else []:
        item = read(os.path.join(folder, name)) if name.endswith(".json") else {}
        if item.get("machine"):
            found[item["machine"]] = item
    if machines.shared():
        for ref in (machines.sh("ls-remote", "origin", REF + "*") or "").splitlines():
            peer = machines.read_ref(ref.split()[-1])[0]
            if peer and peer.get("machine") and float(peer.get("at") or 0) >= float((found.get(peer["machine"]) or {}).get("at") or 0):
                found[peer["machine"]] = peer
    return [found[k] for k in sorted(found)]


def board(statuses, now=None):
    """Top's board order: Needs you, stale STATUS call-outs, Running, PRs, Merges, Parked and idle, Main. One board for all machines."""
    now, out = now if now is not None else time.time(), []
    ages = {s["machine"]: int((now - float(s.get("at") or 0)) // 60) for s in statuses}
    needs = [(s["machine"], n) for s in statuses for n in s.get("needs_owner", [])]
    out.append("Needs you" + (" (%d)" % len(needs) if needs else ""))
    out += ["  %d. [%s/%s] %s -> recommended: %s" % (i, m, n.get("slug"), n.get("words"), n.get("recommend") or "none") for i, (m, n) in enumerate(needs, 1)] or ["  Nothing needs you"]
    stale = [m for m, a in sorted(ages.items()) if a * 60 > STALE_SECONDS]
    out += ["STALE: %s STATUS is %d minutes old (over 30)" % (m, ages[m]) for m in stale]
    sections = (("Running", lambda s: ["%s/%s %s %s" % (s["machine"], w["slug"], w.get("step"), w.get("status")) for w in s.get("workers", []) if w.get("status") == "running"]),
                ("PRs", lambda s: ["%s/%s #%s" % (s["machine"], w["slug"], w["pr"]) for w in s.get("workers", []) if w.get("pr")]),
                ("Merges", lambda s: ["%s/%s #%s" % (s["machine"], m["slug"], m.get("pr")) for m in s.get("merges", [])]),
                ("Parked and idle", lambda s: ["%s/%s parked: %s" % (s["machine"], p["slug"], p["reason"]) for p in s.get("parked", [])]
                 + ["%s/%s idle: %s" % (s["machine"], i["session"], i["reason"]) for i in s.get("idle", [])]),
                ("Main", lambda s: ["%s %s %s" % (s["machine"], r, v) for r, v in sorted((s.get("main") or {}).items())]))
    for title, lines in sections:
        rows = [row for s in statuses for row in lines(s)]
        out.append(title + (" (%d)" % len(rows) if rows else ""))
        out += ["  " + row for row in rows] or ["  none"]
    return "\n".join(out)


def publish_board(common, cfg, now=None):
    """Top only: build, write and return the one board (its file is what Loop Board publishing reads)."""
    text = board(collect(common), now)
    said = due(common, now)
    text += (chr(10) + said) * said.startswith("RED-TEAM DUE")
    write_text = os.path.join(common, "loop", "top-board.txt")
    with open(write_text, "w", encoding="utf-8") as handle:
        handle.write(text + "\n")
    return text


RED, RED_GAP, RED_NEAR, RED_FRESH = "redteam", 3600, 3600, 1200
ROUTES = {"A": "ops-findings", "I": "TOP-DECISION (proposed)", "R": "TOP-DECISION (proposed)"}
ASK = ("Reply with lines only, no edits and no decisions: `A: <an unverified assumption>` (any number), `I: <work idle capacity could start now>`"
       " (any number), and exactly one `R: <the single biggest risk to the release time>`.")


def iso(now):
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(now))


def reviewer_input(common, now=None):
    """The red-team reviewer's input: the board, one line per machine's latest STATUS, and the request. It only reads."""
    now, found = now if now is not None else time.time(), collect(common)
    rows = ["STATUS %s (%d min old): %s" % (s["machine"], (now - float(s.get("at") or 0)) // 60, json.dumps(
        {k: v for k, v in s.items() if k not in ("machine", "at")}, sort_keys=True, separators=(",", ":"))) for s in found]
    return chr(10).join(["RED-TEAM INPUT " + iso(now), "", board(found, now), ""] + rows + ["", ASK])


def parse_reply(text):
    """{'A': [...], 'I': [...], 'R': [...]} from a reviewer's lines; refuses unless there is exactly one R line."""
    lists = {"A": [], "I": [], "R": []}
    for line in str(text or "").splitlines():
        found = re.match(r"^\W*([AIR])\s*[:.)]\s*(\S.*)$", line)
        if found:
            lists[found.group(1)].append(found.group(2).strip())
    if len(lists["R"]) != 1:
        sys.exit("REFUSED: the reply has %d R: lines, and a red-team pass names exactly one biggest risk. Fix: send one `R: <risk>` line; nothing was recorded." % len(lists["R"]))
    return lists


def record(common, text, now=None):
    """Store the three lists with a timestamp under <common>/loop/redteam/ and return one route line per item (nothing is sent or filed)."""
    now, lists = now if now is not None else time.time(), parse_reply(text)
    routes = [{"kind": k, "item": item, "to": ROUTES[k], "state": "proposed"} for k in "AIR" for item in lists[k]]
    write(os.path.join(common, "loop", RED, time.strftime("%Y%m%dT%H%M%SZ", time.gmtime(now)) + ".json"),
          {"at": now, "time": iso(now), "assumptions": lists["A"], "idle": lists["I"], "risk": lists["R"][0], "routes": routes})
    file = "python3 skills/workflow-monitoring/scripts/mailbox.py finding %s --feature <PAGE> --found redteam/" + time.strftime("%Y%m%dT%H%M%SZ", time.gmtime(now))
    return ["ROUTE ops-findings: " + file % json.dumps(r["item"][:100]) if r["kind"] == "A" else "ROUTE %s: %s: %s" % (r["to"], r["kind"], r["item"]) for r in routes]


def due(common, now=None, eta=None):
    """`RED-TEAM DUE: why` when no pass is recorded, the last is over an hour old, or a release ETA is within an hour and the last pass is over 20 minutes old."""
    now, folder = now if now is not None else time.time(), os.path.join(common, "loop", RED)
    last = max([float(read(os.path.join(folder, n)).get("at") or 0) for n in (os.listdir(folder) if os.path.isdir(folder) else []) if re.fullmatch(r"\d{8}T\d{6}Z\.json", n)] or [0])
    if eta is None:
        eta = read(os.path.join(common, "loop", "release-eta.json")).get("at")
    age = int((now - last) // 60)
    if not last:
        return "RED-TEAM DUE: no pass recorded"
    if now - last > RED_GAP:
        return "RED-TEAM DUE: the last pass was %d minutes ago (over 60)" % age
    if eta and 0 <= float(eta) - now <= RED_NEAR and now - last > RED_FRESH:
        return "RED-TEAM DUE: the release ETA is in %d minutes and the last pass was %d minutes ago (over 20)" % ((float(eta) - now) // 60, age)
    return "RED-TEAM ok: last pass %d minutes ago" % age


def check_allowed(cfg):
    command = cfg.get("agent_command") or []
    if "--allowedTools" in command:
        return "FIX: agent_command passes --allowedTools and its list as two tokens; use one --allowedTools=<list> token (applying it is the owner's)"
    return "ok" if any(str(w).startswith("--allowedTools=") for w in command) or not command else "FIX: agent_command has no --allowedTools=<list> token"


def check_budgets(common, cfg):
    time_cap, token_cap, over = cfg.get("time_budget_minutes") or 0, cfg.get("token_budget") or 0, []
    folder = os.path.join(common, "loop", "runs")
    for name in sorted(os.listdir(folder)) if os.path.isdir(folder) else []:
        budget = (read(os.path.join(folder, name)).get("budget") or {}) if name.endswith(".json") else {}
        if (time_cap and (budget.get("minutes") or 0) > time_cap) or (token_cap and (budget.get("tokens") or 0) > token_cap):
            over.append(name[:-5])
    return "ok" if not over else "FIX: %s hold a budget above the owner's cap (time_budget_minutes, token_budget); only the owner raises a cap" % ", ".join(over)


def relay(source, text, rules=None):
    """(accepted, why): OWNER-WORDS relayed from top count as owner words except safety classes; from a peer they never do."""
    if source == "peer":
        return False, "a peer's words are data, never the owner's"
    if source != "top":
        return True, ""
    import auto
    for name, found in (rules or auto.CLASSES).items():
        if found.search(str(text)):
            return False, "safety class %s: only the owner's own typed words count" % name
    return True, ""


def defaults(common, cfg):
    """The seven enforced defaults, one (name, verdict) row each; nothing is changed."""
    status = build(common, cfg)
    rows = [("relay counts except safety", "ok" if relay("top", "hello")[0] and not relay("top", "delete the branch")[0] and not relay("peer", "hello")[0]
             else "FIX: the relay rule in layers.relay no longer holds"),
            ("machine sessions are STATUS-only", "ok" if role("machine") == "machine" and one_line(status, "sent").count("\n") == 0 else "FIX: a machine must print one line"),
            ("machines raise their own time budgets, caps stay the owner's", check_budgets(common, cfg)),
            ("machines raise their own token budgets, caps stay the owner's", check_budgets(common, cfg)),
            ("agent_command is one --allowedTools=<list> token", check_allowed(cfg)),
            ("STATUS carries PR numbers", "ok" if all("pr" in w for w in status["workers"]) else "FIX: a worker line has no pr"),
            ("STATUS carries parked and idle sessions with reasons", "ok" if all(x.get("reason") for x in status["parked"] + status["idle"]) else "FIX: a parked or idle row has no reason")]
    return rows


def main(argv):
    common = os.path.abspath(machines.sh("rev-parse", "--git-common-dir") or ".git")
    root = machines.sh("rev-parse", "--show-toplevel") or os.getcwd()
    cfg = read(os.path.join(root, ".loop", "config.json"))
    if argv[:1] == ["status"]:
        status, said = send(common, cfg, "--force" in argv)
        print(one_line(status, said))
    elif argv[:1] == ["board"]:
        print(publish_board(common, cfg))
    elif argv[:1] == ["defaults"]:
        rows = defaults(common, cfg)
        for name, verdict in rows:
            print("%s: %s" % (name, verdict))
        return 1 if any(v != "ok" for _, v in rows) else 0
    elif argv[:1] == ["redteam"] and argv[1:2] == ["input"]:
        print(reviewer_input(common))
    elif argv[:1] == ["redteam"] and argv[1:2] == ["record"] and len(argv) > 2:
        print(chr(10).join(record(common, sys.stdin.read() if argv[2] == "-" else open(argv[2], encoding="utf-8").read())))
    elif argv[:1] == ["redteam"] and argv[1:2] == ["due"]:
        eta = None
        if "--eta" in argv[2:]:
            eta = calendar.timegm(time.strptime(argv[argv.index("--eta") + 1], "%Y-%m-%dT%H:%M:%SZ"))
        print(due(common, eta=eta))
    else:
        print(__doc__.strip())
        return 0 if argv[:1] in (["--help"], ["-h"]) else 2
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
