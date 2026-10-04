# ZESPÓŁ — narzędzia, polecenia i limity na tej maszynie

Wspólny dla wszystkich projektów na tej maszynie. Wypełnia i aktualizuje kierownik
(SKILL.md, sekcje 2 i 7). Właściciel może edytować ręcznie.

Stan wypełnienia: NIEWYPEŁNIONY   (kierownik zmienia na: WYPEŁNIONY <data>)


## Wykonawcy

| Narzędzie | Rodzina | Jak uruchamiane | Role |
|---|---|---|---|
| Claude Code — subagenci | Claude | narzędzie Agent w sesji kierownika (parametr `model`; implementacja z `isolation: worktree`) | analiza kodu (tańszy model), weryfikacja kodu Codexa, implementacja gdy Codex niedostępny |
| Codex CLI | OpenAI | `codex exec -C <katalog> -s workspace-write -o .kierownik/T-NNN-<rola>.md "<zlecenie>"` — zweryfikowane: [?] | implementacja, trudne błędy, weryfikacja kodu Claude |
| Antigravity | Google (Gemini) | brak wywołania z terminala → zlecenie przekazuje właściciel ręcznie | tylko gdy potrzebna przeglądarka/UI albo trzecia opinia przy sporze Claude ↔ Codex |

Uwagi:
- Polecenie Codexa sprawdź przy pierwszym uruchomieniu (`codex exec --help` + test dymny)
  i zapisz tu wersję, która zadziałała. Model i poziom rozumowania: <np. domyślne z ~/.codex/config.toml>.
- Recenzja bez zapisu plików: `-s read-only`; recenzja z uruchamianiem testów: `workspace-write`
  w worktree zadania.
- Antigravity nie blokuje pętli: zadanie dla niego kierownik odkłada do raportu etapu,
  chyba że jest jedyną drogą do celu.


## Limity

| System | Plan / subskrypcja | Rodzaj limitu | Stan |
|---|---|---|---|
| Claude (kierownik + subagenci — wspólny limit) | <…> | <np. okno 5 h + tygodniowy> | dostępny |
| OpenAI / Codex | <…> | <…> | dostępny |
| Antigravity | <…> | <…> | dostępny |

Stan: `dostępny` | `niedostępny do <data godzina>` (wpisuje kierownik po komunikacie o limicie).


## Podział pracy (domyślny)

- Analiza / odczyt: subagent Claude na tańszym modelu (Explore).
- Implementacja: Codex. Gdy Codex niedostępny: subagent Claude.
- Weryfikacja: druga rodzina względem autora — kod Codexa sprawdza Claude, kod Claude sprawdza Codex.
- Plan / trudna diagnoza: kierownik na najsilniejszym modelu + druga opinia Codexa.
- Spór Claude ↔ Codex albo zadanie z przeglądarką: Antigravity przez właściciela.

Ponieważ kierownik i subagenci Claude korzystają z tego samego limitu, ciężką implementację
kieruj do Codexa, a Claude zostaw na planowanie, analizę i weryfikację.


## Historia zmian
- <data> — <co zmieniono i dlaczego>
