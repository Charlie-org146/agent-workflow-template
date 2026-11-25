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
        if not isinstance(item, dict) or not item.get("key"):
            return [], "bad record at line %d" % number
        out.append(item)
    return out, None


def read_order(paths_):
    """(record, slugs, note, cause): the owner order, or its last-good copy with a note, or the cause it cannot be read."""
    def one(path):
        try:
            data = json.load(open(path, encoding="utf-8"))
        except FileNotFoundError:
            return None, None
        except (OSError, ValueError):
            return None, "torn or unreadable"
        ok = isinstance(data, dict) and isinstance(data.get("slugs"), list) and isinstance(data.get("record"), str)
        return (data, None) if ok else (None, "bad shape")
    data, cause = one(paths_["order"])
    if data is None and cause:
        good, why = one(paths_["good"])
        if good:
            return good["record"], [str(s) for s in good["slugs"]], "owner order file %s: using its last-good copy" % cause, None
        return "", [], "", "owner order file %s and no usable last-good copy" % cause
    return (data["record"], [str(s) for s in data["slugs"]], "", None) if data else ("", [], "", None)


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
        if prio and not prio.isdigit():
            bad.append(("brief", "%s has a bad Priority line" % os.path.basename(f)))
            prio = ""
        name = clean(text.split("\n")[0].lstrip("# "), 100) or os.path.basename(f)[:-3]
        release = norm(kv.get("release", ""))
        out.append({"file": os.path.basename(f), "name": name, "release": release, "replaced": bool(kv.get("replaced by")),
                    "goals": re.findall(r"[a-z0-9][a-z0-9-]{0,50}", kv.get("goals", "").lower()),
                    "prio": int(prio) if prio else 10 ** 6, "patch": bool(re.fullmatch(r"\d+\.\d+\.[1-9]\d*", release))})
    return out


def selected(root, notes):
    """R: the release whose brief docs/release-brief-X.Y.Z.md exists with no tag yet; exactly one, else unset."""
    found = {norm(m[1]) for f in glob.glob(os.path.join(glob.escape(root), "docs", "release-brief-*.md")) for m in [re.search(r"release-brief-(.+)\.md$", f)] if m}
    try:
        tags = {norm(t) for t in subprocess.run(["git", "-C", root, "tag", "--list"], capture_output=True, text=True, timeout=20).stdout.split()}
    except (OSError, subprocess.SubprocessError):
        tags = set()
    open_ = sorted(found - tags)
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
        if not item or check and not graph.SLUG.match(item["slug"]):
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
    """The schedule: {goals, incomplete: [(input, cause)], notes, release, order, held, waived, banner, strings}. Goals are the queue items
    (as graph.parse returns them) in schedule order with `marks` (the cells after the slug), `kind`, `task` and `hold`."""
    bad, notes = [], []
    pol = policy_on(root) if policy is None else policy
    goals = queue_goals(root, strict, bad, check)
    p = paths(root)
    recs, cause = read_json_lines(p["workaround"])
    cause and bad.append(("workaround", "record file " + cause))
    record, order, onote, ocause = read_order(p)
    ocause and bad.append(("order", ocause))
    onote and notes.append(onote)
    held = "order file unreadable (repair: schedule.py order --clear)" if ocause else ""
    result = {"goals": goals, "incomplete": bad, "notes": notes, "release": None, "order": order, "record": record, "held": held,
              "waived": {}, "active": False, "paths": p, "workarounds": recs}
    for g in goals:
        g.update(kind="fix", task="", marks=[], hold=held)
    if not pol or not goals:
        return finish(result)
    bl = briefs(root, bad)
    known = {g["slug"] for g in goals}
    stale = [x for x in order if x not in known]
    if stale:
        notes.append("order: pruned %s (not queued)" % ", ".join(clean(x, 30) for x in stale))
        order = [x for x in order if x in known]
    R = selected(root, notes)
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
            notes.append("release disagreement for %s: queue line %s, brief %s" % (g["slug"], g["release"], owners[0]["release"]))
    tasks = [g for g in goals if g["kind"] == "task"]
    if bl and not tasks and not any(g["release"] for g in goals):
        notes.append("classification idle: no queue line carries a release")
    use = {(w["key"], g): v for w in recs for g, v in (w.get("uses") or {}).items() if v == "active" and w.get("state") == "done" and w.get("kind") == "tool"}
    for w in recs:
        for goal in w.get("applies", []):
            if (w["key"], goal) in use and goal in known:
                result["waived"].setdefault(goal, set()).add(w["fix"])
    block, idx = blocking(goals), {g["slug"]: i for i, g in enumerate(goals)}
    task_slugs = {g["slug"] for g in tasks}
    for g in goals:  # an activated workaround waives the wait on its fix for that goal only
        g["depends"] = [d for d in g["depends"] if d not in result["waived"].get(g["slug"], ())]
    for g in goals:
        g["why"] = ""
        if g["kind"] == "fix":
            hits = sorted(t for t in block[g["slug"]] & task_slugs if g["slug"] not in result["waived"].get(t, ()))
            if hits:
                g["why"] = "blocks %s" % hits[0]
            elif g["first"] and g["first"] != "safety" and g["first"] in task_slugs:
                g["why"] = "first: %s" % g["first"]
            elif g["first"] == "safety" and g["first_class"] in SAFETY:
                g["why"] = "safety: %s" % g["first_class"]
            elif g["first"] and g["first"] != "safety":
                notes.append("first: key of %s names %s, which is not a queued task goal: ignored" % (g["slug"], clean(g["first"], 30)))
    pos = {s: i for i, s in enumerate(order)}
    dep = lambda g: len(g["depends"])
    def key(g):
        safe = g["why"].startswith("safety")
        task = g["kind"] == "task"
        return (0 if safe else 1, pos.get(g["slug"], 10 ** 6), 0 if g["why"] else 1, 0 if task else 1,
                g.get("prio", 10 ** 6) if task else 0, dep(g) if task else 0, idx[g["slug"]])
    for g in goals:
        if g["why"].startswith("safety") and any(pos.get(x["slug"], 10 ** 6) < pos.get(g["slug"], 10 ** 6) for x in goals):
            notes.append("safety goal %s sits behind an owner-ordered goal" % g["slug"])
    ordered = sorted(goals, key=key)
    result["goals"][:] = ordered
    result["active"] = bool(tasks or order or any(g["why"] for g in goals))
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
            keys = [w["key"] for w in recs if g["slug"] in w.get("applies", []) and (w["key"], g["slug"]) in use]
            g["marks"].append("workaround %s (fix %s pending)" % (keys[0], sorted(result["waived"][g["slug"]])[0]))
    return finish(result)


def finish(result):
    held = result["held"]
    for g in result["goals"]:
        g["hold"] = held
        if held:
            g["marks"] = g.get("marks", []) + ["held: " + held]
        if not result["active"] and not held:
            g["marks"] = []
        g["cell"] = " | ".join([g["slug"]] + g["marks"]) if g["marks"] else ""
    bad = result["incomplete"]
    result["banner"] = ["schedule incomplete: %s (%s); dispatch: %s; repair: %s" % (i, clean(c, 80), "conservative", REPAIR[i]) for i, c in bad[:1]]
    if result["notes"]:
        result["banner"].append("schedule notes: %d (schedule.py show)" % len(result["notes"]))
    return result


def apply(plan, result):
    """The start path's (start, held) with every goal the schedule holds moved to held, with its reason."""
    start, held = plan
    keep = []
    for g in start:
        ok, why = eligible(g, result)
        keep.append(g) if ok else held.append((g, why))
    return keep, held


def warn(result):
    """The unreadable inputs and the banner lines to stderr; sets STATUS to 3 so a command line consumer exits non-zero."""
    global STATUS
    for item, cause in result["incomplete"]:
        STATUS = 3
        print("%s: %s unreadable (%s); dispatch: conservative; repair: %s" % (CODES[item], item, clean(cause, 80), REPAIR[item]), file=sys.stderr)
    return result


STATUS = 0


def eligible(goal, result):
    """(ok, reason): a goal that a hold applies to does not start; the start path still checks its dependencies, less result['waived'][slug]."""
    if goal.get("hold"):
        return False, "held: " + goal["hold"]
    return True, ""


if __name__ == "__main__":
    print(__doc__.strip())
