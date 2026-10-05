# ZESPÓŁ — narzędzia, polecenia i limity na tej maszynie

Wspólny dla wszystkich projektów na tej maszynie. Wypełnia i aktualizuje kierownik
(SKILL.md, sekcje 2 i 7). Właściciel może edytować ręcznie.

Stan wypełnienia: NIEWYPEŁNIONY   (kierownik zmienia na: WYPEŁNIONY <data>)


## Wykonawcy

`<repo>` = bezwzględna ścieżka głównego katalogu projektu; `<worktree>` = katalog worktree zadania.
Wyniki zawsze do `<repo>/.kierownik/` (ścieżka bezwzględna — działa niezależnie od katalogu,
w którym uruchomiono agenta).

| Narzędzie | Rodzina | Polecenie nieinteraktywne | Role |
|---|---|---|---|
| Claude Code — subagenci | Claude | narzędzie Agent w sesji kierownika (parametr `model`; implementacja z `isolation: worktree`) | analiza kodu (tańszy model), weryfikacja, implementacja gdy inni niedostępni |
| Codex CLI | OpenAI | `codex exec -C <worktree> -s workspace-write -o <repo>/.kierownik/T-NNN-<rola>.md "<zlecenie>"` — zweryfikowane: [?] | implementacja (domyślnie), trudne błędy, weryfikacja |
| Antigravity CLI (`agy`) | Google | `cd <worktree> && agy -p "<zlecenie>" --dangerously-skip-permissions > <repo>/.kierownik/T-NNN-<rola>.md 2> <repo>/.kierownik/T-NNN-<rola>.err` — zweryfikowane: [?]; model (Gemini Pro / Flash): flaga z `agy --help` [?] | implementacja, zadania z UI/przeglądarką, weryfikacja, trzecia opinia |

Uwagi:
- Polecenia sprawdź przy pierwszym uruchomieniu (`--help` + test dymny) i zapisz tu wersję,
  która zadziałała. Modele i poziomy rozumowania: <np. Codex: domyślne z ~/.codex/config.toml;
  agy: Pro do implementacji, Flash do szybkich zadań>.
- Codex — recenzja bez zapisu plików: `-s read-only`; z uruchamianiem testów: `workspace-write`
  w worktree zadania.
- `agy` bez `--dangerously-skip-permissions` w trybie `-p` może zapisywać pliki, ale polecenia
  powłoki są „soft-denied”: przebieg kończy się kodem 0, a jedyny ślad to komunikat na stderr.
  Dlatego zawsze czytaj plik `.err` i nie traktuj kodu 0 jako sukcesu.
- `--dangerously-skip-permissions` = agent może wykonać dowolne polecenie bez pytania. Używaj go
  wyłącznie w worktree zadania (nigdy w głównym katalogu ani na main), bez sekretów w zleceniu,
  z zakazami z szablonu A. Po przebiegu sprawdź `git status` i `git log` worktree.


## Limity

| System | Plan / subskrypcja | Rodzaj limitu | Stan |
|---|---|---|---|
| Claude (kierownik + subagenci — wspólny limit) | <…> | <np. okno 5 h + tygodniowy> | dostępny |
| OpenAI / Codex | <…> | <…> | dostępny |
| Google / Antigravity | <…> | <…> | dostępny |

Stan: `dostępny` | `niedostępny do <data godzina>` (wpisuje kierownik po komunikacie o limicie).


## Podział pracy (domyślny)

- Analiza / odczyt: subagent Claude na tańszym modelu (Explore).
- Implementacja: Codex → Antigravity → subagent Claude (kolejny, gdy poprzedni niedostępny
  albo gdy zadanie lepiej pasuje — np. UI/przeglądarka → Antigravity).
- Weryfikacja: zawsze inna rodzina niż autor. Domyślnie:
  kod Codexa → Antigravity; kod Antigravity → Codex; kod Claude (także kierownika) → Codex.
  Weryfikacja celu etapu i zmiany ryzykowne → dodatkowo subagent Claude na najsilniejszym modelu.
- Spór dwóch rodzin (sprzeczne werdykty) → trzecia rodzina rozstrzyga, bez udziału właściciela.
- Plan / trudna diagnoza: kierownik na najsilniejszym modelu + druga opinia innej rodziny.

Ponieważ kierownik i subagenci Claude korzystają z tego samego limitu, implementację i rutynową
weryfikację kieruj do Codexa i Antigravity, a Claude zostaw na planowanie, analizę i decyzje.


## Historia zmian
- <data> — <co zmieniono i dlaczego>
