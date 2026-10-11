# Zlecenia dla osobnych sesji

Wypełniaj rzeczywistymi danymi. Braki oznacz i ustal przed wykonaniem
zależnej czynności. Ścieżki odnoszą się do projektu, nie do pakietu skills.
Nie przekazuj całej historii rozmowy, sekretów ani argumentów wdrażających
niezatwierdzony zakres. Każda sesja najpierw czyta reguły swojego katalogu.

## Wykonawca — jeden task

```text
ROLA: WYKONAWCA
NARZĘDZIE / MODEL: <dostępne, rzeczywiste; odnotuj model użyty w wyniku>
PROJEKT / KATALOG / POWŁOKA: <...>
BAZA / GAŁĄŹ / CHECKOUT: <SHA i proces istniejącego repo>
ZADANIE: <ID i cel>
PRZECZYTAJ: <AGENTS i reguły katalogu>, <workflow>, <TASK/karta>, <VERIFY/kryteria>
ZAKRES I WYŁĄCZENIA: <dokładnie zatwierdzony zakres>
KRYTERIA: oryginalna zatwierdzona wersja <ścieżka/wersja>; bez zmian
ŚRODOWISKO / DANE: <izolacja; konkretne dopuszczone operacje>
GIT / PRAWA ZAPISU: <obszary, kto commituje; bez merge/push poza autoryzacją>
ZRÓB: najprostsze rozwiązanie spełniające task, odpowiednie testy i scenariusz
      użytkownika. Sam popraw własne lokalne błędy w zakresie tego taska.
NIE: zmiana kryteriów, wyłączanie asercji, funkcje na przyszłość, cudze zmiany,
     rozpoczęcie kolejnego taska, samozatwierdzenie wyniku.
WYNIK: <istniejąca ścieżka REPORT lub sposób raportowania v6>; baza, zmienione
       pliki, dokładne komendy/katalogi, exit status, passed/failed/skipped/unrun,
       środowisko, scenariusz i obserwacje, ograniczenia, źródła dowodów.
       Commit tylko według procesu projektu; jego SHA odczytaj po wykonaniu,
       nie wpisuj SHA przyszłego własnego commita do tego samego commita.
```

## Weryfikator — wymagane inna sesja i model

```text
ROLA: WERYFIKATOR
NARZĘDZIE / MODEL: <inny niż autor; preferowana inna rodzina>
AUTOR / MODEL AUTORA: <potwierdzone dane; przy braku wskaż niewiadomą>
PROJEKT / KATALOG / POWŁOKA: <...>
BAZA / OCENIANA WERSJA / DIFF: <konkretna zmiana, także lokalna jeśli bez commitów>
TRYB: recenzja taska | sprawdzenie po integracji | sprawdzenie celu etapu
PRZECZYTAJ: <reguły repo>, <workflow>, <oryginalny TASK/kryteria>, <REPORT>
ŚRODOWISKO / DANE / DOZWOLONE OPERACJE: <izolacja i autoryzacja>
ZRÓB: potwierdź wersję, sprawdź każde oryginalne kryterium i reprezentatywny
      scenariusz, przejrzyj diff, uruchom adekwatną regresję. Dla sprawdzenia
      po integracji użyj rzeczywistej wersji docelowej; dla etapu jego celu.
NIE: naprawianie kodu, zmiana kryteriów, uznawanie exit 0 z zerem testów za PASS.
WYNIK: <istniejąca ścieżka REVIEW lub format v6>; ACCEPT/REWORK/BLOCKED
       lub ZALICZONE/DO POPRAWY/ZABLOKOWANE według workflow. Dla każdego
       kryterium wersja, komenda, wynik i obserwacja, ograniczenia i lokalizacja
       problemów. Oddziel niewykonane sprawdzenia od pozytywnych.
PRAWA ZAPISU: tylko recenzja, gdy dozwolona; bez edycji kodu, danych i kryteriów.
GIT: <czy można commitować wyłącznie REVIEW; inaczej wynik utrwala upoważniona rola>
```

Pozycja „model” w szablonie nie wymusza modelu w narzędziu. Kierownik
sprawdza, czy rzeczywiście został użyty inny model. Przy nieznanym modelu
recenzja nie spełnia jeszcze wymogu niezależności. Samo `codex review` może
pomóc w analizie diffu; nie dowodzi wykonania scenariusza i integracji.

## Architekt / analityk

```text
ROLA: ARCHITEKT / ANALITYK; w osobnej sesji Codex można użyć $architekt
NARZĘDZIE / MODEL: <dostępne>
TRYB: NOWY_PROJEKT | PRZEJECIE | NOWY_ETAP | DIAGNOZA | ZMIANA_PLANU | RECENZJA_PLANU
PROJEKT / KATALOG / POWŁOKA / GAŁĄŹ / SHA: <...>
PRZECZYTAJ: <reguły>, <workflow>, <VISION/PLAN/kolejka>, <istotne ADR>,
            <konkretne taski, raporty, recenzje i logi>
PYTANIE: <ograniczony problem i oczekiwany rezultat>
ZATWIERDZONY ZAKRES / OGRANICZENIA: <decyzje właściciela>
ZRÓB: plan/specyfikacje albo diagnoza z dowodami; wykorzystaj istniejące
      formaty projektu. Szczegóły najbliższego etapu, dalsze niepewne jako DRAFT.
NIE: kod aplikacji, samozatwierdzanie planu, aktywowanie kolejki, cicha zmiana VERIFY.
PRAWA ZAPISU / GIT: <uzgodnione dokumenty; propozycje oznaczone PROPOSED/DRAFT>
WYNIK: rzeczywiste ścieżki, propozycje, wymagane decyzje, READY/DRAFT wg dowodów,
       zmiana/commit jeśli wykonane, jedno przekazanie dla kierownika.
```

Audyt działania zlecaj programiście/weryfikatorowi w osobnej sesji:
konkretny obszar → działa/nie działa/nie da się sprawdzić z dowodem.
Architekt dostaje wynik audytu, nie zastępuje go nowym założeniem.
Recenzja planu wymaga recenzenta niezależnego od jego autora; stosuj ją
przy dużym/ryzykownym planie lub zmianie architektury, nie automatycznie.

## Przekazanie do natywnego agenta

Tylko przy autoryzacji delegacji i dostępności narzędzia:

1. Sprawdź izolację i brak równoległego zapisu w checkoutcie.
2. Przekaż właściwy szablon i minimalny kontekst. Dla recenzenta zapewnij
   osobną sesję/model; nie dziedzicz całej rozmowy autora.
3. Odnotuj rzeczywisty identyfikator agenta/zlecenia i model jeśli dostępny.
4. Odbierz zakończony wynik i sprawdź artefakty; zakończenie agenta nie jest ACCEPT.
5. Dopiero potem zaktualizuj kolejkę, zgodnie z jej regułami przekazania.

Jeśli nie można spełnić któregoś warunku, użyj ręcznego zlecenia. Nie
zmieniaj konfiguracji klienta i nie instaluj dodatkowego narzędzia w ukryciu.
