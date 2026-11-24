#!/usr/bin/env python3
"""Deliver first (DLF-1): stop table, filing and ledger, budget rule, release cut, setting. Every outside write goes through write()."""
import hashlib
import json
import os
import re
import sys
import urllib.parse

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import private  # noqa: E402

LABEL, ISSUE = "deliver-first", "repos/{owner}/{repo}/issues"
KEY = re.compile(r"<!-- dlf key=(\S+) id=(\S+) -->")
EVENT = re.compile(r"<!-- dlf-event key=(\S+) state=(\w+) -->")


def mem(runs, slug):
    try:
        got = json.load(open(os.path.join(runs, slug + ".dlf.json")))
    except (OSError, ValueError):
        got = {}
    return {"lines": {}, "queue": [], "local": [], **(got if isinstance(got, dict) else {})}


def keep(runs, slug, held):
    path = os.path.join(runs, slug + ".dlf.json")
    json.dump(held, open(path + ".tmp", "w"), indent=1)
    os.replace(path + ".tmp", path)


def write(top, runs, slug, kind, text, do):
    """The one door out: scan first; a failed scan keeps the text local."""
    got = private.scan(top, None, texts={kind: text})
    if got["state"] not in ("clean", "off"):
        held = mem(runs, slug)
        held["local"].append({"kind": kind, "text": text, "why": got["state"]})
        keep(runs, slug, held)
        return False, "kept local: the private-name scan said %s" % got["state"]
    return do(text)


def pages(top, path):
    """Every page, or None when a read fails."""
    code, out = private.gh(top, "api", "--paginate", "--slurp", path)
    try:
        got = None if code else json.loads(out)
    except ValueError:
        got = None
    return [x for p in got for x in (p if isinstance(p, list) else [p])] if isinstance(got, list) else None


def find_issue(top, rel):
    rows = pages(top, "%s?state=all&per_page=100&labels=%s" % (ISSUE, urllib.parse.quote("%s:%s" % (LABEL, rel))))
    return None if rows is None else min([r["number"] for r in rows if "pull_request" not in r], default=0)


def comments(top, number):
    rows = pages(top, "%s/%d/comments?per_page=100" % (ISSUE, number))
    return None if rows is None else sorted(rows, key=lambda r: r["id"])


def post(top, path, field, text, *more):
    code, out = private.gh(top, "api", "-X", "POST", path, "-f", "%s=%s" % (field, text), *more)
    return not code, out


def ensure_issue(top, runs, slug, rel):
    number = find_issue(top, rel)
    if number != 0:
        return number
    body = "Lines goals of release %s filed instead of waiting. One comment a line. Accept: accept-all <id> <id> ...\n<!-- dlf-issue -->" % rel
    ok, out = write(top, runs, slug, "issue", body, lambda t: post(top, ISSUE, "title", "Deliver-first lines: %s" % rel, "-f", "body=" + t,
                                                                  "-f", "labels[]=%s:%s" % (LABEL, rel)))
    if not ok:
        return None
    mine, lowest = json.loads(out)["number"], find_issue(top, rel)
    if lowest is None:
        return None
    if lowest and lowest != mine:
        private.gh(top, "api", "-X", "PATCH", "%s/%d" % (ISSUE, mine), "-f", "state=closed")
        return lowest
    return mine


def later(runs, slug, item):
    held = mem(runs, slug)
    held["queue"] = [q for q in held["queue"] if q != item] + [item]
    keep(runs, slug, held)
    return "", "queued"


def filed(runs, slug, held, key, lid, item):
    held["lines"][key] = lid
    held["queue"] = [q for q in held["queue"] if q != item]
    held["local"] = [x for x in held["local"] if "key=%s " % key not in x["text"]]
    keep(runs, slug, held)
    return lid, ""


def file_line(top, runs, slug, rel, stop, subject, occ, what, words, rec):
    key = "|".join((slug, stop, subject, re.sub(r"[^A-Za-z0-9_.:-]", "-", str(occ))[:40]))
    what, words, rec = (" ".join(str(x).split()) for x in (what, words, rec))
    held = mem(runs, slug)
    item = dict(rel=rel, stop=stop, subject=subject, occ=occ, what=what, words=words, rec=rec)
    if key in held["lines"]:
        return filed(runs, slug, held, key, held["lines"][key], item)
    n0, number = len(held["local"]), ensure_issue(top, runs, slug, rel)
    rows = comments(top, number) if number else None
    if rows is None:
        if not number and len(mem(runs, slug)["local"]) > n0:
            return "", "local"
        return later(runs, slug, item)
    for row in rows:
        mark = KEY.search(row["body"])
        if mark and mark[1] == key:
            return filed(runs, slug, held, key, mark[2], item)
    lid = "%s-%s-%d" % (slug, stop, 1 + sum(1 for k in held["lines"] if k.startswith("%s|%s|" % (slug, stop))))
    text = '[ ] %s %s | %s | %s - %s; settle with: "%s"; recommend: %s\n<!-- dlf key=%s id=%s -->' % (
        lid, slug, stop, subject, what, words, rec, key, lid)
    ok, out = write(top, runs, slug, "line", text, lambda t: post(top, "%s/%d/comments" % (ISSUE, number), "body", t))
    if not ok and out.startswith("kept local"):
        return "", "local"
    if not ok and not any((KEY.search(r["body"]) or [0, 0])[1] == key for r in comments(top, number) or []):
        return later(runs, slug, item)
    return filed(runs, slug, held, key, lid, item)


def retry(top, runs, slug):
    todo = mem(runs, slug)["queue"]
    return [file_line(top, runs, slug, q["rel"], q["stop"], q["subject"], q["occ"], q["what"], q["words"], q["rec"]) for q in todo]


def post_event(top, runs, slug, rel, key, state, text):
    def do(t):
        number = find_issue(top, rel)
        return post(top, "%s/%d/comments" % (ISSUE, number), "body", t) if number else (False, "no release issue")
    return write(top, runs, slug, "event", "%s\n<!-- dlf-event key=%s state=%s -->" % (text, key, state), do)[0]


def cap_line(top, runs, slug, rel, spend, estimate, old, new):
    what = "reached its 2x cap at %d of %d (budget %d, now %d)" % (spend, estimate, old, new)
    return file_line(top, runs, slug, rel, "cap", "other", "cap", what, "accept to continue or decline to queue a patch goal", "keep working at the cap")


def convert(top, runs, slug, rel, key, lid, what, words):
    patch, path = "patch-" + hashlib.sha1(key.encode()).hexdigest()[:8], os.path.join(top, ".loop", "queue.md")
    text = "- slug: %s | level: quick | touches: .loop/findings.md | goal: Settle deliver-first line %s: %s | done: %s is settled: %s\n" % (
        patch, lid, what, lid, words)

    def add(t):
        if "slug: %s |" % patch not in (open(path).read() if os.path.exists(path) else ""):
            open(path, "a").write(t)
        return True, patch
    return write(top, runs, slug, "patch", text, add)[0]


# stop table (DLF-1.1, DLF-1.3)
SAFETY = ("deleting what cannot be restored", "money", "security and sandbox settings", "private data", "steward merges",
          "a change to what a feature promises", "a test loosened or deleted")
STOPS = ("break", "plan", "cap", "budget", "test", "choice")
WORDS = dict(zip(SAFETY, (r"force[- ]push|rm -rf|drop (table|database)|delete (the |a )?(repo|branch|backup|release|history)|hard reset",
                          r"\b(payment|refund|invoice|billing|purchase)s?\b|\$\d",
                          r"\bsandbox|permission mode|bypass ?permissions|settings\.json|allowlist|credential|api[_ -]?key|secret|password",
                          r"private[- ]name|private data|\bleak|personal data|\bpii\b", r"steward|auto[- ]?merge|merge queue",
                          r"what (the |a )?feature promises|\bpromises?\b|requirement text|done line",
                          r"loosen|weaken|\bxfail\b|skip(s|ped)? (a |the )?test|delete[sd]? (a |the )?test")))
PATHS = {SAFETY[2]: r"(^|/)(\.claude/|permissions\.tsv|\.github/workflows/|settings[^/]*\.json$)", SAFETY[5]: r"^docs/wiki/[^/]*\.md$"}
TESTS = r"(^|/)(tests?/|dev/toy/test-)|\.loop/regression\.tsv|\.test\.|_test\."
SECRET = r"AKIA[0-9A-Z]{16}|gh[pousr]_[A-Za-z0-9]{30,}|sk-[A-Za-z0-9]{20,}|-----BEGIN [A-Z ]*PRIVATE KEY-----"
SKIP = r"\b(skip|xfail)\b|expectedFailure|\|\| true"


def loosened(diff):
    path = ""
    for line in diff.splitlines():
        if line.startswith("--- ") or line.startswith("+++ ") and "/dev/null" not in line:
            path = line[4:].strip()
        elif re.search(TESTS, path) and (line.startswith("-") and not line.startswith("---") or line.startswith("+") and re.search(SKIP, line)):
            return True
    return False


def classify(stop, text="", paths=(), diff="", label="", cls="", template=False):
    """A stop's subject; a label only raises it; unclassifiable waits."""
    if diff is None or stop not in STOPS or cls and cls not in SAFETY + ("other",) or stop in ("break", "plan", "choice") and not (cls or paths or diff) or stop == "test" and not diff:
        return "unclassifiable"
    if cls in SAFETY or label in SAFETY:
        return cls if cls in SAFETY else label
    if loosened(diff):
        return SAFETY[6]
    if re.search(SECRET, diff + text):
        return SAFETY[3]
    for subject, pattern in PATHS.items():
        if any(re.search(pattern, p) for p in list(paths) + re.findall(r"^\+\+\+ (\S+)", diff, re.M)):
            return subject
    return next((s for s, w in WORDS.items() if not template and re.search(w, text, re.I)), "other")


def wait_line(slug, cls, why, action):
    return "WAITING %s: %s - %s - owner action: %s" % (slug, cls, why, action)


# setting (DLF-1.5)
def cfg(top):
    try:
        return json.load(open(os.path.join(top, ".loop", "config.json")))
    except (OSError, ValueError):
        return {}


def brief(top, slug):
    import glob
    for f in sorted(glob.glob(os.path.join(glob.escape(top), ".loop", "tasks", "*.md"))):
        kv = {m[1].lower(): m[2].strip() for m in re.finditer(r"^- +(release|goals) *: *(.*)$", open(f, encoding="utf-8").read(), re.M | re.I)}
        if slug in re.split(r"[ ,|]+", kv.get("goals", "")):
            return os.path.basename(f)[:-3], re.sub(r"[^A-Za-z0-9_.-]", "-", kv.get("release") or "default")
    return "", "default"


def setting(top, slug):
    held, (task, rel) = cfg(top).get("deliver_first") or {}, brief(top, slug)
    for scope, ident in (("goal", slug), ("task", task), ("release", rel)):
        if isinstance((held.get(scope) or {}).get(ident), bool):
            return held[scope][ident], scope
    return True, "default"


def set_setting(top, scope, ident, value, rid, g=None):
    held = (cfg(top).get("deliver_first") or {}).get(scope, {}).get(ident)
    now, where = setting(top, ident) if scope == "goal" else (held is not False, scope)
    if not rid:
        return "refused: set deliver_first %s for %s %s needs an owner reference; unchanged (%s, from %s)" % (
            value, scope, ident, "on" if now else "off", where)
    if g:
        import fit
        fit.monitor("auto", True).eta_record(g, rid, ident, "a setting change")
    data = cfg(top)
    data.setdefault("deliver_first", {}).setdefault(scope, {})[ident] = value == "on"
    json.dump(data, open(os.path.join(top, ".loop", "config.json"), "w"), indent=2)
    return ""


def safe(top, text):
    """The text, or 'text withheld' when it holds a secret-shaped value or a configured private name."""
    return "text withheld" if re.search(SECRET, text) or private.scan(top, None, texts={"w": text})["state"] not in ("clean", "off", "none") else text


def settle(top, runs, slug, stop, occ, what, words, rec, **ctx):
    on, scope = setting(top, slug)
    retry(top, runs, slug)
    subject = classify(stop, what, ctx.get("paths", ()), ctx.get("diff", ""), ctx.get("label", ""), ctx.get("cls", ""), ctx.get("template", False))
    ask = "the operation answers it (goal.py answer %s)" % slug
    if not on:
        return "wait", wait_line(slug, "setting off", "deliver-first is off for %s %s" % (scope, slug), ask)
    if subject in SAFETY or subject == "unclassifiable":
        return "wait", wait_line(slug, subject, "text withheld" if subject == SAFETY[3] else safe(top, what)[:120], ask)
    lid, status = file_line(top, runs, slug, brief(top, slug)[1], stop, subject, occ, what, words, rec)
    if status == "local":
        return "wait", wait_line(slug, "private data", "the line failed the private-name scan", "remove the name, then " + ask)
    return "continue", lid or status


SHARE = {"idea": .05, "plan": .15, "build": .40, "review": .15, "qa": .15, "ship": .10}


def raise_budget(held, estimate, spent, done=0, finished=False):
    if not held or not estimate:
        return held, False
    left = max(0, estimate - done) or estimate / 4
    return round(max(held, min(spent + left, 2 * estimate))), spent >= 2 * estimate and not finished


def budget_stop(slug, state, runs, cfg_, at=None, save=None, top=""):
    import fit
    if save:
        import goal
        goal.SEEN[slug] = json.dumps(state)
    seen = fit.view(state, runs)
    held, source = fit.budget(seen, cfg_)
    stored = dict(held)
    minutes, on = fit.active_minutes(state, at, cfg_), bool(top) and setting(top, slug)[0]
    on and retry(top, runs, slug)
    auto = fit.monitor("auto", True) if seen.get("eta") or seen.get("eta_extend") else None
    eta = bool(auto) and auto.eta_over(seen, minutes)
    if eta and on:
        held["minutes"], source = max(held["minutes"], auto.eta_minutes(seen)), "the ETA"
    elif eta:
        save and auto.eta_wait(state, minutes, save)
        sys.exit("REFUSED: %dm spent, past the ETA of %dm; no new step starts and the goal waits for the owner: ship now, extend "
                 "once, or defer. Fix: the operation session runs goal.py set %s --eta-choice ship|defer or --eta-extend N, "
                 "with --owner-record ID (ETA_PAST)" % (minutes, auto.eta_minutes(seen), slug))
    share = sum(s for k, s in SHARE.items() if fit.recorded(state, k))
    for name, spent in (("minutes", minutes), ("tokens", fit.spent_tokens(state, bool(held["tokens"])))):
        if held[name] and spent >= held[name]:
            est = (seen.get("eta") or {}).get("estimate") if name == "minutes" else cfg_.get("token_budget")
            new, capped = raise_budget(held[name], est, spent, share * (est or 0))
            raised, was = on and est and new > held[name], stored[name] or held[name]
            if raised:
                import guards
                guards.add_set(runs, slug, "budget", dict(held, **{name: new}), "raised the %s budget %d to %d (spent %d, estimate %d)" % (name, was, new, spent, est))
                name == "minutes" and guards.add_set(runs, slug, "dlf_budget", {"minutes": new}, "eta follows")
                print("BUDGET %s: %s %d -> %d (spent %d, estimate %d)" % (slug, name, was, new, spent, est))
                held[name] = new
            if on and est and capped:
                cap_line(top, runs, slug, brief(top, slug)[1], spent, est, was, new)
            elif not raised:
                sys.exit("REFUSED: %d %s spent, at the %s budget of %d (%s); no new step starts. Fix: goal.py set %s --budget-%s N "
                         "--why ... from the operation session (BUDGET_%s)" % (spent, name, name.rstrip("s"), held[name], source, slug, name, name.upper()))


def ledger(top, rel, owner, loop):
    number = find_issue(top, rel)
    rows = comments(top, number) if number else []
    if number is None or rows is None:
        return None
    lines, notes = {}, []
    for r in rows:
        who, body = r["user"]["login"], r["body"]
        mark, event = KEY.search(body), EVENT.search(body)
        if mark and mark[1] not in lines:
            lines[mark[1]] = dict(id=mark[2], goal=mark[1].split("|")[0], text=body.split("\n")[0][4:], state="open", cid=r["id"], key=mark[1])
        for verb, rest in [] if event or mark else re.findall(r"^\s*(accept-all|accept|decline)\b(.*)$", body, re.M):
            ids = re.findall(r"[\w.:-]+", rest)
            if who != owner or not ids:
                notes.append("ignored %s by %s: %s" % (verb, who, "not the owner" if who != owner else "no line ids named"))
            for l in [l for l in lines.values() if l["id"] in ids]:
                if l["cid"] > r["id"]:
                    notes.append("ignored %s of %s: filed after it" % (verb, l["id"]))
                elif who == owner and l["state"] in ("open", "accepted") and not (verb != "decline" and l["state"] != "open"):
                    l["state"], l["at"] = "converted" if verb == "decline" else "accepted", r["created_at"]
            known = [l["id"] for l in lines.values()]
            notes += ["ignored %s of %s: no such id" % (verb, i) for i in ids if who == owner and i not in known]
        if event and event[1] in lines:
            l = lines[event[1]]
            ok = who == loop and event[2] == "closed" and l["state"] == "accepted"
            l["state"] = "closed" if ok else l["state"]
            notes += [] if ok or who == loop and event[2] in ("open", "filed") else ["ignored %s by %s on %s" % (event[2], who, l["id"])]
    return lines, notes, number


def cut(top, runs, rel, owner="", loop=""):
    import glob
    if not os.path.isdir(runs):
        return "read failed: the run-record folder %s can't be read" % os.path.basename(runs)
    owner = owner or cfg(top).get("owner_login") or os.environ.get("LOOP_OWNER_LOGIN", "")
    loop, out = loop or private.gh(top, "api", "user", "-q", ".login")[1].strip(), []
    for f in glob.glob(os.path.join(runs, "*.dlf.json")):
        goal = os.path.basename(f)[:-9]
        retry(top, runs, goal)
        try:
            held = json.load(open(f))
        except (OSError, ValueError):
            out.append("read failed: %s" % os.path.basename(f))
            continue
        queued = [q for q in held.get("queue", []) if q.get("rel") == rel]
        out += ["unfiled: %d line(s) of %s never reached the issue" % (len(queued), goal)] * bool(queued)
        out += ["local: %s holds %d text(s) the private-name scan refused" % (goal, len(held.get("local", [])))] * bool(held.get("local"))
    got = ledger(top, rel, owner, loop)
    if got is None:
        return "\n".join(["read failed: release %s's issue can't be read completely" % rel] + out)
    lines, notes, number = got
    if lines and not owner:
        return "owner acceptance can't be read: owner_login is not set (set LOOP_OWNER_LOGIN, or owner_login in a private config)"
    todo = sorted((l for l in lines.values() if l["state"] == "open"), key=lambda l: (l["goal"], l["cid"]))
    for l in [l for l in lines.values() if l["state"] == "converted"]:
        convert(top, runs, l["goal"], rel, l["key"], l["id"], l["text"], "declined")
        patch = "patch-" + hashlib.sha1(l["key"].encode()).hexdigest()[:8]
        try:
            merged = json.load(open(os.path.join(runs, patch + ".json"))).get("release") == "merged"
        except (OSError, ValueError):
            merged = False
        out += [] if merged else ["converted: %s waits for patch goal %s to merge; merge it, then cut" % (l["id"], patch)]
    if not todo and not out:
        [post_event(top, runs, l["goal"], rel, l["key"], "closed", "%s closed after the accept" % l["id"]) for l in lines.values() if l["state"] == "accepted"]
        return ""
    head = ["Release %s has %d open deliver-first line(s) on issue #%d. Accept them all in one comment, posted as %s:\n  accept-all %s" % (
        rel, len(todo), number, owner, " ".join(l["id"] for l in todo))] * bool(todo)
    for goal in sorted({l["goal"] for l in todo}):
        head += [goal + ":"] + ["  [ ] %s %s" % (l["id"], l["text"]) for l in todo if l["goal"] == goal]
    return "\n".join(head + out + notes + ["accepted %s at %s" % (l["id"], l["at"]) for l in lines.values() if l["state"] == "accepted"])


def main(argv):
    """dlf.py set deliver_first on|off --scope S --id ID [--owner-record R]"""
    if argv[:2] != ["set", "deliver_first"] or argv[2:3] not in (["on"], ["off"]):
        print(main.__doc__)
        return 0 if "--help" in argv else 2
    import goal as g
    o = lambda n: argv[argv.index(n) + 1] if n in argv else ""
    why = set_setting(g.root(), o("--scope"), o("--id"), argv[2], o("--owner-record"), g)
    print(why or "SET deliver_first %s for %s %s" % (argv[2], o("--scope"), o("--id")))
    return 1 if why else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
