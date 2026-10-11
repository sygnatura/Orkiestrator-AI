# Sprawdzenie pakietu Codex

Data: 2026-10-11. Dostępny klient: `codex-cli 0.159.2`.
Sprawdzenia wykonano w tym środowisku oraz w tymczasowych repozytoriach
pod `/tmp`. Nie instalowano skills do oryginalnego projektu ani globalnie.

## Potwierdzone

- Wszystkie cztery oryginalne dokumenty są identyczne bajtowo z HEAD
  `2fb079b3474d560618872de87c31fea7a5de6d1b`.
- Wszystkie lokalne odsyłacze Markdown w pakiecie prowadzą do istniejących plików.
- Dwie samowystarczalne kopie WORKFLOW są identyczne i zawierają niezmieniony
  oryginalny kontrakt SDD, poprzedzony adapterem dla Codex i starszego v6.
- Oba SKILL.md przeszły publiczny walidator OpenAI
  [quick_validate.py](https://github.com/openai/codex/blob/main/codex-rs/skills/src/assets/samples/skill-creator/scripts/quick_validate.py)
  uruchomiony na ich folderach. To sprawdza format, nie decyzje modelu.
- Instalacja przez `install.py --project <repo-testowe>` tworzy oba skills.
  Powtórzenie identycznej instalacji nie zmienia plików.
- Istniejący CLAUDE.md pozostaje bez zmian. Kolizja z inną wersją architekta
  przerywa przed kopiowaniem kierownika i zachowuje plik użytkownika.
- Katalog bez repozytorium Git oraz dowiązanie docelowego `.agents`
  są odrzucane bez zapisu poza projektem.
- Metadane `agents/openai.yaml` obu skills mają poprawny YAML,
  wskazują właściwą nazwę skill i wymagają jawnego wywołania.

## Niewykonane i ograniczenia

Wykrywanie przez `skills/list` w lokalnym app-server **nie zostało
potwierdzone**. Dostępny binarny klient próbuje zapisać swój stan w
`/run/codex-environment/codex-home`, który jest zamontowany tylko do odczytu.
Po skierowaniu bazy SQLite do `/tmp` start nadal wymaga zapisu
`installation_id` w tym chronionym katalogu. Nie zmieniano jego plików,
uprawnień, HOME ani CODEX_HOME. To ograniczenie dodatkowego procesu
CLI w tej maszynie, a nie wykryty błąd formatu skills.

Nie wykonano scenariuszy zachowania modelu z PRZEJECIE.md ani rzeczywistego
przejęcia projektu po Claude. Repozytorium źródłowe zawiera prompty i
kontrakt, bez prowadzonego projektu, kolejki, aktywnego taska lub raportów.
Kompatybilność przejęcia jest opisana w instrukcjach; nie jest potwierdzonym
wynikiem kontynuacji konkretnego projektu. Weryfikację wykonaj po instalacji
w kliencie Codex i na kopii prowadzonego repozytorium.
