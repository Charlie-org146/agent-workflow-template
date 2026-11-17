"""File health findings as tagged issues, under the owner's control (HLT-4). Used by health.py preview and file.

plan() works out what each finding does (open, update, reopen, close, link or same). preview prints the plan and has no
write path; file carries it out for the named groups (and --feature) only.
- Each issue is labelled health and health:<group> (review findings: health:review-<kind>), and is a defect (a FAIL except a
  performance one, a review conflict: labelled defect, no milestone) or a backlog item (labelled backlog, on its feature's
  milestone "Backlog: <Feature>", "Backlog: Other" when none, made first when missing). An issue the owner moved stays put.
  It is always tagged feature:<Page>, or feature:Other when it fits no page (issues.feature_label), whatever feature_labels
  says, made beforehand with label create --force; if that fails it is filed without it and a FAILED label line says so.
- Its marker `<!-- loop-health KEY evidence=H placed= -->` names the finding and a hash of its stable evidence (placed= is
  always empty; older markers naming a milestone still parse). A repeat updates, a fix closes (only when that rule ran and
  read its data), a return reopens. A health:closed issue (closed by triage) stays closed while its evidence hash is unchanged.
- An open non-health issue naming the finding's subject (an exact path, requirement id or row id) already covers it: it gets
  one link comment, `<!-- loop-health-link KEY evidence=H -->`, never a duplicate issue.
- Markers from before the twelve groups (criteria:, cost:, size:...:limit) are found and moved to the new key.
It runs gh and nothing else, never edits a tracked page, and stops before any write when gh can't list the issues.
"""
import glob
import hashlib
import json
import os
import re
import subprocess
import sys
import tempfile

import report as G
import issues as IS
import milestone as MS
from issues import covering, evidence_of, key_of, legacy

# No terminal, no waiting: a prompt must fail, not block.
os.environ.update(GIT_TERMINAL_PROMPT="0", GH_PROMPT_DISABLED="1", GIT_EDITOR="true", GIT_ASKPASS="true", SSH_ASKPASS="true")
if not sys.stdin or not sys.stdin.isatty():
    os.dup2(os.open(os.devnull, os.O_RDONLY), 0)

MARK = "<!-- loop-health %s evidence=%s placed=%s -->"
LINK = "<!-- loop-health-link %s evidence=%s -->"
FOUND = re.compile(r"<!-- loop-health (.+?)(?: evidence=(\w+))?(?: placed=(\S*))? -->")  # a key may hold spaces
GROUPS = tuple(g for g in G.ORDER if g != "controls") + ("review",)
DEFAULT = tuple(g for g in G.ORDER if g not in ("mine", "controls"))  # a preview with no group names these
BAD = ("WARN", "FAIL", "UNREAD")
# Shown, never filed: local state, the controls, the check's own clock.
REPORT_ONLY = ("test-time", "suite-cap", "worktrees", "local-branches", "idle-sessions", "eta-missing", "eta-extended", "eta-overrun", "scan-hook", "hooks", "check-time", "control",
               "finding-age")  # finding-age would feed itself


def tag_of(group, item=None):
    if group == "review" and item:
        return "health:review-" + item["rule"]
    return "health:" + group


def home(item, page):
    """(label, milestone) of a new issue."""
    if (item["state"] == "FAIL" and item["family"] != "performance") or (item["family"] == "review" and item["rule"] == "conflict"):
        return "defect", ""
    return "backlog", "Backlog: " + page if page else MS.OTHER


def line_of(item):
    text = "%s %s %s %s: %s" % (item["state"], item["family"], item["subject"], item["rule"], item["detail"])
    return text + (" -> fix: " + item["fix"] if item["fix"] else "")


def body_of(item):
    line = line_of(item) if item["family"] != "mine" else "%s mine %s %s: details stay local; run health.py check --group mine" % (
        item["state"], item["subject"], item["rule"])
    angle = G.ANGLE.get(item["family"], "the reviewer's angle: %s" % item.get("angle", "per feature"))
    return "%s\n\n%s\n\nGroup: %s (%s). Evidence: %s\n\nFiled by health.py file.\n" % (
        MARK % (key_of(item), evidence_of(item), ""), line, G.TITLE.get(item["family"], item["family"]), angle,
        item.get("evidence") or item["subject"])


def run(args, root, body=None):
    """gh; a long body= goes in a temp --body-file (Windows caps the command line)."""
    if body is not None:
        with tempfile.NamedTemporaryFile("w", suffix=".md", delete=False, encoding="utf-8", newline="\n") as f:
            f.write(body)
        args = args + ["--body-file", f.name]
    try:
        return subprocess.run(["gh"] + args, cwd=root, capture_output=True, text=True, timeout=120)
    except (OSError, subprocess.SubprocessError) as error:
        return subprocess.CompletedProcess(args, 127, "", str(error))
    finally:
        if body is not None:
            os.remove(f.name)


def saves(root, here, rows):
    """(items, read): the judge's savings as rows, and whether it answered. Calls a model."""
    sys.path.insert(0, here)
    try:
        import judge
        answer, why = judge.ask(judge.gather(root, here, rows), root)
        found = judge.parse(answer)["SAVES"]
    except Exception:  # advice only
        return [], False
    finally:
        sys.path.pop(0)
    if why or not found:
        return [], False
    return saves_rows(found), True


def saves_rows(found):
    """The judge's SAVES lines (percent, where, change) as rows, keyed by what they are about, not by their wording (#4543)."""
    return [{"state": "WARN", "family": "performance", "subject": "judge", "rule": "saves-" + hashlib.sha1(IS.about(w).encode()).hexdigest()[:8],
             "detail": "%s%% saving: %s" % (p.rstrip("% "), w), "fix": c, "about": IS.about(w)} for p, w, c in found]


def held(root):
    """({marker key: issue}, why), or (None, why) when gh can't list."""
    found, _, why = held_all(root)
    return found, why


def held_all(root):
    """({marker key: issue}, every issue, why) or (None, None, why) when gh can't list."""
    found, why = IS.fetch(root, "held")
    if found is None:
        return None, None, why
    out = {}
    for issue in sorted(found, key=lambda one: one["number"]):
        match = FOUND.search(issue.get("body") or "")
        if match and IS.is_health(issue):
            name = IS.posix(match.group(1))
            seen = out.get(name)
            if seen is None or (seen.get("state") != "open" and issue.get("state") == "open"):  # an open duplicate wins
                out[name] = dict(issue, evidence=match.group(2) or "")
    return out, found, ""


def judge_twin(item, issues):
    if item.get("about") is None:
        return None
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    try:
        import judge
        return judge.twin(item, issues)
    finally:
        sys.path.pop(0)


def plan(rows, issues, groups, extra=(), judged=False, root=".", ran_rules=None, everything=(), only=None, reviewed=False):
    """Actions (kind open, update, reopen, close, link or same) for the groups and feature `only`."""
    found = [item for item in list(rows) + list(extra)
             if item["state"] in BAD and item["family"] in groups and item["rule"] not in REPORT_ONLY]
    cache, out, current = {}, [], set()
    tagging = bool(root)
    for item in found:
        page = IS.feature_of(root, item, cache)
        if only and page != only:
            continue
        key, group, mark = key_of(item), item["family"], evidence_of(item)
        if key in current:  # one identity, one issue
            continue
        current.add(key)
        issue = issues.get(key) or next((issues[k] for k in legacy(item) if k in issues), None)
        old = None if issue else judge_twin(item, issues)  # filed under an older judge key for the same subject (#4543)
        issue = issue or (old and old[1])
        current.update(k for k in legacy(item) if k in issues)  # migrated: updated, never closed
        old and current.add(old[0])
        label, stone = home(item, page)
        act = {"group": group, "key": key, "body": body_of(item), "evidence": mark, "tag": tag_of(group, item),
               "label": label, "stone": stone, "feature": IS.feature_label(page or "Other") if tagging else "",

               "title": "health: %s %s %s" % (group, IS.posix(item["subject"]), item["rule"])}
        if not issue:
            cover = covering(item, everything)
            out.append(dict(act, kind="link", number=str(cover["number"])) if cover else dict(act, kind="open"))
            continue
        act["number"] = str(issue["number"])
        names = [l.get("name") if isinstance(l, dict) else l for l in issue.get("labels") or []]
        act["stale"] = [t for t in names if t.startswith("health:") and t not in (act["tag"], "health:closed")]
        closed = issue.get("state", "").lower() != "open"
        if closed and "health:closed" in names and (issue.get("evidence") == mark or old):
            out.append(dict(act, kind="same", why="closed by the owner, evidence unchanged"))
            continue
        if closed:
            out.append(dict(act, kind="reopen", unclose="health:closed" in names))
        old = re.sub(r" placed=\S* -->", " placed= -->", issue.get("body") or "", count=1)  # a marker from before: not a change
        if old.rstrip() != act["body"].rstrip() or act["tag"] not in names or act["stale"] or (act["feature"] and act["feature"] not in names):
            out.append(dict(act, kind="update"))
        elif not closed:
            out.append(dict(act, kind="same"))
    for key, issue in sorted(issues.items()):
        family, _, rest = key.partition(":")
        family = G.ALIASES.get(family, family)
        rule = G.rule_of({"family": family, "rule": rest.rsplit(":", 1)[-1], "subject": rest.rsplit(":", 1)[0]})
        if family == "mine":  # a private rule closes only when it ran here
            rule = "mine:" + rest.rsplit(":", 1)[0]
        if key in current or family not in groups or issue.get("state", "").lower() != "open" or only:
            continue
        savings = ":judge:saves-" in key
        whole = {"criteria": {"requirements", "traceability", "tests"}, "cost": {"performance"}}.get(key.partition(":")[0])
        if whole and not whole <= set(groups):  # an old key may mean a rule in a group not run: leave it
            continue
        if (savings and judged) or (not savings and ran_rules is not None and rule in ran_rules) or (reviewed and family == "review"):
            out.append({"kind": "close", "group": family, "key": key, "number": str(issue["number"]), "title": "", "body": "",
                        "tag": tag_of(family), "feature": ""})
    return out


def words(act):
    kind = act["kind"]
    tags = act["tag"] + (", " + act["feature"] if act.get("feature") else "")
    if kind == "open":
        return "open issue %r [%s] as %s%s" % (act["title"], tags, act["label"], " on " + act["stone"] if act["stone"] else "")
    if kind == "link":
        return "link #%s (already covers %s) [%s]" % (act["number"], act["key"], act["tag"])
    return "%s #%s %s [%s]" % (kind, act["number"], act["key"], tags) + (", no longer found" if kind == "close" else "")


def args_of(act):
    kind, n = act["kind"], act.get("number")
    if kind == "open":
        return (["issue", "create", "--title", act["title"], "--label", "health", "--label", act["tag"], "--label", act["label"]]
                + (["--label", act["feature"]] if act.get("feature") else []) + (["--milestone", act["stone"]] if act["stone"] else []))
    if kind == "update":
        return (["issue", "edit", n, "--add-label", act["tag"]] + (["--add-label", act["label"]] if act.get("label") else [])
                + (["--add-label", act["feature"]] if act.get("feature") else [])
                + [part for t in act.get("stale") or [] for part in ("--remove-label", t)])
    if kind == "reopen":
        return ["issue", "reopen", n]
    if kind == "close":
        return ["issue", "close", n, "--comment", "No longer found by health.py file."]
    raise KeyError(kind)


def issue_text(act):
    """The long text of an open or update action (--body-file)."""
    return act["body"] if act["kind"] in ("open", "update") else None


def only_open(acts):
    """--open-only."""
    home, keep = os.path.expanduser("~"), []
    for act in acts:
        text = act["title"] + act["body"]
        if act["kind"] not in ("open", "link"):
            continue
        if (len(home) > 1 and home in text) or re.search(r"[\w.+-]+@[\w-]+\.[\w.-]+", text):
            print("NOTE: skipped %s (holds a private value)" % act["key"])
            continue
        keep.append(act)
    return keep


def preview(acts):
    """Print what would happen. Nothing here can write."""
    for act in acts:
        print(("SAME #%s %s [%s]%s" % (act["number"], act["key"], act["tag"], " (%s)" % act["why"] if act.get("why") else ""))
              if act["kind"] == "same" else "WOULD " + words(act))
    return len([act for act in acts if act["kind"] != "same"])


def linked(root, number, act):
    """True when the covering issue has this finding's link comment."""
    got = run(["issue", "view", number, "--json", "comments"], root)
    try:
        return LINK % (act["key"], act["evidence"]) in json.dumps(json.loads(got.stdout))
    except ValueError:
        return False


def apply(acts, root, groups):
    """Carry out the plan."""
    for tag in sorted({act["tag"] for act in acts} | {"health"}):
        run(["label", "create", tag, "--description", "Filed by health.py file", "--force"], root)
    for kind in sorted({act["label"] for act in acts if act.get("label")}):
        run(["label", "create", kind, "--description", "Filed by health.py file"], root)  # not --force
    gone, have = set(), None
    for stone in sorted({act["stone"] for act in acts if act.get("stone") and act["kind"] == "open"}):
        try:
            have = MS.held(root) if have is None else have
            _, why = MS.make(root, stone, have, True)
        except SystemExit as error:
            why = str(error)
        if why:
            print("FAILED milestone %s: %s" % (stone, why[:160]))
            gone.add(stone)
    lost = set()
    for label in sorted({act["feature"] for act in acts if act.get("feature")}):
        made = run(["label", "create", label, "--description", "Filed by health.py file", "--force"], root)
        if made.returncode:
            print("FAILED label %s: %s" % (label, made.stderr.strip()[:160]))
            lost.add(label)
    for act in acts:
        if act["kind"] == "same":
            print("SAME #%s %s" % (act["number"], act["key"]))
            continue
        if act.get("feature") in lost or act.get("stone") in gone:
            act = dict(act, feature="" if act.get("feature") in lost else act.get("feature"), stone="" if act.get("stone") in gone else act.get("stone"))
        if act["kind"] == "link":
            if linked(root, act["number"], act):
                print("SAME #%s %s (already linked)" % (act["number"], act["key"]))
                continue
            done = run(["issue", "comment", act["number"]], root, "%s\nHealth finds this here: %s" % (
                LINK % (act["key"], act["evidence"]), act["body"].split("\n\n")[1]))
        else:
            done = run(args_of(act), root, issue_text(act))
            if done.returncode not in (0, 127) and "label" in done.stderr.lower() and act.get("feature") and act["kind"] in ("open", "update"):
                print("FAILED label %s: %s" % (act["feature"], done.stderr.strip()[:160]))
                act = dict(act, feature="")
                done = run(args_of(act), root, issue_text(act))
            if act["kind"] == "reopen" and act.get("unclose") and not done.returncode:
                run(["issue", "edit", act["number"], "--remove-label", "health:closed"], root)
        print(("FAILED %s: %s" % (words(act), done.stderr.strip()[:160])) if done.returncode else "DONE " + words(act))


def number(config, key, default):
    value = config.get(key)
    return value if isinstance(value, (int, float)) and not isinstance(value, bool) and value >= 0 else default


def limit_row(state, subject, rule, detail, fix=""):
    return {"state": state, "family": "cost", "subject": subject, "rule": rule, "detail": detail, "fix": fix}


def limit_rows(root):
    """GRD-2."""
    try:
        with open(os.path.join(root, ".loop", "config.json")) as handle:
            config = json.load(handle)
        done = subprocess.run(["git", "rev-parse", "--git-common-dir"], cwd=root, capture_output=True, text=True)
        loop = os.path.join(os.path.abspath(os.path.join(root, done.stdout.strip() or ".git")), "loop")
    except (OSError, ValueError):
        return []
    rows, live, rounds = [], 0, number(config, "max_merge_rounds", 8)
    for path in glob.glob(os.path.join(loop, "runs", "*.json")):
        try:
            with open(path) as handle:
                state = json.load(handle)
        except (OSError, ValueError):
            continue
        if not isinstance(state, dict) or state.get("status") in ("done", "merged", "retired", "failed", "stopped"):
            continue
        live += 1
        if rounds and "MERGE_ROUNDS" in str((state.get("waiting") or {}).get("ask", "")):
            rows.append(limit_row("WARN", state.get("slug") or os.path.basename(path)[:-5], "rounds", "waits after more than %d merge-main-and-rerun rounds" % rounds,
                            "land it when main is quiet, or raise max_merge_rounds, then goal.py answer"))
    try:
        with open(os.path.join(loop, "memory-waits.log")) as handle:
            waits = len(handle.read().splitlines())
        if waits and number(config, "min_free_memory_gb", 4):
            rows.append(limit_row("WARN", "memory", "waits", "%d lane wait(s) for free memory (min_free_memory_gb %s)" % (waits, config.get("min_free_memory_gb", 4)), "close sessions to free memory, or lower min_free_memory_gb"))
    except OSError:
        pass
    active = number(config, "max_active_goals", 20)
    if active and live > active:
        rows.append(limit_row("WARN", "goals", "active", "%d goals live, over max_active_goals %d" % (live, active), "finish or stop goals, or raise max_active_goals"))
    try:
        with open(os.path.join(loop, "plan-usage.json")) as handle:
            used = float(json.load(handle)["percent"])
        pause = number(config, "plan_pause_percent", 80)
        if pause and used > pause:
            rows.append(limit_row("WARN", "plan", "usage", "weekly plan usage %g%%, over plan_pause_percent %d%%; no new goal starts" % (used, pause), "wait for the plan to reset, or raise plan_pause_percent"))
    except (OSError, ValueError, KeyError, TypeError):
        pass
    return rows
