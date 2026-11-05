# Biblioteka domowa — opis systemu
Aktualizacja: po etapie E1, przed etapem E2

## Cel
Problem: domowa biblioteka (kilkaset książek, kilka osób pożyczających) chce prowadzić katalog z wiersza poleceń.
Użytkownik: jedna osoba, lokalnie, bez sieci.
Zrobione w E1: lista, szukanie, dodawanie, import i eksport CSV, `--version`.
E2: ISBN, wypożyczenia i raport przetrzymanych, filtrowanie i sortowanie listy, statystyki, bezpieczeństwo eksportu
i zapisu.
Kluczowe założenie: katalog mieści się w jednym pliku JSON — potwierdzone (dane/biblioteka.json).
Czego NIE robimy: baza danych, interfejs webowy, sieć, wielu użytkowników naraz.
Kryterium sukcesu: kryteria etapu E2 spełnione, testy przechodzą.

## Jak działa
`python -m biblioteka [--dane PLIK] <polecenie>` → `cli.py` parsuje argumenty, `magazyn.wczytaj()` czyta katalog,
polecenie wypisuje linie przez `formatuj()` albo zmienia katalog i zapisuje go `magazyn.zapisz()`.

## Format danych
Lista obiektów: `id` (int, unikalne, nowe = największe + 1), `tytul` (str), `autor` (str), `rok` (int albo null —
część starych pozycji nie ma roku), `wypozyczona_przez` (str albo null), `data_wypozyczenia` (ISO albo null;
w starych wpisach bywa null także przy wypożyczonej książce). Kolejność w pliku jest kolejnością wyświetlania.
Ten plik czytają też inne domowe skrypty, dlatego układ istniejących pól się nie zmienia.

## Moduły
- `cli.py` — polecenia `lista`, `szukaj`, `dodaj`, `eksport`, `import`, `formatuj()`.
- `magazyn.py` — `wczytaj()`, `zapisz()`, `nastepne_id()`.
- `wyszukiwanie.py` — `pasuje()` (fragment, bez wielkości liter), `szukaj()`.
- `eksport.py` — `do_csv()` (kolumny `id,tytul,autor,rok,wypozyczona_przez`).
- `importer.py` — `z_csv()` (kolumny `tytul,autor,rok`; `rok` może być pusty).

## Środowisko i koszty
- Bez LLM, bez usług zewnętrznych, bez sekretów. Dane tylko przykładowe.

## Stan funkcjonalny
- Działa: wszystko z E1. Nazwa pliku eksportu jest sprawdzana (sama nazwa, bez dowiązań).
- Znane braki: zapis nadpisuje plik w miejscu (przerwany zapis niszczy katalog); szukanie nie znajduje tekstu
  zapisanego w innej normalizacji Unicode (np. NFD z macOS); eksport nie chroni przed formułami w arkuszu.

## Pułapki
- Polskie znaki: wyjście w UTF-8 (`reconfigure` w `main`).
