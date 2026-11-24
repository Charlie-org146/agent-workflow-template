#!/usr/bin/env python3
"""CBS-1 and ASZ-1: sizing.py size|rule|show SLUG [STEP]. A goal is sized from its plan, the size picks its checks from the table
checks_by_size (read from origin/<base>; sizing is off without it), a size only goes up. Imported by guards, role and flow."""
import hashlib
import json
import os
import re
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import lanekit  # noqa: E402
fcntl = lanekit.fcntl

ORDER = ("small", "medium", "large")
FIXED = ("build-gate", "full-test-run", "leak-readers", "safety-classes")
VARIABLE = ("plan-review", "red-team", "review")
CHECKS_AT = {"plan": ("plan-review", "red-team"), "review": ("review",)}
DEPTH_AT = {"plan": "plan-review", "review": "review"}
GRAMMAR = "Reply grammar, one line per check before the STEP line: CHECK: <check> <form> <passes>"
FIX_SIZE = "python3 skills/workflow-delivery/scripts/sizing.py size "


def _f(passes, covers, run=""):
    return {"passes": passes, "covers": covers, "run": run, "markers": []}


FORMS = {
    "build-gate": {"full": _f(1, "the build gate passes")},
    "full-test-run": {"full": _f(1, "the full test run passes before merge", "python3 skills/workflow-regression/scripts/regression.py run")},
    "leak-readers": {"full": _f(2, "two readers check for leaks before any push")},
    "safety-classes": {"full": _f(1, "every safety class goes to the owner")},
    "plan-review": {"one-round": _f(1, "one round of plan review"), "full": _f(3, "CEO, design and engineering review")},
    "red-team": {"one-pass-no-rerun": _f(1, "one red-team pass, no rerun"), "full": _f(2, "red team and a rerun")},
    "review": {"normal": _f(1, "one review pass"), "full": _f(2, "review and adversarial pass")},
}
DEFAULTS = {"forms": FORMS}
for _s, _p in (("small", ("one-round", "one-pass-no-rerun", "normal")), ("medium", ("full", "one-pass-no-rerun", "normal")),
               ("large", ("full", "full", "full"))):
    DEFAULTS[_s] = dict({c: "full" for c in FIXED}, **dict(zip(VARIABLE, _p)))


class Refusal(Exception):
    pass


def refuse(why, fix, code):
    raise Refusal(why, fix, code)


def stop(err):
    sys.stderr.write("REFUSED (no try used): %s. Fix: %s (%s)\n" % err.args)
    sys.exit(2)


def git(*args):
    return subprocess.run(["git"] + list(args), capture_output=True, text=True)


def runs():
    return os.path.join(os.path.abspath(git("rev-parse", "--git-common-dir").stdout.strip()), "loop", "runs")


def grow(old, new):
    return max((old or "small", new or "small"), key=ORDER.index)


def base_cfg():
    head = git("symbolic-ref", "--short", "refs/remotes/origin/HEAD").stdout.strip()  # never the worktree's config
    base = head.split("/", 1)[1] if "/" in head else "main"
    for ref in ("origin/" + base, base):
        done = git("show", "%s:.loop/config.json" % ref)
        if done.returncode == 0:
            try:
                found = json.loads(done.stdout)
            except ValueError:
                return base, {}, False
            return base, found if isinstance(found, dict) else {}, True
    return base, {}, False


def on(base=None):
    cfg, ok = base_cfg()[1:]
    return ok and "checks_by_size" in cfg


def validate(raw):
    try:
        return _validate(raw)
    except (AttributeError, TypeError):
        return None, "checks_by_size is malformed"


def _validate(raw):
    forms = {c: {f: dict(d) for f, d in fs.items()} for c, fs in FORMS.items()}
    for c, fs in (raw.get("forms") or {}).items():
        for f, d in (fs or {}).items():
            have = FORMS.get(c, {}).get(f)
            if not have or not isinstance(d, dict):
                return None, "form %s of %s is not a shipped form" % (f, c)
            if d.get("passes", have["passes"]) != have["passes"]:
                return None, "form %s of %s changes its pass count" % (f, c)
            forms[c][f].update({k: d[k] for k in ("covers", "run", "markers") if k in d})
    table = {"forms": forms}
    for size in ORDER:
        row = raw.get(size)
        if not isinstance(row, dict):
            return None, "row %s is missing" % size
        bad = [c for c in FIXED if row.get(c) != "full"] or [c for c in VARIABLE if c not in row]
        if bad:
            return None, "row %s drops or lightens %s (fixed checks must be full)" % (size, bad[0])
        if any(f not in forms.get(c, {}) for c, f in row.items()):
            return None, "row %s names a check or form that is not shipped" % size
        table[size] = row
    return table, ""


def read_table():
    base, cfg, ok = base_cfg()
    if not ok:
        refuse("the base branch's .loop/config.json can't be read", "rerun after the read works, then run sizing.py size SLUG", "SIZING_READ_FAILED")
    table, why = validate(cfg.get("checks_by_size", DEFAULTS))
    if not table:
        refuse("the checks table is refused: " + why, "edit the row on %s with the owner's words, then run sizing.py size SLUG" % base, "SIZING_BAD_TABLE")
    return table, base, cfg


def parse(text):
    def field(name):
        found = re.search(r"^[ \t>*-]*%s[ \t]*:[ \t]*(.+)$" % name, text, re.M | re.I)
        return (found.group(1).strip() or None) if found else None
    got = {n: field(n) for n in ("Files", "Lines", "Gates", "Classes")}
    none = lambda s: not s or re.match(r"(none|n/?a|no\b)", s, re.I)
    num = re.search(r"\d+", got["Lines"] or "")
    return {"files": [x.strip() for x in re.sub(r"\([^)]*\)", "", got["Files"]).split(",") if x.strip()] if got["Files"] else [],
            "lines": int(num.group(0)) if num else None, "gates": [] if none(got["Gates"]) else [g.strip() for g in got["Gates"].split(",")],
            "classes": "" if none(got["Classes"]) else got["Classes"], "missing": [n for n, v in got.items() if v is None]}


def classes_of(cfg, text, paths):
    import fit
    hits = sorted(n for n, rx in fit.monitor("auto", True).CLASSES.items() if rx.search(text))
    for pattern in cfg.get("risky_paths") or []:
        try:
            hits += ["risky path " + pattern] * any(re.search(pattern, p) for p in paths)
        except re.error:
            pass
    return hits


def judge(files, lines, gates, safety):
    nums = "%d files, %d lines, %d gates" % (files, lines, len(gates))
    if safety:
        return "large", "%s; safety class %s" % (nums, ", ".join(safety))
    over = [t for t, bad in (("files %d > 3" % files, files > 3), ("lines %d > 150" % lines, lines > 150), ("gate " + ", ".join(gates), gates)) if bad]
    if not over:
        return "small", nums + "; within the small line"
    return ("medium", "%s; crossed the small line (%s)" % (nums, "; ".join(over))) if files <= 10 else ("large", "%s; files %d > 10" % (nums, files))


def text_of(got):
    return " ".join(got["files"] + got["gates"] + [got["classes"]])


def size_of(text, changed, cfg):
    got = parse(text)
    tail = "; missing plan fields: " + ", ".join(got["missing"]) if got["missing"] else ""
    odd = [f for f in got["files"] if re.search(r"[*?\[]", f) or f.endswith("/") or os.path.isdir(f)]
    if not got["files"] or odd or got["lines"] is None:
        return "large", "large: " + ("no Files list" if not got["files"] else "directory or glob in Files: " + ", ".join(odd[:3]) if odd else "no Lines estimate") + tail, got
    size, why = judge(len(got["files"]), got["lines"], got["gates"], classes_of(cfg, text_of(got), sorted(set(got["files"]) | set(changed))))
    return size, why + tail, got


def build(old, size, reason, table, extra):
    old = old or {}
    big = grow(old.get("size"), size)
    if old and big != size:
        reason = "%s; kept %s (a size never goes down; computed %s)" % (old.get("reason", ""), big, size)
    checks, added = dict(old.get("checks") or {}), list(old.get("added") or [])
    for c, f in table[big].items():
        v = {"form": f, "passes": table["forms"][c][f]["passes"]}
        if v["passes"] > (checks.get(c) or {"passes": 0})["passes"]:
            checks[c] = v
            added += [{"check": c, "form": f}] * bool(old and {"check": c, "form": f} not in added)
    return dict(old, size=big, reason=reason, checks=checks, added=added, evidence=old.get("evidence") or {}, **extra)


def update(slug, fn):
    path = os.path.join(runs(), slug + ".json")
    with open(path + ".lock", "w") as lock:
        fcntl.flock(lock, fcntl.LOCK_EX)
        disk = json.load(open(path))
        new = fn(disk.get("sized"))
        if new != disk.get("sized"):
            disk["sized"] = new
            with open(path + ".tmp", "w") as out:
                json.dump(disk, out, indent=2)
            os.replace(path + ".tmp", path)
    return new


def adopt(state, new):
    state["sized"], goal = new, sys.modules.get("goal")
    if goal and state.get("slug") in goal.SEEN:
        goal.SEEN[state["slug"]] = json.dumps(dict(json.loads(goal.SEEN[state["slug"]]), sized=new))


def diff(base):
    ref = "origin/" + base if git("rev-parse", "--verify", "--quiet", "origin/" + base).returncode == 0 else base
    got = git("diff", "--numstat", git("merge-base", ref, "HEAD").stdout.strip())
    if got.returncode:
        return None
    paths, lines = [], 0
    for row in got.stdout.splitlines():
        a, b, path = row.split("\t", 2)
        paths.append(path)
        lines += sum(int(n) for n in (a, b) if n.isdigit())
    for path in git("ls-files", "--others", "--exclude-standard").stdout.splitlines():
        paths.append(path)
        lines += len(open(path, errors="replace").read().splitlines()) if os.path.isfile(path) else 0
    return [p for p in paths if not p.startswith((".loop/goals/", ".loop/designs/"))], lines


def need_diff(base, slug):
    got = diff(base)
    if got is None:
        refuse("the diff against %s can't be read" % base, "rerun after git diff against the base works, then run sizing.py size " + slug, "SIZING_READ_FAILED")
    return got


def unmet(sized):
    sized = sized or {}
    return [a["check"] for a in sized.get("added") or [] if sized["evidence"].get(a["check"]) != sized["checks"][a["check"]]["form"]]


def block(sized, table, step=None):
    out = []
    for c in CHECKS_AT.get(step) or sized["checks"]:
        v = sized["checks"].get(c)
        f = table["forms"][c][v["form"]] if v else {}
        out += ["  %s: form %s, %d pass%s. Covers: %s. Run: %s" % (c, v["form"], v["passes"], "" if v["passes"] == 1 else "es", f["covers"], f["run"] or "-")] * bool(v)
    out += ["  ADDED, no evidence yet: " + ", ".join(unmet(sized))] * bool(unmet(sized))
    if DEPTH_AT.get(step) in sized["checks"]:
        out.append("DEPTH: " + depth({"sized": sized}, step))
    return "\n".join(out + [GRAMMAR])


def rule(step, state):
    if not on():
        return ""
    if not state.get("sized"):
        return "NOT SIZED: run sizing.py size " + state["slug"]
    try:
        return "CHECKS at %s (size %s):\n%s" % (step or "every step", state["sized"]["size"], block(state["sized"], read_table()[0], step))
    except Refusal as err:
        return "REFUSED: %s (%s)" % (err.args[0], err.args[2])
    except KeyError:
        return "REFUSED: a stored form left the table (SIZING_BAD_TABLE)"


def cmd_size(slug):
    plan = os.path.join(git("rev-parse", "--show-toplevel").stdout.strip(), ".loop", "goals", slug + ".plan.md")
    if not os.path.exists(plan):
        refuse("there is no plan file for " + slug, "write .loop/goals/%s.plan.md, then run sizing.py size %s" % (slug, slug), "SIZING_NO_PLAN")
    text, (table, base, cfg) = open(plan, encoding="utf-8").read(), read_table()
    got = need_diff(base, slug)
    size, reason, parsed = size_of(text, got[0], cfg)
    kinds = classes_of(cfg, text_of(parsed), [])
    extra = {"plan_sha": hashlib.sha1(text.encode("utf-8")).hexdigest(), "gates": parsed["gates"], "classes": kinds}
    new = update(slug, lambda old: build(old, size, reason, table, extra))
    print("SIZE %s: %s\n%s" % (new["size"], new["reason"], block(new, table)))


def regrow(state):
    old = state.get("sized")
    if not old or (base_cfg()[2] and not on()):
        return
    table, base, cfg = read_table()
    got = need_diff(base, state["slug"])
    size, reason = judge(len(got[0]), got[1], old.get("gates") or [], list(old.get("classes") or []) + classes_of(cfg, "", got[0]))
    adopt(state, update(state["slug"], lambda was: build(was, size, "diff: " + reason, table, {})))


def resize(state, step=""):
    if step in ("review", "qa", "ship") and state.get("step") == step:
        try:
            regrow(state)
        except Refusal as err:
            stop(err)


def at_pr(g, state):
    try:
        regrow(state)
        if on() and unmet(state.get("sized")):
            refuse("added checks have no evidence line: " + ", ".join(unmet(state["sized"])), "run sizing.py rule %s, run each added check, record its CHECK line" % state["slug"], "SIZING_ADDED_UNMET")
    except Refusal as err:
        g.guards.refuse_no_try(state, err.args[0], err.args[1], err.args[2], g.save)


def override(state, size, record):
    old, slug = state.get("sized"), state["slug"]
    for bad, why, fix, code in ((not old, "goal %s has no size yet" % slug, FIX_SIZE + slug, "NOT_SIZED"),
                                (not record, "a size change needs the owner's words", "record the owner's words, then rerun with --owner-record ID", "NO_RECORD"),
                                (old and old.get("classes"), "goal %s touches a safety class, so it is always large" % slug, "leave the size as it is", "SAFETY"),
                                (size not in ORDER or old and ORDER.index(size) < ORDER.index(old["size"]), "sizes only go up (now %s, asked %s)" % (old and old["size"], size), "sizeline.py set %s SIZE --owner-record ID" % slug, "DOWN")):
        if bad:
            refuse(why, fix, "SIZING_" + code)
    table, mark = read_table()[0], {"record": record, "from": old["size"], "to": size}
    adopt(state, update(slug, lambda was: build(was, size, "%s; owner raised it to %s (record %s)" % (was["reason"], size, record), table, {"owner": mark})))
    return state["sized"]


def check(state, step, text):
    sized, ok = state.get("sized"), base_cfg()[2]
    if not on():
        return None if ok or not sized else ("the base config can't be read", "rerun after the read works, then record again", "SIZING_READ_FAILED sizing")
    if not sized:
        return ("%s refused: this goal has no size" % step, FIX_SIZE + state["slug"], "SIZING_NOT_SIZED sizing") if step == "plan" else None
    try:
        forms = read_table()[0]["forms"]
    except Refusal as err:
        return err.args[0], err.args[1], err.args[2] + " sizing"
    gone = [c for c, v in sized["checks"].items() if v["form"] not in forms.get(c, {})]
    if gone:
        return "form %s of %s left the table" % (sized["checks"][gone[0]]["form"], gone[0]), "restore the row on the base branch, then run sizing.py size " + state["slug"], "SIZING_BAD_TABLE sizing"
    found = re.search(r"^\W*STEP:\s*(done|skipped|pending|failed)\b", text, re.M | re.I)
    result, rows = found.group(1).lower() if found else "", re.findall(r"^\W*CHECK:(.*)$", text, re.M)
    fix, seen = "run sizing.py rule %s and write each CHECK line it prints, then record again" % state["slug"], {}
    no = lambda why, code: (why, fix, "SIZING_" + code + " sizing")
    if rows and result in ("skipped", "failed"):
        return no("a CHECK line on a step that is " + result, "CHECK_STEP")
    for row in rows:
        part, stored = row.split(), sized["checks"].get((row.split() or [""])[0])
        miss = [m for m in forms[part[0]][part[1]].get("markers") or [] if m.lower() not in text.lower()] if stored and part[1:2] == [stored["form"]] else []
        why = ("unknown check in CHECK:" + row[:50]) if not stored else "%s is not in its stored form %s" % (part[0], stored["form"]) if part[1:2] != [stored["form"]] \
            else "%s names %s passes, its form has %d" % (part[0], part[2:3], stored["passes"]) if part[2:] != [str(stored["passes"])] \
            else "%s lacks the phase %s its form needs" % (part[0], miss[0]) if miss else ""
        if why:
            return no(why, "LINE")
        seen[part[0]] = part[1]
    gone = [c for c in CHECKS_AT.get(step, ()) if c not in seen and result not in ("skipped", "failed")]
    if gone:
        return no("the %s reply has no CHECK line for %s" % (step, gone[0]), "MISSING")
    new = {c: f for c, f in seen.items() if sized["evidence"].get(c) != f}
    if new:
        adopt(state, update(state["slug"], lambda was: dict(was, evidence=dict(was["evidence"], **new))))
    if step == "ship" and result == "done" and unmet(state["sized"]):
        return no("ship refused: added checks have no evidence line: " + ", ".join(unmet(state["sized"])), "ADDED_UNMET")


def prompted(fn):
    def wrapped(step, state=None, runs=None):
        text = fn(step, state, runs)
        if state is None or not on():
            return text
        doc = open(os.path.join(HERE, os.pardir, "references", "commands.md"), newline="").read().replace("\r\n", "\n")

        def part(name):
            found = re.search(r"^## sizing %s\n(.*?)(?=^## |\Z)" % name, doc, re.M | re.S)
            return found.group(1).strip().format(path=os.path.join(HERE, "sizing.py"), slug=state["slug"], step=step) if found else ""
        d = depth(state, step)
        return "\n".join(x for x in (part("depth " + d) if d else text, part("plan" if step == "plan" else "check") if step in ("plan", "review", "qa", "ship") else "") if x)
    return wrapped


def depth(state, step):
    got = (state.get("sized") or {}).get("checks", {}).get(DEPTH_AT.get(step, ""))
    return ("full" if got["passes"] > 1 else "condensed") if got else ""


def lite(c, v):
    return c in FORMS and v["passes"] < max(d["passes"] for d in FORMS[c].values())


def light(state, step):
    have = (state.get("sized") or {}).get("checks") or {}
    bits = ["%s %s" % (c, have[c]["form"]) for c in CHECKS_AT.get(step, ()) if c in have and lite(c, have[c])]
    return " (light: %s)" % ", ".join(bits) if bits else ""


def main(argv):
    if len(argv) < 3 or argv[1] not in ("size", "rule", "show"):
        print("usage: sizing.py size|rule|show SLUG [STEP]")
        return 1
    cmd, slug = argv[1], argv[2]
    try:
        if cmd == "size":
            return cmd_size(slug) or 0
        state = json.load(open(os.path.join(runs(), slug + ".json")))
        if cmd == "show" and state.get("sized"):
            print("SIZE %s: %s" % (state["sized"]["size"], state["sized"]["reason"]))
        print(rule(argv[3] if len(argv) > 3 else state.get("step") if cmd == "rule" else None, state))
    except Refusal as err:
        stop(err)
    except (OSError, ValueError):
        print("REFUSED (no try used): no goal named %s. Fix: start it with goal.py new (SIZING_NO_GOAL)" % slug)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
