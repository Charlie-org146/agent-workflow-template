#!/usr/bin/env python3
"""Rebuilds the two System design figures from the README's principle tables: python3 dev/system-design.py [--check].
Each number is how many of a principle's requirements name the feature in the Feature column. Not shipped: the package holds skills/ only."""
import collections, re, sys
OUT = {"principle": "docs/wiki/system-design-by-principle.svg", "feature": "docs/wiki/system-design-by-feature.svg"}
NAMES = ["Docs-driven", "Enforced", "Fast, cheap", "Private", "Reproducible", "Autonomous", "Standard", "Honest"]
AREAS = [("Build loop", ["Delivery", "Operation", "Check in and board"]), ("Quality", ["Regression", "Health", "Guardrails"]),
         ("Docs", ["Documentation"]), ("Operations", ["Automation", "Machines", "Setup"]), ("Other", ["Release", "Integrations"])]
SHORT = {"Check in and board": "Check-in and board"}
LIGHT = ["#3b6fd6", "#d9822b", "#2f8f4a", "#c5483f", "#8a5cd6", "#0f8f9c", "#a8791a", "#cc3f7c"]
DARK = ["#6d9bf0", "#f0a050", "#4fb56c", "#e0736a", "#b08cf0", "#3fc4d2", "#e0b84a", "#f07aa8"]
F = "system-ui,-apple-system,Segoe UI,sans-serif"
CAP = "Each number is how many of this principle's requirements are on this feature. One figure for all principles."

def counts(readme):
    got = collections.Counter()
    for sec in re.split(r"\n(?=## )", readme):
        m = re.match(r"## (\d)\. ", sec)
        if not m:
            continue
        rows = sec.split("\n")
        head = next(i for i, r in enumerate(rows) if r.startswith("| Requirement"))
        col = [c.strip() for c in rows[head].strip("|").split("|")].index("Feature")
        for r in rows[head + 2:]:
            if not r.startswith("|"):
                break
            for name in re.findall(r"([^,()]+?) \([^)]+\)", re.split(r"(?<!\\)\|", r.strip()[1:-1])[col]):
                got[(int(m[1]), name.strip())] += 1
    return got

def top(o, title, h):
    c = "".join(".c%d{fill:%s}" % (i + 1, v) for i, v in enumerate(LIGHT)); d = "".join(".c%d{fill:%s}" % (i + 1, v) for i, v in enumerate(DARK))
    o.append('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 640 %d" width="640" role="img" aria-label="%s"><title>%s</title>' % (h, title, title))
    o.append("<style>.t{font:600 15px %s;fill:#1b2430}.h{font:600 9px %s;fill:#566173;letter-spacing:.04em}.s{font:400 11px %s;fill:#27303c}.x{font:400 10.5px %s;fill:#566173}.n{font:400 9px %s;fill:#27303c}.k{font:700 10px %s;fill:#fff}"
             ".bg{fill:#fff}.you{fill:#e4eeff;stroke:#3b6fd6}.box{fill:#f3f5f8;stroke:#8a94a3}.stripe{fill:#f3f5f8}.rule{stroke:#8a94a3;stroke-width:1}.a{stroke:#6b7686;stroke-width:1.5;fill:none}.ah{fill:#6b7686}%s"
             "@media (prefers-color-scheme: dark){.t{fill:#eef2f6}.h,.x{fill:#a3afbf}.s,.n{fill:#e1e7ee}.k{fill:#12171d}.bg{fill:#12171d}.you{fill:#162a4f;stroke:#6d9bf0}.box{fill:#222b36;stroke:#5c6b7d}.stripe{fill:#181e26}.rule{stroke:#5c6b7d}.a{stroke:#9aa7b8}.ah{fill:#9aa7b8}%s}</style>" % (F, F, F, F, F, F, c, d))
    o.append('<defs><marker id="ah" viewBox="0 0 8 8" refX="7" refY="4" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 0 L8 4 L0 8 z" class="ah"/></marker></defs><rect width="640" height="%d" class="bg"/>' % h)
    o.append('<text x="12" y="22" class="t">%s</text>' % title)
    o.append('<rect x="240" y="32" width="160" height="34" rx="8" class="you" stroke-width="1.2"/><text x="320" y="48" text-anchor="middle" class="s">The owner</text><text x="320" y="61" text-anchor="middle" class="x">any machine</text>')
    o.append('<path d="M320 66 L320 82" class="a" marker-end="url(#ah)"/><text x="326" y="78" class="x">says a goal, answers what is theirs</text>')

def bottom(o, y):
    o.append('<text x="12" y="%d" class="h">OUTSIDE SYSTEMS</text>' % (y + 12))
    for i, (t, sub) in enumerate([("GitHub", "repos, wiki, Actions"), ("Agent tools", "Claude Code, Codex"), ("The PC and the Mac", "the hardware it runs on")]):
        x = 28 + i * 204
        o.append('<rect x="%d" y="%d" width="176" height="40" rx="8" class="box" stroke-width="1.2"/><text x="%d" y="%d" text-anchor="middle" class="s">%s</text><text x="%d" y="%d" text-anchor="middle" class="x">%s</text>' % (x, y + 20, x + 88, y + 36, t, x + 88, y + 50, sub))
    o.append('<text x="12" y="%d" class="x">%s</text></svg>' % (y + 78, CAP))

def cell(o, x, y, n, k):
    o.append('<circle cx="%.1f" cy="%.1f" r="8.5" class="c%d"/><text x="%.1f" y="%.1f" text-anchor="middle" class="k">%d</text>' % (x, y, k, x, y + 3.6, n))

def by_feature(c):
    o = []; top(o, "System design, by feature: how many requirements each principle has", 592)
    cx = [196 + i * 50 for i in range(8)]
    for i, n in enumerate(NAMES):
        o.append('<circle cx="%d" cy="104" r="8" class="c%d"/><text x="%d" y="107.5" text-anchor="middle" class="k">%d</text><text x="%d" y="128" text-anchor="middle" class="n"%s>%s</text>' % (cx[i], i + 1, cx[i], i + 1, cx[i], ' textLength="46" lengthAdjust="spacingAndGlyphs"' if len(n) > 10 else "", n))
    o.append('<text x="%d" y="128" text-anchor="middle" class="n">Total</text>' % 600)
    y, r = 140, 0
    for area, feats in AREAS:
        t0 = y
        for f in feats:
            if r % 2 == 0: o.append('<rect x="12" y="%d" width="616" height="26" class="stripe"/>' % y)
            o.append('<text x="86" y="%d" class="s">%s</text>' % (y + 17, SHORT.get(f, f)))
            tot = 0
            for n in range(1, 9):
                if c[(n, f)]: cell(o, cx[n - 1], y + 13, c[(n, f)], n); tot += c[(n, f)]
            o.append('<text x="600" y="%d" text-anchor="middle" class="s" style="font-weight:600">%d</text>' % (y + 17, tot))
            y += 26; r += 1
        o.append('<text x="16" y="%d" class="h">%s</text><path d="M12 %d L628 %d" class="rule"/>' % ((t0 + y) // 2 + 3, area.upper(), y, y)); y += 5
    bottom(o, y + 6)
    return "\n".join(o) + "\n"

def by_principle(c):
    o = []; top(o, "System design, by principle: how many requirements it has on each feature", 560)
    feats = [f for _, fs in AREAS for f in fs]; W, x0, xs = 34, 130, {}
    x = x0
    for area, fs in AREAS:
        l = x
        for f in fs: xs[f] = x + W / 2; x += W
        o.append('<text x="%.1f" y="94" text-anchor="middle" class="h">%s</text><path d="M%d 98 L%d 98" class="rule"/>' % ((l + x) / 2, area.upper().replace("OPERATIONS", "OPER."), l + 2, x - 2)); x += 6
    for f in feats:
        o.append('<text transform="translate(%.1f 104) rotate(-90)" x="-84" y="3" class="n" style="font-size:9.5px">%s</text>' % (xs[f], SHORT.get(f, f)))
    tx = x + W / 2 - 4
    o.append('<text x="%.1f" y="196" text-anchor="middle" class="n">Total</text>' % tx)
    y = 198
    for n in range(1, 9):
        if n % 2: o.append('<rect x="12" y="%d" width="616" height="30" class="stripe"/>' % y)
        o.append('<circle cx="26" cy="%d" r="8" class="c%d"/><text x="26" y="%.1f" text-anchor="middle" class="k">%d</text><text x="40" y="%d" class="s">%s</text>' % (y + 15, n, y + 18.5, n, y + 19, NAMES[n - 1]))
        tot = 0
        for f in feats:
            if c[(n, f)]: cell(o, xs[f], y + 15, c[(n, f)], n); tot += c[(n, f)]
        o.append('<text x="%.1f" y="%d" text-anchor="middle" class="s" style="font-weight:600">%d</text>' % (tx, y + 19, tot))
        y += 30
    o.append('<path d="M12 %d L628 %d" class="rule"/>' % (y, y))
    bottom(o, y + 12)
    return "\n".join(o) + "\n"

def build(readme):
    c = counts(readme)
    return {OUT["principle"]: by_principle(c), OUT["feature"]: by_feature(c)}, sum(c.values())

if __name__ == "__main__":
    figs, total = build(open("README.md").read())
    if "--check" in sys.argv:
        stale = [p for p, t in figs.items() if not __import__("os").path.exists(p) or open(p).read() != t]
        print("system-design figures %s (%d requirement links)" % ("are current" if not stale else "are stale: " + ", ".join(stale) + "; run python3 dev/system-design.py", total))
        sys.exit(1 if stale else 0)
    for p, t in figs.items():
        open(p, "w").write(t)
    print("WROTE %s (%d requirement links)" % (", ".join(figs), total))
