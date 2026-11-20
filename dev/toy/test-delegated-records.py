#!/usr/bin/env python3
# windows: ok
# reads: skills/workflow-monitoring/scripts/sessions.py skills/workflow-monitoring/scripts/checkin.py skills/workflow-docs/scripts/criteria.py
# reads: skills/workflow-docs/scripts/milestones.py skills/workflow-docs/scripts/deployments.py
"""DOC-2 under o664 (TD465): a delegated record (sessions.py owner-words --from top --delegated TDn --doc2 rN) carries the owner's
asking words; criteria.py revise and review accept it for a wording change that is not a safety class, refuse it for one that is,
and every other path (a plain record, no --user) is refused as before. The next check-in lists each delegated record.
Runs on a scratch copy of this repo, so the real pages and records are never touched."""
import os
import re
import shutil
import subprocess
import sys
import tempfile

here = os.path.dirname(os.path.abspath(__file__))
top = os.path.abspath(os.path.join(here, "..", ".."))
fails = 0


def check(ok, text):
    global fails
    print(("PASS: " if ok else "FAIL: ") + text)
    fails += 0 if ok else 1


scratch = tempfile.mkdtemp(prefix="delegated-")
env = {k: v for k, v in os.environ.items() if not k.startswith(("LOOP_", "CLAUDE"))}
env.update(HOME=scratch, USERPROFILE=scratch, GIT_AUTHOR_NAME="t", GIT_AUTHOR_EMAIL="t@t", GIT_COMMITTER_NAME="t", GIT_COMMITTER_EMAIL="t@t")


def run(*cmd, cwd=None, more=None):
    return subprocess.run(list(cmd), cwd=cwd or work, capture_output=True, text=True, env=dict(env, **(more or {})))


work = os.path.join(scratch, "repo")
os.makedirs(work)
for name in ("skills", "docs", ".loop", "README.md"):
    src = os.path.join(top, name)
    if os.path.isdir(src):
        shutil.copytree(src, os.path.join(work, name), ignore=shutil.ignore_patterns(".git", "__pycache__", "worktrees"))
    elif os.path.exists(src):
        shutil.copy(src, work)
run("git", "init", "-q", "-b", "loop/delegation-records")
run("git", "add", "-A")
run("git", "commit", "-qm", "base")
crit = os.path.join(work, "skills", "workflow-docs", "scripts", "criteria.py")
os.makedirs(os.path.join(work, ".git", "loop"), exist_ok=True)
open(os.path.join(work, ".git", "loop", "operation.id"), "w").write("op-session\n")
OPERATION = {"CLAUDE_SESSION_ID": "op-session"}
sess = os.path.join(work, "skills", "workflow-monitoring", "scripts", "sessions.py")
text = open(os.path.join(work, "docs", "wiki", "Documentation.md")).read()
section = text.split("### DOC-2\n", 1)[1].split("\n### ", 1)[0]
rev = re.search(r"^\| (r\d+) \|", section, re.M).group(1)  # DOC-2's newest revision row


def record(words, ids, *more, who=None):
    done = run(sys.executable, sess, "owner-words", words, "--ids", ids, "--from", "top", *more, more=OPERATION if who is None else who)
    return done, (re.search(r"OWNER-WORDS (o\d+)", done.stdout) or [None, ""])[1]


def revise(rid, new):
    path = os.path.join(scratch, "new.txt")
    open(path, "w").write(new + "\n- One versioned skills package works out of the box in Claude Code and Codex. [SET-10]\n")
    return run(sys.executable, crit, "revise", "SET-10", "--owner-record", rid, "--goal", "delegation-records", "--why", "TD465 delegated toy", "--text-file", path)


ask = "Please say in SET-10 that the package works in Claude Code and Codex"
done, rid = record(ask, "delegation-records,SET-10", "--delegated", "TD465", "--doc2", rev)
row = [r for r in open(os.path.join(work, ".git", "loop", "owner-words.tsv")).read().splitlines() if r.startswith(rid + "\t")]
check(rid and row and "operation-top:delegated:TD465:DOC-2:%s" % rev in row[0], "a delegated record is written, citing TD465, DOC-2's revision and the asking words (%s)" % rid)
for label, who in (("a worker session", {"CLAUDE_SESSION_ID": "op-session", "LOOP_ROLE": "worker"}), ("a session not in operation.id", {"CLAUDE_SESSION_ID": "other-session"}), ("a session with no id", {}), ("a worker that sets the operation id as LOOP_POD_ID", {"LOOP_POD_ID": "op-session", "LOOP_ROLE": "worker"})):
    bad, none = record(ask, "delegation-records,SET-10", "--delegated", "TD465", "--doc2", rev, who=who)
    check(bad.returncode != 0 and "operation session" in bad.stdout + bad.stderr and not none, "a delegated record from %s is REFUSED and nothing is written" % label)
run("git", "worktree", "add", "-q", os.path.join(work, ".git", "loop", "worktrees", "w1"), "-b", "loop/w1")
there = run(sys.executable, sess, "owner-words", ask, "--ids", "SET-10", "--from", "top", "--delegated", "TD465", "--doc2", rev, cwd=os.path.join(work, ".git", "loop", "worktrees", "w1"), more=OPERATION)
check(there.returncode != 0 and "only an operation session" in there.stdout + there.stderr, "the operation session's id used inside a worker worktree is REFUSED")
bad, _ = record(ask, "SET-10", "--delegated", "TD465")
check(bad.returncode != 0 and "REFUSED" in (bad.stdout + bad.stderr), "a delegated record without DOC-2's revision is refused")
bad, _ = record("Delete the old branches and force push", "SET-10", "--delegated", "TD465", "--doc2", rev)
check(bad.returncode != 0 and "safety class" in (bad.stdout + bad.stderr), "a delegated record whose asking words are in a safety class is refused at once")
good = revise(rid, "One versioned package; every agent runs one loop")
check(good.returncode == 0 and "REVISED SET-10" in good.stdout, "revise accepts a delegated record for a wording change that is not a safety class (%s)" % good.stdout.strip()[:60])
done, rid2 = record(ask, "delegation-records,SET-10", "--delegated", "TD465", "--doc2", rev)
seen = run(sys.executable, crit, "review", "SET-10", "--owner-record", rid2)
page = open(os.path.join(work, "docs", "wiki", "Setup.md")).read()
check(seen.returncode == 0 and re.search(r"^- SET-10: \*\*Reviewed \d{4}-\d\d-\d\d\*\*", page, re.M), "review accepts it with no --user, and SET-10 reads Reviewed (%s)" % seen.stdout.strip()[:60])
# the safety-class change: a requirement whose text is in a safety class
open(os.path.join(work, "docs", "wiki", "Setup.md"), "w").write(re.sub(r"^- SET-10: \*\*Reviewed[^\n]*", "- SET-10: **Unreviewed** Never force push main or delete a branch", page, count=1, flags=re.M))
done, rid3 = record(ask, "delegation-records,SET-10", "--delegated", "TD465", "--doc2", rev)
refused = run(sys.executable, crit, "review", "SET-10", "--owner-record", rid3)
check(refused.returncode != 0 and "only the owner changes a review" in refused.stdout + refused.stderr, "review refuses a delegated record for a safety-class requirement, exactly as before")
done, rid4 = record(ask, "delegation-records,SET-10", "--delegated", "TD465", "--doc2", rev)
still = run(sys.executable, crit, "review", "SET-10", "--owner-record", rid4, "--user")
check(still.returncode != 0 and "only the owner changes a review" in still.stdout + still.stderr, "even with --user a delegated record cannot review a safety-class requirement")
done, rid5 = record(ask, "delegation-records,SET-10", "--delegated", "TD465", "--doc2", rev)
refused = revise(rid5, "Never delete a branch or force push")
check(refused.returncode != 0 and "REV-RECORD" in refused.stdout + refused.stderr, "revise refuses a delegated record when the new text is a safety class")
plain, rid6 = record(ask, "delegation-records,SET-10")
refused = run(sys.executable, crit, "review", "SET-10", "--owner-record", rid6)
check(refused.returncode != 0 and "only the owner changes a review" in refused.stdout + refused.stderr, "a plain record with no --user is refused as before (negative control)")
checked = run(sys.executable, os.path.join(work, "skills", "workflow-monitoring", "scripts", "checkin.py"))
check("Delegated approvals" in checked.stdout and rid in checked.stdout, "the next check-in lists each delegated record (%s)" % rid)
shutil.rmtree(scratch, ignore_errors=True)
sys.exit(1 if fails else 0)
