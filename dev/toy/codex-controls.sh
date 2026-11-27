# Sourced by test-codex.sh; not run by itself.
# reads: dev/toy/codexrun.py dev/toy/hist.py dev/toy/fakecodex .github/workflows/regression-pr.yml
standin() { printf '#!/bin/bash\n%s\n' "$2" > "$1"; chmod +x "$1"; }
# Each rule of the live part, shown on a stand-in: the run must be reported as failed, with its code.
controls() {
  local out KEEP=""  # the stand-in runs below never touch the file a person asked for
  standin "$T/exit3" "bash '$here/dev/toy/fakecodex' \"\$@\"; exit 3"
  out=$(fails=0; as_codex ctl-exit "$T/exit3" "" 60; echo "fails=$fails")
  check "fake: a codex that writes every result and then exits with an error fails, with CODEX-E04" "grep -q '^FAIL: CODEX-E04: ctl-exit: .*Fix: .*In plain words: .*Side effects: PARTIAL' <<<\"\$out\" && grep -q '^fails=1' <<<\"\$out\""
  mkdir -p "$T/ctl-rc" && cp -R "$T/fake/repo/.codex-out" "$T/fake/repo/.loop" "$T/ctl-rc/" && echo 1 > "$T/ctl-rc/.codex-out/merge.rc"
  out=$(fails=0; verify ctl-rc "$T/ctl-rc"; echo "fails=$fails")
  check "fake: a command whose output matches but whose exit status is wrong fails, with CODEX-E05" "grep -q '^FAIL: CODEX-E05: ctl-rc: .*merge exited 1, expected 0' <<<\"\$out\""
  standin "$T/slow" 'sleep 20'
  out=$(fails=0; SECONDS=0; as_codex ctl-slow "$T/slow" "" 2; echo "fails=$fails took=$SECONDS")
  check "fake: a codex past its deadline is stopped and fails, with CODEX-E03" "grep -q '^FAIL: CODEX-E03: ctl-slow: ' <<<\"\$out\" && [ \$(sed -n 's/.*took=//p' <<<\"\$out\") -lt 15 ]"
  printf 'key ghp_%s end\n' "$(printf 'Q7%.0s' {1..18})" > "$T/raw.log"
  cr keep "$T/raw.log" "$T/kept.log" "$here"
  check "fake: a kept Codex log is screened: a secret-shaped value is not copied" "[ -s '$T/kept.log' ] && ! grep -q 'Q7Q7Q7' '$T/kept.log'"
  local word="plantedname""qzx" saved=$caller_names
  printf '%s\n' "$word" > "$T/names"; caller_names="$T/names"
  printf 'about %s here\nan ordinary line\n' "$word" > "$T/named.log"
  cr keep "$T/named.log" "$T/named-kept.log" "$here"
  check "fake: a kept Codex log is screened: a listed private name alone is not copied" "grep -qx 'an ordinary line' '$T/named-kept.log' && ! grep -q '$word' '$T/named-kept.log'"
  out=$(cr screen "cannot reach $word now"; cr line CODEX-E04 ctl-name "cannot reach $word now")
  check "fake: an error line holds no listed private name" "grep -q 'withheld' <<<\"\$out\" && ! grep -q '$word' <<<\"\$out\""
  caller_names=$saved
  mkdir -p "$T/not-a-file"
  out=$(fails=0; KEEP="$T/not-a-file"; as_codex ctl-keep "$here/dev/toy/fakecodex" "" 60; echo "fails=$fails")
  check "fake: a kept log that can't be written fails the run and shows no local path" "grep -q '^REFUSED: the kept log could not be written' <<<\"\$out\" && grep -q '^FAIL: ctl-keep: the kept log you asked for' <<<\"\$out\" && grep -qx 'fails=1' <<<\"\$out\" && ! grep -q \"$T\" <<<\"\$out\""
  # the two admission probes: a stand-in that hangs at sign-in status, or at the one-word reply, is a failure, not a skip
  local stuck
  for stuck in login exec; do
    standin "$T/stuck-$stuck" "[ \"\$1\" = $stuck ] && sleep 20; exit 0"
    out=$(fails=0; live_skip=""; PROBE_LIMIT=2; live_part "$T/stuck-$stuck"; echo "fails=$fails skip=$live_skip")
    check "fake: a $stuck probe past its limit fails with CODEX-E03 and is not a skip" "grep -q '^FAIL: CODEX-E03: live: ' <<<\"\$out\" && grep -qx 'fails=1 skip=' <<<\"\$out\""
  done
  out=$(fails=0; live_skip=""; CR="$T/no-helper.py"; live_part "$T/no-such-codex" 2>/dev/null; echo "fails=$fails skip=$live_skip")
  check "fake: a skip reason the helper can't print is a failure, never a silent pass" "grep -qx 'fails=1 skip=' <<<\"\$out\""
  standin "$T/no-answer" '[ "$1" = login ] && exit 0; echo "ERROR: no reply"; exit 1'
  printf 'import runpy, sys\nif sys.argv[1] == "screen": sys.exit(3)\nrunpy.run_path("%s", run_name="__main__")\n' "$CR" > "$T/no-screen.py"
  out=$(fails=0; live_skip=""; CR="$T/no-screen.py"; live_part "$T/no-answer" 2>/dev/null; echo "fails=$fails skip=$live_skip")
  check "fake: a reply-probe reason the helper can't screen is a failure, never a silent pass" "grep -qx 'fails=1 skip=' <<<\"\$out\""
  standin "$T/lingers" 'sleep 25 & echo OK'
  out=$(SECONDS=0; said=$(cr limited 5 -- "$T/lingers" 2>&1); echo "said=$said took=$SECONDS")
  check "fake: a process left behind holding the output doesn't outlast the program" "grep -q '^said=OK took=' <<<\"\$out\" && [ \$(sed -n 's/.*took=//p' <<<\"\$out\") -lt 15 ]"
  out=$(cr keep "$T/raw.log" "$here/codex-keep-control.log" "$here"; echo "rc=$?")
  check "fake: keeping a Codex log inside the repository is refused" "grep -q '^REFUSED: KEEP names a file inside the repository' <<<\"\$out\" && grep -qx 'rc=2' <<<\"\$out\" && [ ! -e '$here/codex-keep-control.log' ]"
  local limit
  limit=$(grep -oE -- '--timeout [0-9]+' "$here/.github/workflows/regression-pr.yml" | awk '{print $2}' | sort -n | head -1)
  check "fake: the live deadline ($LIVE_DEADLINE s) is strictly under the pull request's row limit (${limit:-unread} s)" "[ -n \"$limit\" ] && [ $LIVE_DEADLINE -lt ${limit:-0} ]"
  check "fake: the run left nothing inside the repository" "[ \"\$(git -C '$here' status --porcelain 2>/dev/null)\" = \"\$inside_before\" ]"
}
