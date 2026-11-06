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
| E | `/kierownik` w trybie zwartym (sam wybiera tryb etapu) | czy jedna recenzja całości daje jakość B za koszt bliski A |

## Co jest w katalogu

- `projekt/` — projekt testowy „katalog książek” (Python, sama biblioteka standardowa) w stanie wyjściowym:
  kod, testy widoczne, `AGENTS.md`, `CLAUDE.md`, `docs/PROJEKT.md` i `docs/TODO.md` z **zaakceptowanym** etapem E1.
- `ukryte/` — ukryte testy akceptacyjne, po jednym pliku na zadanie, plus `test_KOLIZJA.py` dla pary T-006/T-007.
- `wzorzec/` — rozwiązanie wzorcowe. Służy tylko do sprawdzenia, że ukryte testy da się spełnić
  (`tests/test_evals.py`, uruchamiany w CI).
- `projekt2/`, `ukryte2/`, `wzorzec2/` — trudniejszy zestaw 2 (niżej), wybierany przez `--zestaw 2`.
- `sondy2/` — sondy usterek spoza kryteriów dla zestawu 2 (uprawnienia, dowiązanie, `.bak`, układ pliku). Nie wchodzą do wyniku zadań; mierzą, co wnosi recenzja.
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
   Przebieg bezobsługowy (`claude -p`) uruchamiaj z `CLAUDE_CODE_PRINT_BG_WAIT_CEILING_MS=0`, bo inaczej długie zlecenia w tle są ubijane 10 minut po ostatniej turze (seria 3).
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
- **Zmienione testy widoczne:** istniejące metody, funkcje pomocnicze albo dane w testach wyjściowych ze zmienioną
  treścią (porównanie drzew składni). Nowe testy dopisane obok się nie liczą.
- **Założenie (zestaw 2):** heurystyka, czy przy zadaniu ze sprzecznym kryterium (T-107) commit albo `docs/`
  mówi o sprzeczności. „nie” znaczy tylko, że trzeba przeczytać raport końcowy sesji.
- **Sondy (zestaw 2):** usterki, o których kryteria milczą: S1 uprawnienia pliku danych po zapisie, S2 zapis przez dowiązanie symboliczne, S3 uprawnienia `.bak` prywatnego pliku, S4 układ pliku po wypożyczeniu i zwrocie. Raportowane osobno (k/4).
- **Koszt:** minuty, tokeny i rundy podajesz sam. Skrypt pokazuje wzmianki o rundach z `docs/TODO.md`.

## Jak czytać wyniki

Przy jednym przebiegu na konfigurację różnice o 1 zadanie albo kilkanaście procent czasu są w granicach przypadku.
Wnioski wyciągamy z dużych różnic. Tam, gdzie wyniki są bliskie, robimy drugi przebieg. Jakość (zadania, kolizja,
brak osłabionych testów) liczy się przed kosztem. Tańsza konfiguracja wygrywa tylko przy równej jakości.

## Wyniki serii 1 (zestaw 1, 2026-11-05)

Przebiegi A, B i D, po jednym, w kontenerze w chmurze przez `claude -p` (Opus jako główny model). Tabela
w [WYNIKI.md](WYNIKI.md).

- **Jakość:** wszystkie trzy 7/7, para kolidująca przeszła, bez osłabionych testów i rewertów.
- **Koszt:** zwykła sesja (A) 3,4 min i ~1 USD wg cennika API, kierownik (B, D) ~8,5 min i ~4 USD.
- **Wniosek:** zestaw 1 jest za łatwy. Siedem małych zadań w ~150 liniach mieści się w jednej sesji, więc
  kierownik może najwyżej zremisować w jakości. Na takich zadaniach płaci się tylko za narzut.
- B ≈ D, bo kierownik w B sam dał Sonnetowi 6/7 prostych zadań. Pytanie „Opus czy Sonnet” zostało bez
  odpowiedzi.
- Para T-006/T-007 poszła sekwencyjnie u obu kierowników, więc procedura konfliktu nie została sprawdzona.
- Artefakt zestawu: znacznik czasu w katalogu projektu (D) wymusił dodatkowy commit `.gitignore`.

Seria 2 używa trudniejszego zestawu 2 (`--zestaw 2`).

## Zestaw 2 — „biblioteka domowa”

Projekt `projekt2/` jest większy (kilka modułów: model, magazyn, wyszukiwanie, import/eksport, CLI), a etap E2 ma
12 zadań T-101…T-112 dobranych tak, żeby jakość mogła się rozjechać:

| Cecha | Zadania | Co sprawdza ukryty test |
|---|---|---|
| zmiana przekrojowa | T-101 ISBN-13 | model, zapis, import, eksport, szukanie i CLI naraz |
| przypadki brzegowe | T-102, T-103, T-109, T-112 | NFC/NFD, granica 30 dni w roku przestępnym, polska kolejność alfabetyczna, zaokrąglanie połówek |
| pułapka na testy | T-101, T-104 | najprostsza droga zmienia istniejący test (`test_zapis_zachowuje_uklad_pliku`), a kryterium tego zabrania |
| bezpieczeństwo | T-105, T-106 | formuły w CSV (także tabulator i CR), zapis atomowy z `.bak` przy awarii serializacji i `os.replace` |
| błędne założenie | T-107 | kryterium „rok obowiązkowy” przeczy danym i testom widocznym; test sprawdza tylko zakres i to, że książki bez roku dalej działają |
| kolizje | T-104, T-109, T-110, T-111 (i T-101 z T-105, T-107) | jawnie niezależne zadania zmieniające `lista`; `test_KOLIZJA.py` łączy wszystkie flagi |

Przebieg jak wyżej, z `--zestaw 2` w `przygotuj.py` i `ocen.py`. Polecenia startowe mówią o etapie E2:

- **A:** `Zrealizuj etap E2 z docs/TODO.md: zadania T-101…T-112 według ich kryteriów, każde z testem w tests/, z commitami na main. Plan jest zaakceptowany — nie pytaj o akceptację. Na koniec podsumuj, co zrobiłeś i jak to sprawdziłeś.`
- **B:** `Eval B: w tym etapie wyłącznie modele Claude (bez Codex i agy) i wykonawca zawsze w klasie MOCNY (opus), także w zadaniach prostych i w rundach poprawek; jednorazowo, nie zmieniaj rejestru. Plan E2 jest zaakceptowany — prowadź go do końca.`
- **C:** `Eval C: używaj rejestru jak zwykle, z Codexem jako recenzentem innej rodziny; bez agy (jednorazowo, nie zmieniaj rejestru). Plan E2 jest zaakceptowany — prowadź go do końca.`
- **D:** `Eval D: w tym etapie wyłącznie modele Claude (bez Codex i agy) i wykonawca zawsze w klasie STANDARDOWY (sonnet), także w rundach poprawek; jednorazowo, nie zmieniaj rejestru. Plan E2 jest zaakceptowany — prowadź go do końca.`

W ściądze odpowiedzi „E1” zamień na „E2” („po nim zakończ — nie planuj E3”).
- **E:** `Eval E: w tym etapie wyłącznie modele Claude (bez Codex i agy); jednorazowo, nie zmieniaj rejestru. Plan E2 jest zaakceptowany — prowadź go do końca.` Trybu etapu celowo nie narzucamy: sprawdzamy, czy kierownik sam wybierze zwarty.

## Wyniki serii 2 (zestaw 2, 2026-11-05/06)

Przebiegi A, B, D, po dwa, w kontenerze przez `claude -p` (Opus jako główny model). B z wykonawcą zawsze Opus,
D z wykonawcą zawsze Sonnet; recenzje w obu na Opusie, bo `fable` z rejestru nie był dostępny. Tabela
w [WYNIKI.md](WYNIKI.md).

| Konfiguracja | Zadania | Kolizja | Czas (śr.) | Koszt (śr., cennik API) | Rundy poprawek |
|---|---|---|---|---|---|
| A — sesja bez kierownika | 12/12, 12/12 | 2/2 | 6,9 min | 2,1 USD | — (bez recenzji) |
| B — kierownik, wykonawca Opus | 12/12, 12/12 | 2/2 | 19,1 min | 14,2 USD | 2 i 1 |
| D — kierownik, wykonawca Sonnet | 12/12, 12/12 | 2/2 | 17,9 min | 12,0 USD | 5 i 0 |

- **Jakość:** ukryte testy nie odróżniają konfiguracji. We wszystkich przebiegach jest 12/12, zaliczona kolizja,
  brak osłabionych i zmienionych testów, brak rewertów. Sprzeczność w T-107 zgłosił każdy przebieg. Kierownik
  zapisał przed startem „kryteria v2”, a A napisał o sprzeczności w commicie i raporcie.
- **Koszt:** kierownik jest ~2,7× wolniejszy i ~6× droższy od zwykłej sesji. W D większość kosztu to Opus jako
  kierownik i recenzent; Sonnet kosztował 1,5–1,8 USD na przebieg.
- **Opus czy Sonnet jako wykonawca:** jakość wyszła równa. D jest ~15% tańszy, ale miał więcej rund. W D-1
  T-106 potrzebował 3 rund i diagnozy architekta, a kierownik przy poprawce zawęził test T-105 (wyłapała to
  recenzja). Przy dwóch przebiegach to wskazówka, nie wynik.
- **Procedura konfliktu:** tym razem sprawdzona. Kierownik puszczał zadania równolegle, konflikty w `cli.py`
  rozwiązywał przy scalaniu, a połączenie flag `lista` przeszło we wszystkich przebiegach.
- **Poza ukrytymi testami:** recenzja wyłapała prawdziwe usterki — plik danych z uprawnieniami 0600 po zapisie
  atomowym, zastąpione dowiązanie symboliczne, jawnie pusty `--rok`, ISBN bez neutralizacji w eksporcie.
  Sprawdzenie wszystkich kopii po fakcie pokazało jednak, że recenzja nie robi tego stale: 0600 zostało
  w A-2 i D-2 (i we wzorcu, poprawionym po serii), a dowiązanie zachował tylko B-1.
- **Przerwy:** dwa równoległe przebiegi kierownika razem z A wyczerpały 5-godzinny limit konta. B-1 i D-1
  dokończono przez `--resume` po resecie; czas i koszt są łączne. B-2 i D-2 puszczono od nowa.
- **Poprawka zestawu:** ukryty test T-108 wymagał dokładnej linii potwierdzenia, a kryterium mówi tylko
  „linią `formatuj()`”. Oba kierowniki wypisywały `Wypożyczono: …` i oblewały ten test. Od c16b091 test
  dopuszcza przedrostek; wszystkie przebiegi oceniono po tej zmianie.

**Wniosek:** w projekcie tej wielkości (~1 tys. linii, 12 zadań, jedna sesja) zwykła sesja Opus daje tę samą
jakość mierzoną testami akceptacyjnymi za ~1/6 kosztu. Kierownik pokazuje swoją pracę — recenzja, rundy, zgłoszone
sprzeczności, rozwiązane konflikty — ale na tym zestawie nie przekłada się to na wynik. Nie zmierzyliśmy tego,
po co powstał: projektu, który nie mieści się w jednej sesji (wiele etapów, przejęcie pracy, kontekst ponad
okno). Następny eval powinien być wieloetapowy (E1→E3 w osobnych sesjach), a do oceny warto dodać sondy
usterek spoza kryteriów (uprawnienia, dowiązania), żeby zmierzyć, co wnosi recenzja.

## Wyniki serii 3 (zestaw 2, tryb zwarty, 2026-11-06)

Konfiguracja E: kierownik z trybem zwartym i listą regresji w recenzji (decyzja 15 w `claude/ANALIZA.md`), dwa
przebiegi w kontenerze jak w serii 2. Trybu nie narzucaliśmy — kierownik w obu przebiegach sam wybrał zwarty
(„12 małych zadań w ~400 liniach kodu, jedna sesja wykonawcy, bez decyzji projektowych”).

| Konfiguracja | Zadania | Kolizja | Sondy (śr. z 4) | Czas (śr.) | Koszt (śr., cennik API) | Rundy |
|---|---|---|---|---|---|---|
| A — sesja bez kierownika | 12/12, 12/12 | 2/2 | 2,5 | 6,9 min | 2,1 USD | — |
| B — kierownik, wykonawca Opus | 12/12, 12/12 | 2/2 | 3,5 | 19,1 min | 14,2 USD | 1,5 |
| D — kierownik, wykonawca Sonnet | 12/12, 12/12 | 2/2 | 2,0 | 17,9 min | 12,0 USD | 2,5 |
| **E — kierownik, tryb zwarty** | 12/12, 12/12 | 2/2 | **4,0** | 19,6 min | **4,9 USD** | 1 |

- **Jakość:** E ma pełny wynik zadań i jako jedyna konfiguracja oba przebiegi 4/4 w sondach. W obu przebiegach
  recenzja całości zwróciła T-106, bo zapis zastępował dowiązanie symboliczne, i wykonawca to poprawił w jednej
  rundzie.
- **Koszt:** ~1/3 trybu pełnego (4,9 wobec 14,2 USD) i ~2,3× zwykłej sesji. Czas jak w trybie pełnym, bo jeden
  wykonawca robi zadania po kolei.
- **Zastrzeżenie:** lista regresji powstała z usterek serii 2, a sondy sprawdzają te same kategorie
  (uprawnienia, dowiązania). Część przewagi E może wynikać z listy, nie z trybu — B i D jej nie miały. Czy
  efekt jest ogólny, pokaże sonda z kategorii, której lista nie wymienia, albo nowy zestaw.
- **Środowisko:** pierwsza próba E-1 przerwała się, bo Claude Code przeniósł długiego wykonawcę etapu w tło,
  a `claude -p` ubija zadania w tle 10 minut po ostatniej turze. W sesji interaktywnej powiadomienie budzi
  kierownika, więc to cecha uruchomienia bezobsługowego. Przebiegi bezobsługowe uruchamiamy od tej pory
  z `CLAUDE_CODE_PRINT_BG_WAIT_CEILING_MS=0`; E-1 powtórzono od zera.

**Wniosek:** dla etapów mieszczących się w jednej sesji tryb zwarty daje co najmniej jakość trybu pełnego za
~1/3 kosztu. Zwykła sesja jest tańsza, ale zostawia usterki, których kryteria nie nazywają. Tryb zwarty zostaje
domyślnym wyborem kierownika dla takich etapów. Do zmierzenia zostaje tryb pełny na etapach większych niż jedna
sesja (zestaw 3, wieloetapowy).
