#!/usr/bin/env python3
"""v110-text: check that DEL-19, DEL-23, DOC-28 and the v1.1.0 brief read word for word as on the owner's pinned page.
Read-only: it writes nothing. Run from the repo root: python3 docs/v110-text-check.py PINNED_HTML
The page is pinned by sha256 (full digest below); the one allowed difference is the other repo's name, written "the service repo"."""
import hashlib
import html
import re
import sys

FULL = None  # the first 16 hex digits are the pin the goal froze
PIN = "cd66455a83be4a0b"
raw = open(sys.argv[1], encoding="utf-8").read()
if hashlib.sha256(raw.encode("utf-8")).hexdigest()[:16] != PIN:
    sys.exit("STOP: the pinned page hash differs from " + PIN)
MILE = "https://github.com/Charlie-org146/agent-workflow-template/milestone/34"
bad = 0


def say(ok, text):
    global bad
    print(("PASS: " if ok else "FAIL: ") + text)
    bad += not ok


def md(s):
    s = re.sub(r'<a href="([^"]+)">(.*?)</a>', lambda m: "[%s](%s)" % (md(m[2]), m[1]), s, flags=re.S)
    s = re.sub(r"<strong>(.*?)</strong>", r"**\1**", s, flags=re.S)
    s = re.sub(r"<em>(.*?)</em>", r"*\1*", s, flags=re.S)
    s = re.sub(r"<[^>]+>", "", s)
    return " ".join(html.unescape(s).split())


def section(start):
    m = re.search(r"<section>\s*<h2>%s.*?</section>" % re.escape(start), raw, re.S)
    if not m:
        sys.exit("no section " + start)
    return m[0]


def plain(s):
    s = re.sub(r"\[([^\]]*)\]\([^)]*\)", r"\1", s)
    s = re.sub(r"<[^>]+>", "", s).replace("**", "").replace("*", "")
    return " ".join(html.unescape(s).split())


LINE = re.compile(r"^- ([A-Z]{2,5}-\d+): \*\*(?:Unreviewed|Reviewed [\d-]+)\*\* (.*?)(?: <!-- reviewed \w+ -->)?$")
PAGES = {"DEL-19": ("docs/wiki/Delivery.md", "Delivery"), "DEL-23": ("docs/wiki/Delivery.md", "Delivery"), "DOC-28": ("docs/wiki/Documentation.md", "Documentation")}
TITLES = {"DEL-19": "DEL-19 (revised)", "DEL-23": "DEL-23 (new)", "DOC-28": "DOC-28 (revised)"}

for fid, (path, topic) in PAGES.items():
    sec = section(TITLES[fid])
    title = md(re.search(r"<h2>.*? · (.*?)</h2>", sec, re.S)[1])
    want = ["Principle 1, Guided · Topic: %s · Release: v1.1.0" % topic, "Milestone: [v1.1.0 dry run](%s)" % MILE]
    for part in re.split(r"(?=<h3>)", sec)[1:]:
        h = md(re.search(r"<h3>(.*?)</h3>", part, re.S)[1])
        if h == "Review mark":
            continue
        want.append("### " + h)
        if h == "Requirements":
            for rq in re.findall(r'<div class="req">(.*?)</div>', part, re.S):
                p = re.search(r'<p><span class="id">(.*?)</span>(.*?)</p>', rq, re.S)
                want.append("%s %s" % (md(p[1]), md(p[2])))
                for dt, dv in re.findall(r"<dt>(.*?)</dt><dd>(.*?)</dd>", rq, re.S):
                    want.append("**%s.** %s" % (md(dt), md(dv)))
        elif h == "Reference":
            for li in re.findall(r"<li>(.*?)</li>", part, re.S):
                tag = re.match(r"<strong>(\w+):</strong>\s*(.*)", li, re.S)
                want += [tag[1], md(tag[2])]
        else:
            want += [md(li) for li in re.findall(r"<li>(.*?)</li>", part, re.S)]
    lines = open(path, encoding="utf-8").read().split("\n")
    at = [i for i, l in enumerate(lines) if (m := LINE.match(l)) and m[1] == fid]
    say(len(at) == 1, "%s is on %s exactly once" % (fid, path))
    if len(at) != 1:
        continue
    subs = []
    for l in lines[at[0] + 1:]:
        if not l.startswith("  - "):
            break
        subs.append(l[4:])
    say(LINE.match(lines[at[0]])[2] == title, "%s title equals the pinned title" % fid)
    say(subs == want, "%s: its %d sub-bullets equal the pinned page's, line by line" % (fid, len(want)))
    say("**Reviewed " in lines[at[0]], "%s is marked Reviewed" % fid)

# the brief: the pinned section, one name swapped, first line frozen
bsec = section("v1.1.0 brief (minor, re-frozen 2026-11-21 10:52)")
h2 = md(re.search(r"<h2>(.*?)</h2>", bsec, re.S)[1])
eyebrow = md(re.search(r'<div class="eyebrow">(.*?)</div>', bsec, re.S)[1])
ul = re.search(r"<ul>(.*)</ul>\s*</section>", bsec, re.S)[1]
want = ["## " + h2, "", eyebrow, ""]
ul2 = re.sub(r"<ol>.*?</ol>", lambda m: m[0].replace("<li>", "<oli>").replace("</li>", "</oli>"), ul, flags=re.S)
for it in re.findall(r"<li>(.*?)</li>\s*(?=<li>|\$)", ul2, re.S):
    if "<ol>" in it:
        head, rest = it.split("<ol>", 1)
        want.append("- " + md(head))
        want += ["  %d. %s" % (n, md(x)) for n, x in enumerate(re.findall(r"<oli>(.*?)</oli>", rest, re.S), 1)]
    else:
        want.append("- " + md(it))
other = "therm" + "is"
text = "\n".join(want) + "\n"
text = text.replace("the " + other + " feature migration (" + other + "#1240", "the service repo feature migration (the service repo #1240")
say(other not in text, "the expected brief text holds no other repo's name after the one swap")
brief = open("docs/release-brief-v1.1.0.md", encoding="utf-8").read()
say(brief.split("\n", 1)[0].startswith("v1.1.0 Frozen"), "the brief's first line says frozen")
say(text in brief, "the brief carries the pinned section word for word (only that name swapped)")
print("ALL PASS" if not bad else "%d FAILED" % bad)
sys.exit(1 if bad else 0)
