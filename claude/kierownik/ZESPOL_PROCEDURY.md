# ZESPOL_PROCEDURY — machine setup, team changes, running backup CLIs

Read by the lead (SKILL.md, file list) only when the trigger occurs:
A — ZESPOL.md is not filled in; B — the owner writes `zespół: …` or a limit message arrives;
C — before the first Codex/`agy` run in a session. State goes into ZESPOL.md, never into this file.

## A. Machine setup (once; afterwards only ZESPOL.md updates)

The Claude team needs no setup beyond installing the subagents; in ZESPOL.md fill in only the column
„Wskazuje dziś na” of the class table (the owner's answer from point 3). The backup is set up like this:
1. Detect the backup tools (`codex --version`, `agy --version`). For each available one check `--help` of the
   non-interactive mode (incl. model selection) — don't assume flags from memory. A tool with state
   `wyłączony przez właściciela` in ZESPOL.md is skipped completely (no smoke test, no use).
2. Smoke test of each backup tool in a temporary directory with a git repository, with exactly the command you
   will use later (part C: order from a file, result and stderr to files): „utwórz plik ok.txt z treścią OK
   i uruchom `git status`”. Success = the file exists and the answer contains the `git status` output. For
   `agy` read stderr: a "soft-denied"-type message means shell commands were skipped despite exit code 0 (an
   observation, not documentation — hence the criterion). The test uses up limit — if the tool reports an
   exhausted limit, record that as its state and skip the test.
3. Ask the owner one combined question (with proposed answers) about the backup tools' limits and what
   `/model` shows. Record everything in ZESPOL.md.

## B. A class is unavailable or a new model appears

Signal: the owner writes `zespół: …` (e.g. "fable wymaga credits", "wyszedł nowy model X", "nie używaj codex")
or the lead gets a limit message. Aliases and the note "Requires usage credits" are visible in `/model`, which
the owner reads out.

1. **NAJMOCNIEJSZY outside the plan's limit** ("Requires usage credits", limit, not in the plan) → MOCNY replaces it:
   - in `~/.claude/agents/kier-architekt.md` change `model: fable` → `model: opus` (keep the effort); in the
     current thread also pass `model: opus` when calling `kier-architekt` (the parameter takes precedence);
   - wherever SKILL.md section 7 calls for NAJMOCNIEJSZY (review of MOCNY work, of ŚREDNIE/WYSOKIE-risk tasks,
     stage goal verification), pass the MOCNY alias. Only when the reviewer thereby ends up in the author's class
     (author MOCNY, also you) does the same-class exception apply (SKILL.md, section 7): your own tests (section 8,
     point 2) and „recenzja tą samą klasą” in TODO.md and the stage report. A STANDARDOWY author reviewed by
     MOCNY is still one class above — no exception, no label;
   - plan review is then done by a second, fresh `kier-architekt` in the same class MOCNY; add
     „recenzja planu tą samą klasą” to the TODO.md header („Ustalenia”);
   - record the state (class table, „Limity”) and an entry in „Historia zmian”; when the class returns — undo
     and record that too.
2. **New version in an existing line** (e.g. the next Opus): the alias points to it automatically — nothing
   changes in the agents. Fix the column „Wskazuje dziś na” and the date. Effort levels don't mean the same
   across model generations: if the vendor changed the recommended effort for the line, fix `effort:` of the
   agents of that class.
3. **New line, new alias or a change in the strength order**: assign the model to a class (strength and cost
   relative to the others) and confirm with the owner; change the alias in the class table and `model:` in the
   frontmatter of that class's agents (alias or full model ID; a full ID works only in frontmatter — the
   call-time `model` parameter accepts aliases only, so a line without an alias can't be used for a class
   change at call time; note that in „Uwagi”). For class MOCNY also: the „Kierownik” row of the role table,
   the `"model"` value in the settings.json template (`${CLAUDE_SKILL_DIR}/SZABLONY.md`, section 8) and in the
   current project's `.claude/settings.json`; the package README (not installed) gives the old alias in
   `/model` — tell the owner. Check effort (point 2).
4. A permanent effort change of a role is made in the agent file only after an observed problem or a measured
   gain, with the reason in „Historia zmian”; the role table in ZESPOL.md must match the frontmatter.
5. Every change → an entry in „Historia zmian”.

## C. Running Codex / `agy`

Used only: (a) when Claude is unavailable, (b) for an other-family review in the cases from SKILL.md, section 7.
Choice: a tool with state `dostępny`; if both are available — the one with more limit left. A tool with state
`wyłączony przez właściciela` is skipped completely.

Directories: `<repo>` = absolute project path. `<katalog roli>`: executor — `<repo>/.kierownik/wt/T-NNN`
(worktree of the task branch, created by the lead per SKILL.md, section 5, step 3); reviewer —
`<repo>/.kierownik/wt/T-NNN-rec`, a detached worktree on the branch's commit
(`git worktree add --detach <repo>/.kierownik/wt/T-NNN-rec task/T-NNN-nazwa`, because the same branch can't be
checked out in two worktrees), created before the order is written. `-rec` is a fresh checkout — before running
the CLI reviewer install the dependencies there („Instalacja” in AGENTS.md) and copy the test configuration (what
the ŚRODOWISKO line of order A says), because Codex in `-s read-only` won't do that itself; dependencies and
`.env` are git-ignored, so `git status --short` stays empty.

Write the order (template A/B from ZLECENIA.md, with its `[CLI]` lines) to
`<repo>/.kierownik/T-NNN-<rola>.zlecenie.md` and pass it from the file, never inline — backticks and quotes from
the order pasted into the command line would be executed by the shell or would break the argument. Commands
below are for a POSIX shell; in PowerShell use `agy -p (Get-Content -Raw <plik>) …` and
`Get-Content <plik> | codex exec … -`. Owner-specific deviations are in ZESPOL.md (backup tools table).

| Tool | Non-interactive command |
|---|---|
| Antigravity CLI (`agy`, Google) | `cd <katalog roli> && agy -p "$(cat <repo>/.kierownik/T-NNN-<rola>.zlecenie.md)" --dangerously-skip-permissions > <repo>/.kierownik/T-NNN-<rola>.md 2> <repo>/.kierownik/T-NNN-<rola>.err`; model selection by the flag from `agy --help` |
| Codex CLI (OpenAI) | `codex exec -C <katalog roli> -s workspace-write -o <repo>/.kierownik/T-NNN-<rola>.md - < <repo>/.kierownik/T-NNN-<rola>.zlecenie.md 2> <repo>/.kierownik/T-NNN-<rola>.err` (review without writing: `-s read-only`; model: `-m <model>` per `codex exec --help`) |

Notes:
- `agy` without `--dangerously-skip-permissions` in `-p` mode may skip shell commands without an error (exit 0,
  a "soft-denied"-type message only on stderr — an observation, not documentation) — always read `.err`.
- No-prompt mode = the agent can run any command on the whole machine; the worktree organises changes in the
  repository but does not limit access. Codex has its own sandbox (`-s`), `agy` doesn't. Hence: only in the role
  directory, no secrets in the order, after the run `git status` and `git log` of the worktree and the `.err` file.
- Codex CLI loads AGENTS.md by itself; `agy` may not — keep the `[CLI: AGENTS.md]` read in its orders until a
  smoke test shows it reads AGENTS.md.
- After a CLI review in the detached worktree: `git status --short` must be empty and `git rev-parse HEAD` equal to
  `git rev-parse task/T-NNN-nazwa` (a commit on a detached HEAD doesn't change `git status`) — otherwise reject
  the verdict. Finally `git worktree remove <repo>/.kierownik/wt/T-NNN-rec` (`--force` when files remained).
  Codex with `-s read-only` may instead review in the author's worktree directory (path from its report).
