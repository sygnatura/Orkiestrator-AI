# URUCHAMIANIE_CLI — running a CLI runner from the registry (shared by the Claude Code and Codex hosts)

Read by the lead before the first CLI run in a session (SKILL.md, section 7).

Directories: `<repo>` = absolute project path. `<katalog roli>`: executor — `<repo>/.kierownik/wt/T-NNN` (worktree of
the task branch: `git worktree add .kierownik/wt/T-NNN -b task/T-NNN-nazwa main`); reviewer —
`<repo>/.kierownik/wt/T-NNN-rec`, a detached worktree on the branch's commit
(`git worktree add --detach <repo>/.kierownik/wt/T-NNN-rec task/T-NNN-nazwa`, because a branch can't be checked out in
two worktrees). `-rec` is a fresh checkout — install the dependencies there („Instalacja” in AGENTS.md) and copy the
test configuration (the ŚRODOWISKO line of order A) before running the reviewer, because a read-only reviewer won't.
A read-only reviewer (`-s read-only`) may instead work in the author's worktree directory (path from its report).

Write the order (ZLECENIA.md, with its `[CLI]` lines — the runner has no `kier-*` role definition) to
`<repo>/.kierownik/T-NNN-<rola>.zlecenie.md` and pass it from the file, never inline — backticks and quotes pasted into
a command line would be executed by the shell. Result to `<repo>/.kierownik/T-NNN-<rola>.md`, stderr to `….err`.
Use the verified command from the registry; starting templates (POSIX; PowerShell: `(Get-Content -Raw <plik>)` or
`Get-Content <plik> | … -`):

| Runner | Starting template — verify with `--help` and the smoke test before use |
|---|---|
| codex-cli | `codex exec -C <katalog roli> -s workspace-write -o <wynik> - < <zlecenie> 2> <err>` (review: `-s read-only`; model `-m <model>`) |
| agy-cli | `cd <katalog roli> && agy -p "$(cat <zlecenie>)" --dangerously-skip-permissions > <wynik> 2> <err>` |
| claude-cli | `cd <katalog roli> && claude -p --model <alias> < <zlecenie> > <wynik> 2> <err>` (permission mode per `claude --help`; read-only tools for review) |
| codex-sub (Codex host) | `python3 <skill>/scripts/run_agent.py --role kier-<rola> --cwd <katalog roli> --prompt <zlecenie> --result <wynik>` |

Safety: a no-prompt CLI can run any command on the whole machine — only in the role directory, never in the main
directory or on main, no secrets in the order; `agy` has no sandbox, Codex has `-s`. After every run check the
worktree's `git status` and `git log` and the `.err` file — exit code 0 proves nothing. Codex CLI loads AGENTS.md by
itself; keep `[CLI: AGENTS.md]` for runners whose smoke test didn't show it. After a CLI review in the detached
worktree: `git status --short` empty and `git rev-parse HEAD` equal to `git rev-parse task/T-NNN-nazwa` — otherwise
reject the verdict; finally `git worktree remove <repo>/.kierownik/wt/T-NNN-rec` (`--force` when files remained).
A run that ended on a limit message is not a result: record the limit (ZESPOL_PROCEDURY.md, B.1) and re-route.
