# ZLECENIA v12 — Codex

Order text is in Polish; keep the field names below. An order is self-contained: PO CO, real paths and full
SHAs, scope, the original criteria, environment and permissions. A native agent gets the right role and minimal
context; the CLI helper inserts the same role definition. Codex loads AGENTS.md from the repo root to the working
directory by itself, so orders don't repeat it; name only directory rules and CLAUDE.md imports the agent must open.
Never the author's full conversation, secrets, or a prompt pasted as executable shell text.
Lines marked `[CLI]` are added only when the order goes to an external CLI runner from the registry (`claude-cli`,
`agy-cli` or any other): it has no Codex role definition and may not load AGENTS.md, so the order carries the role
rules itself.

## A. Executor

```text
ZADANIE: T-NNN — <jeden cel>
PO CO: <cel etapu i zachowanie dla użytkownika>
KATALOG / POWŁOKA: <rzeczywisty katalog roli>
GAŁĄŹ / BAZA / AKTUALNA WERSJA: <przygotowana gałąź, pełne SHA>
  Gałąź już wyewidencjonowana; nie twórz innej ani worktree.
  Poprawki: ta sama gałąź i ostatni commit poprzedniej rundy.
PRZECZYTAJ: PROJEKT (sekcje ...), karta jeśli istnieje, konkretne pliki;
           [reguły katalogu / importy CLAUDE.md, jeśli dotyczą]. Wskaż rzeczywiste odpowiedniki dokumentów.
ŚRODOWISKO: <instalacja repo, testowa konfiguracja, usługi, izolacja danych>
ZAKRES: <obszary IN/OUT; wyłącznie zatwierdzone zadanie>
KRYTERIA: <oryginalne K1..Kn, komendy, scenariusz użytkownika, wersja kryteriów>
[KONFLIKT: <pliki>; gałąź koliduje z main @ <sha> — wykonaj `git merge <sha main>`, rozwiąż konflikt tak,
          żeby zostało zachowanie obu stron, uruchom testy i scommituj scalenie]   (tylko po `kier.py merge` → 4)
NIE: merge (poza wierszem KONFLIKT)/push/reset, TODO/PROJEKT/kryteria, osłabianie testów, produkcja,
     płatne API aplikacji/testów bez zgody wskazanej tutaj.
WYNIK: commit według procesu repo (Git odmówi przez sandbox → zmiany bez commitu, napisz to; commituje
       kierownik), raport do 15 linii: gałąź, katalog,
       baza→zmiana, pliki, komendy→exit/passed/failed/skipped, scenariusz,
       NIE SPRAWDZONO, POZA ZAKRESEM. W karcie tylko Postęp/Odkrycia/Wynik.
[CLI] PRZECZYTAJ też AGENTS.md. Przed końcem prawdziwe sprawdzenie (testy, lint,
     scenariusz z kryteriów — do końca); kontrola składni albo polecenie, które nie wystartowało,
     to NIE SPRAWDZONO. Najprostsze rozwiązanie, bez kodu „na przyszłość”; każde twierdzenie
     w raporcie z wyniku polecenia z tej sesji. Nie podejmuj innych zadań.
     Logi: długie wyjście (instalacja, testy, build) kieruj do pliku w katalogu tymczasowym systemu, czytaj kod wyjścia i końcówkę.
```

## B. Reviewer — fresh context

```text
RECENZJA: T-NNN albo CEL ETAPU E<n>
KATALOG / POWŁOKA: <przygotowany katalog zmiany, odblokowany po autorze>
BAZA / OCENIANY SHA: <pełne wersje; dla etapu zakres od poprzedniego etapu>
DIFF: git diff <baza>...<oceniany SHA>
AUTOR / KLASA / MODEL: <fakty, bez wniosków autora>
PRZECZYTAJ: karta tylko Cel/Kontekst/Zakres/Kryteria; [reguły katalogu, jeśli dotyczą].
KRYTERIA: <te same K1..Kn; etap: cel i scenariusz E2E>
JAK URUCHOMIĆ / DANE: <testowe komendy i izolacja, konkretne dozwolone operacje>
ZRÓB: K w działaniu z własnym dowodem, scenariusz i diff zakres/testy/błędy/nadmiar.
NIE: poprawianie kodu, commit, przełączanie gałęzi, instalowanie braków,
     zmiana kryteriów, czytanie Postęp/Odkrycia/Wynik autora jako podpowiedzi.
WYNIK do 20 linii: ZALICZONE | DO POPRAWY | ZABLOKOWANE — ID @ SHA;
  K1..Kn: OK / NIE / NIE SPRAWDZONO (powód), dowód komenda→wynik/obserwacja;
  BLOKUJĄCE z lokalizacją; OPCJONALNE. Źródła/indeks/HEAD bez zmian.
[CLI] PRZECZYTAJ też AGENTS.md. Testy z liczbą passed/failed/skipped; kod wyjścia 0
     nie wystarcza, polecenie, które nie wystartowało, i sama lektura kodu nie są dowodem →
     NIE SPRAWDZONO. BLOKUJĄCE są tylko: niespełnione kryterium, błąd, wyjście poza zakres,
     osłabiony test, kod „na przyszłość”, sekret; reszta OPCJONALNE (bez wpływu na werdykt).
     ZALICZONE: wszystkie K OK i brak BLOKUJĄCYCH; DO POPRAWY: choć jedna BLOKUJĄCA;
     ZABLOKOWANE: brak BLOKUJĄCYCH, ale któreś K niesprawdzalne — wymień, czego brakuje.
     Logi: długie wyjście (instalacja, testy, build) kieruj do pliku w katalogu tymczasowym systemu, czytaj kod wyjścia i końcówkę; katalog zmiany ma zostać czysty.
```

Reviewer per SKILL section 7 (MOCNY or risky work: another family first); under the v10 exception: fresh context plus your own tests and an explicit record of the
deviation. The reviewer doesn't need the author's report; its evidence comes from its own checks.

## C. Analyst / architect / plan review

```text
PYTANIE: <jedno: mapa | plan | recenzja planu | diagnoza | spike>
PO CO: <decyzja lub następny krok kierownika>
KATALOG / GAŁĄŹ @ SHA: <fakty>
PRZECZYTAJ: PROJEKT, TODO oraz konkretne pliki/obserwacje.
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

## Sending and receiving

Native: choose the available API, a fresh context for the reviewer and a confirmed directory. Don't inherit the
author's whole conversation. If the directory can't be set or isolated, use the CLI. run_agent.py doesn't create
branches or worktrees: the lead prepares them. Keep the real ID/round number and the result file. During `stop`
start no new order. Afterwards check artefacts, Git and stderr; exit 0 doesn't mean ZALICZONE or GOTOWE.
