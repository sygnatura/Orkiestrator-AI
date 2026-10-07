# ZLECENIA — szablony dla wykonawcy, recenzenta i analityka/architekta

Czyta kierownik (SKILL.md, sekcja 12) przed pierwszym zleceniem w sesji.

Zlecenie jest samowystarczalne: agent nie zna rozmowy kierownika. Odwołuje się do plików zamiast
kopiować ich treść. Podaje POWÓD zadania — agent w świeżym kontekście bez niego nie wie, które
kompromisy są dopuszczalne. Ścieżki i sha są ustalone, nie wymyślone.

Subagentowi `kier-*` podajesz tylko treść zlecenia — rola, zasady i format wyniku są już w jego
definicji, a AGENTS.md dostaje automatycznie (przez CLAUDE.md projektu). Wiersze z prefiksem `[CLI]`
dodajesz tylko do zlecenia dla Codex/`agy`; wiersz `[CLI zamiast …]` ZASTĘPUJE wskazany wiersz dla subagenta
Claude, nie uzupełnia go. `general-purpose` (gdy subagentów `kier-*` nie ma — SKILL.md, sekcja 1, krok 5)
dostaje wiersze `[CLI]`, ale GAŁĄŹ i KATALOG jak subagent Claude, bo pracuje w worktree Claude Code; dopisz mu
kroki „Na start” z `~/.claude/agents/kier-wykonawca.md`.

## A. Wykonawca (`kier-wykonawca`, klasa wg SKILL.md, sekcja 7; zapas: CLI)

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
    [CLI] NA KONIEC: commit wg konwencji z AGENTS.md i raport wg AGENTS.md (≤ 15 linii).
          Nie podejmuj innych zadań.

## B. Recenzent (`kier-recenzent` w klasie wyżej niż autor; wybiórczo: inna rodzina przez CLI)

    RECENZJA: T-NNN — <cel>   (albo: CEL ETAPU E<n> na main)
    KATALOG: <ścieżka worktree wykonawcy — z jego raportu lub `git worktree list`; tam jest
             wyewidencjonowana gałąź zadania>   (etap: <repo> na main)
    [CLI zamiast wiersza KATALOG] KATALOG: <repo>/.kierownik/wt/T-NNN-rec — odłączony worktree na commicie
             gałęzi, przygotowany przez kierownika PRZED zapisaniem zlecenia (ZESPOL.md „Zapas”: utworzony,
             zależności i konfiguracja testowa na miejscu); pracuj tylko w nim, niczego nie instaluj,
             nie twórz worktree ani gałęzi; brak czegoś → NIE SPRAWDZONO
    ZMIANA: <sha bazy> ... task/T-NNN-nazwa @ <sha>   (etap: <sha zamknięcia poprzedniego etapu; pierwszy etap:
            sha commitu przejęcia projektu albo pierwszego commitu> ... main @ <sha>)
            diff: `git diff <sha bazy>...<gałąź>` — trzy kropki: tylko zmiany gałęzi
    PRZECZYTAJ: [CLI: AGENTS.md (sekcja „Weryfikacja cudzej zmiany”),] [docs/tasks/T-NNN.md — tylko Cel,
                Kontekst, Zakres, Kryteria; sekcje autora (Postęp, Odkrycia i decyzje, Wynik) pomiń]
    KRYTERIA: <dokładnie te z zadania; dla etapu: cel etapu + scenariusz end-to-end>
    JAK URUCHOMIĆ: <polecenia> (wnioski autora celowo pominięte)
    [CLI] ZRÓB: sprawdź każde kryterium w działaniu (sama lektura kodu to nie dowód → NIE SPRAWDZONO);
          przejrzyj diff (zakres, testy, zbędne abstrakcje, błędy).
    [CLI] NIE: nie poprawiaj kodu, nie commituj, nie przełączaj gałęzi; tylko zasoby testowe/lokalne.
    [CLI] WYNIK (≤ 20 linii):
      WERDYKT: ZALICZONE | DO POPRAWY (są BLOKUJĄCE) | ZABLOKOWANE (czego brakuje) — T-NNN @ <sha>  (etap: E<n> @ <sha main>)
      K1..Kn: OK / NIE / NIE SPRAWDZONO (powód) — dowód (polecenie → wynik / obserwacja)
      BLOKUJĄCE: … z lokalizacją      OPCJONALNE: …

## C. Analiza / plan / recenzja planu / diagnoza (`kier-analityk` lub `kier-architekt`; bez zmian w kodzie)

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
