# Kierownik projektu AI — instrukcja (v9, Claude Max)

Skill dla Claude Code, który robi z sesji Claude kierownika technicznego projektu: rozumie system,
prowadzi plan rozwoju i stan w repozytorium, deleguje pracę zespołowi subagentów Claude
(Sonnet / Opus / Fable / Haiku dobierane do zadania), niezależnie weryfikuje, scala i wypycha to,
co zweryfikowane, a do Ciebie wraca z raportem po etapie albo z decyzją, która należy do Ciebie.
Codex i Antigravity są zapasem oraz dodatkową recenzją innej rodziny modeli, gdy jest wskazana.

## Instalacja (raz na maszynę)

Skopiuj skill i subagentów:

    # Windows (PowerShell)
    Copy-Item -Recurse .\kierownik $HOME\.claude\skills\kierownik
    New-Item -ItemType Directory -Force $HOME\.claude\agents | Out-Null
    Copy-Item .\agents\*.md $HOME\.claude\agents\
    # Linux / macOS
    cp -r kierownik ~/.claude/skills/kierownik
    mkdir -p ~/.claude/agents && cp agents/*.md ~/.claude/agents/

W każdym projekcie na tej maszynie masz polecenie `/kierownik` i subagentów `kier-*`.
Opis skilla nie obciąża innych sesji (`disable-model-invocation: true`).

## Użycie

1. Otwórz Claude Code w katalogu projektu i ustaw model kierownika: `/model opus`
   (Opus 5.5, effort high). Opcjonalnie bezpiecznik kontekstu: `/autocompact 400k`.
2. Wpisz `/kierownik`.
3. Pierwszy raz na maszynie: kierownik sprawdzi zapasowe narzędzia (`agy`, `codex`) i zapyta
   o stan ich limitów — zapisze to w `~/.claude/skills/kierownik/ZESPOL.md`.
4. Pierwszy raz w projekcie:
   - **istniejący projekt** — trzech analityków równolegle mapuje kod, kierownik uruchamia testy
     (jeśli są bezpieczne), pisze `docs/PROJEKT.md`, `AGENTS.md`, `CLAUDE.md`, a architekt (Fable)
     przygotowuje plan w `docs/TODO.md`; dostajesz jedną wiadomość: obraz projektu, cel/MVP
     do potwierdzenia, plan etapu;
   - **nowy projekt** — do 5 pytań z proponowanymi odpowiedziami, potem plan od architekta.
5. Po Twojej akceptacji kierownik pracuje sam do końca etapu.

**Nowy wątek** (po etapie albo gdy kierownik poprosi): `/clear`, potem `/kierownik`.
Nic nie kopiujesz — stan jest w plikach.

## Zespół

| Rola | Kto | Model domyślny |
|---|---|---|
| Kierownik | wątek główny | Opus 5.5 (high) |
| Analityk — czyta kod i logi, zwraca streszczenia | `kier-analityk` | Sonnet (low) → Opus przy dużym repo |
| Wykonawca — implementuje w osobnym worktree | `kier-wykonawca` | Sonnet (high) → Opus przy trudnych zadaniach |
| Recenzent — niezależna weryfikacja | `kier-recenzent` | Opus (high); Fable dla kodu Opusa i celu etapu |
| Architekt — plan, przejęcie, diagnozy, decyzje | `kier-architekt` | Fable 5.1 (xhigh) |
| Zapas / recenzja innej rodziny | Antigravity `agy`, Codex `codex exec` | według limitów |

Niezależność weryfikacji: recenzent to zawsze inny model niż autor, startuje ze świeżym kontekstem
i widzi tylko kryteria, diff i polecenia — nie rozumowanie autora. Recenzję innej rodziny
(Antigravity lub Codex) kierownik dodaje tylko przy zmianach dotyczących bezpieczeństwa, danych,
pieniędzy lub kontraktów zewnętrznych, przy sprzecznych sygnałach, po dwóch nieudanych rundach
poprawek i przy weryfikacji celu etapu kluczowego dla MVP. Gdy Claude jest niedostępny,
zapas przejmuje wykonawstwo i recenzję.

Niezależne zadania etapu idą równolegle (do 4 wykonawców naraz, każdy w swoim worktree).

Fable 5.1 jest u Ciebie w limicie planu. Gdyby `/model` zaczął pokazywać przy nim „Requires usage
credits”, powiedz kierownikowi `zespół: Fable wymaga credits` — zastąpi go Opusem.

Zapasowe CLI działają w trybie bez pytań (`agy --dangerously-skip-permissions`), więc kierownik
uruchamia je wyłącznie w worktree zadania (`.kierownik/wt/T-NNN`), bez sekretów w zleceniu,
i po każdym przebiegu sprawdza `git status` oraz stderr.

## Co powstaje w projekcie

    AGENTS.md          zasady dla wszystkich agentów (polecenia, środowisko i koszty, granice, raport)
    CLAUDE.md          @AGENTS.md (+ ewentualne różnice dla Claude Code)
    docs/PROJEKT.md    jak działa system: cel, moduły, przepływ, środowisko i koszty, stan funkcjonalny
    docs/TODO.md       plan rozwoju i stan — tu patrzysz, gdy chcesz wiedzieć „gdzie jesteśmy”
    docs/DONE.md       archiwum zrobionych zadań z dowodami
    docs/tasks/        plany zadań ryzykownych / wielosesyjnych
    docs/decisions/    decyzje trudne do odwrócenia (ADR)

Po tygodniach przerwy: nagłówek `docs/TODO.md` (cel, etap, ostatni zweryfikowany commit, w toku,
blokady, następny krok) + `docs/PROJEKT.md`.

## Kiedy kierownik Cię pyta

Tylko o: cel / zakres / MVP i plan kolejnego etapu; trudną do odwrócenia zmianę stosu lub
architektury; operacje na prawdziwych danych i usługach (produkcyjna baza, wysyłki, płatności,
wdrożenia, płatne API wywoływane przez aplikację); operacje nieodwracalne (force push, usuwanie).
Testy, gałęzie, subagenci, scalanie zweryfikowanych zmian i `git push` robi sam. Przed pytaniem
sprawdza fakty (np. czy LLM aplikacji jest lokalny).

Jeśli Claude Code często prosi o zgodę na bezpieczne polecenia, to kwestia uprawnień narzędzia:
kierownik zaproponuje `.claude/settings.json` (wzór w `kierownik/SZABLONY.md`, sekcja 8)
albo użyj trybu auto.

## Skróty

| Wpisz | Efekt |
|---|---|
| `status` | Stan z TODO.md i Gita |
| `dalej` | Kontynuuj pętlę |
| `pomysł: …` | Zapis do „Pomysły” — nic nie jest uruchamiane |
| `zmiana: …` | Zmiana celu/zakresu/priorytetów — najpierw pokazany wpływ |
| `zespół: …` | Np. „Codex wyczerpany do piątku”, „Fable wymaga credits” |
| `stop` | Dokończ bieżący krok, zapisz stan, nie zaczynaj nowych zadań |

## Gdy Claude jest niedostępny

Projekt może poprowadzić Codex CLI albo `agy`: „Przeczytaj ~/.claude/skills/kierownik/SKILL.md
i działaj według niego jako kierownik tego projektu.” Role subagentów Claude przejmą wtedy
pozostałe dwie rodziny (wykonawca jedną, recenzent drugą).

## Pliki tego repozytorium

| Plik | Do czego |
|---|---|
| `kierownik/SKILL.md` | Metoda pracy kierownika |
| `kierownik/ZESPOL.md` | Modele, role, zapas, limity (jeden na maszynę) |
| `kierownik/SZABLONY.md` | Wzory plików projektu + zasady AGENTS.md/CLAUDE.md wg OpenAI i Anthropic |
| `agents/kier-*.md` | Definicje subagentów: analityk, wykonawca, recenzent, architekt |
| `ANALIZA.md` | Dlaczego tak; lekcje z poprzednich wersji; źródła |
| `archiwum/` | Wersje v6, SDD, v7 |
