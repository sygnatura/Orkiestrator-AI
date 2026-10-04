# Kierownik projektu AI — instrukcja (v8)

Skill dla Claude Code, który robi z sesji Claude kierownika technicznego projektu: rozumie system,
prowadzi plan rozwoju i stan w repozytorium, deleguje implementację do Codexa, weryfikuje
krzyżowo (kod Codexa sprawdza Claude, kod Claude sprawdza Codex), scala i wypycha to, co
zweryfikowane, a do Ciebie wraca z raportem po etapie albo z decyzją, która należy do Ciebie.

## Instalacja (raz na maszynę)

Skopiuj katalog `kierownik/` do `~/.claude/skills/`:

    # Windows (PowerShell)
    Copy-Item -Recurse .\kierownik $HOME\.claude\skills\kierownik
    # Linux / macOS
    cp -r kierownik ~/.claude/skills/kierownik

Gotowe — w każdym projekcie na tej maszynie dostępne jest polecenie `/kierownik`.
Opis skilla nie obciąża innych sesji (`disable-model-invocation: true`): pełna treść ładuje się
tylko po wpisaniu `/kierownik`.

## Użycie

1. Otwórz Claude Code w katalogu projektu (nowego lub istniejącego).
2. Wpisz `/kierownik`.
3. Za pierwszym razem na maszynie kierownik sprawdzi Codexa (test dymny) i zada jedno pytanie
   o Twoje limity — zapisze to w `~/.claude/skills/kierownik/ZESPOL.md`.
4. Za pierwszym razem w projekcie:
   - **istniejący projekt** — sam przeanalizuje kod (subagenci), uruchomi testy (jeśli są
     bezpieczne), napisze `docs/PROJEKT.md`, `AGENTS.md`, `CLAUDE.md`, plan w `docs/TODO.md`
     i przyjdzie z jedną wiadomością: obraz projektu, cel/MVP do potwierdzenia, plan etapu;
   - **nowy projekt** — zada do 5 pytań z proponowanymi odpowiedziami i przygotuje plan.
5. Po Twojej akceptacji pracuje sam do końca etapu.

**Nowy wątek** (np. po etapie albo gdy kierownik o to poprosi): `/clear`, potem `/kierownik`.
Nic nie kopiujesz — stan jest w plikach.

Model: do przejęcia projektu i planowania etapów użyj najsilniejszego modelu (`/model`);
samą pętlę wykonawczą może prowadzić tańszy model, jeśli chcesz oszczędzać limit Claude.

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
Testy, zmiany na gałęziach, subagenci, Codex, scalanie zweryfikowanych zmian i `git push` —
robi sam. Przed pytaniem sprawdza fakty (np. czy LLM aplikacji jest lokalny).

Jeśli Claude Code mimo to często prosi o zgodę na bezpieczne polecenia, to kwestia uprawnień
narzędzia, nie promptu: kierownik zaproponuje `.claude/settings.json` (wzór w `kierownik/SZABLONY.md`,
sekcja 8) albo użyj trybu auto.

## Skróty

| Wpisz | Efekt |
|---|---|
| `status` | Stan z TODO.md i Gita |
| `dalej` | Kontynuuj pętlę |
| `pomysł: …` | Zapis do „Pomysły” — nic nie jest uruchamiane |
| `zmiana: …` | Zmiana celu/zakresu/priorytetów — najpierw pokazany wpływ |
| `zespół: …` | Np. „Codex wyczerpany do piątku” |
| `stop` | Dokończ bieżący krok, zapisz stan, nie zaczynaj nowych zadań |

## Zespół

Domyślnie: Claude Code (kierownik + subagenci) i Codex CLI wywoływany z terminala.
Antigravity nie ma wywołania z terminala, więc kierownik używa go tylko przez Ciebie — dla zadań
z przeglądarką/UI albo jako trzecia opinia przy sporze Claude ↔ Codex. Konfiguracja i limity:
`kierownik/ZESPOL.md`.

## Gdy Claude jest niedostępny

Możesz poprowadzić projekt w Codex CLI: „Przeczytaj ~/.claude/skills/kierownik/SKILL.md i działaj
według niego jako kierownik tego projektu.” Bez subagentów Claude część analizy i weryfikację
kodu Codexa przejmie świeża sesja `codex exec` albo Antigravity — jakość krzyżowej weryfikacji
będzie wtedy niższa.

## Pliki tego repozytorium

| Plik | Do czego |
|---|---|
| `kierownik/SKILL.md` | Metoda pracy kierownika |
| `kierownik/ZESPOL.md` | Narzędzia, polecenia, limity (jeden na maszynę) |
| `kierownik/SZABLONY.md` | Wzory plików projektu + zasady AGENTS.md/CLAUDE.md wg OpenAI i Anthropic |
| `ANALIZA.md` | Dlaczego tak; lekcje z poprzednich wersji; źródła |
| `archiwum/` | Wersje v6, SDD, v7 |
