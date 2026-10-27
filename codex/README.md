# Kierownik v12 dla Codex

Odpowiednik **kierownika v10 z gałęzi
`claude/eloquent-meitner-98b5px`**, commit
[`c45c525`](https://github.com/sygnatura/Orkiestrator-AI/commit/c45c525445034b7859f66dda158e2226489db4b2).
Zastępuje wcześniejszy port v6/SDD w tym folderze. Od v12 zespół obejmuje wielu
dostawców: wspólny rejestr runnerów `~/.kierownik/ZESPOL.md` (ten sam co dla kierownika
w Claude Code) mówi, kto i jakim modelem może wykonać rolę, a limit u jednego dostawcy
oznacza przejście do następnego. Od v11 instrukcje dla modeli
są po angielsku (mniej tokenów), a kierownik pisze do Ciebie po polsku; pliki
projektu, zlecenia i raporty zostają po polsku, statusy bez zmian.
[Wersja Claude](../claude/README.md) jest w `../claude/`, a
[starsze wersje](../archiwum/README.md) w `../archiwum/`.

Po `$kierownik` Codex sam prowadzi zatwierdzony etap: analizuje projekt,
deleguje wykonanie, uruchamia testy, odbiera niezależną recenzję, integruje
i wypycha sprawdzone zmiany według procesu repo. Drobiazgi może robić sam.
Pyta o decyzje właściciela i rzeczywiste ryzyko, zgodnie z autonomią v10.
Stan i wiedza pozostają w **tych samych `docs/PROJEKT.md` i `docs/TODO.md`**,
więc przełączenie Claude ↔ Codex nie wymaga nowej kolejki ani odtwarzania planu.

## Instalacja

Wymagane: Python **3.11+**, Git i klient Codex ze skills. Nie ma zależności
Python do instalowania. Najprościej z głównego katalogu repozytorium: `python3 install.py`
(aktualizuje też wersję Claude i usuwa skill `architekt` z pierwszego portu). Tylko Codex,
z katalogu `codex/` na swojej maszynie:

```bash
python3 install.py --user --register-agents
```

PowerShell:

```powershell
py .\install.py --user --register-agents
```

Instalacja raz na maszynę: skill w `~/.agents/skills/kierownik`, cztery role
TOML wewnątrz niego, brakujące wpisy `agents.kier-*` w `~/.codex/config.toml`.
Model, uprawnienia, MCP i inne ustawienia nie są zastępowane. Konflikt
istniejącej roli przerywa przed instalacją; nie nadpisujemy cudzej definicji.
Installer nie zmienia oryginalnych skills/agentów/settings Claude.

Alternatywnie tylko w jednym repozytorium:

```bash
python3 install.py --project /sciezka/do/projektu --register-agents
```

Wtedy instalacja trafia do `<projekt>/.agents/skills/kierownik` i dodaje role
do `<projekt>/.codex/config.toml`. Klient może wymagać zaufania repo, aby
odczytać projektowy config; installer nie nadaje zaufania automatycznie.
Nie instaluj obu wariantów o tej samej nazwie dla tego samego projektu;
sprawdź w kliencie, którą instalację skill faktycznie wybrano.

`--register-agents` jest opcjonalne: bez niego dostępne pozostają skill
i helper CLI, który odczytuje te same instrukcje ról. Jeśli klient blokuje
narzędzia native, to nie powód do wyłączenia sandboxa.

## Start i kontynuacja po Claude

Otwórz **nową sesję Codex w repozytorium prowadzonego projektu** i wpisz:

```text
$kierownik
```

Do przejęcia:

```text
$kierownik Przejmij projekt po kierowniku Claude v10–v12. Wznów z istniejących
PROJEKT.md, TODO.md i Git. Zachowaj aktywne zadania, statusy i zatwierdzony
plan; kontynuuj zapisany następny krok bez ponownego zlecania trwającej pracy.
```

Najlepiej wcześniej poprosić Claude o aktualny checkpoint/handoff w TODO.
Codex wykorzystuje te same statusy **TODO, W TOKU, DO SPRAWDZENIA, GOTOWE,
ZABLOKOWANE**, karty `docs/tasks/T-NNN.md`, DONE i ADR. Zachowuje istniejące
odpowiedniki. Nie wymaga osobnego PLAN/WORKFLOW/TASK/VERIFY/REPORT/REVIEW.

Ukryta pamięć Claude, niezapisane pliki i działające procesy na innej
maszynie nie przenoszą się automatycznie. Udostępnij aktualny checkout
lub utrwal/przenieś potrzebne artefakty. Kierownik ustala los istniejącego
wykonawcy przed kolejnym zleceniem. Po powrocie do Claude jego `/kierownik`
odczyta ten sam wspólny stan. `codex resume` dotyczy wyłącznie sesji Codex.

## Zespół i architektura Codex

| Rola | Zadanie |
|---|---|
| Kierownik | Główna sesja: stan, routing, testy, integracja, raport etapu |
| `kier-analityk` | Odczyt i krótkie streszczenia |
| `kier-wykonawca` | Jeden task w wskazanym katalogu, commit i raport |
| `kier-recenzent` | Świeży kontekst, kryteria/diff/scenariusz; bez napraw |
| `kier-architekt` | Plan, recenzja planu, specyfikacja i diagnoza |

Konkretnych modeli nie pinujemy. Rejestr `~/.kierownik/ZESPOL.md` (wzór:
[ZESPOL_WZOR.md](skills/kierownik/ZESPOL_WZOR.md), procedury:
[ZESPOL_PROCEDURY.md](skills/kierownik/ZESPOL_PROCEDURY.md), uruchamianie CLI:
[URUCHAMIANIE_CLI.md](skills/kierownik/URUCHAMIANIE_CLI.md)) mapuje klasy na modele
każdej Twojej subskrypcji, z priorytetem i stanem limitu. TOML ról początkowo
dziedziczy model; po rozpoznaniu można ustawić `model` i obsługiwany effort.
Każde zadanie recenzuje najpierw inna rodzina niż autor (Claude CLI, `agy`); gdy żadna nie jest dostępna, wyjątek v10 dopuszcza tę samą klasę/model
w świeżym kontekście z własnymi testami kierownika i zapisem odstępstwa.
Wykonawca pracuje domyślnie w klasie MOCNY; STANDARDOWY tylko przy prostych zadaniach (ryzyko NISKIE, typowa
trudność). `agy` bez sandboxa kierownik uruchamia dopiero po Twojej zgodzie zapisanej w rejestrze
z dopiskiem „(potwierdzona na tej maszynie)”.

Natywny subagent Codex nie jest automatycznie worktree Claude. Jeśli API
nie zapewnia osobnego katalogu, kierownik uruchamia świeże `codex exec`
przez [run_agent.py](skills/kierownik/scripts/run_agent.py), z określonym `-C`,
rolą w developer_instructions, zleceniem przez stdin i raportem/stderr do
plików. Nie ma ręcznego kopiowania zleceń przez właściciela jako domyślnej pętli.
Helper zachowuje kod CLI i odrzuca recenzję, która zmieniła HEAD/źródła/status.
Sandbox recenzenta dopuszcza lokalne wyniki testów, ale nie naprawianie kodu.

Lokalnie niezależne taski mogą działać w maksymalnie czterech osobnych
worktree; kierownik tworzy je jawnie od SHA bazy i scala pojedynczo.
W cloud istniejący checkout jest już izolowany: bez dodatkowego worktree,
chyba że właściciel zażąda, i tylko jeden zapisujący agent naraz. Proces
integracji/PR/ochrona gałęzi platformy nadal obowiązuje. Kod nie jest
GOTOWE przed dowodem z rzeczywiście zintegrowanej wersji.

Claude CLI, Antigravity i każde inne narzędzie dopisane do rejestru są
pełnoprawnymi runnerami: recenzja innej rodziny, druga opinia i ciągłość pracy
przy limicie. Ich aktualne flagi i autoryzację sprawdza kierownik (`--help`,
test dymny); limity zapisuje po komunikacie. Gdy limit ma sam Codex, kierownik
zapisuje stan i podaje polecenie kontynuacji w Claude Code. Pakiet nie zakłada, że są zainstalowane lub zalogowane, i nie
wyłącza ich zabezpieczeń. Uprawnienia klienta mogą wymagać osobnej decyzji
technicznej mimo autoryzacji pracy w skill.

## Aktualizacja i stan zespołu

```bash
python3 install.py --user --register-agents --upgrade
```

Odpowiednio użyj `--project` przy instalacji projektowej. Różniący się skill
bez `--upgrade` jest zachowany. Aktualizacja zachowuje stary lokalny ZESPOL.md
(źródło migracji do `~/.kierownik/ZESPOL.md`) i całą
poprzednią instalację w `.agents/backups/`, poza katalogiem discovery skills.
Własne zmiany instrukcji/role models porównaj z backupem i przenieś potrzebne
ustawienia; nowe role są wzorcami z modelami dziedziczonymi. Kierownik sprawdza
zgodność rejestru z faktycznie działającą konfiguracją, nie z samą tabelą.

Jeśli instalowałeś pierwszy port, zaktualizuj `kierownik` z `--upgrade`.
Starszego osobnego `$architekt` installer nie usuwa; v10 korzysta z roli
`kier-architekt`, a nie z tamtego skilla.

## Skróty i sprawdzenie

`status`, `dalej`, `pomysł:`, `zmiana:`, `zespół:`, `stop`, `handoff` to
wiadomości do kierownika. Nowy wątek + `$kierownik` odtwarza checkpoint;
nie potrzeba komend `/clear` ani `/autocompact` Claude.

```bash
python3 -B -m unittest discover -s tests -v
```

[VALIDATION.md](docs/VALIDATION.md) rozróżnia wykonane testy adaptera i konfiguracji
od niewykonanego pilota z modelem. [ANALIZA.md](docs/ANALIZA.md) wyjaśnia różnice
architektury; [SOURCE.json](docs/SOURCE.json) wskazuje dokładne źródła v10.
