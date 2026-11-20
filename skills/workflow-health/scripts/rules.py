"""Freshness, Tests, Adoption, Security, Size, Performance and Hygiene rules, plus principle-map. Read-only; dates are days, so
one day's runs print the same lines."""
import datetime
import glob
import importlib.util
import json
import os
import re
import subprocess
import sys
import time

import issues as IS
import report as _report
from defects import LINE, behind, pages, row, setting, table, wiki


os.environ.update(GIT_TERMINAL_PROMPT="0", GH_PROMPT_DISABLED="1", GIT_EDITOR="true", GIT_ASKPASS="true", SSH_ASKPASS="true")


def today():
    return datetime.date.today()


def days_since(text):
    try:
        return (today() - datetime.date.fromisoformat(str(text)[:10])).days
    except ValueError:
        return None


def last_runs(root):
    """{row id: (status, date)} from .loop/regression-runs.tsv."""
    out = {}
    try:
        with open(os.path.join(root, ".loop", "regression-runs.tsv")) as handle:
            for line in handle:
                cells = line.rstrip("\n").split("\t")
                if line.strip() and not line.startswith("#") and len(cells) >= 3:
                    out[cells[0]] = (cells[1], cells[2])
    except OSError:
        pass
    return out


def nightly(root):
    ids = [item["id"] for item in table(root) if item["level"] == "nightly"]
    if not ids:
        return [row("INFO", "freshness", "nightly", "nightly", "no nightly rows")]
    runs = last_runs(root)
    dates = [runs[key][1] for key in ids if key in runs]
    newest = max(dates) if dates else ""
    age = days_since(newest) if newest else None
    if age is None or age > 1:
        return [row("WARN", "freshness", "nightly", "nightly", "the newest nightly run is %s" % (newest or "missing"),
                    "check that the nightly workflow runs", "nightly")]
    return []


def git(root, *args):
    done = subprocess.run(["git", *args], cwd=root, capture_output=True, text=True)
    return done.stdout.strip() if done.returncode == 0 else ""


def unreleased(root):
    tag = git(root, "describe", "--tags", "--abbrev=0", "--match", "v*")
    if not tag:
        return [row("INFO", "freshness", "release", "unreleased", "no v* release tag")]
    dates = git(root, "log", "--format=%cs", "--reverse", tag + "..HEAD").splitlines()
    age = days_since(dates[0]) if dates else None
    if age is not None and age > 3:
        return [row("WARN", "freshness", tag, "unreleased", "%d commits since %s, the oldest from %s" % (len(dates), tag, dates[0]),
                    "cut a release (workflow-release)", tag)]
    return []


def finding_age(root):
    found, why = IS.fetch(root, "health")
    if found is None:
        return [row("INFO", "freshness", "findings", "finding-age", why)]
    return [row("WARN", "freshness", "#%d" % i["number"], "finding-age", "open since %s" % str(i.get("created_at"))[:10],
                "fix it or close it with triage", "#%d" % i["number"])
            for i in found if i.get("state") == "open" and IS.is_health(i) and (days_since(i.get("created_at")) or 0) > 30]


def skipped(root):
    return [row("WARN", "tests", key, "skipped", "skipped since %s" % date, "make it run again, or retire it", key)
            for key, (status, date) in sorted(last_runs(root).items())
            if status == "SKIPPED" and (days_since(date) or 0) > 7]


def network(root):
    hits = re.compile(r"\b(curl|wget)\s|https?://")
    return [row("WARN", "tests", item["id"], "network", "its command reaches the network", "use a stand-in (dev/toy/fakegh)", item["id"])
            for item in table(root) if item["level"] == "land" and hits.search(item["command"]) and "fakegh" not in item["command"]]


def config(root):
    path = os.path.join(root, ".loop", "config.json")
    try:
        with open(path) as handle:
            found = json.load(handle)
    except (OSError, ValueError) as error:
        return [row("FAIL", "adoption", ".loop/config.json", "config", "can't be read: %s" % str(error)[:80], "fix the JSON")]
    if not isinstance(found, dict) or not found.get("base"):
        return [row("FAIL", "adoption", ".loop/config.json", "config", "has no base branch", "set base (workflow-setup)")]
    return []


def checks_run_tests(root):
    if not os.path.exists(os.path.join(root, ".github", "workflows", "regression.yml")):
        return []
    if not any(item["level"] == "land" for item in table(root)):
        return [row("WARN", "adoption", "regression.yml", "checks-run-tests", "the regression workflow has no land row to run",
                    "add a land row (regression.py add)", "regression.yml")]
    return []


def template_version(root):
    try:
        version = open(os.path.join(root, "VERSION")).read().strip()
        head = re.search(r"^## v(\S+)", open(os.path.join(root, "CHANGELOG.md")).read(), re.M)
    except OSError:
        return [row("INFO", "adoption", "VERSION", "template-version", "no VERSION or CHANGELOG.md")]
    if head and head.group(1) != version:
        return [row("WARN", "adoption", "VERSION", "template-version", "VERSION %s, newest CHANGELOG heading v%s" % (version, head.group(1)),
                    "release again, or fix VERSION", "VERSION")]
    return []


def scheduled(root):
    """The regression workflow is scheduled unless regression_runs is mac."""
    out, flows = [], os.path.join(root, ".github", "workflows")
    try:
        mac = json.load(open(os.path.join(root, ".loop", "config.json"))).get("regression_runs") == "mac"
    except (OSError, ValueError, AttributeError):
        mac = False
    text = open(os.path.join(flows, "regression.yml")).read() if os.path.exists(os.path.join(flows, "regression.yml")) else ""
    if "schedule:" not in text and not mac:
        out.append(row("WARN", "adoption", "regression.yml", "scheduled", "missing" if not text else "has no schedule",
                       "write it (workflow-regression workflow); setup records regression_runs", "regression.yml"))
    if os.path.exists(os.path.join(flows, "health.yml")):
        out.append(row("WARN", "adoption", "health.yml", "scheduled", "has no job: health runs on the Mac",
                       "git rm .github/workflows/health.yml", "health.yml"))
    return out


def no_fit(root):
    try:
        text = open(os.path.join(root, ".loop", "findings.md")).read()
    except OSError:
        return []
    found = [(re.match(r"^- \[adoption\] ([\w-]+): (.+?)\. Fix: (.+?)\s*$", l), l) for l in text.splitlines()]
    return [row("WARN", "adoption", m.group(1), "no-fit", "did not fit when adopted: " + m.group(2), m.group(3), m.group(2))
            for m, line in found if m and not line.rstrip().endswith("[closed]")]


POINTER = re.compile(r"^In \S+, fast-forward to origin/main, then read \S+'s Runbook section \S+ and follow it exactly\.$")


def prompt_pointer(root):
    """prompt-pointer: a WARN for a scheduled-task prompt with a line beyond the Runbook pointer."""
    try:
        items = json.load(open(os.path.join(root, ".loop", "config.json"))).get("automation") or []
    except (OSError, ValueError, AttributeError):
        return []
    base, out = os.environ.get("LOOP_SCHEDULED_TASKS_DIR") or os.path.expanduser("~/.claude/scheduled-tasks"), []
    tasks = {str(e.get("runs")).partition(":")[2] for e in items if isinstance(e, dict) and str(e.get("runs")).partition(":")[0] in ("claude", "mac")}
    for task in sorted(tasks - {""}):
        try:
            text = open(os.path.join(base, task, "SKILL.md"), encoding="utf-8").read()
        except OSError:
            continue
        body = re.sub(r"\A---\n.*?\n---\n", "", text.replace("\r\n", "\n"), flags=re.S)
        extra = [x for x in (line.strip() for line in body.splitlines()) if x and not POINTER.match(x)]
        if extra:
            out.append(row("WARN", "adoption", task, "prompt-pointer", "the scheduled prompt holds %d line(s) beyond the Runbook pointer, the first: %s" % (len(extra), extra[0][:60]),
                           "replace its prompt with the lines docs.py prompts prints; the steps live in the Runbook", task))
    return out


def milestones(root):
    if "github.com" not in (git_raw(root, "remote", "get-url", "origin") or ""):
        return []
    import milestone
    try:
        have = set(json.loads(os.environ["LOOP_BACKLOG_MILESTONES"])) if "LOOP_BACKLOG_MILESTONES" in os.environ else set(milestone.held(root))
    except (SystemExit, ValueError, TypeError) as error:
        return [row("INFO", "adoption", "milestones", "milestones", "not checked: %s" % str(error)[:90], "gh auth login")]
    return [row("WARN", "adoption", title, "milestones", "this standing milestone is missing", "milestone.py backlog --live (setup makes them)", title)
            for title in milestone.standing(root) if title not in have]


def machine(root):
    tool = os.path.join(os.path.dirname(os.path.realpath(__file__)), "..", "..", "..", "dev", "machine.py")
    if os.environ.get("CI") or not os.path.isdir(os.path.expanduser("~/.claude/skills/workflow-health")) or not os.path.exists(tool):
        return []
    try:
        text = subprocess.run([sys.executable, tool, "check", "--repo", root], capture_output=True, text=True, timeout=30).stdout
    except (OSError, subprocess.SubprocessError):
        return []
    return [row("WARN", "adoption", g, "machine", w, f, g) for g, w, f in re.findall(r"^GAP ([^:]+): (.*?) -> (.*)$", text, re.M)]


FUNCTIONS = {"nightly": nightly, "unreleased": unreleased, "finding-age": finding_age, "skipped": skipped,
             "network": network, "config": config, "checks-run-tests": checks_run_tests,
             "template-version": lambda root: template_version(root) + behind(root), "scheduled": scheduled, "machine": machine, "no-fit": no_fit, "agent-tools": _report.agent_tools, "prompt-pointer": prompt_pointer,
             "milestones": milestones}




SKILL_LINES = 150
CHECK_SECONDS = 60


def git_raw(root, *args):
    done = subprocess.run(["git", *args], cwd=root, capture_output=True, text=True)
    return done.stdout if done.returncode in (0, 1) else None


def patterns():
    found = []
    for path in dict.fromkeys(os.path.expanduser(p) for p in ("~/.workflow-loop/flow.json", os.environ.get("LOOP_FLOW") or "")):
        try:
            with open(path) as handle:
                items = json.load(handle).get("leak_patterns") or []
        except (OSError, ValueError, AttributeError):
            continue
        found += [p for p in items if isinstance(p, str) and p.strip()]
    return list(dict.fromkeys(found))


def private(root):
    wanted = patterns()
    if not wanted:
        return [row("INFO", "security", "patterns", "private", "not applicable here: no leak_patterns set in the private flow file")]
    out = []
    for number, pattern in enumerate(wanted, 1):
        hits = git_raw(root, "grep", "-n", "-I", "-E", "-e", pattern, "--", ".", ":(exclude).git")
        if hits is None:  # a bad pattern: never a silent pass
            out.append(row("UNREAD", "security", "pattern %d" % number, "private", "leak pattern %d is not a valid regex" % number,
                           "fix leak_patterns in the private flow file"))
            continue
        for line in hits.splitlines():
            where = ":".join(line.split(":", 2)[:2])  # never the text
            out.append(row("FAIL", "security", where, "private", "matches leak pattern %d" % number,
                           "remove it from the file and from history", where))
    return out


def scan_hook(root):
    hooks = (git_raw(root, "config", "core.hooksPath") or "").strip()
    common = (git_raw(root, "rev-parse", "--git-common-dir") or ".git").strip()
    path = os.path.join(root, hooks, "pre-commit") if hooks else os.path.join(root, common, "hooks", "pre-commit")
    if os.path.isfile(path) and os.access(path, os.X_OK):
        return []
    if os.environ.get("CI") or os.environ.get("GITHUB_ACTIONS"):
        return [row("INFO", "security", "pre-commit", "scan-hook", "not applicable here: a fresh clone has no hooks")]
    return [row("WARN", "security", "pre-commit", "scan-hook", "no commit scan hook is installed",
                "install it (workflow-setup)", "pre-commit")]


def workflow_permissions(root):
    out = []
    for path in sorted(glob.glob(os.path.join(root, ".github", "workflows", "*.y*ml"))):
        text = open(path, errors="replace").read()
        if not any(line.startswith("permissions:") for line in text.splitlines()):
            name = os.path.relpath(path, root)
            out.append(row("WARN", "security", name, "workflow-permissions", "no top-level permissions:",
                           "declare the least permissions it needs", name))
    return out


def skill_lines(root):
    out, cap = [], setting(root, "health_skill_lines", SKILL_LINES)
    for path in sorted(glob.glob(os.path.join(root, "skills", "*", "SKILL.md"))):
        with open(path, "rb") as handle:
            count = len(handle.read().replace(b"\r\n", b"\n").splitlines())
        if count >= cap:
            name = os.path.relpath(path, root)
            out.append(row("FAIL", "size", name, "skill-lines", "%d lines, %d or more" % (count, cap),
                           "move detail into references/", name))
    return out


def requirements_per_page(root):
    try:
        with open(os.path.join(root, ".loop", "config.json")) as handle:
            limit = int(json.load(handle).get("criteria_max", 10))
    except (OSError, ValueError, TypeError, AttributeError):
        limit = 10
    return [row("FAIL", "size", name, "requirements-per-page", "%d requirements, over %d" % (len(LINE.findall(text)), limit),
                "merge requirements, or raise criteria_max", name)
            for name, text in pages(root).items() if len(LINE.findall(text)) > limit]


def check_time(root):
    start = float(os.environ.get("LOOP_HEALTH_T0") or 0) or (getattr(sys.modules.get("__main__"), "T0", [None]) or [None])[0]
    if not start:
        return [row("INFO", "performance", "check", "check-time", "not measured outside health.py check")]
    if time.time() - start > CHECK_SECONDS:
        return [row("WARN", "performance", "check", "check-time", "the check took over %d seconds" % CHECK_SECONDS,
                    "find the slow rule (health.py check --group NAME)", "check")]
    return []


def idle_sessions(root):
    common = (git_raw(root, "rev-parse", "--git-common-dir") or ".git").strip()
    loop = os.path.join(root, common, "loop")
    try:
        with open(os.path.join(loop, "session-pool.json")) as handle:
            pool = json.load(handle)
    except (OSError, ValueError):
        return [row("INFO", "hygiene", "sessions", "idle-sessions", "not applicable here: no session pool")]
    out = []
    for sid, item in sorted((pool or {}).items()):
        if not isinstance(item, dict) or item.get("state") != "busy" or not item.get("slug"):
            continue
        try:
            with open(os.path.join(loop, "runs", item["slug"] + ".json")) as handle:
                status = json.load(handle).get("status")
        except (OSError, ValueError, AttributeError):
            continue
        if status in ("done", "merged"):
            out.append(row("WARN", "hygiene", sid, "idle-sessions", "busy with %s, which is %s" % (item["slug"], status),
                           "sessions.py free %s" % item["slug"], sid))
    return out


ETA = ("eta-missing", "eta-extended", "eta-overrun", "auto-safety", "auto-record")
HONEST = ("eta-unmarked", "eta-missed", "eta-rate", "statement-wrong")  # HLT-4


def eta(root, name):
    path = os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir, os.pardir, "workflow-monitoring", "scripts", "auto.py")
    if not os.path.exists(path):
        return [row("UNREAD", "hygiene", "eta", name, "workflow-monitoring is not installed beside this skill")]
    sys.path.insert(0, os.path.dirname(path))
    try:
        spec = importlib.util.spec_from_file_location("health_eta", path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
    finally:
        sys.path.pop(0)
    if name in HONEST:
        import file as filing
        return filing.honesty(root, name, module)
    return [row(level, "hygiene", text.split()[0], name, text, "sessions.py owner-words with --ids full-auto-rule, or goal.py set with an owner record")
            for rule, level, text in module.eta_rows(root) + module.auto_rows(root) if rule == name]


GUARD_FUNCTIONS = {"private": private, "scan-hook": scan_hook, "workflow-permissions": workflow_permissions,
             "skill-lines": skill_lines, "requirements-per-page": requirements_per_page, "check-time": check_time,
             "idle-sessions": idle_sessions}


GUARD_FUNCTIONS.update({name: (lambda root, name=name: eta(root, name)) for name in ETA + HONEST})
FUNCTIONS.update(GUARD_FUNCTIONS)


def pmap(root):
    try:
        text = open(os.path.join(wiki(root), "Principles.md"), errors="replace").read()
    except OSError:
        return {}
    return {n: re.findall(r"^\| \[([A-Z]+-\d+) ", b, re.M) for n, b in re.findall(r"^## (\d)\. .*\n((?:(?!## ).*\n?)*)", text, re.M)}


def reviewed(root, mark="Reviewed"):
    return {k for t in pages(root).values() for k in re.findall(r"^- ([A-Z]+-\d+): \*\*" + mark, t, re.M)}


def principle_map(root):
    plan, done = pmap(root), reviewed(root)
    under = {i for ids in plan.values() for i in ids}
    bad = lambda i, why, fix: row("FAIL", "requirements", i, "principle-map", why, fix)
    return ([bad(i, "%s is Reviewed under no principle" % i, "add it to Principles.md") for i in sorted(done - under)] * bool(plan)
            + [bad(i, "Principles.md lists %s, no live requirement (stale)" % i, "regenerate it") for i in sorted(under - reviewed(root, "[A-Za-z]"))]
            + [bad("principle " + n, "principle %s has no Reviewed requirement" % n, "add one") for n, ids in sorted(plan.items()) if not done & set(ids)])


def principle_review(root):
    plan, done, hit = pmap(root), reviewed(root), {}
    for item in table(root):
        hit[item["goal"].strip()] = hit.get(item["goal"].strip(), 0) + 1
    return ["PRINCIPLES: Reviewed requirements, tests and weak spots per principle"] + ["principle %s: %s" % (n, ", ".join(
        "%s (%d tests)%s" % (i, hit.get(i, 0), "" if hit.get(i) else " WEAK") for i in ids if i in done) or "NONE") for n, ids in sorted(plan.items())]


def f_principle_map(root):
    for name, body in (("Principles", "## 1. A\n| [AB-1 x](One) |\n## 2. B\n"), ("One", "## Requirements\n- AB-1: **Reviewed 2026-11-19** a.\n- AB-2: **Reviewed 2026-11-19** b.\n")):
        os.makedirs(os.path.join(root, "docs", "wiki"), exist_ok=True)
        open(os.path.join(root, "docs", "wiki", name + ".md"), "w").write("# %s\n\n%s" % (name, body))


CONTROLS = {"principle-map": ("requirements", "principle-map", f_principle_map)}
FUNCTIONS["principle-map"] = principle_map
