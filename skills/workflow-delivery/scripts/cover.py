#!/usr/bin/env python3
"""SKP-1.1 (o939): a goal skips its local run of the rows the PR's L1 run on GitHub covers, and names L1 as the cover.

usage: cover.py lane SLUG STEP   rerun the local lane for only the uncovered rows of a claimed cover (the command a refusal names)

Per ROW: covered = the rows lanes_cli affected AND tiers.plan both select, minus the base branch's regression-skips.tsv and
regression-limits.tsv (nightly) rows and the previous lane's failed, skipped and flaky rows; local = every other planned row. Any
unknown means NO cover and the whole lane runs. The claim is made at qa or ship, never granted at pr (a one-way ratchet), kept in
<runs>/<slug>.cover.json. Printed reasons are codes, never repo names or URLs. Hooks: flow.py (lane), goal_steps.py (need, late,
pr_part, refresh), lane.py (LOOP_COVER_IDS), sizing.py (rule_fix), flow_steps.py (prompt)."""
import hashlib
import json
import os
import re
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
os.environ.update(GIT_TERMINAL_PROMPT="0", GH_PROMPT_DISABLED="1", GIT_EDITOR="true", GIT_ASKPASS="true", SSH_ASKPASS="true")  # no prompt ever blocks (DEL-10)
REG = os.path.join(HERE, os.pardir, os.pardir, "workflow-regression", "scripts")
APP, BOUND, NAME = 15368, 30, "L1"  # the GitHub Actions app id; seconds per call
HEAD_TRIES, HEAD_WAIT = 6, 5  # reads of the PR head after the push, seconds apart
IFS = ("github.event_name != 'merge_group'", "always() && github.event_name != 'merge_group'", "always()",
       "always() && needs.shard.result == 'success'", "github.event_name == 'merge_group'")
PIN = ("name: regression-pr\n", "  pull_request:\n  merge_group:\n    types: [checks_requested]\n", "\n  shard:\n", "\n  affected:\n",
       "\n  small:\n", "cutgate.py", 'test "${{ needs.shard.result }}" = success')
JOB = {"shard": "github.event_name != 'merge_group'", "affected": "always() && github.event_name != 'merge_group'",
       "small": "github.event_name == 'merge_group'"}  # each job's own if: (a disabled pull_request job is no cover)
# sha1 of the base's regression-pr.yml as reviewed: any edit turns the cover off. Exactly two generated texts are reviewed (TD2357):
WF_SHA = ("533fbed6f28fac049a2bd2c45eaa3bdbffed1ac6",  # the text with the `run nightly --reuse --tier goal` line (a table that is not armed)
          "19b5c86b5523cea9c2219fb081e82592e9f48370")  # the text with the `run L1 --reuse --tier goal` line (an armed table)
WF_FIX = "Fix: python3 skills/workflow-regression/scripts/regression.py workflow, then commit .github/workflows/regression-pr.yml and merge it. "
SILENT = ("GH", "RUNS")
PLAN = r"""
import json, sys
sys.path.insert(0, sys.argv[1]); sys.dont_write_bytecode = True
import regression, tiers, lanes, runs, levels_gate, completion
root = regression.top(); levels_gate.check_read(root); rows = regression.read_rows(root)
def planned(word):
    class A: tier, target, kind, reuse = "goal", word, None, True
    picked = [r for r in tiers.kinds(regression.chosen(rows, tiers.target(root, A)), None) if r["level"] not in ("draft", "covered")]
    return picked, tiers.plan(root, picked, lanes.record_path(root))
armed = completion.armed(root)
pr = planned("L1")[1][0] if armed else None  # armed: what the pull request's L1 run selects
picked, (todo, reused, old, why) = planned("land")  # the local goal lane's plan, as before
bad = [k for k, v in ((old or {}).get("rows") or {}).items() if v.get("status") in ("FAIL", "SKIPPED", "LEFT") or v.get("flaky")]
bad += runs.unproven(root, picked, regression.SEEN)  # a row with no seen-failing date fails the lane wherever it runs
todo += [k for k in bad if k in {r["id"] for r in picked} and k not in todo]  # a cut, failed, skipped or flaky row runs here, never reused
print(json.dumps({"todo": todo, "bad": bad, "l0": sorted(levels_gate.l0_ids(root)), "pr": pr}))
"""


def sh(argv, cwd=None, env=None):
    try:
        done = subprocess.run(argv, cwd=cwd, env=env, capture_output=True, text=True, timeout=BOUND, stdin=subprocess.DEVNULL)
        return done.returncode, done.stdout.strip()
    except (OSError, subprocess.TimeoutExpired):
        return 124, ""


def path(runs, slug):
    return os.path.join(runs, slug + ".cover.json")


def load(runs, slug):
    try:
        data = json.load(open(path(runs, slug)))
    except (OSError, ValueError):
        return {}
    return data if isinstance(data, dict) else {}


def save(runs, slug, data):
    with open(path(runs, slug) + ".tmp", "w") as out:
        json.dump(data, out, indent=1, sort_keys=True)
    os.replace(path(runs, slug) + ".tmp", path(runs, slug))


def pinned(text):
    ifs = re.findall(r"^\s*(?:- )?if: (.+)$", text, re.M)
    for name, want in JOB.items():
        block = re.search(r"\n  %s:\n(.*?)(?=\n  [\w-]+:\n|\Z)" % name, text, re.S)
        got = re.search(r"^    if: (.+)$", block.group(1), re.M) if block else None
        if not got or got.group(1) != want:
            return False
    same = hashlib.sha1(text.strip().replace("\r\n", "\n").encode()).hexdigest() in WF_SHA
    return same and all(p in text for p in PIN) and all(i in IFS for i in ifs)


def ruleset(root):
    rc, out = sh(["gh", "api", "repos/{owner}/{repo}/rules/branches/main"], root)
    try:
        rules = json.loads(out) if not rc else []
        got = {c["context"]: c.get("integration_id") for r in rules if r.get("type") == "required_status_checks"
               for c in r["parameters"]["required_status_checks"]}
    except (ValueError, KeyError, TypeError):
        return "RULE"
    return "" if got.get("affected") == APP and got.get("small") == APP else "RULE"


def facts(root, cfg):
    """(code, diff paths): the first predicate that fails, or '' when the cover may be claimed."""
    base = cfg.get("base", "main")
    rc, url = sh(["git", "remote", "get-url", "origin"], root)
    if base != "main" or not re.search(r"(^|[/@.])github[.]com[:/]", url):
        return "GH", []
    if cfg.get("regression_runs") != "actions":
        return "RUNS", []
    if sh(["git", "fetch", "-q", "origin", base], root)[0]:
        return "FETCH", []
    rc, yml = sh(["git", "show", "origin/%s:.github/workflows/regression-pr.yml" % base], root)
    if rc or not pinned(yml) or ruleset(root):
        return "WF" if rc or not pinned(yml) else "RULE", []
    import private
    if private.repo_is_private(root) is not False:
        return "PRIV", []
    rc, out = sh(["git", "diff", "--name-only", "origin/%s...HEAD" % base], root)
    names = out.split()
    if rc or not names:
        return "DIFF", []
    if any(n.startswith(".github/") for n in names):
        return "GHDIR", names
    if any(n.startswith("skills/workflow-regression/scripts/") for n in names):
        return "TOOL", names
    return ("" if [n for n in names if not re.search(r"[.]md$|^[.]loop/(goals|kept)/", n)] else "DOC"), names


def ids_of(text, col=0, only=None):
    rows = [x.split("\t") for x in text.splitlines() if x.strip() and x[0] != "#"]
    return {r[col] for r in rows if only is None or r[1:2] == [only]}


def select(root, cfg, names):
    """(covered, local, code): the rows both planners select, less what GitHub does not run; code when unknown."""
    base = cfg.get("base", "main")
    rc, out = sh([sys.executable, "-B", os.path.join(REG, "lanes_cli.py"), "affected", "--root", root, "--"] + names, root)
    found = re.search(r"^AFFECTED \d+ of \d+ rows \((.*)\)", out, re.M)
    if rc or not found or re.search(r"^(UNMAPPED|DELETED) ", out, re.M):
        return [], [], "REACH"
    reach = set(found.group(1).split(", ")) - {"none", ""}
    rc, out = sh([sys.executable, "-B", "-c", PLAN, os.path.abspath(REG)], root)
    try:
        plan = json.loads(out.splitlines()[-1])
    except (ValueError, IndexError):
        return [], [], "PLAN"
    gone = set(plan["bad"]) | set(plan.get("l0") or ())  # L0 rows always run here; GitHub reads the merge ref: a row on either the base's or this branch's list is not run there
    for ref in ("origin/%s" % base, "HEAD"):
        for name, only in (("skips", None), ("limits", "nightly")):
            rc, out = sh(["git", "show", "%s:.loop/regression-%s.tsv" % (ref, name)], root)
            if rc and sh(["git", "ls-tree", ref, "--", ".loop/regression-%s.tsv" % name], root) != (0, ""):
                return [], [], "LIST"  # the list is there (or unknown) but unread: no row may be claimed
            gone |= ids_of(out, 0, only)
    todo, pr, l0 = list(plan["todo"]), plan.get("pr"), set(plan.get("l0") or ())
    runs_there = todo if pr is None else pr
    if pr is not None:  # GitHub reads the merge ref: an entry the base changed since the branch point may not run there
        point = sh(["git", "merge-base", "origin/%s" % base, "HEAD"], root)[1]
        was, now = (sh(["git", "show", "%s:.loop/regression-relevel.tsv" % ref], root) for ref in (point, "origin/%s" % base))
        if not point or now[0]:
            return [], [], "LIST"
        old, new = ({x.split("\t")[0]: x for x in text[1].splitlines()} for text in (was, now))
        gone |= {key for key in set(old) | set(new) if old.get(key) != new.get(key)}
    covered = sorted(k for k in runs_there if k in reach and k not in gone)
    local = sorted((set(todo) | (set(runs_there) & l0)) - set(covered))  # L0 stays local; what L1 won't run does too
    left = [] if pr is None else [k for k in local if k not in set(pr) | l0]
    if left:
        print("NOT COVERED by %s: %s (the pull request's run leaves %s out; run locally)" % (
            NAME, ", ".join(left[:12]) + (", +%d more" % (len(left) - 12) if len(left) > 12 else ""),
            "it" if len(left) == 1 else "them"))
    return covered, local, "" if covered else "NONE"


def drop(runs, slug):
    import lane as lanes
    import lanekit
    for name in ("qa", "ship", "pr"):
        lanes.stop(*lanes.job_of(runs, slug, name))  # a partial job left running would later pass as the full lane
        for end in (".ok", ".last"):
            try:
                os.remove(lanekit.lane_base(runs, slug, name) + end)
            except OSError:
                pass


def off(runs, slug, step, code):
    data = load(runs, slug)
    if code not in SILENT and data.get("off", {}).get(step) != code:
        print("COVER OFF: %s. %s%sNothing is lost: the local lane runs in full; rerun %s if the cause was transient" % (
            code, "private repo: no cover. " if code == "PRIV" else "", WF_FIX if code == "WF" else "", "goal.py pr " + slug if step == "pr" else "flow.py %s %s" % (slug, step)))
    data.setdefault("off", {})[step] = code
    if data.pop("claim", None):
        drop(runs, slug)
        print("COVER LOST (COVER_LOST): %s. Non-fatal: the local lane now runs in full" % code)
    save(runs, slug, data)


def lane(fn, runs, slug, step, spec, cfg, wait=90):
    root = sh(["git", "rev-parse", "--show-toplevel"])[1]
    data = load(runs, slug)
    if not root or (step == "pr" and not data.get("claim")):
        return fn(runs, slug, step, spec, cfg, wait)
    code, names = facts(root, cfg)
    covered, local = [], []
    if not code:
        covered, local, code = select(root, cfg, names)
    if code:
        off(runs, slug, step, code)
        return fn(runs, slug, step, spec, cfg, wait)
    head = sh(["git", "rev-parse", "HEAD"], root)[1]
    was = data.get("claim") or {}
    if was and local and set(local) != set(was.get("local", [])):
        drop(runs, slug)  # other rows are local now: no earlier partial pass stands for them
    data["claim"] = {"name": NAME, "head": head, "covered": covered, "local": local, "step": step, "ran": was.get("ran", [])}
    save(runs, slug, data)
    line = "COVERED %d rows by %s; running %d locally: %s (claimed; pending PR recheck and GitHub execution)" % (
        len(covered), NAME, len(local), ", ".join(local[:12]) + (", +%d more" % (len(local) - 12) if len(local) > 12 else "") or "none")
    if not local:
        return "pass", line, []
    os.environ["LOOP_COVER_IDS"] = ",".join(local)
    try:
        status, text, ids = fn(runs, slug, step, spec, cfg, wait)
    finally:
        os.environ.pop("LOOP_COVER_IDS", None)
    if status == "pass":  # the rows that ran locally, kept across steps for the PR text
        data["claim"]["ran"] = sorted(set(data["claim"].get("ran", [])) | set(local))
        save(runs, slug, data)
    return status, line + "\n" + text, ids


def need(fn, over, runs, slug, reply, step="qa"):
    """role.need_lane, with the lane waived only for rows recomputed as covered; the uncovered rows still need their own pass."""
    ref = fn(runs, slug, reply, step)
    if ref and ref[2] not in ("LANE_MISSING", "HEAD_MOVED"):
        return ref  # not about the lane (TEST_CAPS, say): the cover never hides it
    data = load(runs, slug)
    claim, root = data.get("claim"), sh(["git", "rev-parse", "--show-toplevel"])[1]
    if not claim or not root:
        return ref
    try:
        cfg = json.load(open(os.path.join(root, ".loop", "config.json")))
    except (OSError, ValueError):
        cfg = {}
    code, names = facts(root, cfg)
    covered, local = [], []
    if not code:
        covered, local, code = select(root, cfg, names)
    if code:
        off(runs, slug, step, code)
        return fn(runs, slug, reply, step)
    if ref is None and set(local) <= set(claim["local"]):
        return ref
    if not local:
        return over() if step == "qa" else None
    fix = "python3 %s lane %s %s" % (os.path.join("skills", "workflow-delivery", "scripts", "cover.py"), slug, step)
    return ("the rows %s have no passing local lane on this head" % ", ".join(local[:10]), fix, "LANE_MISSING_UNCOVERED")


def late(runs, slug, cfg):
    """After role.record's commit: True when the cover no longer holds on the final head (the caller runs the full lane once)."""
    if not load(runs, slug).get("claim"):
        return False
    root = sh(["git", "rev-parse", "--show-toplevel"])[1]
    code, names = facts(root, cfg)
    if not code:
        got = select(root, cfg, names)
        code = got[2] or ("GREW" if not set(got[1]) <= set(load(runs, slug)["claim"]["local"]) else "")
    if code:
        off(runs, slug, "pr", code)
    return bool(code)


def refresh(g, state, info, body):
    """After pr_open: an already open PR gets the new Regression lane text; a failed edit (BODY_STALE) or a moved head (COVER_MOVED) refuses."""
    mark = hashlib.sha1(body.encode()).hexdigest()
    if info.get("state") != "OPEN" or state.get("pr_body_pushed") in (None, mark):
        state["pr_body_pushed"] = mark
        return
    head, runs = sh(["git", "rev-parse", "HEAD"])[1], os.path.dirname(g.state_path(state["slug"]))
    claim = load(runs, state["slug"]).get("claim")
    for _ in range(HEAD_TRIES if claim else 1):  # GitHub shows a push late: with a cover, only a head that stays other or unread moved
        rc, out = sh(["gh", "pr", "view", state["branch"], "--json", "headRefOid", "-q", ".headRefOid"])
        if not rc and out == head:
            break
        time.sleep(HEAD_WAIT if claim else 0)
    else:
        if not claim:  # no cover to lose: the body waits for the next pr run (an unread head is edited, as before)
            if not rc:
                return print("NOTE: the PR head moved; the body is not edited (the next pr run edits it)")
        else:
            off(runs, state["slug"], "pr", "MOVED")
            g.guards.refuse_no_try(state, "the PR head %s; the body is not edited (PR %s)" % ("is unread" if rc else "moved", info.get("url", "")),
                                   "goal.py pr %s reruns the pr step on the current head, with the whole lane" % state["slug"], "COVER_MOVED", g.save)
    file = g.state_path(state["slug"]) + ".body"
    g.write(file, body)
    if sh(["gh", "pr", "edit", state["branch"], "--body-file", file])[0]:
        g.guards.refuse_no_try(state, "the PR is open and its body is stale (PR %s)" % info.get("url", ""),
                               "goal.py pr %s reruns the pr step: it re-syncs, may rerun the lane and push, then retries the edit" % state["slug"], "BODY_STALE", g.save)
    state["pr_body_pushed"] = mark


def prompt(text, runs, slug):
    """flow_steps: the LANE sentence of the qa/ship prompt, for a standing claim."""
    claim = load(runs, slug).get("claim")
    if not claim:
        return text
    return re.sub(r"The regression lane \(label regression.*?returns at once\.", "%d rows are covered by %s (claimed; pending PR recheck and "
                  "GitHub execution); the %d other rows run by flow.py; run no suite yourself." % (len(claim["covered"]), NAME, len(claim["local"])),
                  text, flags=re.S)


def rule_fix(text, runs, slug):
    """sizing.rule: the full-test-run line says what the cover runs."""
    claim = load(runs, slug).get("claim")
    return text if not claim else re.sub(r"(full-test-run:[^\n]*Run: )[^\n]*", r"\1covered by %s (claimed; pending PR recheck and GitHub "
                                         "execution): %d rows; the other %d rows still run locally" % (NAME, len(claim["covered"]), len(claim["local"])), text)


def main(argv=None):
    argv = sys.argv[1:] if argv is None else argv
    if len(argv) != 3 or argv[0] != "lane" or argv[2] not in ("qa", "ship", "pr"):
        print("usage: cover.py lane SLUG qa|ship|pr\n\n" + __doc__)
        return 0 if argv[:1] in (["-h"], ["--help"]) else 2
    runs = os.path.join(os.path.abspath(sh(["git", "rev-parse", "--git-common-dir"])[1]), "loop", "runs")
    top = sh(["git", "rev-parse", "--show-toplevel"])[1]
    try:
        cfg = json.load(open(os.path.join(top, ".loop", "config.json")))
    except (OSError, ValueError):
        cfg = {}
    data = load(runs, argv[1])
    if data.get("claim") and top:  # recompute first: the named command must reach what the record will ask for
        code, names = facts(top, cfg)
        got = select(top, cfg, names) if not code else ([], [], code)
        if got[2]:
            off(runs, argv[1], argv[2], got[2])
        else:
            was = data["claim"]
            if got[1] and set(got[1]) != set(was["local"]):
                drop(runs, argv[1])
            data["claim"] = dict(was, head=sh(["git", "rev-parse", "HEAD"], top)[1], covered=got[0], local=got[1], step=argv[2])
            save(runs, argv[1], data)
    claim = load(runs, argv[1]).get("claim") or {}
    if claim and not claim.get("local"):
        print("COVERED: every selected row is covered by %s; nothing is left to run locally" % NAME)
        return 0
    env = dict(os.environ, **({"LOOP_COVER_IDS": ",".join(claim["local"])} if claim.get("local") else {}))
    return subprocess.run([sys.executable, os.path.join(HERE, "role.py"), "lane", argv[1], argv[2]], env=env).returncode


from cover_text import limits, pr_part  # noqa: E402,F401  (the PR text moved there: TD1850)

if __name__ == "__main__":
    sys.exit(main())
