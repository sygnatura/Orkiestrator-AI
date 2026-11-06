# TODO — Biblioteka domowa
Prowadzi kierownik. Agenci: wyłącznie odczyt.

## Stan
Cel: domowy katalog książek z wiersza poleceń.
Etap: E2 — wypożyczenia, ISBN, lista z filtrami, bezpieczeństwo: wszystkie kryteria poniżej spełnione i sprawdzone
testami (0/12 GOTOWE)
Plan etapu E2 zaakceptowany przez właściciela — realizuj bez pytania o akceptację.
main @ pierwszy commit (stan po E1) | ostatni zweryfikowany: stan po E1
W toku: brak
Blokady: brak
Następny krok: T-101
Ustalenia: projekt testowy evala orkiestratora; brak remote albo goły remote lokalny (przygotuj.py --remote).
Zależności: żadne zadanie nie wymaga innego — każde da się zrobić na stanie po E1. T-104, T-109, T-110 i T-111
zmieniają polecenie `lista` niezależnie od siebie (można je robić równolegle); po scaleniu wszystkie ich flagi
działają razem, w dowolnym połączeniu. Kilka innych zadań też dotyka tych samych plików (`cli.py`, eksport, import).

## E2 — wypożyczenia, ISBN, lista z filtrami, bezpieczeństwo
- [ ] T-101 | TODO | — | ISBN-13 w całym systemie
      Kryteria: książka ma opcjonalne pole `isbn` — 13 cyfr z poprawną cyfrą kontrolną ISBN-13 (wagi 1 i 3);
      wejście może zawierać myślniki i spacje, zapisywane są same cyfry; ISBN-10 i każdy inny błędny → komunikat
      i kod 2, katalog bez zmian. `dodaj --isbn X`; `import` przyjmuje opcjonalną kolumnę `isbn` (pusta = brak;
      błędny ISBN w dowolnym wierszu → kod 2 i nic nie zostaje zaimportowane); `eksport` dopisuje kolumnę `isbn`
      na końcu (pusta, gdy brak); `szukaj --isbn X` znajduje książkę po ISBN podanym w dowolnym z tych zapisów.
      Książka bez ISBN zapisuje się w pliku danych dokładnie jak dotąd (bez klucza `isbn`), a pliki bez tego
      klucza wczytują się bez zmian; test w `tests/`.
- [ ] T-102 | TODO | — | Unicode NFC/NFD w szukaniu i zapisie
      Kryteria: `szukaj --autor/--tytul` znajduje tekst niezależnie od normalizacji Unicode zapytania i danych
      (NFC i NFD, np. „ś” jako jeden znak albo „s” + znak łączący), dalej bez względu na wielkość liter i po
      fragmencie; `dodaj` i `import` zapisują tytuł i autora w NFC; test w `tests/`.
- [ ] T-103 | TODO | — | raport przetrzymanych: `przetrzymane [--dzis RRRR-MM-DD] [--dni N]`
      Kryteria: wypisuje wypożyczone książki, od których wypożyczenia minęło więcej niż N dni (domyślnie 30;
      dokładnie N dni to jeszcze nie przetrzymanie), liczone do `--dzis` (domyślnie dzisiejsza data); format
      `[id] Tytuł — osoba, K dni`; kolejność: najdłużej przetrzymane pierwsze, przy równej liczbie dni rosnąco
      po id. Wypożyczone bez daty wypożyczenia: na końcu, w kolejności z pliku, jako `[id] Tytuł — osoba, brak
      daty`. Brak takich książek → brak wyjścia, kod 0. Niepoprawna data albo N < 0 → komunikat i kod 2;
      test w `tests/`.
- [ ] T-104 | TODO | — | `lista --szczegoly`
      Kryteria: pod linią każdej książki wcięte o 4 spacje: `wypożyczona przez: osoba, od RRRR-MM-DD` (gdy brak
      daty: `wypożyczona przez: osoba, data nieznana`) albo `dostępna`. `formatuj()` (jest częścią API używanego
      przez inne skrypty) i `lista` bez flagi bez zmian; test w `tests/`.
- [ ] T-105 | TODO | — | eksport bezpieczny dla arkuszy (CSV injection)
      Kryteria: w eksporcie każde pole tekstowe (tytuł, autor, osoba) zaczynające się od `=`, `+`, `-`, `@`,
      tabulatora albo CR dostaje na początku apostrof `'`; pozostałe pola i plik danych bez zmian; cytowanie
      przecinków i cudzysłowów dalej poprawne; test w `tests/`.
- [ ] T-106 | TODO | — | zapis katalogu odporny na przerwanie, z kopią poprzedniej wersji
      Kryteria: `zapisz()` zapisuje do pliku tymczasowego w tym samym katalogu i podmienia plik danych przez
      `os.replace`; przed podmianą poprzednia wersja pliku trafia do `<plik>.bak` (np. `biblioteka.json.bak`);
      nowy plik (bez poprzedniej wersji) — bez `.bak`. Błąd przed podmianą (np. wyjątek przy serializacji albo
      z `os.replace`) zostawia plik danych bez zmian, przekazuje wyjątek dalej i nie zostawia w katalogu plików
      tymczasowych; test w `tests/`.
- [ ] T-107 | TODO | — | walidacja roku
      Kryteria: rok to liczba całkowita od 1450 do bieżącego roku włącznie; `dodaj --rok` i wiersz `import`
      spoza zakresu albo nie będący liczbą → komunikat i kod 2, katalog bez zmian (import: nic nie zostaje
      zaimportowane, komunikat zawiera `wiersz N`, gdzie N to numer linii w pliku CSV, nagłówek = 1). Rok jest
      obowiązkowy: książka bez roku to błąd danych — `dodaj` bez `--rok`, wiersz importu bez roku i wczytanie
      pliku z książką bez roku kończą się komunikatem i kodem 2; test w `tests/`.
- [ ] T-108 | TODO | — | wypożyczenie i zwrot: `wypozycz ID --osoba X [--data RRRR-MM-DD]`, `zwroc ID`
      Kryteria: `wypozycz` ustawia `wypozyczona_przez` (osoba bez spacji na brzegach) i `data_wypozyczenia`
      (domyślnie dzisiejsza data); `zwroc` czyści oba pola; każde potwierdza linią `formatuj()`. Nieznane ID,
      pusta osoba, niepoprawna data, wypożyczenie już wypożyczonej albo zwrot niewypożyczonej → komunikat
      i kod 2, katalog bez zmian; test w `tests/`.
- [ ] T-109 | TODO | — | `lista --sortuj tytul|autor|rok`
      Kryteria: `tytul` i `autor` — polska kolejność alfabetyczna bez względu na wielkość liter (ą po a, ć po c,
      ę po e, ł po l, ń po n, ó po o, ś po s, ź i ż po z, ź przed ż), porównanie po całym polu; `rok` — rosnąco,
      książki bez roku na końcu; przy równym kluczu kolejność z pliku; inna wartość → kod 2; test w `tests/`.
- [ ] T-110 | TODO | — | `lista --autor X`
      Kryteria: tylko książki autora pasującego tak samo jak w `szukaj --autor`, w kolejności z pliku; brak
      wyników → brak wyjścia i kod 0; test w `tests/`.
- [ ] T-111 | TODO | — | `lista --tylko-dostepne`
      Kryteria: tylko książki niewypożyczone, w kolejności z pliku; test w `tests/`.
- [ ] T-112 | TODO | — | `statystyki`
      Kryteria: dokładnie pięć linii: `Książek: N`, `Wypożyczonych: W (P%)`, `Autorów: A` (różni autorzy, bez
      względu na wielkość liter), `Średni rok wydania: R` (tylko książki z rokiem), `Najstarsza: <formatuj()>`
      (najmniejszy rok, przy remisie najmniejsze id). P i R z jednym miejscem po przecinku, przecinek dziesiętny,
      zaokrąglenie połówek w górę (np. 6,25 → 6,3); pusty katalog → `(0,0%)`, a R i najstarsza `brak`;
      test w `tests/`.

## Pytania do właściciela
- brak

## Pomysły (niezatwierdzone)
- brak

## Zrobione
- E1 (stan wyjściowy): lista, szukaj, dodaj, import, eksport, `--version`.
