# Kierownik projektu AI — instrukcja (v13, wielu dostawców)

Skill dla Claude Code, który robi z sesji Claude kierownika technicznego projektu: rozumie system,
prowadzi plan rozwoju i stan w repozytorium, deleguje pracę zespołowi subagentów Claude (model
dobierany do zadania spośród klas od najszybszego do najmocniejszego), niezależnie weryfikuje, scala
i wypycha to, co zweryfikowane, a do Ciebie wraca z raportem po etapie albo z decyzją, która należy do
Ciebie.

Od v12 zespół to nie tylko Claude. Kierownik wybiera wykonawców i recenzentów z **rejestru runnerów**
(`~/.kierownik/ZESPOL.md`, jeden na maszynę, wspólny dla kierownika w Claude Code i w Codex): subagenci
Claude, Codex CLI, Antigravity `agy` i każde narzędzie, które dopiszesz. Role mają wymagania (klasa
modelu, preferowana rodzina), a nie przypisane narzędzia. Wyczerpany limit u jednego dostawcy oznacza
przejście do następnego, a nie zatrzymanie projektu. Nowa lub anulowana subskrypcja to jedna zmiana
w rejestrze.

Instrukcje dla modeli (skill i subagenci) są od v11 po angielsku — to mniej tokenów w każdej sesji
i każdym wywołaniu subagenta. Kierownik pisze do Ciebie wyłącznie po polsku, a pliki projektu
(`docs/`, `AGENTS.md`), zlecenia i raporty zostają po polsku. Statusy i pola zleceń są te same co
w v10, więc istniejące projekty działają bez migracji.

## Instalacja (raz na maszynę)

Najprościej z głównego katalogu repozytorium: `python3 install.py` (najpierw `--dry-run`). Instalator
instaluje albo aktualizuje wszystko, rozpoznaje pliki ze starszych wersji, kasuje zbędne i robi kopię
zapasową — szczegóły w [README repozytorium](../README.md#instalacja-i-aktualizacja--jedno-polecenie).
Ręcznie, z katalogu `claude/`, skopiuj skill i subagentów:

    # Linux / macOS
    mkdir -p ~/.claude/skills ~/.claude/agents
    cp -r kierownik ~/.claude/skills/ && cp agents/*.md ~/.claude/agents/
    # Windows (PowerShell)
    New-Item -ItemType Directory -Force $HOME\.claude\skills, $HOME\.claude\agents | Out-Null
    Copy-Item -Recurse .\kierownik $HOME\.claude\skills\
    Copy-Item .\agents\*.md $HOME\.claude\agents\

W każdym projekcie na tej maszynie masz polecenie `/kierownik` i subagentów `kier-*`.
Opis skilla nie obciąża innych sesji (`disable-model-invocation: true`); krótkie opisy czterech
subagentów są widoczne w każdej sesji — to kilka linii.

### Aktualizacja zestawu

Zalecane: `python3 install.py` z głównego katalogu repozytorium. Ręcznie: kopiuj instrukcje i agentów. Stan maszyny jest w `~/.kierownik/ZESPOL.md`, poza zestawem.

    # Linux / macOS
    cp -r kierownik/. ~/.claude/skills/kierownik/ && cp agents/*.md ~/.claude/agents/
    # Windows (PowerShell)
    Copy-Item -Recurse -Force .\kierownik\* $HOME\.claude\skills\kierownik\
    Copy-Item .\agents\*.md $HOME\.claude\agents\

Aktualizacja z v10/v11: stary `~/.claude/skills/kierownik/ZESPOL.md` zostaje na miejscu (polecenia wyżej
go nie nadpisują). Przy pierwszym starcie kierownik przeniesie z niego aliasy, limity i Twoje decyzje do
rejestru `~/.kierownik/ZESPOL.md` i zapyta raz o modele, klasy i priorytety pozostałych dostawców.
Jeśli w `~/.claude/agents/kier-*.md` zmieniałeś `model:`, po skopiowaniu agentów przywróć tę zmianę.

## Użycie

1. Otwórz Claude Code w katalogu projektu i ustaw model kierownika: `/model opus` (alias — zawsze
   najnowszy model tej linii). `/model` nie zmienia effortu — zostaje domyślny dla modelu (Opus: medium)
   i to wystarcza na co dzień, bo kierownik działa przez cały wątek, a high podnosi koszt każdej tury.
   `/effort high` (potem z powrotem `/effort medium`) włącz na przejęcie projektu, plan i akceptację etapu,
   „plan pod znakiem zapytania”, trudną diagnozę albo gdy we wpisach „przydział” widzisz powtarzające się błędy. Opcjonalnie bezpiecznik kontekstu: `/autocompact` z progiem poniżej
   pełnego okna modelu (dziś `/autocompact 200k`; wartość prowadzi rejestr `~/.kierownik/ZESPOL.md`). Wymaga
   Claude Code ≥ 2.1.221 i zapisuje się w Twoich ustawieniach użytkownika, więc działa we wszystkich projektach.
   Wszystko to możesz zapisać raz w `settings.json` (wzór: `kierownik/SZABLONY.md`, sekcja 8).
2. Wpisz `/kierownik`.
3. Pierwszy raz na maszynie: kierownik wykryje narzędzia innych dostawców (`codex`, `agy` i inne, które
   wskażesz; są opcjonalne — bez nich cała pętla działa na Claude), każde obecne sprawdzi `--help`
   i krótkim testem dymnym w tymczasowym repozytorium, tym samym poleceniem, którego potem używa (test zużywa
   odrobinę limitu; `agy` dopiero po Twojej zgodzie na tryb bez sandboxa — patrz „Bezpieczeństwo”), zapyta Cię
   jednym pytaniem o modele każdej subskrypcji, ich klasy, priorytety i limity, i zapisze wszystko
   w rejestrze `~/.kierownik/ZESPOL.md`.
4. Pierwszy raz w projekcie:
   - **istniejący projekt** — trzech analityków równolegle mapuje kod, kierownik uruchamia testy
     (jeśli są bezpieczne), pisze `docs/PROJEKT.md`, `AGENTS.md`, `CLAUDE.md`, a architekt przygotowuje
     plan etapów, który kierownik zapisuje w `docs/TODO.md`; dostajesz jedną wiadomość: obraz projektu,
     cel/MVP do potwierdzenia, plan etapu;
   - **nowy projekt** — do 5 pytań z proponowanymi odpowiedziami, potem plan od architekta.
5. Po Twojej akceptacji kierownik pracuje sam do końca etapu.

**Nowy wątek** (po etapie albo gdy kierownik poprosi): `/clear`, potem `/kierownik`.
Nic nie kopiujesz — stan jest w plikach.

## Zespół

| Rola | Kto | Co robi |
|---|---|---|
| Kierownik | wątek główny (`/kierownik`) | rozumie projekt, prowadzi plan, deleguje, weryfikuje, scala |
| Analityk | `kier-analityk` | czyta kod, logi i dokumenty, zwraca streszczenia |
| Wykonawca | `kier-wykonawca` | implementuje jedno zadanie w osobnym worktree |
| Recenzent | `kier-recenzent` | niezależna weryfikacja zmiany albo celu etapu |
| Architekt | `kier-architekt` | plan, recenzja planu, przejęcie, specyfikacje, diagnozy, decyzje |
| Inne rodziny | Codex `codex exec`, Antigravity `agy`, inne z rejestru | domyślna recenzja pracy klasy MOCNY, druga opinia, wykonawstwo, gdy Claude ma limit |

Modele są opisane klasami: SZYBKI < STANDARDOWY < MOCNY < NAJMOCNIEJSZY, porównywalnymi między
dostawcami. Który model którego dostawcy stoi za którą klasą, priorytety subskrypcji, limity i
sprawdzone polecenia CLI — to jedno miejsce: rejestr `~/.kierownik/ZESPOL.md`. Domyślnie: kierownik,
recenzent, architekt i wykonawca w klasie MOCNY, analityk w STANDARDOWY. Proste zadania (ryzyko NISKIE,
typowa trudność, kryteria sprawdzalne jednym poleceniem) kierownik daje wykonawcy w STANDARDOWY (Sonnet).
Powód: Opus kosztuje dziś tylko dwa razy więcej niż Sonnet, a każda nieudana runda poprawek to dodatkowa
recenzja i kontekst kierownika — liczy się koszt ukończonego zadania ([ANALIZA.md](ANALIZA.md), decyzja 14).
Przy każdym wywołaniu kierownik może też podnieść effort (Claude Code ≥ 2.1.292).
Klasę NAJMOCNIEJSZY (dziś Fable) kierownik zostawia na rzadkie, decydujące kroki: plan etapu, przejęcie
projektu, trudną diagnozę, rozstrzygnięcie sprzecznego werdyktu i weryfikację celu etapu.

Niezależność weryfikacji: recenzent startuje ze świeżym kontekstem i widzi tylko kryteria, diff
i polecenia — nie rozumowanie autora — i jest albo z innej rodziny, albo o klasę wyżej. Każde zadanie
recenzuje najpierw inna rodzina niż autor (np. pracę Sonneta — Codex), według priorytetu i limitu;
gdy żadna nie jest dostępna, recenzuje Opus — o klasę wyżej albo w trybie „recenzja tą samą klasą”
z własnymi testami kierownika. Przy każdym zleceniu kierownik wpisuje w `TODO.md` jeden wpis „przydział”:
kto był autorem, jakie ryzyko, czego reguła wymaga i kogo wybrał — od razu widać, czy trzyma się
zasad. Inna rodzina jest dodawana zawsze przy zmianach dotyczących bezpieczeństwa,
danych, pieniędzy lub kontraktów zewnętrznych, przy sprzecznych sygnałach, po dwóch nieudanych rundach
poprawek i przy weryfikacji celu etapu kluczowego dla MVP.

**Gdy kończy się limit.** Kierownik zapisuje limit w rejestrze — przy modelu, jeśli komunikat go
wskazuje (np. tylko Fable), inaczej przy całej subskrypcji — i wysyła to samo zlecenie
następnemu, który spełnia wymagania roli. Jeśli żadnego nie ma, sięga o klasę wyżej, a dopiero
potem obniża wymaganie o jeden krok i zapisuje to w `TODO.md`. Projekt zatrzymuje się dopiero, gdy nikt nie może wykonać pozostałej pracy
albo limit ma dostawca samego kierownika — wtedy dostajesz stan zapisany w Gicie i gotowe polecenie
do kontynuacji w drugim narzędziu (Codex: `$kierownik Wznów…`).

Niezależne zadania etapu idą równolegle (do 4 wykonawców naraz, każdy w swoim worktree).

**Nowe modele i subskrypcje.** Aliasy Claude (`opus`, `sonnet`, `haiku`, `fable`) wskazują zawsze
najnowszy model swojej linii, więc po nowej wersji nic nie zmieniasz. Wszystko inne zgłaszasz jednym
zdaniem, a kierownik aktualizuje rejestr: `zespół: wyszedł nowy model <nazwa>` (zaproponuje klasę),
`zespół: mam <dostawca>` (wykryje CLI, sprawdzi `--help`, zrobi test dymny), `zespół: rezygnuję z <dostawca>`,
`zespół: oszczędzaj <dostawca>` (niższy priorytet), `zespół: <alias> wymaga credits`.

## Bezpieczeństwo

CLI innych dostawców działają w trybie bez pytań: Codex w sandboxie `-s workspace-write`, a `agy`
działa bez pytań tylko z `--dangerously-skip-permissions`, czyli bez sandboxa. Dlatego kierownik pyta Cię
o zgodę raz, przy zakładaniu rejestru (albo przed pierwszym użyciem `agy`), i zapisuje odpowiedź
w `~/.kierownik/ZESPOL.md` z dopiskiem „(potwierdzona na tej maszynie: <hostname>)”. Bez zgody `agy` nie jest
testowany ani używany; zgodę cofa `zespół: agy bez trybu bez sandboxa`. Zgoda przeniesiona ze starszego
wzoru rejestru (v12) nie liczy się — kierownik zapyta ponownie. Worktree zadania (`.kierownik/wt/T-NNN`)
porządkuje zmiany w repozytorium, ale nie ogranicza dostępu `agy` do maszyny. Jeśli masz na tej maszynie cenne dane poza repozytorium, uruchamiaj Claude Code
w kontenerze albo wyłącz `agy`: napisz `zespół: nie używaj agy` albo w `~/.kierownik/ZESPOL.md` wpisz
w jego wierszu stan `wyłączony przez właściciela` — kierownik go wtedy nie testuje i nie używa. Kierownik nie przekazuje sekretów w zleceniu i po każdym przebiegu sprawdza `git status` oraz
stderr. Reguły `deny` z `settings.json` (SZABLONY.md, sekcja 8) blokują czytanie `.env` także
subagentom.

## Co powstaje w projekcie

    AGENTS.md              zasady dla wszystkich agentów (polecenia, środowisko i koszty, granice, Definition of Done)
    CLAUDE.md              @AGENTS.md (+ ewentualne różnice dla Claude Code)
    docs/PROJEKT.md        jak działa system: cel, moduły, przepływ, środowisko i koszty, stan funkcjonalny
    docs/TODO.md           plan rozwoju i stan — tu patrzysz, gdy chcesz wiedzieć „gdzie jesteśmy”
    docs/DONE.md           archiwum zrobionych zadań z dowodami
    docs/tasks/            plany zadań ryzykownych / wielosesyjnych
    docs/decisions/        decyzje trudne do odwrócenia (ADR)
    .claude/worktrees/     worktree subagentów Claude (tworzy Claude Code na gałęzi worktree-<nazwa>;
                           kierownik sprząta po scaleniu; poza Gitem)
    .kierownik/            worktree, zlecenia i wyniki runnerów CLI, logi testów (poza Gitem)
    .claude/settings.json  uprawnienia i ustawienia dla pętli (propozycja kierownika wg SZABLONY.md,
                           sekcja 8; Ty akceptujesz)

Po tygodniach przerwy: nagłówek `docs/TODO.md` (cel, etap, ostatni zweryfikowany commit, w toku,
blokady, następny krok) + `docs/PROJEKT.md`.

## Kiedy kierownik Cię pyta

Tylko o: cel / zakres / MVP i plan kolejnego etapu; trudną do odwrócenia zmianę stosu lub
architektury; operacje na prawdziwych danych i usługach (produkcyjna baza, wysyłki, płatności,
wdrożenia, płatne API wywoływane przez aplikację); operacje nieodwracalne (force push, usuwanie).
Testy, gałęzie, subagenci, scalanie zweryfikowanych zmian i `git push` robi sam. Przed pytaniem
sprawdza fakty (np. czy LLM aplikacji jest lokalny).

Jeśli Claude Code często prosi o zgodę na bezpieczne polecenia, to kwestia uprawnień narzędzia:
kierownik zaproponuje `.claude/settings.json` (wzór w `kierownik/SZABLONY.md`, sekcja 8) albo włącz
tryb auto (klasyfikator zamiast pytań). Uwaga: `"permissions": {"defaultMode": "auto"}` działa tylko
w ustawieniach użytkownika (`~/.claude/settings.json`) albo z flagi CLI przy starcie Claude Code —
wpisane do projektowego `.claude/settings.json` jest ignorowane. Reguły `deny` obowiązują także
w trybie auto.

## Skróty

| Wpisz | Efekt |
|---|---|
| `status` | Stan z TODO.md i Gita |
| `dalej` | Zbierz zakończone zlecenia i kontynuuj pętlę — także gdy kierownik stoi, a zadanie w tle już się skończyło |
| `pomysł: …` | Zapis do „Pomysły” — nic nie jest uruchamiane |
| `zmiana: …` | Zmiana celu/zakresu/priorytetów — najpierw pokazany wpływ |
| `zespół: …` | Np. „Codex wyczerpany do piątku”, „mam Gemini CLI”, „rezygnuję z agy”, „oszczędzaj Claude”, „wyszedł nowy model X” |
| `stop` | Dokończ bieżący krok, zapisz stan, nie zaczynaj nowych zadań |

## Gdy Claude jest niedostępny

Gdy limit mają tylko niektóre modele Claude, kierownik przechodzi na inne runnery z rejestru (wyżej:
„Gdy kończy się limit”). Gdy limit ma cały Claude, zatrzymuje się też sam kierownik, bo działa w Claude
Code. Zanim to nastąpi, zapisuje stan w `docs/TODO.md`, robi commit i push, a Tobie podaje polecenie
dla Codex: zainstaluj tam pakiet z `codex/` i wpisz w tym samym projekcie
`$kierownik Wznów z PROJEKT.md i TODO.md; zachowaj aktywne zlecenia i kontynuuj zapisany następny krok.`
Kierownik w Codex czyta ten sam rejestr, więc wie, że Claude ma limit, i używa Claude CLI dopiero po
jego odnowieniu. Po powrocie wystarczy `/kierownik`.

## Pliki tego repozytorium

| Plik | Do czego |
|---|---|
| `kierownik/SKILL.md` | Metoda pracy kierownika (wczytywana w każdej sesji) |
| `kierownik/ZESPOL_WZOR.md` | Wzór rejestru runnerów; żywy rejestr to `~/.kierownik/ZESPOL.md` (jeden na maszynę) |
| `kierownik/ZESPOL_PROCEDURY.md` | Zakładanie rejestru i zmiany: limit, model, dostawca (czytane tylko w razie potrzeby) |
| `kierownik/URUCHAMIANIE_CLI.md` | Katalogi, polecenia i kontrole runnerów CLI (czytane przed pierwszym użyciem CLI w sesji) |
| `kierownik/START_PROJEKTU.md` | Przejęcie istniejącego projektu i nowy projekt (czytane raz na projekt) |
| `kierownik/ZLECENIA.md` | Szablony zleceń dla wykonawcy, recenzenta i analityka/architekta |
| `kierownik/scripts/kier.py` | Mechanika gita i testów kierownika (scalanie, konflikty, sprzątanie, logi testów) — wspólna z Codex |
| `kierownik/SZABLONY.md` | Wzory plików projektu + zasady AGENTS.md/CLAUDE.md wg OpenAI i Anthropic (po polsku) |
| `agents/kier-*.md` | Definicje subagentów: analityk, wykonawca, recenzent, architekt |
| `ANALIZA.md` | Dlaczego tak; lekcje z poprzednich wersji; źródła |
| `archiwum/` | Wersje v6, SDD, v7 |
