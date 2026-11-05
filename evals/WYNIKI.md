# Wyniki evali orkiestratora

| Zestaw | Konf. | Przebieg | Data | Zadania | Kolizja | Widoczne | Osłabione | Rewerty | Commity | Minuty | Tokeny | Koszt USD | Rundy | Wersja |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | A | 1 | 2026-11-05 | 7/7 | tak | tak | 0 | 0 | 8 | 3.4 | 1237943 | 1.01 | 0 | c28ae3a |
| 1 | B | 1 | 2026-11-05 | 7/7 | tak | tak | 0 | 0 | 20 | 8.7 | 3522898 | 4.24 | 0 | c28ae3a |
| 1 | D | 1 | 2026-11-05 | 7/7 | tak | tak | 0 | 0 | 24 | 8.4 | 5397211 | 3.95 | 0 | c28ae3a |

## Średnie na konfigurację

| Zestaw | Konfiguracja | Przebiegów | Zadania | Kolizja (%) | Minuty | Tokeny | Koszt USD | Rundy |
|---|---|---|---|---|---|---|---|---|
| 1 | A — sesja bez kierownika | 1 | 7.0 | 100 | 3.4 | 1237943.0 | 1.0 | 0.0 |
| 1 | B — kierownik, tylko Claude | 1 | 7.0 | 100 | 8.7 | 3522898.0 | 4.2 | 0.0 |
| 1 | D — kierownik, wykonawca Sonnet | 1 | 7.0 | 100 | 8.4 | 5397211.0 | 4.0 | 0.0 |

## Uwagi z przebiegów

- z1 A-1: claude -p w kontenerze (Opus); bez kierownika; 7 commitów zadań, 34 nowe testy
- z1 B-1: claude -p w kontenerze; kierownik sam dał Sonnetowi 6/7 zadań (proste), Opus dla T-005, Fable: recenzja T-005 i weryfikacja etapu; T-006/T-007 sekwencyjnie (konflikt nie sprawdzony); 15 subagentów
- z1 D-1: claude -p w kontenerze; wykonawca Sonnet 7/7; T-006/T-007 sekwencyjnie; artefakt zestawu: znacznik .eval-start w katalogu projektu wymusił commit .gitignore
