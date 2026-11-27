#!/usr/bin/env python3
"""What the owner is shown about goals under DLF-1.3, and the functions moved here to make room. Imported by the
monitoring scripts; it has no command of its own. Standard library only."""
import argparse
import datetime
import glob
import importlib.util
import os
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import board_status as bs  # noqa: E402
os.environ.update(GIT_TERMINAL_PROMPT="0", GH_PROMPT_DISABLED="1", GIT_EDITOR="true", GIT_ASKPASS="true", SSH_ASKPASS="true")


def eta_new(root, slug, done, touches, budget, cfg=None):
    """{minutes, estimate, basis}: the model's high end plus the margin (30 minutes at least), else the time budget."""
    import auto  # here, not above: auto.py calls into this script
    names = glob.glob(os.path.join(auto.loop_dir(root), "runs", "*.json"))
    runs = [r for r in map(bs.read_json, names) if isinstance(r, dict) and r.get("slug")]
    try:
        found = bs.estimate_full({"slug": slug, "status": "queued", "done": done, "touches": touches}, runs,
                                 datetime.datetime.now(datetime.timezone.utc), root)
    except Exception:
        found = None
    if not found or not found[2]:
        return {"minutes": budget or 240, "estimate": 0, "basis": "no estimate yet, so the time budget"}
    high, margin = int(found[2] // 60), auto.eta_margin(cfg)
    return {"minutes": max(auto.ETA_FLOOR, -(-int(high * margin) // 5) * 5), "estimate": high,
            "basis": "estimate %dm plus a %d%% margin%s" % (high, round((margin - 1) * 100), ", rough" if found[3] else "")}


def start_events(runs):
    """DLF-1.3: the start review's one message, keyed by its code, until it is answered."""
    out = []
    for run in runs:
        review = run.get("start_review") or {}
        if review.get("mail") and not run.get("start_answer") and run.get("status") != "stopped":
            out.append(("start:%s:%s" % (run["slug"], review["code"]), "start review", run["slug"], review["mail"]))
    return out


def start_mail(notify, args):
    """Send one goal's start review, if its code was not sent yet, and say in one line what happened."""
    if not notify.enabled():
        print("NOT MAILED %s: mail is off on this machine (notify_email in the flow file)" % args.slug)
        return 0
    path = os.path.join(notify.lb.loop_dir(args.root), "notified.json")
    keys = [e[0] for e in notify.events(args.root, "") if e[1] == "start review" and e[2] == args.slug]

    def sent():
        return (notify.read_json(path).get("sent") or {}).get(keys[0]) if keys else None

    before = sent()
    notify.cmd_send(argparse.Namespace(root=args.root, checkin=os.devnull, slug=args.slug))
    now = sent()
    if before == "mailed":
        print("%s was already mailed with this code" % args.slug)
    elif now == "mailed":
        print("MAILED %s: the start review is sent" % args.slug)
    else:
        print("NOT MAILED %s: %s" % (args.slug, "it may have gone out, so it is not sent twice" if now == "mailing"
                                     else "see the NOTIFY line; the next check-in tries again"))
    return 0


def delivery(name):
    """One of delivery's scripts, loaded by path (skills don't import each other)."""
    spec = importlib.util.spec_from_file_location("one_review_" + name, os.path.join(
        os.path.dirname(os.path.abspath(__file__)), "..", "..", "workflow-delivery", "scripts", name + ".py"))
    found = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(found)
    return found


def decided(roots, owner=False):
    """The "Decided for you" lines of every followed repo. A decision stays until the owner was shown it (`owner`, the
    operation session's flag for that run) and its goal's release is cut or the goal is retired. Only printed ids are marked."""
    out = []
    for root in roots:
        try:
            common = subprocess.run(["git", "rev-parse", "--git-common-dir"], cwd=root, capture_output=True, text=True, check=True).stdout.strip()
            runs = os.path.join(os.path.abspath(os.path.join(root, common)), "loop", "runs")
            names = sorted(glob.glob(os.path.join(runs, "*.json")))
        except (OSError, subprocess.SubprocessError):
            out.append("- %s: its decisions can't be read" % root)
            continue
        for state in (bs.read_json(n) for n in names if os.path.basename(n).count(".") == 1):
            if not isinstance(state, dict) or not state.get("one_review"):
                continue
            try:
                reverts, ledger = delivery("reverts"), delivery("decisions")
                pairs = reverts.listing(root, runs, state)
                entries = ledger.entries(runs, state["slug"])
                shown = {i for e in entries if e["kind"] == "delivered" for i in e["ids"]}
                done = state.get("release") == "cut" or state.get("status") == "retired"
                printed = []
                for line, command in pairs:
                    number = int(line.split("#", 1)[1].split(":", 1)[0])
                    if not (done and number in shown):
                        out += ["- " + line, "  " + command]
                        printed.append(number)
                fresh = [n for n in printed if n not in shown]
                owner and fresh and ledger.add(runs, state["slug"], "delivered", ids=fresh)
            except (SystemExit, Exception) as stop:  # noqa: BLE001 - one bad goal must not hide the others
                out.append("- %s: its decisions can't be listed: %s" % (state.get("slug"), str(stop)[:160]))
    return ["", "Decided for you"] + out if out else []
