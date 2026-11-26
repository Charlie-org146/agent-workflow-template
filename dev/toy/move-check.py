#!/usr/bin/env python3
# windows: ok
# reads: dev/toy/move-manifest.json skills/workflow-delivery/scripts/ skills/workflow-release/scripts/merge.py
"""The move check of the make-room goal (pure moves of whole functions into sibling modules).
usage: move-check.py check [--root DIR] [--pin SHA] [--only STEM[,STEM]]   prove the moves (of those scripts) against their base: PASS/FAIL lines, exit 1 on a FAIL
       move-check.py --derive | --apply NAME | --inventory   write the derived prefixes | perform one move | list the toys and rows that name a moved function
The manifest (move-manifest.json) holds the base sha and per move: script, module, doc, functions, derived prefixes (later moves: own base, header lines). A name a moved function uses is `_s.NAME` when it stays in the script, plain when it moves too; a
standard-library module is imported again. Only the header lines differ from a byte-identical move."""
import ast
import builtins
import json
import os
import re
import subprocess
import sys
import symtable

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", ".."))
MAN = os.path.join(HERE, "move-manifest.json")
GIT = os.environ.get("MR_GIT") or REPO  # where git commands run (a row runs this from an archive of a pinned commit)
GUARD = 'os.environ.update(GIT_TERMINAL_PROMPT="0", GH_PROMPT_DISABLED="1", GIT_EDITOR="true", GIT_ASKPASS="true", SSH_ASKPASS="true")'
BAN = ("__file__", "__name__", "traceback", "inspect", "_getframe")
PATH = "if os.path.dirname(os.path.abspath(__file__)) not in sys.path:\n    sys.path.append(os.path.dirname(os.path.abspath(__file__)))"
OUT = []


def say(ok, text):
    OUT.append(ok)
    print(("PASS: " if ok else "FAIL: ") + text)


def base_text(man, path, base=None):
    got = subprocess.run(["git", "show", "%s:%s" % (base or man["base"], path)], capture_output=True, text=True, cwd=GIT)
    return got.stdout if got.returncode == 0 else ""


PIN = [""]


def read(root, path):
    if PIN[0]:
        got = subprocess.run(["git", "show", "%s:%s" % (PIN[0], path)], capture_output=True, text=True, cwd=GIT)
        return got.stdout.replace("\r\n", "\n")
    with open(os.path.join(root, path), encoding="utf-8", newline="") as handle:
        return handle.read().replace("\r\n", "\n")


def tops(tree):
    return {n.name: n for n in tree.body if isinstance(n, ast.FunctionDef)}


def seg(lines, node):
    start = node.decorator_list[0].lineno if node.decorator_list else node.lineno
    return "\n".join(lines[start - 1:node.end_lineno])


def tables(top, name):
    for child in top.get_children():
        if child.get_name() == name and child.get_type() == "function":
            return child
    raise KeyError(name)


def used_globals(table, bound):
    """{name: 'g'|'l'} over a function table and its nested ones."""
    found = {}
    for sym in table.get_symbols():
        n = sym.get_name()
        if sym.is_global() and sym.is_referenced() or sym.is_global() and sym.is_assigned():
            found[n] = "g"
        elif sym.is_local() and n not in found:
            found.setdefault(n, "l")
    for child in table.get_children():
        for n, kind in used_globals(child, bound).items():
            found[n] = "g" if kind == "g" else found.get(n, "l")
    return found


def classify(text, path, funcs):
    """Per function: (prefix names, std names) from the base text."""
    tree, top = ast.parse(text), symtable.symtable(text, path, "exec")
    names = {s.get_name() for s in top.get_symbols() if s.is_assigned() or s.is_imported() or s.is_namespace()}
    std = {}
    for node in tree.body:
        if isinstance(node, ast.Import):
            for alias in node.names:
                if alias.name.split(".")[0] in sys.stdlib_module_names and not alias.asname:
                    std[alias.name.split(".")[0]] = "import " + alias.name
    out = {}
    for fn in funcs:
        pre, sd = set(), set()
        for n, kind in used_globals(tables(top, fn), names).items():
            if kind != "g" or n in funcs:
                continue
            if n in std:
                sd.add(n)
            elif n in names:
                pre.add(n)
            elif not hasattr(builtins, n):
                pre.add(n)
        out[fn] = (sorted(pre), sorted(sd))
    return out, std


def header_names(node):
    """Names a def evaluates when defined."""
    parts = list(node.args.defaults) + [d for d in node.args.kw_defaults if d] + list(node.decorator_list)
    parts += [a.annotation for a in node.args.args + node.args.kwonlyargs if a.annotation] + ([node.returns] if node.returns else [])
    return {m.id for p in parts for m in ast.walk(p) if isinstance(m, ast.Name)}


def derive():
    man = json.load(open(MAN))
    for move in man["moves"]:
        text = base_text(man, move["script"], move.get("base"))
        info, std = classify(text, move["script"], move["functions"])
        tree = tops(ast.parse(text))
        bad = [f for f in move["functions"] if f not in tree]
        if bad:
            sys.exit("REFUSED: %s has no function %s at the base" % (move["script"], ", ".join(bad)))
        move["prefix"] = {f: info[f][0] for f in move["functions"]}
        move["std"] = {n: std[n] for f in move["functions"] for n in info[f][1]}
        late = {f: sorted(header_names(tree[f]) & (set(info[f][0]) | set(move["functions"]))) for f in move["functions"]}
        if any(late.values()):
            sys.exit("REFUSED: a moved def evaluates a script name at definition time: %s" % late)
    json.dump(man, open(MAN, "w"), indent=1)
    print("DERIVED %d moves" % len(man["moves"]))


def rewrite(lines, node, prefix):
    """The function's source with each prefixed global name written `_s.NAME`."""
    first = node.decorator_list[0].lineno if node.decorator_list else node.lineno
    body = ["" + l for l in lines[first - 1:node.end_lineno]]
    hits = [(m.lineno - first, m.col_offset, len(m.id)) for m in ast.walk(node) if isinstance(m, ast.Name) and m.id in prefix]
    for row, col, size in sorted(hits, reverse=True):
        raw = body[row].encode("utf-8")
        body[row] = (raw[:col] + b"_s." + raw[col:]).decode("utf-8")
    return "\n".join(body)


def apply(name):
    man = json.load(open(MAN))
    move = next(m for m in man["moves"] if os.path.basename(m["script"])[:-3] == name)
    path = os.path.join(REPO, move["script"])
    text = open(path, encoding="utf-8", newline="").read()
    lines, tree = text.split("\n"), ast.parse(text)
    fns, drop, chunks = tops(tree), [], []
    for f in move["functions"]:
        node = fns[f]
        chunks.append(rewrite(lines, node, set(move["prefix"][f])))
        first = node.decorator_list[0].lineno if node.decorator_list else node.lineno
        drop.append((first, node.end_lineno))
    code = "\n\n\n".join(chunks)
    std = sorted({v for v in move["std"].values()} | ({"import os"} if "subprocess" in code else set()))
    head = ['"""%s"""' % move["doc"]] + std + ([GUARD] if "subprocess" in code else [])
    mod = "\n".join(head) + "\n\n\n" + code + "\n\n\nimport %s as _s  # noqa: E402\n" % name
    open(os.path.join(os.path.dirname(path), move["module"] + ".py"), "w", encoding="utf-8", newline="").write(mod)
    keep = [l for i, l in enumerate(lines, 1) if not any(a <= i <= b for a, b in drop)]
    new = re.sub(r"\n{4,}", "\n\n\n", "\n".join(keep))
    sibs = {f[:-3] for f in os.listdir(os.path.dirname(path)) if f.endswith(".py")}
    need = move.get("needs") or []
    reg = regline(name)
    block = ("if __name__ in sys.modules:\n    " + reg) if "guard" in need else reg
    pre = ([PATH] if "path" in need else []) + [block]
    lead = []
    if reg not in new and 'sys.modules.setdefault("%s"' % name not in new:
        t2 = ast.parse(new)
        first = next((n for n in t2.body if isinstance(n, (ast.Import, ast.ImportFrom)) and (n.names[0].name if isinstance(n, ast.Import) else n.module or "").split(".")[0] in sibs - {name}), None)
        if first is not None:
            new = "\n".join(new.split("\n")[:first.lineno - 1] + pre + new.split("\n")[first.lineno - 1:])
        else:
            lead = pre  # no sibling import to put it before: it goes just before the re-export
    elif "path" in need and PATH.split("\n")[0] not in new:
        lead = [PATH]
    out = "from %s import %s  # noqa: E402,F401" % (move["module"], ", ".join(move["functions"]))
    t3 = ast.parse(new)
    tail = t3.body[main_at(t3)] if main_at(t3) is not None else None
    rows = new.split("\n")
    at = tail.lineno - 1 if tail else len(rows)
    new = "\n".join(rows[:at] + lead + [out, "", ""] + rows[at:])
    open(path, "w", encoding="utf-8", newline="").write(new)
    print("MOVED %s: %d functions, %d bytes into %s.py" % (name, len(chunks), len(mod.encode()), move["module"]))


def strings(tree):
    return sorted(repr(n.value) for n in ast.walk(tree) if isinstance(n, ast.Constant) and isinstance(n.value, str))


def regline(stem):
    return 'sys.modules.setdefault("%s", sys.modules[__name__])' % stem


def forms(move, stem):
    reg = regline(stem)
    src = {"export": "from %s import %s" % (move["module"], ", ".join(move["functions"])), "registration": reg,
           "guard": "if __name__ in sys.modules:\n    " + reg, "path": PATH}
    return {k: ast.dump(ast.parse(v).body[0]) for k, v in src.items()}


def main_at(tree):
    for i, n in enumerate(tree.body):
        if isinstance(n, ast.If) and any(isinstance(c, ast.Constant) and c.value == "__main__" for c in ast.walk(n.test)):
            return i


def later_than_pin(move, mpath):
    own = move.get("base")
    git = lambda *a: subprocess.run(["git"] + list(a), cwd=GIT, capture_output=True, text=True)
    if not (PIN[0] and own) or git("cat-file", "-e", PIN[0] + "^{commit}").returncode or git("cat-file", "-e", own + "^{commit}").returncode:
        return False
    if git("cat-file", "-e", "%s:%s" % (PIN[0], mpath)).returncode == 0:
        return False
    pin, base = (git("rev-parse", x + "^{commit}").stdout.strip() for x in (PIN[0], own))
    return pin != base and git("merge-base", "--is-ancestor", pin, base).returncode == 0


def check(root, only=()):
    man = json.load(open(MAN))
    if not man["moves"]:
        say(False, "the manifest holds no moves")
        return False
    if only and not set(only) <= {os.path.basename(m["script"])[:-3] for m in man["moves"]}:
        say(False, "--only names no move: " + ",".join(only))
        return False
    checked = 0
    for move in man["moves"]:
        if only and os.path.basename(move["script"])[:-3] not in only:
            continue
        stem = os.path.basename(move["script"])[:-3]
        folder = os.path.dirname(move["script"])
        mpath = os.path.join(folder, move["module"] + ".py")
        if not (move.get("base") or man.get("base")):
            say(False, "%s: the move names no base" % stem)
            continue
        if later_than_pin(move, mpath):
            print("SKIP: %s: added after this pin" % stem)
            continue
        if not PIN[0] and not os.path.exists(os.path.join(root, mpath)):
            print("SKIP %s: not moved yet" % stem)
            continue
        checked += 1
        btext, ntext, mtext = base_text(man, move["script"], move.get("base")), read(root, move["script"]), read(root, mpath)
        btree, ntree, mtree = ast.parse(btext), ast.parse(ntext), ast.parse(mtext)
        blines, mlines = btext.split("\n"), mtext.split("\n")
        bf, nf, mf = tops(btree), tops(ntree), tops(mtree)
        for f in move["functions"]:
            pre = set(move["prefix"][f])
            node = mf.get(f)
            if f not in bf or node is None or f in nf:
                say(False, "%s: %s is not moved exactly once (base %s, old script %s, module %s)" % (stem, f, f in bf, f in nf, node is not None))
                continue
            plain = re.sub(r"\b_s\.(?=(%s)\b)" % "|".join(sorted(pre)) if pre else r"\b_s\.\b\b", "", seg(mlines, node))
            norm = ast.parse(plain).body[0]
            same = ast.dump(norm) == ast.dump(bf[f]) and plain == seg(blines, bf[f])
            say(same, "%s.%s moved byte-identical but for the _s. prefixes" % (stem, f))
            for m in ast.walk(node):
                if isinstance(m, ast.Attribute) and isinstance(m.value, ast.Name) and m.value.id == "_s":
                    print("PREFIX %s %s line %d: _s.%s" % (move["module"], f, m.lineno, m.attr))
            used = {m.id for m in ast.walk(bf[f]) if isinstance(m, ast.Name)} | {m.attr for m in ast.walk(bf[f]) if isinstance(m, ast.Attribute)}
            say(not (set(BAN) & used), "%s.%s uses none of %s" % (stem, f, ", ".join(BAN)))
        info, stds = classify(btext, move["script"], move["functions"])
        say(all(sorted(move["prefix"][f]) == info[f][0] for f in move["functions"]), "%s: the manifest's prefixes equal the free names derived from the base" % stem)
        mtop = symtable.symtable(mtext, mpath, "exec")
        mnames = {x.get_name() for x in mtop.get_symbols() if x.is_assigned() or x.is_imported() or x.is_namespace()}
        for f in move["functions"]:
            if f in mf:
                lost = sorted(n for n, k in used_globals(tables(mtop, f), mnames).items() if k == "g" and n not in mnames and not hasattr(builtins, n))
                say(not lost, "%s.%s has no unresolved global name%s" % (move["module"], f, (": " + ", ".join(lost)) if lost else ""))
        names = {n for n in mf} & set(move["functions"])
        say(f"from {move['module']} import " in ntext and all(re.search(r"\b%s\b" % f, ntext.split("from %s import" % move["module"])[-1].split("\n")[0]) for f in move["functions"]),
            "%s re-exports its moved names from %s" % (stem, move["module"]))
        rest = [ast.dump(n) for n in btree.body if not (isinstance(n, ast.FunctionDef) and n.name in move["functions"])]
        have = [ast.dump(n) for n in ntree.body]
        extra = [n for n in ntree.body if ast.dump(n) not in rest]
        fm, need = forms(move, stem), move.get("needs")
        ok = {"export", "registration"} if need is None else {"export"} | set(need)
        pos = {k: [i for i, n in enumerate(ntree.body) if ast.dump(n) == v and n in extra] for k, v in fm.items()}
        exact = all(ast.dump(n) in {fm[k] for k in ok} for n in extra) and all(len(pos[k]) == 1 for k in ["export"] + (need or [])) \
            and not any(pos[k] for k in fm if k not in ok) and len(pos["registration"]) <= 1
        say(exact and [d for d in map(ast.dump, ntree.body) if d in rest] == rest, "%s: the rest of the script is the base's plus exactly the allowed header lines (%s)" % (stem, ", ".join(k for k in fm if pos[k])))
        for n in extra:
            print("LINE %s %s line %d" % (stem, next((k for k, v in fm.items() if ast.dump(n) == v), "?"), n.lineno))
        exp, tail = (pos["export"] or [None])[0], main_at(ntree)
        say(exp is not None and all(i < exp for k in ("registration", "guard", "path") for i in pos[k]) and (tail is None or exp < tail),
            "%s: the registration and path lines come before the re-export, and that before the main block" % stem)
        body = [n for n in mtree.body if not (isinstance(n, ast.FunctionDef) and n.name in move["functions"])]
        want, gd = {ast.dump(ast.parse(v).body[0]) for v in list(move["std"].values()) + ["import os"]}, ast.dump(ast.parse(GUARD).body[0].value)
        okh = all(isinstance(n, ast.Import) and ast.dump(n) in want or isinstance(n, ast.Expr) and (isinstance(n.value, ast.Constant) or ast.dump(n.value) == gd) for n in body[:-1]) \
            and ast.unparse(body[-1]) == "import %s as _s" % stem and sorted(n.name for n in mtree.body if isinstance(n, ast.FunctionDef)) == sorted(move["functions"])
        say(okh, "%s: the header of %s holds only the docstring, the manifest's imports, the guard line and the _s import, and each moved function exactly once" % (move["module"], move["module"]))
        header = [n for n in mtree.body if not isinstance(n, ast.FunctionDef)]
        want = sorted(strings(btree))
        got = sorted(strings(ast.Module([n for n in ntree.body if ast.dump(n) in rest] + [n for n in mtree.body if isinstance(n, ast.FunctionDef)], [])))
        say(want == got, "%s and %s hold the base's string constants exactly" % (stem, move["module"]))
        say(("subprocess" not in mtext) or "GIT_TERMINAL_PROMPT" in mtext, "%s carries the DEL-10 guard where it starts processes" % move["module"])
    if PIN[0] and not checked:
        say(False, "nothing was checked under this pin")
    return all(OUT)


def inventory():
    man = json.load(open(MAN))
    names = {f for m in man["moves"] for f in m["functions"]} | {os.path.basename(m["script"]) for m in man["moves"]}
    pat = re.compile("|".join(r"\b%s\b" % re.escape(n) for n in sorted(names)))
    for rel in ("dev/toy", "dev/package.py", ".loop/regression.tsv"):
        full = os.path.join(REPO, rel)
        files = [os.path.join(full, f) for f in sorted(os.listdir(full))] if os.path.isdir(full) else [full]
        for f in files:
            if f.endswith((".json", ".bak")) or "move-" in f or not os.path.isfile(f):
                continue
            for n, line in enumerate(open(f, encoding="utf-8", errors="replace"), 1):
                if pat.search(line) and re.search(r"grep|split|open\(|read|cat |\.find\(|count", line):
                    print("%s:%d: %s" % (os.path.relpath(f, REPO), n, line.strip()[:150]))


def main(argv):
    if argv[:1] == ["--derive"]:
        return derive() or 0
    if argv[:1] == ["--apply"] and len(argv) == 2:
        return apply(argv[1]) or 0
    if argv[:1] == ["--inventory"]:
        return inventory() or 0
    if argv[:1] == ["check"]:
        root = argv[argv.index("--root") + 1] if "--root" in argv else REPO
        PIN[0] = argv[argv.index("--pin") + 1] if "--pin" in argv else ""
        return 0 if check(root, argv[argv.index("--only") + 1].split(",") if "--only" in argv else ()) else 1
    print("usage: move-check.py check [--root DIR] [--pin SHA] | --derive | --apply NAME | --inventory")
    return 0 if argv[:1] in (["-h"], ["--help"]) else 2


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
