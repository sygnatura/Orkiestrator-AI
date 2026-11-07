# Biblioteka domowa

CLI do prowadzenia domowego katalogu książek w pliku JSON: przeglądanie, wyszukiwanie, dodawanie, import i eksport
CSV. Opis systemu: docs/PROJEKT.md. Plan i stan: docs/TODO.md.

## Polecenia
- Instalacja: `brak — sama biblioteka standardowa Pythona 3.11+`
- Uruchomienie: `python -m biblioteka lista`
- Testy: `python -m unittest discover -s tests` | jeden test: `python -m unittest tests.test_cli.CliTest.test_formatuj`

## Środowisko i koszty
- Bez LLM, bez sieci, bez usług zewnętrznych. Dane przykładowe: `dane/biblioteka.json` (w testach używaj kopii
  w katalogu tymczasowym — polecenia zapisujące zmieniają plik danych).
- Świeży worktree: nic do przygotowania.

## Struktura
- `biblioteka/model.py` — `Ksiazka` i konwersja do/z JSON.
- `biblioteka/magazyn.py` — odczyt i zapis pliku danych (zapis atomowy z `.bak`).
- `biblioteka/wyszukiwanie.py` — dopasowanie tekstu (NFC, bez wielkości liter), `szukaj()`, polska kolejność.
- `biblioteka/eksport.py`, `biblioteka/importer.py` — CSV (eksport chroni przed formułami).
- `biblioteka/isbn.py`, `biblioteka/walidacja.py` — ISBN-13, rok, daty, znaki sterujące.
- `biblioteka/cli.py` — polecenia, `formatuj()`, obsługa błędów użytkownika.
- `tests/` — testy jednostkowe (unittest).

## Konwencje
- Komunikaty dla użytkownika po polsku. Błąd użytkownika → `BladUzytkownika` → komunikat na stderr i kod
  wyjścia 2; plik danych wtedy się nie zmienia.
- Daty w pliku danych i w argumentach w formacie ISO `RRRR-MM-DD`.
- Commity: Conventional Commits z ID zadania, np. `feat(T-301): historia wypożyczeń`.
- Gałęzie zadań: `task/T-NNN-nazwa`; main zawsze działa.

## Granice
- Zmieniaj tylko to, czego dotyczy zadanie. Pomysły spoza zakresu wpisz w raporcie.
- Najprostsze rozwiązanie spełniające kryteria, tylko biblioteka standardowa.
- Nie edytuj docs/TODO.md, docs/PROJEKT.md ani kryteriów zadania — prowadzi je kierownik.
- Nie osłabiaj, nie usuwaj, nie zmieniaj i nie wyłączaj istniejących testów; nowe testy dopisuj obok.
- Kryterium sprzeczne z istniejącym testem albo z innym zadaniem: nie obchodź po cichu — zgłoś w raporcie.
- Bez merge, push i przepisywania historii — robi to kierownik.

## Definition of Done
- Kryteria spełnione i pokazane dowodem (polecenie → wynik). Testy przechodzą.
- Nowe zachowanie ma test w `tests/`.
