# URUCHAMIANIE_CLI — running a CLI runner from the registry (shared by the Claude Code and Codex hosts)

Read by the lead before the first CLI run in a session (SKILL.md, section 7).

Directories — every CLI run gets its own role directory under `<repo>/.kierownik/wt/`, never the main directory or
main itself (`<repo>` = absolute project path):
- executor: `T-NNN` — worktree of the task branch (`git worktree add .kierownik/wt/T-NNN -b task/T-NNN-nazwa main`);
- task reviewer: `T-NNN-rec` — detached worktree on the branch's commit
  (`git worktree add --detach .kierownik/wt/T-NNN-rec task/T-NNN-nazwa`; a branch can't be checked out twice);
- stage verification: `E<n>-rec` — detached worktree on the verified main commit;
- analyst, architect, plan review: `<id>-ro` — detached worktree on the commit the order names: main HEAD by default;
  for a diagnosis of a task, the task branch's commit (the failure may exist only there). Whatever they must read —
  a plan draft, logs, observations — is committed first or passed as a file named in the order (e.g. under
  `<repo>/.kierownik/`), because a fresh worktree sees only commits. They answer in their result file, and the lead
  writes any docs/tasks or ADR content into the repo itself.
Reviewer and stage directories are fresh checkouts — install the dependencies („Instalacja” in AGENTS.md) and the
test configuration (the ŚRODOWISKO line of order A) before the run. Run reviewers with write access to their own
directory (Codex `-s workspace-write`), because tests write build output and caches; independence is protected by the
check afterwards, not by a read-only sandbox. **Cloud / shared checkout** (no extra worktrees allowed): one runner at a
time in the existing checkout — the executor on the task branch, a reviewer only after the executor finished, with
the same check afterwards.

Write the order (ZLECENIA.md, with its `[CLI]` lines — the runner has no `kier-*` role definition) to
`<repo>/.kierownik/T-NNN-<rola>.zlecenie.md` and pass it from the file, never inline — backticks and quotes pasted into
a command line would be executed by the shell. Result to `<repo>/.kierownik/T-NNN-<rola>.md`, stderr to `….err`.
Use the verified command from the registry; starting templates (POSIX; PowerShell: `(Get-Content -Raw <plik>)` or
`Get-Content <plik> | … -`):

| Runner | Starting template — verify with `--help` and the smoke test before use |
|---|---|
| codex-cli | `codex exec -C <katalog roli> -s workspace-write -m <model> -o <wynik> - < <zlecenie> 2> <err>` (analysis only: `-s read-only`) |
| agy-cli | `cd <katalog roli> && agy -p "$(cat <zlecenie>)" --dangerously-skip-permissions <flaga modelu> > <wynik> 2> <err>` — the flag only with the owner's consent recorded in the registry row (ZESPOL_PROCEDURY.md, A.4); none → no flag, no run |
| claude-cli | `cd <katalog roli> && claude -p --model <alias> < <zlecenie> > <wynik> 2> <err>` (permission mode per `claude --help`; no blanket skip-permissions) |
| codex-sub (Codex host) | `python3 <skill>/scripts/run_agent.py --role kier-<rola> --model <model> --cwd <katalog roli> --prompt <zlecenie> --result <wynik>` |

Always pass the model chosen from the registry (`-m`, `--model`, the agy model flag): a fresh CLI otherwise uses its
own configured default, not the lead's model.

Safety: a skip-permissions / no-sandbox flag gives the agent the whole machine, including secrets readable by its
process (keeping secrets out of the order doesn't protect those). Use such a flag only when the registry row records
„zgoda … TAK <data> (potwierdzona na tej maszynie)” — the owner decides, ideally after moving the work into a container
or VM; never on a host whose own rules forbid bypassing approvals (Codex) without that explicit consent. Without it the
runner is used in its prompting/sandboxed mode, or not at all (`agy -p` without the flag silently skips shell
commands — useless for tasks that need them). Everywhere: only in the role directory, no secrets in the order. After every run check the
worktree's `git status` and `git log` and the `.err` file — exit code 0 proves nothing. Codex CLI loads AGENTS.md by
itself; keep `[CLI: AGENTS.md]` for runners whose smoke test didn't show it. After a CLI review or a read-only role: `git status --short` in its directory empty and `git rev-parse HEAD` equal
to the commit the directory was created on — otherwise reject the result. Cleanup removes only worktrees you created
for that order under `<repo>/.kierownik/wt/`: `git worktree remove <that directory>` (`--force` when ignored files
remained). Never remove the shared/cloud checkout, the main directory, or any worktree you didn't create.
Executor commits: a CLI sandbox may protect Git metadata (a worktree's gitdir lives in the main `.git`), so the commit
can fail. The order says: commit if Git allows; if it refuses, leave the changes uncommitted and say so in the report.
The lead then checks `git -C <katalog roli> status --short` against the report and commits them itself
(`git -C <katalog roli> add -A && git -C <katalog roli> commit -m "<typ>(T-NNN): <opis>"`) before the review.
A run that ended on a limit message is not a result: record the limit (ZESPOL_PROCEDURY.md, B.1) and re-route.
