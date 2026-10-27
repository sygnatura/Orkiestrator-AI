# ZESPOL_PROCEDURY — runner registry procedures (shared by the Claude Code and Codex hosts)

Read by the lead only when the trigger occurs: A — no registry found (SKILL.md, section 1), „Stan wypełnienia”
NIEWYPEŁNIONY, or a registry without the line „Registry v12, schemat 2”; B — the owner writes `zespół: …`, a limit message arrives, or a new model/provider appears. Running a
CLI runner: URUCHAMIANIE_CLI.md. State goes into the registry, never into this file. "Host" = the tool the lead runs
in (Claude Code or Codex); "runner" = a row of the registry.

## A. Registry setup (once per machine; afterwards only updates)

LOCAL DECISIONS WIN: whatever the owner decided on this machine — a `wyłączony przez właściciela` state, a revoked or
never-given consent (e.g. to a no-sandbox mode), a priority — always overrides the template. A consent counts only
when the live registry records it with „(potwierdzona na tej maszynie)”; any other consent (copied from an older
template, e.g. „2026-10-18”, or without that note) counts as not given — ask once, before the next use of that mode,
and record the answer either way (TAK/NIE <data> „(potwierdzona na tej maszynie)” + „Historia zmian”).

0. A registry that says „Registry v12” without „schemat 2” (an early v12 draft) is updated in place before use: every
   `niedostępny od <czas>` becomes `niedostępny do <czas + 5 h> (szacunek)`; „Modele” gets the „Rodzina” column (the
   family of each model, not of its subscription); the subscription column „Rodzina” becomes „Dostawca”; template
   consents per LOCAL DECISIONS WIN; then set the header line to „Registry v12, schemat 2” and log it. If its
   „Stan wypełnienia” is WYPEŁNIONY, steps 1–5 are not needed; if NIEWYPEŁNIONY, continue with steps 3–5.

1. Read first, write second. Look for a filled v10/v11 `ZESPOL.md` (no „Registry v12” line) in every installed skill
   directory — `~/.claude/skills/kierownik/`, `~/.agents/skills/kierownik/`, a project install
   `<repo>/.agents/skills/kierownik/` — and merge them in memory into the ZESPOL_WZOR.md layout (consents per LOCAL DECISIONS WIN — an old
   `wyłączony przez właściciela` for agy means no no-sandbox consent here): Claude aliases with
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
4. Smoke test every installed CLI (URUCHAMIANIE_CLI.md) and, on a Codex host, its own roles (`run_agent.py` with
   `--role kier-analityk`): in a temporary directory with a git repository, with exactly the command you will use
   later — „utwórz plik ok.txt z treścią OK i uruchom `git status`” (read-only roles: „podaj wynik `git status`”).
   Success = the expected file/answer, exit code and stderr checked; a "soft-denied"-type message on stderr (seen with
   `agy`) means shell commands were skipped despite exit 0. The test uses up limit — a tool reporting an exhausted
   limit gets that state and no test. Record the verified command and „Test dymny: OK <data>”.
   A CLI whose non-interactive mode needs a no-sandbox / skip-permissions flag (today `agy`): before its first test or
   use, ask the owner one question — „<CLI> działa bez pytań tylko bez sandboxa: dostęp do całej maszyny, także do
   plików poza repozytorium. Zgadzasz się? Bezpieczniej: kontener albo VM.” — and record TAK/NIE <data>
   „(potwierdzona na tej maszynie)” in its runner row. NIE → no flag, no test; the runner stays `NIEZNANY` with the
   note „bez zgody na tryb bez sandboxa”. Bundle this question with step 5 when both are open.
5. Ask the owner one combined question (with proposed answers): models of each subscription and their class (your
   proposal from capability and cost), priorities, current limits, what `/model` shows. Record; set „Stan wypełnienia”.

## B. Changes

1. **Limit or capacity message** → if it names a model (e.g. "Fable limit", "Requires usage credits" for one alias),
   set that MODEL's state; otherwise set the SUBSCRIPTION's state (every runner of it is affected, on both hosts).
   `niedostępny do <czas>` with the reset time from the message, or now + 5 h „(szacunek)” when it gives none. When the
   time has passed the item may be tried once; a limit again → double the previous wait.
2. **Owner's messages**: `zespół: rezygnuję z X` / `nie używaj X` → `wyłączony przez właściciela`;
   `zespół: X wymaga credits` → the model `wymaga credits`; `zespół: oszczędzaj X` → raise X's Priorytet number (and
   `zespół: używaj X` → lower it); `zespół: mam X` → new subscription, models and runner rows, then A.3–A.5 for it;
   consent to a CLI's no-sandbox mode given or revoked (`zespół: agy bez trybu bez sandboxa`) → that runner row
   and „Historia zmian”.
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
