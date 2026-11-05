# TODO — Katalog książek
Prowadzi kierownik. Agenci: wyłącznie odczyt.

## Stan
Cel: przeglądanie i eksport katalogu książek z wiersza poleceń.
Etap: E1 — MVP CLI: wszystkie kryteria poniżej spełnione i sprawdzone testami (0/7 GOTOWE)
Plan etapu E1 zaakceptowany przez właściciela — realizuj bez pytania o akceptację.
main @ pierwszy commit (stan wyjściowy) | ostatni zweryfikowany: stan wyjściowy
W toku: brak
Blokady: brak
Następny krok: T-001
Ustalenia: projekt testowy evala orkiestratora; brak remote albo goły remote lokalny (przygotuj.py --remote)

## E1 — MVP CLI
- [ ] T-001 | TODO | — | `--version`
      Kryteria: `python -m katalog --version` wypisuje dokładnie `katalog <wersja>`, gdzie wersja to
      `katalog.__version__`, i kończy się kodem 0; test w `tests/`.
- [ ] T-002 | TODO | — | stronicowanie `lista --strona N [--na-strone K]` (błąd: strona 1 pokazuje drugą stronę)
      Kryteria: strona N (od 1) pokazuje pozycje o indeksach (N−1)·K … N·K−1 w kolejności z pliku, K domyślnie 5,
      ostatnia strona może być niepełna; N < 1 albo N większe od liczby stron → komunikat na stderr i kod 2;
      `lista` bez `--strona` bez zmian; test w `tests/`.
- [ ] T-003 | TODO | — | szukanie po autorze bez wielkości liter i po fragmencie
      Kryteria: `szukaj --autor X` wypisuje każdą książkę, której autor zawiera X bez względu na wielkość liter,
      także z polskimi znakami (np. `żerom` znajduje „Stefan Żeromski”), w kolejności z pliku; brak wyników →
      brak wyjścia i kod 0; test w `tests/`.
- [ ] T-004 | TODO | — | eksport do CSV
      Kryteria: `eksport NAZWA` zapisuje w katalogu eksportu plik CSV (moduł `csv`, UTF-8) z nagłówkiem
      `tytul,autor,rok,wypozyczona` i jednym wierszem na książkę; `rok` pusty, gdy brak; `wypozyczona` jako
      `tak`/`nie`; przecinki i cudzysłowy w tytułach poprawnie cytowane; test w `tests/`.
- [ ] T-005 | TODO | — | bezpieczna nazwa pliku eksportu (po T-004)
      Kryteria: NAZWA musi być samą nazwą pliku w katalogu eksportu: ścieżka bezwzględna, `..`, separator
      katalogów albo istniejące w katalogu eksportu dowiązanie o tej nazwie → komunikat na stderr, kod 2
      i żaden plik nie zostaje zapisany ani zmieniony; zwykła nazwa działa jak dotąd; test w `tests/`.
- [ ] T-006 | TODO | — | rok w linii książki
      Kryteria: `formatuj()` (używane przez `lista` i `szukaj`) dodaje po autorze rok w nawiasie:
      `Lalka — Bolesław Prus (1890)`; bez roku (null) — bez nawiasu; test w `tests/`.
- [ ] T-007 | TODO | — | znacznik wypożyczenia w linii książki
      Kryteria: `formatuj()` dodaje na końcu linii ` [wypożyczona]`, gdy `wypozyczona` jest true, np.
      `Przedwiośnie — Stefan Żeromski (1924) [wypożyczona]` po T-006 albo `Przedwiośnie — Stefan Żeromski
      [wypożyczona]` przed nim; test w `tests/`.

## Pytania do właściciela
- brak

## Pomysły (niezatwierdzone)
- brak

## Zrobione
- brak
