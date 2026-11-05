# Evale orkiestratora

Powtarzalny sprawdzian, czy kierownik daje lepszy wynik niż zwykła sesja i która konfiguracja zespołu się opłaca.
Każda konfiguracja dostaje ten sam mały projekt i ten sam etap E1: 7 zadań, w tym zadanie bezpieczeństwa i parę
zadań, które przy równoległej pracy kolidują. Wynik ocenia się **ukrytymi testami akceptacyjnymi**, których agenci
nie widzą.

| Konfiguracja | Co to jest | Odpowiada na pytanie |
|---|---|---|
| A | zwykła sesja Claude Code, bez kierownika | punkt odniesienia |
| B | `/kierownik`, tylko modele Claude (wykonawca Opus) | czy kierownik poprawia jakość |
| C | `/kierownik` z Codexem jako recenzentem innej rodziny | czy druga rodzina modeli coś wnosi |
| D | jak B, ale wykonawca zawsze Sonnet | czy Opus jako wykonawca się opłaca |

## Co jest w katalogu

- `projekt/` — projekt testowy „katalog książek” (Python, sama biblioteka standardowa) w stanie wyjściowym:
  kod, testy widoczne, `AGENTS.md`, `CLAUDE.md`, `docs/PROJEKT.md` i `docs/TODO.md` z **zaakceptowanym** etapem E1.
- `ukryte/` — ukryte testy akceptacyjne, po jednym pliku na zadanie, plus `test_KOLIZJA.py` dla pary T-006/T-007.
- `wzorzec/` — rozwiązanie wzorcowe. Służy tylko do sprawdzenia, że ukryte testy da się spełnić
  (`tests/test_evals.py`, uruchamiany w CI).
- `przygotuj.py`, `ocen.py`, `zestaw.py` — przygotowanie przebiegu, ocena, zestawienie.
- `wyniki/` — pliki JSON z przebiegów (commituj je); `WYNIKI.md` — zestawienie.

## Przed pierwszym przebiegiem (raz)

1. Aktualny pakiet: `python3 install.py` w katalogu tego repozytorium.
2. W `~/.claude/settings.json` (ustawienia użytkownika, więc działa w każdej kopii) dopisz
   `"env": { "CLAUDE_CODE_FORK_SUBAGENT": "0" }`. Bez tego kierownik nie może czekać na subagentów
   (SZABLONY §8), a warunki przebiegów nie byłyby równe.
3. Rejestr `~/.kierownik/ZESPOL.md` powinien już istnieć, z Twojej normalnej pracy. W konfiguracji C potrzebny jest
   działający, zalogowany `codex`. `agy` w przebiegach nie używamy: bez sandboxa widzi cały dysk, także ukryte testy.

## Jeden przebieg

Zalecana kolejność pierwszej serii: **B, A, C, D**, każda raz.

1. Przygotuj świeżą kopię **poza** tym repozytorium (skrypt odmówi kopii w środku):
   `python3 evals/przygotuj.py ~/evale/B-1 --remote`
2. Otwórz nową sesję Claude Code w `~/evale/B-1` i zanotuj godzinę startu.
3. Wpisz polecenie startowe danej konfiguracji (niżej) i nie ingeruj do końca etapu. Na pytania odpowiadaj
   ze ściągi, żeby każdy przebieg dostał te same odpowiedzi.
4. Gdy etap jest zamknięty (raport etapu albo informacja, że wszystko zrobione), zanotuj czas i odczytaj zużycie
   (`/cost` albo `/usage` w Claude Code; w C dodaj tokeny z podsumowania Codex). Rundy poprawek policz w sekcji
   „Zrobione” w `docs/TODO.md`.
5. Oceń:
   `python3 evals/ocen.py ~/evale/B-1 --konfiguracja B --przebieg 1 --minuty 42 --tokeny 1850000 --rundy 2 --uwagi "..."`
   W `--uwagi` zapisz, co się działo, np. pytania kierownika albo ręczne interwencje.
6. Po serii: `python3 evals/zestaw.py`. Zcommituj `evals/wyniki/` i `evals/WYNIKI.md`, a zestawienie wklej
   do rozmowy z Claude, który je oceni.

### Polecenia startowe

- **A** (bez `/kierownik`):
  `Zrealizuj etap E1 z docs/TODO.md: zadania T-001…T-007 według ich kryteriów, każde z testem w tests/, z commitami na main. Plan jest zaakceptowany — nie pytaj o akceptację. Na koniec podsumuj, co zrobiłeś i jak to sprawdziłeś.`
- **B**: `/kierownik`, a po starcie:
  `Eval B: w tym etapie używaj wyłącznie modeli Claude (bez Codex i agy; to jednorazowe, nie zmieniaj rejestru). Plan E1 jest zaakceptowany — prowadź go do końca.`
- **C**: `/kierownik`, a po starcie:
  `Eval C: używaj rejestru jak zwykle, z Codexem jako recenzentem innej rodziny; bez agy (jednorazowo, nie zmieniaj rejestru). Plan E1 jest zaakceptowany — prowadź go do końca.`
- **D**: `/kierownik`, a po starcie:
  `Eval D: w tym etapie wyłącznie modele Claude (bez Codex i agy) i wykonawca zawsze w klasie STANDARDOWY (sonnet), także w rundach poprawek; jednorazowo, nie zmieniaj rejestru. Plan E1 jest zaakceptowany — prowadź go do końca.`

### Ściąga odpowiedzi

| Pytanie kierownika | Odpowiedź |
|---|---|
| propozycja `.claude/settings.json` | `Tak, zastosuj.` |
| zgoda na `agy` bez sandboxa | `Nie.` |
| brak remote / push | `Remote jest lokalny (przygotuj.py --remote), pushuj.` (bez `--remote`: `Bez remote, nie pushuj.`) |
| akceptacja planu albo kolejnego etapu | `Etap E1 jest zaakceptowany; po nim zakończ — nie planuj E2.` |
| każde inne pytanie | `Przyjmij swoją rekomendację.` |

## Co mierzy `ocen.py`

- **Zadania (główna metryka):** ukryte testy zaliczone na zadanie, 0–7. Oceniany jest katalog roboczy na `main`.
- **Kolizja:** czy po scaleniu T-006 i T-007 linia ma oba elementy (rok i znacznik).
- **Testy widoczne:** czy przechodzą. **Osłabione testy:** usunięte pliki, metody albo asercje z testów
  wyjściowych.
- **Historia Gita:** commity na main, scalenia (z liczbą commitów na zadanie), rewerty, pozostawione gałęzie
  `task/*` i worktree, niezacommitowane zmiany.
- **Koszt:** minuty, tokeny i rundy podajesz sam. Skrypt pokazuje wzmianki o rundach z `docs/TODO.md`.

## Jak czytać wyniki

Przy jednym przebiegu na konfigurację różnice o 1 zadanie albo kilkanaście procent czasu są w granicach przypadku.
Wnioski wyciągamy z dużych różnic. Tam, gdzie wyniki są bliskie, robimy drugi przebieg. Jakość (zadania, kolizja,
brak osłabionych testów) liczy się przed kosztem. Tańsza konfiguracja wygrywa tylko przy równej jakości.
