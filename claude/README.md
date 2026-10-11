# Kierownik projektu AI — instrukcja (v10, Claude Max)

Skill dla Claude Code, który robi z sesji Claude kierownika technicznego projektu: rozumie system,
prowadzi plan rozwoju i stan w repozytorium, deleguje pracę zespołowi subagentów Claude (model
dobierany do zadania spośród klas od najszybszego do najmocniejszego), niezależnie weryfikuje, scala
i wypycha to, co zweryfikowane, a do Ciebie wraca z raportem po etapie albo z decyzją, która należy do
Ciebie. Codex i Antigravity są zapasem oraz dodatkową recenzją innej rodziny modeli, gdy jest wskazana.

## Instalacja (raz na maszynę)

Skopiuj skill i subagentów:

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

Kopiuj tylko instrukcje; `ZESPOL.md` to stan Twojej maszyny — nie nadpisuj go.

    # Linux / macOS
    cp kierownik/SKILL.md kierownik/ZLECENIA.md kierownik/SZABLONY.md ~/.claude/skills/kierownik/ && cp agents/*.md ~/.claude/agents/
    # Windows (PowerShell)
    Copy-Item .\kierownik\SKILL.md, .\kierownik\ZLECENIA.md, .\kierownik\SZABLONY.md $HOME\.claude\skills\kierownik\
    Copy-Item .\agents\*.md $HOME\.claude\agents\

Jeśli zmienił się szablon ZESPOL.md, porównaj go ręcznie ze swoim.

## Użycie

1. Otwórz Claude Code w katalogu projektu i ustaw model kierownika: `/model opus` (alias — zawsze
   najnowszy model tej linii). `/model` nie zmienia effortu — zostaje domyślny dla modelu; jeśli chcesz
   wyższego, dodaj `/effort high`. Opcjonalnie bezpiecznik kontekstu: `/autocompact` z progiem poniżej
   pełnego okna modelu (dziś np. `/autocompact 400k`; wartość prowadzi `kierownik/ZESPOL.md`).
   Wszystko to możesz zapisać raz w `settings.json` (wzór: `kierownik/SZABLONY.md`, sekcja 8).
2. Wpisz `/kierownik`.
3. Pierwszy raz na maszynie: kierownik wykryje zapasowe narzędzia (`codex`, `agy`; są opcjonalne —
   bez nich cała pętla działa na Claude), każde obecne sprawdzi krótkim testem dymnym w tymczasowym
   repozytorium, tym samym poleceniem, którego potem używa (`agy` już w trybie bez pytań o zgodę —
   patrz „Bezpieczeństwo”; test zużywa odrobinę limitu narzędzia), zapyta Cię o stan limitów i o to,
   co pokazuje `/model`, i zapisze wszystko w `~/.claude/skills/kierownik/ZESPOL.md`. Jeśli któregoś
   narzędzia nie chcesz używać, powiedz `zespół: nie używaj codex` — kierownik zapisze to w ZESPOL.md.
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
| Zapas / recenzja innej rodziny | Antigravity `agy`, Codex `codex exec` | wykonawstwo i recenzja, gdy Claude jest niedostępny; dodatkowa recenzja w przypadkach poniżej |

Modele są opisane klasami: SZYBKI < STANDARDOWY < MOCNY < NAJMOCNIEJSZY. Który alias Claude Code
(`haiku`, `sonnet`, `opus`, `fable`, …) stoi za którą klasą, który model pełni którą rolę, z jakim
effortem, i jakie są bieżące ograniczenia (limity, kredyty) — to jedno miejsce:
`kierownik/ZESPOL.md` (po instalacji `~/.claude/skills/kierownik/ZESPOL.md`). Kierownik aktualizuje
ten plik w czasie pracy, dlatego README go nie powiela. Domyślnie: kierownik i recenzent w klasie
MOCNY, analityk i wykonawca w STANDARDOWY (trudne zadania → MOCNY), architekt i weryfikacja celu
etapu w NAJMOCNIEJSZY.

Niezależność weryfikacji: recenzent to z zasady model klasy wyżej niż autor (gdy najmocniejsza klasa
jest poza limitem planu — co najmniej świeży kontekst i niezależnie uruchomione testy), startuje ze
świeżym kontekstem i widzi tylko kryteria, diff i polecenia — nie rozumowanie autora. Recenzję innej
rodziny (Antigravity lub Codex) kierownik dodaje tylko przy zmianach dotyczących bezpieczeństwa,
danych, pieniędzy lub kontraktów zewnętrznych, przy sprzecznych sygnałach, których nie rozstrzygnęła
recenzja w klasie NAJMOCNIEJSZY, po dwóch nieudanych rundach poprawek i przy weryfikacji celu etapu
kluczowego dla MVP. Gdy Claude jest niedostępny, zapas przejmuje wykonawstwo i recenzję.

Niezależne zadania etapu idą równolegle (do 4 wykonawców naraz, każdy w swoim worktree).

**Nowe modele.** Aliasy `opus`, `sonnet`, `haiku`, `fable` wskazują zawsze najnowszy model swojej
linii, więc po wydaniu nowej wersji nic nie zmieniasz. Gdy pojawi się nowa linia (inna nazwa), napisz:
`zespół: wyszedł nowy model <nazwa>` — kierownik zaproponuje, do której klasy (SZYBKI…NAJMOCNIEJSZY) go
przypisać, a po Twoim potwierdzeniu zaktualizuje tabelę klas w ZESPOL.md i pole `model:` (alias albo pełne ID
modelu; w razie potrzeby także `effort:`) u agentów tej klasy w `~/.claude/agents/kier-*.md`.
Czy model mieści się w limicie planu, widzisz w `/model`: dopisek „Requires usage credits” oznacza, że
pobiera kredyty — zgłoś to `zespół: <alias> wymaga credits`, a kierownik przestawi rolę na inną klasę
z planu i odnotuje to w ZESPOL.md.

## Bezpieczeństwo

Zapasowe CLI działają w trybie bez pytań (`agy --dangerously-skip-permissions`; Codex w sandboxie
`-s workspace-write`). Worktree zadania (`.kierownik/wt/T-NNN`) porządkuje zmiany w repozytorium, ale
nie ogranicza dostępu `agy` do maszyny — a kierownik uruchamia `agy` już przy pierwszym `/kierownik`
(test dymny). Jeśli masz na tej maszynie cenne dane poza repozytorium, uruchamiaj Claude Code
w kontenerze albo wyłącz `agy`: w `~/.claude/skills/kierownik/ZESPOL.md` (tabela „Limity”, wiersz
Google / Antigravity) wpisz stan `wyłączony przez właściciela` — kierownik go wtedy nie testuje i nie
używa. Kierownik nie przekazuje sekretów w zleceniu i po każdym przebiegu sprawdza `git status` oraz
stderr. Reguły `deny` z `settings.json` (SZABLONY.md, sekcja 8) blokują czytanie `.env` także
subagentom.

## Co powstaje w projekcie

    AGENTS.md              zasady dla wszystkich agentów (polecenia, środowisko i koszty, granice, raport)
    CLAUDE.md              @AGENTS.md (+ ewentualne różnice dla Claude Code)
    docs/PROJEKT.md        jak działa system: cel, moduły, przepływ, środowisko i koszty, stan funkcjonalny
    docs/TODO.md           plan rozwoju i stan — tu patrzysz, gdy chcesz wiedzieć „gdzie jesteśmy”
    docs/DONE.md           archiwum zrobionych zadań z dowodami
    docs/tasks/            plany zadań ryzykownych / wielosesyjnych
    docs/decisions/        decyzje trudne do odwrócenia (ADR)
    .claude/worktrees/     worktree subagentów Claude (tworzy Claude Code na gałęzi worktree-<nazwa>;
                           kierownik sprząta po scaleniu; poza Gitem)
    .kierownik/            worktree i wyniki zleceń zapasowych CLI (poza Gitem)
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
| `dalej` | Kontynuuj pętlę |
| `pomysł: …` | Zapis do „Pomysły” — nic nie jest uruchamiane |
| `zmiana: …` | Zmiana celu/zakresu/priorytetów — najpierw pokazany wpływ |
| `zespół: …` | Np. „Codex wyczerpany do piątku”, „fable wymaga credits”, „wyszedł nowy model X”, „nie używaj agy” |
| `stop` | Dokończ bieżący krok, zapisz stan, nie zaczynaj nowych zadań |

## Gdy Claude jest niedostępny

Kierownikiem jest zawsze sesja Claude Code — SKILL.md zakłada jej narzędzia (subagenci `kier-*`,
worktree, `/clear`, `/model`), więc Codex ani `agy` nie poprowadzą według niego projektu. Gdy w trakcie
etapu modele Claude mają limit lub awarię, kierownik przekazuje role wykonawcy i recenzenta zapasowym
CLI (SKILL.md, sekcja 7 „ZAPAS”). Gdy Claude jest niedostępny całkiem, nic nie przepada: stan projektu
jest w plikach (`docs/TODO.md`, `docs/PROJEKT.md`, `AGENTS.md`) — możesz ręcznie zlecić pojedyncze
zadanie Codexowi lub `agy` szablonem A z `kierownik/ZLECENIA.md`, a po powrocie Claude kierownik wznowi
pracę z Gita i TODO.md (tryb WZNOWIENIE).

## Pliki tego repozytorium

| Plik | Do czego |
|---|---|
| `kierownik/SKILL.md` | Metoda pracy kierownika |
| `kierownik/ZESPOL.md` | Klasy modeli i aliasy, role, effort, zapas, limity (jeden na maszynę) |
| `kierownik/ZLECENIA.md` | Szablony zleceń dla wykonawcy, recenzenta i analityka/architekta |
| `kierownik/SZABLONY.md` | Wzory plików projektu + zasady AGENTS.md/CLAUDE.md wg OpenAI i Anthropic |
| `agents/kier-*.md` | Definicje subagentów: analityk, wykonawca, recenzent, architekt |
| `ANALIZA.md` | Dlaczego tak; lekcje z poprzednich wersji; źródła |
| `archiwum/` | Wersje v6, SDD, v7 |
