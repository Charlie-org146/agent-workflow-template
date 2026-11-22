#!/usr/bin/env python3
"""DEL-23 tasks and DOC-28 release briefs: frozen briefs, the one task list, and the gates that read them.

  brief.py freeze task|release NAME --owner-record ID   freeze .loop/tasks/NAME.md or docs/release-brief-NAME.md
  brief.py check                                         every frozen brief still hashes to its freeze line
  brief.py tasks                                         the one list: name, state, goals, ETA
  brief.py finish NAME --met N,N                         mark a task done (every goal merged, every done-when met)
  brief.py gate merge|bump|cut ...                       the refusals the release scripts call; exit 1 refuses

A task brief is `.loop/tasks/<name>.md`: Feature:, Purpose:, optional Needs: and Replaces:, Kind: feature|fix, then
`## Done when` numbered lines. A release brief is `docs/release-brief-<version>.md`: `## Tasks` numbered with task names
in order. Freezing appends one last line `Frozen: <sha256 of everything above> <record id> <date>`; a changed word
fails check. Every refusal prints what, fix and a code (BRF-n) and exits 1; it never prints the owner's words.
"""
import argparse
import datetime
import glob
import hashlib
import json
import os
import re
import subprocess
import sys

os.environ.setdefault("GIT_TERMINAL_PROMPT", "0")  # DEL-10: git never waits on a prompt
NAME = re.compile(r"^[a-z0-9][a-z0-9-]*$")
VERSION = re.compile(r"^\d+(\.\d+){1,3}$")
FROZEN = re.compile(r"^Frozen: ([0-9a-f]{64}) (\S+) (\S+)$", re.M)
CODES = {"BRF-1": "bad name", "BRF-2": "no typed record", "BRF-3": "brief missing or not frozen", "BRF-4": "brief changed after the freeze",
         "BRF-5": "task not startable or not done", "BRF-6": "release gate", "BRF-7": "private value in text"}


def refuse(code, what, fix):
    print("REFUSED %s: %s. Fix: %s" % (code, what, fix), file=sys.stderr)
    sys.exit(1)


def top():
    return subprocess.run(["git", "rev-parse", "--show-toplevel"], capture_output=True, text=True).stdout.strip() or os.getcwd()


def common(root):
    got = subprocess.run(["git", "-C", root, "rev-parse", "--git-common-dir"], capture_output=True, text=True).stdout.strip()
    return os.path.abspath(os.path.join(root, got))


def path_of(root, kind, name):
    (VERSION if kind == "release" else NAME).match(name) or refuse("BRF-1", "%r is not a name" % name, "use lowercase letters, digits and dashes")
    return os.path.join(root, ".loop", "tasks", name + ".md") if kind == "task" else os.path.join(root, "docs", "release-brief-%s.md" % name)


def read(path):
    try:
        return open(path, encoding="utf-8").read()
    except OSError:
        return ""


def frozen(text):
    """(body, record, date) of a frozen brief, or None."""
    found = FROZEN.search(text)
    if not found:
        return None
    body = text[:found.start()]
    return (body, found[2], found[3]) if hashlib.sha256(body.encode()).hexdigest() == found[1] else ("", "", "")


def field(text, key):
    found = re.search(r"^%s:\s*(.*)$" % key, text, re.M)
    return found[1].strip() if found else ""


def names(text):
    return [x.strip() for x in re.split(r"[,\s]+", text) if x.strip()]


def scan(text):
    """A private value in text (the home folder, an email address, or a name on the private list), or ''."""
    if re.search(r"[\w.+-]+@[\w-]+\.[\w.-]+", text) or (len(os.path.expanduser("~")) > 1 and os.path.expanduser("~") in text):
        return "an email address or the home folder"
    here = os.path.dirname(os.path.abspath(__file__))
    try:
        sys.path.insert(0, os.path.join(here, "..", "..", "workflow-delivery", "scripts"))
        import private
        got = private.scan(top(), None, texts={"brief": text})
        return "a private name" if got.get("state") in ("hit", "broken") else ""
    except Exception:
        return ""


def ledger_row(root, record):
    log = os.path.join(common(root), "loop", "owner-words.tsv")
    try:
        return next((r for r in (x.rstrip("\n").split("\t") for x in open(log, encoding="utf-8")) if len(r) == 5 and r[0] == record), None)
    except OSError:
        return None


def freeze(root, kind, name, record):
    path = path_of(root, kind, name)
    text = read(path)
    text or refuse("BRF-3", "no brief at %s" % os.path.relpath(path, root), "write it first")
    frozen(text) and refuse("BRF-4", "%s is already frozen" % name, "a change is a new task that replaces this one: brief.py freeze task NEW --replaces %s" % name)
    row = ledger_row(root, record)
    if not row or row[4].split(",") != [name] or row[2] not in ("operation", "owner"):
        refuse("BRF-2", "no owner record naming exactly %s (record %s)" % (name, record or "none"),
               "the owner types one decision: \"Freeze %s? Recommended: yes\"; the operation session records it with sessions.py owner-words --from owner. A lane stops with status waiting" % name)
    bad = scan(text)
    bad and refuse("BRF-7", "the brief holds %s" % bad, "remove it, then freeze")
    body = text if text.endswith("\n") else text + "\n"
    with open(path, "w", encoding="utf-8") as fh:
        fh.write(body + "Frozen: %s %s %s\n" % (hashlib.sha256(body.encode()).hexdigest(), record, datetime.date.today().isoformat()))
    print("FROZEN %s %s by record %s" % (kind, name, record))


def briefs(root, kind):
    pattern = os.path.join(root, ".loop", "tasks", "*.md") if kind == "task" else os.path.join(root, "docs", "release-brief-*.md")
    out = {}
    for p in sorted(glob.glob(pattern)):
        n = os.path.basename(p)[:-3]
        out[n if kind == "task" else n[len("release-brief-"):]] = read(p)
    return out


def check(root):
    bad = []
    for kind in ("task", "release"):
        for name, text in briefs(root, kind).items():
            if FROZEN.search(text) and frozen(text) == ("", "", ""):
                bad.append("%s %s" % (kind, name))
    bad and refuse("BRF-4", "frozen brief changed after the freeze: %s" % ", ".join(bad), "restore the words, or freeze a new task that replaces it")
    print("BRIEFS OK")


def runs(root):
    out = []
    for p in glob.glob(os.path.join(common(root), "loop", "runs", "*.json")):
        try:
            out.append(json.load(open(p, encoding="utf-8")))
        except (OSError, ValueError):
            pass
    return out


def merged(run):
    return run.get("status") == "done" and (run.get("release") in ("merged", "cut") or (run.get("report") or {}).get("status") == "merged")


def done_rows(root):
    return {r[0] for r in (x.split("\t") for x in read(os.path.join(root, ".loop", "tasks.tsv")).splitlines()) if len(r) > 1 and r[1] == "done"}


def tasks(root):
    """The one list: [(name, state, [goal slugs], eta)], states queued, running, waiting, done or replaced."""
    all_runs, finished, out = runs(root), done_rows(root), []
    briefs_ = briefs(root, "task")
    replaced = {field(t, "Replaces") for t in briefs_.values()}
    for name, text in briefs_.items():
        mine = [r for r in all_runs if r.get("task") == name]
        state = "replaced" if name in replaced else "done" if name in finished else "waiting" if any(r.get("waiting") for r in mine if r.get("status") != "done") else "running" if any(r.get("status") != "done" for r in mine) else "queued"
        eta = next((str((r.get("eta") or {}).get("minutes", "")) for r in mine if r.get("eta")), "")
        out.append((name, state, [r.get("slug", "") for r in mine], eta, "" if frozen(text) else "not frozen"))
    return out


def lines(root):
    """Board lines: each task by name, its state and its goals underneath."""
    return ["task %s: %s%s%s" % (n, s, " (%s)" % note if note else "", " eta %sm" % e if e else "") + "".join("\n    goal %s" % g for g in gs) for n, s, gs, e, note in tasks(root)]


GWT = re.compile(r"^\d+\. Given .+ when .+ then .+", re.I)
PARTS = (("title", r"^# \S"), ("Slug", r"^- Slug: \S"), ("Touches", r"^- Touches: \S"), ("ETA", r"^- ETA: \S"), ("Task", r"^- Task: \S"), ("Release", r"^- Release: \S"), ("Done lines", r"^## Done lines$"), ("a done line", r"^\d+\. \S"))


def feature_state(root, fid):
    """'Reviewed' or 'Unreviewed' for a feature id on the wiki pages, '' when none lists it."""
    try:
        wiki = json.load(open(os.path.join(root, ".loop", "config.json"))).get("wiki_dir") or "docs/wiki"
    except (OSError, ValueError):
        wiki = "docs/wiki"
    for path in sorted(glob.glob(os.path.join(root, wiki, "*.md"))):
        found = re.search(r"^- %s: \*\*(Reviewed|Unreviewed)" % re.escape(fid), read(path), re.M)
        if found:
            return found[1]
    return ""


def parts_missing(text):
    """DEL-19.1: the parts a goal file in the fixed format lacks (a file with no Task line is an older one: none)."""
    return [] if "\n- Task:" not in text else [n for n, p in PARTS if not re.search(p, text, re.M)]


def freeze_check(g, args, lines):
    """DEL-19.1, DEL-23.1, DOC-27.5: what a goal needs before it freezes (g is the goal module)."""
    root, task = g.root(), getattr(args, "task", None)
    if task is None:  # goal.py adopt: the goal file already says
        text = read(g.goal_file(args.slug))
        found = re.search(r"^- Task: (\S.*)$", text, re.M)
        if "\n- Release:" in text and not found:
            g.no("the goal file has a Release line and no task. Fix: add '- Task: NAME' before adopting it.")
        args.task = found[1].strip() if found else ""
        return
    task.strip() or g.no("no task. Fix: --task NAME, the task this goal serves.")
    bad = [x for x in lines if not GWT.match(x)]
    bad and g.no("done line %r is not Given ... when ... then ... Fix: write it that way." % bad[0][:50])
    if os.path.isdir(os.path.join(root, ".loop", "tasks")):
        can_start(root, task)
        text = briefs(root, "task").get(task) or ""
        if field(text, "Kind") != "fix" and feature_state(root, field(text, "Feature")) == "Unreviewed":
            g.no("task %s serves %s, which is Unreviewed. Fix: the owner reviews it first; a bug fix is Kind: fix." % (task, field(text, "Feature")))


def can_start(root, name):
    text = briefs(root, "task").get(name)
    text is None and refuse("BRF-5", "task %s has no brief" % name, "write .loop/tasks/%s.md and freeze it" % name)
    frozen(text) or refuse("BRF-3", "task %s is not frozen" % name, "brief.py freeze task %s --owner-record ID" % name)
    states = {n: s for n, s, *_ in tasks(root)}
    wait = [d for d in names(field(text, "Needs")) if states.get(d) != "done"]
    wait and refuse("BRF-5", "task %s needs %s, not done yet" % (name, ", ".join(wait)), "start it after they are done")


def finish(root, name, met):
    text = briefs(root, "task").get(name) or refuse("BRF-3", "no task %s" % name, "check the name")
    lines_ = re.findall(r"^\d+\. .+$", text.split("## Done when", 1)[-1], re.M) if "## Done when" in text else []
    unmet = [str(i) for i in range(1, len(lines_) + 1) if str(i) not in names(met)]
    open_ = [r.get("slug") for r in runs(root) if r.get("task") == name and not merged(r)]
    (unmet or open_ or not lines_) and refuse("BRF-5", "task %s is not done: %s" % (name, ("done-when lines %s unmet" % ", ".join(unmet)) if unmet else ("goals not merged: %s" % ", ".join(open_)) if open_ else "it has no done-when lines"),
                                              "meet every done-when line and merge every goal, then finish with --met 1,2,..")
    with open(os.path.join(root, ".loop", "tasks.tsv"), "a", encoding="utf-8") as fh:
        fh.write("%s\tdone\t%s\n" % (name, datetime.date.today().isoformat()))
    print("DONE %s" % name)


def release_tasks(root, version):
    text = read(path_of(root, "release", version))
    return [x for x in re.findall(r"^\d+\. (\S+)", text.split("## Tasks", 1)[-1], re.M)] if frozen(text) else None


def gate_merge(root, task):
    """DOC-28.3: a feature task merges only once a frozen release brief names it; a fix task any time."""
    text = briefs(root, "task").get(task)
    if text is None or field(text, "Kind") == "fix":
        return
    if not any(task in (release_tasks(root, v) or []) for v in briefs(root, "release")):
        refuse("BRF-6", "feature task %s is named by no frozen release brief" % task, "it builds and waits; name it in the release brief, freeze that, then merge")


def gate_bump(root, kind, version):
    """DOC-28.2: a major or minor needs a frozen release brief; a major also needs an empty known-red list."""
    if kind == "major":
        rows = [k for x in known_red(root) for k in x[2]]
        rows and refuse("BRF-6", "a major needs an empty known-red list; it holds %s" % ", ".join(rows), "fix each row; clearing a row is the only path, there is no waiver")
    if kind in ("major", "minor") and release_tasks(root, version) is None:
        refuse("BRF-3", "no frozen release brief for %s" % version, "brief.py freeze release %s --owner-record ID" % version)


def gate_cut(root, version):
    """DOC-28.4: every named task is done; the tag notes and the result record are built from the brief."""
    named = release_tasks(root, version)
    named is None and refuse("BRF-3", "no frozen release brief for %s" % version, "freeze it first")
    states = {n: s for n, s, *_ in tasks(root)}
    open_ = [t for t in named if states.get(t) != "done"]
    open_ and refuse("BRF-5", "tasks not done: %s" % ", ".join(open_), "finish them (brief.py finish NAME --met ..) before the cut")


def gate(root, kind, version):
    """The bump hook (release.bump): a patch ships no feature task; a minor needs its frozen brief with every task done."""
    if kind == "patch":
        all_ = briefs(root, "release")
        shipped = {t for v, x in all_.items() if "## Results" in x for t in release_tasks(root, v) or []}
        loose = [n for n, x in briefs(root, "task").items() if field(x, "Kind") != "fix" and n not in shipped and any(r.get("task") == n and merged(r) for r in runs(root))]
        loose and refuse("BRF-6", "a patch cannot ship feature task %s" % ", ".join(loose), "cut it as a minor named in a frozen release brief, or leave it unmerged")
    elif kind == "minor":
        gate_bump(root, kind, version)
        gate_cut(root, version)


def held(root, state):
    """DOC-28.3: the unshipped release brief that names this goal's feature task, else ''."""
    task, text = state.get("task") or "", briefs(root, "task").get(state.get("task") or "")
    if text is None or field(text, "Kind") == "fix":
        return ""
    return next((v for v, x in briefs(root, "release").items() if "## Results" not in x and task in (release_tasks(root, v) or [])), "")


def known_red(root):
    """DOC-28.1: [(check, subject, keys)] for every row on the known-red list; a major has no waiver (o714)."""
    rows = [x.split("\t")[0] for x in read(os.path.join(root, ".loop", "regression-known.tsv")).splitlines() if x.strip() and x[:1] != "#"]
    return [("known-red", "row %s is on the known-red list; clearing a row is the only path" % r, [r]) for r in rows]


def notes(root, version):
    return ["- task %s" % t for t in release_tasks(root, version) or []]


def files(root, version):
    """The release brief's path when it exists, for the release commit."""
    path = path_of(root, "release", version)
    return [os.path.relpath(path, root)] * os.path.exists(path)


def result(root, version):
    """DOC-28.5: after the cut the brief records each task's merged goals (written once; a retry adds nothing)."""
    path = path_of(root, "release", version)
    text = read(path)
    if "## Results" in text or release_tasks(root, version) is None:
        return
    body = "\n## Results\n" + "".join("- %s: %s\n" % (t, ", ".join(r.get("slug", "") for r in runs(root) if r.get("task") == t and merged(r)) or "no goals") for t in release_tasks(root, version) or [])
    bad = scan(body)
    bad and refuse("BRF-7", "the result record holds %s" % bad, "remove it from the goal names")
    with open(path, "a", encoding="utf-8") as fh:
        fh.write(body)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="command", required=True)
    f = sub.add_parser("freeze")
    f.add_argument("kind", choices=("task", "release"))
    f.add_argument("name")
    f.add_argument("--owner-record", default="")
    sub.add_parser("check")
    sub.add_parser("tasks")
    d = sub.add_parser("finish")
    d.add_argument("name")
    d.add_argument("--met", default="")
    g = sub.add_parser("gate")
    g.add_argument("what", choices=("merge", "start", "bump", "cut", "notes", "result"))
    g.add_argument("args", nargs="*")
    args = ap.parse_args(argv)
    root = top()
    if args.command == "freeze":
        freeze(root, args.kind, args.name, args.owner_record)
    elif args.command == "check":
        check(root)
    elif args.command == "tasks":
        print("\n".join(lines(root)) or "no tasks")
    elif args.command == "finish":
        finish(root, args.name, args.met)
    else:
        a = args.args
        {"merge": lambda: gate_merge(root, a[0]), "start": lambda: can_start(root, a[0]), "bump": lambda: gate_bump(root, a[0], a[1]),
         "cut": lambda: gate_cut(root, a[0]), "notes": lambda: print("\n".join(notes(root, a[0]))), "result": lambda: result(root, a[0])}[args.what]()
    return 0


if __name__ == "__main__":
    sys.exit(main())
