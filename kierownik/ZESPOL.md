# ZESPÓŁ — modele, role, zapas i limity na tej maszynie

Wspólny dla wszystkich projektów na tej maszynie. Wypełnia i aktualizuje kierownik
(SKILL.md, sekcje 2 i 7). Właściciel może edytować ręcznie.

Stan wypełnienia: NIEWYPEŁNIONY   (kierownik zmienia na: WYPEŁNIONY <data>)


## Główny zespół — Claude Code (plan Max)

| Rola | Subagent (`~/.claude/agents/`) | Model domyślny (effort) | Kiedy wyżej |
|---|---|---|---|
| Kierownik | wątek główny `/kierownik` | Opus 5.5 (high) | — |
| Analityk | `kier-analityk` | Sonnet (low) | duże repo / trudne pytanie → Opus; trywialne → Haiku |
| Wykonawca | `kier-wykonawca` | Sonnet (high) | trudne / ryzykowne / po nieudanej rundzie → Opus (high/xhigh) |
| Recenzent | `kier-recenzent` | Opus (high) | autor na Opus → Fable; cel etapu → Fable |
| Architekt | `kier-architekt` | Fable 5.1 (xhigh) | — |

Fable 5.1: w limicie planu (bez „Requires usage credits”) — stan na <data>.
Jeśli `/model` zacznie pokazywać „Requires usage credits” przy Fable, kierownik zastępuje Fable
Opusem (effort max) i odnotowuje to tutaj.

Stan subagentów `kier-*`: zainstalowani [?]   (kierownik sprawdza na starcie sesji)


## Zapas i recenzja innej rodziny

Używane tylko: (a) gdy Claude jest niedostępny, (b) do recenzji innej rodziny w przypadkach
z SKILL.md, sekcja 7. Wybór: narzędzie ze stanem `dostępny`; jeśli oba dostępne — to z większym
zapasem limitu.

`<repo>` = bezwzględna ścieżka projektu; worktree zadania: `<repo>/.kierownik/wt/T-NNN`.

| Narzędzie | Rodzina | Polecenie nieinteraktywne | Zweryfikowane |
|---|---|---|---|
| Antigravity CLI (`agy`) | Google | `cd <repo>/.kierownik/wt/T-NNN && agy -p "<zlecenie>" --dangerously-skip-permissions > <repo>/.kierownik/T-NNN-<rola>.md 2> <repo>/.kierownik/T-NNN-<rola>.err`; model (Gemini Pro / Flash) flagą z `agy --help` | [?] |
| Codex CLI | OpenAI | `codex exec -C <repo>/.kierownik/wt/T-NNN -s workspace-write -o <repo>/.kierownik/T-NNN-<rola>.md "<zlecenie>"` (recenzja bez zapisu: `-s read-only`) | [?] |

Uwagi:
- `agy` bez `--dangerously-skip-permissions` w trybie `-p` po cichu pomija polecenia powłoki
  (kod 0, komunikat tylko na stderr) — zawsze czytaj `.err`.
- Tryb bez pytań = agent może wykonać dowolne polecenie: tylko w worktree zadania, bez sekretów
  w zleceniu, po przebiegu `git status` i `git log` worktree.


## Limity

| System | Plan | Stan |
|---|---|---|
| Claude | Max | dostępny |
| Google / Antigravity | <…> | <dostępny / niedostępny do …> |
| OpenAI / Codex | <…> | <dostępny / niedostępny do …> |

Stan: `dostępny` | `niedostępny do <data godzina>` (wpisuje kierownik po komunikacie o limicie
albo po informacji od właściciela).


## Historia zmian
- <data> — <co zmieniono i dlaczego>
