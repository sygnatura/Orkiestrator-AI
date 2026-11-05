# Katalog książek — opis systemu
Aktualizacja: stan wyjściowy evala, przed etapem E1

## Cel
Problem: domowa biblioteka chce przeglądać i eksportować swój katalog książek z wiersza poleceń.
Użytkownik: jedna osoba, lokalnie, bez sieci.
MVP: lista (ze stronicowaniem), szukanie po autorze, eksport do CSV, czytelny format linii.
Kluczowe założenie: katalog mieści się w jednym pliku JSON — potwierdzone (dane/katalog.json).
Czego NIE robimy: edycja katalogu z CLI, baza danych, interfejs webowy, sieć.
Kryterium sukcesu: kryteria etapu E1 spełnione, testy przechodzą.

## Jak działa
`python -m katalog [--dane PLIK] <polecenie>` → `katalog/cli.py` parsuje argumenty, `dane.wczytaj()` czyta
listę książek z JSON, polecenie wypisuje linie przez `formatuj()` albo zapisuje plik eksportu.

## Format danych
Lista obiektów: `tytul` (str), `autor` (str), `rok` (int albo null), `wypozyczona` (bool). Kolejność w pliku
jest kolejnością wyświetlania.

## Moduły
- `katalog/cli.py` — polecenia `lista`, `szukaj`, `eksport` i `formatuj()`.
- `katalog/dane.py` — odczyt i zapis pliku JSON.

## Środowisko i koszty
- Bez LLM, bez usług zewnętrznych, bez sekretów. Dane tylko przykładowe.

## Stan funkcjonalny
- Działa: `lista` bez stronicowania, `szukaj` z pełnym, dokładnym nazwiskiem, `eksport` do prostego pliku tekstowego.
- Nie działa: stronicowanie (`--strona 1` pokazuje drugą stronę), brak `--version`.

## Pułapki
- Polskie znaki: wyjście w UTF-8 (`sys.stdout.reconfigure`).
