#!/usr/bin/env python3
"""The Actions workflow regression.py writes: rows on a schedule, one issue per failure."""
import json
import os
import re
import sys

from slots import ROUTINE_STEP, SUMMARY_JOB

os.environ.update(GIT_TERMINAL_PROMPT="0", GH_PROMPT_DISABLED="1", GIT_EDITOR="true", GIT_ASKPASS="true", SSH_ASKPASS="true")
if not sys.stdin or not sys.stdin.isatty():
    os.dup2(os.open(os.devnull, os.O_RDONLY), 0)

BUDGET_MINUTES = 30  # REG-7, AUT-7
SHARDS = 16  # REG-4, REG-7


ROW_DROP = ("GH_TOKEN", "GITHUB_TOKEN", "GITHUB_STEP_SUMMARY", "GITHUB_ENV", "GITHUB_OUTPUT", "GITHUB_PATH", "GITHUB_STATE",
            "REGRESSION_RESULTS", "REGRESSION_MAP", "RUNNER_TEMP", "SUITE_TIME_FILE",
            "LOOP_ROW_TIMES", "REGRESSION_SHARD", "REGRESSION_LEVELS", "REGRESSION_TARGET", "REGRESSION_CLEANUP")
LANE_DROP = ("_LOOP_LANE_NOTE", "_LOOP_LANE_QUEUED", "_LOOP_LANE_STARTED")  # the lane runner's own handoff files
APP_DROP = ("CLAUDE_CODE_HOST_SESSION_ID",)  # app-session names, never set on GitHub, so not mirrored in the workflow
GIT_KEEP = ("GIT_TERMINAL_PROMPT", "GIT_EDITOR", "GIT_ASKPASS",  # set above, so no row's git waits
            "GIT_CEILING_DIRECTORIES")  # a caller's limit; its GIT_CONFIG_ files and settings stay too; other GIT_ names go


LANE_ONLY = ("LOOP_FLAKY_FILE", "GITHUB_EVENT_NAME")  # this run's own: no row inherits them


def row_env():
    return dict({k: v for k, v in os.environ.items() if k not in ROW_DROP + LANE_DROP + APP_DROP + LANE_ONLY and (k in GIT_KEEP or k.startswith("GIT_CONFIG_") or not k.startswith("GIT_"))}, LOOP_PRIVATE_NAMES=os.environ.get("LOOP_PRIVATE_NAMES") or os.devnull)


WORKFLOW = r"""# Written by workflow-regression. It reads .loop/regression.tsv and .loop/regression-known.tsv.
name: regression
on:
@SCHEDULE@  workflow_dispatch:
    inputs:
      target:
        description: "land, nightly or a row id; empty: @LEVELS@"
        required: false
        default: ""
        type: string
      cleanup:
        description: "true: run no row, close skipped-only and duplicate issues"
        required: false
        default: false
        type: boolean
permissions:
  contents: read
  issues: write
  pull-requests: read
concurrency:
  group: regression-${{ github.ref }}
  cancel-in-progress: true  # GRD-7
jobs:
  regression:
    runs-on: ubuntu-latest
    timeout-minutes: @BUDGET@
    strategy:
      fail-fast: false
      max-parallel: 6
      matrix:
        shard: @MATRIX@
    steps:
      - uses: actions/checkout@v4
        with:
          persist-credentials: false
          fetch-depth: 0
      - uses: actions/setup-python@v5
        with:
          python-version: "3.12"
@ROUTINE@      - name: Run the rows, and keep one issue per failing row
        if: steps.routine.outputs.on == 'true'
        env:
          L: ${{ github.ref == 'refs/heads/main' && '--live' }}
          GH_TOKEN: ${{ github.token }}
          REGRESSION_RESULTS: ${{ runner.temp }}/regression-results.tsv
          SUITE_TIME_FILE: ${{ runner.temp }}/suite-time.tsv
          REGRESSION_TARGET: @TARGET@
          REGRESSION_CLEANUP: ${{ inputs.cleanup }}
          REGRESSION_LEVELS: "@LEVELS@"
          LOOP_PRIVATE_NAMES: /dev/null  # o675
          REGRESSION_SHARD: "${{ matrix.shard }}/@SHARDS@"
        run: |
          here=$(mktemp -d)
          cat > "$here/tests.py" <<'TESTS_PY_EOF'
@TESTS@
          TESTS_PY_EOF
          python3 -I "$here/tests.py" list --tsv > "$here/map.tsv" 2>/dev/null || true
          export REGRESSION_MAP="$here/map.tsv"
          python3 - $L <<'PY'
          import json, os, re, subprocess, sys, tempfile, time, urllib.parse
          def rows(path):
              if not os.path.exists(path):
                  return []
              return [line.rstrip("\n").split("\t") for line in open(path) if line.strip() and not line.startswith("#")]
@ROWTAIL@
          known = {row[0] for row in rows(".loop/regression-known.tsv")}
          TARGET = os.environ.get("REGRESSION_TARGET") or os.environ.get("REGRESSION_LEVELS") or "nightly"
          if not re.fullmatch(r"land|nightly|L2|[A-Za-z0-9_.-]+", TARGET) or TARGET not in ("land", "nightly", "L2") and \
                  TARGET not in [row[0] for row in rows(".loop/regression.tsv")]:
              print("REFUSED (BAD_TARGET): bad target %s: use land, nightly, L2 or a row id from regression.py list. Fix: rerun the "
                    "workflow with one of those" % json.dumps(TARGET), file=sys.stderr)
              sys.exit(1)
          def wanted(row):
              return row[0] == TARGET if TARGET not in ("land", "nightly", "L2") else row[1] in ("land", "nightly" if TARGET == "L2" else TARGET)
          def gh(*args, body=None):
              if args[0] != "api" and "--live" not in sys.argv[1:]:
                  print("WOULD gh " + " ".join(args)[:70])
                  return subprocess.CompletedProcess(args, 0, "", "")
              with tempfile.TemporaryDirectory() as tmp:
                  if body is not None:
                      open(tmp + "/b", "wb").write(body.encode())
                      args += ("--body-file", tmp + "/b")
                  return subprocess.run(("gh",) + args, capture_output=True, text=True)
          def seconds(name, default):
              try:
                  value = int(os.environ.get(name) or default)
              except ValueError:
                  return default
              return value if value > 0 else default
          ROW_SECONDS, JOB_SECONDS = seconds("REGRESSION_ROW_SECONDS", 900), seconds("REGRESSION_JOB_SECONDS", (@BUDGET@ - 2) * 60)
          ROW_ENV = {k: v for k, v in os.environ.items() if k not in @ROWDROP@}
          def run(command, limit):
              skip = os.path.join(tempfile.gettempdir(), "skip%d" % os.getpid())
              with tempfile.TemporaryFile("w+", errors="replace") as log:
                  child = subprocess.Popen(command, shell=True, stdout=log, stderr=subprocess.STDOUT, env=dict(ROW_ENV, TOY_SKIP_FILE=skip),
                                           start_new_session=True)
                  timed_out = False
                  try:
                      child.wait(timeout=limit)
                  except subprocess.TimeoutExpired:
                      timed_out = True
                      try:
                          ps = subprocess.run(["ps", "-o", "pid,ppid,stat,wchan:20,args", "-s", str(child.pid)], capture_output=True, text=True)
                          log.write("\nprocesses at the timeout:\n" + ps.stdout)
                      except OSError:
                          pass
                  try:
                      os.killpg(child.pid, 9)
                  except OSError:
                      pass
                  except AttributeError:
                      subprocess.run(["taskkill", "/T", "/F", "/PID", str(child.pid)], capture_output=True)
                  child.wait()
                  log.seek(0)
                  out = log.read()
              if timed_out:
                  return 124, out + "\ntimed out after %d s" % limit
              if child.returncode and os.path.exists(skip):
                  os.remove(skip)
                  return 77, out
              return child.returncode, out
          def result(name, state):
              with open(os.environ.get("REGRESSION_RESULTS") or os.devnull, "a") as handle:
                  handle.write("%s\t%s\n" % (name, state))
          gh("label", "create", "regression", "--force", "--description", "A regression row is failing")
          gh("label", "create", "defect", "--description", "A test that guards it is failing")
          def gone():
              if TARGET == "L2":
                  with open(os.environ.get("REGRESSION_RESULTS") or os.devnull, "a") as handle:
                      handle.write("# gh-failed\n")
          if TARGET == "L2" and gh("label", "create", "l2-red", "--force", "--description", "A row failed in the full L2 run").returncode:
              print("FAILED label l2-red: it could not be created (FILE_FAILED)")
              gone()
          guards = {cells[1]: cells for cells in rows(os.environ.get("REGRESSION_MAP") or os.devnull) if len(cells) > 4}
          out = gh("api", "--paginate", "repos/{owner}/{repo}/issues?state=open&labels=regression&per_page=100", "--jq",
                   '.[] | select(.pull_request == null) | {number, state: "OPEN", body, labels}')
          issues = [json.loads(line) for line in out.stdout.splitlines() if line] if out.returncode == 0 else None
          if issues is None:
              print("NOTE: can't read issues, so none changed: " + out.stderr.strip()[:200])
          FEATURES = {row[0] for row in rows(".loop/docs.tsv") if row and row[0] and row[0] != "Home"}
          try:
              LABELS_ON = json.load(open(".loop/config.json")).get("feature_labels") is True
          except (OSError, ValueError, AttributeError):
              LABELS_ON = False
          failed, filed = [], [0]
          CLEANUP, halt = os.environ.get("REGRESSION_CLEANUP") == "true", []
          def write(what, *args, body=None):
              if halt or CLEANUP and time.time() - start > JOB_SECONDS - 120:
                  return halt and failed.append(what)
              if CLEANUP:
                  time.sleep(float(os.environ.get("REGRESSION_PACE") or 20))
              done = gh(*args, body=body)
              if done.returncode:
                  failed.append(what)
                  gone()
                  halt.extend(["rate limit"] * ("rate limit" in done.stderr.lower()))
                  print("FAILED %s: %s (FILE_FAILED)" % (what, done.stderr.strip()[:160]))
              else:
                  filed[0] += 1
              return done
          def label_for(page):
              if not LABELS_ON or page not in FEATURES:
                  return ""
              label = "feature:" + "".join(c for c in page if c != "," and c.isprintable())[:42]
              made = gh("label", "create", label, "--force", "--description", "Issues about one feature")
              if made.returncode:
                  print("FAILED label %s: %s" % (label, made.stderr.strip()[:160]))
                  return ""
              return label
          FOUND = re.compile(r"<!-- loop-regression (\S+?)(?: placed=(\S*))? -->")
          def marked(body):
              match = FOUND.search(body or "")
              return (match.group(1), urllib.parse.unquote(match.group(2) or "")) if match else (None, "")
          red, start, dupes, unrun = [], time.time(), [600 if CLEANUP else 20], [0]
          with open(os.environ.get("REGRESSION_RESULTS") or os.devnull, "w") as handle:
              handle.write("# started %d\n" % start)
          mine, seen = (os.environ.get("REGRESSION_SHARD") or "0/1").split("/"), 0
          mine, shards = int(mine[0]), int(mine[1])
          for row in rows(".loop/regression.tsv"):
              if len(row) < 3 or not wanted(row):
                  continue
              seen += 1
              if (seen - 1) % shards != mine:
                  continue
              if CLEANUP and time.time() - start > JOB_SECONDS - 120:
                  break
              if CLEANUP:
                  code, said, skipped = 125, "", True
              elif JOB_SECONDS - (time.time() - start) < 30:
                  code, said, skipped = 125, "skipped: out of job time; this row did not run", True
                  unrun[0] += 1
                  with open(os.environ.get("REGRESSION_RESULTS") or os.devnull, "a") as handle:
                      handle.write("# unrun %s\n" % row[0])
              else:
                  (code, said), skipped = run(row[2], int(min(ROW_SECONDS, JOB_SECONDS - (time.time() - start)))), False
              hits = sorted((item for item in issues or [] if marked(item["body"])[0] == row[0]), key=lambda i: i["number"])
              sk = lambda i: (i["body"] or "").split("\n")[1:2] == ["The row `%s` was skipped." % row[0]]
              hit = hits[0] if hits else None
              for item in [i for i in hits if i["state"] == "OPEN" and i is not hit]:
                  if dupes[0] > 0:
                      dupes[0] -= 1
                      write("close duplicate #%d" % item["number"], "issue", "close", str(item["number"]), "--comment",
                            "Duplicate of #%d, kept for row %s." % (hit["number"], row[0]))
              state = "PASS" if code == 0 else "SKIPPED" if skipped or code == 77 else "KNOWN" if row[0] in known else "FAIL"
              print(state, row[0])
              result(row[0], state)
              if code == 0:
                  if hit and hit["state"] == "OPEN":
                      write("close #%d" % hit["number"], "issue", "close", str(hit["number"]), "--comment", "Passing again.")
              elif skipped:
                  for item in hits:
                      if item["state"] == "OPEN" and sk(item) and dupes[0] > 0:
                          dupes[0] -= 1
                          write("close skipped #%d" % item["number"], "issue", "close", str(item["number"]), "--comment",
                                "Closed: a skipped row files no issue.")
              elif row[0] not in known and code != 77:
                  red.append(row[0])
                  text = shown(lambda c: run(c, ROW_SECONDS), row[2], code, said)
                  note = "#### FAIL %s\n```\n%s\n```" % (row[0], "\n".join(text.splitlines()[-20:]))
                  print(note)
                  with open(os.environ.get("GITHUB_STEP_SUMMARY") or os.devnull, "a") as handle:
                      handle.write(note + "\n")
                  if issues is None:
                      continue
                  cells = guards.get(row[0]) or [""] * 5
                  label = label_for(cells[0])
                  mark = "<!-- loop-regression %s placed= -->" % row[0]
                  about = "- Feature: %s\n- Guards: %s\n- Checks: %s\n\n" % (cells[0] or "-", cells[3] or "-", cells[4] or "-")
                  body = "%s\nThe row `%s` %s.\n\n%s```\n%s\n```\n" % (mark, row[0], "fails", about,
                                                                 text)
                  tag = ["--label", "l2-red"] * (TARGET == "L2")
                  if not hit:
                      make = ["issue", "create", "--title", "Regression: " + row[0], "--label", "regression", "--label", "defect"]
                      made = gh(*make, *(["--label", label] if label else []), *tag, body=body + "\nLabelled l2-red.\n" * bool(tag))
                      if made.returncode and tag:
                          print("FAILED label l2-red: %s (FILE_FAILED)" % made.stderr.strip()[:160])
                          gone()
                          made = gh(*make, *(["--label", label] if label else []), body=body)
                      if made.returncode and label and "label" in made.stderr.lower():
                          print("FAILED label %s: %s" % (label, made.stderr.strip()[:160]))
                          made = gh(*make, body=body)
                      if made.returncode:
                          failed.append("issue for " + row[0])
                          print("FAILED issue for %s: %s (FILE_FAILED)" % (row[0], made.stderr.strip()[:160]))
                      else:
                          filed[0] += 1
                  else:
                      n = str(hit["number"])
                      names = [label.get("name") for label in hit.get("labels") or []]
                      if hit["state"] != "OPEN":
                          write("reopen #" + n, "issue", "reopen", n)
                      if sk(hit):
                          write("body #" + n, "issue", "edit", n, body=body)
                      if "defect" not in names:
                          write("label #" + n, "issue", "edit", n, "--add-label", "defect")
                      if label and label not in names:
                          write("feature label #" + n, "issue", "edit", n, "--add-label", label)
                      if TARGET == "L2" and "l2-red" not in names:
                          write("l2 label #" + n, "issue", "edit", n, "--add-label", "l2-red")
                      write("comment #" + n, "issue", "comment", n, body="Still failing.")
          if TARGET in ("nightly", "L2") and not CLEANUP:
              took, sha = int(time.time() - start), subprocess.run(["git", "rev-parse", "HEAD"], capture_output=True, text=True).stdout.strip()
              with open(os.environ.get("SUITE_TIME_FILE") or os.devnull, "w") as handle:
                  handle.write("%s\tfull\t%d\t%s\t%d\n" % (sha, took, time.strftime("%Y-%m-%d", time.gmtime()), unrun[0]))
              print("SUITE_TIME %d" % took)
          if CLEANUP:
              ids = {row[0] for row in rows(".loop/regression.tsv") if row}
              for item in [i for i in issues or [] if i["state"] == "OPEN" and marked(i["body"])[0] not in ids | {None}]:
                  if dupes[0] > 0:
                      dupes[0] -= 1
                      write("close removed #%d" % item["number"], "issue", "close", str(item["number"]), "--comment",
                            "Closed: row removed from the regression table.")
              print("CLEANUP closed %d issues%s" % (filed[0], "; stopped: rate limit" * bool(halt)))
          if failed:
              print("FILED %d issue writes; FAILED %d: %s (FILE_FAILED)" % (filed[0], len(failed), ", ".join(failed)))
          sys.exit(1 if red or failed or CLEANUP and issues is None else 0)
          PY
      - name: Keep the full suite's time for the health job
        if: always() && steps.routine.outputs.on == 'true'
        continue-on-error: true
        uses: actions/upload-artifact@v4
        with:
          name: suite-time-${{ matrix.shard }}
          path: ${{ runner.temp }}/suite-time.tsv
          if-no-files-found: ignore
          retention-days: 30
      - name: Keep this shard's results for the summary
        if: always() && steps.routine.outputs.on == 'true'
        continue-on-error: true
        uses: actions/upload-artifact@v4
        with:
          name: results-${{ matrix.shard }}
          path: ${{ runner.temp }}/regression-results.tsv
          if-no-files-found: ignore
          retention-days: 30
@SUMMARY@"""


HERE = os.path.dirname(os.path.abspath(__file__))
UNSAFE = ("${{", "@CRON@", "@ROWDROP@", "@TESTS@", "@SCHEDULE@", "@LEVELS@", "@TARGET@", "@BUDGET@", "@ROWTAIL@", "@MATRIX@", "@SHARDS@", "@SUMMARY@", "@ROUTINE@", "TESTS_PY_EOF")


def render(cron, levels="nightly"):
    with open(os.path.join(HERE, "tests.py")) as handle:
        source = handle.read()
    bad = [token for token in UNSAFE if token in source]
    if bad:
        sys.exit("REFUSED: tests.py contains %s, which the workflow can't carry. Fix: reword that line" % bad[0])
    body = "\n".join(("          " + line).rstrip() for line in source.rstrip("\n").split("\n"))
    with open(os.path.join(HERE, "runs.py")) as handle:
        tail = "\n".join(("          " + x).rstrip() for x in handle.read().split("# rowtail:")[1].split("\n")[1:-1])
    schedule = "" if cron == "off" else '  schedule:\n    - cron: "%s"\n' % cron
    return WORKFLOW.replace("@ROUTINE@", ROUTINE_STEP).replace("@SUMMARY@", SUMMARY_JOB).replace("@SCHEDULE@", schedule).replace("@CRON@", cron).replace("@TARGET@", "${{ inputs.target || (inputs.cleanup && 'nightly' || 'L2') }}" if levels == "nightly" else "${{ inputs.target }}").replace("@LEVELS@", levels).replace("@ROWDROP@", repr(ROW_DROP)) \
        .replace("@BUDGET@", str(BUDGET_MINUTES)).replace("@SHARDS@", str(SHARDS)).replace("@MATRIX@", str(list(range(SHARDS)))) \
        .replace("@TESTS@", body).replace("@ROWTAIL@", tail)


def write(root, default):
    import actions_write
    return actions_write.write(root, default, render)
