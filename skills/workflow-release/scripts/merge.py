#!/usr/bin/env python3
"""Merge a finished goal's pull request into the base branch, then release.

usage: merge.py SLUG

Refuses unless `"auto_merge": true` is in .loop/config.json, the goal is done and its pull request is open. Then it runs
the base's routines (refusing if one fails), merges, and releases (autorelease.py: bump, CHANGELOG, GitHub
release); failure: `release_error`. Where .loop/docs.tsv maps pages, it first refuses while one is stale
and after the merge publishes the wiki (wiki.py; refused: `wiki_error`).
Before merging it scans the branch and notes for private names, and holds the merge (REQUIREMENT_MISSING) while a
criterion row the goal adds names a requirement ID no base wiki page names, where the base's pages use that prefix
(else a NOTE). Takes <common>/loop/merge.lock (one per repo), refuses another pod's goal; a merged goal leaves
the pr queue.

Also here, the release pull request (autorelease.py calls `merge.advance` when the base takes no direct push): it pushes
the commit to `release/vX-<slug>`, opens `Release vX (<slug>)` with the notes as its body (scanned) and
merges it with `gh pr merge --merge`, never `--admin`. `gh pr view` decides the next move: MERGED: VERSION at the merge
commit must be vX (else RELEASE_VERSION_MISMATCH); OPEN: pending checks wait, a review or block records
RELEASE_PR_BLOCKED, no passing status RELEASE_STATUS_FAILED or _UNTESTED, a conflict restarts with the next
version; CLOSED: restart.
"""
import argparse
import datetime
import importlib.util
import json
import os
import re
import subprocess
import sys

import autorelease as ar
import release
import wiki


HERE = os.path.dirname(os.path.abspath(__file__))


def _pods():  # MON-15: workflow-monitoring's graph.py, or None
    try:
        spec = importlib.util.spec_from_file_location("pods_graph", os.path.join(HERE, "..", "..", "workflow-monitoring", "scripts", "graph.py"))
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        return mod
    except Exception:
        return None


pods = _pods()

# No terminal, no waiting: a prompt from git or gh must fail, not block.
os.environ.update(GIT_TERMINAL_PROMPT="0", GH_PROMPT_DISABLED="1", GIT_EDITOR="true", GIT_ASKPASS="true", SSH_ASKPASS="true")
if not sys.stdin or not sys.stdin.isatty():
    os.dup2(os.open(os.devnull, os.O_RDONLY), 0)


def run(args, cwd=None):
    return subprocess.run(args, cwd=cwd, capture_output=True, text=True)


REACH = os.path.normpath(os.path.join(HERE, "..", "..", "workflow-regression", "scripts", "lanes_cli.py"))


def reach(top, paths):
    """Row ids a change to PATHS can affect, or None for every row (unmapped, deleted, no planner)."""
    if not paths:
        return set()
    if not os.path.exists(REACH):
        return None
    done = run([sys.executable, "-B", REACH, "affected", "--root", top, "--"] + paths, cwd=top)
    found = re.search(r"^AFFECTED \d+ of \d+ rows \((.*)\)", done.stdout, re.M)
    if done.returncode or not found or re.search(r"^(UNMAPPED|DELETED) ", done.stdout, re.M):
        return None  # a failing planner can't clear the merge
    return set(found.group(1).split(", ")) - {"none", ""}


def wiki_only(top, cfg, old, new):
    """True when NEW descends from OLD (the pr lane's head) and every commit between only edits .md pages in the base's
    wiki folder (wiki_dir from origin/<base>'s config), no SKILL.md."""
    if run(["git", "merge-base", "--is-ancestor", old, new], cwd=top).returncode:
        return False
    head = run(["git", "symbolic-ref", "--short", "refs/remotes/origin/HEAD"], cwd=top).stdout.strip()
    shown = run(["git", "show", "%s:.loop/config.json" % (head or "origin/main")], cwd=top)
    try:
        folder = (json.loads(shown.stdout).get("wiki_dir") if shown.returncode == 0 else None) or "docs/wiki"
    except (ValueError, AttributeError):
        folder = "docs/wiki"
    done = run(["git", "diff", "--raw", "--no-renames", old, new], cwd=top)  # a move shows its source
    rows = [(a.split(), b) for a, *b in (line.split("\t") for line in done.stdout.split("\n") if line)]
    return not done.returncode and bool(rows) and all(
        len(m) == 5 and len(p) == 1 and m[4] in ("A", "M") and m[1] != "120000"  # no symlink
        and p[0].startswith(str(folder).rstrip("/") + "/") and p[0].endswith(".md") and os.path.basename(p[0]) != "SKILL.md"
        for m, p in rows)


def base_moved(state, cfg, top):
    """None when the merge may go ahead, else (exit code, refusal): the base moved since the pr lane in paths this goal's
    rows reach (2), or origin can't be fetched (3); a move elsewhere only notes it."""
    base, was, slug = cfg.get("base", "main"), state.get("pr_base"), state.get("slug", "SLUG")
    if not was and state.get("pr_head"):  # a head but no base: never clear
        return 2, "REFUSED (BASE_MOVED): the base the pr lane ran on was not recorded. Fix: goal.py pr %s, then merge.py %s" % (
            slug, slug)
    if not was:  # opened before pr recorded a base
        return None
    try:
        done = subprocess.run(["git", "fetch", "-q", "origin", base], cwd=top, capture_output=True, text=True, timeout=60)
        why = (done.stderr.strip().splitlines() or ["exit %d" % done.returncode])[-1] if done.returncode else ""
    except subprocess.TimeoutExpired:
        why = "timed out after 60s"
    if why:
        return 3, "REFUSED (BASE_FETCH): cannot fetch origin/%s: %s. Fix: run merge.py %s again when the remote answers; " \
                  "nothing merged" % (base, why, slug)
    now = run(["git", "rev-parse", "origin/" + base], cwd=top).stdout.strip()
    if now == was:
        return None
    def names(a, b):  # None when git can't diff: refused below
        done = run(["git", "diff", "--name-only", "--no-renames", a, b], cwd=top)
        return None if done.returncode else [p for p in done.stdout.split("\n") if p]
    theirs, ours = [None if x is None else reach(top, x) for x in (names(was, now), names(was, state.get("pr_head") or "HEAD"))]
    if theirs is None or ours is None or theirs & ours:
        return 2, "REFUSED (BASE_MOVED): %s moved in paths this goal's rows reach (lane on %s, base now %s). Fix: goal.py " \
                  "pr %s, then merge.py %s" % (base, was[:12], now[:12], slug, slug)
    print("NOTE: %s moved in paths this goal's rows don't reach; merging" % base)
    return None


def missing_ids(top, cfg, head="HEAD"):
    """(held, noted): requirement IDs this goal's criterion rows add that no origin/<base> wiki page names."""
    base = "origin/" + cfg.get("base", "main")
    folder = (cfg.get("wiki_dir") or "docs/wiki").strip("/")
    added = run(["git", "diff", "-U0", base + "..." + head, "--", ".loop/regression.tsv"], cwd=top).stdout
    ids = set()
    for line in added.splitlines():
        cells = line[1:].split("\t") if line.startswith("+") and not line.startswith("+++") else []
        if len(cells) > 3 and (cells[6:7] in ([], [""], ["criterion"])) and re.match(r"^[A-Z]{2,5}-\d+$", cells[3]):
            ids.add(cells[3])
    if not ids:
        return [], []
    def pages(ref):
        found = run(["git", "ls-tree", "--name-only", ref, folder + "/"], cwd=top).stdout.split()
        return found, "\n".join(run(["git", "show", "%s:%s" % (ref, n)], cwd=top).stdout for n in found if n.endswith(".md"))
    names, text = pages(base)
    both = text + "\n" + pages(head)[1]  # a page this goal adds counts
    gone = sorted(i for i in ids if not re.search(r"\b%s\b" % re.escape(i), both))
    held = [i for i in gone if names and re.search(r"\b%s\d+\b" % re.escape(i.split("-")[0] + "-"), text)]
    return held, [i for i in gone if i not in held]


# ---- the release pull request (DEL-5, issues 134 and 154)
FIELDS = "state,mergeStateStatus,reviewDecision,mergeCommit,statusCheckRollup,url,number,headRefOid"
REVIEW = ("REVIEW_REQUIRED", "CHANGES_REQUESTED")
PENDING = ("QUEUED", "IN_PROGRESS", "WAITING", "PENDING", "REQUESTED", "EXPECTED")
KEYS = ("release_pr", "release_pr_branch", "release_pr_version", "release_pushed", "release_pr_waiting", "release_status")


def title_of(version, slug):
    return "Release v%s (%s)" % (version, slug)


def view(top, ref):
    got = ar.sh(["gh", "pr", "view", ref, "--json", FIELDS], cwd=top)
    try:
        seen = json.loads(got.stdout) if got.returncode == 0 else {}
    except ValueError:
        seen = {}
    return seen if isinstance(seen, dict) else {}


def forget(state, why):
    for key in KEYS:
        state.pop(key, None)
    release.save(state, "release PR forgotten: " + why)
    print("RESTART the release pull request: " + why)


def start(top, cfg, state):
    """Push release/vX-<slug>, open its pull request, record release_pr."""
    base, slug = cfg.get("base", "main"), state["slug"]
    version = ar.push_release_commit(top, cfg, state, state["release_part"], to_branch=True)[0]
    branch = "release/v%s-%s" % (version, slug)
    title, body = title_of(version, slug), ar.notes_text(state)
    ar.check(state, top, None, {"release PR title": title, "release notes": body})
    made = ar.sh_text(["gh", "pr", "create", "--base", base, "--head", branch, "--title", title], body, cwd=top)
    url = (made.stdout.strip().splitlines() or [""])[-1] if made.returncode == 0 else ""
    if not url:  # a restart may find it still open
        seen = view(top, branch)
        url = seen.get("url", "") if seen.get("state") == "OPEN" else ""
    if not url:
        ar.fail(state, "gh pr create for %s failed: %s. Side effects: branch %s pushed, no pull request "
                         "(partial). Fix: run merge.py %s again" % (branch, (made.stderr or "").strip()[-200:], branch, slug))
    state.update(release_pr=url, release_pr_branch=branch, release_pr_version=version)
    release.save(state, "release PR %s opened for v%s" % (url, version))
    print("RELEASE PR %s (%s)" % (url, title))


def pending(seen):
    return any(isinstance(item, dict) and (item.get("status") in PENDING or item.get("state") in PENDING)
               for item in seen.get("statusCheckRollup") or [])


def advance(top, cfg, state, again=False):
    """(version, merge commit) once the release PR is merged, None while it waits."""
    if not state.get("release_pr"):
        start(top, cfg, state)
    url, version, slug = state["release_pr"], state["release_pr_version"], state["slug"]
    seen, said = view(top, url), ""
    if seen.get("state") == "OPEN":
        ar.check(state, top, None, {"release PR title": title_of(version, slug), "release notes": ar.notes_text(state)})
        ar.release_statuses(top, cfg, state, state["release_pr_branch"], seen.get("headRefOid"))
        merged = ar.sh(["gh", "pr", "merge", url, "--merge"], cwd=top)
        said = (merged.stderr or merged.stdout).strip()[-200:]
        seen = view(top, url)
    status, number = seen.get("state"), seen.get("number") or url.rstrip("/").split("/")[-1]
    if status == "MERGED":
        oid = (seen.get("mergeCommit") or {}).get("oid") or ""
        base, vfile = cfg.get("base", "main"), cfg.get("version_file") or "VERSION"
        ar.sh(["git", "fetch", "-q", "origin", base], cwd=top)
        found = ar.sh(["git", "show", "%s:%s" % (oid, vfile)], cwd=top)
        if oid and found.stdout.strip() != version:  # VERSION set by hand: release at the tip
            tip = ar.sh(["git", "rev-parse", "origin/" + base], cwd=top).stdout.strip()
            fixed = ar.sh(["git", "show", "origin/%s:%s" % (base, vfile)], cwd=top)
            oid, found = (tip, fixed) if tip and fixed.stdout.strip() == version else (oid, found)
        if not oid or found.stdout.strip() != version:
            ar.fail(state, "the release PR %s merged, but VERSION at its merge commit %s is %r, not %s; no "
                    "release was created. Fix: set VERSION on the base by hand, then run merge.py %s "
                    "(RELEASE_VERSION_MISMATCH)" % (url, oid[:12] or "(none)", found.stdout.strip(), version, slug))
        state.pop("release_pr_waiting", None)
        print("MERGED the release PR %s at %s" % (url, oid[:12]))
        return version, oid
    if not again and (status == "CLOSED" or (status == "OPEN" and seen.get("mergeStateStatus") in ("DIRTY", "BEHIND"))):
        if status == "OPEN":  # another release moved VERSION first
            ar.sh(["gh", "pr", "close", url], cwd=top)
        forget(state, "%s was %s" % (url, "closed unmerged" if status == "CLOSED" else "behind the base"))
        return advance(top, cfg, state, again=True)
    if status == "OPEN" and seen.get("reviewDecision") not in REVIEW and (pending(seen) or seen.get("mergeStateStatus") == "UNKNOWN"):
        state["release_pr_waiting"] = "checks pending on %s (#%s)" % (url, number)
        state.pop("release_error", None)
        release.save(state, "waiting: " + state["release_pr_waiting"])
        print("WAITING %s: required checks are pending on the release PR %s; the next merge.py %s run merges it"
              % (slug, url, slug))
        return None
    state["release_tries"] = state.get("release_tries", 0) + 1
    ar.status_held(state, url, number, seen)
    why = "a review is required" if seen.get("reviewDecision") in REVIEW else "it is %s, %s" % (
        status or "unreadable", seen.get("mergeStateStatus") or said or "no reason given")
    ar.fail(state, "the release PR %s (#%s) can't merge: %s; it needs the owner to approve and merge it. Fix: "
            "gh pr merge %s --merge, then merge.py %s. Side effects: branch %s pushed and the pull request open "
            "(partial); try %d (RELEASE_PR_BLOCKED)" % (
                url, number, why, number, slug, state.get("release_pr_branch"), state["release_tries"]))


def load(path):
    try:
        with open(path) as handle:
            return json.load(handle)
    except (OSError, ValueError):
        return None


def leave_queue(path, slug):
    """A merged goal leaves the pr queue (#4343)."""
    for name in (slug, slug + ".beat"):
        gone = os.path.join(os.path.dirname(os.path.dirname(path)), "pr-queue", name)
        os.path.exists(gone) and os.unlink(gone)


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("slug")
    slug = parser.parse_args().slug
    top, common = (run(["git", "rev-parse", opt]).stdout.strip() for opt in ("--show-toplevel", "--git-common-dir"))
    if not top or not common:
        sys.exit("REFUSED: not in a git repo.")
    cfg = load(os.path.join(top, ".loop", "config.json"))
    if cfg is None:
        sys.exit("REFUSED: no readable .loop/config.json. Fix: run workflow-setup and merge its branch.")
    base = cfg.get("base", "main")
    wiki.where(__file__, cfg.get("base"))
    if cfg.get("auto_merge") is not True:
        sys.exit("REFUSED: auto_merge is off in this repo, so the owner merges. Nothing was merged.")
    path = os.path.join(os.path.abspath(common), "loop", "runs", slug + ".json")
    state = load(path)
    if state is None:
        sys.exit("REFUSED: no goal named %s." % slug)
    if not ar.mergeable(state):
        sys.exit("REFUSED: %s has no finished pull request. Fix: run goal.py pr first." % slug)
    if pods:
        pods.refuse(state)
        pods.merge_lock(os.path.abspath(common))  # one merge per repo
    view = run(["gh", "pr", "view", state["pr"], "--json", "state,headRefOid"])
    info = json.loads(view.stdout or "{}") if view.returncode == 0 else {}
    known, new = info.get("state", ""), info.get("headRefOid")
    if known != "MERGED":
        head = "origin/" + state.get("branch", "")  # the pull request's tip
        if wiki.top_of():
            stale = wiki.pending(top, cfg, head=head)
            if stale:
                ar.fail(state, "stale wiki pages: %s. Fix: update %s, then run wiki.py prepare %s --commit." % (
                    ", ".join(stale), ", ".join(sorted({l.split(":")[0].split()[1] for l in stale if l.startswith("REWRITE ")})) or "them", slug))
            if run(["git", "branch", "-r", "--contains", "HEAD", "--list", "origin/*"], cwd=top).stdout.strip() == "":
                sys.exit("REFUSED: this branch's latest commit is not on origin. Fix: run wiki.py prepare %s --commit." % slug)
        if known != "OPEN":
            sys.exit("REFUSED: the pull request %s is %s, not open." % (state["pr"], known or "unknown"))
        tested = state.get("pr_head")
        if tested and new and new != tested and wiki_only(top, cfg, tested, new):
            print("NOTE: the pull request head moved only by wiki page commits (wiki.py prepare); merging %s" % new[:12])
            tested = new
        if tested and new and new != tested:
            print("REFUSED (HEAD_MOVED): the pull request head moved since the pr lane passed (lane on %s, PR head %s). Fix: "
                  "goal.py pr %s, then merge.py %s" % (tested[:12], new[:12], slug, slug), file=sys.stderr)
            return ar.reopen(state, 4)
        moved = base_moved(state, cfg, top)
        if moved:
            print(moved[1], file=sys.stderr)
            return ar.reopen(state, moved[0])
        ar.stage_notes(top, state, cfg)
        ar.stage_part(top, state)
        if not state.get("branch") or run(["git", "fetch", "-q", "origin", state["branch"]], cwd=top).returncode:
            ar.fail(state, "could not fetch the goal branch %s to scan it; nothing was merged (PRIVATE_LIST)" % state.get("branch"))
        ar.check(state, top, "origin/" + base, {"release notes": ar.notes_text(state)}, True, head)
        held, noted = missing_ids(top, cfg, head)
        if held:
            ar.fail(state, "criterion rows name %s, which no wiki page on origin/%s names; nothing was merged. Fix: "
                    "merge the goal that adds their text, then merge.py %s (REQUIREMENT_MISSING)" % (", ".join(held), base, slug))
        if noted:
            print("NOTE: no wiki page on the base names %s yet; merging anyway" % ", ".join(noted))
        ar.run_routines(top, cfg, state)
        if tested != state.get("pr_head"):
            ar.restatus(top, cfg, state, tested)
        done = run(["gh", "pr", "merge", state["pr"], "--merge"] + (["--match-head-commit", tested] if tested else []))
        if done.returncode:
            ar.fail(state, "gh could not merge %s: %s" % (state["pr"], done.stderr.strip()[-300:]))
    at = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    ar.mark_merged(state)
    state["updated"] = at
    state.setdefault("log", []).append("%s merged %s (auto_merge)" % (at, state["pr"]))
    with open(path + ".tmp", "w") as handle:
        json.dump(state, handle, indent=2)
    os.replace(path + ".tmp", path)
    print("MERGED %s into %s" % (state["pr"], base))
    leave_queue(path, slug)
    ar.finish(top, cfg, state)
    if wiki.top_of():
        wiki.cmd_publish(argparse.Namespace(slug=slug))
    return 0


if __name__ == "__main__":
    sys.exit(main())
