# Wznowienie kierownika v10 — Claude ↔ Codex

## Źródła wspólne

PROJEKT (jak działa), TODO (cel/plan/stan/dowody/następny krok), DONE,
AGENTS, istniejący CLAUDE, karty `docs/tasks/T-NNN.md`, ADR i rzeczywisty Git.
Zachowaj ID/statusy oraz zatwierdzenia. Nie twórz osobnych PROJEKT/TODO dla
Codex, PLAN.md, PROJECT_WORKFLOW.md ani REPORT/REVIEW jako warunku wznowienia.
Istniejące odpowiedniki/SDD zachowaj z mapowaniem, bez mechanicznej migracji.

Model/limity zespołu to stan danej instalacji skilla, nie stan projektu.
Nie nadpisuj `~/.claude/skills/kierownik/ZESPOL.md`, agentów Claude ani jego
settings podczas przejęcia. Możesz odczytać potrzebne, jawne metadane,
ale mapowanie Codex prowadź we własnym ZESPOL. Nie importuj sesji/sekretów.

## Odtworzenie pracy

Odczytaj status/HEAD/gałęzie/worktree/diff i aktualny TODO. Dla wskazanych
SHA sprawdź istnienie (`git cat-file -t`) i integrację (`merge-base --is-ancestor`).
Brak relacji po squash/cherry-pick nie dowodzi braku integracji: sprawdź
zapisany commit docelowy/dowód. Nie przełączaj cudzego checkoutu ani nie resetuj.

| Zapisany stan | Działanie Codex |
|---|---|
| TODO z zaakceptowanego etapu | Uruchom wykonawcę, nie pytaj ponownie o plan |
| W TOKU, żywa sesja Claude lub los nieznany | Ustal los istniejącego zlecenia; bez duplikatu |
| W TOKU, niepełny commit lub niezapisane zmiany | Zachowaj pracę, kontynuuj ten task/katalog po ustaleniu autorstwa |
| W TOKU, zmiana ukończona | Odbiór formalny, własne testy i recenzja tej wersji |
| DO SPRAWDZENIA, brak werdyktu | Odbierz trwającą lub uruchom tylko brakującą recenzję |
| DO SPRAWDZENIA, właściwy ZALICZONE dla SHA | Integracja i testy tej wersji; bez ponownej implementacji |
| DO POPRAWY jako werdykt | W TOKU, uwagi BLOKUJĄCE na tej samej gałęzi |
| ZABLOKOWANE | Usuń konkretną przeszkodę lub zbierz brakującą decyzję |
| Merge i pozytywne testy, TODO nieaktualny | Uzupełnij punkt kontrolny na podstawie dowodów |
| GOTOWE z dowodem | Zachowaj wynik, następny task |
| GOTOWE bez dostępnego dowodu | Zapisz lukę i sprawdź obszar, nie cofaj całego etapu |
| Sam merge bez dowodu zintegrowanej wersji | Sprawdzenie tej wersji, bez ogłoszenia GOTOWE |

Używaj istniejących `.claude/worktrees/` tylko po zakończeniu poprzedniego
wykonawcy i sprawdzeniu dostępu. Codex nie musi usuwać ich i tworzyć nowych.
Gałąź `task/*` może być wyewidencjonowana tylko w jednym worktree. Odłączony
checkout recenzenta rozwiązuje kolizję bez przełączania katalogu autora.
Worktree na innej maszynie nie zostaje przeniesione przez Git push. Brak
SHA/pliku w cloud oznacza niedostępny artefakt tutaj, nie zgodę na rozpoczęcie
zadania od nowa. Odzyskaj dostępne commity, poproś tylko o brakującą pracę.

## Punkt kontrolny i handoff

Aktualizuj istniejący nagłówek TODO, nie osobny plik. Zapisz:

```text
Cel / etap / zatwierdzony plan: <ścieżki i źródło decyzji>
Gałąź główna @ pełny SHA / ostatni zweryfikowany: <wersja + dowód>
W toku: <ID, status v10, gałąź, baza, ostatni commit, katalog/maszyna>
Lokalne zmiany: <autor/obszary/staging, bez sekretów>
Wykonawca: <narzędzie, faktyczny model/klasa, ID/los sesji, zlecenie/runda>
Recenzja: <oceniony SHA, świeży kontekst, werdykt, dowody, odstępstwa>
Integracja: <wersja, testy/scenariusz; czy stan/push wykonany>
Blokady / pytania / środowisko: <warunek i brakujące dane>
Ustalenia: <proces, mapowanie, zgody z odnośnikami, bez wartości sekretów>
Następny krok: <jedno konkretne działanie, task, rola, oczekiwany dowód>
```

Ważne wyniki przenieś do TODO/karty, bo `.kierownik/` jest lokalne/ignorowane.
Nie zapisuj w commicie SHA jego samego: identyfikator checkpointu podaj po
commicie. Dopiero potwierdzony push czyni commity dostępnymi z innej maszyny.

Prompt startowy: `$kierownik Wznów z PROJEKT.md i TODO.md; zachowaj aktywne
zlecenia i kontynuuj zapisany następny krok.` Po powrocie do Claude wystarcza
jego `/kierownik` z tymi samymi plikami. Zapisane fakty nie zastępują bieżących
uprawnień ani niedostępnej akceptacji pozostawionej wyłącznie w czacie.
