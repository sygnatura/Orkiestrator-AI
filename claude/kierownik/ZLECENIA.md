# ZLECENIA — order templates for the executor, reviewer and analyst/architect

Read by the lead (SKILL.md, section 12) before the first order in a session. Order text is in Polish; keep the
field names exactly as below.

An order is self-contained: the agent doesn't know the lead's conversation. It refers to files instead of
copying them. It states the REASON (PO CO) — an agent in a fresh context doesn't know otherwise which trade-offs
are acceptable. Paths and shas are established, not invented.

To a `kier-*` subagent give only the order content — role, rules and output format are in its definition, and it
gets AGENTS.md automatically (through the project's CLAUDE.md). Lines prefixed `[CLI]` are added only to orders
for Codex/`agy`, which have no role definition; a `[CLI zamiast …]` line REPLACES the named line of the Claude
version, it doesn't add to it. `[CLI: AGENTS.md]` in PRZECZYTAJ is needed only by `agy` (Codex loads AGENTS.md by
itself). `general-purpose` (when there are no `kier-*` subagents — SKILL.md, section 1, step 5) gets the `[CLI]`
lines except AGENTS.md (it gets CLAUDE.md), but GAŁĄŹ and KATALOG as a Claude subagent, because it works in a
Claude Code worktree; add the "On start" steps from the package's `agents/kier-wykonawca.md`.

## A. Executor (`kier-wykonawca`, class per SKILL.md section 7; backup: CLI)

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
    [CLI] NIE: merge, push, zmiany TODO.md / PROJEKT.md / kryteriów, osłabianie testów,
          płatne lub produkcyjne zasoby (patrz AGENTS.md „Środowisko i koszty”).
    [CLI] NA KONIEC: prawdziwe sprawdzenie (testy, lint, scenariusz z kryteriów — do końca), commit wg
          konwencji z AGENTS.md i raport ≤ 15 linii; każde twierdzenie z wyniku polecenia z tej sesji:
            T-NNN | gałąź | sha bazy → sha końcowy | katalog pracy
            ZMIANY: 1–3 zdania; liczba plików
            TESTY: `<polecenie>` → exit <n>; passed/failed/skipped
            SCENARIUSZ: co uruchomiono jak użytkownik → wynik
            NIE SPRAWDZONO: …
            POZA ZAKRESEM: propozycje (niewdrożone)
          Nie podejmuj innych zadań.

## B. Reviewer (`kier-recenzent` one class above the author; selectively: other family via CLI)

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
    [CLI] UWAGI: BLOKUJĄCE są tylko: niespełnione kryterium, błąd, wyjście poza zakres, osłabiony test, kod
          „na przyszłość”, sekret — z lokalizacją plik:linia. Reszta OPCJONALNE (nie wpływa na werdykt).
    [CLI] NIE: nie poprawiaj kodu, nie commituj, nie przełączaj gałęzi; tylko zasoby testowe/lokalne.
    [CLI] WYNIK (≤ 20 linii):
      WERDYKT: ZALICZONE | DO POPRAWY (są BLOKUJĄCE) | ZABLOKOWANE (czego brakuje) — T-NNN @ <sha>  (etap: E<n> @ <sha main>)
      K1..Kn: OK / NIE / NIE SPRAWDZONO (powód) — dowód (polecenie → wynik / obserwacja)
      BLOKUJĄCE: … z lokalizacją      OPCJONALNE: …

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
