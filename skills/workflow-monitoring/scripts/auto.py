#!/usr/bin/env python3
"""Full auto (MON-11): the operation session answers a worker's routine decision with its recommended option.

usage: auto.py pass [--dry-run]  decide each waiting goal's new question once (operate.py runs it every pass)
       auto.py since ISO       the decisions logged after a time (the check-in lists those since the last one)
       auto.py decide-text     read a question on stdin, print AUTO or WAITS with why (for tests and by hand)

`full_auto` in .loop/config.json (on by default) is read at each decision. Only the operation session answers: a worker's
`sessions.py report --status waiting --ask Q --words W ... --recommend W --kind K` just records the question. A decision
is answered only when all of these hold, else it waits under Needs you with its reason (logged once per question):
- its kind is `routine` (destructive, money, security, owner, a missing or an unknown kind all wait);
- it names a recommended answer that is one of its words;
- no risky word (WORDS below: delete, publish, merge, token, secret ...; whole words, case ignored) appears in the
  question or the answer, nor a path matching `risky_paths`;
- the owner hasn't answered that goal before: an owner answer on the goal sends every later question to the owner
  (answers.jsonl, source owner), so full auto never answers over the owner's word.
An answer goes through `operate.py send SLUG WORDS --source auto`, as an owner answer does; the worker runs goal.py answer
as usual. Each decision is appended to <git common dir>/loop/auto.log as `time | slug | AUTO|WAITS | question | answer |
reason`; the run's waiting.auto marks it decided. The check-in lists each auto answer with the words that revert it.
"""
import argparse
import datetime
import glob
import json
import os
import re
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import board_status as bs  # noqa: E402
import graph  # noqa: E402
os.environ.update(GIT_TERMINAL_PROMPT="0", GH_PROMPT_DISABLED="1", GIT_EDITOR="true", GIT_ASKPASS="true", SSH_ASKPASS="true")  # no prompt ever blocks

KINDS = ("routine", "destructive", "money", "security", "owner")
END = r"(?:e|es|ed|ing|s|ion|ions|al|als)?"  # the endings a risky word may take: delete, deletes, deleted, deleting
WORDS = ["delet", "remov", "drop", "dropp", "rm", "wip", "truncat", "discard", "forc", "overwrit", "overwritten", "renam",
         "publish", "releas", "deploy", "deployment", "merg", "push", "pay", "payment", "purchas", "billing", "cost",
         "spend", "spent", "money", "permission", "access", "token", "secret", "credential", "password", "key", "licens",
         "migrat", "schema", "auth", "authenticat", "authoriz", "secur", "security", "rebas", "amend", "squash", "eras",
         "destroy", "uninstall", "kill", "unlink", "rmdir", "removal", "revert", "rewrit", "rewritten"]
RISKY = re.compile(r"\b(?:%s)%s\b|reset\s+--hard|git\s+clean" % ("|".join(WORDS), END), re.I)
# A PENDING line that asks for the owner's words (a reviewed change, a criteria_max raise) is never full auto's (#4287).
OWNER_WORDS = re.compile(r"owner[- ]words|criteria_max|\b(?:un|re)-?review|reviewed\s+(?:page|requirement|prd)|\b(?-i:[A-Z]{2,5})-\d+\b[^.?]{0,60}\b(?:sub-?bullet|wording)", re.I)


def top():
    return bs.git("rev-parse", "--show-toplevel")


def loop_dir(root):
    common = subprocess.run(["git", "rev-parse", "--git-common-dir"], cwd=root, capture_output=True, text=True).stdout.strip()
    return os.path.join(os.path.abspath(os.path.join(root, common)), "loop")


def config(root):
    found = bs.read_json(os.path.join(root, ".loop", "config.json"))
    return found if isinstance(found, dict) else {}


def key_of(text):
    return " ".join(str(text or "").lower().split())


def owner_answered(folder, slug):
    try:
        with open(os.path.join(folder, "answers.jsonl")) as handle:
            for line in handle:
                try:
                    item = json.loads(line)
                except ValueError:
                    continue
                if item.get("slug") == slug and item.get("source", "owner") == "owner":
                    return True
    except OSError:
        pass
    return False


def why_not(waiting, cfg, answered=False):
    """'' when full auto may answer this decision, else why it waits."""
    if cfg.get("full_auto", True) is False:
        return "full_auto is off"
    kind, rec = waiting.get("kind") or "", waiting.get("recommend") or ""
    if kind not in KINDS:
        return "no kind given" if not kind else "unknown kind %s" % kind
    if kind != "routine":
        return "a %s decision is the owner's" % kind
    if not rec or rec not in (waiting.get("words") or []):
        return "no recommended answer among its words"
    said = " ".join([str(waiting.get("ask") or ""), rec])
    if OWNER_WORDS.search(said):
        return "it asks for owner words"
    hit = RISKY.search(said)
    if hit:
        return "it mentions %s" % hit.group(0).lower()
    for pattern in cfg.get("risky_paths") or []:
        try:
            if re.search(pattern, said):
                return "it names a risky path (%s)" % pattern
        except re.error:
            continue
    if answered:
        return "the owner has answered this goal before"
    return ""


def log(folder, slug, verdict, waiting, answer, reason, at):
    line = " | ".join(str(x).replace("|", "/") for x in (at, slug, verdict, key_of(waiting.get("ask"))[:200], answer or "-", reason))
    os.makedirs(folder, exist_ok=True)
    with open(os.path.join(folder, "auto.log"), "a") as handle:
        handle.write(line.replace("\n", " ") + "\n")
    return line


def decide_all(root=None, now=None, dry=False):
    """One pass: each waiting goal's newest question decided once. Returns the log lines written (dry: would write)."""
    root = root or top()
    folder, cfg = loop_dir(root), config(root)
    at = now or datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    out = []
    runs_dir = os.path.join(folder, "runs")
    for name in sorted(os.listdir(runs_dir)) if os.path.isdir(runs_dir) else []:
        path = os.path.join(runs_dir, name)
        run = bs.read_json(path) if name.endswith(".json") else None
        if not isinstance(run, dict) or run.get("status") != "waiting" or not isinstance(run.get("waiting"), dict):
            continue
        waiting = run["waiting"]
        if waiting.get("auto") or graph.foreign(run):  # a pod never answers another pod's question
            continue
        reason = why_not(waiting, cfg, owner_answered(folder, run.get("slug")))
        if reason == "full_auto is off":
            continue  # re-read at the next decision; nothing is marked, so turning it on later still answers
        if dry:
            out.append("WOULD %s %s: %s" % ("WAIT" if reason else "ANSWER", run["slug"], reason or waiting["recommend"]))
            continue
        if reason:
            out.append(log(folder, run["slug"], "WAITS", waiting, "", reason, at))
            waiting["auto"] = {"verdict": "waits", "why": reason, "at": at}
        else:
            words = waiting["recommend"]
            sent = subprocess.run([sys.executable, os.path.join(HERE, "operate.py"), "send", run["slug"], words, "--source", "auto"],
                                  cwd=root, capture_output=True, text=True)
            if sent.returncode:
                out.append(log(folder, run["slug"], "WAITS", waiting, "", "the answer could not be sent", at))
                continue  # not marked: the next pass tries again
            out.append(log(folder, run["slug"], "AUTO", waiting, words, "routine, recommended", at))
            waiting["auto"] = {"verdict": "answered", "words": words, "at": at}
        fresh = bs.read_json(path)
        if isinstance(fresh, dict) and fresh.get("status") == "waiting" and key_of((fresh.get("waiting") or {}).get("ask")) == key_of(waiting.get("ask")):
            fresh["waiting"]["auto"] = waiting["auto"]
            tmp = path + ".%d.tmp" % os.getpid()
            with open(tmp, "w") as handle:
                json.dump(fresh, handle, indent=2)
            os.replace(tmp, path)
    return out


def since(root, stamp):
    try:
        with open(os.path.join(loop_dir(root), "auto.log")) as handle:
            return [line.rstrip("\n") for line in handle if line[:20] > stamp]
    except OSError:
        return []


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = parser.add_subparsers(dest="cmd", required=True)
    item = sub.add_parser("pass")
    item.add_argument("--dry-run", action="store_true", help="print what would be answered or sent to you, change nothing")
    item = sub.add_parser("since")
    item.add_argument("stamp")
    item = sub.add_parser("decide-text")
    item.add_argument("--kind", default="")
    item.add_argument("--recommend", default="")
    item.add_argument("--words", action="append", default=[])
    args = parser.parse_args()
    if getattr(args, "stamp", None) is not None and not re.match(r"^\d{4}(-\d\d(-\d\d(T\d\d(:\d\d(:\d\dZ?)?)?)?)?)?$", args.stamp):
        sys.exit("REFUSED: %r is not a time. Fix: give it as YYYY-MM-DDTHH:MM:SSZ." % args.stamp)
    if args.cmd == "decide-text":
        reason = why_not({"ask": sys.stdin.read(), "kind": args.kind, "recommend": args.recommend,
                          "words": args.words or [args.recommend]}, config(top() or "."))
        print("WAITS: " + reason if reason else "AUTO")
        return 0
    lines = since(top(), args.stamp) if args.cmd == "since" else decide_all(dry=args.dry_run)
    print("\n".join(lines) if lines else "AUTO: nothing to decide")
    return 0


# The owner's messages (sessions.py owner-words TEXT --ids A,B): one line each in <git common dir>/loop/owner-words.tsv:
# id (o1, ...), UTC time, the operation session's id, the text as JSON, the IDs or pages it covers. A worker is refused.


def owner_words_path():
    top = subprocess.run(["git", "rev-parse", "--git-common-dir"], capture_output=True, text=True).stdout.strip()
    return os.path.join(os.path.abspath(top), "loop", "owner-words.tsv")


def owner_words_add(text, ids):
    """Append the message and print OWNER-WORDS <id> <ids>; refuse a worker, an empty message or no ids."""
    if os.environ.get("LOOP_ROLE") == "worker":
        sys.exit("REFUSED: only the operation session records the owner's words; a worker never does. Nothing was written.")
    ids = [item.strip() for item in ids.split(",") if item.strip()]
    if not text.strip() or not ids:
        sys.exit("REFUSED: give the owner's exact message and --ids (requirement IDs or page names it covers). Nothing was written.")
    where = owner_words_path()
    os.makedirs(os.path.dirname(where), exist_ok=True)
    count = 0
    if os.path.exists(where):
        with open(where, encoding="utf-8") as handle:
            count = sum(1 for line in handle if line.strip())
    stamp = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    with open(where, "a", encoding="utf-8") as handle:
        handle.write("o%d\t%s\t%s\t%s\t%s\n" % (count + 1, stamp, os.environ.get("LOOP_OPERATION_SESSION") or "operation",
                                              json.dumps(text, ensure_ascii=False), ",".join(ids)))
    print("OWNER-WORDS o%d covers %s" % (count + 1, ",".join(ids)))
    return 0


# --- the hard ETA (GRD-13, o52): active minutes a goal may run, recorded at freeze. Past it nothing starts and the goal
# waits under Needs you: ship now, extend once, or defer; only `goal.py set --eta-extend|--eta-choice` with an owner record moves it.

ETA_MARGIN, ETA_FLOOR = 1.25, 30


def eta_new(root, slug, done, touches, budget):
    """{minutes, estimate, basis}: the model's high end for a goal of this size plus 25%, up to 5 minutes (30 at least);
    the time budget when it has no estimate."""
    names = glob.glob(os.path.join(loop_dir(root), "runs", "*.json"))
    runs = [r for r in map(bs.read_json, names) if isinstance(r, dict) and r.get("slug")]
    try:
        found = bs.estimate_full({"slug": slug, "status": "queued", "done": done, "touches": touches}, runs,
                                 datetime.datetime.now(datetime.timezone.utc), root)
    except Exception:
        found = None
    if not found or not found[2]:
        return {"minutes": budget or 240, "estimate": 0, "basis": "no estimate yet, so the time budget"}
    high = int(found[2] // 60)
    return {"minutes": max(ETA_FLOOR, -(-int(high * ETA_MARGIN) // 5) * 5), "estimate": high,
            "basis": "estimate %dm plus a 25%% margin%s" % (high, ", rough" if found[3] else "")}


def eta_seen(root, run):
    """The run record with the sidecar settings (eta_extend, eta_choice) over it."""
    extra = bs.read_json(os.path.join(loop_dir(root), "runs", "%s.extra.json" % run["slug"])) or {}
    return dict(run, **(extra.get("set") if isinstance(extra.get("set"), dict) else {}))


def eta_minutes(seen):
    eta = seen.get("eta") if isinstance(seen.get("eta"), dict) else {}
    more = [e.get("by") for e in seen.get("eta_extend") or [] if isinstance(e, dict)]
    return eta["minutes"] + sum(n for n in more if isinstance(n, int)) if isinstance(eta.get("minutes"), int) else 0


def eta_spent(run, at=None):
    return int(sum(bs.flow_seconds(run, at or datetime.datetime.now(datetime.timezone.utc)).values()) // 60)


def eta_over(seen, spent):
    """The goal has spent its ETA and the owner has not chosen ship now."""
    held = eta_minutes(seen)
    return bool(held) and spent >= held and (seen.get("eta_choice") or {}).get("choice") != "ship"


def eta_text(seen, at):
    """The check-in's ETA cell: a clock time, passed, or none."""
    held = eta_minutes(seen)
    left = held - eta_spent(seen, at)
    return "no ETA" if not held else "ETA passed" if left <= 0 else "ETA " + (at + datetime.timedelta(minutes=left)).astimezone().strftime("%H:%M")


def eta_wait(state, spent, save):
    """Put a goal past its ETA under Needs you (kind owner: never auto-answered)."""
    slug = state["slug"]
    if (state.get("waiting") or {}).get("eta"):
        return
    words = [w % slug for w in ("ship %s now", "extend %s by N minutes", "defer %s")]
    state["status"] = "waiting"
    state["waiting"] = {"ask": "%s is past its ETA (%dm of %dm): ship now, extend once by an amount "
                               "in your words, or move it to the next release" % (slug, spent, eta_minutes(state)),
                        "words": words, "recommend": words[0], "kind": "owner", "eta": True}
    save(state, "past its ETA: waiting for the owner's choice")


def eta_record(g, rid, slug, what):
    """The record's id, or refuse: none, not covering the goal, or used before."""
    fix = "the operation session runs sessions.py owner-words TEXT --ids %s, then repeats this with --owner-record ID" % slug
    if not rid:
        g.no("%s needs the owner's words. Fix: %s (ETA_NO_RECORD)" % (what, fix))
    try:
        with open(owner_words_path(), encoding="utf-8") as handle:
            rows = [line.rstrip("\n").split("\t") for line in handle]
    except OSError:
        rows = []
    found = [r for r in rows if len(r) == 5 and r[0] == rid]
    if not found or slug not in found[-1][4].split(","):
        g.no("owner-words record %s does not exist or does not cover %s. Fix: %s (ETA_NO_RECORD)" % (rid, slug, fix))
    for path in glob.glob(os.path.join(g.state_dir(), "*.extra.json")):
        if '"record": "%s"' % rid in open(path, encoding="utf-8").read():
            g.no("owner-words record %s was already used. Fix: %s (ETA_NO_RECORD)" % (rid, fix))
    return rid


def eta_set(g, args, state, why):
    """goal.py set --eta-extend N or --eta-choice ship|defer, with --owner-record."""
    slug, runs, rid = args.slug, g.state_dir(), eta_record(g, args.owner_record, args.slug, "an ETA change")
    stamp = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    note = {"record": rid, "at": stamp, "why": why}
    if args.eta_extend:
        if args.eta_extend < 1:
            g.no("--eta-extend wants a whole number of minutes above 0.")
        more = (g.fit.view(state, runs).get("eta_extend") or []) + [dict(note, by=args.eta_extend)]
        g.guards.add_set(runs, slug, "eta_extend", more, "set eta +%dm (record %s): %s" % (args.eta_extend, rid, why))
    else:
        g.guards.add_set(runs, slug, "eta_choice", dict(note, choice=args.eta_choice), "set eta choice %s (record %s): %s" % (args.eta_choice, rid, why))
    if args.eta_choice == "ship":
        for step in g.fit.STEPS:
            if not g.fit.recorded(state, step):
                state.setdefault("flow", {})[step] = "skipped: past its ETA, the owner chose ship now (record %s)" % rid
    if args.eta_choice == "defer":
        state["status"], state["retired"] = "retired", {"reason": "past its ETA, the owner moved it to the next release (record %s)" % rid}
    elif (state.get("waiting") or {}).get("eta"):
        state["status"], state["waiting"] = "running", None
    g.save(state, "eta %s (record %s): %s" % (args.eta_choice or "extended by %dm" % args.eta_extend, rid, why))


def eta_rows(root, at=None):
    """(rule, level, text): eta-missing (WARN), eta-extended (FAIL: no covering record), eta-overrun (FAIL: a step past
    its ETA and not waiting for the owner). Read-only."""
    at, out, covers = at or datetime.datetime.now(datetime.timezone.utc), [], {}
    try:
        with open(os.path.join(loop_dir(root), "owner-words.tsv"), encoding="utf-8") as handle:
            covers = {r[0]: r[4].split(",") for r in (line.rstrip("\n").split("\t") for line in handle) if len(r) == 5}
    except OSError:
        pass
    grace = (config(root).get("step_budget_minutes") or 30)
    for path in sorted(glob.glob(os.path.join(loop_dir(root), "runs", "*.json"))):
        run = bs.read_json(path)
        if not isinstance(run, dict) or not run.get("slug"):
            continue
        seen, slug = eta_seen(root, run), run["slug"]
        for e in seen.get("eta_extend") or []:
            if not isinstance(e, dict) or slug not in covers.get(e.get("record"), []):
                out.append(("eta-extended", "FAIL", "%s has an ETA extended with no covering owner-words record" % slug))
                break
        if run.get("status") not in ("running", "waiting", "failed", "stopped"):
            continue
        if not eta_minutes(seen):
            out.append(("eta-missing", "WARN", "%s has no ETA" % slug))
        elif eta_over(seen, eta_spent(seen, at) - grace) and not (run.get("waiting") or {}).get("eta"):
            out.append(("eta-overrun", "FAIL", "%s is past its ETA and not waiting under Needs you" % slug))
    return out


if __name__ == "__main__":
    sys.exit(main())
