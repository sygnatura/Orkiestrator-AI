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
REGRESJE: także to, czego zmiana nie może zepsuć, choć kryteria milczą: uprawnienia i właściciel plików,
     dowiązania symboliczne, utrata danych przy błędzie (zapis atomowy, kopie), kodowanie i normalizacja
     tekstu, zgodność formatu plików i API z dotychczasowymi odbiorcami, ścieżki błędów (kod wyjścia, stan bez
     zmian), dane z zewnątrz w arkuszach, powłoce, SQL i ścieżkach. Regresja wprowadzona przez tę zmianę to błąd
     (BLOKUJĄCE); istniejąca wcześniej — OPCJONALNE.
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

## Tryb zwarty (compact mode, SKILL section 5)

Zwarty only when all hold: the whole stage fits one executor session (about ≤ 15 tasks of typical size, and the
code the stage touches can be read in full); no task needs a design decision, a task card or an architect's plan;
one runner of the required class can do every task. Otherwise, or in doubt → pełny. The owner's `tryb: …`
overrides. Record the decision in the TODO header before the first order. Why: in the evals (claude/ANALIZA.md,
decision 15) per-task orders and reviews cost ~6× a single session on stages that fit one session, with no gain in
measured quality; the gain came from review, which this mode keeps once per stage.

Stage variant of A (the fields of A, with these lines instead):

```text
ZADANIE: E<n> — etap w trybie zwartym: T-NNN, T-NNN, … (kolejność z TODO)
GAŁĄŹ / BAZA / AKTUALNA WERSJA: task/E<n>-etap, pełne SHA (poprawki: ta sama gałąź)
PRZECZYTAJ: PROJEKT, TODO (etap E<n>: kryteria wszystkich zadań), karty jeśli istnieją.
KRYTERIA: te z TODO dla każdego zadania; każde zadanie to osobny commit z jego ID i własny test;
          runda poprawek: tylko zadania i uwagi BLOKUJĄCE wymienione w zleceniu.
WSTRZYMAJ: kryterium sprzeczne z istniejącym testem, danymi albo innym zadaniem, albo potrzebna decyzja →
          nie obchodź po cichu: zrób to, co niesporne, opisz w raporcie; zadania, którego nie skończysz,
          nie commituj (cofnij częściowe zmiany) i wpisz je w WSTRZYMANE.
WYNIK: raport do 25 linii: wiersz na zadanie „T-NNN | sha | test → wynik | uwagi”, testy całości,
       scenariusz, WSTRZYMANE, NIE SPRAWDZONO, POZA ZAKRESEM.
```

Compact-stage variant of B (the fields of B, with these lines instead):

```text
RECENZJA: E<n> — etap w trybie zwartym: T-NNN, T-NNN, …
BAZA / OCENIANY SHA: <sha bazy> ... task/E<n>-etap @ <sha>; commity: git log --oneline <baza>..task/E<n>-etap
KRYTERIA: każdego zadania (z TODO) + cel etapu i scenariusz E2E (runda powtórna: zadania zmienione + scenariusz)
WYNIK do 40 linii: wiersz na zadanie „T-NNN: ZALICZONE | DO POPRAWY | ZABLOKOWANE — K1..Kn: …”,
  „CEL ETAPU: OK / NIE — scenariusz → wynik”, BLOKUJĄCE z T-NNN i lokalizacją, OPCJONALNE.
```

Flow: one order A (stage variant, executor in MOCNY, „przydział” as for a task) → one order B (compact-stage
variant; other family first when the stage touches security, data, money or an external contract) instead of
the per-task reviews and the stage-goal evidence → DO POPRAWY for some tasks: `KIER fix-round E<n>-etap`, order A
with only those tasks, order B for them plus the stage scenario (two failed rounds → diagnosis as usual) → all
ZALICZONE: `KIER merge E<n>-etap --push`, „Zrobione” a line per task („recenzja wspólna E<n>”). Back to pełny for
the rest of the stage when the executor stopped half-way, a task needs a decision, or one review returned ≥ 3
tasks DO POPRAWY: review and merge what the branch finished, then continue task by task from main.

## Sending and receiving

Native: choose the available API, a fresh context for the reviewer and a confirmed directory. Don't inherit the
author's whole conversation. If the directory can't be set or isolated, use the CLI. run_agent.py doesn't create
branches or worktrees: the lead prepares them. Keep the real ID/round number and the result file. During `stop`
start no new order. Afterwards check artefacts, Git and stderr; exit 0 doesn't mean ZALICZONE or GOTOWE.
