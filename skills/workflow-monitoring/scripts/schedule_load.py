#!/usr/bin/env python3
"""TSK-1: the one reader of the goal queue, the task briefs, the owner order and the workaround record. load(root) returns the
goals in schedule order, each marked task or fix with the exact cells the boards print; eligible(goal, result) says whether a goal
may start. Imported, not run (--help prints this). Read-only: schedule_state.py writes, schedule.py is the command line.

Order key: safety, owner order, a fix that blocks (or is first: for) a queued task goal, task goals before fixes, the brief's
priority then fewest unmet dependencies (task goals only), file order. With no task goal and no owner line the order is today's."""
import glob
import json
import os
import re
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import graph  # noqa: E402

NAME = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]{0,59}$")
SAFETY = ("deletion", "money", "security", "private-data", "steward-merge", "leak", "loosened-test")
STRIP = re.compile(r"[\x00-\x1f\x7f-\x9f|]")
CODES = {"brief": "SCHED-E10", "workaround": "SCHED-E11", "order": "SCHED-E12", "queue": "SCHED-E13", "release": "SCHED-E14"}
REPAIR = {"brief": "fix the brief file named in the cause", "workaround": "schedule.py workaround list", "order": "schedule.py order --clear",
          "queue": "fix the queue line named in the cause", "release": "git tag --list"}


def fields(line):  # moved whole from batch.py
    out = {}
    for part in line.strip()[2:].split("|"):
        key, _, value = part.partition(":")
        out.setdefault(key.strip(), " ".join(value.split()))
    return out


def outside(root, *texts, strict=True):
    """The name scan and secret screen (schedule_state.outside); None when the texts may leave this machine, else the reason."""
    import schedule_state
    return schedule_state.outside(root, *texts, strict=strict)


def norm(name):
    name = str(name).strip().lower()
    return name[1:] if re.match(r"^v\d", name) else name


def clean(text, limit=60):
    return STRIP.sub(" ", str(text))[:limit].strip()


def paths(root):
    """Where the state files live: the git common directory's loop folder, next to the run records."""
    try:
        common = subprocess.run(["git", "-C", root, "rev-parse", "--git-common-dir"], capture_output=True, text=True, timeout=20).stdout.strip()
    except (OSError, subprocess.SubprocessError):
        common = ""
    common = common if os.path.isabs(common) else os.path.join(root, common or ".git")
    folder = os.path.join(common, "loop")
    return {"folder": folder, "workaround": os.path.join(folder, "workarounds.jsonl"), "order": os.path.join(folder, "order.json"),
            "good": os.path.join(folder, "order.json.good"), "lock": os.path.join(folder, "schedule.lock")}


def read_json_lines(path):
    """([records], None) for an absent or clean file, ([], cause) for an unreadable or torn one."""
    try:
        text = open(path, encoding="utf-8").read()
    except FileNotFoundError:
        return [], None
    except (OSError, ValueError) as err:
        return [], "unreadable: " + type(err).__name__
    out = []
    for number, line in enumerate(text.splitlines(), 1):
        if not line.strip():
            continue
        try:
            item = json.loads(line)
        except ValueError:
            return [], "torn at line %d" % number
        ok = isinstance(item, dict) and all(isinstance(item.get(k), str) and NAME.match(item[k]) for k in ("key", "fix")) and item.get("kind") in ("tool", "dependency") \
            and isinstance(item.get("applies"), list) and all(isinstance(x, str) for x in item["applies"]) and isinstance(item.get("uses"), dict) \
            and item.get("state") in ("pending", "done", "failed", "closed") and isinstance(item.get("words"), str) and isinstance(item.get("goal"), str) and all(isinstance(item.get(k), str) and NAME.match(item[k]) for k in ("feature", "found"))
        if not ok:
            return [], "bad record at line %d" % number
        out.append(item)
    return out, None


def read_order(paths_):
    """(record, slugs, note, cause, soft): the owner order, or its last-good copy with a note and a soft cause (still incomplete, exit 3), or the cause it cannot be read."""
    def one(path):
        try:
            data = json.load(open(path, encoding="utf-8"))
        except FileNotFoundError:
            return None, None
        except (OSError, ValueError):
            return None, "torn or unreadable"
        ok = isinstance(data, dict) and isinstance(data.get("slugs"), list) and isinstance(data.get("record"), str) and bool(NAME.match(data["record"])) and all(isinstance(x, str) for x in data["slugs"])
        return (data, None) if ok else (None, "bad shape")
    data, cause = one(paths_["order"])
    if data is None and cause:
        good, why = one(paths_["good"])
        if good:
            return good["record"], good["slugs"], "owner order file %s: using its last-good copy" % cause, None, "owner order file %s, using its last-good copy" % cause
        return "", [], "", "owner order file %s and no usable last-good copy" % cause, None
    return (data["record"], data["slugs"], "", None, None) if data else ("", [], "", None, None)


def briefs(root, bad):
    out = []
    for f in sorted(glob.glob(os.path.join(glob.escape(root), ".loop", "tasks", "*.md"))):
        try:
            text = open(f, encoding="utf-8").read()
        except (OSError, ValueError):
            bad.append(("brief", "%s unreadable" % os.path.basename(f)))
            continue
        kv = {m[1].lower(): m[2].strip() for m in re.finditer(r"^- +(release|goals|replaced by|priority) *: *(.*)$", text, re.M | re.I)}
        prio = kv.get("priority", "")
        if prio and not re.fullmatch(r"[0-9]{1,6}", prio):
            bad.append(("brief", "%s has a bad Priority line" % os.path.basename(f)))
            prio = ""
        name = clean(text.split("\n")[0].lstrip("# "), 100) or os.path.basename(f)[:-3]
        release = norm(kv.get("release", ""))
        out.append({"file": os.path.basename(f), "name": name, "release": release, "replaced": bool(kv.get("replaced by")),
                    "goals": re.findall(r"[a-z0-9][a-z0-9-]{0,50}", kv.get("goals", "").lower()),
                    "prio": int(prio) if prio else 10 ** 6, "patch": bool(re.fullmatch(r"\d+\.\d+\.[1-9]\d*", release))})
    return out


def selected(root, notes, bad):
    """R: the release whose brief docs/release-brief-X.Y.Z.md exists with no tag yet; exactly one, else unset."""
    found = {norm(m[1]) for f in glob.glob(os.path.join(glob.escape(root), "docs", "release-brief-*.md")) for m in [re.search(r"release-brief-(.+)\.md$", f)] if m}
    try:
        done = subprocess.run(["git", "-C", root, "tag", "--list"], capture_output=True, text=True, timeout=20)
        tags = {norm(t) for t in done.stdout.split()}
        done.returncode and bad.append(("release", "git tag --list failed"))
    except (OSError, subprocess.SubprocessError):
        tags = set()
        bad.append(("release", "git tag --list could not run"))
    open_ = sorted(found - tags)
    if any(i == "release" for i, _ in bad):
        return None
    if len(open_) != 1:
        notes.append("release: none or several unpublished release briefs, so no release is selected")
    return open_[0] if len(open_) == 1 else None


def policy_on(root):
    try:
        return str(json.load(open(os.path.join(root, ".loop", "config.json"))).get("schedule_policy", "on")).lower() != "off"
    except (OSError, ValueError, AttributeError):
        return True


def queue_goals(root, strict, bad, check=True):
    try:
        lines = open(os.path.join(root, ".loop", "queue.md"), encoding="utf-8").read().splitlines()
    except FileNotFoundError:
        return []
    except (OSError, ValueError):
        bad.append(("queue", "queue file unreadable"))
        return []
    goals, seen = [], set()
    for line in lines:
        item = graph.parse(line)
        if not item:
            continue
        if check and not graph.SLUG.match(item["slug"]):
            strict and print("SKIPPED queue line (needs a good slug, a goal and a done line): %s" % line.strip()[:80])
            continue
        if strict and (item["slug"] in seen or not item["goal"] or not item["done"]):
            print("SKIPPED queue line (needs a good slug, a goal and a done line): %s" % line.strip()[:80])
            continue
        first = re.search(r"\|\s*first\s*:\s*([^|]*)", line)
        item["first"] = " ".join(first.group(1).split()).split(":")[0].strip().lower() if first else ""
        item["first_class"] = ""
        if first and item["first"] == "safety":
            item["first_class"] = (first.group(1).split(":") + ["", ""])[1].strip().lower()
        seen.add(item["slug"])
        goals.append(item)
    return goals


def blocking(goals):
    """slug -> every goal that waits (directly or through others) on that slug."""
    by = {g["slug"]: g for g in goals}
    out = {g["slug"]: set() for g in goals}
    for g in goals:
        todo, seen = list(g["depends"]), set()
        while todo:
            d = todo.pop()
            if d in seen or d not in by:
                continue
            seen.add(d)
            out[d].add(g["slug"])
            todo += by[d]["depends"]
    return out


def load(root, strict=False, policy=None, check=True):
    """The schedule: {goals, incomplete: [(input, cause)], notes, release, order, held, waived, banner}. Goals are the queue items
    (as graph.parse returns them) in schedule order with `marks` (the cells after the slug), `cell`, `kind`, `task` and `hold`.
    With no task goal and no owner line the goals come back in file order with no marks."""
    bad, notes = [], []
    pol = policy_on(root) if policy is None else policy
    goals = queue_goals(root, strict, bad, check)
    p = paths(root)
    recs, cause = read_json_lines(p["workaround"])
    cause and bad.append(("workaround", "record file " + cause))
    record, order, onote, ocause, soft = read_order(p)
    ocause and bad.append(("order", ocause))
    soft and bad.append(("order", soft))
    onote and notes.append(onote)
    held = "order file unreadable (repair: schedule.py order --clear)" if ocause else ""
    bl = briefs(root, bad)
    result = {"goals": goals, "incomplete": bad, "notes": notes, "release": None, "order": order, "record": record, "held": held,
              "waived": {}, "active": False, "paths": p, "workarounds": recs, "root": root}
    for g in goals:
        g.update(kind="fix", task="", marks=[], hold=held, why="", safe=g["first"] == "safety" and g["first_class"] in SAFETY)
    known = {g["slug"] for g in goals}
    stale = [x for x in order if x not in known]
    if stale:
        notes.append("order: pruned %s (not queued)" % ", ".join(clean(x, 30) for x in stale))
        order = [x for x in order if x in known]
    if not pol or not goals or not bl and not order:
        return finish(result)
    R = selected(root, notes, bad) if bl else None
    result["release"] = R
    live = [b for b in bl if not b["replaced"] and not b["patch"] and R and b["release"] == R]
    for g in goals:
        owners = [b for b in bl if g["slug"] in b["goals"] and not b["replaced"]]
        if not owners or not R:
            continue
        mine = [b for b in owners if b in live]
        if mine and norm(g["release"]) == R:
            best = sorted(mine, key=lambda b: (b["prio"], b["file"]))[0]
            g.update(kind="task", task=best["name"], prio=best["prio"])
        elif norm(g["release"]) != owners[0]["release"] and g["release"]:
            notes.append("release disagreement for %s: queue line %s, brief %s" % (g["slug"], clean(g["release"], 30), owners[0]["release"]))
    tasks = [g for g in goals if g["kind"] == "task"]
    if bl and not tasks and not any(g["release"] for g in goals):
        notes.append("classification idle: no queue line carries a release")
    if not tasks and not order:
        return finish(result)
    safe_fix = {g["slug"] for g in goals if g["safe"]}
    use = {(w["key"], g) for w in recs for g, v in w["uses"].items() if v == "active" and w["state"] == "done" and w["kind"] == "tool"}
    for w in recs:
        for goal in w["applies"]:
            if (w["key"], goal) in use and goal in known and w["fix"] not in safe_fix and not w.get("safe"):  # a safety dependency is never waived
                result["waived"].setdefault(goal, set()).add(w["fix"])
    for g in goals:  # an activated workaround waives the wait on its fix for that goal only
        g["depends"] = [d for d in g["depends"] if d not in result["waived"].get(g["slug"], ())]
    block, idx = blocking(goals), {g["slug"]: i for i, g in enumerate(goals)}
    task_slugs = {g["slug"] for g in tasks}
    for g in goals:
        if g["kind"] != "fix":
            continue
        hits = sorted(t for t in block[g["slug"]] & task_slugs if g["slug"] not in result["waived"].get(t, ()))
        if g["safe"]:
            g["why"] = "safety: %s" % g["first_class"]
        elif hits:
            g["why"] = "blocks %s" % hits[0]
        elif g["first"] in task_slugs and g["first"] in block[g["slug"]] and g["slug"] not in result["waived"].get(g["first"], ()):
            g["why"] = "first: %s" % g["first"]
        elif g["first"]:
            notes.append("first: key of %s names %s, which it does not block (or it is no queued task goal or safety class): ignored" % (g["slug"], clean(g["first"], 30)))
    pos = {s: i for i, s in enumerate(order)}
    def key(g):
        task = g["kind"] == "task"
        return (0 if g["safe"] else 1, pos.get(g["slug"], 10 ** 6), 0 if g["why"] else 1, 0 if task else 1,
                g.get("prio", 10 ** 6) if task else 0, len(g["depends"]) if task else 0, idx[g["slug"]])
    ordered = sorted(goals, key=key)
    result["goals"][:] = ordered
    result["active"] = True
    for n, g in enumerate(ordered):
        ahead = next((t["slug"] for t in ordered[n + 1:] if t["kind"] == "task"), "")
        owner = g["slug"] in pos and record
        if g["kind"] == "task":
            g["marks"] = ["task " + g["task"]] + (["ordered by owner (%s)" % record] if owner else [])
        else:
            place = ("ahead of %s (%s)" % (ahead, g["why"]) if g["why"] and ahead else "ahead of %s (ordered by owner (%s))" % (ahead, record) if owner and ahead else "after task goals")
            passed = sum(1 for t in ordered[:n] if t["kind"] == "task" and idx[t["slug"]] > idx[g["slug"]])
            mark = ["fix", place]
            if not g["why"] and passed > 5 and not owner:
                mark[-1] += "; overdue: passed over by %d task goals" % passed
            g["marks"] = mark
        if g["slug"] in result["waived"]:
            g["waived"] = sorted({(w["key"], w["fix"]) for w in recs if g["slug"] in w["applies"] and (w["key"], g["slug"]) in use and w["fix"] in result["waived"][g["slug"]]})
            g["marks"].append("workaround %s (fix %s pending)" % g["waived"][0])
    return finish(result)


def finish(result):
    held = result["held"]
    for g in result["goals"]:
        g["hold"] = "" if g.get("safe") else held  # a safety goal is never held by a torn order file
        if g["hold"]:
            g["marks"] = g.get("marks", []) + ["held: " + held]
        if not result["active"] and not held:
            g["marks"] = []
    bad = result["incomplete"]
    banner = ["schedule incomplete: %s (%s); dispatch: %s; repair: %s" % (i, clean(c, 80), "last-good copy" if "using its last-good" in c else "conservative", REPAIR[i]) for i, c in bad[:1]]
    if result["active"] or held or result["notes"] or banner:  # everything the boards print passes the name scan once
        why = outside(result["root"], "\n".join([c for g in result["goals"] for c in g["marks"] + g["depends"]] + result["notes"] + banner + [g["slug"] for g in result["goals"]]), strict=False)
        if why:
            result["notes"], banner = ["output hidden: " + why] * bool(result["notes"]), [x.split(" (")[0] + " (hidden: " + why + ")" for x in banner]
            for g in result["goals"]:
                g["marks"], g["hidden"] = ["hidden: " + why] if g["marks"] else [], why
    for g in result["goals"]:
        g["cell"] = "(hidden: %s)" % g["hidden"] if g.get("hidden") else " | ".join([g["slug"]] + g["marks"]) if g["marks"] else ""
        g["sched"] = {"kind": g["kind"], "task": g["task"], "cell": g["cell"], "waived": [{"key": k, "fix": f} for k, f in g.get("waived", [])]} if g["marks"] else None
    result["banner"] = banner
    if result["notes"]:
        result["banner"].append("schedule notes: %d (schedule.py show)" % len(result["notes"]))
    return result


def split(result):
    """(goals that may start, [(goal, reason)] held): taken out BEFORE slots are allocated, so a held goal never takes a safety goal's slot."""
    ok = [(g, eligible(g, result)) for g in result["goals"]]
    return [g for g, (yes, _) in ok if yes], [(g, why) for g, (yes, why) in ok if not yes]


def apply(plan, result):
    """The start path's (start, held) with every goal the schedule holds moved to held, with its reason."""
    start, held = plan
    keep = []
    for g in start:
        ok, why = eligible(g, result)
        keep.append(g) if ok else held.append((g, why))
    return keep, held


def shown(root, text):
    """A cause as it may be printed on any channel: cleaned, and hidden when the name scan or secret screen flags it."""
    why = outside(root, text, strict=False)
    return "(hidden: %s)" % why if why else clean(text, 80)


def warn(result):
    """The unreadable inputs and the banner lines to stderr; sets STATUS to 3 so a command line consumer exits non-zero."""
    global STATUS
    for item, cause in result["incomplete"]:
        STATUS = 3
        print("%s: %s unreadable (%s); dispatch: conservative; repair: %s" % (CODES[item], item, shown(result["root"], cause), REPAIR[item]), file=sys.stderr)
    return result


STATUS = 0


def eligible(goal, result):
    """(ok, reason): a goal that a hold applies to does not start; the start path still checks its dependencies, less result['waived'][slug]."""
    if goal.get("hold"):
        return False, "held: " + goal["hold"]
    return True, ""


if __name__ == "__main__":
    print(__doc__.strip())
