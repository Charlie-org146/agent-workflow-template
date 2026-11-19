#!/usr/bin/env python3
"""The goal tier of `regression.py run land --reuse --tier goal` (REG-4), and `--kind`. Imported by regression.py, not run.

A goal lane runs the rows whose closure reaches a file changed since the branch's merge-base, rows added or changed in
.loop/regression.tsv, root runners, a usable record's FAIL rows and any flaky row; a path no row maps is a Note, never a full
run (REG-7). FLAKY (REG-9): a row whose result flipped on the same clean commit, host and python keeps its raw PASS/FAIL and a
sticky `flaky` flag. Plan cache: <git common dir>/loop/plans/; LANES_NO_CACHE=1 turns it off (references/commands.md).
"""
import hashlib
import json
import math
import os
import platform
import socket
import subprocess
import sys

import lanes
import narrow
from lanes import guard
from narrow import features, md_table, refuse
from slots import KIND, OTHER, RUNS, SEEN, STATES, cell, issues_of, key_of, tsv  # slots sets GIT_TERMINAL_PROMPT

KNOWN = ".loop/regression-known.tsv"
KINDS = {"requirement": "criterion", "workflow": "workflow", "defect": "defect"}
BASE = None


def kinds(rows, kind):
  """A1e: only the rows of one kind; requirement means category criterion."""
  return rows if not kind else [row for row in rows if row["category"] == KINDS[kind]]


def target(root, args):
  """A goal lane plans from goal_levels: land (default), or nightly for land and nightly rows."""
  return "nightly" if args.tier and args.target == "land" and config(root).get("goal_levels") == "nightly" else args.target


def config(root):
  try:
    data = json.load(open(os.path.join(root, ".loop", "config.json")))
  except (OSError, ValueError):
    data = {}
  return data if isinstance(data, dict) else {}


def merge_base(root, base):
  for ref in ("origin/" + base, base):
    out = lanes.git(root, "merge-base", "HEAD", ref)
    if out and out.strip():
      return out.strip()
  return None


def usable(root, record, base):
  """(record or None, usable): usable only when its merge-base equals the current one."""
  old, _ = lanes.load(record, root)
  return old, bool(old and base and old.get("merge_base") == base)


def current(root, name):
  try:
    lines = open(os.path.join(root, ".loop", name)).read().splitlines()
  except OSError:
    return {}
  return {line.split("\t")[0]: line for line in lines if line.strip() and line[0] != "#"}


def changed(root, commit, memo):
  seen = memo.setdefault("from", {})
  if commit not in seen:
    seen[commit] = lanes.changed(root, commit) or []
  return seen[commit]


def status(root):
  """git status lines with unquoted non-ASCII paths, or None when git failed."""
  try:
    out = lanes.git(root, "-c", "core.quotepath=false", "status", "--porcelain", "--no-renames", "--untracked-files=all")
  except UnicodeError:
    return None
  return None if out is None else out.splitlines()


def loop_state(root, lines):
  """A digest of the loop's uncommitted files (lanes.BOOKKEEPING), which lanes.dirty ignores."""
  digest = hashlib.sha256()
  for line in sorted(lines or []):
    if line[3:].strip('"').startswith(lanes.BOOKKEEPING):
      digest.update(line.encode())
      try:
        with open(os.path.join(root, line[3:].strip('"')), "rb") as handle:
          digest.update(handle.read())
      except OSError:
        pass
  return digest.hexdigest()


def clean(lines):
  """Whether git status worked and lists nothing but the loop's own files."""
  return lines is not None and all(line[3:].strip('"').startswith(lanes.BOOKKEEPING) for line in lines)


def unsafe(root, cache):
  """Why the plan must not be saved, or None: it read a file outside the repo or an ignored one."""
  names, top = set(cache.get("text", ())), os.path.realpath(root)
  for item, value in cache.items():
    if isinstance(item, tuple) and item[0] in ("closure", "walk"):
      names |= set(value[0] if item[0] == "closure" else value)
  seen = set()
  for name in names:
    real = os.path.realpath(os.path.join(root, name))
    if not (real + os.sep).startswith(top + os.sep):
      return "symlink outside repo"
    seen |= {name, os.path.relpath(real, top)}
  text = "\0".join(sorted(n for n in seen if not n.endswith("/")))
  done = subprocess.run(["git", "check-ignore", "--stdin", "-z"], cwd=root, capture_output=True,
    input=text.encode("utf-8", "surrogateescape"))
  return "ignored file read" if done.returncode != 1 else None


def key(root, lines=None):
  """(sha256 hex, parts) of the plan cache's key."""
  lines = status(root) if lines is None else lines
  try:
    with open(os.path.join(root, lanes.TABLE), "rb") as handle:
      rows = hashlib.sha256(handle.read()).hexdigest()
  except OSError:
    rows = ""
  parts = ["1", lanes.runner(), (lanes.git(root, "rev-parse", "HEAD") or "").strip(), rows,
    "1" if os.environ.get("LANES_WIDE") == "1" else "0", loop_state(root, lines)]
  return hashlib.sha256(json.dumps(parts).encode()).hexdigest(), parts


def plan_file(record):
  """The record's path with its tests folder swapped for plans."""
  folder, name = os.path.split(record)
  return os.path.join(os.path.dirname(folder), "plans", name)


def lead(root, picked, record, cache):
  """Print the PLAN_CACHE line and seed the cache; (file, key) when a miss may be saved."""
  off = os.environ.get("LANES_NO_CACHE", "").lower() in ("1", "true", "yes")
  lines = status(root) if record and not off else None
  left = [line for line in lines or [] if not line[3:].strip('"').startswith(lanes.BOOKKEEPING)]
  path, now = (plan_file(record), key(root, lines)) if record and not off and lines is not None else (None, None)
  line = "off (LANES_NO_CACHE=1)" if off else "none (no branch)" if not record else \
    "dirty (git status failed, cache not used)" if lines is None else \
    "dirty (%d paths, cache not used)" % len(left) if left else narrow.warm(path, now, picked, cache)
  print("PLAN_CACHE: " + line)
  return (path, now) if line.startswith("miss") else (None, None)


def moved(root, old, base):
  """What the base brought in since the record's merge-base: those rows rerun."""
  was = (old or {}).get("merge_base")
  out = lanes.git(root, "diff", "--name-only", "--no-renames", was, base) if was and base and was != base else ""
  return (out or "").split()


def ancestor(root, commit, memo):
  """lanes.ancestor once per commit per plan."""
  cache = memo.setdefault("anc", {})
  if commit not in cache:
    cache[commit] = lanes.ancestor(root, commit)
  return cache[commit]


def since(root, row, old, ok, base, memo):
  """(commit to compare the row's table line with, paths changed for this row)."""
  prior = (old or {}).get("rows", {}).get(row["id"])
  seen = bool(prior) and ancestor(root, prior["commit"], memo)
  if seen and ok:
    return prior["commit"], changed(root, prior["commit"], memo)
  extra = changed(root, prior["commit"], memo) if seen else []
  return base, sorted(set(changed(root, base, memo)) | set(extra) | set(memo["moved"]))


def hit(root, row, path, at, cache, memo):
  if path == lanes.TABLE:
    return lanes.reads_table(root, row["command"], cache)
  if path == KNOWN:
    return lanes.table(root, at, "regression-known.tsv", memo).get(row["id"]) != memo["known"].get(row["id"])
  if path == narrow.CONFIG:
    return narrow.config_hit(root, at, row["command"], cache)
  return lanes.touches(root, row["command"], path, cache)


def reason(root, row, old, ok, base, cache, memo):
  """Why this row runs, or ''."""
  if ok and old["rows"].get(row["id"], {}).get("status") == "FAIL":
    return "failure rerun"
  if ok and old["rows"].get(row["id"], {}).get("status") == "SKIPPED":
    return "skipped last time"
  at, paths = since(root, row, old, ok, base, memo)
  if lanes.table(root, at, "regression.tsv", memo).get(row["id"]) != memo["tsv"].get(row["id"]):
    return "new row"
  found = next((p for p in paths if hit(root, row, p, at, cache, memo)), None)
  prior = ok and old["rows"].get(row["id"])
  if found and prior and ancestor(root, prior["commit"], memo) and not any(hit(root, row, p, base, cache, memo) for p in changed(root, base, memo)):
    return ""
  if found:
    return "reaches " + found
  if paths and lanes.closure(root, row["command"], cache)[1]:
    return "root runner"
  return "failure rerun (flaky: never reused)" if (old or {}).get("rows", {}).get(row["id"], {}).get("flaky") else ""


def quiet(path, gone):
  """Paths the unmapped rule ignores: deleted ones, the loop's tables and files no row reads."""
  return path in gone or path in (lanes.TABLE, KNOWN) or path.startswith(lanes.BOOKKEEPING) or any(
    path == n or (n.endswith("/") and path.startswith(n)) for n in lanes.NO_EFFECT)


def unmapped(root, picked, base, cache):
  """(paths no row maps, deleted paths) the goal changed since the merge-base."""
  gone = lanes.deleted(root, base)
  deps = [lanes.closure(root, row["command"], cache)[0] for row in picked]
  return [p for p in lanes.changed(root, base) or [] if not quiet(p, gone) and not any(lanes.hits(p, d) for d in deps)], gone


def notes(loose, gone):
  """The advisory UNMAPPED lines (DX-15, DX-18): the rows naming a path no row maps, and the runners."""
  return ["UNMAPPED %s: no row declares it. Note: the rows that name it and the runners run; declare it in the "
    "# reads: header of the row that tests it to map it" % p for p in loose] + [
    "UNMAPPED %s: deleted. Note: the rows that name it and the runners run" % p for p in gone]


def picks(root, picked, paths, old, ok, cache, memo):
  """{row id: why} for the rows a path no row maps (or a deleted one) selects."""
  found = {}
  for row in picked:
    mine = [p for p in paths if p in since(root, row, old, ok, BASE, memo)[1]]
    if mine and lanes.hits(lanes.RUNNER, lanes.closure(root, row["command"], cache)[0]):
      found[row["id"]] = "root runner (unmapped path)"
    elif mine and lanes.names_any(root, row["command"], mine, cache):
      found[row["id"]] = "names an unmapped path"
  return found


def rank(because):
  """Run order (#531): new or changed rows, reruns, reaches, then root runners and picks."""
  return 0 if because.startswith("new row") else 1 if because.startswith(("failure", "skipped")) else 3 if because.startswith(
    ("root runner", "names")) else 2


def plan(root, picked, record):
  """(to run ids in tier order, reused ids, usable record or None, why no plan or ''); prints its plan lines."""
  global BASE
  name = config(root).get("base") or "main"
  BASE = merge_base(root, name)
  cache, memo = {}, {"tsv": current(root, "regression.tsv"), "known": current(root, "regression-known.tsv")}
  saved, now = lead(root, picked, record, cache)
  old, ok = usable(root, record, BASE)
  memo["moved"] = moved(root, old, BASE)
  loose, gone, why = [], [], {}
  full, text, lines = "no merge-base with %s" % name, "can't tell what this branch changed (a shallow clone or a " \
    "missing base ref), so every row is a candidate and the time budget keeps what fits", []
  if BASE:
    loose, gone = unmapped(root, picked, BASE, cache)
    why = {row["id"]: reason(root, row, old, ok, BASE, cache, memo) for row in picked}
    lines, full = notes(loose, gone), ""
    for rid, because in (picks(root, picked, loose + gone, old, ok, cache, memo) if loose or gone else {}).items():
      why[rid] = why[rid] or because
  why = {row["id"]: why.get(row["id"]) or ("FULL" if full else "") for row in picked}
  todo = [row["id"] for row in picked if why[row["id"]]]
  todo.sort(key=lambda rid: rank(why[rid]))
  reused = [rid for rid in why if ok and rid in old["rows"] and not why[rid]]
  print("\n".join(lines)) if lines else None
  summary(picked, todo, why, len(loose) + len(gone), (full, text), old if ok else None)
  failed = None
  if saved:
    again = status(root)
    if clean(again) and key(root, again) == now:
      failed = unsafe(root, cache) or narrow.store(saved, now, cache)
  print("PLAN_CACHE: not saved (%s)" % failed) if failed else None
  return todo, reused, old if ok else None, full


def summary(picked, todo, why, count, full, old):
  """The kind line (FULL, REUSED or AFFECTED), one SELECTED line per row and the ROWS line."""
  if full[0]:
    print("FULL (%s): %s" % full)
  elif not todo and old:
    print("REUSED %d rows from %s (%s)" % (len(picked), old["commit"][:12], old["at"]))
  else:
    ids = ", ".join(todo[:10]) + (", +%d more" % (len(todo) - 10) if len(todo) > 10 else "")
    print("AFFECTED %d of %d rows (%s): changed since %s" % (len(todo), len(picked), ids or "none", BASE[:12]))
  for rid in todo:
    print("SELECTED %s: %s" % (rid, why[rid]))
  first = [why[rid].split()[0] for rid in todo]
  print("ROWS: %d selected (%d affected, %d new, %d root runners, %d failure reruns), %d reused; unmapped: %d" % (
      len(todo), first.count("reaches"), first.count("new"), first.count("root"), first.count("failure"),
      len(picked) - len(todo), count))


def suite_time(root, args, head, results, day):
  """REG-7: a plain full `run nightly` appends `<sha> TAB full TAB <seconds> TAB <date>` to loop/suite-times.tsv and prints SUITE_TIME."""
  if args.target != "nightly" or args.reuse or args.tier or args.kind or not results:
    return
  seconds = int(round(sum(item["seconds"] for item in results)))
  folder = os.path.join(root, (lanes.git(root, "rev-parse", "--git-common-dir") or ".git").strip(), "loop")
  os.makedirs(folder, exist_ok=True)
  with open(os.path.join(folder, "suite-times.tsv"), "a") as handle:
    handle.write("%s\tfull\t%d\t%s\n" % (head, seconds, day))
  print("SUITE_TIME %d" % seconds)


def runner():
  return socket.gethostname(), platform.python_version()


def previous(record):
  """The lane record's rows as written (the same commit means the same code)."""
  try:
    with open(record) as handle:
      rows = json.load(handle).get("rows")
    return rows if isinstance(rows, dict) else {}
  except (OSError, ValueError, TypeError, AttributeError):
    return {}


def compare(prev, state, head, clean):
  """The row's flaky flag after this result: the commit it flipped on, or ''."""
  prev = prev if isinstance(prev, dict) else {}
  mark = str(prev.get("flaky") or "")
  if not clean or state == "SKIPPED" or prev.get("status") == "SKIPPED":
    return mark
  if prev.get("commit") == head and prev.get("clean") == "yes" and (prev.get("host"), prev.get("python")) == runner():
    if mark == head or (prev.get("status") == "PASS") != (state == "PASS"):
      return head
  return "" if state == "PASS" and mark != head else mark


def word(passed):
  return "passed" if passed else "failed"


def flaky_apply(record, results, head, clean):
  """Give each result its commit, clean, host, python and flaky fields; return the FLAKY lines."""
  rows, (host, python), lines = previous(record) if record else {}, runner(), []
  for item in results:
    item.update(commit=head, clean="yes" if clean else "no", host=host, python=python)
    if not clean:
      continue
    item["flaky"] = compare(rows.get(item["id"]), item["state"], head, clean)
    if item["flaky"] == head:
      now, was = item["state"] == "PASS", (rows.get(item["id"]) or {}).get("status") == "PASS"
      seen = "%s then %s" % (word(was), word(now)) if was != now else "%s again, still flaky" % word(now)
      lines.append("FLAKY %s: %s on %s (same clean tree; runner %s, python %s). Note: the result counts as %s; "
        "the row is never reused while flaky" % (item["id"], seen, head[:12], host, python, word(now)))
  return lines


# <tests
def fields(row, found, ran, issues, markdown=False, raw=False):
  """The one fixed format for one row: test, kind, guards, checks, runs, result, seen failing."""
  status, day, flag = (tuple(ran.get(row[0], ("not run", ""))) + ("",))[:3]
  known = issues.get(row[7], ()) if row[6] == "defect" else ()
  if len(known) > 2 and known[2] and known[0] == "open" and not (status == "PASS" and day > known[2][:10]):
    status, day = "failing (issue reopened)", known[2][:10]
  return [cell(item, raw) for item in (row[0], KIND.get(row[6] or "criterion", row[6]), guard(row, found, issues, markdown),
      row[5] or "-", RUNS.get(row[1], row[1] or "-"), (status + " " + day).strip() + flag,
      row[4] if SEEN.match(row[4]) else "no")]


def entries(root, results=None, markdown=False, raw=False):
  """[(feature, [fields])] in page order, then Other; draft rows left out; with results, only the rows that ran."""
  titles, found = features(root)
  ran = {row[0]: ((row + [""] * 5)[1:3] + [" FLAKY" if (row + [""] * 5)[4] else ""]) for row in tsv(root, "regression-runs.tsv")
    if len(row) > 1}
  if results is not None:
    ran = {name: (state, "", "") for name, state in results.items()}
  issues, groups = issues_of(root), {}
  rows = {row[0]: (row + [""] * 8)[:8] for row in tsv(root, "regression.tsv")}
  order = [name for name in rows if rows[name][1] != "draft"] if results is None else list(results)
  for name in order:
    row = rows.get(name) or [name, "", "", "-", "", "", "-", ""]
    key = key_of(row)
    groups.setdefault(found[key][0] if key in found else OTHER, []).append(fields(row, found, ran, issues, markdown, raw))
  return [(title, groups[title]) for title in titles + [OTHER] if title in groups]


def cmd_summary(args):
  try:
    took = float(args.took)
    if took < 0 or not math.isfinite(took):
      raise ValueError
  except ValueError:
    return refuse("--took %r is not a number of seconds. Fix: pass the run's seconds, e.g. --took 95" % args.took)
  try:
    with open(args.results) as handle:
      raw = handle.read().splitlines()
  except OSError as err:
    return refuse("can't read the results file %s: %s. Fix: pass the file the run wrote" % (args.results, err.strerror))
  results = {}
  for number, line in enumerate(raw, 1):
    if not line.strip() or line.startswith("#"):
      continue
    parts = line.split("\t")
    if len(parts) != 2 or parts[1] not in STATES:
      return refuse("%s:%d is %r, not id<TAB>state with a state in %s. Fix: correct that line"
        % (args.results, number, line[:80], ", ".join(STATES)))
    results[parts[0]] = parts[1]
  count = {state: sum(1 for value in results.values() if value == state) for state in STATES}
  minutes, seconds = divmod(int(round(took)), 60)
  out = ["## Regression: %d passed, %d failed, %d known, %d skipped of %d, in %dm %02ds"
    % (count["PASS"], count["FAIL"], count["KNOWN"], count["SKIPPED"], len(results), minutes, seconds), ""]
  for feature, lines in entries(args.root, results, markdown=True):
    out += ["### " + feature, ""] + md_table(("Test", "Kind", "Guards", "Checks", "Result"),
      [x[:4] + [x[5]] for x in lines]) + [""]
  print("\n".join(out).rstrip("\n"))
  return 0


# tests>
