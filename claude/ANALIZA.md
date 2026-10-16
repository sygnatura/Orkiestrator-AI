# ANALIZA I DECYZJE (v10–v11)

Do czytania, gdy chcesz zmieniać system. Do codziennej pracy niepotrzebne.


## 1. Czego oczekuje właściciel

Kierownika technicznego, któremu można powierzyć projekt: rozumie system, ma ciągłość między
sesjami bez tłumaczenia od nowa, sam deleguje i sprawdza pracę, scala zweryfikowane zmiany,
pyta tylko o decyzje właściciela, nie dryfuje, nie przeinżynierowuje — i nie rozdyma własnego
wątku, bo to najdroższy zasób (każde wczytanie zjada limit, a pełny kontekst pogarsza decyzje).
Zestaw ma być w pełni zgodny z mechaniką Claude Code i nie może być przypisany do dzisiejszych modeli.


## 2. Lekcje z poprzednich wersji (dlaczego zawodziły)

| Objaw w praktyce | Przyczyna w prompcie | Zmiana |
|---|---|---|
| Kierownik ma słabe pojęcie o projekcie, decyzje mylące | Zakaz czytania kodu i uruchamiania testów; w repo tylko cel (VISION) i lista zadań (TODO), brak opisu działania systemu | (v8) `docs/PROJEKT.md` — opis systemu budowany przez subagentów przy przejęciu i aktualizowany po każdym etapie; kierownik może czytać i uruchamiać wszystko |
| Pyta o zgodę na testy z „płatnym LLM”, choć projekt używa lokalnego | Brak faktów o środowisku + granice „pytaj, gdy może kosztować” bez obowiązku sprawdzenia | (v8) Sekcja „Środowisko i koszty” w PROJEKT.md i AGENTS.md; zasada „zanim zapytasz, sprawdź, czy ryzyko jest realne” |
| Nic nie może zrobić, o wszystko pyta | Granice oparte na nieufności (edytuje tylko TODO.md, uruchamia tylko odczyt, merge/push robi właściciel) | (v8) Autonomia według ryzyka: lista „robisz sam” / „pytasz”; scalanie i push zweryfikowanych zmian bez pytania |
| Nie wywołuje subagentów, właściciel kopiuje zlecenia | Model „właściciel jako kurier” | (v8) Kierownik sam uruchamia subagentów Claude i CLI |
| Każdy nowy wątek = wklejanie 30 KB promptu | Prompt jako wklejka | (v8) Skill `/kierownik` instalowany raz; nowy wątek = `/clear` + `/kierownik` |
| Oszczędzanie kontekstu przez niewiedzę | „Czytaj tylko `git --stat`” | (v8) Oszczędzanie przez delegowanie: ciężkie czytanie robią subagenci, do kierownika wracają streszczenia |
| Po wyjściu nowego modelu trzeba poprawiać pięć plików; recenzent „inny model niż autor” przestaje być jednoznaczny | Nazwy i wersje modeli (Opus 5.5, Fable 5.1) wpisane w SKILL.md, README, ZESPOL.md, ANALIZA | (v10) Klasy modeli; mapowanie klasa → alias tylko w ZESPOL.md (decyzja 9) |
| Pętla poprawek i recenzja nie działają z worktree subagentów | Instrukcje zakładały, że subagent wraca do tego samego worktree, odgałęzia się od lokalnego main i że jedną gałąź da się wyewidencjonować w dwóch worktree | (v10) Przepływ Git napisany pod faktyczną mechanikę `isolation: worktree` (decyzja 10) |
| Kierownik „ustawia effort” subagentowi, którego ustawić nie może | Założenie, że effort jest parametrem wywołania | (v10) Effort tylko we frontmatter agentów; przy wywołaniu zmienia się wyłącznie klasę modelu |


## 3. Kluczowe decyzje (v8–v10)

1. **Skill zamiast promptu.** `disable-model-invocation: true` sprawia, że opis skilla nie trafia
   do kontekstu innych sesji, a treść ładuje się tylko po `/kierownik`. Pliki pomocnicze
   (ZESPOL, ZLECENIA, SZABLONY) ładują się na żądanie z `${CLAUDE_SKILL_DIR}`. SKILL.md zakłada narzędzia
   Claude Code (subagenci `kier-*`, worktree, komendy `/…`), więc inny agent nie poprowadzi według niego
   projektu; zapas (Codex, `agy`) działa wyłącznie w rolach wykonawcy i recenzenta (SKILL.md, sekcja 7).
2. **Dwa pliki stanu projektu**: PROJEKT.md (jak działa system — zmienia się wolno) i TODO.md
   (plan i stan — zmienia się po każdym zadaniu). VISION.md wchłonięty przez PROJEKT.md.
3. **Claude Max jako główny zespół.** Przy dużym zapasie limitów Claude cała pętla działa na subagentach
   Claude Code z klasą modelu dobraną do roli: analityk STANDARDOWY (trywialne pytania → SZYBKI),
   wykonawca STANDARDOWY/MOCNY, recenzent MOCNY/NAJMOCNIEJSZY, architekt NAJMOCNIEJSZY, kierownik MOCNY
   (mapowanie klas na aliasy Claude Code: kierownik/ZESPOL.md). Subagenci są zdefiniowani w
   `agents/kier-*.md` (model, effort, narzędzia, worktree), więc zlecenia są krótkie, a zasady ról nie
   rozjeżdżają się między sesjami.
4. **Niezależność weryfikacji w jednej rodzinie**: recenzent to model klasy wyżej niż autor
   (STANDARDOWY → MOCNY, MOCNY → NAJMOCNIEJSZY), świeży kontekst, tylko kryteria + diff + polecenia —
   wzorzec recenzji zalecany przez Anthropic. Gdy klasa NAJMOCNIEJSZY jest poza limitem, pracę klasy
   MOCNY recenzuje ta sama klasa (świeży kontekst, testy uruchomione przez kierownika) i jest to
   odnotowane. Recenzja innej rodziny (Antigravity / Codex) jest wybiórcza: bezpieczeństwo, dane,
   pieniądze, kontrakty zewnętrzne, sprzeczne sygnały nierozstrzygnięte przez klasę NAJMOCNIEJSZY, dwie
   nieudane rundy, cel etapu kluczowego dla MVP. Codex i Antigravity są też zapasem, gdy Claude jest
   niedostępny; wybór zawsze według stanu limitów w ZESPOL.md — schemat nie zakłada wolnego limitu
   żadnego z nich.
5. **Pięć statusów**: TODO, W TOKU, DO SPRAWDZENIA, GOTOWE, ZABLOKOWANE. Status „do scalenia”
   zniknął, bo kierownik scala sam zaraz po weryfikacji. Werdykt recenzenta ma trzy wartości:
   ZALICZONE, DO POPRAWY (są uwagi blokujące), ZABLOKOWANE (kryterium niesprawdzalne — kierownik usuwa
   przeszkodę i powtarza recenzję).
6. **Uwagi recenzenta BLOKUJĄCE vs OPCJONALNE** — tylko blokujące wracają do poprawy (Anthropic:
   recenzent zawsze coś znajdzie, gonienie wszystkiego prowadzi do przeinżynierowania). Dowodem jest
   polecenie uruchomione w sesji recenzenta; kryterium bez dowodu to NIE SPRAWDZONO, nie OK.
7. **Punkt kontrolny po każdym zadaniu** (commit TODO.md) — wątek można zamknąć w dowolnej chwili.
8. **AGENTS.md jako jedyne źródło zasad, CLAUDE.md = `@AGENTS.md`** — zgodnie z aktualną
   dokumentacją obu firm (szczegóły: kierownik/SZABLONY.md, sekcja 1). Subagenci Claude dostają
   CLAUDE.md projektu automatycznie, także w worktree, więc zlecenia dla nich nie powtarzają zasad.
9. **(v10) Klasy modeli zamiast nazw.** Nazwy i wersje modeli wpisane w prompty degradują się po
   każdym nowym wydaniu (Anthropic, prompt-audit), a aliasy Claude Code (`haiku`, `sonnet`, `opus`,
   `fable`) wskazują zawsze najnowszy model danej linii. Dlatego SKILL.md, README i szablony mówią
   o klasach SZYBKI / STANDARDOWY / MOCNY / NAJMOCNIEJSZY, a jedyne mapowanie klasa → alias → model —
   wraz z effortem ról i procedurą aktualizacji po wyjściu nowego modelu lub nowej linii — jest
   w ZESPOL.md. Poza nim alias stoi tylko tam, gdzie wymaga go Claude Code albo jedno polecenie dla
   właściciela: `model:` we frontmatter `agents/kier-*.md`, parametr `model` narzędzia Agent przy nadpisaniu
   domyślnej klasy oraz `/model <alias>` w README i jego trwały odpowiednik `"model"` we wzorze settings.json
   (oba obejmuje procedura z ZESPOL.md, gdy zmienia się alias klasy MOCNY); pozostałe wzmianki to przykłady,
   nie routing. Effort żyje
   wyłącznie we frontmatter agentów (Claude Code nie ma go w parametrach wywołania). Nowa wersja
   w tej samej linii = zero zmian; nowa linia = jedna tabela w ZESPOL.md i pole `model:` u agentów tej
   klasy. Poziomy effort dobrane według zaleceń Anthropic dla obecnej generacji: `high` tylko dla
   recenzenta i architekta (plan to długi dokument — `xhigh` podwaja tokeny bez zmierzonego zysku),
   `medium` dla wykonawcy i analityka (zalecany punkt wyjścia dla agentowego kodowania; `low` pomija
   weryfikację), effort kierownika domyślny dla modelu.
10. **(v10) Przepływ Git pod mechanikę worktree Claude Code.** Subagent z `isolation: worktree`
   dostaje za każdym razem nowy worktree w `.claude/worktrees/<nazwa>` na gałęzi `worktree-<nazwa>`,
   odgałęzionej domyślnie od `origin/HEAD` (nie od HEAD sesji), widzi tylko commity, a worktree
   z commitami nie znika sam. Stąd: wykonawca tworzy gałąź zadania jawnie od sha bazy ze zlecenia,
   kierownik commituje wszystko przed zleceniem i proponuje `worktree.baseRef: head`, przed rundą
   poprawek usuwa stary worktree (jedna gałąź nie może być w dwóch worktree), recenzent pracuje
   w worktree autora (CLI: w odłączonym worktree), scalenie i revert są dokładnym skryptem
   (`git revert -m 1`, revert rewertu przed ponownym scaleniem), sprzątanie obejmuje gałąź
   `worktree-*`, a `.claude/worktrees/` jest wykluczony z Gita.
11. **(v10) Jedno źródło; powtórzenia tylko świadome.** Mapowanie klasa → alias jest tylko w ZESPOL.md;
   domyślna klasa i effort roli działają we frontmatter `agents/kier-*.md`, a tabela ról w ZESPOL.md je
   streszcza (zmieniasz jedno, zmieniasz drugie). Routing klas do zadań prowadzi SKILL.md, sekcja 7 (bez
   aliasów i effortu); README podaje tylko domyślne klasy i odsyła do ZESPOL.md. Zasady wspólne dla wszystkich
   narzędzi (granice, Definition of Done, weryfikacja cudzej zmiany, wzór raportu) stoją w AGENTS.md projektu;
   definicje `kier-*` powtarzają z nich to, co dotyczy roli — żeby rola działała także bez kompletnego
   AGENTS.md — a szablony zleceń (ZLECENIA.md) tylko w wierszach `[CLI]` dla narzędzi zapasowych, które widzą
   wyłącznie AGENTS.md i zlecenie. Powtórzone reguły muszą orzekać to samo: zmiana reguły = oba miejsca.
   (v11: zmienione — patrz decyzja 12.)
12. **(v11) Optymalizacja tokenów.** Przegląd v10 pokazał, że największy koszt to nie długość wątku, tylko
   treść wczytywana stale, a rzadko potrzebna, powtórzenia i weryfikacja każdego zadania. Zmiany:
   - SKILL.md zawiera tylko rdzeń pętli; przejęcie/nowy projekt (`START_PROJEKTU.md`) oraz konfiguracja
     maszyny, zmiany zespołu i uruchamianie CLI (`ZESPOL_PROCEDURY.md`) czyta się tylko przy wyzwalaczu.
     `ZESPOL.md` zawiera wyłącznie stan. Numeracja sekcji SKILL.md została, żeby odsyłacze były ważne.
   - Instrukcje dla modeli po angielsku (polski tekst to wyraźnie więcej tokenów na tę samą treść).
     Komunikacja z właścicielem, pliki projektu, zlecenia i raporty po polsku; słowa protokołu (statusy,
     werdykty, pola zleceń, skróty) bez zmian — zgodność z istniejącymi projektami i portem Codex.
   - Zasady ról wyjęte z AGENTS.md (sekcje „Raport po zadaniu” i „Weryfikacja cudzej zmiany”): AGENTS.md
     wczytuje się w każdej sesji, także kierownika. Rola żyje w definicji `kier-*`, a dla CLI w wierszach
     `[CLI]` zlecenia. Definicja wykonawcy nie powtarza „Granic” i „Definition of Done” z AGENTS.md —
     zostawia tylko krótkie twarde ograniczenia na wypadek niepełnego AGENTS.md.
   - Recenzent na effort `medium`; głębię daje klasa (ryzyko ŚREDNIE/WYSOKIE → NAJMOCNIEJSZY), zgodnie
     z zasadą „zmień klasę, nie effort”. Kierownik uruchamia własne testy przed scaleniem tylko wtedy, gdy
     recenzja nie jest niezależną recenzją Claude klasy wyżej (wyjątek tej samej klasy, recenzent CLI, brak
     recenzenta, sprzeczne liczby) — inaczej dowodem są testy recenzenta i testy na main po scaleniu.
   - Testy kierownika: pełny log do `.kierownik/log/`, do kontekstu kod wyjścia i 30 linii; `| tail` gubił
     kod wyjścia testów.
   - `/autocompact 200k` zamiast 400k: próg wynika z kosztu tury, nie z rozmiaru okna; przekazanie wątku po
     ~8 zadaniach przychodzi dużo wcześniej.
   - `kier-wykonawca` ma jawną listę narzędzi (bez dziedziczenia wszystkich, w tym MCP).
   - Subagenci też kierują długie wyjście (instalacja zależności, testy, build) do logu w katalogu
     tymczasowym systemu i czytają kod wyjścia + końcówkę — pełny log w kontekście kosztuje w każdej
     kolejnej turze. Poza repozytorium, żeby `git status` recenzenta został czysty.
   - Pomiar: tokeny sesji wykonawcy i recenzenta zapisywane w „Zrobione”, suma w raporcie etapu.
   Czego nie zmierzono: rzeczywistej liczby tokenów w sesji i wpływu effortu `medium` na jakość recenzji.
   Pilot powinien to sprawdzić; przy gorszych recenzjach wróć do `high` (plik agenta + ZESPOL.md).


## 4. Czy to ma sens — uczciwa ocena

Ma sens, jeśli projekt trwa tygodnie i ma więcej niż kilka modułów. Rdzeń — stan i wiedza w plikach,
małe zadania z kryteriami, weryfikacja przez inny model, świeży kontekst zamiast długiego wątku —
to dokładnie to, co Anthropic i OpenAI opisują jako sprawdzone praktyki długiej pracy agentów.

Ograniczenia, o których trzeba wiedzieć:
- To nadal instrukcje dla modelu, nie program. Model może je łamać; dlatego ważne reguły mają
  zabezpieczenie techniczne (uprawnienia, ochrona gałęzi), a stan jest kontrolowalny w Gicie.
- Delegowanie ma narzut (zlecenie, worktree, instalacja zależności w świeżym worktree, raport,
  recenzja). Dla drobnych zmian kierownik robi je sam — inaczej system byłby wolniejszy niż zwykła
  sesja Claude Code.
- Weryfikacja w obrębie jednej rodziny (Claude → Claude) jest słabsza niż między rodzinami
  (wspólne ślepe punkty). Łagodzą to: klasa wyżej, świeży kontekst, testy uruchamiane niezależnie
  i recenzja innej rodziny w przypadkach ryzykownych.
- Duże okno kontekstu kusi, żeby nie przekazywać wątku. Koszt każdej tury i jakość decyzji nadal
  zależą od długości wątku — stąd przekazanie po etapie i bezpiecznik `/autocompact` (wartość
  w ZESPOL.md).
- Dla małego projektu lub jednorazowej zmiany wystarczy zwykła sesja Claude Code z trybem planu; kierownik
  zaczyna się opłacać, gdy ciągłość między sesjami staje się problemem.
- Effortu subagenta nie da się zmienić przy wywołaniu — tylko w pliku agenta. Eskalacja trudnego
  zadania to zmiana klasy modelu, nie effortu; to świadomy kompromis, żeby nie mnożyć definicji agentów.
- Zapasowe `codex exec` i `agy` wymagają zalogowania i działania bez interakcji na tej maszynie —
  kierownik sprawdza to testem dymnym przy pierwszym uruchomieniu.
- `agy --dangerously-skip-permissions` to agent bez żadnych pytań o zgodę i bez sandboxa. Worktree
  porządkuje zmiany w repozytorium, ale nie ogranicza dostępu do maszyny. Producent zaleca kontener
  lub sandbox — właściciel może wyłączyć `agy` jednym wpisem w ZESPOL.md. Bez flagi `agy -p` po cichu
  pomija polecenia powłoki (kod 0, komunikat tylko na stderr) — stąd obowiązek czytania stderr.
- v10 działała u właściciela na prawdziwym projekcie poprawnie, ale kosztownie — to był powód v11.
  v11 nie przeszła jeszcze pilota. Zalecany: jeden etap na projekcie prowadzonym wcześniej na v10;
  porównać tokeny na zadanie („Zrobione”) i to, czy weryfikacja celu etapu znajduje błędy przepuszczone
  przez recenzenta zadania (sygnał, że effort `medium` nie wystarcza).


## 5. Świadomie pominięte

Długie osobne prompty ról powielające wspólne zasady (rolę opisuje krótka definicja subagenta
`agents/kier-*.md`, zasady wspólne są tylko w AGENTS.md, zlecenia to szablony A–C z SKILL.md — zapas CLI
dostaje pełny szablon), osobne definicje agentów na każdy poziom effortu, PROJECT_WORKFLOW.md
w repozytorium, pliki REPORT/REVIEW dla każdego zadania, osobny PLAN.md, statusy DRAFT/READY/ACCEPTED,
lista funkcji w JSON, lokalny model w zespole, trwała pamięć subagentów (`memory:` w frontmatter —
wiedza ma być w plikach repo, nie w pamięci agenta), hooki „na wszelki wypadek”. Każdy z tych
elementów można dodać, gdy pojawi się konkretny problem, którego obecny układ nie rozwiązuje.


## 6. Źródła
Lista w kierownik/SZABLONY.md (sekcja „Źródła”). Fakty o mechanice Claude Code (frontmatter subagentów
i skilli, worktree, aliasy modeli, effort, uprawnienia) sprawdzone w dokumentacji 2026-10-06.
Poprzednia analiza (v7) z oceną materiałów wejściowych: archiwum/ANALIZA_v7.md.
