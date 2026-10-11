# Przejęcie projektu i handoff Claude ↔ Codex

## 1. Fakty przed działaniem

Pełne przejęcie: pierwszy kontakt, brak aktualnej migawki albo sprzeczność.
Szybkie wznowienie: aktualny handoff, potwierdzony checkout i aktywne artefakty.
Odczytaj tyle, ile potrzeba do ustalenia następnego działania; nie analizuj
całego kodu ani archiwum przy każdej sesji.

Ustal system/powłokę i repozytorium. Polecenia odczytu Git, wspólne dla Bash
i PowerShell (najpierw przejdź do rzeczywistego katalogu projektu):

```text
git rev-parse --show-toplevel
git status --short --branch
git rev-parse HEAD
git log -20 --oneline
git branch --list
git worktree list --porcelain
git diff --stat
git diff --cached --stat
```

Lista lokalnych gałęzi nie dowodzi ich integracji. Dla wskazanych wersji
sprawdź istnienie obiektów i relację przodka do rzeczywistej gałęzi docelowej:
`git cat-file -t <SHA>` oraz `git merge-base --is-ancestor <SHA> <cel>`.
Kod wyjścia 0 oznacza przodka; 1 brak tej relacji; inny błąd wymaga diagnozy.
Po squash/cherry-pick brak relacji przodka nie dowodzi braku integracji:
odszukaj zapisany commit integracyjny i dowód recenzenta. Kierownik nie
rozstrzyga sam równoważności logiki dwóch zmian.

Nie pobieraj/resetuj/checkoutuj gałęzi i nie przenoś cudzych zmian tylko
w celu ujednolicenia środowiska. Sprawdź aktywnych agentów, jeśli klient daje
takie narzędzie; brak lokalnej sesji nie wyklucza pracy Claude na innej maszynie.
Niewiadomy los aktywnego zlecenia wymaga konkretnego pytania do właściciela.

Czytaj kolejno: obowiązujące reguły → jedyny rejestr i handoff → wizję/plan
→ workflow i istotne ADR → aktywne taski/kryteria → raporty/recenzje.
README, manifesty i CI pomagają ustalić komendy; nie uruchamiaj ich jako
kierownik. Przy sprzeczności poszerz odczyt tylko o odpowiedni obszar.

## 2. Mapowanie zamiast migracji

| Obszar | SDD | Starszy v6 / równoważny projekt |
|---|---|---|
| Kolejka | `docs/TODO.md` | rzeczywisty TODO/WORKBOARD/ROADMAP |
| Plan | zatwierdzony `docs/PLAN.md` | zatwierdzone etapy w kolejce lub planie |
| Zadanie | `docs/tasks/T-NNN/TASK.md` | `docs/tasks/T-NNN.md` albo istniejąca karta |
| Kryteria | `VERIFY.md` | sekcja karty lub utrwalone zatwierdzone zlecenie |
| Wynik | `REPORT.md`, `REVIEW.md` | istniejące raporty; wskaż brak trwałego zapisu |
| Przed zleceniem | DRAFT / READY | TODO; gotowość wynika z dowodów zatwierdzenia |
| Recenzja | DO_SPRAWDZENIA | DO SPRAWDZENIA |
| Po pozytywnej recenzji | ACCEPTED | zachowaj status, dopisz oczekiwanie na integrację |
| Werdykt | ACCEPT / REWORK / BLOCKED | ZALICZONE / DO POPRAWY / ZABLOKOWANE |

Nie mapuj TODO automatycznie na READY. Nie zamieniaj GOTOWE na ACCEPTED tylko
dlatego, że przechodzisz do Codex. Nie zmieniaj ID, nie rozbijaj kart i nie
twórz osobnych rejestrów dla każdego narzędzia. Oznacz potwierdzone fakty,
deklaracje historyczne i brakujące dowody osobno. Mapowanie oraz odstępstwa
zapisz w nagłówku dotychczasowego rejestru w ramach uprawnień kierownika.
Gdy brak zatwierdzonego procesu, użyj wzorca WORKFLOW jako propozycji do decyzji.

Jeżeli ustalenia pozostały tylko w rozmowie Claude, poproś o konkretną decyzję,
kryteria lub raport. Nie potrzebujesz całego transkryptu ani dostępu do
prywatnych plików sesji Claude. Nie uznawaj streszczenia za zgodę na nowy zakres.

## 3. Punkt kontynuacji

| Znaleziony stan | Następne działanie |
|---|---|
| Brak zatwierdzonego celu/planu | Zlecenie ARCHITEKTOWI; istniejący kod pozostaje |
| Plan zatwierdzony, brak wymaganej specyfikacji | ARCHITEKT uzupełnia bieżący task; bez implementacji |
| ZLECONE, brak wyniku | Ustal los istniejącego wykonawcy; nie uruchamiaj duplikatu |
| ZLECONE, zmiana i raport już istnieją | Odbiór formalny i niezależna recenzja tej zmiany |
| DO_SPRAWDZENIA / DO SPRAWDZENIA | Ustal los recenzji, odbierz ją albo zleć tylko brakującą |
| Recenzja autora / ten sam model / model nieznany | Brak wymaganej niezależności; właściwy recenzent |
| DO_POPRAWY lub uwagi DO POPRAWY | Poprawa przez wykonawcę w istniejącym zakresie |
| ACCEPTED / ZALICZONE, brak integracji | Przygotuj integrację zgodną z procesem repo |
| Integracja istnieje, brak sprawdzenia tej wersji | Zleć weryfikację zintegrowanej wersji |
| GOTOWE, dowody zgodne z wersją | Zachowaj stan; następny zatwierdzony task |
| GOTOWE, brak dostępnego dowodu | Odnotuj lukę; ograniczony audyt, bez automatycznego cofania etapu |
| ZABLOKOWANE | Odtwórz przyczynę i konkretny warunek odblokowania |
| Lokalne zmiany bez jasnego autora | Zachowaj je; ustal autorstwo przed zapisem/integracją |

Potwierdź dostępność SHA, plików i gałęzi w aktualnym checkoutcie. Brak
obiektu lokalnego oznacza brak dostępu tutaj, a nie nieistnienie na maszynie
Claude. W cloud poproś o przeniesienie brakujących artefaktów odpowiednim
procesem; nie obiecuj odtworzenia niezapisanych plików z pamięci modelu.

## 4. Migawka w istniejącym rejestrze

Uzupełnij istniejący nagłówek lub sekcję handoff. Poniżej wzorzec pól,
**nie nowy plik ani nowa kolejka**. Zachowaj nieznane wartości jako NIEZNANE.

```text
Stan na: <rzeczywista data i strefa właściciela>
Projekt / katalog / powłoka: <rzeczywiste dane; ścieżka może różnić się między maszynami>
Workflow / mapowanie / zatwierdzenie: <ścieżki, wersja, odnośnik do decyzji>
Cel / bieżący etap: <VISION i PLAN albo rzeczywiste odpowiedniki>
Git: <gałąź docelowa, HEAD, baza zadania, gałąź/checkout zadania>
Zmiany niezacommitowane: <autor, obszary, stan stagingu lub NIEZNANE>
Ostatni potwierdzony działający punkt: <wersja + scenariusz + dowód>
Aktywne zadanie: <ID, niezmieniony status, zależności>
Specyfikacja i kryteria: <ścieżki, zatwierdzona wersja>
Wykonawca: <narzędzie/model, ID sesji jeśli znane, los zlecenia>
Zmiana: <commit lub baza + diff, dokładna oceniana wersja>
Raport: <ścieżka/źródło, czego nie zweryfikowano>
Recenzent: <narzędzie/model, niezależność od autora, los zlecenia>
Recenzja: <ścieżka, werdykt, wersja, brakujące dowody>
Integracja: <brak lub wersja docelowa + dowód sprawdzenia>
Zgody i ograniczenia: <zakres, odnośniki do decyzji; bez sekretów>
Zespół / dostępność: <odstępstwa, niedostępne modele, aktywne sesje>
Blokady / niewiadome: <konkretna przyczyna i warunek rozwiązania>
Następne działanie: <jedna czynność, rola, oczekiwany dowód>
```

Handoff przenosi artefakty, nie autoryzację przez samo skopiowanie tekstu:
nowa sesja weryfikuje zapisane decyzje i respektuje uprawnienia klienta.
Identyfikatory sesji są pomocnicze; nie zastępują raportów i wersji Git.
Nie zapisuj wartości sekretów ani pełnych prywatnych transkryptów.

Prompt do nowej sesji (właściciel podstawia rzeczywisty rejestr):

```text
Wejdź w rolę kierownika projektu (w Codex: $kierownik; w Claude: prompt
orkiestratora używany w tym projekcie). Przeczytaj reguły repo oraz aktualny
handoff w <rejestr>. Odtwórz stan z plików i Git. Zachowaj ID, statusy,
zatwierdzony proces i aktywne zlecenia. Kontynuuj od zapisanego następnego
działania; nie uruchamiaj ponownie zadania już przekazanego wykonawcy.
```

## 5. Scenariusze akceptacyjne na kopii projektu

1. v6 z TODO i płaską kartą → zachowanie formatu; READY nie jest dopisywane.
2. SDD z READY i kompletnym APPROVED TASK/VERIFY → zlecenie tego taska.
3. ZLECONE bez raportu i bez znanego losu agenta → pytanie o wykonawcę,
   bez duplikatu zlecenia.
4. Istniejący REPORT i diff, brak REVIEW → tylko niezależna recenzja.
5. REVIEW pozytywny od modelu autora → brak ACCEPTED/GOTOWE.
6. REVIEW właściwego recenzenta, brak integracji → integracja jako następny krok.
7. Integracja bez sprawdzenia zintegrowanej wersji → weryfikacja, bez GOTOWE.
8. Handoff po Claude z aktualnymi artefaktami → ten sam aktywny task i następny krok.
9. Handoff po Codex → kierownik Claude może odtworzyć go z tej samej kolejki.
10. Natywni agenci niedostępni → jeden prompt do właściciela, bez fałszywego ID.

Są to oczekiwane zachowania do sprawdzenia z modelem i projektem;
sam opis scenariuszy nie oznacza ich wykonania.
