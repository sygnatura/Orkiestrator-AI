# Orkiestrator AI — instrukcja użycia (v7)

System prowadzenia większych projektów programistycznych z wieloma agentami AI. Jeden wątek
„kierownika” planuje i pilnuje stanu; kod piszą, sprawdzają i diagnozują inne modele w osobnych
sesjach; stan żyje w repozytorium, nie w czacie.

## Pliki zestawu

| Plik | Do czego | Kto czyta |
|---|---|---|
| `ORKIESTRATOR_PROJEKTU.md` | Prompt kierownika — **jedyny prompt, który wklejasz** | Wątek orkiestratora |
| `SZABLONY_PROJEKTU.md` | Wzory AGENTS.md, CLAUDE.md, planu zadania, ADR + zasady plików instrukcji wg OpenAI i Anthropic | Orkiestrator i wykonawca, tylko przy zakładaniu/naprawie tych plików |
| `ANALIZA.md` | Dlaczego system wygląda tak, a nie inaczej; porównanie wariantów; źródła | Ty, gdy chcesz zmieniać system |
| `archiwum/` | Poprzednie wersje (v6, SDD, architekt, workflow) | Nikt — tylko do porównań |

Agenci wykonawczy i weryfikatorzy nie dostają żadnego z tych plików. Dostają krótkie zlecenie
przygotowane przez orkiestratora, a zasady projektu czytają z jego `AGENTS.md`.

## Co powstaje w Twoim projekcie

    AGENTS.md            zasady dla wszystkich agentów (polecenia, granice, format raportu)
    CLAUDE.md            @AGENTS.md (+ ewentualne różnice dla Claude Code)
    docs/VISION.md       cel, MVP, czego NIE robimy
    docs/TODO.md         stan + etapy + zadania + pomysły + zrobione z dowodami  ← tu patrzysz
    docs/tasks/T-NNN.md  tylko dla zadań ryzykownych / wielosesyjnych
    docs/decisions/      tylko decyzje trudne do odwrócenia
    docs/DONE.md         archiwum zrobionych (gdy TODO.md się wydłuży)

Po tygodniach przerwy otwierasz **nagłówek docs/TODO.md**: cel, etap, ostatni zweryfikowany
commit, zadanie w toku, blokady, następny krok. Dowody weryfikacji są w „Zrobione”.

## Szybki start

1. Sklonuj ten zestaw w stałe miejsce, np. `C:\dev\Orkiestrator-AI` albo `~/Orkiestrator-AI`.
2. Otwórz NOWY wątek dla orkiestratora. Zalecane: Claude Code uruchomiony w katalogu projektu
   w trybie planu lub z uprawnieniami tylko do odczytu (orkiestrator sam zaproponuje ograniczenia).
   Może to być też czat bez dostępu do plików — wtedy orkiestrator poda Ci polecenia do uruchomienia.
3. Pierwsza wiadomość:

   ```
   <cała treść ORKIESTRATOR_PROJEKTU.md>

   Projekt: <ścieżka do repozytorium projektu>
   Szablony: <ścieżka>/SZABLONY_PROJEKTU.md
   ```

   Jeśli narzędzie ma „instrukcje projektu” / „system prompt”, możesz tam wkleić prompt,
   a w wiadomości podać tylko dwie ścieżki.
4. Dalej:
   - **nowy projekt** — opisz pomysł własnymi słowami; orkiestrator zada do 5 pytań
     z proponowanymi odpowiedziami, napisze szkic VISION.md, zleci plan architektowi;
   - **istniejący projekt** — napisz „przejmij”; orkiestrator zrobi odczyt, raport wdrożenia
     i zaproponuje pierwszy krok, niczego nie zmieniając.

## Cykl pracy (to, co robisz na co dzień)

    orkiestrator: STAN / DECYZJA / ZLECENIE (blok kodu) / OCZEKUJĘ
        │  kopiujesz zlecenie do wskazanego narzędzia (Codex, Claude Code, Antigravity, Qwen)
        ▼
    ty: „przekazane T-012”                         → status ZLECONE
        │  agent kończy i oddaje raport ≤ 15 linii
        ▼
    ty: „raport T-012” + wklejka                    → kontrola formalna → zlecenie dla weryfikatora
        │  weryfikator (inny model) oddaje werdykt
        ▼
    ty: „raport T-012” + werdykt                    → DO SCALENIA + polecenia scalenia
        │  scalasz i uruchamiasz podane sprawdzenie
        ▼
    ty: wynik sprawdzenia                           → GOTOWE + wpis dowodu w TODO.md

Decyzje zostają po Twojej stronie: akceptacja VISION i planu, nowe moduły i zależności, zmiany
zakresu i architektury, scalanie, push, migracje, operacje na prawdziwych danych.

## Skróty

| Wpisz | Efekt |
|---|---|
| `status` | Stan z TODO.md i Gita + jeden następny krok |
| `przekazane T-NNN` | Potwierdzasz uruchomienie zlecenia |
| `raport T-NNN` + wklejka | Odbiór raportu wykonawcy albo werdyktu weryfikatora |
| `pomysł: …` | Zapis do „Pomysły” z oceną zgodności z celem — nic nie jest uruchamiane |
| `zmiana: …` | Zmiana celu / zakresu / priorytetów — najpierw pokazany wpływ, zapis po akceptacji |
| `zespół: …` | Np. „Codex niedostępny do piątku” — zamiennik w tej samej roli |
| `przekaż` | Przekazanie wątku (poniżej) |

## Pilnowanie kontekstu orkiestratora

Wątek orkiestratora jest jednorazowy. W każdej odpowiedzi widzisz licznik `wątek: n/6`.
Orkiestrator sam zaproponuje przekazanie, gdy: zamknie etap, licznik dojdzie do 6, narzędzie
pokaże >50% zużycia kontekstu lub automatyczne kompaktowanie, w wątku będą 3+ długie wklejki
albo zacznie mylić fakty.

Przekazanie: wpisz `przekaż` → orkiestrator commituje TODO.md i daje prompt startowy (≤ 10 linii)
→ otwierasz NOWY wątek, wklejasz `ORKIESTRATOR_PROJEKTU.md` + ten prompt startowy.
Nowy wątek startuje w trybie WZNOWIENIE: czyta tylko nagłówek TODO.md, bieżący etap i kilka
tanich poleceń Gita.

Żeby nie zapychać wątku:
- wklejaj raporty w formacie z AGENTS.md (≤ 15 linii), nie całe transkrypty sesji agentów;
- długie logi daj do streszczenia modelowi rutynowemu i wklej streszczenie;
- tematy poboczne omawiaj w osobnym czacie, a do orkiestratora wpisz tylko `pomysł: …`.

## AGENTS.md i CLAUDE.md — zasada w jednym akapicie

AGENTS.md jest jedynym źródłem zasad dla wszystkich narzędzi (Codex czyta go automatycznie;
Claude Code też, ale tylko gdy nie ma CLAUDE.md). CLAUDE.md zawiera w pierwszej linii import
`@AGENTS.md` i ewentualnie krótką sekcję tylko dla Claude Code — nigdy kopię zasad ani zdanie
„przeczytaj AGENTS.md”. Plik ma być krótki (≤ ~150 linii), bez stanu projektu i planów.
Regułę dopisuje się, gdy agent drugi raz popełni ten sam błąd; reguły, których złamanie jest
kosztowne, zabezpiecza się technicznie (uprawnienia, hook, CI). Szczegóły i wzory:
`SZABLONY_PROJEKTU.md`.

## Dostosowanie

- **Zespół i modele** — edytuj blok `<zespol>` w sekcji 1 promptu (Twoje stałe ustawienia)
  albo zgłaszaj zmiany w rozmowie (`zespół: …`).
- **Próg przekazania wątku** — zmień „6” w sekcji 3 promptu (np. 4 dla małych okien kontekstu,
  8–10 dla dużych).
- **Tryb automatyczny** — napisz „włącz tryb automatyczny”, jeśli narzędzie orkiestratora umie
  uruchamiać agentów; granice i niezależny weryfikator obowiązują dalej.
- **Istniejący projekt z własnym procesem** — orkiestrator używa Twoich plików (np. ROADMAP.md)
  i zapisuje mapowanie w nagłówku TODO.md; nic nie przebudowuje.

## Najczęstsze problemy

| Objaw | Co zrobić |
|---|---|
| Orkiestrator zaczyna analizować kod lub proponować poprawki | Przypomnij: „SYGNAŁ STOP” (sekcja 6) |
| Agent zmienił pliki spoza zakresu albo TODO.md | Orkiestrator odrzuci odbiór; gdy się powtarza — dopisz regułę / dodaj hook |
| Weryfikator zgłasza dziesiątki drobiazgów | Do poprawy idą tylko BLOKUJĄCE; reszta ląduje w „Pomysły” |
| Ten sam problem po dwóch rundach poprawek | Orkiestrator przerywa pętlę i zleca diagnozę architektowi |
| Nie wiesz, czy coś naprawdę działa | Szukaj wpisu w „Zrobione” z dowodem; brak wpisu = niezweryfikowane |
| Claude Code nie stosuje zasad z AGENTS.md | Sprawdź `/context`; CLAUDE.md musi zawierać `@AGENTS.md`, a nie zdanie z odesłaniem |
| Codex ignoruje końcówkę AGENTS.md | Plik (łącznie z zagnieżdżonymi) przekracza 32 KiB — skróć |
