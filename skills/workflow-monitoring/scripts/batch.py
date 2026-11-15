#!/usr/bin/env python3
"""Assign goals in batches. The operation session only adds, starts workers and watches; it never runs a goal.

usage: batch.py <command> [options]

  add NAME --goal GOAL --done LINE [--done LINE] [--slug S] [--touches A,B] [--depends-on A,B] [--release ask]
      add a goal line under the heading '## Batch: NAME' in .loop/queue.md
  start NAME [--max N] [--skill-dir DIR]
      start one worker for each goal line (watch.py beside this file does it); each worker runs its own loop to the end
      and reports back by prompt message; otherwise print the command that starts them
  status NAME
      one line for each goal of the batch
  roadmap [--issues FILE] [--out FILE]
      the Roadmap wiki page: docs/ROADMAP.md's v1.0.0 group tables and Rollout, each open issue in its group (a hand row
      first, else by label), a status per row (in flight, queued or open; a closed issue drops out), the Backlog milestones
      apart as "after v1.0", the "To-do:" issues, the goals in flight and each page's Unreviewed requirements; Priority is
      left empty. Open issues come from gh (--issues FILE reads the same JSON); with --out it writes the page, else prints it

Each goal runs the one skill flow in its own worktree, in its own worker. Nothing is merged.
"""
import argparse
import datetime
import glob
import json
import os
import re
import subprocess
import sys

# No terminal, no waiting: a prompt from git or gh must fail, not block.
os.environ.update(GIT_TERMINAL_PROMPT="0", GH_PROMPT_DISABLED="1", GIT_EDITOR="true", GIT_ASKPASS="true", SSH_ASKPASS="true")
if not sys.stdin or not sys.stdin.isatty():
    os.dup2(os.open(os.devnull, os.O_RDONLY), 0)

SELF = os.path.abspath(sys.argv[0])
SLUG = re.compile(r"^[a-z0-9][a-z0-9-]{0,50}$")
HEAD = re.compile(r"^## Batch: (\S+)\s*$")
STEPS = ("build", "plan", "idea", "review", "qa", "ship", "step", "pr", "record", "run")
REFUSE = "REFUSED: %s is worker work; the operation session only assigns, watches and reports. Use: batch.py start NAME"

def git(*args, cwd=None, check=True):
    done = subprocess.run(["git"] + list(args), cwd=cwd, capture_output=True, text=True)
    if check and done.returncode:
        sys.exit("REFUSED: git %s: %s" % (" ".join(args), done.stderr.strip()))
    return done.stdout.strip() if done.returncode == 0 else ""


def now():
    return datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def loop_dir(*parts):
    path = os.path.join(os.path.abspath(git("rev-parse", "--git-common-dir")), "loop", *parts)
    os.makedirs(path, exist_ok=True)
    return path


def root():
    return git("rev-parse", "--show-toplevel")




def record_path(slug):
    return os.path.join(loop_dir("runs"), slug + ".json")


def load(slug):
    try:
        with open(record_path(slug)) as handle:
            return json.load(handle)
    except (OSError, ValueError):
        return None




def queue_path():
    return os.path.join(root(), ".loop", "queue.md")


def read_queue():
    try:
        with open(queue_path()) as handle:
            return handle.read().splitlines()
    except OSError:
        return []


def fields(line):
    out = {}
    for part in line.strip()[2:].split("|"):
        key, _, value = part.partition(":")
        out.setdefault(key.strip(), " ".join(value.split()))
    return out


def batch_items(name):
    """The goal lines under '## Batch: NAME', as (kind, fields)."""
    items, inside = [], False
    for line in read_queue():
        if line.startswith("## "):
            match = HEAD.match(line)
            inside = bool(match and match.group(1) == name)
        elif inside and line.startswith("- slug:"):
            items.append(("goal", fields(line)))
    return items


def taken(slug):
    return any(line.startswith("- slug: %s " % slug) for line in read_queue()) or load(slug)


def put(name, line):
    lines = read_queue()
    at = None
    for index, text in enumerate(lines):
        if text.startswith("## "):
            if at is not None:
                break
            at = index + 1 if (HEAD.match(text) or [0, 0])[1] == name else None
        elif at is not None and text.strip():
            at = index + 1
    if at is None:
        lines += [""] * bool(lines and lines[-1].strip()) + ["## Batch: " + name, line]
    else:
        lines.insert(at, line)
    with open(queue_path(), "w") as handle:
        handle.write("\n".join(lines) + "\n")


def clean(text):
    text = " ".join(str(text).split())
    if "|" in text:
        sys.exit("REFUSED: no | in any text.")
    return text


def cmd_add(args):
    if not SLUG.match(args.name):
        sys.exit("REFUSED: bad batch name (lowercase letters, digits, dashes).")
    if not args.goal or not args.done:
        sys.exit("REFUSED: give --goal GOAL with at least one --done.")
    text = clean(args.goal)
    words = re.findall(r"[a-z0-9]+", text.lower())[:6]
    slug = args.slug or "-".join(words)[:40].strip("-") or "item"
    if not SLUG.match(slug) or taken(slug):
        sys.exit("REFUSED: %s is a bad slug or already exists. Pick a new --slug." % slug)
    depends = [x for x in re.split(r"[,\s]+", args.depends_on) if x]
    unknown = [x for x in depends if not taken(x)]
    if unknown:
        sys.exit("REFUSED: depends-on %s is not a goal in the queue or the runs." % ", ".join(unknown))
    parts = ["slug: " + slug]
    if args.touches:
        parts.append("touches: " + clean(args.touches))
    if depends:
        parts.append("depends-on: " + ", ".join(depends))
    if args.release:
        parts.append("release: " + args.release)
    parts += ["goal: " + text] + ["done: " + clean(item) for item in args.done]
    line = "- " + " | ".join(parts)
    put(args.name, line)
    print("ADDED %s to batch %s" % (slug, args.name))
    return 0


def cmd_start(args):
    items = batch_items(args.name)
    if not items:
        sys.exit("REFUSED: no goal lines under '## Batch: %s'." % args.name)
    if items:
        flags = (["--max", str(args.max)] if args.max else []) + (["--skill-dir", args.skill_dir] if args.skill_dir else [])
        watch = os.path.join(os.path.dirname(SELF), "watch.py")
        if os.path.exists(watch):
            subprocess.run([sys.executable, watch, "watch", "--once"] + flags, cwd=root())
        else:
            print("NEXT: run watch.py watch --once to start the goal lines.")
    return 0


def cmd_status(args):
    items = batch_items(args.name)
    for kind, item in items:
        slug = item.get("slug")
        state = load(slug)
        print("%s %s: %s" % (kind, slug, state.get("status") if state else "not started"))
    print("%d line(s) in batch %s" % (len(items), args.name)) if items else print("EMPTY batch " + args.name)
    return 0

GROUPS = ("Size caps", "Windows-safe", "Regression trust", "Open defects", "Adoption", "Unreviewed requirements", "Package rules")
LABEL_GROUP = (("health:size", 0), ("regression", 2), ("defect", 3), ("health:adoption", 4))


def table(head, rows):
    return ["| %s |" % " | ".join(head), "|" + "---|" * len(head)] + ["| %s |" % " | ".join(c.replace("|", "/") for c in r) for r in rows] + [""]


def section(text, name):
    found = re.search(r"^## %s\s*\n(.*?)(?=^## |\Z)" % re.escape(name), text, re.M | re.S)
    return found.group(1) if found else ""


def cmd_roadmap(args):
    top = root()
    with open(os.path.join(top, "docs", "ROADMAP.md"), encoding="utf-8") as handle:
        source = handle.read()
    if args.issues:
        with open(args.issues, encoding="utf-8") as handle:
            raw = json.load(handle)
    else:
        done = subprocess.run(["gh", "issue", "list", "--state", "open", "--limit", "1000", "--json", "number,title,labels,milestone"], capture_output=True, text=True, cwd=top)
        if done.returncode:
            sys.exit("REFUSED: gh issue list failed: %s" % done.stderr.strip()[:200])
        raw = json.loads(done.stdout or "[]")
    names = lambda x: x.get("name") if isinstance(x, dict) else x
    issues = {i["number"]: (i["title"], [names(l) for l in i.get("labels") or []], (i["milestone"].get("title") if isinstance(i.get("milestone"), dict) else i.get("milestone")) or "") for i in raw}
    states = {}
    for name in os.listdir(loop_dir("runs")):
        record = load(name[:-5]) if name.endswith(".json") and "." not in name[:-5] else None
        if isinstance(record, dict) and record.get("slug"):
            states[record["slug"]] = record
    flying = {s: str(r.get("goal", "")) for s, r in states.items() if r.get("status") in ("running", "waiting") and r.get("goal")}
    queued = {f.get("slug"): f.get("goal", "") for f in (fields(l) for l in read_queue() if l.startswith("- slug:")) if f.get("slug") not in flying}
    hit = lambda ref, goals: any(ref == s or (ref[0] == "#" and re.search(ref + r"(?!\d)", t)) for s, t in goals.items())
    status = lambda ref: "in flight" if hit(ref, flying) else "queued" if hit(ref, queued) else "open"
    rows, hand = {g: [] for g in GROUPS}, set()
    for part in re.split(r"^### ", section(source, "v1.0.0"), flags=re.M)[1:]:
        group = part.split("\n", 1)[0].strip()
        for line in part.splitlines()[1:]:
            cells = [c.strip() for c in line.strip().strip("|").split("|")]
            ref = cells[0].strip("`") if line.startswith("| ") else ""
            if group not in rows or not (ref.startswith("#") or SLUG.match(ref)) or len(cells) < 3:
                continue
            number = int(ref[1:]) if ref.startswith("#") and ref[1:].isdigit() else 0
            if number:
                hand.add(number)
            if (number and number in issues) or (not number and states.get(ref, {}).get("status") not in ("done", "merged")):
                rows[group].append((cells[0], cells[1], cells[2], status(ref), ""))
    after, todos = {}, []
    for number, (title, labels, stone) in sorted(issues.items()):
        if stone.startswith("Backlog"):
            after.setdefault(stone, []).append(("#%d" % number, title[:110], ""))
        elif title.startswith("To-do:"):
            todos.append(("#%d" % number, title[6:].strip()[:110], status("#%d" % number)))
        elif number not in hand:
            group = next((g for l, g in LABEL_GROUP if l in labels), None)
            rows["Package rules" if group is None and "package" in title.lower() else "Windows-safe" if group is None and "windows" in title.lower() else GROUPS[group] if group is not None else "Open defects"].append(("#%d" % number, title[:110], "v1.0.0", status("#%d" % number), ""))
    out = ["<!-- workflow-docs -->", "<!-- workflow-docs guide -->", "# Roadmap", "",
           "Generated by `batch.py roadmap` from docs/ROADMAP.md, the open issues and the run records (%d open issues, %s); edit docs/ROADMAP.md, never this page. "
           "v1.0.0 is done when every open issue below is closed. Fill the Priority column to rank them." % (len(issues), now()[:10]), "", "## Before v1.0.0", ""]
    for group in GROUPS:
        out += ["### " + group, ""]
        if group == "Unreviewed requirements":
            pages = []
            for page in sorted(glob.glob(os.path.join(top, "docs", "wiki", "*.md"))):
                with open(page, encoding="utf-8") as handle:
                    for found in re.finditer(r"^- ([A-Z]+-\d+): \*\*Unreviewed\*\* (.*?)(?: <!--.*)?$", handle.read(), re.M):
                        pages.append((os.path.basename(page)[:-3], found.group(1), found.group(2)[:110], "open", ""))
            out += table(("Issue or goal", "Outcome", "Blocks", "Status", "Priority"), rows[group]) if rows[group] else []
            out += table(("Page", "Requirement", "Outcome", "Status", "Priority"), pages) if pages else ["No requirement is Unreviewed.", ""]
        else:
            out += table(("Issue or goal", "Outcome", "Blocks", "Status", "Priority"), rows[group]) if rows[group] else ["Nothing open.", ""]
    out += ["## Goals in flight", ""] + ["- `%s`: %s" % (s, " ".join(str(states[s].get("goal", "")).split())[:140]) for s in sorted(flying)] + [""]
    out += ["## Off-machine to-dos (these do not block v1.0.0)", ""] + (table(("Issue", "To-do", "Status"), todos) if todos else ["None.", ""])
    out += ["## After v1.0", "", "Backlog milestones wait for v1.1 and later.", ""]
    for stone in sorted(after):
        out += ["### " + stone, ""] + table(("Issue", "Outcome", "Priority"), after[stone])
    out += ["## Rollout", ""] + section(source, "Rollout").strip().splitlines() + [""]
    text = "\n".join(out).rstrip("\n") + "\n"
    if args.out:
        with open(os.path.join(top, args.out), "w", encoding="utf-8", newline="\n") as handle:
            handle.write(text)
        print("WROTE %s: %d open issues, %d goals in flight" % (args.out, len(issues), len(flying)))
    else:
        sys.stdout.write(text)
    return 0


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = parser.add_subparsers(dest="command", required=True)
    item = sub.add_parser("add")
    item.add_argument("name")
    item.add_argument("--goal", default="")
    item.add_argument("--done", action="append", default=[])
    item.add_argument("--slug", default="")
    item.add_argument("--touches", default="")
    item.add_argument("--depends-on", default="")
    item.add_argument("--release", default="", choices=["", "ask"])
    item = sub.add_parser("start")
    item.add_argument("name")
    item.add_argument("--max", type=int, default=0)
    item.add_argument("--skill-dir", default="")
    sub.add_parser("status").add_argument("name")
    item = sub.add_parser("roadmap")
    item.add_argument("--issues", default="")
    item.add_argument("--out", default="")
    if sys.argv[1:2] and sys.argv[1] in STEPS and os.environ.get("LOOP_ROLE") != "worker":
        sys.exit(REFUSE % sys.argv[1])
    args = parser.parse_args()
    return globals()["cmd_" + args.command.lstrip("_")](args)


if __name__ == "__main__":
    sys.exit(main())
