# Wyniki evali orkiestratora

| Zestaw | Konf. | Przebieg | Data | Zadania | Kolizja | Widoczne | Osłabione | Zmienione | Założenie | Rewerty | Commity | Minuty | Tokeny | Koszt USD | Rundy | Wersja |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | A | 1 | 2026-11-05 | 7/7 | tak | tak | 0 | — | — | 0 | 8 | 3.4 | 1237943 | 1.01 | 0 | c28ae3a |
| 1 | B | 1 | 2026-11-05 | 7/7 | tak | tak | 0 | — | — | 0 | 20 | 8.7 | 3522898 | 4.24 | 0 | c28ae3a |
| 1 | D | 1 | 2026-11-05 | 7/7 | tak | tak | 0 | — | — | 0 | 24 | 8.4 | 5397211 | 3.95 | 0 | c28ae3a |
| 2 | A | 1 | 2026-11-06 | 12/12 | tak | tak | 0 | 0 | tak | 0 | 13 | 6.7 | 2657461 | 2.1 | 0 | c16b091 |
| 2 | A | 2 | 2026-11-06 | 12/12 | tak | tak | 0 | 0 | tak | 0 | 14 | 7.1 | 2450836 | 2.05 | 0 | c16b091 |
| 2 | B | 1 | 2026-11-06 | 12/12 | tak | tak | 0 | 0 | tak | 0 | 39 | 20.1 | 18533806 | 15.52 | 2 | c16b091 |
| 2 | B | 2 | 2026-11-06 | 12/12 | tak | tak | 0 | 0 | tak | 0 | 48 | 18.1 | 18173600 | 12.94 | 1 | c16b091 |
| 2 | D | 1 | 2026-11-06 | 12/12 | tak | tak | 0 | 0 | tak | 0 | 48 | 20.7 | 22549626 | 15.8 | 5 | c16b091 |
| 2 | D | 2 | 2026-11-06 | 12/12 | tak | tak | 0 | 0 | tak | 0 | 35 | 15.0 | 12084021 | 8.25 | 0 | c16b091 |

## Średnie na konfigurację

| Zestaw | Konfiguracja | Przebiegów | Zadania | Kolizja (%) | Minuty | Tokeny | Koszt USD | Rundy |
|---|---|---|---|---|---|---|---|---|
| 1 | A — sesja bez kierownika | 1 | 7.0 | 100 | 3.4 | 1237943.0 | 1.0 | 0.0 |
| 1 | B — kierownik, tylko Claude (z2: wykonawca Opus) | 1 | 7.0 | 100 | 8.7 | 3522898.0 | 4.2 | 0.0 |
| 1 | D — kierownik, wykonawca Sonnet | 1 | 7.0 | 100 | 8.4 | 5397211.0 | 4.0 | 0.0 |
| 2 | A — sesja bez kierownika | 2 | 12.0 | 100 | 6.9 | 2554148.5 | 2.1 | 0.0 |
| 2 | B — kierownik, tylko Claude (z2: wykonawca Opus) | 2 | 12.0 | 100 | 19.1 | 18353703.0 | 14.2 | 1.5 |
| 2 | D — kierownik, wykonawca Sonnet | 2 | 12.0 | 100 | 17.9 | 17316823.5 | 12.0 | 2.5 |

## Uwagi z przebiegów

- z1 A-1: claude -p w kontenerze (Opus); bez kierownika; 7 commitów zadań, 34 nowe testy
- z1 B-1: claude -p w kontenerze; kierownik sam dał Sonnetowi 6/7 zadań (proste), Opus dla T-005, Fable: recenzja T-005 i weryfikacja etapu; T-006/T-007 sekwencyjnie (konflikt nie sprawdzony); 15 subagentów
- z1 D-1: claude -p w kontenerze; wykonawca Sonnet 7/7; T-006/T-007 sekwencyjnie; artefakt zestawu: znacznik .eval-start w katalogu projektu wymusił commit .gitignore
- z2 A-1: claude -p w kontenerze, jedna sesja bez subagentów; sprzeczność T-107 zgłoszona w commicie i raporcie (rok opcjonalny)
- z2 A-2: jak A-1; sprzeczność T-107 zgłoszona w raporcie
- z2 B-1: wykonawca zawsze opus, recenzja opus (fable z rejestru niedostępny); przerwany 5-godzinnym limitem konta przy weryfikacji etapu i dokończony przez --resume (czas i koszt łącznie); T-107 kryteria v2 przed startem; rundy: T-106 (uprawnienia 0600, zapis przez dowiązanie), T-107 (jawnie pusty --rok) + scalenie z konfliktem
- z2 B-2: wykonawca zawsze opus; T-107 kryteria v2 przed startem; runda: T-107 (jawnie pusty --rok); konflikty cli.py rozwiązane przy scalaniu
- z2 D-1: wykonawca sonnet, recenzja opus; przerwany limitem w rundzie T-106 i dokończony przez --resume (łącznie); T-106: 3 rundy + diagnoza architekta; T-101: isbn w eksporcie bez neutralizacji i zawężony test T-105 (wyłapane w recenzji); T-109: komunikat błędu
- z2 D-2: wykonawca sonnet, recenzja opus; 0 rund; konflikty cli.py rozwiązane przy scalaniu; kierownik dopisał test łączenia flag lista
