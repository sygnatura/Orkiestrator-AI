# ZESPÓŁ v10 — Codex, klasy i stan tej instalacji

Stan wypełnienia: NIEWYPEŁNIONY. Kierownik ustala fakty na starcie, bez
blokowania pracy dostępnym modelem. Ten plik zachowuj przy aktualizacji.
Nie kopiuj tu aliasów ani limitów z instalacji Claude jako ustawień Codex.

## Klasy modeli

Jedyny opis mapowania klasa → model. Identyfikatory wpisuj po sprawdzeniu
modeli dostępnych w kliencie lub po informacji właściciela; nie zakładaj
istnienia automatycznych aliasów na najnowszą generację.

| Klasa | Model dostępny w tym kliencie | Dostępność / data / ograniczenia |
|---|---|---|
| NAJMOCNIEJSZY | do ustalenia; na start dziedziczony | NIEZNANE |
| MOCNY | do ustalenia; na start dziedziczony | NIEZNANE |
| STANDARDOWY | model sesji, jeśli brak innego potwierdzonego | NIEZNANE |
| SZYBKI | do ustalenia; bez pozornego przypisania | NIEZNANE |

Domyślne role działają bez `model`, dziedzicząc konfigurację Codex. To tryb
startowy, a nie dowód użycia czterech różnych modeli. Dla jednej dostępnej
klasy obowiązuje wyjątek v10: świeża recenzja i niezależne testy kierownika,
z zapisanym odstępstwem. Zmiana effortu nie oznacza zmiany modelu.

## Role i effort

| Rola | Definicja | Preferowana klasa | Początkowy effort |
|---|---|---|---|
| Kierownik | główna sesja `$kierownik` | MOCNY | ustawienie sesji |
| Analityk | roles/kier-analityk.toml | STANDARDOWY; rutyna SZYBKI | medium |
| Wykonawca | roles/kier-wykonawca.toml | STANDARDOWY; trudne MOCNY | medium |
| Recenzent | roles/kier-recenzent.toml | wyżej niż autor | high |
| Architekt | roles/kier-architekt.toml | NAJMOCNIEJSZY | high |

Effort/model faktycznie działają w polach TOML ról lub obsługiwanych polach
wywołania. Tabela jest opisem, nie konfiguracją wykonawczą. Aktualizując model
roli, uzupełnij `model` w jej lokalnym TOML i odnotuj zmianę tutaj. Native
może wymagać nowej sesji/reload; helper CLI czyta TOML przy każdym uruchomieniu.
Tymczasowe `--model`/`--effort` helpera mają pierwszeństwo tylko w danym zleceniu.
Używaj poziomów obsługiwanych przez konkretny model; odrzucony effort popraw
zgodnie z jego możliwościami, bez zgadywania modelu.

Natywne role `kier-*`: NIEZWERYFIKOWANE. Obsługa świeżego kontekstu/katalogu:
NIEZWERYFIKOWANA. Przy braku per-agent cwd wykonawca działa przez CLI.
Bezpiecznik kontekstu: nie kopiuj tokenowego progu Claude; sprawdź aktualny
klient i pojemność modelu. W Codex punkty kontrolne i nowy wątek są podstawą.

## Routing, dostępność i zapas

Nowy model nie zmienia procesu: przypisz go do klasy na podstawie możliwości
i kosztu, potwierdź nieznaną istotną zmianę z właścicielem i uzupełnij role.
Limit: zanotuj źródło komunikatu, czas resetu jeśli podany, wybierz dostępny
zamiennik. Nie wymyślaj czasu ani planu abonamentowego. Właściciel może
wyłączyć narzędzie; nie testuj ani nie używaj wtedy jego CLI.

| System | Stan | Test dymny / polecenie używane na tej maszynie |
|---|---|---|
| Codex native | do sprawdzenia w bieżącym kliencie | role/fresh context/cwd |
| Codex CLI | do sprawdzenia | `codex exec --help`, helper scripts/run_agent.py |
| Claude CLI (inna rodzina / zapas) | NIEZNANY | sprawdź `claude --help`, tryb nieinteraktywny i uprawnienia |
| Antigravity CLI lub inny zapas | NIEZNANY | aktualne `--help`; nie kopiuj flag obchodzących uprawnienia |

Stany: dostępny | niedostępny do <czas, jeśli znany> | wyłączony przez
właściciela | NIEZNANY. Zapas testuj w tymczasowym Git tym samym poleceniem,
którego potem użyjesz. Plik OK, git status, exit i stderr są wymaganym
dowodem. Test dotyczy limitów agentów, a nie zgody na płatne API aplikacji.

## Wykonanie CLI

Katalog roli przygotowuje kierownik: lokalny wykonawca w task worktree,
recenzent w odłączonym worktree ocenianego SHA lub odblokowanym katalogu
autora. Cloud bez żądania worktree: istniejący checkout, sesje kolejno.
Recenzenta uruchom dopiero po przygotowaniu zależności/testowej konfiguracji.
Worktree to organizacja Git, nie kontrola dostępu do całej maszyny.

Przykład POSIX (ścieżki podstaw rzeczywistymi, ujętymi w cudzysłowy):

```bash
python3 "$SKILL_DIR/scripts/run_agent.py" \
  --role kier-wykonawca --cwd "$TASK_DIR" \
  --prompt "$ORDER_FILE" --result "$RESULT_FILE"
```

PowerShell:

```powershell
py "$SkillDir/scripts/run_agent.py" --role kier-wykonawca --cwd $TaskDir `
  --prompt $OrderFile --result $ResultFile
```

To zwykłe zmienne ścieżek ustalone w sesji, nie zmienne wbudowane Codex.
Helper wstawia instrukcje roli, przekazuje zlecenie przez stdin i loguje
stderr do `<wynik>.err`. Nie używa powłoki do interpretacji prompta.
Zachowuje exit CLI; recenzja zmieniająca HEAD/źródła/status zostaje odrzucona.
Nie nadpisuje istniejących wyników. Pełne zlecenia i logi trzymaj w ignorowanym
`.kierownik/`, a dowody i wersje w TODO/kartach. Wynik CLI nie zastępuje
kontroli kierownika ani dowodu zintegrowanej wersji.

## Historia zmian
- <data> — <zmiana, źródło informacji, powód, rzeczywisty model/effort>
