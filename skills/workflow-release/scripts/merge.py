#!/usr/bin/env python3
"""Merge a goal's pull request into the base, then release: merge.py SLUG [--go-head SHA];
merge.py SLUG SLUG [SLUG] --batch (merge_batch; refused under a merge queue). `land` enqueues when the base has one.
Refuses unless auto_merge is true and the goal is done with its PR open; commands.md lists the codes.
"""
import argparse
import importlib.util
import json
import os
import re
import subprocess
import sys
import time

import autorelease as ar
import release
import review
import wiki


HERE = os.path.dirname(os.path.abspath(__file__))
MON = os.path.join(HERE, "..", "..", "workflow-monitoring", "scripts")


def file_issue(top, page, texts):
    title = "Docs: %s has DOC-19/DOC-4 findings" % page
    stone = "Backlog: " + (page[11:] if page.startswith("How-to-use-") else "Documentation" if "/" in page or page == "Home" else page)
    gh = lambda *a: run(["gh"] + list(a), top)
    try:
        held = gh("issue", "list", "--state", "open", "--limit", "1000", "--json", "title", "-q", ".[].title")
        if held.returncode or title in held.stdout.splitlines():
            return "no issue filed (gh)" if held.returncode else "its issue is open"
        gh("api", "-X", "POST", "repos/{owner}/{repo}/milestones", "-f", "title=" + stone)
        return "filed " + gh("issue", "create", "--title", title, "--milestone", stone, "--body", "\n".join(texts)).stdout.split()[-1]
    except (OSError, IndexError):
        return "no issue filed (gh)"


def _pods():
    sys.path.append(MON)
    try:
        spec = importlib.util.spec_from_file_location("pods_graph", os.path.join(MON, "graph.py"))
        spec.loader.exec_module(mod := importlib.util.module_from_spec(spec))
        return mod
    except Exception:
        return None


pods = _pods()

os.environ.update(GIT_TERMINAL_PROMPT="0", GH_PROMPT_DISABLED="1", GIT_EDITOR="true", GIT_ASKPASS="true", SSH_ASKPASS="true")
if not sys.stdin or not sys.stdin.isatty():
    os.dup2(os.open(os.devnull, os.O_RDONLY), 0)


def run(args, cwd=None):
    return subprocess.run(args, cwd=cwd, capture_output=True, text=True)


REACH = os.path.normpath(os.path.join(HERE, "..", "..", "workflow-regression", "scripts", "lanes_cli.py"))


def reach(top, paths):
    if not paths:
        return set()
    if not os.path.exists(REACH):
        return None
    done = run([sys.executable, "-B", REACH, "affected", "--root", top, "--"] + paths, cwd=top)
    found = re.search(r"^AFFECTED \d+ of \d+ rows \((.*)\)", done.stdout, re.M)
    if done.returncode or not found or re.search(r"^(UNMAPPED|DELETED) ", done.stdout, re.M):
        return None
    return set(found.group(1).split(", ")) - {"none", ""}


OPERATE = os.path.join(MON, "operate.py")


def base_moved(state, cfg, top):
    base, was, slug = cfg.get("base", "main"), state.get("pr_base"), state.get("slug", "SLUG")
    if not was and state.get("pr_head"):
        return 2, "REFUSED (BASE_MOVED): the base the pr lane ran on was not recorded. Fix: goal.py pr %s, then merge.py %s" % (
            slug, slug)
    if not was:
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
    def names(a, b):
        done = run(["git", "diff", "--name-only", "--no-renames", a, b], cwd=top)
        return None if done.returncode else [p for p in done.stdout.split("\n") if p]
    theirs, ours = [None if x is None else reach(top, x) for x in (names(was, now), names(was, state.get("pr_head") or "HEAD"))]
    if theirs is None or ours is None or theirs & ours:
        return 2, "REFUSED (BASE_MOVED): %s moved in paths this goal's rows reach (lane on %s, base now %s). Fix: goal.py " \
                  "pr %s, then merge.py %s" % (base, was[:12], now[:12], slug, slug)
    print("NOTE: %s moved in paths this goal's rows don't reach; merging" % base)
    return None


def missing_ids(top, cfg, head="HEAD"):
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
    both = text + "\n" + pages(head)[1]
    gone = sorted(i for i in ids if not re.search(r"\b%s\b" % re.escape(i), both))
    held = [i for i in gone if names and re.search(r"\b%s\d+\b" % re.escape(i.split("-")[0] + "-"), text)]
    return held, [i for i in gone if i not in held]


FIELDS = "isInMergeQueue,state,mergeStateStatus,reviewDecision,mergeCommit,statusCheckRollup,url,number,headRefOid"
REVIEW = ("REVIEW_REQUIRED", "CHANGES_REQUESTED")
PENDING = ("QUEUED", "IN_PROGRESS", "WAITING", "PENDING", "REQUESTED", "EXPECTED")
KEYS = ("release_pr", "release_pr_branch", "release_pr_version", "release_pushed", "release_pr_waiting", "release_status")


def title_of(version, slug):
    return "Release v%s (%s)" % (version, slug)


def view(top, ref):
    try:
        seen = json.loads(ar.sh(["gh", "pr", "view", ref, "--json", FIELDS], cwd=top).stdout)
    except ValueError:
        seen = {}
    return seen if isinstance(seen, dict) else {}


def forget(state, why):
    for key in KEYS:
        state.pop(key, None)
    release.save(state, "release PR forgotten: " + why)
    print("RESTART the release pull request: " + why)


def start(top, cfg, state):
    base, slug = cfg.get("base", "main"), state["slug"]
    version = ar.push_release_commit(top, cfg, state, state["release_part"], to_branch=True)[0]
    branch = "release/v%s-%s" % (version, slug)
    title, body = title_of(version, slug), ar.notes_text(state)
    ar.check(state, top, None, {"release PR title": title, "release notes": body})
    made = ar.sh_text(["gh", "pr", "create", "--base", base, "--head", branch, "--title", title], body, cwd=top)
    url = (made.stdout.strip().splitlines() or [""])[-1] if made.returncode == 0 else ""
    if not url:
        seen = view(top, branch)
        url = seen.get("url", "") if seen.get("state") == "OPEN" else ""
    if not url:
        ar.fail(state, "gh pr create for %s failed: %s. Fix: run merge.py %s again" % (branch, (made.stderr or "").strip()[-200:], slug))
    state.update(release_pr=url, release_pr_branch=branch, release_pr_version=version)
    release.save(state, "release PR %s opened for v%s" % (url, version))
    print("RELEASE PR %s (%s)" % (url, title))


def queue_on(top, base):
    """True: base has a merge_queue rule; None: unreadable."""
    got = run(["gh", "api", "repos/{owner}/{repo}/rules/branches/" + base], top)
    return None if got.returncode else '"type":"merge_queue"' in got.stdout.replace(" ", "")


def land(top, base, url, head=None):
    """"" once url is merged (enqueued, bound to head, under a queue), else why not."""
    queue = queue_on(top, base)
    bind = ["--match-head-commit", head] if head else []
    if queue is None:
        return "can't read the rules for %s (QUEUE_UNREADABLE)" % base
    seen, began = view(top, url), time.time()
    if not queue or seen.get("state") == "OPEN" and not seen.get("isInMergeQueue"):
        done = run(["gh", "pr", "merge", url, "--merge"] + ["--auto"] * queue + bind, top)
        if done.returncode or not queue:
            return done.stderr.strip()[-300:] if done.returncode else ""
    while True:
        seen, waited = view(top, url), time.time() - began
        state, oid = seen.get("state"), seen.get("headRefOid")
        if state == "MERGED":
            return ""
        if state == "CLOSED" or head and oid not in (None, head):
            return "left the queue: %s at %s, not %s" % (state, str(oid)[:12], head[:12])
        if not seen.get("isInMergeQueue") and waited > int(os.environ.get("LOOP_QUEUE_GRACE") or 120):
            return "dropped from the queue (QUEUE_DEQUEUED)"
        if waited > int(os.environ.get("LOOP_MERGE_LOCK_SECONDS") or 1800):
            return "still queued after %ds (QUEUE_TIMEOUT)" % waited
        time.sleep(float(os.environ.get("LOOP_QUEUE_POLL") or 15))


def pending(seen):
    return any(isinstance(item, dict) and (item.get("status") in PENDING or item.get("state") in PENDING)
               for item in seen.get("statusCheckRollup") or [])


def advance(top, cfg, state, again=False):
    if not state.get("release_pr"):
        start(top, cfg, state)
    url, version, slug = state["release_pr"], state["release_pr_version"], state["slug"]
    seen, said = view(top, url), ""
    if seen.get("state") == "OPEN":
        ar.check(state, top, None, {"release PR title": title_of(version, slug), "release notes": ar.notes_text(state)})
        ar.release_statuses(top, cfg, state, state["release_pr_branch"], seen.get("headRefOid"))
        said = land(top, cfg.get("base", "main"), url)[-200:]
        seen = view(top, url)
    status, number = seen.get("state"), seen.get("number") or url.rstrip("/").split("/")[-1]
    if status == "MERGED":
        oid = (seen.get("mergeCommit") or {}).get("oid") or ""
        base, vfile = cfg.get("base", "main"), cfg.get("version_file") or "VERSION"
        ar.sh(["git", "fetch", "-q", "origin", base], cwd=top)
        found = ar.sh(["git", "show", "%s:%s" % (oid, vfile)], cwd=top)
        if oid and found.stdout.strip() != version:
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
        if status == "OPEN":
            ar.sh(["gh", "pr", "close", url], cwd=top)
        forget(state, "%s was %s" % (url, "closed unmerged" if status == "CLOSED" else "behind the base"))
        return advance(top, cfg, state, again=True)
    if status == "OPEN" and seen.get("reviewDecision") not in REVIEW and (pending(seen) or seen.get("mergeStateStatus") == "UNKNOWN"):
        state["release_pr_waiting"] = "checks pending on %s (#%s)" % (url, number)
        state.pop("release_error", None)
        release.save(state, "waiting: " + state["release_pr_waiting"])
        print("WAITING %s: checks pending on the release PR %s; run merge.py again" % (slug, url))
        return None
    state["release_tries"] = state.get("release_tries", 0) + 1
    ar.status_held(state, url, number, seen)
    why = "a review is required" if seen.get("reviewDecision") in REVIEW else "it is %s, %s" % (
        status or "unreadable", seen.get("mergeStateStatus") or said or "no reason given")
    ar.fail(state, "the release PR %s (#%s) can't merge: %s; the owner approves and merges it. Fix: gh pr merge %s --merge, "
            "then merge.py %s; try %d (RELEASE_PR_BLOCKED)" % (url, number, why, number, slug, state["release_tries"]))


def load(path):
    try:
        return json.load(open(path))
    except (OSError, ValueError):
        return None


def leave_queue(path, slug):
    for name in (slug, slug + ".beat"):
        gone = os.path.join(os.path.dirname(os.path.dirname(path)), "pr-queue", name)
        os.path.exists(gone) and os.unlink(gone)


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("slug", nargs="+")
    parser.add_argument("--batch", action="store_true", help="2-3 goals as one")
    parser.add_argument("--go-head", metavar="SHA", help="GO for this head only")
    args = parser.parse_args()
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
    queue = queue_on(top, base)
    if args.batch or len(args.slug) > 1:
        if queue is not False:
            sys.exit("REFUSED: main has a merge queue or unreadable rules; GitHub builds merge groups, so merge goals alone. Nothing merged.")
        if not (args.batch and cfg.get("merge_batch") is True):
            sys.exit("REFUSED: several goals need --batch and merge_batch true. Nothing merged.")
        pods and pods.merge_lock(os.path.abspath(common))
        spec = importlib.util.spec_from_file_location("batch", os.path.join(MON, "machines.py"))
        machines = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(machines)
        return machines.batch(top, common, cfg, args.slug, args.go_head, sys.modules[__name__])
    slug = args.slug[0]
    runs = os.path.join(os.path.abspath(common), "loop", "runs")
    path = os.path.join(runs, slug + ".json")
    state = load(path)
    if state is None:
        sys.exit("REFUSED: no goal named %s." % slug)
    if not ar.mergeable(state):
        sys.exit("REFUSED: %s has no finished pull request. Fix: run goal.py pr first." % slug)
    if pods:
        pods.refuse(state)
        pods.pr_queue("wait", runs, slug)
        queue or pods.merge_lock(os.path.abspath(common))
    wiki.top_of() and print(run([sys.executable, OPERATE, "apply", slug, str(state.get("branch"))], top).stdout.strip())
    view = run(["gh", "pr", "view", state["pr"], "--json", "state,headRefOid,statusCheckRollup"])
    info = json.loads(view.stdout or "{}") if view.returncode == 0 else {}
    known, new = info.get("state", ""), info.get("headRefOid")
    if known != "MERGED":
        head = "origin/" + state.get("branch", "")
        if wiki.top_of():
            stale = wiki.pending(top, cfg, head=head, filer=file_issue)
            if stale:
                ar.fail(state, "stale wiki pages: %s. Fix: update %s, then run wiki.py prepare %s --commit." % (
                    ", ".join(stale), ", ".join(sorted({l.split(":")[0].split()[1] for l in stale if l.startswith("REWRITE ")})) or "them", slug))
            if run(["git", "branch", "-r", "--contains", "HEAD", "--list", "origin/*"], cwd=top).stdout.strip() == "":
                sys.exit("REFUSED: this branch's latest commit is not on origin. Fix: wiki.py prepare %s --commit." % slug)
        if known != "OPEN":
            sys.exit("REFUSED: the pull request %s is %s, not open." % (state["pr"], known or "unknown"))
        tested = state.get("pr_head")
        if tested and new and new != tested and run([sys.executable, OPERATE, "wiki-only", tested, new], top).returncode == 0:
            print("NOTE: the pull request head moved only by wiki page commits (wiki.py prepare); merging %s" % new[:12])
            tested = new
        if tested and new and new != tested:
            print("REFUSED (HEAD_MOVED): the pull request head moved since the pr lane passed (lane on %s, PR head %s). Fix: "
                  "goal.py pr %s, then merge.py %s" % (tested[:12], new[:12], slug, slug), file=sys.stderr)
            return ar.reopen(state, 4)
        why = args.go_head and ar.go_gate(top, base, info, args.go_head)
        if why:
            print(why, file=sys.stderr)
            return 4 if "GO_HEAD" in why else 5
        moved = base_moved(state, cfg, top)
        if moved:
            print(moved[1], file=sys.stderr)
            return ar.reopen(state, moved[0])
        why = review.frozen(top, head, slug)
        why and ar.fail(state, why)
        why = review.held(cfg, state, new)
        if why:
            print(why, file=sys.stderr)
            return review.wait(state)
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
            print("NOTE: no base wiki page names %s yet" % ", ".join(noted))
        ar.run_routines(top, cfg, state)
        if tested != state.get("pr_head"):
            ar.restatus(top, cfg, state, tested)
        why = land(top, base, state["pr"], tested)
        why and ar.fail(state, "gh could not merge %s: %s" % (state["pr"], why))
    queue and pods and pods.merge_lock(os.path.abspath(common))
    ar.mark_merged(state)
    release.save(state, "merged %s (auto_merge)" % state["pr"])
    print("MERGED %s into %s" % (state["pr"], base))
    leave_queue(path, slug)
    ar.finish(top, cfg, state)
    if wiki.top_of():
        wiki.cmd_publish(argparse.Namespace(slug=slug))
    return 0


if __name__ == "__main__":
    sys.exit(main())
