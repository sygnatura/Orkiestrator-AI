# ZESPÓŁ — klasy modeli, role, zapas i limity na tej maszynie

Wspólny dla wszystkich projektów na tej maszynie. Wypełnia i aktualizuje kierownik (SKILL.md, sekcje 2 i 7);
właściciel może edytować ręcznie. To jedyny plik zestawu, w którym stoją nazwy konkretnych modeli.

Stan wypełnienia: NIEWYPEŁNIONY   (kierownik zmienia na: WYPEŁNIONY <data>)


## Klasy modeli

SKILL.md, README.md i szablony mówią o KLASACH — drabinie siły SZYBKI < STANDARDOWY < MOCNY < NAJMOCNIEJSZY.
Tabela niżej mówi, jaki alias Claude Code stoi dziś za każdą klasą. Aliasy wskazują zawsze najnowszy model
danej linii, więc nowe wydanie w tej samej linii nie wymaga żadnej zmiany; tabela starzeje się dopiero, gdy
Anthropic doda nową linię lub alias, wycofa którąś albo zmieni zalecane poziomy effort.

| Klasa | Alias (`model:` we frontmatter agenta i parametr `model` przy wywołaniu) | Wskazuje dziś na (stan na <data>) | Uwagi |
|---|---|---|---|
| NAJMOCNIEJSZY | `fable` | <np. Fable 5.1> | w `/model` istnieje też `best` (= najmocniejszy dostępny), ale nie działa we frontmatter subagentów |
| MOCNY | `opus` | <np. Opus 5.5> | domyślny model planu; domyślny effort tej linii w Claude Code: medium |
| STANDARDOWY | `sonnet` | <np. Sonnet 5.5> | |
| SZYBKI | `haiku` | <np. Haiku 4.5> | nie obsługuje pola effort — wywołanie `kier-analityk` z `model: haiku` niezweryfikowane [?]; gdy zawiedzie, zostań przy STANDARDOWY |

Kolumnę „Wskazuje dziś na” kierownik wypełnia tym, co pokazuje `/model` (wpisuje właściciel) — wyłącznie
do wiedzy; nigdzie poza tą tabelą nazw wersji nie zapisujesz.


## Role i effort

Działający model i effort każdej roli to pola `model:` i `effort:` we frontmatter `~/.claude/agents/kier-*.md`.
Tabela je streszcza i musi być z nimi zgodna — zmieniasz jedno, zmieniasz drugie. Kiedy wywołać rolę w innej
klasie niż domyślna: SKILL.md, sekcja 7 (parametr `model` przy wywołaniu).

| Rola | Subagent | Klasa domyślna (`model:`) | `effort:` | Inna klasa przy wywołaniu |
|---|---|---|---|---|
| Kierownik | wątek główny `/kierownik` | MOCNY (`/model opus`) | effort sesji: domyślny modelu; `/effort high` ustawia właściciel, gdy decyzje są płytkie | — |
| Analityk | `kier-analityk` | STANDARDOWY (`sonnet`) | medium | duże repo, trudne pytanie → MOCNY; trywialne → SZYBKI |
| Wykonawca | `kier-wykonawca` | STANDARDOWY (`sonnet`) | medium | trudne, ryzykowne, po nieudanej rundzie → MOCNY |
| Recenzent | `kier-recenzent` | MOCNY (`opus`) | high | autor w klasie MOCNY (także kierownik), weryfikacja celu etapu → NAJMOCNIEJSZY |
| Architekt | `kier-architekt` | NAJMOCNIEJSZY (`fable`) | high | recenzja planu: druga, świeża instancja w klasie MOCNY |

Mechanika Claude Code, od której zależy ta tabela:
- `model` nadpisujesz przy każdym wywołaniu subagenta (parametr narzędzia Agent; aliasy z tabeli klas).
- `effort` jest TYLKO we frontmatter (albo dziedziczony z sesji, gdy pola brak) — przy wywołaniu nie da się go
  zmienić. Poziomy wyżej są dobrane pod domyślną klasę roli i zostają po zmianie klasy przy wywołaniu.
  Potrzebujesz głębszej pracy → zmień klasę, nie effort, i napisz w zleceniu, co jest trudne i dlaczego.
  Trwałą zmianę effortu roli robisz w pliku agenta — tylko po zaobserwowanym problemie albo zmierzonym zysku —
  z powodem w „Historii zmian”.
- Poziomy effort nie znaczą tego samego między generacjami modeli; po zmianie modelu za aliasem sprawdź
  zalecenia producenta i w razie potrzeby popraw frontmatter.

Bezpiecznik kontekstu kierownika: `/autocompact <próg>` wyraźnie poniżej pełnego okna modelu kierownika —
dziś `/autocompact 400k` (stan na <data>; przy zmianie modelu lub wariantu okna przelicz i odnotuj).

Stan subagentów `kier-*`: zainstalowani [?]   (kierownik sprawdza na starcie sesji i wpisuje TAK/NIE z datą)


## Gdy klasa jest niedostępna albo pojawia się nowy model

Sygnał: właściciel pisze `zespół: …` (np. „fable wymaga credits”, „wyszedł nowy model X”, „nie używaj codex”)
albo kierownik dostaje komunikat o limicie. Aliasy i dopisek „Requires usage credits” widać w `/model`,
które wpisuje właściciel.

1. **NAJMOCNIEJSZY poza limitem planu** („Requires usage credits”, limit, brak w planie) → zastępuje go MOCNY:
   - w `~/.claude/agents/kier-architekt.md` zmień `model: fable` → `model: opus` (effort zostaw); w bieżącym
     wątku dodatkowo podawaj `model: opus` przy wywołaniu `kier-architekt` (parametr ma pierwszeństwo);
   - tam, gdzie SKILL.md sekcja 7 każe podać klasę NAJMOCNIEJSZY (recenzja pracy klasy MOCNY, weryfikacja celu
     etapu), podawaj alias klasy MOCNY; niezależność recenzji daje wtedy świeży kontekst i testy uruchomione
     przez Ciebie (wyjątek w SKILL.md, sekcja 7), a w TODO.md i raporcie etapu dopisujesz „recenzja tą samą klasą”;
   - zapisz stan (tabela klas, „Limity”) i wpis w „Historii zmian”; gdy klasa wróci — cofnij i też odnotuj.
2. **Nowa wersja w istniejącej linii** (np. kolejny Opus): alias wskazuje ją automatycznie — w agentach nic nie
   zmieniasz. Popraw kolumnę „Wskazuje dziś na” i datę; jeśli producent zmienił zalecany effort dla tej linii,
   popraw `effort:` u agentów tej klasy.
3. **Nowa linia, nowy alias albo zmiana kolejności siły**: przypisz model do klasy (siła i koszt względem
   pozostałych) i potwierdź z właścicielem; zmień alias w tabeli klas, `model:` we frontmatter agentów tej
   klasy (alias albo pełne ID modelu) oraz polecenie `/model` w README, jeśli zmienił się alias klasy MOCNY.
   Sprawdź effort (pkt 2).
4. Każda zmiana → wpis w „Historii zmian”.


## Zapas i recenzja innej rodziny

Używane tylko: (a) gdy Claude jest niedostępny, (b) do recenzji innej rodziny w przypadkach z SKILL.md,
sekcja 7. Wybór: narzędzie ze stanem `dostępny`; jeśli oba dostępne — to z większym zapasem limitu. Narzędzie
ze stanem `wyłączony przez właściciela` pomijasz całkowicie (bez testu dymnego i bez użycia).

Katalogi: `<repo>` = bezwzględna ścieżka projektu. `<katalog roli>`: wykonawca — `<repo>/.kierownik/wt/T-NNN`
(worktree gałęzi zadania, tworzy kierownik); recenzent — `<repo>/.kierownik/wt/T-NNN-rec` (odłączony worktree
na commicie gałęzi: `git worktree add --detach <repo>/.kierownik/wt/T-NNN-rec task/T-NNN-nazwa`, bo ta sama
gałąź nie może być wyewidencjonowana w dwóch worktree; tworzenie i sprzątanie: SKILL.md, sekcja 7).

Zlecenie (szablon A/B z SKILL.md) zapisz do `<repo>/.kierownik/T-NNN-<rola>.zlecenie.md` i przekaż z pliku,
nie inline — odwrotne apostrofy i cudzysłowy ze zlecenia wklejone w wiersz poleceń wykonałaby powłoka albo
przerwałyby argument. Polecenia niżej są dla powłoki POSIX; w PowerShell użyj
`agy -p (Get-Content -Raw <plik>) …` oraz `Get-Content <plik> | codex exec … -`.

| Narzędzie | Rodzina | Polecenie nieinteraktywne | Zweryfikowane na tej maszynie |
|---|---|---|---|
| Antigravity CLI (`agy`) | Google | `cd <katalog roli> && agy -p "$(cat <repo>/.kierownik/T-NNN-<rola>.zlecenie.md)" --dangerously-skip-permissions > <repo>/.kierownik/T-NNN-<rola>.md 2> <repo>/.kierownik/T-NNN-<rola>.err`; wybór modelu flagą z `agy --help` | [?] |
| Codex CLI | OpenAI | `codex exec -C <katalog roli> -s workspace-write -o <repo>/.kierownik/T-NNN-<rola>.md - < <repo>/.kierownik/T-NNN-<rola>.zlecenie.md 2> <repo>/.kierownik/T-NNN-<rola>.err` (recenzja bez zapisu: `-s read-only`; model: `-m <model>` wg `codex exec --help`) | [?] |

Uwagi:
- `agy` bez `--dangerously-skip-permissions` w trybie `-p` po cichu pomija polecenia powłoki (kod 0,
  komunikat tylko na stderr) — zawsze czytaj `.err`.
- Tryb bez pytań = agent może wykonać dowolne polecenie na całej maszynie; worktree porządkuje zmiany
  w repozytorium, ale nie ogranicza dostępu. Codex ma własny sandbox (`-s`), `agy` nie. Dlatego: tylko
  w katalogu roli, bez sekretów w zleceniu, po przebiegu `git status` i `git log` worktree oraz plik `.err`.
- Po recenzji CLI w odłączonym worktree: `git status --short` ma być pusty, a `git rev-parse HEAD` równy
  `git rev-parse task/T-NNN-nazwa` (commit na odłączonym HEAD nie zmienia `git status`) — inaczej odrzuć
  werdykt. Na koniec `git worktree remove <repo>/.kierownik/wt/T-NNN-rec` (`--force`, gdy zostały pliki).
  Codex z `-s read-only` może zamiast tego recenzować w katalogu worktree autora (ścieżka z jego raportu).


## Limity

| System | Plan | Stan |
|---|---|---|
| Claude | Max | dostępny |
| Google / Antigravity | <…> | <dostępny / niedostępny do … / wyłączony przez właściciela> |
| OpenAI / Codex | <…> | <dostępny / niedostępny do … / wyłączony przez właściciela> |

Stan: `dostępny` | `niedostępny do <data godzina>` | `wyłączony przez właściciela`. Dwa pierwsze wpisuje
kierownik (po komunikacie o limicie albo po informacji od właściciela); trzeci tylko właściciel — kierownik
takiego narzędzia nie testuje i nie używa.


## Historia zmian
- <data> — <co zmieniono i dlaczego>
