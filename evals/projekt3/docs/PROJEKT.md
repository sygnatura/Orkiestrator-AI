# Biblioteka domowa — opis systemu
Aktualizacja: po etapie E2, przed etapem E3

## Cel
Problem: domowa biblioteka (kilkaset książek, kilka osób pożyczających) prowadzi katalog z wiersza poleceń.
Użytkownik: jedna osoba, lokalnie, bez sieci.
Zrobione: E1 (lista, szukanie, dodawanie, import i eksport CSV, `--version`), E2 (ISBN-13, NFC/NFD, wypożyczenia,
raport przetrzymanych, `lista` z filtrami i sortowaniem, statystyki, eksport bezpieczny dla arkuszy, zapis atomowy).
Dalej: E3 konfiguracja i formaty, E4 historia i rezerwacje, E5 jeden plik danych w formacie v2.
Kluczowe założenie: katalog mieści się w jednym pliku JSON — potwierdzone (dane/biblioteka.json).
Czego NIE robimy: baza danych, interfejs webowy, sieć, wielu użytkowników naraz.

## Jak działa
`python -m biblioteka [--dane PLIK] <polecenie>` → `cli.py` parsuje argumenty, `magazyn.wczytaj()` czyta katalog,
polecenie wypisuje linie przez `formatuj()` albo zmienia katalog i zapisuje go `magazyn.zapisz()` (plik tymczasowy
+ `os.replace`, poprzednia wersja w `<plik>.bak`).

## Format danych
Lista obiektów: `id`, `tytul`, `autor`, `rok` (int albo null — rok jest opcjonalny), `wypozyczona_przez`,
`data_wypozyczenia` (ISO albo null), opcjonalnie `isbn` (13 cyfr; klucz tylko, gdy ustawiony). Kolejność w pliku
jest kolejnością wyświetlania. Plik czytają też inne domowe skrypty przez `magazyn.wczytaj()` i `magazyn.zapisz()`
(API listy książek) — to API zostaje.

## Polecenia
`lista [--szczegoly] [--sortuj tytul|autor|rok] [--autor X] [--tylko-dostepne]`, `szukaj --autor/--tytul/--isbn`,
`dodaj`, `import`, `eksport`, `wypozycz ID --osoba X [--data]`, `zwroc ID`, `przetrzymane [--dzis] [--dni]`,
`statystyki`. Daty w argumentach i w pliku: ISO. Jedyne wyjście z datą: `lista --szczegoly` („od RRRR-MM-DD”).

## Środowisko i koszty
- Bez LLM, bez usług zewnętrznych, bez sekretów. Dane tylko przykładowe. Python 3.11+ (jest `tomllib`).

## Stan funkcjonalny
- Działa: wszystko z E1 i E2.

## Pułapki
- Polskie znaki: wyjście w UTF-8 (`reconfigure` w `main`).
- Rok bywa null; `data_wypozyczenia` bywa null także przy wypożyczonej książce.
