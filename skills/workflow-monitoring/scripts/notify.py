#!/usr/bin/env python3
"""Mail the owner once per new check-in event (MON-5), so nobody has to watch the operation session.

usage: notify.py send [--checkin FILE] [--root DIR]   what operate.py runs after each check-in it prints
       notify.py status [--root DIR]                  whether it is on here, mail.env is there, and how many events are seen

Off unless `notify_email` is true in this machine's flow file (`$LOOP_FLOW` or ~/.workflow-loop/flow.json); off, it
prints nothing and sends nothing. The events: each numbered item under Needs you in the check-in (default
<git common dir>/loop/checkin.txt, which operate.py writes), a goal stopped or failed, a goal past its hard ETA, and a
goal merged and released. One mail per event, naming the goal and what to do, through workflow-health's mail.py
(digest_mail picks the sender) with the variables in the schedule's mail.env (`$LOOP_MAIL_ENV`, else
`$LOOP_SCHEDULE_HOME`/mail.env, else ~/.workflow-loop/schedule/mail.env), outside the repo. The keys already sent are
kept in <git common dir>/loop/notified.json, so a repeat sends nothing; the first run there records every current event
and sends none. No printed line or kept file holds the address.
"""
import argparse
import datetime
import importlib
import json
import os
import re
import subprocess
import sys

# Match the subprocess prompt guard used throughout the delivery tools (DEL-10).
os.environ.update(GIT_TERMINAL_PROMPT="0", GH_PROMPT_DISABLED="1", GIT_EDITOR="true", GIT_ASKPASS="true", SSH_ASKPASS="true")

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import auto  # noqa: E402
import graph  # noqa: E402
import live_board as lb  # noqa: E402

HEALTH = os.path.join(HERE, "..", "..", "workflow-health", "scripts")
SECRETS = ("DIGEST_TO", "DIGEST_FROM", "CLOUDFLARE_ACCOUNT_ID", "CLOUDFLARE_EMAIL_TOKEN", "DIGEST_SMTP_USER", "DIGEST_SMTP_PASSWORD")
HEAD = re.compile(r"^[\s>#*_`-]*([A-Za-z ]+?)[\s:*_`]*(?:\(\d+\))?\s*$")


def mailer():
    """workflow-health's mail.py (it brings rounds.py), loaded only when there is something to send."""
    sys.path.insert(1, HEALTH)
    return importlib.import_module("mail")  # another skill's script: no static import, so the package scan sees none


def say(text):
    print("NOTIFY: " + (sys.modules["mail"].scrub(text) if "mail" in sys.modules else str(text)))


def read_json(path):
    try:
        with open(path) as handle:
            data = json.load(handle)
            return data if isinstance(data, dict) else {}
    except (OSError, ValueError):
        return {}


def flow_path():
    return os.path.expanduser(os.environ.get("LOOP_FLOW") or "~/.workflow-loop/flow.json")


def enabled():
    return read_json(flow_path()).get("notify_email") is True


def env_path():
    home = os.environ.get("LOOP_SCHEDULE_HOME") or os.path.expanduser("~/.workflow-loop/schedule")
    return os.environ.get("LOOP_MAIL_ENV") or os.path.join(home, "mail.env")  # rounds.mail_path


def load_env():
    """The mail.env variables, or the code that says why there are none."""
    path = env_path()
    if not os.path.exists(path):
        return None, "MAIL_NOT_SET_UP"
    if os.name != "nt" and os.stat(path).st_mode & 0o077:
        return None, "MAIL_ENV_MODE"
    found = {}
    with open(path) as handle:
        for row in handle:
            name, _, value = row.strip().partition("=")
            if name in SECRETS and value:
                found[name] = value
    return found, ""


def needs(text):
    """The numbered Needs you items of a check-in, wrapped lines joined."""
    items, inside = [], False
    for line in str(text or "").splitlines():
        name = (HEAD.match(line) or [None, ""])[1].strip().lower()
        if name == "coming up":
            break
        if name == "needs you":
            inside = True
            continue
        found = inside and re.match(r"\s*\d+\.\s+(.*)", line)
        if found:
            items.append(found.group(1).strip())
        elif inside and items and line.strip() and not line.lstrip().startswith("-"):
            items[-1] += " " + line.strip()
    return items


def slug_in(text, slugs):
    hits = [(text.find(s), s) for s in slugs if re.search(r"(?<![\w-])%s(?![\w-])" % re.escape(s), text)]
    lead = re.match(r"([a-z0-9][\w.-]*(?:/[\w.-]+)?)(?=:| asks\b| is\b)", text)
    return min(hits)[1] if hits else lead.group(1) if lead else "operation"


def events(root, text):
    """[(key, kind, slug, action)] for everything the owner should hear about now."""
    runs = [r for r in lb.load(root) if not graph.foreign(r)]
    slugs = sorted((r["slug"] for r in runs), key=len, reverse=True)
    out = []
    for item in needs(text):
        key = re.sub(r"\d+", "#", re.sub(r"\s*\[[^\[\]]*\]\s*$", "", item))
        out.append(("needs:" + key, "needs you", slug_in(item, slugs), item))
    for run in runs:
        slug, status = run["slug"], run.get("status")
        if status in ("stopped", "failed"):
            why = run.get("finding") or "it stopped at %s" % (run.get("step") or "a step")
            out.append(("stopped:%s:%s" % (slug, run.get("attempt") or 1), "stopped", slug,
                        "%s stopped: %s. You: resume it or retire it." % (slug, lb.plain(why, 160))))
        seen = auto.eta_seen(root, run)
        if status in ("running", "waiting") and auto.eta_left(seen, datetime.datetime.now(datetime.timezone.utc)) == 0:
            out.append(("eta:%s:%d" % (slug, auto.eta_minutes(seen)), "past ETA", slug,
                        "%s is past its ETA. You: pick ship now, extend once or defer." % slug))
        if status == "done" and run.get("release_version"):
            out.append(("released:%s:%s" % (slug, run["release_version"]), "released", slug,
                        "%s merged (%s) and released as v%s. Nothing to do." % (slug, run.get("pr") or "its pull request", run["release_version"])))
    told = {slug for _, kind, slug, _ in out if kind in ("stopped", "past ETA")}
    return [(key, "covered" if kind == "needs you" and slug in told else kind, slug, action) for key, kind, slug, action in out]


def save(path, state):
    temp = path + ".tmp"
    with open(temp, "w") as handle:
        json.dump(state, handle, indent=1, sort_keys=True)
    os.replace(temp, path)


def cmd_send(args):
    if not enabled():
        return 0
    folder = lb.loop_dir(args.root)
    text = ""
    try:
        with open(args.checkin or os.path.join(folder, "checkin.txt"), encoding="utf-8", errors="replace") as handle:
            text = handle.read()
    except OSError:
        pass
    found, path = events(args.root, text), os.path.join(folder, "notified.json")
    if not os.path.exists(path):
        save(path, {"sent": {key: "baseline" for key, _, _, _ in found}})
        say("baseline %d events, nothing sent; from now on each new one is mailed" % len(found))
        return 0
    state = read_json(path)
    sent = state.setdefault("sent", {})
    new = [e for e in found if e[0] not in sent]
    for key, kind, _, _ in [e for e in new if e[1] == "covered"]:  # its stopped or past-ETA mail says it
        sent[key] = "covered"
    new = [e for e in new if e[1] != "covered"]
    save(path, state)
    if not new:
        return 0
    secrets, why = load_env()
    if secrets is None:
        say("%d new event(s), not sent: no usable mail.env on this machine (%s)" % (len(new), why))
        return 0
    os.environ.update(secrets)
    mail = mailer()
    try:
        mode, host, port, wait, api = mail.settings(args.root)
        if mode == "off":
            raise mail.Stop("MAIL_OFF", "digest_mail is off in .loop/config.json")
        keys = mail.secrets(mode, False)
    except mail.Stop as stop:
        say("%d new event(s), not sent: %s (%s)" % (len(new), stop.text, stop.code))
        return 0
    repo = os.path.basename(os.path.abspath(args.root))
    for key, kind, slug, action in new:
        sent[key] = "mailing"
        save(path, state)
        body = "%s\n\nRepo: %s. Event: %s.\n" % (action, repo, kind)
        try:
            outcome, detail, _ = mail.deliver(mode, keys, "Loop: %s %s (%s)" % (kind, slug, repo), body, mail.rounds.to_html(body),
                                              (host, port, wait, api))
        except Exception as err:  # noqa: BLE001 - maybe mid-send: keep it marked, never send twice
            outcome, detail = "unknown", type(err).__name__
        if outcome == "refused":
            del sent[key]
            say("not sent %s %s: %s (MAIL_REFUSED)" % (kind, slug, detail))
        elif outcome == "unknown":
            say("%s %s may have been sent: %s; kept, so it is not sent twice (MAIL_UNKNOWN)" % (kind, slug, detail))
        else:
            sent[key] = "mailed"
            say("sent %s %s" % (kind, slug))
        save(path, state)
    return 0


def cmd_status(args):
    state = read_json(os.path.join(lb.loop_dir(args.root), "notified.json"))
    _, why = load_env()
    print("NOTIFY: %s on this machine; mail.env %s; %d event(s) seen" % (
        "on" if enabled() else "off", "ready" if not why else "missing (%s)" % why, len(state.get("sent") or {})))
    return 0


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = parser.add_subparsers(dest="command", required=True)
    for name, func in (("send", cmd_send), ("status", cmd_status)):
        item = sub.add_parser(name)
        item.add_argument("--root", default="")
        item.set_defaults(func=func)
        if name == "send":
            item.add_argument("--checkin", default="")
    args = parser.parse_args()
    if not args.root:
        top = subprocess.run(["git", "rev-parse", "--show-toplevel"], capture_output=True, text=True)
        args.root = top.stdout.strip() or os.getcwd()
    try:
        return args.func(args)
    except Exception as err:  # never a traceback: it could hold an address
        say("failed: %s: %s (NOTIFY_FAILED)" % (type(err).__name__, str(err)[:160]))
        return 1


if __name__ == "__main__":
    sys.exit(main())
