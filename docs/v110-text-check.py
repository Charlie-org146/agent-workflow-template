#!/usr/bin/env python3
"""v110-text: check that the units and sentences written from the owner's pinned pages read word for word as on them.
Read-only: it writes nothing. From the repo root: python3 docs/v110-text-check.py OLD_HTML NEW_HTML [marked]
OLD_HTML is the v1.1.0 page (PIN_OLD): DEL-23, DOC-28 and the brief. NEW_HTML is the 17:42 page (PIN_NEW): DEL-17, DEL-19, DEL-22,
DEL-25, DEL-26 and DEL-27, and the principle 3, 4 and 5 sentences (o802, "Yes, as drafted"). Each page is pinned by the first 16 hex
digits of its sha256. Allowed differences: the other repo's name, written "the service repo"; the page notes in brackets after a
principle sentence (a page note is not sentence text); the first letter of a sentence, capitalised. 'marked' also requires Reviewed.
One parser both writes the units (import this file and call units()) and checks them. TD1039."""
import hashlib
import html
import re
import sys

PIN_OLD, PIN_NEW = "cd66455a83be4a0b", "c952ee382c4153f8"
MILE = "https://github.com/Charlie-org146/agent-workflow-template/milestone/34"
META_MILE = "Milestone: [v1.1.0 dry run](%s)" % MILE
FAST = "Principle 3, Fast · Topic: Delivery"
UNITS = {  # id: (page, pinned h2 start, metadata lines before the first heading)
    "DEL-17": ("docs/wiki/Delivery.md", "DEL-17 (revised)", [FAST]),
    "DEL-19": ("docs/wiki/Delivery.md", "DEL-19 (revised again", ["Principle 1, Guided · Topic: Delivery · Release: v1.1.0", META_MILE]),
    "DEL-22": ("docs/wiki/Delivery.md", "DEL-22 ·", [FAST, META_MILE]),
    "DEL-25": ("docs/wiki/Delivery.md", "DEL-25 (new)", [FAST]),
    "DEL-26": ("docs/wiki/Delivery.md", "DEL-26 (new)", [FAST]),
    "DEL-27": ("docs/wiki/Delivery.md", "DEL-27 (new)", [FAST]),
}
OLD_UNITS = {
    "DEL-23": ("docs/wiki/Delivery.md", "DEL-23 (new)", ["Principle 1, Guided · Topic: Delivery · Release: v1.1.0", META_MILE]),
    "DOC-28": ("docs/wiki/Documentation.md", "DOC-28 (revised)", ["Principle 1, Guided · Topic: Documentation · Release: v1.1.0", META_MILE]),
}
LINE = re.compile(r"^- ([A-Z]{2,5}-\d+): \*\*(?:Unreviewed|Reviewed [\d-]+)\*\* (.*?)(?: <!-- reviewed \w+ -->)?$")
SKIP_H3 = {"Review mark", "Revisions", "Adoption and confidence"}  # the repo writes these itself (marks, r1 rows, generated cells)


def md(s):
    s = re.sub(r'<a href="([^"]+)">(.*?)</a>', lambda m: "[%s](%s)" % (md(m[2]), m[1]), s, flags=re.S)
    s = re.sub(r"<strong>(.*?)</strong>", r"**\1**", s, flags=re.S)
    s = re.sub(r"<em>(.*?)</em>", r"*\1*", s, flags=re.S)
    s = re.sub(r"<[^>]+>", "", s)
    return " ".join(html.unescape(s).split())


def load(path, pin):
    raw = open(path, encoding="utf-8").read()
    if hashlib.sha256(raw.encode("utf-8")).hexdigest()[:16] != pin:
        sys.exit("STOP: the pinned page hash differs from " + pin)
    return raw


def section(raw, start):
    m = re.search(r"<section>\s*<h2>%s.*?</section>" % re.escape(start), raw, re.S)
    if not m:
        sys.exit("no section " + start)
    return m[0]


def unit(raw, start, meta):
    """The unit as page lines: (title, sub-bullets, [(req id, req text)], [reference lines])."""
    sec = section(raw, start)
    title = md(re.search(r"<h2>.*? · (.*?)</h2>", sec, re.S)[1])
    want, reqs = list(meta), []
    for part in re.split(r"(?=<h3>)", sec)[1:]:
        h = md(re.search(r"<h3>(.*?)</h3>", part, re.S)[1])
        if h in SKIP_H3:
            continue
        want.append("### " + h)
        if h == "Requirements":
            for rq, note in re.findall(r'<div class="req">(.*?)</div>|<p class="note">(.*?)</p>', part, re.S):
                if note:
                    want.append(md(note))
                    continue
                p = re.search(r'<p><span class="id">(.*?)</span>(.*?)</p>', rq, re.S)
                want.append("%s %s" % (md(p[1]), md(p[2])))
                reqs.append((md(p[1]), md(p[2])))
                for dt, dv in re.findall(r"<dt>(.*?)</dt><dd>(.*?)</dd>", rq, re.S):
                    want.append("**%s.** %s" % (md(dt), md(dv)))
        elif h == "Reference":
            for li in re.findall(r"<li>(.*?)</li>", part, re.S):
                tag = re.match(r"<strong>(\w+):</strong>\s*(.*)", li, re.S)
                want += [tag[1], md(tag[2])]
        elif "<table" in part:
            for tr in re.findall(r"<tbody>(.*?)</tbody>", part, re.S)[0].split("</tr>")[:-1]:
                want.append(" · ".join(md(c) for c in re.findall(r"<td[^>]*>(.*?)</td>", tr, re.S)))
        else:
            want += [md(li) for li in re.findall(r"<li>(.*?)</li>", part, re.S)]
    return title, want, reqs


def units(new_html):
    raw = load(new_html, PIN_NEW)
    return {k: unit(raw, v[1], v[2]) for k, v in UNITS.items()}


def sentences(new_html):
    """Principles 3, 4 and 5: {n: sentence}, from the pin's draft list, page notes dropped, first letter capitalised."""
    sec = section(load(new_html, PIN_NEW), "Principle 3 becomes three principles")
    out = {}
    for n, rest in re.findall(r"<li><strong>(\d) \w+:</strong>(.*?)</li>", sec, re.S):
        s = re.sub(r"\s*\([^()]*\)\s*$", "", md(rest)).strip()
        out[int(n)] = s[0].upper() + s[1:]
    return out


def main(old_html, new_html, marked):
    old, bad = load(old_html, PIN_OLD), 0

    def say(ok, text):
        nonlocal bad
        print(("PASS: " if ok else "FAIL: ") + text)
        bad += not ok

    parsed = units(new_html)
    cases = [(k, v, unit(old, v[1], v[2])) for k, v in OLD_UNITS.items()] + [(k, v, parsed[k]) for k, v in UNITS.items()]
    for fid, (path, _, _), (title, want, _) in cases:
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
        need = bool(marked or fid in OLD_UNITS)
        say(not need or "**Reviewed " in lines[at[0]], "%s is marked Reviewed (required: %s)" % (fid, need))
        svg = open("docs/wiki/flows/%s.svg" % fid, encoding="utf-8").read()
        say("<title>%s %s</title>" % (fid, title.replace("'", "&#x27;")) in svg, "%s: its flow figure is titled with its own ID and title" % fid)
    say(not any("Tokens" in l for l in open("docs/wiki/Delivery.md", encoding="utf-8").read().split("- DEL-17:")[1].split("\n- DEL-")[0].split("\n")), "DEL-17 holds no Tokens line (the pin has none)")
    # the principle sentences: the list health reads, and README, Home and the Principles page
    sent = sentences(new_html)
    say(sorted(sent) == [3, 4, 5], "the pin yields the sentences of principles 3, 4 and 5")
    book = open("skills/workflow-health/references/commands.md", encoding="utf-8").read()
    for n, s in sent.items():
        row = re.search(r"^\| %d \| [^|]* \| ([^|]*) \|" % n, book, re.M)
        say(bool(row) and row[1].strip() == s, "principle %d: the list's sentence equals the pinned one" % n)
        for page in ("README.md", "docs/wiki/Home.md", "docs/wiki/Principles.md"):
            say(s in open(page, encoding="utf-8").read().split("\n"), "principle %d: %s carries the pinned sentence" % (n, page))
    # the control: two emitted units against hand-read pin text, so the parser's own reading is checked
    u = parsed
    say(u["DEL-19"][2][1][1].replace("**", "").startswith("Every goal runs one list of steps: freeze, plan, build, quick checks, tests, merge, after the merge, release."), "control: DEL-19.2 reads as the pin does")
    say(u["DEL-26"][2][4][1].replace("**", "").startswith("Nothing private goes to GitHub: no private-name list and no secrets; CI uses the empty list."), "control: DEL-26.5 reads as the pin does")
    # the brief: the pinned section, one name swapped, first line frozen
    bsec = section(old, "v1.1.0 brief (minor, re-frozen 2026-11-21 10:52)")
    h2 = md(re.search(r"<h2>(.*?)</h2>", bsec, re.S)[1])
    eyebrow = md(re.search(r'<div class="eyebrow">(.*?)</div>', bsec, re.S)[1])
    ul = re.search(r"<ul>(.*)</ul>\s*</section>", bsec, re.S)[1]
    want = ["## " + h2, "", eyebrow, ""]
    ul2 = re.sub(r"<ol>.*?</ol>", lambda m: m[0].replace("<li>", "<oli>").replace("</li>", "</oli>"), ul, flags=re.S)
    for it in re.findall(r"<li>(.*?)</li>\s*(?=<li>|\Z)", ul2, re.S):
        if "<ol>" in it:
            head, rest = it.split("<ol>", 1)
            want.append("- " + md(head))
            want += ["  %d. %s" % (n, md(x)) for n, x in enumerate(re.findall(r"<oli>(.*?)</oli>", rest, re.S), 1)]
        else:
            want.append("- " + md(it))
    assert len(re.findall(r"<li>", ul2)) == sum(1 for w in want if w.startswith("- ")), "a top-level bullet of the pinned section was not read"
    text = "\n".join(want) + "\n"
    named = re.search(r"the (\w+) feature migration \((\w+)#1240", text)
    other = named[1].lower() if named and named[1] == named[2] else None
    say(other is not None, "the pinned brief names the other repo once in the expected place")
    if other:
        text = text.replace(named[0], "the service repo feature migration (the service repo #1240")
    say(bool(other) and other not in text.lower(), "the expected brief text holds no other repo's name after the one swap")
    brief = open("docs/release-brief-v1.1.0.md", encoding="utf-8").read()
    say(brief.split("\n", 1)[0].startswith("v1.1.0 Frozen"), "the brief's first line says frozen")
    say(bool(other) and other not in brief.lower(), "the brief file holds no other repo's name")
    say(brief.split("\n", 2)[2:] == [text], "the brief is its frozen first line, a blank line and the pinned section word for word, nothing else (only that name swapped)")
    print("ALL PASS" if not bad else "%d FAILED" % bad)
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1], sys.argv[2], len(sys.argv) > 3 and sys.argv[3] == "marked"))
