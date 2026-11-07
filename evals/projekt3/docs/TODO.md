# TODO — Biblioteka domowa
Prowadzi kierownik. Agenci: wyłącznie odczyt.

## Stan
Cel: domowy katalog książek z wiersza poleceń.
Etap: E3 — konfiguracja i formaty (0/4 GOTOWE); dalej E4, E5
Plan etapów E3, E4 i E5 zaakceptowany przez właściciela — realizuj bez pytania o akceptację.
Jeden etap na sesję: po zamknięciu etapu zakończ sesję; następny etap zaczyna nowa sesja.
main @ pierwszy commit (stan po E2) | ostatni zweryfikowany: stan po E2
W toku: brak
Blokady: brak
Następny krok: T-201
Ustalenia: projekt testowy evala orkiestratora; brak remote albo goły remote lokalny (przygotuj.py --remote).
Zależności: zadania realizuj w kolejności numerów — późniejsze zadanie etapu może korzystać z wcześniejszych
(np. testy T-201 mogą używać `--format-daty` z T-202 dopiero po T-202), a etap — z poprzednich etapów.

## E3 — konfiguracja i formaty
- [ ] T-201 | TODO | — | plik konfiguracji i polecenie `konfiguracja`
      Kryteria: plik TOML (`tomllib`) — domyślnie `biblioteka.toml` w katalogu pliku danych, albo globalna opcja
      `--konfiguracja PLIK`; brak pliku domyślnego → wartości domyślne, brak pliku podanego jawnie → komunikat
      i kod 2. Klucze (wszystkie opcjonalne): `dni_przetrzymania` (liczba całkowita ≥ 0, domyślnie 30),
      `format_daty` (`"pl"` albo `"iso"`, domyślny — T-202), `katalog_eksportu` (tekst, domyślnie `eksport` względem
      bieżącego katalogu jak dotąd; ścieżka względna z pliku liczona od katalogu pliku konfiguracji). Błędny TOML, nieznany klucz, zły typ (np. `true`
      albo `"10"` zamiast liczby) albo wartość → komunikat z nazwą klucza i kod 2 przy każdym poleceniu, pliki bez zmian. Polecenie
      `konfiguracja` wypisuje trzy linie w kolejności alfabetycznej kluczy: `<klucz> = <wartość> (<źródło>)`,
      gdzie źródło to `domyślne`, `plik` albo `argument`, a wartość jest taka, jak ją podano; test w `tests/`.
- [ ] T-202 | TODO | — | format dat w wyjściu
      Kryteria: daty wypisywane przez CLI (dziś: `lista --szczegoly`, „od …”; w kolejnych etapach każde nowe
      wyjście z datą) w formacie `pl` = `DD.MM.RRRR` albo `iso` = `RRRR-MM-DD`. Pierwszeństwo: globalna opcja
      `--format-daty pl|iso` > klucz `format_daty` z konfiguracji > format domyślny. **Format domyślny: do
      ustalenia z właścicielem przed implementacją.** W pliku danych daty zostają w ISO; test w `tests/`.
- [ ] T-203 | TODO | — | daty w argumentach w obu formatach
      Kryteria: `wypozycz --data` i `przetrzymane --dzis` (oraz każdy nowy argument z datą) przyjmują
      `RRRR-MM-DD` i `DD.MM.RRRR` (dzień i miesiąc dwucyfrowe); niepoprawna data w obu formatach (np. `31.02.2026`,
      `1.2.2026`) → komunikat i kod 2. W pliku zapisywane w ISO; test w `tests/`.
- [ ] T-204 | TODO | — | ustawienia z konfiguracji w poleceniach (po T-201)
      Kryteria: `przetrzymane` bez `--dni` używa `dni_przetrzymania`; `eksport` bez `--katalog-eksportu` zapisuje
      do `katalog_eksportu`; jawne argumenty mają pierwszeństwo; test w `tests/`.

## E4 — historia i rezerwacje
- [ ] T-301 | TODO | — | historia wypożyczeń: `historia ID`
      Kryteria: każde udane `wypozycz` i `zwroc` zapisuje zdarzenie (id książki, typ, osoba, data wypożyczenia
      albo zwrotu); nieudane polecenie niczego nie zapisuje. `historia ID` wypisuje jedno zdarzenie na linię
      w kolejności dat (przy równych datach — w kolejności zapisu): `<data> — wypożyczenie — <osoba>` albo
      `<data> — zwrot — <osoba>`, data w formacie wyjścia z T-202. Nieznane ID → kod 2; brak zdarzeń → brak
      wyjścia, kod 0. Do E5 zdarzenia są w pliku obok danych: `<nazwa pliku danych bez .json>.historia.json`,
      zapisywanym jak plik danych (T-106); test w `tests/`.
- [ ] T-302 | TODO | — | data zwrotu: `zwroc ID [--data D]`
      Kryteria: data zwrotu domyślnie dzisiejsza, formaty z T-203; wcześniejsza niż data wypożyczenia →
      komunikat i kod 2, nic się nie zmienia; test w `tests/`.
- [ ] T-303 | TODO | — | rezerwacje: `rezerwuj ID --osoba X`, `rezerwacje ID`
      Kryteria: `rezerwuj` dopisuje osobę (bez spacji na brzegach) na koniec kolejki książki i wypisuje
      `Zarezerwowano: <osoba>, pozycja <N>`; rezerwować można także książkę dostępną (niewypożyczoną); nieznane ID,
      pusta osoba albo osoba już w kolejce → kod 2. `rezerwacje ID` wypisuje kolejkę: `1. <osoba>`, `2. …`;
      pusta → brak wyjścia, kod 0; nieznane ID → kod 2. Do E5 kolejki są
      w pliku `<nazwa pliku danych bez .json>.rezerwacje.json`, zapisywanym jak plik danych; test w `tests/`.
- [ ] T-304 | TODO | — | wypożyczenie respektuje rezerwacje (po T-303)
      Kryteria: gdy kolejka książki nie jest pusta, wypożyczyć może tylko pierwsza osoba z kolejki (po
      usunięciu spacji na brzegach) — wtedy znika z kolejki; inna osoba → komunikat z imieniem pierwszej
      osoby, kod 2, nic się nie zmienia; test w `tests/`.
- [ ] T-305 | TODO | — | zwrot pokazuje następną rezerwację (po T-303)
      Kryteria: gdy po zwrocie kolejka nie jest pusta, `zwroc` wypisuje drugą linię
      `Zarezerwowana dla: <pierwsza osoba z kolejki>`; test w `tests/`.

## E5 — jeden plik danych (format v2)
- [ ] T-401 | TODO | — | format v2
      Kryteria: CLI czyta dwa formaty pliku danych: stary (lista książek + pliki `.historia.json`
      i `.rezerwacje.json` obok) i v2 — jeden plik `{"wersja": 2, "ksiazki": [...], "historia": [...],
      "rezerwacje": {...}}` (dokładnie te klucze; książki w dotychczasowym układzie, bez klucza `isbn`, gdy brak
      ISBN). Zapisuje w formacie, w którym plik przeczytało: stary plik zostaje stary (inne skrypty go czytają),
      v2 zostaje v2 i nie powstają przy nim pliki poboczne. Wszystkie polecenia działają tak samo w obu
      formatach. Zapis jak w T-106 (plik tymczasowy, `os.replace`, `.bak`). API `magazyn.wczytaj()` /
      `magazyn.zapisz()` (lista książek) zostaje bez zmian; test w `tests/`.
- [ ] T-402 | TODO | — | polecenie `migruj` (po T-401)
      Kryteria: przenosi plik w starym formacie do v2 bez utraty danych, każdy istniejący plik poboczny dostaje
      nazwę `<plik>.v1.bak`, i wypisuje `Zmigrowano do wersji 2: <N> książek, <M> zdarzeń, <R> rezerwacji`
      (R — liczba osób we wszystkich kolejkach); plik już w v2 → `Plik jest już w wersji 2.`, kod 0, plik bez
      zmian; test w `tests/`.
- [ ] T-403 | TODO | — | nieobsługiwana wersja (po T-401)
      Kryteria: plik danych, który jest obiektem z `wersja` innym niż 2 albo bez `wersja`, albo nie jest ani
      listą, ani obiektem → każde polecenie kończy się komunikatem zawierającym słowo `wersja` i kodem 2,
      żaden plik się nie zmienia; test w `tests/`.

## Pytania do właściciela
- brak

## Pomysły (niezatwierdzone)
- brak

## Zrobione
- E1: lista, szukaj, dodaj, import, eksport, `--version`.
- E2: T-101…T-112 (ISBN, NFC/NFD, przetrzymane, lista z filtrami, eksport bezpieczny, zapis atomowy, walidacja roku,
  wypożyczenia, statystyki). T-107 kryteria v2: rok opcjonalny, sprawdzany zakres.
