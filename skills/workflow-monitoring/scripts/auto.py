#!/usr/bin/env python3
"""Full auto (MON-11, o118): the operation session answers every waiting decision that names a recommended option, unless it is a safety class.

usage: auto.py pass [--dry-run] | since ISO | decide-text   (operate.py runs pass every round; the check-in lists since)

`full_auto` (on by default) is read at each decision. A worker's `sessions.py report --status waiting --ask Q --words W ... --recommend W
--kind K` records the question. It is answered, whatever its kind, once a standing record exists (sessions.py owner-words TEXT --ids
full-auto-rule: the owner's o118 words); it waits under Needs you, with why, when its kind is destructive, money, security or unknown, it
is an ETA choice, its goal is always-ask (a record covering always-ask:SLUG or *), it has no recommended answer, or the question or
answer is in a safety class (CLASSES) or names a risky_paths path. The answer goes through `operate.py send SLUG "WORDS (full auto,
owner rule oN)" --source auto`. Each decision is a line of <git common dir>/loop/auto.log: `time | slug | AUTO|WAITS | question | answer | reason`.
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
RULE = "full-auto-rule"  # the owner-words id of the standing record


def cls(stems):  # whole words with an ending (delete, deleted); "~" is a space
    return re.compile(r"\b(?:%s)(?:e|es|ed|ing|s|ion|ions|al|als)?\b" % "|".join(stems.split()).replace("~", " "), re.I)


CLASSES = {"destructive": cls("delet remov drop dropp rm wip truncat discard clos cancel purg unpublish reset clean~up forc overwrit overwritten renam rebas amend squash eras destroy uninstall kill unlink rmdir revert rewrit rewritten publish releas deploy deployment migrat schema reset~--hard git~clean"),
           "money": cls("pay payment purchas billing invoice money credits? card~on~file subscription buy bill paid price charg dollar usd cost~(?:money|\\$)"),
           "security": cls("secret credential password passphrase api[~_-]?key ssh[~_-]?key private~key signing~key (?:api|access|auth|bearer)~token permission allowlist allow~rule sandbox auth authenticat\\w* authoriz\\w* secur\\w* licens access~control (?:write|admin|root)~access grant rotat"),
           "private data": cls("private[~-]name private[~-]list private[~-]data private[~-]repos? dro" "pbox mail gmail e-?mail inbox smtp (?:customer|personal|private)~records?"),
           "steward merge": cls("steward merg\\w*(?:\\W+\\w+){0,3}\\W+(?:pull~request|PR|\\#\\d+)")}


def top():
    return bs.git("rev-parse", "--show-toplevel")


def loop_dir(root):
    common = subprocess.run(["git", "rev-parse", "--git-common-dir"], cwd=root, capture_output=True, text=True).stdout.strip()
    return os.path.join(os.path.abspath(os.path.join(root, common)), "loop")


def config(root):
    found = bs.read_json(os.path.join(root, ".loop", "config.json"))
    return found if isinstance(found, dict) else {}


def stamp():
    return datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def key_of(text):
    return " ".join(str(text or "").lower().split())


def standing(root):
    """The latest owner-words record covering full-auto-rule, else ''."""
    rows = [r[0] for r in owner_rows(root) if RULE in r[4].split(",")]
    return rows[-1] if rows else ""


def always(root, slug):
    return any({"always-ask:" + slug, "always-ask:*"} & set(r[4].split(",")) for r in owner_rows(root))


def why_not(waiting, cfg, ask_always=False):
    """'' when full auto may answer this decision, else why it waits."""
    if cfg.get("full_auto", True) is False:
        return "full_auto is off"
    kind, rec = waiting.get("kind") or "", waiting.get("recommend") or ""
    if kind and kind not in KINDS:
        return "unknown kind %s" % kind
    if kind in ("destructive", "money", "security"):
        return "a %s decision is the owner's" % kind
    if waiting.get("eta") or ask_always or re.search(r"\bETA\b", str(waiting.get("ask"))):
        return "an ETA choice or an always-ask goal is the owner's"
    if not rec or rec not in (waiting.get("words") or []):
        return "no recommended answer"
    said = " ".join([str(waiting.get("ask") or ""), rec])
    for name, found in CLASSES.items():
        if found.search(said):
            return "safety class %s: %s" % (name, found.search(said).group(0).lower())
    for pattern in cfg.get("risky_paths") or []:
        try:
            if re.search(pattern, said):
                return "risky path %s" % pattern
        except re.error:
            continue
    return ""


def log(folder, slug, verdict, waiting, answer, reason, at):
    line = " | ".join(str(x).replace("|", "/") for x in (at, slug, verdict, key_of(waiting.get("ask"))[:200], answer or "-", reason))
    os.makedirs(folder, exist_ok=True)
    with open(os.path.join(folder, "auto.log"), "a") as handle:
        handle.write(line.replace("\n", " ") + "\n")
    return line


def decide_all(root=None, now=None, dry=False):
    """One pass: each waiting goal's newest question decided once; the log lines written (dry: would write)."""
    root = root or top()
    folder, cfg, rule = loop_dir(root), config(root), standing(root or top())
    at, out, runs_dir = now or stamp(), [], os.path.join(folder, "runs")
    for name in sorted(os.listdir(runs_dir)) if os.path.isdir(runs_dir) else []:
        path = os.path.join(runs_dir, name)
        run = bs.read_json(path) if name.endswith(".json") else None
        if not isinstance(run, dict) or run.get("status") != "waiting" or not isinstance(run.get("waiting"), dict):
            continue
        waiting = run["waiting"]
        if graph.foreign(run) or (waiting.get("auto") and not (waiting["auto"].get("norule") and rule)):
            continue
        reason = why_not(waiting, cfg, always(root, run["slug"]))
        if reason == "full_auto is off":
            continue  # nothing is marked: turning it on later still answers
        norule = not reason and not rule
        reason = reason or ("no standing owner rule recorded: sessions.py owner-words TEXT --ids %s" % RULE if norule else "")
        if dry:
            out.append("WOULD %s %s: %s" % ("WAIT" if reason else "ANSWER", run["slug"], reason or waiting["recommend"]))
            continue
        say = lambda verdict, answer, why: out.append(log(folder, run["slug"], verdict, waiting, answer, why, at))
        if reason:
            say("WAITS", "", reason)
            waiting["auto"] = {"verdict": "waits", "why": reason, "at": at, "norule": norule}
        else:
            words = waiting["recommend"]
            sent = subprocess.run([sys.executable, os.path.join(HERE, "operate.py"), "send", run["slug"], "%s (full auto, owner rule %s)" % (words, rule), "--source", "auto"],
                                  cwd=root, capture_output=True, text=True)
            if sent.returncode:
                say("WAITS", "", "the answer could not be sent")
                continue
            say("AUTO", words, "%s, recommended, owner rule %s" % (waiting.get("kind") or "no kind", rule))
            waiting["auto"] = {"verdict": "answered", "words": words, "at": at}
        fresh = bs.read_json(path)
        if isinstance(fresh, dict) and fresh.get("status") == "waiting" and key_of((fresh.get("waiting") or {}).get("ask")) == key_of(waiting.get("ask")):
            fresh["waiting"]["auto"] = waiting["auto"]
            tmp = path + ".%d.tmp" % os.getpid()
            with open(tmp, "w") as handle:
                json.dump(fresh, handle, indent=2)
            os.replace(tmp, path)
    return out


def since(root, stamp, name="auto.log"):
    try:
        with open(os.path.join(loop_dir(root), name)) as handle:
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
    args.cmd == "since" and bs.timed(args.stamp)
    if args.cmd == "decide-text":
        reason = why_not({"ask": sys.stdin.read(), "kind": args.kind, "recommend": args.recommend,
                          "words": args.words or [args.recommend]}, config(top() or "."))
        print("WAITS: " + reason if reason else "AUTO")
        return 0
    lines = since(top(), args.stamp) if args.cmd == "since" else decide_all(dry=args.dry_run)
    print("\n".join(lines) if lines else "AUTO: nothing to decide")
    return 0


# Owner words (sessions.py owner-words TEXT --ids A,B): <git common dir>/loop/owner-words.tsv, id, UTC time, session, JSON text, IDs.


def owner_words_path(root="."):
    return os.path.join(loop_dir(root), "owner-words.tsv")


def owner_rows(root="."):
    """The owner-words records as [id, time, session, text, covers]."""
    try:
        with open(owner_words_path(root), encoding="utf-8") as handle:
            return [r for r in (line.rstrip("\n").split("\t") for line in handle) if len(r) == 5]
    except OSError:
        return []


def auto_rows(root):
    """(rule, FAIL, text): auto-record (an AUTO line without an existing standing record), auto-safety (an AUTO line in a safety class)."""
    out, rules = [], {r[0]: r[1] for r in owner_rows(root) if RULE in r[4].split(",")}
    first = min(rules.values(), default="")  # AUTO lines from before the rule existed are history
    for p in (map(str.strip, x.split(" | ")) for x in since(root, "")):
        p = list(p)
        if len(p) > 5 and p[2] == "AUTO" and p[0] >= first:
            found = re.search(r"owner rule (o\d+)", p[5])
            found and found.group(1) in rules or out.append(("auto-record", "FAIL", "%s has an auto answer with no standing owner rule record" % p[1]))
            hit = next((n for n, x in CLASSES.items() if x.search(p[3] + " " + p[4])), "")
            hit and out.append(("auto-safety", "FAIL", "%s was auto-answered in safety class %s" % (p[1], hit)))
    return out


# --- the hard ETA (GRD-14, o52): past it the goal waits under Needs you (ship now, extend once, defer); only `goal.py set` with an owner record moves it.

ETA_FLOOR = 30


def eta_margin(cfg):
    """The ETA margin factor: eta_margin_percent (0 to 300, else 25)."""
    value = (cfg or {}).get("eta_margin_percent", 25)
    return 1 + (value if isinstance(value, (int, float)) and not isinstance(value, bool) and 0 <= value <= 300 else 25) / 100


def eta_new(root, slug, done, touches, budget, cfg=None):
    """{minutes, estimate, basis}: the model's high end plus the margin (30 minutes at least), else the time budget."""
    names = glob.glob(os.path.join(loop_dir(root), "runs", "*.json"))
    runs = [r for r in map(bs.read_json, names) if isinstance(r, dict) and r.get("slug")]
    try:
        found = bs.estimate_full({"slug": slug, "status": "queued", "done": done, "touches": touches}, runs,
                                 datetime.datetime.now(datetime.timezone.utc), root)
    except Exception:
        found = None
    if not found or not found[2]:
        return {"minutes": budget or 240, "estimate": 0, "basis": "no estimate yet, so the time budget"}
    high, margin = int(found[2] // 60), eta_margin(cfg)
    return {"minutes": max(ETA_FLOOR, -(-int(high * margin) // 5) * 5), "estimate": high,
            "basis": "estimate %dm plus a %d%% margin%s" % (high, round((margin - 1) * 100), ", rough" if found[3] else "")}


def eta_seen(root, run):
    """The run record with the sidecar settings (eta_extend, eta_choice) over it."""
    extra = bs.read_json(os.path.join(loop_dir(root), "runs", "%s.extra.json" % run["slug"])) or {}
    return dict(run, **(extra.get("set") if isinstance(extra.get("set"), dict) else {}))


def eta_minutes(seen):
    eta = seen.get("eta") if isinstance(seen.get("eta"), dict) else {}
    more = [e.get("by") for e in seen.get("eta_extend") or [] if isinstance(e, dict)]
    return (eta["minutes"] if isinstance(eta.get("minutes"), int) else 0) + sum(n for n in more if isinstance(n, int))


def eta_open(seen):
    """Pre-flight items (#4535) still unanswered."""
    done = (seen.get("preflight_answers") or {}).get("answers") or {}
    return [i for i in (seen.get("preflight") or {}).get("items") or [] if i.get("id") not in done]


def eta_start(seen):
    return (seen.get("preflight_answers") or {}).get("spent") or 0  # active minutes when the last pre-flight item was answered


def eta_left(seen, at):
    """Seconds of hard ETA left; None with no ETA or an open pre-flight."""
    held = eta_minutes(seen)
    return None if not held or eta_open(seen) else max(0, held - bs.active_minutes(seen, at) + eta_start(seen)) * 60


def eta_over(seen, spent):
    """The goal has spent its ETA and the owner has not chosen ship now."""
    held = eta_minutes(seen)
    return bool(held) and not eta_open(seen) and spent - eta_start(seen) >= held and (seen.get("eta_choice") or {}).get("choice") != "ship"


def eta_text(seen, at):
    """The check-in's ETA cell: a clock time, passed, or none."""
    held, n = eta_minutes(seen), len(eta_open(seen))
    left = held - bs.active_minutes(seen, at) + eta_start(seen)
    return "no ETA" if not held else "ETA after your answers (%d open)" % n if n else "ETA passed" if left <= 0 else "ETA " + (at + datetime.timedelta(minutes=left)).astimezone().strftime("%H:%M")


def eta_wait(state, spent, save):
    """Put a goal past its ETA under Needs you (never auto-answered)."""
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
    found = [r for r in owner_rows() if r[0] == rid]
    if found and RULE in found[-1][4].split(",") and what != "an ETA change" and (what.startswith("the recommended") or what == "raising a budget" and any(" | %s | AUTO | " % slug in x and "budget" in x for x in since(top(), ""))):
        return rid  # the standing rule, for a goal full auto answered: reusable (never an ETA move)
    if not found or slug not in found[-1][4].split(","):
        g.no("owner-words record %s does not exist or does not cover %s. Fix: %s (ETA_NO_RECORD)" % (rid, slug, fix))
    for path in glob.glob(os.path.join(g.state_dir(), "*.extra.json")):
        if '"record": "%s"' % rid in open(path, encoding="utf-8").read():
            g.no("owner-words record %s was already used. Fix: %s (ETA_NO_RECORD)" % (rid, fix))
    return rid


def eta_set(g, args, state, why):
    """goal.py set --eta-extend N or --eta-choice ship|defer, with --owner-record."""
    slug, runs, rid = args.slug, g.state_dir(), eta_record(g, args.owner_record, args.slug, "an ETA change")
    note = {"record": rid, "at": stamp(), "why": why}
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
    """(rule, level, text): eta-missing (WARN), eta-extended (FAIL: no covering record), eta-overrun (FAIL: past its ETA, not waiting)."""
    at, out = at or datetime.datetime.now(datetime.timezone.utc), []
    covers, grace = {r[0]: r[4].split(",") for r in owner_rows(root)}, config(root).get("step_budget_minutes") or 30
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
        elif eta_over(seen, bs.active_minutes(seen, at) - grace) and not (run.get("waiting") or {}).get("eta"):
            out.append(("eta-overrun", "FAIL", "%s is past its ETA and not waiting under Needs you" % slug))
    return out


if __name__ == "__main__":
    sys.exit(main())
