# ZESPOL_PROCEDURY — runner registry procedures (shared by the Claude Code and Codex hosts)

Read by the lead only when the trigger occurs: A — `~/.kierownik/ZESPOL.md` missing or not filled in;
B — the owner writes `zespół: …`, a limit message arrives, or a new model/provider appears; C — before the first
external-CLI run in a session. State goes into `~/.kierownik/ZESPOL.md`, never into this file. "Host" = the tool the
lead runs in (Claude Code or Codex); "runner" = a row of the registry.

## A. Registry setup (once per machine; afterwards only updates)

1. Create `~/.kierownik/ZESPOL.md` (Windows: `%USERPROFILE%\.kierownik\ZESPOL.md`) from ZESPOL_WZOR.md in this
   skill's directory. A filled ZESPOL.md left in an installed skill directory by v10/v11
   (`~/.claude/skills/kierownik/ZESPOL.md`, `~/.agents/skills/kierownik/ZESPOL.md`) is the source: carry over its
   aliases, limits, owner decisions and history into the registry layout; leave the old file in place. A Codex host
   writing outside its workspace asks for approval once; refused → keep the registry in the skill directory and say so.
2. Detect the CLIs (`codex --version`, `agy --version`, `claude --version`, and anything the owner names). For each
   check `--help` of its non-interactive mode: how to pass the order from a file or stdin, set the working directory,
   choose the model and effort, write the result, and its sandbox/permission flags — never assume flags from memory.
   A runner `wyłączony przez właściciela` is skipped completely.
3. Smoke test every available CLI in a temporary directory with a git repository, with exactly the command you will
   use later (part C): „utwórz plik ok.txt z treścią OK i uruchom `git status`”. Success = the file exists and the
   answer contains the `git status` output. Read stderr: a "soft-denied"-type message (seen with `agy`) means shell
   commands were skipped despite exit 0. The test uses up limit — a tool reporting an exhausted limit gets that state
   and no test. Record the verified command in „Polecenia CLI”.
4. Ask the owner one combined question (with proposed answers): which models each subscription offers and their
   class (your proposal from capability and cost), the priority of each runner, the current limits, and what `/model`
   shows. Record everything; set „Stan wypełnienia”.

## B. Changes: limit, new model, new or dropped provider

1. **Limit message from a runner** → `niedostępny do <czas>` (or `niedostępny od <czas>` when no reset time is given),
   then SKILL.md section 7 picks the next candidate for the same order. When the time passes, treat the runner as
   available again on its next use (a new limit message simply sets the state again).
2. **The owner drops a subscription** (`zespół: rezygnuję z X`) → `wyłączony przez właściciela`; nothing else changes.
   **The owner adds one** (`zespół: mam X`) → new row, A.2–A.3 for its CLI, class proposal confirmed by the owner.
3. **New version in an existing line** (an alias already follows it): fix only the model column if it names
   versions. Effort levels don't mean the same across generations: if the vendor changed the recommended effort for
   the line, fix the effort of the roles of that class (agent files / role TOML and the host table).
4. **New line, new alias, or a change in the strength order**: assign the model to a class (capability and cost
   relative to the others), confirm with the owner, update the row. On a Claude Code host, if the class of a default
   role changes: `model:` in `~/.claude/agents/kier-*.md` (alias or full model ID; a full ID works only in frontmatter,
   the call-time `model` parameter takes aliases only) and the host table; for class MOCNY also the `"model"` value in
   the settings.json template (SZABLONY.md, section 8) and the project's `.claude/settings.json`. On a Codex host:
   `model` in the role TOML and the host table.
5. **A whole class is missing on every runner** (e.g. NAJMOCNIEJSZY needs credits nobody wants to pay) → nothing to
   edit in agents: section 7 falls back to the next lower class with the recorded degradation
   („recenzja tą samą klasą”, „plan bez klasy NAJMOCNIEJSZY”).
6. A permanent effort change of a role only after an observed problem or a measured gain, with the reason in
   „Historia zmian”. Every change → an entry in „Historia zmian”.

## C. Running an external CLI runner

Directories: `<repo>` = absolute project path. `<katalog roli>`: executor — `<repo>/.kierownik/wt/T-NNN` (worktree of
the task branch: `git worktree add .kierownik/wt/T-NNN -b task/T-NNN-nazwa main`); reviewer —
`<repo>/.kierownik/wt/T-NNN-rec`, a detached worktree on the branch's commit
(`git worktree add --detach <repo>/.kierownik/wt/T-NNN-rec task/T-NNN-nazwa`, because a branch can't be checked out in
two worktrees). `-rec` is a fresh checkout — install the dependencies there („Instalacja” in AGENTS.md) and copy the
test configuration (the ŚRODOWISKO line of order A) before running the reviewer, because a read-only reviewer won't.

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
reject the verdict; finally `git worktree remove <repo>/.kierownik/wt/T-NNN-rec` (`--force` when files remained). A
read-only reviewer (`-s read-only`) may instead work in the author's worktree directory.
