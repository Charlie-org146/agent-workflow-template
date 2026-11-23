#!/usr/bin/env python3
"""DEL-22.4's fault side, split out of planlevel.py to keep every script under 19,000 bytes: reading the planning tool's own guard log, the frozen
release brief's goal list, the regex mask, and the previewed issue block with its live filing (main's Actions run only)."""
import hashlib
import json
import os
import re
import subprocess

FAULT_CODES = ("snapshot",)
PINNED = {"id": "o807", "release": "v1.1.0"}
PAGE = "Delivery"  # the page DEL-22 sits on; its label is feature:Delivery and its milestone Backlog: Delivery


def pl():
    import planlevel
    return planlevel


def config(top=None):
    """plan_levels from origin/main's committed config (the base is main), after a bounded fetch into the remote-tracking ref (GRD-4): a locally moved ref, the
    working tree and a worker-named base are never read. A fetch that fails (no network, a lost lock race) still reads the last fetched ref, so the levels do not
    change, but marks _fetch_failed and the fallback is off; a config that cannot be read marks _config_unreadable and gives the defaults."""
    import subprocess
    try:
        lost = subprocess.run(["git", "fetch", "-q", "origin", "+refs/heads/main:refs/remotes/origin/main"], cwd=top, capture_output=True, timeout=20).returncode
    except (OSError, subprocess.SubprocessError):
        lost = 1
    try:
        found = json.loads(pl().git("show", "origin/main:.loop/config.json", cwd=top)).get("plan_levels")
        out = dict(found) if isinstance(found, dict) else {}
    except (OSError, ValueError, subprocess.SubprocessError):
        out = {"_config_unreadable": True}
    return dict(out, _fetch_failed=True) if lost else out


def brief_goals(release, top=None, why=None, slug=None):
    """The goals of the FROZEN release brief, by implement-v110's own brief.py (TD1078: one brief format, no parser of mine). Everything is read from
    origin/main into a temp tree (the brief.py itself, the release brief, the task briefs), so a worker's own copy of any of them is never used.
    A goal is listed when the frozen release brief (its sha256 check passes) names a task whose frozen task brief's Goals bullet names it. Any failure
    (brief.py not on main yet, a missing, unfrozen, unverified or changed brief, an error) gives [] and the fallback stays off; `why`, a list, receives the
    reason. Importing brief.py sets GIT_TERMINAL_PROMPT=0 in this process, which fit.py already sets at its top, so nothing new."""
    why = [] if why is None else why
    import importlib.util
    import tempfile
    version = str(release).lstrip("v")
    if not re.fullmatch(r"\d+(\.\d+){1,3}", version):
        why.append("the approval's release %r is not a version name" % release)
        return []
    git = pl().git
    try:
        with tempfile.TemporaryDirectory() as tmp:
            def put(rel):
                text = git("show", "origin/main:" + rel, cwd=top)
                if not text:
                    return False
                os.makedirs(os.path.dirname(os.path.join(tmp, rel)), exist_ok=True)
                with open(os.path.join(tmp, rel), "w", encoding="utf-8") as handle:
                    handle.write(text)
                return True
            if not put("skills/workflow-release/scripts/brief.py"):
                why.append("brief.py is not on origin/main")
                return []
            if not put("docs/release-brief-%s.md" % version):
                why.append("no docs/release-brief-%s.md on origin/main (brief.py's own name: no 'v')" % version)
                return []
            for rel in git("ls-tree", "--name-only", "origin/main", ".loop/tasks/", ".loop/sources/", cwd=top).split():
                put(rel)
            spec = importlib.util.spec_from_file_location("brief_main", os.path.join(tmp, "skills/workflow-release/scripts/brief.py"))
            brief = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(brief)
            seen = brief.frozen(brief.read(os.path.join(tmp, "docs/release-brief-%s.md" % version)))  # None, or ("", "", "") for a changed brief
            if not seen or seen == ("", "", ""):  # a changed brief is refused here
                why.append("the release brief is not frozen, or its words changed after the freeze (its sha256 does not match)")
                return []
            named = brief.release_tasks(tmp, version)
            if not named:
                why.append("the frozen release brief lists no tasks")
                return []
            tasks = brief.briefs(tmp, "task")
            out = []
            for name in named:
                text = tasks.get(name)
                if not text:
                    why.append("task %s, named by the frozen release brief, has no brief file on origin/main" % name)
                    continue
                got = brief.frozen(text, tmp)
                if got and got != ("", "", "") and got[2] != "unverified":  # a Source-form brief counts only when its .loop/sources file verifies
                    out += brief.names(brief.field(text, "Goals"))
                elif slug in brief.names(brief.field(text, "Goals")):  # only a task that names this goal can be the reason it is off
                    why.append("task %s names this goal but is not frozen, changed after its freeze, or its source does not verify" % name)
            return out
    except (Exception, SystemExit) as err:  # SystemExit from brief.refuse() too; an interrupt is not swallowed
        why.append("brief.py failed: %s" % type(err).__name__)
        return []


def fallback_check(cfg, slug, top=None):
    """(on, why): the decision and its reason from ONE read of origin/main (so they cannot disagree, and the briefs are copied once)."""
    if isinstance(cfg, dict) and cfg.get("_fetch_failed"):
        return False, "could not fetch origin/main"
    if isinstance(cfg, dict) and cfg.get("_config_unreadable"):
        return False, "origin/main has no readable .loop/config.json"
    held = cfg.get("fallback_approved") if isinstance(cfg, dict) else None
    if not (isinstance(held, dict) and held.get("id") and held.get("release")):
        return False, "no plan_levels.fallback_approved on origin/main (the owner's approval record is not set there)"
    if held != PINNED:  # the fallback is pinned to its approval and its release: any other record is off
        return False, "plan_levels.fallback_approved is not the approval this fallback is pinned to"
    why = []
    if slug in brief_goals(held["release"], top, why, slug):
        return True, ""
    return False, why[0] if why else "this goal is in no task's Goals of the frozen brief"


def fallback_on(cfg, slug, top=None):
    """The owner's one-time approval (DEL-22.4: "you approve it once in the release's brief"): on only for a goal NAMED through the frozen brief of the
    approval's release, read from origin/main by brief.py's own readers (TD1078). It merges after implement-v110; until brief.py is on main it is off."""
    return fallback_check(cfg, slug, top)[0]


_N = r"[^\\/\s:;,)\"}\]']+(?:'[^\\/\s:;,)\"}\]']+)*"  # one name token (an apostrophe only between letters)
HOME = re.compile(r"(?i)(?:file://)?(?:/(?:Users|home)/|[A-Z]:[\\/]{1,2}(?:Users|home)[\\/]{1,2}|\\\\[^\\/\s]+[\\/]{1,2}(?:Users|home)[\\/]{1,2})(?:" + _N + r"(?: " + _N + r"){1,2}(?=[\\/])|" + _N + r")(?:[\\/][^\s\"')}\]]*)?")  # a home path, with its whole tail


def mask(text):
    """The text with every flagged private word (the repo's own list, private.patterns()), home paths, other paths, emails, URLs other than a plain
    github.com one, and tokens each replaced by a mark that says what it was. None when the private list is broken: the caller stores no quote then."""
    import private
    import urllib.parse
    import uuid
    state, found, _ = private.patterns()
    if state == "broken":
        return None
    for _, rx in found:
        text = rx.sub("<masked: private word>", text)
    keep, tag, tok = [], uuid.uuid4().hex[:12], r"\b(?:[A-Za-z0-9_\-]{24,}|gh[pousr]_[A-Za-z0-9]+|sk-[A-Za-z0-9]+)\b"

    def url(m):
        got = urllib.parse.urlsplit(m.group(0))
        if got.scheme in ("http", "https") and got.netloc == "github.com" and not got.query:
            keep.append(re.sub(tok, "<masked: token>", m.group(0)))
            return "\x00%s\x00%d\x00" % (tag, len(keep) - 1)
        return "<masked: url>"
    text = re.sub(r"https?://[^\s\"')\]}>]+", url, text)
    text = HOME.sub("<masked: path>", text)
    text = re.sub(r"(?<![\w/])~[\w.-]*(?:/[\w.\-@]+)+", "<masked: path>", text)  # a tilde path
    text = re.sub(r"(?<![\w.\-@])(?:/[\w.\-@]+){2,}", "<masked: path>", text)  # another absolute path
    text = re.sub(r"\b[\w.+-]+@[\w-]+\.[\w.-]+\b", "<masked: email>", text)
    text = re.sub(tok, "<masked: token>", text)
    return re.sub(r"\x00%s\x00(\d+)\x00" % tag, lambda m: keep[int(m.group(1))], text)


def quote_of(row):
    """A guard-log row as JSON text with each STRING VALUE masked before it is dumped, or None when the private list is broken."""
    def walk(value):
        if isinstance(value, str):
            done = mask(value)
            if done is None:
                raise ValueError("broken")
            return done
        if isinstance(value, dict):
            return {walk(k): walk(v) for k, v in value.items()}
        return [walk(v) for v in value] if isinstance(value, list) else value
    try:
        return json.dumps(walk(row), sort_keys=True, ensure_ascii=False)
    except ValueError:
        return None


def faults(cfg, held):
    """New guard-log entries since the last ask: the planning tool's OWN denial that names its fallback. Agent text is never read."""
    path = cfg.get("guard_log")
    if not isinstance(path, str):  # the planning tool keeps its own log in a dot-folder of the home: analytics/autoplan-guard.jsonl
        import glob
        found = sorted(glob.glob(os.path.expanduser("~/.*/analytics/autoplan-guard.jsonl")))
        path = found[0] if found else None
    if not path or not os.path.isfile(path):
        return [], held.get("log_pos", 0)
    codes = cfg.get("fault_codes") if isinstance(cfg.get("fault_codes"), list) else list(FAULT_CODES)
    found, pos = [], held.get("log_pos")
    with open(path, "rb") as handle:
        data = handle.read()
    start = len(data) if pos is None else min(pos, len(data))
    for raw in data[start:].splitlines():
        try:
            row = json.loads(raw)
        except ValueError:
            continue
        if isinstance(row, dict) and row.get("decision") == "deny" and row.get("disposition") == "fallback" and row.get("code") in codes:
            found.append(row)
    return found, len(data)


def block(slug):
    found = pl().sidecar(slug).get("issue")
    return "<!-- plan-fault-issue %s -->" % json.dumps(found, sort_keys=True) if found else ""


def issue(slug, live, body=None):
    """Preview: print the block. Live (main's Actions run only): the block comes from a pull request body, but only its goal slug and key are taken, each
    checked against a fixed shape; the title and text are built here, and the issue is found again by the key in its TITLE across open and closed issues."""
    if body is None:
        print(block(slug) or "no issue was previewed for %s" % slug)
        return 0
    found = re.search(r"<!-- plan-fault-issue (\{.*?\}) -->", body)
    if not found or not live:
        print("no issue block in the body" if not found else "PREVIEW only without --live")
        return 0
    try:
        held = json.loads(found.group(1))
    except ValueError:
        print("the block is not JSON; nothing filed")
        return 0
    if not (re.fullmatch(r"[a-z0-9][a-z0-9-]{0,60}", str(held.get("goal"))) and re.fullmatch(r"[0-9a-f]{12}", str(held.get("key")))):
        print("the block's goal or key has the wrong shape; nothing filed")
        return 0
    title = "Planning tool fault on goal %s [%s]" % (held["goal"], held["key"])
    text = "The planning tool's own guard denied a plan and named its fallback. Goal: %s. The quote is in the goal's record, not here." % held["goal"]
    extra = ["--label", "feature:" + PAGE, "--milestone", "Backlog: " + PAGE]  # the feature's own label and Backlog milestone (HLT-4)
    try:
        seen = subprocess.run(["gh", "issue", "list", "--state", "all", "--search", held["key"] + " in:title", "--json", "number"] + extra[:2], capture_output=True, text=True, timeout=60)
        if seen.returncode:  # a failed lookup is not "no such issue": never create on a guess
            print("issue NOT filed (the lookup failed: %s); nothing was created or retried" % (seen.stderr.strip().splitlines() or ["no message"])[0][:200])
            return 1
        if json.loads(seen.stdout or "[]"):
            print("already filed (key %s)" % held["key"])
            return 0
        done = subprocess.run(["gh", "issue", "create", "--title", title, "--body", text] + extra, capture_output=True, text=True, timeout=60)
        if done.returncode:  # the label or milestone may be missing: fail the job so the missing issue is seen, and never retry
            print("issue NOT filed (gh said: %s); nothing was retried" % (done.stderr.strip().splitlines() or ["no message"])[0][:200])
            return 1
        print("issue filed")
    except (OSError, ValueError, subprocess.SubprocessError):
        print("issue NOT filed (gh did not run); nothing was retried")
        return 1
    return 0
