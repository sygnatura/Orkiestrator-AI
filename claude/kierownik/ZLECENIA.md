# ZLECENIA — order templates for the executor, reviewer and analyst/architect

Read by the lead (SKILL.md, section 12) before the first order in a session. Order text is in Polish; keep the
field names exactly as below.

An order is self-contained: the agent doesn't know the lead's conversation. It refers to files instead of
copying them. It states the REASON (PO CO) — an agent in a fresh context doesn't know otherwise which trade-offs
are acceptable. Paths and shas are established, not invented.

To a `kier-*` subagent give only the order content — role, rules and output format are in its definition, and it
gets AGENTS.md automatically (through the project's CLAUDE.md). Lines prefixed `[CLI]` are added only to orders
for external CLI runners (Codex, `agy`, `claude -p` or any other in the registry), which have no role definition; a `[CLI zamiast …]` line REPLACES the named line of the Claude
version, it doesn't add to it. `[CLI: AGENTS.md]` in PRZECZYTAJ is needed by runners that don't load AGENTS.md themselves (Codex
does; for others the smoke test decides). `general-purpose` (when there are no `kier-*` subagents — SKILL.md, section 1, step 4) gets the `[CLI]`
lines except AGENTS.md (it gets CLAUDE.md), but GAŁĄŹ and KATALOG as a Claude subagent, because it works in a
Claude Code worktree; add the "On start" steps from the package's `agents/kier-wykonawca.md`.

## A. Executor (`kier-wykonawca` or an external CLI runner, class per SKILL.md section 7)

    ZADANIE: T-NNN — <cel jednym zdaniem>
    PO CO: <cel etapu i komu służy; co użytkownik będzie mógł zrobić po zmianie — 1–2 zdania>
    GAŁĄŹ: task/T-NNN-nazwa od <sha bazy> — utwórz ją `git switch -c task/T-NNN-nazwa <sha>`
           (runda poprawek: gałąź już istnieje @ <sha> → `git switch task/T-NNN-nazwa`, nie twórz nowej)
    [CLI zamiast wiersza GAŁĄŹ] KATALOG: <repo>/.kierownik/wt/T-NNN — gałąź task/T-NNN-nazwa @ <sha> jest
           już utworzona i wyewidencjonowana w tym katalogu; pracuj na niej, nie twórz gałęzi ani worktree
    PRZECZYTAJ: [CLI: AGENTS.md,] docs/PROJEKT.md (sekcje: …) [+ docs/tasks/T-NNN.md] [+ konkretne pliki]
    ŚRODOWISKO: <co poza „Instalacja” z AGENTS.md jest potrzebne, żeby testy ruszyły w świeżym worktree —
                np. `cp .env.example .env`, uruchomiona usługa X; albo: nic>
    ZAKRES: zmieniaj tylko <ścieżki / obszar>. [CLI] Najprostsze rozwiązanie spełniające kryteria;
            bez funkcji spoza zadania i bez kodu „na przyszłość”.
    KRYTERIA: <obserwowalne zachowanie + polecenie testu; scenariusz użycia>
    [KONFLIKT: <pliki>; gałąź koliduje z main @ <sha> — wykonaj `git merge <sha main>`, rozwiąż konflikt tak,
              żeby zostało zachowanie obu stron, uruchom testy i scommituj scalenie]   (tylko po `kier.py merge` → 4)
    [CLI] NIE: merge (poza wierszem KONFLIKT), push, zmiany TODO.md / PROJEKT.md / kryteriów, osłabianie testów,
          płatne lub produkcyjne zasoby (patrz AGENTS.md „Środowisko i koszty”).
    [CLI] LOGI: długie wyjście (instalacja, testy, build) kieruj do pliku w katalogu tymczasowym systemu, czytaj kod wyjścia i końcówkę.
          Wszystko na pierwszym planie, długie polecenia z maksymalnym limitem czasu narzędzia (gdy nie wystarczy →
          NIE SPRAWDZONO z powodem); nie uruchamiaj procesów w tle i nie kończ komunikatem „czekam na…”.
    [CLI] NA KONIEC: prawdziwe sprawdzenie (testy, lint, scenariusz z kryteriów — do końca), commit wg
          konwencji z AGENTS.md (gdy Git odmówi przez sandbox: zostaw zmiany bez commitu i napisz to
          w raporcie — commit zrobi kierownik) i raport ≤ 15 linii; każde twierdzenie z wyniku polecenia z tej sesji:
            T-NNN | gałąź | sha bazy → sha końcowy | katalog pracy
            ZMIANY: 1–3 zdania; liczba plików
            TESTY: `<polecenie>` → exit <n>; passed/failed/skipped
            SCENARIUSZ: co uruchomiono jak użytkownik → wynik
            NIE SPRAWDZONO: …
            POZA ZAKRESEM: propozycje (niewdrożone)
          Nie podejmuj innych zadań.

Stage variant (tryb zwarty, section „Tryb zwarty” below) — the fields above, with these lines instead:

    ZADANIE: E<n> — etap w trybie zwartym: T-NNN, T-NNN, … (kolejność z TODO.md)
    GAŁĄŹ: task/E<n>-etap od <sha bazy> — utwórz ją `git switch -c task/E<n>-etap <sha>`
           (runda poprawek: gałąź już istnieje @ <sha> → `git switch task/E<n>-etap`)
    PRZECZYTAJ: [CLI: AGENTS.md,] docs/PROJEKT.md, docs/TODO.md (etap E<n>: kryteria wszystkich zadań)
                [+ docs/tasks/T-NNN.md]
    KRYTERIA: te z TODO.md dla każdego zadania; każde zadanie to osobny commit z jego ID (konwencja z AGENTS.md)
              i własny test; runda poprawek: tylko zadania i uwagi BLOKUJĄCE wymienione w zleceniu
    WSTRZYMAJ: kryterium sprzeczne z istniejącym testem, danymi albo innym zadaniem, albo potrzebna decyzja →
               nie obchodź po cichu: zrób to, co niesporne, i opisz to w raporcie; zadania, którego nie skończysz,
               nie commituj (cofnij jego częściowe zmiany) i wpisz je w WSTRZYMANE
    RAPORT (≤ 25 linii zamiast 15): wiersz na zadanie „T-NNN | sha | test → wynik | uwagi”, potem TESTY całości,
           SCENARIUSZ, WSTRZYMANE, NIE SPRAWDZONO, POZA ZAKRESEM

## B. Reviewer (runner per SKILL.md section 7: other family via CLI, or host `kier-recenzent`)

    RECENZJA: T-NNN — <cel>   (albo: CEL ETAPU E<n> na main)
    KATALOG: <ścieżka worktree wykonawcy — z jego raportu lub `git worktree list`; tam jest
             wyewidencjonowana gałąź zadania>   (etap: <repo> na main)
    [CLI zamiast wiersza KATALOG] KATALOG: <repo>/.kierownik/wt/T-NNN-rec — odłączony worktree na commicie
             gałęzi, przygotowany przez kierownika PRZED zapisaniem zlecenia (zależności i konfiguracja
             testowa na miejscu); pracuj tylko w nim, niczego nie instaluj, nie twórz worktree ani gałęzi;
             brak czegoś → NIE SPRAWDZONO
    ZMIANA: <sha bazy> ... task/T-NNN-nazwa @ <sha>   (etap: <sha zamknięcia poprzedniego etapu; pierwszy etap:
            sha commitu przejęcia projektu albo pierwszego commitu> ... main @ <sha>)
            diff: `git diff <sha bazy>...<gałąź>` — trzy kropki: tylko zmiany gałęzi
    PRZECZYTAJ: [CLI: AGENTS.md,] [docs/tasks/T-NNN.md — tylko Cel, Kontekst, Zakres, Kryteria; sekcje autora
                (Postęp, Odkrycia i decyzje, Wynik) pomiń]
    KRYTERIA: <dokładnie te z zadania; dla etapu: cel etapu + scenariusz end-to-end>
    JAK URUCHOMIĆ: <polecenia> (wnioski autora celowo pominięte)
    [CLI] ZRÓB: sprawdź każde kryterium w działaniu — testy z liczbą passed/failed/skipped (kod wyjścia 0 nie
          wystarcza; polecenie, które nie wystartowało, niczego nie dowodzi; sama lektura kodu to nie dowód →
          NIE SPRAWDZONO) i scenariusz jak użytkownik; przejrzyj diff (zakres, osłabione testy, zbędne
          abstrakcje, błędy, sekrety).
    [CLI] REGRESJE: sprawdź też to, czego zmiana nie może zepsuć, choć kryteria o tym milczą: uprawnienia
          i właściciel plików, dowiązania symboliczne, utrata danych przy błędzie (zapis atomowy, kopie),
          kodowanie i normalizacja tekstu, zgodność formatu plików i API z dotychczasowymi odbiorcami, ścieżki
          błędów (kod wyjścia, stan bez zmian), dane z zewnątrz trafiające do arkuszy, powłoki, SQL i ścieżek.
          Regresja wprowadzona przez tę zmianę to błąd (BLOKUJĄCE); istniejąca wcześniej — OPCJONALNE.
    [CLI] UWAGI: BLOKUJĄCE są tylko: niespełnione kryterium, błąd, wyjście poza zakres, osłabiony test, kod
          „na przyszłość”, sekret — z lokalizacją plik:linia. Reszta OPCJONALNE (nie wpływa na werdykt).
    [CLI] NIE: nie poprawiaj kodu, nie commituj, nie przełączaj gałęzi; tylko zasoby testowe/lokalne.
    [CLI] LOGI: długie wyjście (instalacja, testy, build) kieruj do pliku w katalogu tymczasowym systemu, czytaj kod wyjścia i końcówkę (katalog zmiany ma zostać czysty).
    [CLI] WYNIK (≤ 20 linii):
      WERDYKT: ZALICZONE | DO POPRAWY (są BLOKUJĄCE) | ZABLOKOWANE (czego brakuje) — T-NNN @ <sha>  (etap: E<n> @ <sha main>)
      K1..Kn: OK / NIE / NIE SPRAWDZONO (powód) — dowód (polecenie → wynik / obserwacja)
      BLOKUJĄCE: … z lokalizacją      OPCJONALNE: …

Compact-stage variant (tryb zwarty) — the fields above, with these lines instead:

    RECENZJA: E<n> — etap w trybie zwartym: T-NNN, T-NNN, …
    ZMIANA: <sha bazy> ... task/E<n>-etap @ <sha>; commity zadań: `git log --oneline <sha bazy>..task/E<n>-etap`
    KRYTERIA: każdego zadania (z TODO.md) + cel etapu i scenariusz end-to-end jak użytkownik
              (runda powtórna: zadania zmienione w rundzie + scenariusz etapu)
    WYNIK (≤ 40 linii zamiast 20): wiersz na zadanie „T-NNN: ZALICZONE | DO POPRAWY | ZABLOKOWANE — K1..Kn: …”,
          wiersz „CEL ETAPU: OK / NIE — scenariusz → wynik”, BLOKUJĄCE z T-NNN i lokalizacją, OPCJONALNE

## C. Analysis / plan / plan review / diagnosis (`kier-analityk` or `kier-architekt`; no code changes)

    PYTANIE: <jedno, ograniczone: mapa obszaru | plan etapu | recenzja planu | diagnoza | spike>
    PO CO: <jaką decyzję lub następny krok kierownika umożliwi odpowiedź — 1 zdanie>
    KATALOG: <główny katalog repo albo worktree zadania> / GAŁĄŹ @ sha: <…>
    PRZECZYTAJ: [CLI: AGENTS.md,] docs/PROJEKT.md, docs/TODO.md [+ konkretne pliki / obserwacje]
    DLA DIAGNOZY: obserwacje (co, gdzie, dokładny komunikat, jak odtworzyć) → przyczyna z dowodem
                  (fakt oddzielnie od hipotezy) i plan naprawy małymi krokami z kryteriami.
    DLA PLANU: najprostszy wariant + porzucone alternatywy; zadania w formacie
               T-NNN | cel | kryteria + polecenie testu | zależności | ryzyko | trudność (typowa / trudna).
    DLA RECENZJI PLANU: <plik lub treść planu>; wynik: uwagi BLOKUJĄCE (z T-NNN) i OPCJONALNE
               + rekomendacja: przyjąć / poprawić.
    DLA SPIKE'U: pytanie „wykonalne / niewykonalne” z kryterium; bez zmian w repo. Spike wymagający
               kodu → zlecenie A dla wykonawcy na gałęzi `spike/T-NNN` z tym kryterium, bez scalania.
    NIE: nie zmieniaj kodu, danych ani konfiguracji.
    WYNIK: ≤ 40 linii (plan może być dłuższy); duży plan lub diagnozę architekt zapisuje
           w docs/tasks/T-NNN.md (analityk nie zapisuje plików).

## Tryb zwarty (compact mode, SKILL.md section 5)

Zwarty only when all hold: the whole stage fits one executor session (about ≤ 15 tasks of typical size, and the
code the stage touches can be read in full); no task needs a design decision, a docs/tasks/T-NNN.md specification
or a plan from `kier-architekt`; one runner of the required class can do every task. Otherwise, or in doubt →
pełny. The owner's `tryb: …` overrides. Record the decision in the TODO.md header before the first order. Why:
in the evals (ANALIZA.md, decision 15) per-task orders and reviews cost ~6× a single session on stages that fit one
session, with no gain in measured quality; the gain came from review, which this mode keeps once per stage.

1. One order A, stage variant, to an executor in MOCNY (the „przydział” line as for a task, role `wykonawca E<n>`).
2. One order B, compact-stage variant, to a fresh reviewer per SKILL.md section 7 (other family first when the
   stage touches security, data, money or an external contract). It replaces the per-task reviews and END OF STAGE
   step 1; your formal check (section 8, point 1) covers the whole branch.
3. Some tasks DO POPRAWY → `KIER fix-round E<n>-etap`, order A (stage variant, existing branch) with only those
   tasks and their BLOKUJĄCE remarks, then order B for them plus the stage scenario. Two failed rounds on the same
   problem → the diagnosis as in full mode.
4. All ZALICZONE → `KIER merge E<n>-etap --push --opis "<opis>"`; „Zrobione”: a line per task (sha of its commit,
   „recenzja wspólna E<n>”, rounds), then END OF STAGE from step 2.

Back to pełny for the rest of the stage when the executor stopped half-way (context, limit), a task turned out to
need a decision, or one review returned ≥ 3 tasks DO POPRAWY: review and merge what the branch finished (order B,
compact-stage variant, for those tasks), then continue task by task from main. WSTRZYMANE tasks are not on the
branch; settle them as any criteria problem (SKILL.md section 8, last paragraph).
