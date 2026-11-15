#!/usr/bin/env python3
"""The run-log and goal-file facts the live board's estimates are read from: which step a goal is on, how long each step
took (flow_seconds) and a goal's size (done lines and touched areas, from its goal file). Imported by board_model.py and
board_status.py; it imports only graph.py and the standard library (`board_log.py report` also loads board_model.py when it runs).
`python3 board_log.py report [--root DIR] [--json]` is the former board_report.py.
"""
import argparse
import datetime
import json
import math
import os
import re
import statistics
import subprocess
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import graph  # noqa: E402

FLOW = ("idea", "plan", "build", "review", "qa", "ship", "pr", "release")
STEPS = FLOW[:-1]
COMMON = {}

# No terminal, no waiting: a prompt from git or gh must fail, not block.
os.environ.update(GIT_TERMINAL_PROMPT="0", GH_PROMPT_DISABLED="1", GIT_EDITOR="true", GIT_ASKPASS="true", SSH_ASKPASS="true")


def git(*args, cwd=None):
    done = subprocess.run(["git", *args], cwd=cwd, capture_output=True, text=True)
    return done.stdout.strip() if done.returncode == 0 else ""


def read_json(path):
    try:
        with open(path) as handle:
            return json.load(handle)
    except (OSError, ValueError):
        return None


def stamp(text):
    try:
        return datetime.datetime.fromisoformat(str(text).split(" ", 1)[0].replace("Z", "+00:00"))
    except ValueError:
        return None



def current(run):
    """Index in FLOW of the step a goal is on: a finished, unmerged goal waits at release. A step outside the flow (a check,
    say) keeps the newest timestamped evidence naming a flow step (a report's at, a log entry; see after), else the furthest step in
    the run's flow record, else idea."""
    if run.get("status") == "done":
        return FLOW.index("release")
    if run.get("step") in FLOW:
        return FLOW.index(run["step"])
    seen = [(stamp(item.get("at")), item["step"]) for item in (run.get("reports") if isinstance(run.get("reports"), list) else [])
            if isinstance(item, dict) and item.get("step") in FLOW and stamp(item.get("at"))]
    seen += [(stamp(entry), after(entry)) for entry in run.get("log") or [] if after(entry) and stamp(entry)]
    if seen:
        return FLOW.index(max(seen, key=lambda pair: pair[0])[1])
    known = [FLOW.index(step) for step in (run.get("flow") or {}) if step in FLOW]
    return max(known) if known else 0


def named(entry):
    """The flow step a log entry names: its first word, or 'step X' in a session report; '' when none."""
    parts = str(entry).split(" ", 2)
    word = parts[1].rstrip(":") if len(parts) > 1 else ""
    if word in FLOW:
        return word
    found = re.search(r"\bstep ([a-z]+)\b", parts[2] if len(parts) > 2 else "")
    return found.group(1) if found and found.group(1) in FLOW else ""


def after(entry):
    """The flow step in force after a log entry: the step it names, or the next one when it says that step is done."""
    word = named(entry)
    done = word and re.search(r"\b(done|auto-approved|approved)\b", str(entry)) and FLOW.index(word) + 1 < len(FLOW)
    return FLOW[FLOW.index(word) + 1] if done else word


# A hold or free entry starts a pause that lasts until a step, a start, a bind or a resume (see holding).
HOLD = re.compile(r"session report: (?:worker · \S+: .*?; )?(?:held|holding) (?:at|before)\b|freed \d+ session")
UNHOLD = re.compile(r"(?:start [a-z]+|bound to session|assigned to session)\b|.*(?:resum|no longer held)")


def holding(entry, paused):
    """Whether a pause is in force after a log entry: a hold entry (a session report that the goal is held at or before a
    step) or a free entry (sessions.py free) starts one; an entry whose first word is a flow step, start <step>, bound or
    assigned to session, or one that says resum or no longer held ends it; any other entry keeps it as it was."""
    text = (str(entry).split(" ", 1) + [""])[1]
    if HOLD.match(text):
        return True
    return False if text.split(" ", 1)[0].rstrip(":") in FLOW or UNHOLD.match(text) else paused


# An entry that says the goal waits on someone else: the pr queue (goal.py pr), an owner question (a step that waits for or
# is pending on the owner, a refusal that asks, a waiting entry). The gap after it is held time (#3878).
WAIT = re.compile(r"waiting\b|[a-z]+ waits for the owner|[a-z]+ pending: |refused \(no try used\)")


def waiting(entry):
    return bool(WAIT.match((str(entry).split(" ", 1) + [""])[1]))


def flow_seconds(run, at, held=None):
    """Time per step with one rule for past and live runs: a gap before an entry naming a step counts toward that step;
    any other gap counts toward the step in force (the last one named, or the next after a finished one). A gap after a
    stopped or failed entry, or one that waits (see waiting), is a pause and counts nothing, and so is every gap while a hold or free pause is in
    force (see holding). The time since the last entry counts while running, unless the goal is held: held is True or
    False when the session pool says so, and None when it is unknown, when a pause in force at the last entry stops it."""
    found, force, paused, log = {}, None, False, run.get("log") or []
    for before, entry in zip(log, log[1:]):
        a, b, word = stamp(before), stamp(entry), named(entry)
        paused = holding(before, paused)
        pause = paused or waiting(before) or (str(before).split(" ", 2) + ["", ""])[1].rstrip(":") in ("stopped", "failed")
        step = word if word in STEPS and not re.search(r"\bstep [a-z]+, running", str(entry)) else force
        if a and b and step in STEPS and not pause:
            found[step] = found.get(step, 0) + max(0, (b - a).total_seconds())
        force = after(entry) or force
    last = stamp(log[-1]) if log else None
    step = run.get("step") if run.get("step") in STEPS else force
    idle = bool(log) and waiting(log[-1]) or (held if held is not None else bool(log) and holding(log[-1], paused))
    if run.get("status") == "running" and step in STEPS and last and not idle:
        found[step] = found.get(step, 0) + max(0, (at - last).total_seconds())
    return found


def active_minutes(run, at=None):
    """Whole minutes of active step time: flow_seconds summed, up to now when at is not given (the budget gate, #3878)."""
    return int(sum(flow_seconds(run, at or datetime.datetime.now(datetime.timezone.utc)).values()) // 60)


def goal_file(run, root):
    """The goal file's text: in the run's worktree when it is one under <common>/loop/worktrees, else under root."""
    slug = run.get("slug") or ""
    if not graph.SLUG.match(slug):
        return ""
    if root and root not in COMMON:
        COMMON[root] = os.path.realpath(os.path.join(root, git("rev-parse", "--git-common-dir", cwd=root) or ".git"))
    common = COMMON.get(root, "")
    tree = run.get("worktree") or ""
    places = [tree] if tree and common and os.path.isdir(tree) and os.path.realpath(tree).startswith(os.path.join(common, "loop", "worktrees") + os.sep) else []
    for base in places + ([root] if root else []):
        goals = os.path.realpath(os.path.join(base, ".loop", "goals"))
        path = os.path.realpath(os.path.join(goals, slug + ".md"))
        if os.path.dirname(path) != goals:
            continue
        try:
            with open(path) as handle:
                return handle.read()
        except OSError:
            continue
    return ""


def size_of(run, root):
    """(done lines, touched areas) of a goal, or None. The goal file wins for both; then the queue line's done and
    touches, then the run record's touches. Done lines are the numbered lines under ## Done lines, outside code fences."""
    text, done, touches, fenced, inside = goal_file(run, root), [], [], False, False
    for line in text.splitlines():
        fenced = not fenced if line.startswith("```") else fenced
        if line.startswith("## "):
            inside = line.strip() == "## Done lines"
        elif inside and not fenced and re.match(r"\d+\. \S", line):
            done.append(line)
        found = re.match(r"- Touches: (.*)$", line)
        if found and not touches:
            touches = [x.strip() for x in found.group(1).split(",") if x.strip()]
    return graph.size(done or run.get("done") or [], touches or run.get("touches") or [])


REPORT_DOC = """Why the live board uses the estimate model it does: the time-ordered backtest of every candidate in board_model.py over
a repo's finished goals, with diagnostics. It only reads files and runs git rev-parse; it writes nothing.

usage: board_log.py report [--root DIR] [--json]

One row per candidate: its selection score (the median over finished goals of |ln(estimate / actual)| for the whole goal,
in log units and as xN.NN, how many times off it typically was either way), the goals scored, then diagnostics only:
the leave-one-out score, the share of goals inside the
queued range, the 90th-percentile error, the share underestimated and the per-step score. The last lines say which one
the board uses and why, and the gap between the two lowest scores. --json prints the same as one JSON object.
Refusals (exit 1): NO_REPO (DIR is not inside a git repo), RUNS_UNREADABLE (the runs folder cannot be read). A run file
that cannot be parsed is skipped with a BAD_RUN line on stderr.
"""
EXAMPLE = "example: python3 skills/workflow-monitoring/scripts/board_log.py report --root ."


# board_log.py report: why the live board uses the estimate model it does (the CLI of the former board_report.py).


def report_load(root):
    """(runs, folder, skipped, files): every run record under <git common dir>/loop/runs with a slug and not retired."""
    folder = os.path.join(os.path.abspath(os.path.join(root, git("rev-parse", "--git-common-dir", cwd=root))), "loop", "runs")
    if not os.path.isdir(folder):
        return [], folder, 0, 0
    try:
        names = sorted(n for n in os.listdir(folder) if n.endswith(".json"))
    except OSError as error:
        sys.exit("REFUSED: cannot read %s: %s (RUNS_UNREADABLE). Check the folder's permissions; nothing was changed." % (folder, error))
    runs, skipped = [], 0
    for name in names:
        path = os.path.join(folder, name)
        try:
            with open(path) as handle:
                run = json.load(handle)
        except (OSError, ValueError) as error:
            skipped += 1
            print("board_report: skipped %s: %s (BAD_RUN)" % (path, error), file=sys.stderr)
            continue
        if isinstance(run, dict) and run.get("slug") and run.get("status") != "retired":
            runs.append(run)
    return runs, folder, skipped, len(names)


def report_share(flags):
    return {"share": round(sum(flags) / len(flags), 3) if flags else None, "of": len(flags)}


def report_step(rows, name):
    errors = [abs(math.log(r["per"][name][s][0] / r["seconds"][s])) for r in rows for s in STEPS
              if r["seconds"].get(s) and r["per"][name].get(s) and r["per"][name][s][0]]
    return round(statistics.median(errors), 3) if errors else None


def report(root):
    import board_model as bm  # lazily: board_model imports this module
    runs, folder, skipped, files = report_load(root)
    at = datetime.datetime.now(datetime.timezone.utc)
    bm.MODEL.clear()
    began = time.time()
    _, n = bm.backtest(runs, at, root)
    elapsed = time.time() - began
    name = bm.chosen(runs, at, root)
    rows = bm.MODEL.get("folds") or []
    loo_rows = bm.folds(bm.MODEL["hist"], bm.CANDIDATES, bm.MODEL)
    out = {"candidates": [], "chosen": name, "reason": bm.MODEL["chosen"][1], "n": n, "elapsed_s": round(elapsed, 3),
           "skipped": {"files": skipped, "of": files}, "runs": folder}
    for c in bm.CANDIDATES:
        errs = sorted(abs(math.log(r["left"][c] / r["actual"])) for r in rows)
        low = [sum(b[1] for b in r["per"][c].values() if b) for r in rows]
        high = [sum(b[2] for b in r["per"][c].values() if b) for r in rows]
        loo = round(bm.score(loo_rows, c), 3) if loo_rows else None
        ordered = round(bm.score(rows, c), 3) if rows else None
        out["candidates"].append({
            "id": c, "label": bm.LABELS[c], "score": ordered, "x": round(math.exp(ordered), 2) if ordered is not None else None, "n": len(rows),
            "time_ordered": {"score": ordered, "n": len(rows), "of": len(bm.MODEL["done"])},
            "leave_one_out": {"score": loo, "n": len(loo_rows)},
            "in_range": report_share([lo <= r["actual"] <= hi for r, lo, hi in zip(rows, low, high)]),
            "p90": round(statistics.quantiles(errs, n=10, method="inclusive")[-1] if len(errs) > 1 else errs[0], 3) if errs else None,
            "under": report_share([r["left"][c] < r["actual"] for r in rows]), "step_score": report_step(rows, c)})
    ranked = sorted(x["score"] for x in out["candidates"] if x["score"] is not None)
    out["gap"] = round(ranked[1] - ranked[0], 3) if len(ranked) > 1 else None
    return out


def report_text(out):
    import board_model as bm
    if not out["n"]:
        return ["board_report: 0 of %d scorable goals under %s; the board uses the size rule until %d finished goals have "
                "logged time." % (bm.MIN_BACKTEST, out["runs"], bm.MIN_BACKTEST)]
    dash = lambda v, f="%.3f": "-" if v is None else f % v
    row = "%-22s %9s %7s %4s | %-22s %-11s %6s %-11s %s"
    lines = ["board_report: %d scorable goals under %s, backtest %.2fs" % (out["n"], out["runs"], out["elapsed_s"]),
             row % ("candidate", "time score", "x", "n", "diagnostics: loo", "in range", "p90", "under", "per-step")]
    for c in out["candidates"]:
        t, r, u = c["leave_one_out"], c["in_range"], c["under"]
        lines.append(row % ("%s (%s)" % (c["id"], c["label"]), dash(c["score"]), dash(c["x"], "x%.2f"), c["n"],
                            "%s (%d goals)" % (dash(t.get("score")), t.get("n", 0)),
                            "%s of %d" % (dash(r["share"], "%.2f"), r["of"]), dash(c["p90"]),
                            "%s of %d" % (dash(u["share"], "%.2f"), u["of"]), dash(c["step_score"])))
    lines.append("time-ordered selection (retrospective, current sizes): each goal predicted only from goals finished before it started")
    lines.append("chosen: %s, %s" % (out["chosen"], out["reason"]))
    if out["gap"] is not None:
        lines.append("gap between the two lowest scores: %.3f" % out["gap"])
    return lines


def main(argv=None):
    parser = argparse.ArgumentParser(prog="board_log.py report", description=REPORT_DOC, epilog=EXAMPLE, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--root", help="a folder inside the repo (default: the current repo)")
    parser.add_argument("--json", action="store_true", help="print one JSON object and nothing else")
    args = parser.parse_args(argv)
    where = args.root or "."
    root = git("rev-parse", "--show-toplevel", cwd=where) if os.path.isdir(where) else ""
    if not root:
        sys.exit("REFUSED: %s is not inside a git repo (NO_REPO). Pass --root with a repo path, or run from inside one." % where)
    out = report(root)
    if out["skipped"]["files"]:
        print("board_report: skipped %d of %d run files" % (out["skipped"]["files"], out["skipped"]["of"]), file=sys.stderr)
    print(json.dumps(out, indent=1) if args.json else "\n".join(report_text(out)))
    return 0


if __name__ == "__main__":
    if sys.argv[1:2] == ["report"]:
        sys.exit(main(sys.argv[2:]))
    sys.exit("usage: board_log.py report [--root DIR] [--json]")
