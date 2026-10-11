# ZLECENIA v10 — Codex

Zlecenie jest samowystarczalne: PO CO, rzeczywiste ścieżki i pełne SHA,
zakres, oryginalne kryteria, środowisko i prawa. Native otrzymuje właściwą
rolę i minimalny kontekst; CLI helper wstawia tę samą definicję roli.
Reguły AGENTS i katalogu agent czyta jawnie. Nigdy pełna rozmowa autora,
sekrety ani prompt wklejony jako wykonywalny tekst powłoki.

## A. Wykonawca

```text
ZADANIE: T-NNN — <jeden cel>
PO CO: <cel etapu i zachowanie dla użytkownika>
KATALOG / POWŁOKA: <rzeczywisty katalog roli>
GAŁĄŹ / BAZA / AKTUALNA WERSJA: <przygotowana gałąź, pełne SHA>
  Gałąź już wyewidencjonowana; nie twórz innej ani worktree.
  Poprawki: ta sama gałąź i ostatni commit poprzedniej rundy.
PRZECZYTAJ: reguły AGENTS/katalogu, PROJEKT (sekcje ...), karta jeśli istnieje,
           konkretne pliki. Wskaż rzeczywiste odpowiedniki dokumentów.
ŚRODOWISKO: <instalacja repo, testowa konfiguracja, usługi, izolacja danych>
ZAKRES: <obszary IN/OUT; wyłącznie zatwierdzone zadanie>
KRYTERIA: <oryginalne K1..Kn, komendy, scenariusz użytkownika, wersja kryteriów>
NIE: merge/push/reset, TODO/PROJEKT/kryteria, osłabianie testów, produkcja,
     płatne API aplikacji/testów bez zgody wskazanej tutaj.
WYNIK: commit według procesu repo, raport do 15 linii: gałąź, katalog,
       baza→zmiana, pliki, komendy→exit/passed/failed/skipped, scenariusz,
       NIE SPRAWDZONO, POZA ZAKRESEM. W karcie tylko Postęp/Odkrycia/Wynik.
```

## B. Recenzent — świeży kontekst

```text
RECENZJA: T-NNN albo CEL ETAPU E<n>
KATALOG / POWŁOKA: <przygotowany katalog zmiany, odblokowany po autorze>
BAZA / OCENIANY SHA: <pełne wersje; dla etapu zakres od poprzedniego etapu>
DIFF: git diff <baza>...<oceniany SHA>
AUTOR / KLASA / MODEL: <fakty, bez wniosków autora>
PRZECZYTAJ: reguły i Weryfikacja cudzej zmiany; karta tylko Cel/Kontekst/Zakres/Kryteria.
KRYTERIA: <te same K1..Kn; etap: cel i scenariusz E2E>
JAK URUCHOMIĆ / DANE: <testowe komendy i izolacja, konkretne dozwolone operacje>
ZRÓB: K w działaniu z własnym dowodem, scenariusz i diff zakres/testy/błędy/nadmiar.
NIE: poprawianie kodu, commit, przełączanie gałęzi, instalowanie braków,
     zmiana kryteriów, czytanie Postęp/Odkrycia/Wynik autora jako podpowiedzi.
WYNIK do 20 linii: ZALICZONE | DO POPRAWY | ZABLOKOWANE — ID @ SHA;
  K1..Kn: OK / NIE / NIE SPRAWDZONO (powód), dowód komenda→wynik/obserwacja;
  BLOKUJĄCE z lokalizacją; OPCJONALNE. Źródła/indeks/HEAD bez zmian.
```

Model/klasa wyżej niż autor jeśli dostępne; przy wyjątku v10 świeży kontekst
plus własne testy kierownika i jawny zapis odstępstwa. Reviewer nie potrzebuje
REPORT autora; dowody powstają z jego własnych sprawdzeń.

## C. Analityk / architekt / recenzja planu

```text
PYTANIE: <jedno: mapa | plan | recenzja planu | diagnoza | spike>
PO CO: <decyzja lub następny krok kierownika>
KATALOG / GAŁĄŹ @ SHA: <fakty>
PRZECZYTAJ: reguły, PROJEKT, TODO oraz konkretne pliki/obserwacje.
DIAGNOZA: co/gdzie/komunikat/odtworzenie → przyczyna z dowodem; fakt ≠ hipoteza;
         wykonanie czy założenie; małe kroki z kryteriami.
PLAN: najprostszy wariant i porzucone alternatywy; etapy do celu;
      T-NNN | cel | kryteria+komenda | zależności | ryzyko | typowa/trudna.
RECENZJA PLANU: cudzy plan → BLOKUJĄCE z T-NNN / OPCJONALNE / przyjąć-poprawić.
SPIKE: wykonalne/niewykonalne z kryterium; kod tylko przez wykonawcę
       w zleceniu A na spike branch, bez automatycznego scalenia.
NIE: implementacja, zmiana danych/config, przełączanie głównego checkoutu.
ZAPIS: analityk tylko odpowiedź; architekt tylko wskazane docs/tasks lub ADR,
       bez TODO/PROJEKT. Kryteriów rozpoczętej pracy nie zmieniaj.
WYNIK: analizy/diagnozy do 40 linii, plan do 80; rekomendacja i dowody,
       nieznane jako [?], decyzje właściciela oznaczone z rekomendacją.
```

## Procedura wysłania i odbioru

W native wybierz dostępne API, świeży kontekst recenzenta i potwierdzony
katalog. Nie dziedzicz całej rozmowy autora. Jeśli katalogu nie można
ustawić/izolować, użyj CLI. Run_agent nie tworzy gałęzi/worktree sam:
przygotowuje je kierownik. Zachowaj rzeczywisty ID/numer rundy i plik wyniku.
W trakcie stop nie rozpoczynaj nowego zlecenia. Po zakończeniu sprawdź
artefakty/Git/stderr; exit 0 nie oznacza ZALICZONE ani GOTOWE.
