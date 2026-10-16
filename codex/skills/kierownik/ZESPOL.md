# ZESPÓŁ v11 — Codex, classes and the state of this installation

Stan wypełnienia: NIEWYPEŁNIONY. The lead establishes the facts at start, without blocking work with the
available model. Keep this file on updates. Don't copy Claude installation aliases or limits here as Codex settings.

## Model classes

The only class → model mapping. Write identifiers after checking the models available in the client or after the
owner's information; don't assume automatic aliases to the newest generation.

| Klasa | Model dostępny w tym kliencie | Dostępność / data / ograniczenia |
|---|---|---|
| NAJMOCNIEJSZY | do ustalenia; na start dziedziczony | NIEZNANE |
| MOCNY | do ustalenia; na start dziedziczony | NIEZNANE |
| STANDARDOWY | model sesji, jeśli brak innego potwierdzonego | NIEZNANE |
| SZYBKI | do ustalenia; bez pozornego przypisania | NIEZNANE |

Default roles run without `model`, inheriting the Codex configuration. That is the start mode, not proof that four
different models are used. With a single available class the v10 exception applies: a fresh review and the lead's
independent tests, with the deviation recorded. Changing effort doesn't change the model.

## Roles and effort

| Rola | Definicja | Preferowana klasa | Początkowy effort |
|---|---|---|---|
| Kierownik | główna sesja `$kierownik` | MOCNY | ustawienie sesji |
| Analityk | roles/kier-analityk.toml | STANDARDOWY; rutyna SZYBKI | medium |
| Wykonawca | roles/kier-wykonawca.toml | STANDARDOWY; trudne MOCNY | medium |
| Recenzent | roles/kier-recenzent.toml | wyżej niż autor; ryzyko ŚREDNIE/WYSOKIE NAJMOCNIEJSZY | high |
| Architekt | roles/kier-architekt.toml | NAJMOCNIEJSZY | high |

Effort/model actually take effect in the role TOML fields or supported call fields. This table describes, it doesn't
configure. When updating a role's model, set `model` in its local TOML and record the change here. Native roles may
need a new session/reload; the CLI helper reads the TOML on every run. The helper's temporary `--model`/`--effort`
take precedence only for that order. Use levels the concrete model supports; fix a rejected effort according to its
capabilities, without guessing the model.

Natywne role `kier-*`: NIEZWERYFIKOWANE. Fresh context / directory support: NIEZWERYFIKOWANA. Without per-agent cwd
the executor runs through the CLI. Context safety net: don't copy Claude's token threshold; check the current client
and the model's capacity. In Codex checkpoints and a new thread are the basis.

## Routing, availability and backup

A new model doesn't change the process: assign it to a class by capability and cost, confirm a significant unknown
change with the owner and update the roles. Limit: record the message source and the reset time if given, pick an
available substitute. Don't invent times or subscription plans. The owner may disable a tool; then neither test nor
use its CLI.

| System | Stan | Test dymny / polecenie używane na tej maszynie |
|---|---|---|
| Codex native | do sprawdzenia w bieżącym kliencie | role/fresh context/cwd |
| Codex CLI | do sprawdzenia | `codex exec --help`, helper scripts/run_agent.py |
| Claude CLI (inna rodzina / zapas) | NIEZNANY | sprawdź `claude --help`, tryb nieinteraktywny i uprawnienia |
| Antigravity CLI lub inny zapas | NIEZNANY | aktualne `--help`; nie kopiuj flag obchodzących uprawnienia |

Stany: dostępny | niedostępny do <czas, jeśli znany> | wyłączony przez właściciela | NIEZNANY. Test a backup in a
temporary Git repo with the same command you will use later. The OK file, git status, exit and stderr are the
required evidence. The test concerns agent limits, not consent to the app's paid APIs.

## CLI execution

The lead prepares the role directory: a local executor in the task worktree, a reviewer in a detached worktree of the
reviewed SHA or in the author's unlocked directory. Cloud without a worktree request: the existing checkout, sessions
one after another. Start the reviewer only after preparing dependencies/test configuration. A worktree is Git
organisation, not access control over the whole machine.

POSIX example (substitute real, quoted paths):

```bash
python3 "$SKILL_DIR/scripts/run_agent.py" \
  --role kier-wykonawca --cwd "$TASK_DIR" \
  --prompt "$ORDER_FILE" --result "$RESULT_FILE"
```

PowerShell:

```powershell
py "$SkillDir/scripts/run_agent.py" --role kier-wykonawca --cwd $TaskDir `
  --prompt $OrderFile --result $ResultFile
```

These are ordinary path variables set in the session, not built-in Codex variables. The helper inserts the role
instructions, passes the order via stdin and logs stderr to `<wynik>.err`. It doesn't use a shell to interpret the
prompt. It keeps the CLI exit code; a review that changed HEAD/sources/status is rejected. It never overwrites
existing results. Keep full orders and logs in the ignored `.kierownik/`, evidence and versions in TODO/task files. A
CLI result doesn't replace the lead's check or the evidence for the integrated version.

## Historia zmian
Entries in Polish (the owner reads and edits this file).
- <data> — <zmiana, źródło informacji, powód, rzeczywisty model/effort>
