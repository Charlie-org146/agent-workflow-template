#!/usr/bin/env python3
"""Merge a finished goal's pull request into the base branch, then release. usage: merge.py SLUG [--go-head SHA]
       merge.py SLUG SLUG [SLUG] --batch [--go-head SHA]

Refuses unless "auto_merge" is true and the goal is done with its PR open. Runs the base's routines, merges
(`gh pr merge --match-head-commit`), releases (autorelease.py; failure: `release_error`) and publishes the wiki (wiki.py;
refused: `wiki_error`); a stale wiki page, REVIEW_HOLD, a private name, REQUIREMENT_MISSING or another pod's goal refuse
first. --go-head SHA: GO_HEAD unless the PR head is SHA; CI_PENDING, CI_RED, CI_MISSING unless its checks are green.
Setting merge_queue (off): GitHub's merge queue checks the moved base, so merge.py skips BASE_MOVED and prints MERGED
only once gh reports the pull request merged.

--batch (setting merge_batch, off): machines.py `batch` merges 2-3 green goals as one (commands.md).
Also the release pull request (`merge.advance`): pushes `release/vX-<slug>`, merges it with `gh pr merge --merge`.
"""
import argparse
import datetime
import importlib.util
import json
import os
import re
import subprocess
import sys
import time

sys.modules.setdefault("merge", sys.modules[__name__])
import autorelease as ar
import release
import review
import wiki


HERE = os.path.dirname(os.path.abspath(__file__))
MON = os.path.join(HERE, "..", "..", "workflow-monitoring", "scripts")


def one_review_unanswered(state):
  """DLF-1.3: a marked goal, or one needing a start review, merges only once its answer is saved."""
  path = os.path.join(MON, "..", "..", "workflow-delivery", "scripts", "start_review.py")
  if not os.path.exists(path):
    return "start_review.py is missing. Fix: reinstall the skills." if state.get("one_review") or state.get("start_required") else ""
  spec = importlib.util.spec_from_file_location("one_review_start", path)
  found = importlib.util.module_from_spec(spec)
  spec.loader.exec_module(found)
  return found.unanswered(state, os.getcwd())


def one_review_unapproved(state, top, runs, base, head):
  """DLF-1.3: the exact head being merged changes no Reviewed requirement beyond what its start review approved."""
  if not state.get("one_review"):
    return ""
  path = os.path.join(MON, "..", "..", "workflow-delivery", "scripts", "start_answer.py")
  if not os.path.exists(path):
    return "start_answer.py is missing. Fix: reinstall the skills. (ONE_REVIEW_UNAPPROVED)"
  spec = importlib.util.spec_from_file_location("one_review_answer", path)
  found = importlib.util.module_from_spec(spec)
  spec.loader.exec_module(found)
  more = found.unapproved(top, runs, state, "origin/" + base, head)
  return more and "the pull request changes a Reviewed requirement its start review didn't approve as it reads: %s. Nothing was merged. (ONE_REVIEW_UNAPPROVED)" % ", ".join(more) or ""


def _pods():  # MON-15: workflow-monitoring's graph.py, or None
  sys.path.append(MON)  # graph's proctree
  try:
    spec = importlib.util.spec_from_file_location("pods_graph", os.path.join(MON, "graph.py"))
    spec.loader.exec_module(mod := importlib.util.module_from_spec(spec))
    return mod
  except Exception:
    return None


pods = _pods()

# No terminal, no waiting: a prompt from git or gh must fail, not block.
os.environ.update(GIT_TERMINAL_PROMPT="0", GH_PROMPT_DISABLED="1", GIT_EDITOR="true", GIT_ASKPASS="true", SSH_ASKPASS="true")
if not sys.stdin or not sys.stdin.isatty():
  os.dup2(os.open(os.devnull, os.O_RDONLY), 0)


def run(args, cwd=None, **kw):
  return subprocess.run(args, cwd=cwd, capture_output=True, text=True, **kw)


def merge_pr(top, pr, head):
  return run(["gh", "pr", "merge", pr, "--merge"] + (["--match-head-commit", head] if head else []), top)


REACH = os.path.normpath(os.path.join(HERE, "..", "..", "workflow-regression", "scripts", "lanes_cli.py"))


def reach(top, paths):
  """Row ids PATHS can affect, or None for all."""
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
    ar.fail(state, "gh pr create for %s failed: %s. Side effects: branch %s pushed, no pull request "
                     "(partial). Fix: run merge.py %s again" % (branch, (made.stderr or "").strip()[-200:], branch, slug))
  state.update(release_pr=url, release_pr_branch=branch, release_pr_version=version)
  release.save(state, "release PR %s opened for v%s" % (url, version))
  print("RELEASE PR %s (%s)" % (url, title))


def pending(seen):
  return any(isinstance(item, dict) and (item.get("status") in PENDING or item.get("state") in PENDING)
             for item in seen.get("statusCheckRollup") or [])


def load(path):
  try:
    with open(path) as handle:
      return json.load(handle)
  except (OSError, ValueError):
    return None


def leave_queue(path, slug):
  for name in (slug, slug + ".beat"):
    gone = os.path.join(os.path.dirname(os.path.dirname(path)), "pr-queue", name)
    os.path.exists(gone) and os.unlink(gone)


def queued(top, pr):
  """True once gh reports the pull request MERGED, False if it closes or LOOP_QUEUE_WAIT seconds pass."""
  for _ in range(int(os.environ.get("LOOP_QUEUE_WAIT") or 900) // 10):
    state = view(top, pr).get("state")
    if state in ("MERGED", "CLOSED"):
      return state == "MERGED"
    time.sleep(10)
  return False


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
  if args.batch or len(args.slug) > 1:
    if not (args.batch and cfg.get("merge_batch") is True):
      sys.exit("REFUSED: several goals need --batch and merge_batch true. Nothing merged.")
    held = [s for s in args.slug if (load(os.path.join(os.path.abspath(common), "loop", "runs", s + ".cover.json")) or {}).get("claim")]
    held and sys.exit("REFUSED: %s ran with a cover and cannot join a batch; merge it alone: merge.py SLUG (COVER_NOBATCH)." % ", ".join(held))
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
  held = one_review_unanswered(state)
  held and sys.exit("REFUSED: %s Nothing was merged. (ONE_REVIEW_UNANSWERED)" % held)
  if pods:
    pods.refuse(state)
    pods.pr_queue("wait", runs, slug)  # an earlier pr lane holds the slot
    pods.merge_lock(os.path.abspath(common))
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
        sys.exit("REFUSED: this branch's latest commit is not on origin. Fix: run wiki.py prepare %s --commit." % slug)
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
    moved = not cfg.get("merge_queue") and base_moved(state, cfg, top)
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
    ar.label_part(top, cfg, state)
    if not state.get("branch") or run(["git", "fetch", "-q", "origin", state["branch"]], cwd=top).returncode:
      ar.fail(state, "could not fetch the goal branch %s to scan it; nothing was merged (PRIVATE_LIST)" % state.get("branch"))
    ar.check(state, top, "origin/" + base, {"release notes": ar.notes_text(state)}, True, head)
    loose = one_review_unapproved(state, top, runs, base, tested or head)
    loose and ar.fail(state, loose)
    held, noted = missing_ids(top, cfg, head)
    if held:
      ar.fail(state, "criterion rows name %s, which no wiki page on origin/%s names; nothing was merged. Fix: "
              "merge the goal that adds their text, then merge.py %s (REQUIREMENT_MISSING)" % (", ".join(held), base, slug))
    if noted:
      print("NOTE: no wiki page on the base names %s yet; merging anyway" % ", ".join(noted))
    ar.run_routines(top, cfg, state)
    if tested != state.get("pr_head"):
      ar.restatus(top, cfg, state, tested)
    done = merge_pr(None, state["pr"], tested)
    if done.returncode:
      ar.fail(state, "gh could not merge %s: %s" % (state["pr"], done.stderr.strip()[-300:]))
    if cfg.get("merge_queue") and not queued(top, state["pr"]):
      ar.fail(state, "the merge queue has not merged %s; nothing else changed" % state["pr"])
  at = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
  ar.mark_merged(state)
  state["updated"] = at
  state.setdefault("log", []).append("%s merged %s (auto_merge)" % (at, state["pr"]))
  with open(path + ".tmp", "w") as handle:
    json.dump(state, handle, indent=2)
  os.replace(path + ".tmp", path)
  print("MERGED %s into %s" % (state["pr"], base))
  print(run([sys.executable, OPERATE, "forward", base], top).stdout.strip())
  leave_queue(path, slug)
  ar.finish(top, cfg, state)
  if wiki.top_of():
    wiki.cmd_publish(argparse.Namespace(slug=slug))
  return 0


from merge_steps import advance, base_moved, missing_ids, file_issue  # noqa: E402,F401


if __name__ == "__main__":
  sys.exit(main())
