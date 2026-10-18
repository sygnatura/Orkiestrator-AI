# ZESPOL_PROCEDURY — runner registry procedures (shared by the Claude Code and Codex hosts)

Read by the lead only when the trigger occurs: A — no registry found (SKILL.md, section 1) or „Stan wypełnienia”
NIEWYPEŁNIONY; B — the owner writes `zespół: …`, a limit message arrives, or a new model/provider appears. Running a
CLI runner: URUCHAMIANIE_CLI.md. State goes into the registry, never into this file. "Host" = the tool the lead runs
in (Claude Code or Codex); "runner" = a row of the registry.

## A. Registry setup (once per machine; afterwards only updates)

1. Read first, write second. Look for a filled v10/v11 `ZESPOL.md` (no „Registry v12” line) in every installed skill
   directory — `~/.claude/skills/kierownik/`, `~/.agents/skills/kierownik/`, a project install
   `<repo>/.agents/skills/kierownik/` — and merge them in memory into the ZESPOL_WZOR.md layout: Claude aliases with
   „Wskazuje dziś na” and notes (haiku without effort, `best` vs `fable`); the Codex model mapping and its
   availability; limits and `wyłączony przez właściciela` states (onto the subscription or the model); the owner's
   command deviations (into „Mechanizm / polecenie”); „Historia zmian”. Don't carry over v11 role rows that differ from
   the host tables in the template (e.g. Architekt = NAJMOCNIEJSZY). Never write over an old file; leave it in place.
2. Write the merged registry to `~/.kierownik/ZESPOL.md` (Windows: `%USERPROFILE%\.kierownik\ZESPOL.md`). A host
   that may not write outside its workspace asks for approval once; refused → write it to `<repo>/.kierownik/ZESPOL.md`
   (inside the workspace, excluded from Git, but per project — not shared with the other host) and record that
   location in the TODO.md header („Ustalenia”), so the next session finds it.
3. Detect the CLIs (`codex --version`, `agy --version`, `claude --version`, and anything the owner names). Not
   installed → its runner stays `NIEZNANY` with the note „brak CLI”. For each installed one check `--help` of its
   non-interactive mode: order from a file or stdin, working directory, model and effort, result output, sandbox and
   permission flags — never assume flags from memory. A subscription `wyłączony przez właściciela` is skipped.
4. Smoke test every installed CLI (URUCHAMIANIE_CLI.md; for a CLI whose non-interactive mode needs a no-sandbox /
   skip-permissions flag, only after the owner's recorded consent — see there) and, on a Codex host, its own roles (`run_agent.py` with
   `--role kier-analityk`): in a temporary directory with a git repository, with exactly the command you will use
   later — „utwórz plik ok.txt z treścią OK i uruchom `git status`” (read-only roles: „podaj wynik `git status`”).
   Success = the expected file/answer, exit code and stderr checked; a "soft-denied"-type message on stderr (seen with
   `agy`) means shell commands were skipped despite exit 0. The test uses up limit — a tool reporting an exhausted
   limit gets that state and no test. Record the verified command and „Test dymny: OK <data>”.
5. Ask the owner one combined question (with proposed answers): models of each subscription and their class (your
   proposal from capability and cost), priorities, current limits, what `/model` shows. Record; set „Stan wypełnienia”.

## B. Changes

1. **Limit or capacity message** → if it names a model (e.g. "Fable limit", "Requires usage credits" for one alias),
   set that MODEL's state; otherwise set the SUBSCRIPTION's state (every runner of it is affected, on both hosts).
   `niedostępny do <czas>` with the reset time from the message, or now + 5 h „(szacunek)” when it gives none. When the
   time has passed the item may be tried once; a limit again → double the previous wait.
2. **Owner's messages**: `zespół: rezygnuję z X` / `nie używaj X` → `wyłączony przez właściciela`;
   `zespół: X wymaga credits` → the model `wymaga credits`; `zespół: oszczędzaj X` → raise X's Priorytet number (and
   `zespół: używaj X` → lower it); `zespół: mam X` → new subscription, models and runner rows, then A.3–A.5 for it.
3. **New version in an existing line** (an alias already follows it): fix only notes that name versions. Effort levels
   don't mean the same across generations: if the vendor changed the recommended effort for the line, fix the effort
   of the roles of that class (agent files / role TOML and the host table).
4. **New line, new alias, or a change in the strength order**: assign the model to a class (capability and cost
   relative to the others) and family, confirm with the owner, add/update the model row — that is the whole change,
   because every order names its model explicitly. Optional housekeeping, so fallbacks stay sensible: the `model:`
   defaults in `~/.claude/agents/kier-*.md` / role TOML, and for the lead's own class the `"model"` value in
   `.claude/settings.json` (SZABLONY.md, section 8). A Claude model without an alias can't be passed per call (the
   `model` parameter takes aliases only) — note it in „Uwagi”; it works only as a frontmatter default.
5. **A class missing everywhere** (e.g. NAJMOCNIEJSZY needs credits nobody pays) → nothing to edit in agents: SKILL.md
   section 7 steps down with the recorded label.
6. A permanent effort change of a role only after an observed problem or a measured gain, with the reason in
   „Historia zmian”. Every change → an entry in „Historia zmian”.
