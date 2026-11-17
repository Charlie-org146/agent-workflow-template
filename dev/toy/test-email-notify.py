#!/usr/bin/env python3
# windows: ok
# reads: skills/workflow-monitoring/scripts/notify.py skills/workflow-monitoring/scripts/operate.py skills/workflow-health/scripts/mail.py skills/workflow-setup/scripts/settings.py
"""MON-5: with notify_email on, each new check-in event (a Needs you item, a stopped goal, a released goal) is mailed
once through mail.py, naming the goal and the owner's action; a repeat sends nothing; off sends nothing; the first run
records a baseline; no address is printed or kept. A local Cloudflare stub stands in for the mail service."""
import http.server
import json
import os
import subprocess
import sys
import tempfile
import threading

here = os.path.dirname(os.path.abspath(__file__))
top = os.path.abspath(os.path.join(here, "..", ".."))
NOTIFY = os.path.join(top, "skills", "workflow-monitoring", "scripts", "notify.py")
SETTINGS = os.path.join(top, "skills", "workflow-setup", "scripts", "settings.py")
ADDR = "owner.fixture@example.test"
failed, posts = [], []


def check(ok, text):
    print(("PASS: " if ok else "FAIL: ") + text)
    if not ok:
        failed.append(text)


class Stub(http.server.BaseHTTPRequestHandler):
    def do_POST(self):
        posts.append(json.loads(self.rfile.read(int(self.headers.get("Content-Length") or 0)) or b"{}"))
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

CHECKIN = """3 running, 1 waiting on you, 0 queued; pool: 2 free
Machine: RAM 9.0 GB free

Needs you
1. ask-goal asks: keep the old flag?; options: "keep" / "drop"; recommended: keep [blocks nothing]

Coming up
- next check-in in 30 minutes
"""

with tempfile.TemporaryDirectory() as tmp:
    root = os.path.join(tmp, "toyrepo")
    subprocess.run(["git", "init", "-q", "-b", "main", root], check=True)
    os.makedirs(os.path.join(root, ".loop"))
    with open(os.path.join(root, ".loop", "config.json"), "w") as f:
        json.dump({"base": "main"}, f)
    runs = os.path.join(root, ".git", "loop", "runs")
    os.makedirs(runs)
    flow, env_file, checkin = (os.path.join(tmp, n) for n in ("flow.json", "mail.env", "checkin.txt"))
    state = os.path.join(root, ".git", "loop", "notified.json")
    env = dict(os.environ, HOME=tmp, USERPROFILE=tmp, LOOP_FLOW=flow, LOOP_MAIL_ENV=env_file, DIGEST_MAIL_RETRY_SECONDS="0",
               DIGEST_MAIL_API="http://127.0.0.1:%d" % server.server_address[1])
    for name in ("DIGEST_TO", "DIGEST_FROM", "CLOUDFLARE_ACCOUNT_ID", "CLOUDFLARE_EMAIL_TOKEN", "DIGEST_SMTP_TEST_PORT", "LOOP_ROLE"):
        env.pop(name, None)

    def setting(on):
        with open(flow, "w") as f:
            json.dump({"notify_email": on}, f)

    def run(text=""):
        with open(checkin, "w") as f:
            f.write(text)
        done = subprocess.run([sys.executable, NOTIFY, "send", "--checkin", checkin], cwd=root, env=env, capture_output=True, text=True)
        return done.stdout + done.stderr

    def record(slug, **fields):
        with open(os.path.join(runs, slug + ".json"), "w") as f:
            json.dump(dict(slug=slug, goal="A goal (MON-5)", **fields), f)

    with open(env_file, "w") as f:
        f.write("DIGEST_TO=%s\nDIGEST_FROM=loop@mail.example.test\nCLOUDFLARE_ACCOUNT_ID=acct-fixture\nCLOUDFLARE_EMAIL_TOKEN=cf-token-fixture-7Q2\n" % ADDR)
    os.chmod(env_file, 0o600)

    setting(False)
    record("stop-goal", status="stopped", step="qa", attempt=1, finding="finding:stop-goal-qa")
    out = run(CHECKIN)
    check(not posts and not out.strip() and not os.path.exists(state), "with notify_email off nothing is sent, printed or kept")

    setting(True)
    out = run(CHECKIN)
    check(not posts and "baseline 2 events" in out and os.path.exists(state), "the first run records the current events as a baseline and sends none")
    os.remove(state)
    os.remove(os.path.join(runs, "stop-goal.json"))
    run("")  # an empty baseline: every event below is new

    record("stop-goal", status="stopped", step="qa", attempt=1, finding="finding:stop-goal-qa")
    record("done-goal", status="done", step="release", pr="https://example.test/pull/7", release="cut", release_version="1.2.0")
    record("busy-goal", status="running", step="build")
    out = run(CHECKIN)
    subjects = sorted(p.get("subject", "") for p in posts)
    texts = " ".join(p.get("text", "") for p in posts)
    check(len(posts) == 3 and out.count("NOTIFY: sent") == 3, "three new events give three mails (%d sent)" % len(posts))
    check(any("ask-goal" in s for s in subjects) and any("stop-goal" in s for s in subjects) and any("done-goal" in s for s in subjects),
          "each mail's subject names its goal (%s)" % "; ".join(subjects))
    check('recommended: keep' in texts and "resume it or retire it" in texts and "released as v1.2.0" in texts,
          "each mail names the owner's action")
    check(all(p.get("to") == ADDR for p in posts), "the mail goes to mail.env's address")

    posts.clear()
    out = run(CHECKIN)
    check(not posts and not out.strip(), "a repeat sends nothing")
    out = run(CHECKIN.replace("keep [blocks nothing]", "keep [holds up a, b (2 goals)]"))
    check(not posts, "the same Needs you item with a new holds-up note is not new")

    record("stop-goal", status="stopped", step="qa", attempt=2, finding="finding:stop-goal-qa")
    os.remove(env_file)
    out = run(CHECKIN)
    check(not posts and "MAIL_NOT_SET_UP" in out, "with no mail.env nothing is sent and the line says not set up")
    with open(env_file, "w") as f:
        f.write("DIGEST_TO=%s\nDIGEST_FROM=loop@mail.example.test\nCLOUDFLARE_ACCOUNT_ID=acct-fixture\nCLOUDFLARE_EMAIL_TOKEN=cf-token-fixture-7Q2\n" % ADDR)
    os.chmod(env_file, 0o600)
    out = run(CHECKIN)
    check(len(posts) == 1 and "stop-goal" in posts[0].get("subject", ""), "an event held for a missing mail.env goes out once it is there")

    kept = open(state).read()
    check(ADDR not in out and ADDR not in kept and "owner.fixture" not in kept, "no address is printed or kept in notified.json")

    ref = subprocess.run([sys.executable, SETTINGS, "reference"], capture_output=True, text=True).stdout
    private = ref.split("## Private settings", 1)[-1]
    check("| `notify_email` | `false` |" in private, "the settings reference lists notify_email as a private setting, off by default")
    operate = open(os.path.join(top, "skills", "workflow-monitoring", "scripts", "operate.py")).read()
    check('script("notify.py", "send"' in operate and "checkin.txt" in operate, "operate.py saves each check-in and runs notify.py send")

server.shutdown()
print("ALL PASS" if not failed else "FAILED: %d" % len(failed))
sys.exit(1 if failed else 0)
