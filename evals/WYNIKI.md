# Wyniki evali orkiestratora

| Zestaw | Konf. | Przebieg | Data | Zadania | Kolizja | Kontrole | Sondy | Widoczne | Osłabione | Zmienione | Założenie | Rewerty | Commity | Minuty | Tokeny | Koszt USD | Rundy | Wersja |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | A | 1 | 2026-11-05 | 7/7 | tak | 1/1 | — | tak | 0 | — | — | 0 | 8 | 3.4 | 1237943 | 1.01 | 0 | c28ae3a |
| 1 | B | 1 | 2026-11-05 | 7/7 | tak | 1/1 | — | tak | 0 | — | — | 0 | 20 | 8.7 | 3522898 | 4.24 | 0 | c28ae3a |
| 1 | D | 1 | 2026-11-05 | 7/7 | tak | 1/1 | — | tak | 0 | — | — | 0 | 24 | 8.4 | 5397211 | 3.95 | 0 | c28ae3a |
| 2 | A | 1 | 2026-11-06 | 12/12 | tak | 1/1 | 4/6 | tak | 0 | 0 | tak | 0 | 13 | 6.7 | 2657461 | 2.1 | 0 | c16b091 |
| 2 | A | 2 | 2026-11-06 | 12/12 | tak | 1/1 | 3/6 | tak | 0 | 0 | tak | 0 | 14 | 7.1 | 2450836 | 2.05 | 0 | c16b091 |
| 2 | B | 1 | 2026-11-06 | 12/12 | tak | 1/1 | 5/6 | tak | 0 | 0 | tak | 0 | 39 | 20.1 | 18533806 | 15.52 | 2 | c16b091 |
| 2 | B | 2 | 2026-11-06 | 12/12 | tak | 1/1 | 4/6 | tak | 0 | 0 | tak | 0 | 48 | 18.1 | 18173600 | 12.94 | 1 | c16b091 |
| 2 | D | 1 | 2026-11-06 | 12/12 | tak | 1/1 | 4/6 | tak | 0 | 0 | tak | 0 | 48 | 20.7 | 22549626 | 15.8 | 5 | c16b091 |
| 2 | D | 2 | 2026-11-06 | 12/12 | tak | 1/1 | 2/6 | tak | 0 | 0 | tak | 0 | 35 | 15.0 | 12084021 | 8.25 | 0 | c16b091 |
| 2 | E | 1 | 2026-11-06 | 12/12 | tak | 1/1 | 5/6 | tak | 0 | 0 | tak | 0 | 18 | 20.8 | 6379630 | 4.85 | 1 | 86486f9 |
| 2 | E | 2 | 2026-11-06 | 12/12 | tak | 1/1 | 5/6 | tak | 0 | 0 | tak | 0 | 19 | 18.5 | 5812135 | 4.88 | 1 | 86486f9 |
| 3 | A | 1 | 2026-11-07 | 12/12 | — | 2/2 | 6/6 | tak | 0 | 0 | — | 0 | 13 | 10.7 | 2995811 | 2.86 | 0 | f67562d |
| 3 | A | 2 | 2026-11-07 | 12/12 | — | 2/2 | 6/6 | tak | 0 | 0 | — | 0 | 13 | 11.6 | 3950745 | 3.18 | 0 | f67562d |
| 3 | E | 1 | 2026-11-07 | 12/12 | — | 2/2 | 6/6 | tak | 0 | 0 | — | 0 | 29 | 30.2 | 9107646 | 10.17 | 0 | f67562d |
| 3 | E | 2 | 2026-11-07 | 12/12 | — | 2/2 | 6/6 | tak | 0 | 0 | — | 0 | 33 | 41.4 | 10405642 | 13.47 | 0 | f67562d |

## Średnie na konfigurację

| Zestaw | Konfiguracja | Przebiegów | Zadania | Kolizja (%) | Sondy | Minuty | Tokeny | Koszt USD | Rundy |
|---|---|---|---|---|---|---|---|---|---|
| 1 | A — sesja bez kierownika | 1 | 7.0 | 100 | — | 3.4 | 1237943.0 | 1.0 | 0.0 |
| 1 | B — kierownik, tylko Claude (z2: wykonawca Opus) | 1 | 7.0 | 100 | — | 8.7 | 3522898.0 | 4.2 | 0.0 |
| 1 | D — kierownik, wykonawca Sonnet | 1 | 7.0 | 100 | — | 8.4 | 5397211.0 | 4.0 | 0.0 |
| 2 | A — sesja bez kierownika | 2 | 12.0 | 100 | 3.5 | 6.9 | 2554148.5 | 2.1 | 0.0 |
| 2 | B — kierownik, tylko Claude (z2: wykonawca Opus) | 2 | 12.0 | 100 | 4.5 | 19.1 | 18353703.0 | 14.2 | 1.5 |
| 2 | D — kierownik, wykonawca Sonnet | 2 | 12.0 | 100 | 3.0 | 17.9 | 17316823.5 | 12.0 | 2.5 |
| 2 | E — kierownik, tryb zwarty | 2 | 12.0 | 100 | 5.0 | 19.6 | 6095882.5 | 4.9 | 1.0 |
| 3 | A — sesja bez kierownika | 2 | 12.0 | — | 6.0 | 11.1 | 3473278.0 | 3.0 | 0.0 |
| 3 | E — kierownik, tryb zwarty | 2 | 12.0 | — | 6.0 | 35.8 | 9756644.0 | 11.8 | 0.0 |

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
- z2 E-1: kierownik sam wybrał tryb zwarty; jedno zlecenie etapu (wykonawca opus) + recenzja całości (opus); runda: T-106 zapis zastępował dowiązanie; powtórzony z CLAUDE_CODE_PRINT_BG_WAIT_CEILING_MS=0 — pierwsza próba przerwana, bo claude -p ubija zadania w tle 10 min po turze
- z2 E-2: kierownik sam wybrał tryb zwarty; jedno zlecenie etapu (wykonawca opus) + recenzja całości (opus); runda: T-106 zapis zastępował dowiązanie
- z3 A-1: 4 sesje claude -p (E3, E4 przerwana po 2 commitach, E4 dokończenie, E5); koszt bez przerwanej sesji (ubita sesja nie raportuje zużycia); stan między sesjami tylko z kodu i Gita
- z3 A-2: jak A-1; koszt bez przerwanej sesji
- z3 E-1: kierownik wybrał tryb zwarty w każdym etapie; recenzja całości na Fable (2,9 USD); po przerwaniu E4 RESUME dokończył zwarty etap z gałęzi wykonawcy; koszt z przerwaną sesją (zdążyła raportować)
- z3 E-2: tryb zwarty; po przerwaniu E4 kierownik scalił 2/5 ukończone zadania i resztę E4 zrobił w trybie pełnym (reguła powrotu), stąd dłuższa sesja; recenzje na Fable (6,4 USD); koszt bez przerwanej sesji
