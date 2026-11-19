#!/usr/bin/env python3
"""The three layers (MON-2, MON-5, MON-11): top (the owner's one session), machine (one operation session per machine), worker.

usage: layers.py status [--force]   a machine: send its STATUS to top when it changed or 30 minutes passed (prints the one line)
       layers.py board              top: build the one board from every machine's latest STATUS and publish it
       layers.py defaults           the seven enforced defaults, each `ok` or `FIX: ...` (never changes a setting)
       layers.py finding TITLE --feature PAGE --found REF [--text WORDS] [--owner-words oN] [--dry-run]
                                    OPS-24: file a finding of top or a machine session, without asking, as an ops-finding issue on
                                    "Backlog: PAGE" ("Other" if no page matches); REF is the TOP-DECISION or record that found it.
                                    Refuses a repeat of an open issue and a safety-class finding with no owner's words.

STATUS is one JSON message per machine in <git common dir>/loop/status/<machine>.json, also published as
refs/loop/status/<machine> when `machine_sync` is on. It carries: the machine, its time, main per repo, one line per worker (step,
status, PR number), the merges, the parked and idle sessions each with a reason, and needs-owner items with the exact words
and a recommendation. Top is the only role that publishes the board; a machine prints one line. Imported by operate.py.
"""
import hashlib
import json
import os
import re
import subprocess
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


def build(common, cfg, now=None):
    """This machine's STATUS as data, from its run records and session pool."""
    folder, workers, merges, parked, idle, needs = os.path.join(common, "loop"), [], [], [], [], []
    for name in sorted(os.listdir(os.path.join(folder, "runs"))) if os.path.isdir(os.path.join(folder, "runs")) else []:
        run = read(os.path.join(folder, "runs", name)) if name.endswith(".json") else {}
        if not run.get("slug") or graph.foreign(run) or run.get("external"):
            continue
        slug, status, pr = run["slug"], run.get("status"), number(run.get("pr"))
        if status in ("running", "waiting", "failed", "stopped", "done") and not (status == "done" and run.get("step") == "release"):
            workers.append({"slug": slug, "step": run.get("step"), "status": status, "pr": pr})
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
    root = os.path.dirname(common) if os.path.basename(common) == ".git" else os.getcwd()
    base = cfg.get("base") or "main"
    main = {os.path.basename(root): machines.sh("rev-parse", "--short", "origin/" + base, cwd=root) or "unknown"}
    return {"machine": machines.me(), "at": now if now is not None else time.time(), "main": main, "workers": workers,
            "merges": merges, "parked": parked, "idle": idle, "needs_owner": needs}


def fingerprint(status):
    return hashlib.sha1(json.dumps({k: v for k, v in status.items() if k != "at"}, sort_keys=True).encode()).hexdigest()


def send(common, cfg, force=False, now=None):
    """Send STATUS to top on change and every 30 minutes; returns (STATUS, 'sent'|'no change')."""
    now = now if now is not None else time.time()
    status, mark = build(common, cfg, now), os.path.join(common, "loop", "status-sent.json")
    mark_role(common)
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
    write_text = os.path.join(common, "loop", "top-board.txt")
    with open(write_text, "w", encoding="utf-8") as handle:
        handle.write(text + "\n")
    return text


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


def gh(args, root):
    try:
        return subprocess.run(["gh"] + args, cwd=root, capture_output=True, text=True, timeout=60)
    except (OSError, subprocess.SubprocessError) as error:
        return subprocess.CompletedProcess(args, 127, "", str(error))


def norm(title):
    return " ".join(re.sub(r"[^a-z0-9#-]+", " ", str(title).lower()).split())


def ids_of(title):
    return set(re.findall(r"#\d+|\b[A-Z]{2,5}-\d+\b", str(title)))


def repeat_of(title, open_issues):
    """The open issue a finding repeats: same normalised title, or same IDs in the title and half its words."""
    mine, ids = set(norm(title).split()), ids_of(title)
    for item in open_issues:
        theirs = set(norm(item["title"]).split())
        if norm(item["title"]) == norm(title) or (ids and ids == ids_of(item["title"]) and len(mine & theirs) * 2 >= len(mine | theirs)):
            return item["number"], item["title"]
    return None


def covered(root, record, title, page):
    """True when the owner-words record lists *, ops-findings, the page or an ID in the title."""
    import auto
    row = next((r for r in auto.owner_rows(root) if r[0] == record), None)
    return bool(row) and bool(({"*", "ops-findings", page} | ids_of(title)) & set(row[4].split(",")))


def file_finding(root, args):
    """(exit code, line): file one finding of the operation layer (OPS-24); nothing is filed when any check refuses."""
    import auto
    title, text, home = " ".join(args.title.split())[:90], " ".join(args.text.split()), os.path.expanduser("~")
    if not title or not args.found.strip():
        return 2, "REFUSED: give a title and --found (the TOP-DECISION or record that found it). Nothing was filed."
    if (len(home) > 1 and home in title + text) or re.search(r"[\w.+-]+@[\w-]+\.[\w.-]+", title + text):
        return 2, "REFUSED: the finding holds a private value. Nothing was filed."
    try:
        with open(os.path.join(root, ".loop", "docs.tsv"), encoding="utf-8") as handle:
            pages = [l.split("\t")[0].strip() for l in handle if l.strip() and l[0] != "#"]
    except OSError:
        pages = []
    page = next((p for p in pages if p.lower() == args.feature.strip().lower() and p != "Home"), "Other")
    for name, found in auto.CLASSES.items():
        if found.search(title + " " + text) and not (args.owner_words and covered(root, args.owner_words, title, page)):
            return 2, "REFUSED: safety class %s needs the owner's words (--owner-words oN listing %s or an ID in the title). Nothing was filed." % (name, page)
    done = gh(["issue", "list", "--state", "open", "--limit", "500", "--json", "number,title"], root)
    try:
        same = repeat_of(title, json.loads(done.stdout)) if not done.returncode else 0
    except ValueError:
        same = 0
    if same == 0:
        return 1, "REFUSED: could not read the open issues, so nothing was filed (%s)" % done.stderr.strip()[:100]
    if same:
        return 1, "REFUSED: repeats open issue #%d (%s). Nothing was filed." % same
    stone = "Backlog: " + page
    if args.dry_run:
        return 0, "WOULD file on %s: %s (found by %s; dry run)" % (stone, title, args.found)
    subprocess.run([sys.executable, os.path.join(HERE, "..", "..", "workflow-health", "scripts", "milestone.py"), "new", stone, "--live"],
                   cwd=root, capture_output=True, text=True, timeout=60)  # kept when it exists
    for label in ("backlog", "ops-finding"):
        gh(["label", "create", label, "--description", "Filed by the operation layer"], root)
    body = "<!-- loop-ops-finding %s -->\n\n%s\n\nFound by %s (operation layer).\n" % (hashlib.sha1(norm(title).encode()).hexdigest()[:12], text or title, args.found)
    done = gh(["issue", "create", "--title", title, "--label", "backlog,ops-finding", "--milestone", stone, "--body", body], root)
    if done.returncode:
        return 1, "FAILED: %s" % done.stderr.strip()[:160]
    number = re.search(r"/issues/(\d+)", done.stdout)
    line = "FILED #%s on %s: %s (found by %s)" % (number.group(1) if number else "?", stone, title, args.found)
    with open(os.path.join(auto.loop_dir(root), "findings.log"), "a", encoding="utf-8") as handle:
        handle.write("%s | %s\n" % (auto.stamp(), line))
    return 0, line


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
    elif argv[:1] == ["finding"]:
        import argparse
        parser = argparse.ArgumentParser(prog="layers.py finding")
        parser.add_argument("title")
        for name in ("feature", "found", "text", "owner-words"):
            parser.add_argument("--" + name, default="")
        parser.add_argument("--dry-run", action="store_true")
        code, line = file_finding(root, parser.parse_args(argv[1:]))
        print(line)
        return code
    else:
        print(__doc__.strip())
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
