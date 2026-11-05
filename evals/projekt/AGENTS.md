# Katalog książek

Prosty CLI do przeglądania i eksportu katalogu książek zapisanego w pliku JSON. Opis systemu: docs/PROJEKT.md.
Plan i stan: docs/TODO.md.

## Polecenia
- Instalacja: `brak — sama biblioteka standardowa Pythona 3.11+`
- Uruchomienie: `python -m katalog lista`
- Testy: `python -m unittest discover -s tests` | jeden test: `python -m unittest tests.test_cli.CliTest.test_lista_wypisuje_wszystkie_tytuly`

## Środowisko i koszty
- Bez LLM, bez sieci, bez usług zewnętrznych. Dane przykładowe: `dane/katalog.json` (wolno używać w testach).
- Świeży worktree: nic do przygotowania.

## Struktura
- `katalog/` — kod: `cli.py` (polecenia i formatowanie), `dane.py` (odczyt/zapis JSON).
- `tests/` — testy jednostkowe (unittest).

## Konwencje
- Komunikaty dla użytkownika po polsku. Błąd użytkownika → komunikat na stderr i kod wyjścia 2.
- Commity: Conventional Commits z ID zadania, np. `feat(T-003): szukanie bez wielkości liter`.
- Gałęzie zadań: `task/T-NNN-nazwa`; main zawsze działa.

## Granice
- Zmieniaj tylko to, czego dotyczy zadanie. Pomysły spoza zakresu wpisz w raporcie.
- Najprostsze rozwiązanie spełniające kryteria, tylko biblioteka standardowa.
- Nie edytuj docs/TODO.md, docs/PROJEKT.md ani kryteriów zadania — prowadzi je kierownik.
- Nie osłabiaj, nie usuwaj i nie wyłączaj testów, żeby przeszły.
- Bez merge, push i przepisywania historii — robi to kierownik.

## Definition of Done
- Kryteria spełnione i pokazane dowodem (polecenie → wynik). Testy przechodzą.
- Nowe zachowanie ma test w `tests/`.
