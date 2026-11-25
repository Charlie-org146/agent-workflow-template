"""the merge steps: base check, release advance, issue filing"""
import os
import re
import subprocess
os.environ.update(GIT_TERMINAL_PROMPT="0", GH_PROMPT_DISABLED="1", GIT_EDITOR="true", GIT_ASKPASS="true", SSH_ASKPASS="true")


def advance(top, cfg, state, again=False):
  """(version, merge commit) once the release PR merges, else None."""
  if not state.get("release_pr"):
    _s.start(top, cfg, state)
  url, version, slug = state["release_pr"], state["release_pr_version"], state["slug"]
  seen, said = _s.view(top, url), ""
  if seen.get("state") == "OPEN":
    _s.ar.check(state, top, None, {"release PR title": _s.title_of(version, slug), "release notes": _s.ar.notes_text(state)})
    _s.ar.release_statuses(top, cfg, state, state["release_pr_branch"], seen.get("headRefOid"))
    merged = _s.ar.sh(["gh", "pr", "merge", url, "--merge"], cwd=top)
    said = (merged.stderr or merged.stdout).strip()[-200:]
    seen = _s.view(top, url)
  status, number = seen.get("state"), seen.get("number") or url.rstrip("/").split("/")[-1]
  if status == "MERGED":
    oid = (seen.get("mergeCommit") or {}).get("oid") or ""
    base, vfile = cfg.get("base", "main"), cfg.get("version_file") or "VERSION"
    _s.ar.sh(["git", "fetch", "-q", "origin", base], cwd=top)
    found = _s.ar.sh(["git", "show", "%s:%s" % (oid, vfile)], cwd=top)
    if oid and found.stdout.strip() != version:
      tip = _s.ar.sh(["git", "rev-parse", "origin/" + base], cwd=top).stdout.strip()
      fixed = _s.ar.sh(["git", "show", "origin/%s:%s" % (base, vfile)], cwd=top)
      oid, found = (tip, fixed) if tip and fixed.stdout.strip() == version else (oid, found)
    if not oid or found.stdout.strip() != version:
      _s.ar.fail(state, "the release PR %s merged, but VERSION at its merge commit %s is %r, not %s; no "
              "release was created. Fix: set VERSION on the base by hand, then run merge.py %s "
              "(RELEASE_VERSION_MISMATCH)" % (url, oid[:12] or "(none)", found.stdout.strip(), version, slug))
    state.pop("release_pr_waiting", None)
    print("MERGED the release PR %s at %s" % (url, oid[:12]))
    return version, oid
  if not again and (status == "CLOSED" or (status == "OPEN" and seen.get("mergeStateStatus") in ("DIRTY", "BEHIND"))):
    if status == "OPEN":
      _s.ar.sh(["gh", "pr", "close", url], cwd=top)
    _s.forget(state, "%s was %s" % (url, "closed unmerged" if status == "CLOSED" else "behind the base"))
    return advance(top, cfg, state, again=True)
  if status == "OPEN" and seen.get("reviewDecision") not in _s.REVIEW and (_s.pending(seen) or seen.get("mergeStateStatus") == "UNKNOWN"):
    state["release_pr_waiting"] = "checks pending on %s (#%s)" % (url, number)
    state.pop("release_error", None)
    _s.release.save(state, "waiting: " + state["release_pr_waiting"])
    print("WAITING %s: required checks are pending on the release PR %s; the next merge.py %s run merges it"
          % (slug, url, slug))
    return None
  state["release_tries"] = state.get("release_tries", 0) + 1
  _s.ar.status_held(state, url, number, seen)
  why = "a review is required" if seen.get("reviewDecision") in _s.REVIEW else "it is %s, %s" % (
      status or "unreadable", seen.get("mergeStateStatus") or said or "no reason given")
  _s.ar.fail(state, "the release PR %s (#%s) can't merge: %s; it needs the owner to approve and merge it. Fix: "
          "gh pr merge %s --merge, then merge.py %s. Side effects: branch %s pushed and the pull request open "
          "(partial); try %d (RELEASE_PR_BLOCKED)" % (
              url, number, why, number, slug, state.get("release_pr_branch"), state["release_tries"]))


def base_moved(state, cfg, top):
  """None to go ahead, else (exit code, refusal): the base moved in paths this goal's rows reach (2), or no fetch (3)."""
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
  now = _s.run(["git", "rev-parse", "origin/" + base], cwd=top).stdout.strip()
  if now == was:
    return None
  def names(a, b):
    done = _s.run(["git", "diff", "--name-only", "--no-renames", a, b], cwd=top)
    return None if done.returncode else [p for p in done.stdout.split("\n") if p]
  theirs, ours = [None if x is None else _s.reach(top, x) for x in (names(was, now), names(was, state.get("pr_head") or "HEAD"))]
  if theirs is None or ours is None or theirs & ours:
    return 2, "REFUSED (BASE_MOVED): %s moved in paths this goal's rows reach (lane on %s, base now %s). Fix: goal.py " \
              "pr %s, then merge.py %s" % (base, was[:12], now[:12], slug, slug)
  print("NOTE: %s moved in paths this goal's rows don't reach; merging" % base)
  return None


def missing_ids(top, cfg, head="HEAD"):
  """(held, noted): requirement IDs its criterion rows add that no origin/<base> wiki page names."""
  base = "origin/" + cfg.get("base", "main")
  folder = (cfg.get("wiki_dir") or "docs/wiki").strip("/")
  added = _s.run(["git", "diff", "-U0", base + "..." + head, "--", ".loop/regression.tsv"], cwd=top).stdout
  ids = set()
  for line in added.splitlines():
    cells = line[1:].split("\t") if line.startswith("+") and not line.startswith("+++") else []
    if len(cells) > 3 and (cells[6:7] in ([], [""], ["criterion"])) and re.match(r"^[A-Z]{2,5}-\d+$", cells[3]):
      ids.add(cells[3])
  if not ids:
    return [], []
  def pages(ref):
    found = _s.run(["git", "ls-tree", "--name-only", ref, folder + "/"], cwd=top).stdout.split()
    return found, "\n".join(_s.run(["git", "show", "%s:%s" % (ref, n)], cwd=top).stdout for n in found if n.endswith(".md"))
  names, text = pages(base)
  both = text + "\n" + pages(head)[1]
  gone = sorted(i for i in ids if not re.search(r"\b%s\b" % re.escape(i), both))
  held = [i for i in gone if names and re.search(r"\b%s\d+\b" % re.escape(i.split("-")[0] + "-"), text)]
  return held, [i for i in gone if i not in held]


def file_issue(top, page, texts):
  title = "Docs: %s has DOC-19/DOC-4 findings" % page
  stone = "Backlog: " + (page[11:] if page.startswith("How-to-use-") else "Documentation" if "/" in page or page == "Home" else page)
  gh = lambda *a, **k: _s.run(["gh"] + list(a), top, **k)
  try:
    held = gh("issue", "list", "--state", "open", "--limit", "1000", "--json", "title", "-q", ".[].title")
    if held.returncode or title in held.stdout.splitlines():
      return "no issue filed (gh)" if held.returncode else "its issue is open"
    gh("api", "-X", "POST", "repos/{owner}/{repo}/milestones", "-f", "title=" + stone)
    return "filed " + gh("issue", "create", "--title", title, "--milestone", stone, "--body-file", "-", input="\n".join(texts)).stdout.split()[-1]
  except (OSError, IndexError):
    return "no issue filed (gh)"


import merge as _s  # noqa: E402
