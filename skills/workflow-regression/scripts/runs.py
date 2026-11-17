"""Read and write .loop/regression-runs.tsv: each row's last run as id, status, date, run, flaky.

run is the GitHub Actions run URL when GITHUB_SERVER_URL, GITHUB_REPOSITORY and GITHUB_RUN_ID are all set, else empty, so same-day
runs on two branches write identical lines and merge cleanly. flaky is empty, or the commit a row's result flipped on (tiers.py
flaky_apply, REG-9); status stays the raw PASS or FAIL. Per-result evidence (commit, clean, host, python) lives in the branch's lane
record in the git common dir, never here: a commit cell would differ per branch and conflict every same-day merge.

It also holds a local `regression.py run`'s GitHub issues (sync_issues): one issue per failing row, keyed by a marker in its body,
dry-run (WOULD lines) unless live; actions.py keeps the CI copy. The time budget of an in-loop test run lives here too (budget, fit,
execute): a --reuse run (qa, ship and pull-request lanes) stops at test_budget_minutes (default 15, floor 15), runs rows in tier
order while their estimated seconds fit, and records the rest LEFT for the scheduled full suite.
"""
import datetime
import glob
import json
import os
import re
import subprocess
import sys
import tempfile
import time

import actions
import lanes

# A prompt from gh must fail, not block.
os.environ.update(GIT_TERMINAL_PROMPT="0", GH_PROMPT_DISABLED="1", GIT_EDITOR="true", GIT_ASKPASS="true", SSH_ASKPASS="true")
if not sys.stdin or not sys.stdin.isatty():
    os.dup2(os.open(os.devnull, os.O_RDONLY), 0)

NAME = "regression-runs.tsv"
HEADER = "# id\tstatus\tdate\trun\tflaky\n"
ISSUE_LIMIT = 1000
WAITS = (0, 5, 20)  # seconds before each of three tries
SKIP_CODE = 77
START_CODES = (3221225794, 3221225495, 3221225773)  # Windows: DLL init failed, no memory, commit limit
LABELS = ("regression", "defect")
MARK = "<!-- loop-regression %s -->"

# rowtail:begin (actions.py copies this block into the workflow)
LAST = 40  # output lines an issue carries (defect 3789)
QUIET = re.compile(r"\|\s*grep\s+-\w*q\w*\s+(?:\"[^\"]*\"|'[^']*'|\S+)")  # `| grep -q PATTERN` hides its stream


def again(command):
    """The command with each `| grep -q PATTERN` made `| cat`, or None when it has none."""
    loud = QUIET.sub("| cat", command)
    return loud if loud != command else None


def shown(run, command, code, text):
    """A failing row's last LAST lines, never empty; a row that printed nothing runs once more with its quiet stage loud (run is
    the caller's (code, text) runner)."""
    if not text.strip() and again(command):
        text = run(again(command))[1]
    lines = [line[:400] for line in text.rstrip().splitlines()[-LAST:]]
    return "\n".join(lines).replace("`" * 3, "'" * 3) or "(the row printed nothing; it exited %s)" % code
# rowtail:end


def path(root):
    return path_of(root, NAME)


def read(root):
    try:
        with open(path(root)) as handle:
            rows = [line.rstrip("\n").split("\t") for line in handle if line.strip() and line[0] != "#"]
    except OSError:
        return {}
    return {cells[0]: (cells + [""] * 5)[:5] for cells in rows}


def where():
    parts = [os.environ.get(key, "") for key in ("GITHUB_SERVER_URL", "GITHUB_REPOSITORY", "GITHUB_RUN_ID")]
    return "%s/%s/actions/runs/%s" % tuple(parts) if all(parts) else ""


def write(root, results, date, sha):
    if not results:
        return
    ran, run = read(root), where()
    for item in results:
        if item["state"] == "SKIPPED" and ran.get(item["id"], "--")[1] in ("PASS", "FAIL"):
            continue  # a skip says nothing against the last result
        flag = item["flaky"] if "flaky" in item else ran.get(item["id"], [""] * 5)[4]
        ran[item["id"]] = [item["id"], item["state"] if item["state"] in ("PASS", "SKIPPED") else "FAIL", date, run, flag[:12]]
    with open(path(root), "w") as handle:
        handle.write(HEADER + "".join("\t".join(ran[key][:4 + bool(ran[key][4])]) + "\n" for key in sorted(ran)))


def gh(*args, body=None):
    if body is not None:
        with tempfile.NamedTemporaryFile("w", suffix=".md", delete=False, encoding="utf-8", newline="\n") as f:
            f.write(body)
        args += ("--body-file", f.name)
    try:
        return subprocess.run(["gh"] + list(args), capture_output=True, text=True)
    finally:
        if body is not None:
            os.remove(f.name)


def read_issues():
    """(issues, ""): the GraphQL list, else REST pages of 100 without comments; (None, error) when both fail."""
    rest = ("api", "--paginate", "repos/{owner}/{repo}/issues?state=all&labels=regression&per_page=100", "--jq",
            ".[] | select(.pull_request == null) | {number, state: (.state | ascii_upcase), body, labels}")
    for args in (("issue", "list", "--label", "regression", "--state", "all", "--limit", str(ISSUE_LIMIT),
                  "--json", "number,state,body,comments,labels"), rest):
        for wait in WAITS:
            time.sleep(wait)
            out = gh(*args)
            if not out.returncode:
                text = out.stdout
                return ([json.loads(x) for x in text.splitlines() if x] if args is rest else json.loads(text or "[]")), ""
    return None, out.stderr


def sync_issues(results, live, day):
    issues = []
    if live:
        gh("label", "create", "regression", "--force", "--description", "A regression row is failing")
        gh("label", "create", "defect", "--description", "A test that guards it is failing")
        issues, err = read_issues()
        if issues is None:
            print("NOTE: can't read issues, so none changed: " + err.strip()[:200])
            return
        if len(issues) >= ISSUE_LIMIT and "comments" in issues[0]:  # REST pages are never cut off
            print("NOTE: the issue list may be cut off at %d, so none changed" % ISSUE_LIMIT)
            return
    for item in results:
        mark = MARK % item["id"]
        hits = sorted((issue for issue in issues if re.search(r"<!-- loop-regression %s(?: placed=\S*)? -->" % re.escape(item["id"]), issue.get("body", ""))),
                      key=lambda i: i["number"])
        opened = [issue for issue in hits if issue.get("state") == "OPEN"]
        hit = opened[0] if opened else hits[-1] if hits else None
        number = str(hit["number"]) if hit else ""
        if item["state"] == "FAIL":
            line = "Failing on %s." % day
            body = "%s\nThe row `%s` fails.\n\n```\n%s\n```\n" % (mark, item["id"], item["tail"])
            for extra in opened[1:] if live else []:
                gh("issue", "close", str(extra["number"]), "--comment", "Duplicate of #%s, kept for row %s." % (hit["number"], item["id"]))
                print("CLOSED duplicate issue %s" % extra["number"])
            if not live:
                print("WOULD open or update the issue for " + item["id"])
            elif not hit:
                gh("issue", "create", "--title", "Regression: " + item["id"], *("--label=" + n for n in LABELS), body=body)
                print("OPENED issue for " + item["id"])
            else:
                if "defect" not in [x.get("name") for x in hit.get("labels") or []]:
                    gh("issue", "edit", number, "--add-label", "defect")
                if hit.get("state") != "OPEN":
                    gh("issue", "reopen", number)
                    print("REOPENED issue %s" % number)
                said = ([n.get("body", "") for n in hit["comments"]] if "comments" in hit
                        else gh("api", "repos/{owner}/{repo}/issues/%s/comments" % number, "--jq", ".[].body").stdout.splitlines())
                if line not in said:
                    gh("issue", "comment", number, body=line)
                    print("UPDATED issue %s" % number)
        elif item["state"] == "PASS" and not live:
            print("WOULD close any open issue for " + item["id"])
        elif item["state"] == "PASS":
            for issue in hits:
                if issue.get("state") == "OPEN":
                    gh("issue", "close", str(issue["number"]), "--comment", "Passing again on %s." % day)
                    print("CLOSED issue %s" % issue["number"])


FLOOR, DEFAULT = 15, 15


def minutes(cfg, key, default=DEFAULT):
    value = cfg.get(key, default)
    if isinstance(value, bool) or not isinstance(value, int) or value < FLOOR:
        sys.exit("REFUSED: %s is %r in .loop/config.json, under the %d-minute floor. Fix: set it to %d or more." % (
            key, value, FLOOR, FLOOR))
    return value


def budget(root):
    try:
        with open(path_of(root, "config.json")) as handle:
            cfg = json.load(handle)
    except (OSError, ValueError):
        cfg = {}
    return minutes(cfg if isinstance(cfg, dict) else {}, "test_budget_minutes") * 60


def fit(todo, est, limit):
    keep, left, used = [], [], 0.0
    for key in todo:
        if used + est.get(key, 0) <= limit:
            keep.append(key)
            used += est.get(key, 0)
        else:
            left.append(key)
    return keep, left


def execute(root, picked, todo, est, limit, timeout, expected, reuse):
    keep, left = fit(todo, est, limit) if limit else (todo[:], [])
    by, results, start, first = {row["id"]: row for row in picked}, [], time.time(), {}
    for key in keep:
        remaining = limit - (time.time() - start) if limit else timeout
        if remaining < 1 and key not in first:
            left.append(key)
            continue
        cap, began = min(timeout, remaining), time.time()
        skip = os.path.join(tempfile.gettempdir(), "loop-skip-%d-%s" % (os.getpid(), key))
        env = dict(actions.row_env(), TOY_SKIP_FILE=skip)
        got = first[key] if remaining < 1 else lanes.run_row(by[key]["command"], root, env, cap)
        code, text, pid, signal = got
        if code in START_CODES and key not in first:  # could not start: rerun it last (#4639)
            first[key] = got
            keep.append(key)
            continue
        if code and os.path.exists(skip):
            os.remove(skip)
            code = SKIP_CODE
        if code == 124 and cap < timeout:
            left.append(key)
            continue
        state = "PASS" if code == 0 else "SKIPPED" if code == SKIP_CODE else ("KNOWN" if key in expected else "FAIL")
        nostart = state == "FAIL" and code in START_CODES
        cannot = state == "FAIL" and (nostart or unrunnable(code, text))
        state = "SKIPPED" if cannot else state
        if code == 0 and key in expected:
            print("FIXED %s: remove it from the known list" % key)
        print("%s %s%s" % ("ENV" if nostart else "NOTRUN" if cannot else state, key, " (%s)" % expected[key] if state == "KNOWN" else " (exit %d: could not start; rerun when memory allows)" % code if nostart else ""), flush=True)
        if signal and state != "PASS":
            print("KILLED %s: signal %s (pid %d). Note: a signal stopped this row; see the lane log" % (key, signal, pid))
        tail = shown(lambda c: lanes.run_row(c, root, env, cap)[:2], by[key]["command"], code, text) if state == "FAIL" else text[-1500:]
        if state == "FAIL" and reuse:
            print(chr(10).join("    " + x for x in tail.splitlines()[-20:]), file=sys.stderr)
        results.append({"id": key, "state": state, "tail": tail, "seconds": round(time.time() - began, 1),
                        "pid": pid, "rc": code, "signal": signal, "notrun": cannot, "env": nostart})
    if left:
        print("BUDGET %d min: ran %d of %d rows; LEFT %d to the scheduled full suite: %s" % (
            (limit or 0) // 60, len(results), len(results) + len(left), len(left), ", ".join(left[:20]) + (
                ", +%d more" % (len(left) - 20)) * (len(left) > 20)))
    return results, left


def today():
    return datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d")


def path_of(root, name):
    return os.path.join(root, ".loop", name)


def clean(text):
    if "\t" in text or "\n" in text:
        sys.exit("REFUSED: a row can't hold a tab or new line. Fix: use a script.")
    return text


def done_lines(path):
    with open(path) as handle:
        part = handle.read().split("## Done lines", 1)[-1].split("\n## ", 1)[0]
    return re.findall(r"^(\d+)\.\s+(.+)$", part, re.M)


def criteria_ids(root):
    try:
        with open(path_of(root, "config.json")) as handle:
            folder = json.load(handle).get("wiki_dir") or "docs/wiki"
    except (OSError, ValueError):
        folder = "docs/wiki"
    ids = []
    for name in sorted(glob.glob(os.path.join(root, folder, "*.md"))):
        with open(name) as handle:
            text = re.sub(r"(?ms)^```.*?^```[^\n]*$", "", handle.read())
        if re.search(r"\n## (?:Requirements|Criteria)[ \t]*\n", text):
            part = re.split(r"\n## (?:Requirements|Criteria)[ \t]*\n", text, maxsplit=1)[1].split("\n## ", 1)[0]
            ids += re.findall(r"^- ([A-Z]{2,5}-\d+): \S", part, re.M)
    return ids


def criterion_rows(rows, key):
    return [row for row in rows.values() if key in (row["id"], row["goal"]) and row["category"] != "defect"]


def chosen(rows, target):
    if target in rows:
        return [rows[target]]
    if target == "land":
        return [row for row in rows.values() if row["level"] == "land"]
    if target == "nightly":
        return [row for row in rows.values() if row["level"] in ("land", "nightly")]
    sys.exit("REFUSED: no row or level called %s." % target)


def lines_of(root, name):
    return {line.split("\t")[0]: line.rstrip("\n") for line in open(path_of(root, name)) if line.strip() and line[0] != "#"} \
        if os.path.exists(path_of(root, name)) else {}


# regression.py red --off-platform (REG-10)
OFF_WINDOWS = re.compile(r"\b(win(dows)?(32|64)?|msys\d*|mingw\d*|cygwin)\b|\b(msys|mingw)\w*", re.I)
OFF_SHA = re.compile(r"^[0-9a-f]{7,40}$")


def off_record(root, row_id, runner, commit, today, read_rows, edit_rows):
    if row_id not in read_rows(root):
        sys.exit("REFUSED: no row %s. Fix: add it first." % row_id)
    runner = (runner or "").strip()
    if not runner or "\t" in runner or "\n" in runner:
        sys.exit("REFUSED: --runner names the machine that saw the row fail (linux-ci, a Linux session). Fix: pass --runner NAME.")
    if OFF_WINDOWS.search(runner):
        sys.exit("REFUSED: runner %s is Windows, where these rows only skip (exit 77) and a skip never sets seen red. "
                 "Fix: prove it red on a Linux or Mac runner." % runner)
    if not OFF_SHA.match(commit or "") or subprocess.run(["git", "cat-file", "-e", commit + "^{commit}"], cwd=root,
                                                     capture_output=True).returncode:
        sys.exit("REFUSED: %s is not a commit in this repo. Fix: git fetch, and pass the commit the red run used." % commit)
    day = today()
    edit_rows(root, lambda current: current[row_id].update(seen_red=day))
    path = path_of(root, "regression-red.tsv")
    kept = [line for line in (open(path).read().splitlines() if os.path.exists(path) else []) if line and line.split("\t")[0] != row_id]
    with open(path, "w", newline="\n") as out:
        out.write("\n".join(kept + ["\t".join((row_id, day, runner, commit))]) + "\n")
    print("SEEN RED %s on %s (proved on %s at %s)" % (row_id, day, runner, commit))
    owed_clear(root, row_id)
    return 0


OWED, OWED_LABEL = "regression-owed.tsv", "other-machine"


def owed_read(root):
    file = path_of(root, OWED)
    cells = [(line.rstrip("\n").split("\t") + [""] * 4)[:4] for line in (open(file) if os.path.exists(file) else []) if line.strip()]
    return {c[0]: c for c in cells}


def owed_clear(root, row_id, live=False):
    held = owed_read(root)
    mine = held.pop(row_id, None)
    if mine:
        with open(path_of(root, OWED), "w", newline="\n") as out:
            out.write("".join("\t".join(c) + "\n" for c in held.values()))
        if mine[3] and live:
            done = gh("issue", "close", mine[3], "--comment", "The red proof for %s is recorded; closing the to-do." % row_id)
            print("OWED CLEARED %s: %s" % (row_id, "closed " + mine[3] if getattr(done, "returncode", 0) == 0 else "could not close %s: close it by hand" % mine[3]))
        else:
            print("OWED CLEARED %s: close its issue" % row_id)


def unproven(root, rows, seen):
    held, out = owed_read(root), []
    for row in rows:
        mine = held.get(row["id"])
        if mine and not seen.match(row["seen_red"]):
            print("PENDING %s: red proof owed on %s since %s (to-do %s); never blocks" % (row["id"], mine[2], mine[1], mine[3] or "-"))
        elif not seen.match(row["seen_red"]):
            out.append(row["id"])
    return out


TOOL = r"(?:pnpm|node|npm|npx|yarn|corepack)"
MISSING = re.compile(r"\b%s: (?:command )?not found|^'?%s'? is not recognized as an internal|No module named '(?:fcntl|termios|pwd|grp|resource)'"
                     r"|spawn %s ENOENT" % (TOOL, TOOL, TOOL), re.M)


def unrunnable(code, text):
    return bool(code and MISSING.search(text or ""))


def owed_issue(root, key, ids, title, text, live, word="owed"):
    stone = ""
    for page in sorted(glob.glob(os.path.join(root, "docs", "wiki", "*.md"))):
        body = open(page, encoding="utf-8").read()
        found = re.search(r"^Milestone:\s*\S*/milestone/(\d+)", body, re.M)
        if found and any("(Tests#t-%s)" % one in body for one in ids):
            stone = found.group(1)
            break
    if not live:
        print("WOULD open a to-do issue (milestone %s) for %s" % (stone or "none", key))
        return ""
    mark = "<!-- loop-%s %s -->" % (word, key)
    listed = gh("issue", "list", "--label", OWED_LABEL, "--state", "open", "--limit", str(ISSUE_LIMIT), "--json", "url,body")
    for item in [] if listed.returncode else json.loads(listed.stdout or "[]"):
        if mark in item.get("body", ""):
            return item["url"]
    name = gh("api", "repos/{owner}/{repo}/milestones/" + stone, "--jq", ".title").stdout.strip() if stone else ""
    gh("label", "create", OWED_LABEL, "--force", "--description", "A step only another machine can do")
    made = gh("issue", "create", "--title", title, "--label", OWED_LABEL, *(("--milestone", name) if name else ()), body=mark + "\n" + text)
    return made.stdout.strip().splitlines()[-1] if made.returncode == 0 and made.stdout.strip() else ""


def notrun_todo(root, slug, ids, live):
    return owed_issue(root, slug, ids, "To do on another machine: run %d rows of %s" % (len(ids), slug),
                      "Goal `%s`: run these rows with `regression.py run ID`, then close this. It never blocks the goal.\n\n%s\n" % (
                          slug, "\n".join("- `%s`" % one for one in ids)), live, "notrun")


def owed_record(root, args, today, read_rows):
    rows, runner, row_id = read_rows(root), (args.runner or "").strip(), args.id
    live = args.live or bool(os.environ.get("GH_TOKEN") or os.environ.get("GITHUB_TOKEN"))
    if row_id not in rows:
        sys.exit("REFUSED: no row %s. Fix: add it first." % row_id)
    if not runner or "\t" in runner or "\n" in runner:
        sys.exit("REFUSED: --runner names the machine that owes the proof. Fix: pass --runner NAME.")
    if re.match(r"\d{4}-\d{2}-\d{2}$", rows[row_id]["seen_red"]):
        sys.exit("REFUSED: %s is already seen failing, so nothing is owed." % row_id)
    if row_id not in owed_read(root):
        issue = owed_issue(root, row_id, [row_id], "To do on %s: prove %s fails" % (runner, row_id),
                           "Row `%s` skips here: red proof owed from %s. There run `regression.py red %s --off-platform --runner %s --commit SHA`, "
                           "then close this. It never blocks.\n" % (row_id, runner, row_id, runner), live)
        with open(path_of(root, OWED), "a", newline="\n") as out:
            out.write("\t".join((row_id, today(), runner, issue)) + "\n")
        print("OWED %s: red proof owed on %s (to-do %s). The goal goes on." % (row_id, runner, issue or "not opened"))
    return 0
