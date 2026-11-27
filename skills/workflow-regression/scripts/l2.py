#!/usr/bin/env python3
"""The L2 run's rules (design items 6 to 9, 12 to 17): the full run that counts a row a state, names every row it did not run
and files its issues. The block between the l2tail markers is copied into the workflow, as runs.py's rowtail block is."""
import json
import os
import re
import subprocess
import sys
import time


# l2tail:begin (actions.py copies this block into the workflow)
def l2_state(rid, code, said, late, known, skips):
    """(state, result comment, cause) for a row at L2. A row that never started is SKIPPED and red; one that ran is PASS, a
    by-design skip (exempt: counts as run, shown apart), KNOWN, any other skip (named), or FAIL."""
    if late:
        return "SKIPPED", "", "out of job time"
    if code == 0:
        return "PASS", "", ""
    why = skips.get(rid)
    if why and (code == 77 or why[1] == "notrun" and unrunnable(code, said)):
        return "SKIPPED", "# exempt %s %s" % (rid, why[0]), why[0]
    if rid in known:
        return "KNOWN", "", ""
    if code == 77:
        return "SKIPPED", "# skipped %s cannot run here" % rid, "cannot run here"
    return "FAIL", "", ""


def l2_again(run, row_s, job_s, begun, code):
    """The runner for a silent failing row's second run: the lesser of the row's limit and the job time left; with none left it is not run."""
    left = min(row_s, int(job_s - (time.time() - begun)))
    return lambda c: run(c, left) if left > 0 else (code, "")


def gone():
    if TARGET == "L2":
        with open(os.environ.get("REGRESSION_RESULTS") or os.devnull, "a") as handle:
            handle.write("# gh-failed\n")


def l2_refuse(target, cleanup):
    """The refusal line for a target and cleanup that L2 does not take, else an empty string."""
    if target == "L2" and cleanup == "true":
        return "REFUSED (L2_CLEANUP_EXCLUSIVE): cleanup runs no row and L2 runs every row. Fix: rerun with cleanup off, or with target nightly"
    return ""


def not_run(table):
    """Name each draft row of the table: a draft is never run, whatever the target."""
    for row in table:
        row[1:2] == ["draft"] and print("not run: draft " + row[0])
# l2tail:end


# Everything below runs in the summary job only (it embeds this whole file); the runner copies only the block above.
ORDER = ("no result", "FAIL", "SKIPPED", "KNOWN", "EXEMPT", "PASS")  # worst first
FIX = {"out of job time": "raise the job budget or move rows to another shard", "cannot run here": "list it in .loop/regression-skips.tsv with a reason, or make it runnable",
       "no result (shard did not finish)": "rerun the workflow and read that shard's log"}


def rows_of(path):
    try:
        return [line.rstrip("\n").split("\t") for line in open(path, encoding="utf-8") if line.strip() and line[0] != "#"]
    except OSError:
        return []


def verdict(expected, text, shards, matrix):
    """The one verdict: state RED > INCOMPLETE > GREEN, and `complete` apart from colour."""
    states, notes, ends, failed = {}, {}, 0, False
    for line in (text or "").splitlines():
        cells = line.split("\t")
        if line.startswith("# "):
            word, _, rest = line[2:].partition(" ")
            ends += word == "end"
            failed = failed or word == "gh-failed"
            if word in ("unrun", "exempt", "skipped"):
                notes[rest.split(" ")[0]] = word
        elif len(cells) > 1:
            states[cells[0]] = cells[1]
    for rid, word in notes.items():
        if word == "exempt" and states.get(rid) == "SKIPPED":
            states[rid] = "EXEMPT"
    count = lambda *names: sum(1 for rid in expected if states.get(rid) in names)
    skipped = {rid: "out of job time" if notes.get(rid) == "unrun" else "cannot run here" for rid in expected if states.get(rid) == "SKIPPED"}
    unfinished = [rid for rid in expected if rid not in states]
    fails = [rid for rid in expected if states.get(rid) == "FAIL"]
    complete = not unfinished and ends >= shards and matrix in ("success", "failure") and not failed
    red = bool(fails or skipped or unfinished)
    return {"state": "RED" if red else "GREEN" if complete and matrix == "success" else "INCOMPLETE", "complete": complete, "skipped": skipped,
            "unfinished": unfinished, "fails": fails, "ran": count("PASS"), "known": count("KNOWN"), "exempt": count("EXEMPT"), "states": states}


def tally(v):
    return "L2 %s: ran %d, known %d, exempt %d, skipped %d, failed %d" % (v["state"], v["ran"], v["known"], v["exempt"], len(v["skipped"]), len(v["fails"]))


def covered_lines(record, states, ids=()):
    """One L2_COVERED line a covered row: its worst cover. The rows the record excuses read `excepted (record)`; with no
    record each reads unresolved and the verdict is not affected. Returns (lines, ids of rows made incomplete)."""
    if record is None:
        return ["L2_COVERED %s unresolved" % rid for rid in ids], []
    lines, incomplete = [], []
    for line in record.splitlines():
        cells = line.split("\t")
        if len(cells) < 8 or line[0] == "#" or cells[1] != "covered":
            continue
        if not cells[4] and cells[7].startswith("excepted"):
            lines.append("excepted (record) " + cells[0])
            continue
        worst = min(((states.get(c) or "no result") for c in cells[4].split(",") if c), key=ORDER.index, default="no result")
        via = [c for c in cells[4].split(",") if (states.get(c) or "no result") == worst][:1]
        lines.append("L2_COVERED %s -> %s via %s" % (cells[0], worst, via[0] if via else "-"))
        if worst == "no result":
            incomplete.append(cells[0])
    return lines, incomplete


def selected(table):
    return [r[0] for r in rows_of(table) if len(r) > 2 and r[1] in ("land", "nightly")]


def check(target, cleanup, table):
    """The summary step's own target check, with the runner's rule; the refusal line, else an empty string."""
    ids = [r[0] for r in rows_of(table)]
    if not re.fullmatch(r"land|nightly|L2|[A-Za-z0-9_.-]+", target) or target not in ("land", "nightly", "L2") + tuple(ids):
        return "REFUSED (BAD_TARGET): bad target %s: use land, nightly, L2 or a row id from regression.py list. Fix: rerun the workflow with one of those" % json.dumps(target)
    return l2_refuse(target, cleanup) or ("REFUSED (L2_NO_ROWS): the table has no land or nightly row to run. Fix: add rows with regression.py add" if target == "L2" and not selected(table) else "")


def gh(*args, body=None):
    try:
        if body is not None:
            path = os.path.join(os.environ.get("RUNNER_TEMP") or ".", "l2-body")
            open(path, "w", encoding="utf-8").write(body)
            args += ("--body-file", path)
        return subprocess.run(("gh",) + args, capture_output=True, text=True, timeout=60,
                              env=dict(os.environ, GIT_TERMINAL_PROMPT="0", GH_PROMPT_DISABLED="1", GIT_EDITOR="true", GIT_ASKPASS="true", SSH_ASKPASS="true"))  # no prompt (DEL-10)
    except (OSError, subprocess.TimeoutExpired):
        return subprocess.CompletedProcess(args, 1, "", "no answer")


def listed(*args):
    done = gh("issue", "list", "--state", "open", "--limit", "200", "--json", "number,body", *args)
    try:
        return json.loads(done.stdout) if done.returncode == 0 else None
    except ValueError:
        return None


def issues(text, v, complete_run):
    """The L2 issue writer: the skipped issue (item 13), then the naming of l2-red issues in the main-red goal's issue (item 17).
    Returns the number of reads or writes that failed (each is a `# gh-failed` line)."""
    bad = 0
    rows = dict(v["skipped"], **{rid: "no result (shard did not finish)" for rid in v["unfinished"]})
    found = listed("--label", "regression")
    mine = [i for i in found or [] if (i["body"] or "").split("\n", 1)[0] == "<!-- loop-l2-skipped -->"]
    bad += found is None
    if found is not None:
        keep = {}
        for line in (mine[0]["body"] if mine and not complete_run else "").splitlines():
            m = re.match(r"- `(\S+)` (.*?)\. Fix: ", line)
            m and keep.setdefault(m[1], m[2])
        keep.update(rows)
        body = "<!-- loop-l2-skipped -->\nRows the L2 run did not run, each with its cause.\n\n" + "\n".join(
            "- `%s` %s. Fix: %s" % (rid, cause[:200].replace("`" * 3, "'" * 3), FIX.get(cause, "read that row's log")) for rid, cause in sorted(keep.items()))
        title = "Regression: L2 skipped rows (%d)" % len(keep)
        if keep and not mine:
            done = gh("issue", "create", "--title", title, "--label", "regression", body=body)
        elif keep:
            done = gh("issue", "edit", str(mine[0]["number"]), "--title", title, body=body)
        elif mine:
            done = gh("issue", "close", str(mine[0]["number"]), "--comment", "Closed: this run left no row unrun.")
        else:
            done = None
        bad += bool(done and done.returncode)
    red = listed("--label", "l2-red")
    bad += red is None
    if red:
        goal = listed("--label", "main-red") or [i for i in listed() or [] if (i["body"] or "").split("\n", 1)[0] == "<!-- loop-l2-main-red -->"]
        if not goal:
            made = gh("issue", "create", "--title", "Regression: L2 failing rows", body="<!-- loop-l2-main-red -->\nThe L2 run's failing rows, one line each.")
            bad += bool(made.returncode)
            number = re.findall(r"/(\d+)\s*$", made.stdout)
            goal = [{"number": int(number[0])}] if number and not made.returncode else []
        if goal:
            seen = gh("issue", "view", str(goal[0]["number"]), "--json", "body,comments", "--jq", '.body, (.comments[]?.body)')
            bad += bool(seen.returncode)
            for one in sorted(i["number"] for i in red):
                if not seen.returncode and not re.search(r"L2 red: #%d(?!\d)" % one, seen.stdout):
                    bad += bool(gh("issue", "comment", str(goal[0]["number"]), body="L2 red: #%d" % one).returncode)
    return bad


def main(argv):
    """l2.py check TARGET CLEANUP | summary RESULTS SHARDS MATRIX SHA | issues RESULTS SHARDS MATRIX: the summary step's three calls."""
    if not argv or argv[0] not in ("check", "summary", "issues"):
        print(main.__doc__)
        return 0
    table, record = ".loop/regression.tsv", ".loop/regression-relevel.tsv"
    if argv[0] == "check":
        said = check(argv[1], argv[2], table)
        print(said)
        return 1 if said else 0
    text = open(argv[1], encoding="utf-8").read() if os.path.exists(argv[1]) else ""
    v = verdict(selected(table), text, int(argv[2]), argv[3])
    if argv[0] == "issues":
        if os.environ.get("GITHUB_REF") != "refs/heads/main" or os.environ.get("REGRESSION_CLEANUP") == "true":
            return 0
        bad = issues(text, v, v["complete"])
        bad and open(argv[1], "a").write("# gh-failed\n" * bad)
        return 0
    lines, late = covered_lines(open(record, encoding="utf-8").read() if os.path.exists(record) else None, v["states"],
                                [r[0] for r in rows_of(table) if len(r) > 2 and r[1] == "covered"])
    if late and v["state"] == "GREEN":
        v["state"] = "INCOMPLETE"
    print(tally(v))
    print("\n".join(lines))
    if os.environ.get("GITHUB_REF") == "refs/heads/main":
        line = "L2_VERDICT %s %s" % (argv[4], v["state"].lower())
        print(line)
        open(os.path.join(os.environ.get("RUNNER_TEMP") or ".", "l2-verdict.txt"), "w").write(line + "\n")
    return 0 if v["state"] == "GREEN" else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
