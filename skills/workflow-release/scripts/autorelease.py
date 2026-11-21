#!/usr/bin/env python3
"""The automatic release, called by merge.py: routines, then after the merge a version bump, the CHANGELOG entry, a push to
the base and a GitHub release (a release pull request on a protected base; with merge_queue, release.yml instead).
Failures: `release_error`. Commit, notes and label pass the private-name scan (PRIVATE_MODULE)."""
import datetime
import importlib.util
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile

import release
import wiki  # noqa: E402

# no prompt
os.environ.update(GIT_TERMINAL_PROMPT="0", GH_PROMPT_DISABLED="1", GIT_EDITOR="true", GIT_ASKPASS="true", SSH_ASKPASS="true")
if not sys.stdin or not sys.stdin.isatty():
  os.dup2(os.open(os.devnull, os.O_RDONLY), 0)

PUSH_TRIES = 3
SIBLING = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "workflow-delivery", "scripts"))
PROTECTED = re.compile(r"GH006|GH013|protected branch|through a pull request|rule violations", re.I)
LOADED = {}


def sibling(name):
  """(module, None), or (None, refusal)."""
  if name not in LOADED:
    path = os.path.join(SIBLING, name + ".py")
    try:
      spec = importlib.util.spec_from_file_location("delivery_" + name, path)
      module = importlib.util.module_from_spec(spec)
      spec.loader.exec_module(module)
    except Exception as error:  # noqa: BLE001
      return None, ("delivery's %s.py could not be loaded from %s (%s: %s); nothing pushed or merged"
        % (name, path, type(error).__name__, str(error)[:80]),
        "reinstall the skills, then run it again", "PRIVATE_MODULE")
    LOADED[name] = module
  return LOADED[name], None


def private_check(top, base, texts, pushed=False, head="HEAD"):
  """None to go on, else (why, fix, code)."""
  private, stop = sibling("private")
  if stop:
    return stop
  try:
    result = private.scan(top, base, texts, head)
    stop = private.refusal(result, base or "the base branch", pushed)
  except Exception as error:  # noqa: BLE001
    return "the private scan failed (%s); nothing was pushed" % error, "run private.py check, then again", "PRIVATE_LIST"
  if not stop and result["state"] == "none":
    print("NOTE: " + result["note"])
  return stop


def check(state, top, base, texts, pushed=False, head="HEAD"):
  stop = private_check(top, base, texts, pushed, head)
  if stop:
    fail(state, "%s. Fix: %s (%s)" % stop)


def notes_text(state):
  bullets = "\n".join("- " + item for item in state["release_bullets"]) or "- No code changes"
  return bullets + "\n\n## How to verify\n\n%s\n\nPull request: %s\n" % (state["release_steps"], state.get("pr", ""))


def protected(top, base):
  got = sh(["gh", "api", "repos/{owner}/{repo}/rules/branches/" + base], cwd=top)
  return got.returncode == 0 and '"type":"pull_request"' in got.stdout.replace(" ", "")


def sh(args, cwd=None):
  try:
    return subprocess.run(args, cwd=cwd, capture_output=True, text=True)
  except OSError as error:
    return subprocess.CompletedProcess(args, 127, "", str(error))


def sh_text(args, text, flag="--body-file", cwd=None):
  with tempfile.NamedTemporaryFile("w", suffix=".md", prefix="gh-text-", delete=False, encoding="utf-8", newline="\n") as f:
    f.write(text)
  try:
    return sh(args + [flag, f.name], cwd=cwd)
  finally:
    os.remove(f.name)


def fail(state, text):
  state["release_error"] = text if len(text) <= 400 else text[:330] + " ... " + text[-65:]
  report, note = state.get("report"), ""
  if not isinstance(report, dict):
    note = "" if report is None else "(the stored report was a %s and was reset) " % type(report).__name__
    report = state["report"] = {}
  report["text"] = ("%s %sRelease failed: %s" % (str(report.get("text") or ""), note, text)).strip()[:600]
  if state.get("release") != "merged":
    state["status"] = "failed"
  release.save(state, "release failed: " + text[:200])
  sys.exit("REFUSED: " + text)


def reopen(state, code):
  """A refused merge sends the goal back to pr."""
  state.update(status="running", step="pr")
  release.save(state, "merge refused (exit %d): run goal.py pr, then merge.py again" % code)
  return code


def mergeable(state):
  """merge.py's gate: a done goal with its PR, or a release_error."""
  return bool(state.get("pr")) and (state.get("status") == "done" or (state.get("status") == "failed" and bool(state.get("release_error"))))


def mark_merged(state):
  state["release"] = "cut" if state.get("release") == "cut" else "merged"
  state["status"] = "done"


def run_routines(top, cfg, state):
  """Routines come from the base: a pull request cannot add one."""
  shown = sh(["git", "show", "origin/%s:.loop/config.json" % cfg.get("base", "main")], cwd=top)
  try:
    routines = (json.loads(shown.stdout) if shown.returncode == 0 else cfg).get("routines") or []
  except ValueError:
    routines = cfg.get("routines") or []
  for item in routines:
    argv = ["sh", "-c", item] if isinstance(item, str) else list(item)
    name = item if isinstance(item, str) else " ".join(item)
    done = sh(argv, cwd=top)
    if done.returncode:
      tail = (done.stderr or done.stdout).strip()[-200:]
      fail(state, "routine %s exited %d before the merge, so nothing was merged: %s" % (name, done.returncode, tail))
    print("ROUTINE ok: %s" % name)


def stage_notes(top, state, cfg):
  if "release_bullets" not in state:
    state["release_bullets"] = release.subjects(release.base_of(top, cfg), top) + wiki.fixes_lines(top)
    state["release_steps"] = release.verify_steps(top, state["slug"]) or "No manual steps were recorded."
    release.save(state)


def stage_part(top, state):
  """The bump, read until the release commit exists."""
  if not state.get("release_part") or not (state.get("release_pushed") or state.get("release_pr")):
    part, reason = release.auto_need(top, state)
    state["release_part"], state["release_reason"] = ("patch", "a docs or test change") if part == "leave" else (part, reason)
    release.save(state)


def drop(top, tree, temp):
  sh(["git", "worktree", "remove", "--force", tree], cwd=top)
  shutil.rmtree(temp, ignore_errors=True)


def push_release_commit(top, cfg, state, part, to_branch=False):
  """(version, sha); (None, stderr) if the base refused the push. to_branch pushes release/vX-<slug>."""
  base, slug = cfg.get("base", "main"), state["slug"]
  temp = tempfile.mkdtemp(prefix="release-")
  tree = os.path.join(temp, "tree")
  try:
    for _ in range(PUSH_TRIES):
      if sh(["git", "fetch", "-q", "origin", base], cwd=top).returncode:
        fail(state, "could not fetch origin/%s" % base)
      sh(["git", "worktree", "remove", "--force", tree], cwd=top)
      if sh(["git", "worktree", "add", "-q", "--detach", tree, "origin/" + base], cwd=top).returncode:
        fail(state, "could not check out origin/%s" % base)
      version_file = cfg.get("version_file") or "VERSION"
      if os.path.isabs(version_file) or ".." in version_file.split("/"):
        fail(state, "version_file must be a path inside the repo")
      vpath = os.path.join(tree, version_file)
      cur = open(vpath).read().strip() if os.path.exists(vpath) else None
      version = "0.1.0" if cur is None else release.bump(cur, "minor" if part == "major" and cur.startswith("0.") else part)
      tag = "v" + version
      if sh(["git", "ls-remote", "--exit-code", "--tags", "origin", tag], cwd=top).returncode == 0:
        fail(state, "tag %s already exists" % tag)
      cpath = os.path.join(tree, "CHANGELOG.md")
      old = open(cpath).read() if os.path.exists(cpath) else ""
      day = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d")
      open(vpath, "w").write(version + "\n")
      open(cpath, "w").write(release.changelog_text(old, version, day, state["release_bullets"], state["release_steps"]))
      files = [version_file, "CHANGELOG.md"]
      if sh(["git", "add", "--"] + files, cwd=tree).returncode or sh(
        ["git", "commit", "-q", "-m", "Release %s (%s)" % (tag, slug), "--"] + files, cwd=tree).returncode:
        fail(state, "could not commit the release files")
      dest = "release/%s-%s" % (tag, slug) if to_branch else base
      texts = {"release notes": notes_text(state)}
      if to_branch:
        texts["release PR title"] = "Release %s (%s)" % (tag, slug)
      check(state, tree, "origin/" + base, texts)
      pushed = sh(["git", "push"] + ["--force"] * to_branch + ["origin", "HEAD:refs/heads/" + dest], cwd=tree)
      if pushed.returncode == 0:
        return version, sh(["git", "rev-parse", "HEAD"], cwd=tree).stdout.strip()
      if to_branch:
        fail(state, "push of %s was rejected: %s" % (dest, pushed.stderr.strip()[-200:]))
      if PROTECTED.search(pushed.stderr):
        print("NOTE: origin/%s is protected; the release goes through a pull request" % base)
        return None, pushed.stderr
            # the base moved: redo the bump on top
    fail(state, "push to %s was rejected %d times: %s" % (base, PUSH_TRIES, pushed.stderr.strip()[-200:]))
  finally:
    drop(top, tree, temp)


def restatus(top, cfg, state, head):
  """Post the pr lane's result for a wiki-only head."""
  module, stop = sibling("private")
  if not stop:
    module.pr_result(top, cfg.get("base", "main"), head, state["branch"], True)


STAMPS = ("VERSION", "CHANGELOG.md", ".loop/regression-runs.tsv", ".loop/regression-issues.tsv")
ROW = re.compile(r":\d{6} 100(?:644|755) \w+ \w+ [AM]\t(.+)")


def tems(top, old, new, extra="", allow=None):
  """Tree equal modulo stamps: old to new only edits regular files at STAMPS paths (and allow's)."""
  done = sh(["git", "diff", "--raw", "--no-renames", old, new], cwd=top)
  rows = [ROW.fullmatch(line) for line in done.stdout.splitlines()]
  return done.returncode == 0 and bool(rows) and all(
    m and (m[1] in STAMPS or m[1] == extra or bool(allow and allow(m[1]))) for m in rows)


def carried(top, cfg, state, sha):
  """The pr lane passed and the head is its parent plus stamps."""
  return state.get("statuses") == "ok" and tems(top, sha + "^", sha, cfg.get("version_file") or "VERSION")


def lane_at(top, cfg, sha):
  """(exit code or None, output) of the affected rows at sha."""
  temp = tempfile.mkdtemp(prefix="release-status-")
  tree, code, text = os.path.join(temp, "tree"), None, "could not check out the head"
  try:
    if sh(["git", "worktree", "add", "-q", "--detach", tree, sha], cwd=top).returncode == 0:
      try:
        script = os.path.join(SIBLING, "..", "..", "workflow-regression", "scripts", "regression.py")
        done = subprocess.run([sys.executable, script, "run", cfg.get("ci_levels") or "nightly", "--reuse", "--tier", "goal",
            "--timeout", "900"], cwd=tree, capture_output=True, text=True, errors="replace", timeout=1200)
        code, text = done.returncode, done.stdout + done.stderr
      except (OSError, subprocess.TimeoutExpired) as error:
        text = "the lane could not finish: %s" % error
  finally:
    drop(top, tree, temp)
  return code, text


def release_statuses(top, cfg, state, branch, sha):
  """Post the lane's result for the release PR head under each required check."""
  module, stop = sibling("private")
  if stop or not sha or state.get("release_status") == "success":
    return
  state.pop("release_status_why", None)
  if sh(["git", "cat-file", "-e", sha + "^{commit}"], cwd=top).returncode:
    sh(["git", "fetch", "-q", "origin", branch], cwd=top)
  if carried(top, cfg, state, sha):
    print("CARRIED the passing lane to the release head %s" % sha[:12])
    ok = True
  else:
    code, text = lane_at(top, cfg, sha)
    rows = re.findall(r"^FAIL (\S+)", text, re.M)
    ok = code == 0
    if not ok and not rows:  # nothing failed: no blame on an untested head
      state["release_status"], state["release_status_why"] = "untested", "the lane at head %s gave no result: %s" % (
        sha[:12], " ".join((text or "(no output)").split())[-160:])
      return print("RELEASE_STATUS untested: " + state["release_status_why"])
    if rows:
      state["release_status_why"] = "rows %s failed at head %s" % (", ".join(rows[:8]) + (" +%d more" % (len(rows) - 8) * (len(rows) > 8)), sha[:12])
  posted = module.pr_result(top, cfg.get("base", "main"), sha, branch, ok)
  state["release_status"] = "success" if ok and posted else "failure"


RED = ("FAILURE", "ERROR", "TIMED_OUT", "CANCELLED", "STARTUP_FAILURE", "ACTION_REQUIRED")


def main_reds(top, base, info, red):
  """(failing rows, log URLs) if every red check is a known main red, else None."""
  show = lambda f: [x.split("\t") for x in sh(["git", "show", "origin/%s:.loop/%s" % (base, f)], cwd=top).stdout.splitlines()]
  known = {x[0] for x in show("regression-known.tsv")} | {x[0] for x in show("regression-runs.tsv") if x[1:2] == ["FAIL"]}
  rows, urls = set(), []
  for c in info.get("statusCheckRollup") or []:
    if isinstance(c, dict) and str(c.get("name") or c.get("context")) in red:
      url = str(c.get("detailsUrl"))
      log = sh(["gh", "api", "repos/{owner}/{repo}/actions/jobs/%s/logs" % url.split("?")[0].rsplit("/", 1)[-1]], cwd=top)
      found = set(re.findall(r"^\S+ FAIL (\S+)$", log.stdout, re.M)) if log.returncode == 0 else set()
      if not found or not found <= known:
        return None
      rows |= found
      urls.append(url)
  return sorted(rows), urls


def go_gate(top, base, info, go):
  """None, or the refusal, unless the head is the GO's and all checks are green (#5171)."""
  head = str(info.get("headRefOid"))
  if len(go) < 7 or not head.startswith(go):
    return "REFUSED (GO_HEAD): the GO was for %s, the PR head is %s. Nothing merged." % (go[:12], head[:12])
  module, stop = sibling("private")
  got = None if stop else module.required_checks(top, base)
  end = lambda c: str(c.get("conclusion") or c.get("state") or "").upper()
  seen = {str(c.get("name") or c.get("context")): "CI_PENDING" if end(c) in ("", "PENDING", "EXPECTED") or str(c.get("status") or "COMPLETED").upper() != "COMPLETED"
    else "CI_RED" if end(c) in RED else "" for c in info.get("statusCheckRollup") or [] if isinstance(c, dict)}
  need = sorted(set(got[0]) | set(got[1]) or seen) if got is not None else ["the required checks"]
  for code in ("CI_RED", "CI_PENDING", "CI_MISSING"):
    names = [n for n in need if seen.get(n, "CI_MISSING") == code] or (["no check reported"] if code == "CI_MISSING" and not need else [])
    found = names and code == "CI_RED" and main_reds(top, base, info, names)
    if found:
      print("GO_HEAD ok: %s red only on known main reds (%s); logs: %s" % (", ".join(names), ", ".join(found[0]), ", ".join(found[1])))
    elif names:
      return "REFUSED (%s): %s on head %s. Nothing merged. Fix: wait for green CI, then merge.py again." % (
        code, ", ".join(names), head[:12])


def status_held(state, url, number, seen=None):
  """Refuse (RELEASE_STATUS_*, RELEASE_CHECKS_FAILED) if the release PR head has no passing status."""
  red = [str(c.get("name") or c.get("context")) for c in (seen or {}).get("statusCheckRollup") or []
    if isinstance(c, dict) and (c.get("conclusion") in RED or c.get("state") in RED)]
  why = state.get("release_status") in ("failure", "untested") and state.get("release_status_why")
  if red and not why:
    fail(state, "the release PR %s (#%s) can't merge: required checks failed: %s. No owner merge is needed. Fix the cause, "
      "run merge.py %s again (RELEASE_CHECKS_FAILED)"
      % (url, number, ", ".join(sorted(set(red))[:8]), state["slug"]))
  if not why:
    return
  fail(state, "the release PR %s (#%s) can't merge: %s. No owner merge is needed. Fix the cause, run merge.py %s again "
    "(%s)" % (url, number, why, state["slug"], "RELEASE_STATUS_" + state["release_status"].upper().replace("FAILURE", "FAILED")))


def create_release(top, cfg, state, version, target):
  tag, text = "v" + version, notes_text(state)
  check(state, top, None, {"release notes": text})
  seen = sh(["gh", "release", "view", tag, "--json", "targetCommitish,url"], cwd=top)
  if seen.returncode == 0:  # a crash after create is adopted; others are not ours
    try:
      info = json.loads(seen.stdout)
    except ValueError:
      info = {}
    if info.get("targetCommitish") == target:
      print("ADOPTED release %s at %s" % (tag, target[:12]))
      return info.get("url") or ""
    fail(state, "a GitHub release %s exists at %s, not at this release commit %s; nothing was created. "
      "Fix: keep or delete it (gh release view %s), then run merge.py %s (RELEASE_EXISTS)"
      % (tag, info.get("targetCommitish") or "another target", target[:12], tag, state["slug"]))
  made = sh_text(["gh", "release", "create", tag, "--title", tag, "--target", target], text, "--notes-file", top)
  if made.returncode:
    fail(state, "gh release create %s failed after the push; run merge.py again: %s" % (
        tag, (made.stderr or made.stdout).strip()[-200:]))
  return (made.stdout.strip().splitlines() or [""])[-1]


def label_part(top, cfg, state):
  """merge_queue: the part is a release:<part> label (default patch)."""
  part = state.get("release_part")
  if cfg.get("merge_queue") and part in ("minor", "major"):
    check(state, top, None, {"label": "release:" + part})
    sh(["gh", "label", "create", "release:" + part, "--force"], cwd=top)
    sh(["gh", "pr", "edit", state["pr"], "--add-label", "release:" + part], cwd=top)


def finish(top, cfg, state):
  """After the merge."""
  if state.get("release") == "cut" and state.get("release_url"):
    print("ALREADY released %s as v%s" % (state["slug"], state.get("release_version")))
    return
  base = cfg.get("base", "main")
  if cfg.get("merge_queue"):  # REL-15: release.yml tags on push; no commit or pull request
    print("RELEASE from CI: tags %s (part %s)" % (state["slug"], state.get("release_part")))
    return True
  if not state.get("release_pushed"):
    stage_notes(top, state, cfg)
    stage_part(top, state)
    part, reason = state["release_part"], state["release_reason"]
    version = sha = None
    if not state.get("release_pr") and not protected(top, base):
      version, sha = push_release_commit(top, cfg, state, part)
    if version is None:  # a protected base: the release pull request lands VERSION and CHANGELOG
      import merge as release_pr
      got = release_pr.advance(top, cfg, state)
      if not got:
        return False
      version, sha = got
    state.update(release_pushed=version, release_part=part, release_target=sha)
    release.save(state, "version pushed: v%s (%s)" % (version, reason))
  version = state["release_pushed"]
  url = create_release(top, cfg, state, version, state.get("release_target") or base)
  state.update(release="cut", release_version=version, release_url=url, status="done", waiting=None)
  for key in ("release_error", "release_pr_waiting"):
    state.pop(key, None)
  release.save(state, "release v%s published %s" % (version, url))
  print("RELEASED v%s %s (%s bump)" % (version, url, state["release_part"]))
  return True
