"""Where a release may run from (issue 4020): the repo's main checkout, fast-forwarded to origin/<base>, or the installed
skills; never a path inside the repo's own goal worktrees, nor a checkout behind its base. merge.py and `wiki.py publish`
call where()."""
import os
import sys

import release


def where(script, base=None):
    """The release runs from the main checkout (fast-forwarded to origin/<base>) or the installed skills, never from a path
    in the repo's own goal worktrees, where a goal could loosen the check that judges it, nor from a checkout behind its
    base (issue 4020). A script outside this repo (installed skills, a toy's repo) is not checked."""
    here = os.path.dirname(os.path.realpath(script))
    common = release.git("rev-parse", "--path-format=absolute", "--git-common-dir", cwd=here, check=False)
    mine = release.git("rev-parse", "--path-format=absolute", "--git-common-dir", check=False)
    norm = lambda path: os.path.normcase(os.path.realpath(path))
    if not common or not mine or norm(common) != norm(mine):
        return
    main = os.path.dirname(norm(common))
    if norm(here).startswith(os.path.join(norm(common), "loop", "worktrees") + os.sep):
        sys.exit("REFUSED (RUN_FROM_WORKTREE): %s is inside a goal worktree, where a goal could change the check that judges it. "
                 "Fix: run it from the main checkout %s, fast-forwarded to origin, or from the installed skills." % (script, main))
    base = base or "main"
    if release.run(["git", "fetch", "-q", "origin", base], cwd=here).returncode:
        return  # the base check reports a fetch it cannot make
    behind = release.git("rev-list", "--count", "HEAD..origin/" + base, cwd=here, check=False)
    if behind.isdigit() and int(behind):
        sys.exit("REFUSED (CHECKOUT_BEHIND): this checkout %s is %s commit%s behind origin/%s, so it would judge the goal by old "
                 "rules. Fix: git -C %s merge --ff-only origin/%s, then run it again." % (
                     main, behind, "" if behind == "1" else "s", base, main, base))
