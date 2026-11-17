#!/usr/bin/env python3
# windows: ok
# reads: skills/workflow-monitoring/scripts/mailbox.py skills/workflow-monitoring/scripts/notify.py skills/workflow-monitoring/scripts/operate.py
"""email-first (#4785, #4671): a new Needs-you item and a merged release each give one mail with numbered options and a
recommendation; two machines share one ledger and one send budget; a reply such as "1 recommended" is recorded as the owner's
words (--source owner) and acted on; a risky question needs the owner's own typed words. A local Cloudflare stub is the fake mailer."""
import http.server
import json
import os
import subprocess
import sys
import tempfile
import threading

HERE = os.path.dirname(os.path.abspath(__file__))
MON = os.path.join(HERE, "..", "..", "skills", "workflow-monitoring", "scripts")
NOTIFY, MAILBOX = os.path.join(MON, "notify.py"), os.path.join(MON, "mailbox.py")
FAILS, POSTS = [], []


def check(ok, name):
    print(("PASS: " if ok else "FAIL: ") + name)
    if not ok:
        FAILS.append(name)


class Stub(http.server.BaseHTTPRequestHandler):
    def do_POST(self):
        POSTS.append(json.loads(self.rfile.read(int(self.headers.get("Content-Length") or 0)) or b"{}"))
        body = b'{"success": true, "result": {}}'
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, *args):
        pass


server = http.server.HTTPServer(("127.0.0.1", 0), Stub)
threading.Thread(target=server.serve_forever, daemon=True).start()
CHECKIN = """1 running, 1 waiting on you, 0 queued; pool: 2 free

Needs you
1. ask-goal asks: keep the old flag?; options: "keep" / "drop"; recommended: keep [blocks nothing]
2. risk-goal asks: delete the old branch?; options: "delete" / "keep"; recommended: keep [blocks nothing]

Coming up
- next check-in in 30 minutes
"""


def git(cwd, *args):
    env = dict(os.environ, GIT_AUTHOR_NAME="t", GIT_AUTHOR_EMAIL="t@t", GIT_COMMITTER_NAME="t", GIT_COMMITTER_EMAIL="t@t")
    return subprocess.run(["git", "-c", "commit.gpgsign=false"] + list(args), cwd=cwd, env=env, capture_output=True, text=True)


with tempfile.TemporaryDirectory() as TMP:
    TMP = os.path.realpath(TMP)
    origin = os.path.join(TMP, "origin.git")
    git(TMP, "init", "-q", "--bare", "-b", "main", origin)
    boxes = {}
    flow, env_file, checkin = (os.path.join(TMP, n) for n in ("flow.json", "mail.env", "checkin.txt"))
    with open(env_file, "w") as f:
        f.write("DIGEST_TO=owner.fixture@example.test\nDIGEST_FROM=loop@mail.example.test\nCLOUDFLARE_ACCOUNT_ID=a\nCLOUDFLARE_EMAIL_TOKEN=t\n")
    os.chmod(env_file, 0o600)
    for name in ("pc", "mac"):
        root = os.path.join(TMP, name)
        git(TMP, "clone", "-q", origin, root)
        if name == "pc":
            git(root, "checkout", "-q", "-b", "main")
            os.makedirs(os.path.join(root, ".loop"))
            with open(os.path.join(root, ".loop", "config.json"), "w") as f:
                json.dump({"base": "main"}, f)
            git(root, "add", "-A")
            git(root, "commit", "-q", "-m", "init")
            git(root, "push", "-q", "origin", "main")
        else:
            git(root, "checkout", "-q", "main")
        os.makedirs(os.path.join(root, ".git", "loop", "runs"))
        boxes[name] = root

    def setting(budget=20):
        with open(flow, "w") as f:
            json.dump({"notify_email": True, "machine_sync": True, "notify_budget": budget}, f)

    def env_of(name):
        env = dict(os.environ, HOME=TMP, USERPROFILE=TMP, LOOP_FLOW=flow, LOOP_MAIL_ENV=env_file, LOOP_MACHINE_NAME=name,
                   DIGEST_MAIL_RETRY_SECONDS="0", DIGEST_MAIL_API="http://127.0.0.1:%d" % server.server_address[1])
        for var in ("LOOP_ROLE", "LOOP_POD_ID", "CLAUDE_SESSION_ID", "DIGEST_SMTP_TEST_PORT"):
            env.pop(var, None)
        return env

    def notify(name, text):
        with open(checkin, "w") as f:
            f.write(text)
        done = subprocess.run([sys.executable, NOTIFY, "send", "--checkin", checkin], cwd=boxes[name], env=env_of(name), capture_output=True, text=True)
        return done.stdout + done.stderr

    def record(name, slug, **fields):
        with open(os.path.join(boxes[name], ".git", "loop", "runs", slug + ".json"), "w") as f:
            json.dump(dict(slug=slug, goal="g", **fields), f)

    def reply(name, qid, text):
        done = subprocess.run([sys.executable, MAILBOX, "reply", qid, text], cwd=boxes[name], env=env_of(name), capture_output=True, text=True)
        return done.returncode, done.stdout + done.stderr

    setting()
    for name in boxes:
        notify(name, "")  # an empty baseline on both machines
    for name in boxes:
        record(name, "ask-goal", status="waiting", step="build", waiting={"ask": "keep the old flag?"})
        record(name, "risk-goal", status="waiting", step="build", waiting={"ask": "delete the old branch?"})
        record(name, "done-goal", status="done", step="release", pr="https://example.test/pull/7", release="merged", release_version="2.0.0")
    notify("pc", CHECKIN)
    texts = [p.get("text", "") for p in POSTS]
    ask = next((t for t in texts if "ask-goal" in t), "")
    check(len(POSTS) == 3, "a new Needs-you item and a merged release each give one mail (%d)" % len(POSTS))
    check("1. keep (recommended)" in ask and "2. drop" in ask, "the question has numbered options and a recommendation")
    check(any("released as v2.0.0" in t and "1. noted, nothing to do (recommended)" in t for t in texts), "the release mail has the report and an option")
    check(all("Question id: q-" in t for t in texts), "every mail carries its question id")
    POSTS.clear()
    notify("mac", CHECKIN)
    check(not POSTS, "the other machine sends nothing for events the first mailed: one stream, not one per machine")

    qid = ask.split("Question id: ")[1].split()[0]
    code, out = reply("pc", qid, "1 recommended")
    answers = open(os.path.join(boxes["pc"], ".git", "loop", "answers.jsonl")).read() if os.path.exists(os.path.join(boxes["pc"], ".git", "loop", "answers.jsonl")) else ""
    check(code == 0 and '"source": "owner"' in answers and '"words": "keep"' in answers, "a reply \"1 recommended\" is recorded as owner words with --source owner and acted on")
    check(reply("pc", qid, "1")[0] == 2, "the answered question is not recorded twice")
    risky = next(t for t in texts if "risk-goal" in t).split("Question id: ")[1].split()[0]
    code, out = reply("pc", risky, "1")
    check(code == 2 and "your own words" in out, "a risky step refuses a bare number")
    code, out = reply("pc", risky, "approve")
    check(code == 2, "a risky step refuses approve")
    code, out = reply("pc", risky, "yes, delete the old branch loop/old-thing")
    answers = open(os.path.join(boxes["pc"], ".git", "loop", "answers.jsonl")).read()
    check(code == 0 and "delete the old branch loop/old-thing" in answers, "the owner's own typed words are recorded as written")
    check(reply("pc", "q-nope", "1")[0] == 2, "an unknown question id records nothing")

    setting(1)
    POSTS.clear()
    for name in boxes:
        record(name, "late-a", status="stopped", step="qa", attempt=1, finding="x")
        record(name, "late-b", status="stopped", step="qa", attempt=1, finding="y")
    notify("pc", CHECKIN)
    check(len(POSTS) == 0, "the send budget is shared and counts the first machine's mails (budget 1, 3 already sent)")
    setting(20)
    notify("mac", CHECKIN)
    check(len(POSTS) == 2, "a raised budget lets the held events go out through the other machine (%d)" % len(POSTS))

if FAILS:
    print("FAILED %d" % len(FAILS))
    sys.exit(1)
print("OK")
