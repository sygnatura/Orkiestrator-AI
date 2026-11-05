# ANALIZA I DECYZJE (v10–v13)

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
| Kierownik „ustawia effort” subagentowi, którego ustawić nie może | Założenie, że effort jest parametrem wywołania | (v10) Effort tylko we frontmatter agentów; przy wywołaniu zmienia się wyłącznie klasę modelu. (v13) Claude Code ≥ 2.1.292 przyjmuje `effort` przy wywołaniu — kierownik go podaje (decyzja 14) |


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
   - Recenzent zostaje na effort `high` (decyzja właściciela: recenzja odpowiada za jakość, która w v10
     się sprawdziła; `medium` rozważyć dopiero na danych z pilota). Ryzyko ŚREDNIE/WYSOKIE → recenzent
     NAJMOCNIEJSZY. Kierownik uruchamia własne testy przed scaleniem tylko wtedy, gdy
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
   Czego nie zmierzono: rzeczywistej liczby tokenów w sesji — pilot to pokaże (pole tokenów w „Zrobione”).


13. **(v12) Zespół wielu dostawców.** W v10–v11 Codex i `agy` były zapasem i wybiórczą recenzją, więc
   w praktyce kierownik zmieniał tylko klasy modeli Claude, a recenzję każdej pracy klasy MOCNY robił Fable —
   najdroższy model, z limitu Claude. Właściciel chce zestawu niezależnego od dzisiejszych subskrypcji. Zmiany:
   - **Rejestr runnerów** `~/.kierownik/ZESPOL.md`, jeden na maszynę i wspólny dla kierownika w Claude Code
     i w Codex (limit zapisany przez jednego zna drugi). Wiersz = sposób wykonania pracy: rodzina, modele →
     klasy, priorytet właściciela, stan limitu, sprawdzone polecenie CLI. Nowa lub anulowana subskrypcja to
     zmiana wiersza; procedury (`ZESPOL_PROCEDURY.md`), uruchamianie CLI (`URUCHAMIANIE_CLI.md`) i wzór (`ZESPOL_WZOR.md`)
     są identyczne w obu pakietach (pilnuje tego test w `codex/tests`). Stan limitu jest zapisywany przy modelu
     (gdy komunikat go wskazuje) albo przy subskrypcji, nie przy runnerze — limit Fable nie blokuje Opus
     i Sonneta, a limit Claude zapisany przez jednego hosta blokuje też `claude-cli` u drugiego.
   - **Routing według wymagań roli** (klasa + preferowana rodzina), nie nazw narzędzi. Kolejność: wymagana
     inna rodzina przed priorytetem (niezależność ważniejsza od ceny), potem priorytet subskrypcji, potem
     host, potem na zmianę. Brak kandydata → najpierw klasa wyżej, potem niżej z zapisem. Limit → to samo zlecenie do następnego kandydata; brak kandydata → obniżenie
     o jeden krok z zapisem; zatrzymanie dopiero, gdy nikt nie może pracować albo limit ma dostawca samego
     kierownika — wtedy LIMIT HANDOFF do drugiego hosta (stan w Gicie, gotowe polecenie startowe). Recenzent CLI
     zawsze oznacza własne testy kierownika (narzędzie może po cichu pominąć polecenia).
   - **Inna rodzina jako domyślny recenzent pracy klasy MOCNY** i zadań ryzykownych; brak → ta sama klasa
     z wyjątkiem v10. Większa niezależność niż „klasa wyżej w tej samej rodzinie” i inny limit niż Claude.
   - **Fable tylko w rzadkich, decydujących krokach**: plan etapu, przejęcie, trudna diagnoza, „plan pod
     znakiem zapytania”, weryfikacja celu etapu. Architekt domyślnie w MOCNY.
   - Po recenzji innej rodziny (Codex): rodzina należy do modelu, nie subskrypcji; limit bez czasu odnowienia
     to szacunek +5 h z podwajaniem; każde zlecenie podaje model jawnie (zmiana mapowania = tylko rejestr);
     tryb bez sandboxa (`agy --dangerously-skip-permissions`) tylko za zapisaną zgodą właściciela; katalog
     roli dla każdej roli CLI, także odczytowych i etapu, oraz tryb cloud; recenzent CLI z zapisem do własnego
     katalogu i kontrolą niezmienności; wykonawca CLI, któremu sandbox nie pozwala na commit, zostawia zmiany,
     a commit robi kierownik; wiersz W TOKU przed każdym zleceniem i LIMIT HANDOFF jako „best effort” —
     drugi host odzyskuje pracę z ostatniego punktu kontrolnego; WZNOWIENIE nie usuwa worktree zadania,
     które może jeszcze działać w innej sesji.
   - Po pilocie: kierownik pominął Codex przy zadaniu o ryzyku ŚREDNIM (recenzja Opus pracy Sonneta). Zmiany:
     wpis „przydział” w `TODO.md` przed każdym zleceniem (wymusza przejście przez regułę i jest widoczna dla
     właściciela) oraz inna rodzina jako pierwszy recenzent KAŻDEGO zadania — przy subskrypcji Codex, która
     odnawia się szybko, i rzadkim limicie Claude to zabiera sesję Opus z każdej recenzji. Koszt: kierownik
     częściej przygotowuje katalog recenzenta CLI i uruchamia własne testy.
   Ograniczenia: kierownik zawsze działa w jednym hoście i zatrzymuje się razem z jego dostawcą; stanu limitu
   nie da się sprawdzić z góry, tylko zapisać po komunikacie; recenzja przez CLI kosztuje więcej pracy
   kierownika (worktree `-rec`, zależności, plik zlecenia) i jest wolniejsza; `agy` działa bez sandboxa.
14. **(v13) Mocniejszy wykonawca, effort przy wywołaniu, zgoda na `agy` na maszynie.** Przegląd v12
   (2026-10-27) wskazał:
   - **Wykonawca domyślnie w MOCNY (Opus, effort medium).** Opus 5.5 kosztuje dziś tylko 2× Sonnet 5.5
     ($4/$20 wobec $2/$10 za 1M tokenów), a nieudana runda poprawek kosztuje znacznie więcej niż różnica
     ceny: drugie zlecenie, ponowną recenzję innej rodziny, worktree i kontekst kierownika. Anthropic
     zaleca liczyć koszt ukończonego zadania, nie pojedynczego wywołania. STANDARDOWY (Sonnet) zostaje dla
     prostych zadań: ryzyko NISKIE, typowa trudność, kryteria sprawdzalne jednym poleceniem. Każda poprawka
     po nieudanej rundzie → MOCNY. „Zrobione” zapisuje klasę wykonawcy i liczbę rund — po kilku etapach
     decyzję da się zweryfikować liczbami.
   - **Recenzja pracy klasy MOCNY**: inna rodzina; bez niej NAJMOCNIEJSZY (Fable) tylko przy
     bezpieczeństwie, danych, pieniądzach i kontraktach zewnętrznych, w pozostałych przypadkach wyjątek
     „recenzja tą samą klasą” z testami kierownika — tak, żeby mocniejszy wykonawca nie zużywał limitu Fable.
   - **Effort przy wywołaniu** (Claude Code ≥ 2.1.292): trudniejsze zadanie najpierw dostaje wyższy effort,
     klasa rośnie, gdy potrzeba większych możliwości. Linia „przydział” może podać `effort <poziom>`.
   - **Zgoda na `agy` bez sandboxa** nie jest już we wzorze rejestru: kierownik pyta o nią raz na maszynie
     i zapisuje odpowiedź z dopiskiem „(potwierdzona na tej maszynie)”; zgoda skopiowana ze starszego wzoru
     się nie liczy. Wzór `settings.json`: `agy` i destrukcyjne formy `git checkout`/`git restore` w `ask`.
   - `/autocompact` jest udokumentowane (Claude Code ≥ 2.1.221) i zapisuje się w ustawieniach użytkownika,
     więc obowiązuje we wszystkich projektach; opis w README i SZABLONY to mówi.
   - **Mechanika gita w skrypcie `scripts/kier.py`** (wspólny, bajtowo identyczny w obu pakietach). Anthropic
     zaleca, żeby przewidywalne kroki wykonywał kod, a model podejmował decyzje; skrypt skilla działa bez
     wczytywania do kontekstu. `env`, `worktree`, `ro-check`, `merge`, `cleanup`, `fix-round`, `sync`, `test`
     zastąpiły ~60 linii poleceń w SKILL.md (443 → ~375 linii) i są pokryte testami (`tests/test_kier.py`).
     Czerwone testy po scaleniu: lokalne, niewypchnięte scalenie jest cofane (`reset --keep`) zamiast
     `revert -m 1` — bez rewertów w historii i bez „rewertu rewertu” przy ponownym scaleniu; rewert z v12
     w historii `merge` przywraca sam.
   - **Konflikt przy scalaniu** (do 4 równoległych wykonawców) ma procedurę: `merge` przerywa z kodem 4,
     `sync` scala main do gałęzi zadania, trywialny konflikt rozwiązuje kierownik, inny — wykonawca (wiersz
     KONFLIKT w zleceniu A); ponowna recenzja tylko, gdy rozwiązanie dotyka logiki.
   - **Ścieżka szybka**: prostą pracę klasy STANDARDOWY (ryzyko NISKIE, typowa) recenzuje host o klasę wyżej
     plus testy kierownika, bez obowiązkowej innej rodziny — tańsza pętla tam, gdzie niezależność rodziny
     niewiele daje. Nie dotyczy bezpieczeństwa, danych, pieniędzy, kontraktów, rund poprawek i sprzecznych
     sygnałów.
   - **Recenzja CLI nie jest odrzucana przez cache testów**: liczą się HEAD, pliki śledzone i wcześniejsze
     pliki nieśledzone; nowe nieśledzone są zgłaszane jako UWAGA.
   - **Straż spójności** `tests/test_spojnosc.py`: wspólne pliki identyczne, słowa protokołu, pola zleceń
     i skróty w obu pakietach, każde wspomniane podpolecenie `kier.py` istnieje, limit długości SKILL.md.
   - **v13.1 — po recenzji Codex (Windows)**: `kier.py` nie nadpisuje plików ignorowanych (scalenie odmawia,
     gdy gałąź dodaje plik istniejący lokalnie) i nie kasuje pracy przy sprzątaniu (usuwa tylko wyjście
     odtwarzalne: cache, build, zależności); polecenia testów wyłącznie z AGENTS.md na main — reguła allow
     dla skryptu nie otwiera już dowolnych poleceń; wcześniejsze scalenie rozpoznawane po temacie
     `merge(T-NNN)`, więc cudzy rewert nie wraca; testy zmieniające pliki śledzone → wynik niewiarygodny,
     zmiany w stashu, scalenie cofnięte; recenzent dopisujący pliki źródłowe traci werdykt; bez ustalonej
     gałęzi głównej odmowa zamiast zgadywania (`--main`); poprawne dopisywanie do `info/exclude`; sumy
     instalatora niezależne od CRLF i `.gitattributes` z LF; zgoda na `agy` powiązana z nazwą hosta.
   - **v13.2 — druga recenzja Codex**: „odtwarzalne” nie wynika już z dowolnego katalogu w ścieżce. `CACHE`
     (node_modules, .venv, __pycache__, .pytest_cache…) jest odtwarzalne zawsze, `OUTPUT` (build, dist,
     target, coverage…) tylko wtedy, gdy projekt je ignoruje — nieignorowany `build/x.py` to praca: sprzątanie
     go nie usuwa, a recenzent, który go dopisze, traci werdykt. Kontrola kolizji sprawdza też rodziców
     ścieżki (ignorowany plik tam, gdzie gałąź dodaje katalog) i czyta nazwy z `-z`, więc polskie znaki
     nie omijają ochrony.
   - **v13.3 — trzecia recenzja Codex**: kontrola kolizji obejmuje każde polecenie, które przesuwa katalog
     roboczy na inny commit (`move_to`): fast-forward w `env`, odświeżenie katalogu recenzenta i cofnięcie
     scalenia (`reset --keep`), a nie tylko scalanie. Reguła zapisana w nagłówku `kier.py`.
   - **v13.4 — czwarta recenzja Codex**: przywracanie rewertu używa tej samej kontroli kolizji (z rodzicami
     ścieżki), a cofanie po testach najpierw sprawdza, czy stash i reset nie nadpiszą czegoś, co testy zostawiły
     w katalogu — jeśli tak, nic nie rusza i kończy kodem 2 z opisem stanu. (v13.5) Lista ścieżek do sprawdzenia
     pochodzi z `git diff --no-renames HEAD`, więc obejmuje też źródła `git mv` i usunięcia z indeksu.
   - **v13.6 — systematyczny przegląd Codex**: każde `git -C` na katalogu z `.kierownik/wt/` albo z argumentu
     wymaga zarejestrowanego worktree (zwykły katalog trafiałby w główne repozytorium i odłączał jego HEAD);
     `merge/revert --abort` wykonywany tylko wtedy, gdy niczego nie nadpisze — inaczej konflikt zostaje
     otwarty (exit 4) i skrypt już nie twierdzi, że main jest bez zmian; po stashu druga kontrola przed
     `reset --keep`. **Ograniczenie:** kontrole biegną tuż przed zapisem, ale proces działający równolegle
     (hook gita, edytor, drugi agent) może zapisać plik w tej samej chwili — ten wyścig jest zawężony, nie
     wykluczony. Nie uruchamiaj hooków ani narzędzi, które piszą do katalogu repozytorium, w trakcie `kier.py`.
   - **v13.7 — kolejna recenzja Codex**: weryfikacja katalogu przeniesiona do samego `git()` — każde
     wywołanie na katalogu innym niż główny checkout najpierw sprawdza, że to zarejestrowany worktree, bez
     dowiązań i junction po drodze i nie główny checkout (dotąd było dopisywane punktowo i `sync`/`cleanup` je
     omijały). Konflikty wykrywa `git merge-tree --write-tree` bez zapisu na dysk (git ≥ 2.38), więc przy
     konflikcie scalenie się nie zaczyna i nie ma czego przerywać. Na starszym gicie abort tylko bez plików
     konfliktowych, inaczej konflikt zostaje otwarty. Ograniczenie z v13.6 zawęża się do równoległego zapisu
     przez inny proces w ułamku sekundy przed zapisem gita.
   - **v13.8**: po jednej walidacji każde polecenie gita dostaje jawne `--git-dir` (katalog administracyjny
     worktree, sprawdzony w `.git/worktrees/` tego repozytorium) i `--work-tree`. Git niczego już nie wykrywa
     z plików na dysku, więc przeniesienie albo podmiana `.git` w trakcie działania (np. przez hook) nie
     przekieruje polecenia do głównego checkoutu.
   - **v13.9 — pilot**: kierownik odpowiedział na pytanie właściciela w trakcie etapu, zakończył turę z
     wykonawcą w tle i nie podjął jego wyniku. Przyczyna w prompcie: „czekaj na powiadomienie” bez zasady na
     koniec tury i bez odzyskiwania. Teraz: nie kończ tury, gdy działają Twoje zlecenia (poza zatrzymaniem z §13),
     pytanie właściciela to nie zatrzymanie, a każda tura zaczyna się od zebrania zakończonych zleceń
     (`dalej` robi to samo). Druga przyczyna z tego samego pilota: wykonawca uruchomił testy w tle i skończył
     komunikatem „czekam na zadania w tle” zamiast raportu (commity już były). Role dostały zasadę: wszystko na
     pierwszym planie, koniec tylko raportem; kierownik wynik bez raportu traktuje jako niedokończony
     i sprawdza worktree. Trzecia przyczyna (dokumentacja Claude Code, sub-agents: „Let Claude wait for a
     subagent”): w sesji interaktywnej fork mode jest domyślnie włączony i każdy subagent startuje w tle, a jego
     wynik przychodzi w późniejszej turze. Wzór `settings.json` (SZABLONY §8) wyłącza go przez
     `CLAUDE_CODE_FORK_SUBAGENT=0`. `status` i `stop` mają pierwszeństwo przed zbieraniem wyników.
   - **Evale** (`evals/`, opis w `evals/README.md`): projekt testowy z 7 zadaniami (w tym bezpieczeństwo
     i para kolidująca), ukryte testy akceptacyjne, rozwiązanie wzorcowe sprawdzane w CI oraz skrypty
     przygotowania, oceny i zestawienia. Konfiguracje A (sesja bez kierownika), B (kierownik, Claude),
     C (kierownik + Codex), D (wykonawca Sonnet). Przebiegi wykonuje właściciel; wyniki w `evals/WYNIKI.md`.
   Dalej (niezrobione): rejestr i routing w kodzie (`kier.py zespol/route/limit`); tryb PR z CI.

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
- Effort subagenta przy wywołaniu działa od Claude Code 2.1.292; starsza wersja go ignoruje i obowiązuje
  wartość z pliku agenta (wtedy eskalacja to zmiana klasy).
- Zapasowe `codex exec` i `agy` wymagają zalogowania i działania bez interakcji na tej maszynie —
  kierownik sprawdza to testem dymnym przy pierwszym uruchomieniu.
- `agy --dangerously-skip-permissions` to agent bez żadnych pytań o zgodę i bez sandboxa. Worktree
  porządkuje zmiany w repozytorium, ale nie ogranicza dostępu do maszyny. Producent zaleca kontener
  lub sandbox — kierownik używa tego trybu tylko po zgodzie właściciela zapisanej na tej maszynie. Bez flagi `agy -p` po cichu
  pomija polecenia powłoki (kod 0, komunikat tylko na stderr) — stąd obowiązek czytania stderr.
- v10 działała u właściciela na prawdziwym projekcie poprawnie, ale kosztownie — to był powód v11.
  v11 nie przeszła jeszcze pilota. Zalecany: jeden etap na projekcie prowadzonym wcześniej na v10;
  porównać tokeny na zadanie („Zrobione”) i to, czy weryfikacja celu etapu znajduje błędy przepuszczone
  przez recenzenta zadania.


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
i skilli, worktree, aliasy modeli, effort, uprawnienia) sprawdzone w dokumentacji 2026-10-06; effort przy wywołaniu subagenta i `/autocompact` — 2026-10-27.
Poprzednia analiza (v7) z oceną materiałów wejściowych: archiwum/ANALIZA_v7.md.
