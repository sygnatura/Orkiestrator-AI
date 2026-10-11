# Sprawdzenie portu v10

2026-10-11. Źródło: gałąź `claude/eloquent-meitner-98b5px`, pełny commit
`c45c525445034b7859f66dda158e2226489db4b2`. Klient dostępny w maszynie:
`codex-cli 0.159.2`; Python 3.12.14. Testy wykonywane na repozytoriach
tymczasowych, bez instalacji globalnej ani zmiany oryginałów.

## Wykonane

`python3 -B -m unittest discover -s codex/tests -v`: **17 passed, 0 failed**.

- Instalacja projektowa i użytkownika, zachowanie innych skills i CLAUDE.
- Dodanie czterech ról bez zastępowania uprawnień/ustawień Codex.
- Ponowna instalacja zachowuje ZESPOL i bajty niezmienionej konfiguracji.
- Aktualizacja archiwizuje pełną poprzednią instalację i zachowuje ZESPOL.
- Kolizje skill/roli, dowiązanie docelowe i katalog bez Git nie nadpisują danych.
- Helper: świeże `exec`, rzeczywisty katalog, instrukcje roli i literalny stdin,
  model/effort w argumentach, zachowany exit, brak raportu nie jest sukcesem.
- Recenzent/analityk zmieniający źródła, untracked plik lub commit z czystym
  statusem zostaje odrzucony. Istniejący raport pozostaje bez zmian.

Testy CLI helpera używają kontrolowanego zastępstwa procesu. Sprawdzają
argumenty, efekty w prawdziwym Git i rozpoznanie błędów; **nie udają pracy LLM**.

Dodatkowo cztery pliki ról TOML przeszły walidację względem publicznego
`codex-rs/core/config.schema.json`. Lokalne `codex -c ... features list`
przyjmuje dodaną rejestrację ról; multi_agent jest w tej wersji aktywne.
To nie jest sprawdzenie uruchomienia każdej roli ani dostępności różnych modeli.
Metadane YAML skilla/UI zostały sparsowane, jawne wywołanie jest ustawione.
SKILL.md przeszedł także publiczny walidator OpenAI `quick_validate.py`.
Wszystkie lokalne odsyłacze Markdown prowadzą do istniejących plików.
Oryginalne cztery dokumenty main sprawdzono bajtowo względem początkowego HEAD;
obecnie znajdują się w głównym `archiwum/` (orkiestrator ma dopisek `_v6`).
Po uporządkowaniu katalogów sprawdzono również zgodność bajtową całego
`claude/` i starszych wersji z przypiętym źródłem, odsyłacze Markdown oraz
ponownie 17 testów pakietu Codex. Zmieniono układ dokumentacji; kod
instalatora, skilla i ról pozostał bez zmian.

## Zgodność metody v10

Przeczytano SKILL, ZESPOL, ZLECENIA, SZABLONY, cztery definicje agentów,
README i ANALIZA z przypiętego źródła. SOURCE.json zawiera sumy źródeł.
Port zachowuje 13 obszarów procesu: start, konfigurację, przejęcie/nowy
projekt, wznowienie, pętlę, autonomię, routing, weryfikację, kontekst/handoff,
kierunek, dokumentację, zlecenia i kontakt. Zmiany mechaniki klienta opisano
w ANALIZA.md, zamiast kopiować nieobsługiwane polecenia Claude.

## Niewykonane

Nie wykonano pełnego pilota: przejęcia realnego aktywnego projektu Claude,
pracy modeli w czterech rolach, integracji produktu i powrotu kierownika
Claude. Repozytorium wejściowe jest pakietem instrukcji, bez takiego projektu.
Nie potwierdzono discovery skills przez app-server w tej maszynie.

Lokalna diagnostyka `codex doctor` ładuje konfigurację, ale raportuje brak
dostępu do endpointu inference (proxy HTTP CONNECT 403). Katalog runtime
Codex jest zamontowany tylko do odczytu. To ogranicza dodatkowe lokalne
sesje CLI w tej maszynie; nie zmieniano HOME/CODEX_HOME, uwierzytelniania,
ustawień zarządzanych ani weryfikacji TLS. Testy adaptera nie dowodzą
poprawnego działania całej pętli modeli w takim runtime.

Pilot po instalacji w swoim kliencie: jeden task ze wspólnego TODO po
Claude → wykonanie → świeża recenzja → testy integracji → checkpoint →
nowy wątek Codex → odczyt tego samego stanu przez Claude. Sprawdź także
W TOKU z nieznanym losem wykonawcy, recenzję już ukończonego SHA i brak
artefaktu z innej maszyny: żaden nie powinien powodować duplikatu implementacji.
