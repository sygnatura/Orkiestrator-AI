# ANALIZA I DECYZJE PROJEKTOWE (v7)

Dokument wyjaśnia, dlaczego zestaw wygląda tak, a nie inaczej. Nie jest potrzebny do codziennej
pracy — przydaje się, gdy chcesz coś zmienić w systemie i nie zepsuć tego, co działa.


## 1. Wymagania → kryteria oceny

| Wymaganie | Kryterium, po którym oceniałem warianty |
|---|---|
| Nowy projekt albo przejęcie istniejącego | Osobne ścieżki startu; przejęcie bez przebudowy repozytorium |
| Trwały plan i stan poza czatem | Po zamknięciu wątku nic nie ginie; stan da się odtworzyć z plików i Gita |
| Małe zadania, różne modele | Zlecenie samowystarczalne; rola → narzędzie → model |
| Niezależna weryfikacja | Weryfikator ≠ autor; dowód zapisany trwale |
| Po tygodniach: cel / plan / w toku / zweryfikowane / następny krok | Jedno miejsce, które odpowiada na pięć pytań w 30 sekund |
| Kontrola, ochrona przed dryfem | Bramki decyzyjne właściciela; pomysły nie wchodzą do planu same |
| Ochrona przed przeinżynierowaniem | Minimum plików i statusów; zasada YAGNI egzekwowana w weryfikacji |
| AGENTS.md / CLAUDE.md wg aktualnych wytycznych | Jedno źródło zasad, poprawne mechanizmy wczytywania |
| Orkiestrator pilnuje własnego kontekstu | Konkretne reguły czytania, limity raportów, wyzwalacze przekazania |


## 2. Ocena materiałów wejściowych

| Plik | Mocne strony (zachowane) | Słabe strony (poprawione) |
|---|---|---|
| ORKIESTRATOR_PROJEKTU.md (v6, „wszystko w jednym”) | Ostre granice roli (nie koduje, nie diagnozuje), SYGNAŁ STOP, szablony A/B/C, tryb szybkiego wznowienia, plan pod znakiem zapytania, weryfikacja celu etapu end-to-end, różne modele w planowaniu | Brak mechanizmu oszczędzania własnego kontekstu poza „gdy rozmowa traci spójność”; kryteria małych zadań żyły tylko w czacie; brak trwałego zapisu dowodu weryfikacji; „CLAUDE.md — tylko odsyłacz” (wg aktualnych wytycznych odsyłacz słowny jest słaby, potrzebny import `@AGENTS.md`); wzory plików wczytywane w każdej sesji orkiestratora, choć potrzebne rzadko; pełne czytanie wszystkich dokumentów przy przejęciu |
| ORKIESTRATOR_PROJEKTU_SDD.md + ARCHITEKT_PROJEKTU.md + PROJECT_WORKFLOW.md | Rozróżnienie „zweryfikowane na gałęzi” od „zintegrowane”; mapowanie istniejących procesów zamiast narzucania; poszanowanie istniejącego procesu Git; skróty `/status`, `/handoff`; specyfikacja przed implementacją | 4 pliki na każde zadanie (TASK, VERIFY, REPORT, REVIEW) — biurokracja także dla zadań 10-minutowych; 8 statusów; trzy dokumenty (PLAN, TODO, WORKFLOW) do synchronizacji → źródło rozjazdów; reguły powielone w trzech promptach; architekt rozpisuje pełne karty dla całego etapu z góry; gęsty, trudny do audytu język |

Wniosek: v6 ma lepszy rdzeń (prostota, granice), SDD wnosi kilka trafnych rozróżnień. Najlepszy
wynik to rdzeń v6 + wybrane elementy SDD + nowa warstwa zarządzania kontekstem + poprawne pliki
instrukcji.


## 3. Burza mózgów — warianty architektury systemu

| Wariant | Opis | Za | Przeciw |
|---|---|---|---|
| W1. Monolit | Jeden prompt ze wszystkim (v6) | Jedno źródło, łatwy start | Wzory plików zajmują kontekst każdej sesji; brak zarządzania kontekstem |
| W2. Prompty ról + wspólny kontrakt | Orkiestrator, architekt, workflow w repo (SDD) | Spójność ról, specyfikacje | 3 pliki do synchronizacji; biurokracja; duplikacja reguł |
| W3. Rdzeń + stan w repo + wzory na żądanie | Krótki stały prompt kierownika; stan w TODO.md; zasady wykonawców w AGENTS.md; wzory czytane tylko przy zakładaniu | Mały stały koszt; zlecenia krótsze, bo protokół raportu jest w AGENTS.md; jedno źródło na każdy temat | Dwa pliki zestawu zamiast jednego |
| W4. Pełna automatyka | Skrypty, lista funkcji w JSON, hooki, agenci uruchamiani programowo | Najsilniejsza kontrola techniczna | Wysoki koszt wejścia; zależność od jednego narzędzia; Ty tracisz wgląd |
| W5. Zewnętrzny tracker | GitHub Issues/Projects jako stan | Dobre dla zespołów ludzi | Nie każdy agent ma dostęp; stan oddzielony od kodu i historii Gita |

**Wybór: W3**, z opcjonalnym „trybem automatycznym” jako furtką do W4 i z zasadą „twarde reguły
→ zabezpieczenie techniczne” (hooki, uprawnienia, CI) zamiast przechodzenia od razu na W4.


## 4. Kluczowe decyzje i ich uzasadnienie

**D1. Jeden prompt kierownika + plik wzorów zamiast osobnego promptu architekta.**
Architekt jest uruchamiany przez samowystarczalne zlecenie C, które niesie wszystkie potrzebne mu
reguły (proponuje, nie aktywuje; najprostszy wariant; format zadań). Osobny długi prompt
architekta dublowałby reguły i rozjeżdżał się z promptem kierownika — dokładnie to był problem
pakietu SDD.

**D2. Jeden rejestr: docs/TODO.md, z nagłówkiem odpowiadającym na pięć pytań.**
Cel, etap, ostatni zweryfikowany commit, zadanie w toku, blokady i następny krok są na górze.
Osobny PLAN.md (SDD) usunięto: etapy i zadania żyją w TODO.md, a zatwierdzenie planu to po prostu
moment zapisu do TODO.md. Mniej plików = mniej rozjazdów.

**D3. Kryteria małych zadań w TODO.md, żywy plan tylko dla zadań ryzykownych.**
v6 trzymał kryteria małych zadań tylko w zleceniu (ginęły z czatem); SDD wymagał 4 plików na
zadanie. Kompromis: 1–2 linie kryteriów pod zadaniem w TODO.md, a docs/tasks/T-NNN.md tylko dla
ryzyka ŚREDNIEGO/WYSOKIEGO lub pracy wielosesyjnej. Wzór T-NNN.md to uproszczony ExecPlan OpenAI
(postęp, odkrycia, decyzje, wynik), bo dokładnie ten format pozwala nowej sesji kontynuować bez
historii.

**D4. Sześć statusów: TODO, ZLECONE, DO SPRAWDZENIA, DO SCALENIA, GOTOWE, ZABLOKOWANE.**
Z SDD zostało rozróżnienie „zweryfikowane na gałęzi” (DO SCALENIA) vs „zintegrowane i potwierdzone”
(GOTOWE) — bo to odpowiedź na pytanie „co naprawdę zweryfikowano”, a DO SCALENIA mówi wprost, że
ruch jest po Twojej stronie. Usunięte: DRAFT/READY (niezatwierdzone = „Pomysły”, zatwierdzone =
TODO), ACCEPTED, DO_POPRAWY (to ZLECONE z „runda n”).

**D5. Dowód weryfikacji zapisany trwale w jednej linii.**
Wpis w „Zrobione”: sha scalenia, kto zweryfikował, polecenie → wynik, scenariusz. Zamiast plików
REPORT.md/REVIEW.md na każde zadanie. Po tygodniach widać, co i czym potwierdzono; nagłówek ma
„ostatni zweryfikowany” commit.

**D6. Weryfikator dostaje kryteria, sha i polecenia — bez wniosków autora.**
Anthropic zaleca recenzję w świeżym kontekście, który widzi tylko diff i kryteria. Z raportu
wykonawcy przekazujemy wyłącznie „jak uruchomić”.

**D7. Uwagi weryfikatora: BLOKUJĄCE vs OPCJONALNE.**
Anthropic wprost ostrzega, że recenzent poproszony o szukanie luk zawsze jakieś znajdzie, a gonienie
każdej uwagi prowadzi do przeinżynierowania. Tylko uwagi blokujące wracają do wykonawcy; reszta
trafia do „Pomysły”. „Zbędny kod na przyszłość” jest blokujący — to główne zabezpieczenie przed
przeinżynierowaniem po stronie wykonawców.

**D8. Budżet kontekstu kierownika jako osobna sekcja z konkretnymi regułami.**
Podstawowe ograniczenie wg Anthropic: wydajność modelu spada wraz z zapełnieniem kontekstu.
Mechanizmy: tanie polecenia Gita zamiast czytania kodu; zakres po `--stat`; analiza dużych obszarów
delegowana z limitem 40 linii; raporty ≤ 15 linii; TODO.md ≤ 150 linii z archiwum w DONE.md;
punkt kontrolny po każdej zmianie statusu; licznik cykli widoczny w każdej odpowiedzi; konkretne
wyzwalacze przekazania wątku. Przekazanie jest tanie, bo stan zawsze jest już w pliku.

**D9. AGENTS.md jako jedyne źródło zasad; CLAUDE.md = `@AGENTS.md` + różnice.**
Wynika bezpośrednio z aktualnych wytycznych (sekcja 5 tego dokumentu). Dodatkowo w AGENTS.md trafił format raportu
i zasady weryfikacji, bo dotyczą każdej sesji wykonawczej — dzięki temu zlecenia są krótsze,
a kontekst kierownika mniejszy.

**D10. Stan projektu nigdy w plikach instrukcji.**
Obie firmy zalecają w AGENTS.md / CLAUDE.md tylko trwałe fakty. Stan zmienia się codziennie,
więc w pliku wczytywanym do każdej sesji byłby szybko nieaktualny i marnowałby kontekst.

**D11. TODO.md w Markdown, nie w JSON.**
Anthropic zauważył, że modele rzadziej niewłaściwie nadpisują JSON niż Markdown. Tutaj jednak
TODO.md czyta przede wszystkim człowiek, a ochronę zapewniają: zakaz edycji w AGENTS.md, kontrola
`git diff --stat` przy odbiorze (agent zmienił TODO.md → odrzucenie) i osobne commity kierownika.

**D12. Ty jako „kurier” między narzędziami, automatyka opcjonalna.**
Zespół obejmuje różne narzędzia (Codex, Antigravity, lokalny Qwen), więc domyślnie Ty uruchamiasz
zlecenia — masz pełną kontrolę i wgląd. Gdy narzędzie kierownika umie uruchamiać agentów, możesz
włączyć tryb automatyczny; granice i niezależność weryfikatora zostają.

**D13. Archiwum zamiast usuwania.**
Poprzednie wersje są w `archiwum/` — do porównań; nie są częścią systemu.


## 5. Co mówią aktualne wytyczne (sprawdzone 2026-10-03) i jak wpłynęły na zestaw

Anthropic — Claude Code:
- Claude Code czyta AGENTS.md sam (od v2.1.277), ale tylko gdy nie ma CLAUDE.md/CLAUDE.local.md;
  z CLAUDE.md czyta tylko CLAUDE.md → **CLAUDE.md musi importować `@AGENTS.md`**.
- Zdanie „przeczytaj AGENTS.md” jest wprost opisane jako słabsze od importu → poprawka względem v6.
- Symlink nie dla Windows → przy PowerShell zawsze import.
- < 200 linii na plik; zbyt długi plik = ignorowane reguły; test „czy usunięcie linii spowoduje błąd”.
- Instrukcje to kontekst, nie wymuszenie → twarde reguły przez hooki/uprawnienia (sekcja 7.5 promptu).
- Kontekst to najważniejszy zasób; świeży kontekst do recenzji; po dwóch nieudanych korektach
  zacząć od nowa z lepszym promptem (odpowiada regule „dwie rundy → diagnoza”).
- Długie zadania: plik postępu + Git + start sesji od sprawdzenia stanu i testu end-to-end.

OpenAI — Codex:
- AGENTS.md od korzenia repozytorium do katalogu roboczego, jeden plik na katalog
  (AGENTS.override.md ma pierwszeństwo), łącznie domyślnie 32 KiB, nadmiar obcinany → krótki plik,
  najważniejsze na górze.
- Brak importów `@` → treść zasad musi być w samym AGENTS.md, a nie w CLAUDE.md (kierunek importu:
  CLAUDE.md → AGENTS.md, nigdy odwrotnie).
- Powtarzający się błąd → reguła w AGENTS.md.
- Długie zadania: ExecPlan — samowystarczalny, żywy dokument z postępem, odkryciami, decyzjami
  i wynikiem → wzór docs/tasks/T-NNN.md.

Ograniczenia weryfikacji: strony developers.openai.com i agents.md były zablokowane w środowisku,
w którym powstał zestaw. Zachowanie Codex sprawdzono w jego kodzie źródłowym i w cookbooku OpenAI
na GitHubie. Obsługi AGENTS.md w Antigravity nie zweryfikowano — SZABLONY_PROJEKTU.md każe
to sprawdzić przed utworzeniem osobnego pliku, a zlecenia i tak zawierają „PRZECZYTAJ: AGENTS.md”.


## 6. Świadomie pominięte (ochrona przed przeinżynierowaniem)

- docs/PROJECT_WORKFLOW.md w każdym repozytorium — workflow jest w prompcie kierownika, a wykonawcy
  potrzebują tylko swojej części (AGENTS.md).
- REPORT.md i REVIEW.md dla każdego zadania — raport w czacie + jednolinijkowy dowód w TODO.md;
  szczegóły dużych zadań w T-NNN.md.
- Osobny PLAN.md, statusy DRAFT/READY/ACCEPTED/DO_POPRAWY.
- Lista funkcji w JSON, skrypty startowe, hooki „na wszelki wypadek” — dodawane dopiero, gdy
  konkretna reguła okaże się łamana.
- Osobny prompt architekta i weryfikatora.


## 7. Ryzyka i kiedy rozbudować system

| Ryzyko | Łagodzenie | Sygnał do rozbudowy |
|---|---|---|
| Kierownik i tak czyta kod | SYGNAŁ STOP, reguły budżetu | Powtarza się mimo reguł → uruchamiaj kierownika z uprawnieniami tylko do odczytu |
| Agent zmienia TODO.md lub kryteria | Zakaz w AGENTS.md, kontrola `--stat` | Zdarzyło się 2× → hook blokujący zapis do docs/TODO.md |
| TODO.md puchnie | Limit 150 linii, DONE.md | Wiele równoległych strumieni → osobny TODO na moduł |
| Weryfikator zbyt łagodny | Inna rodzina modeli, dowody per kryterium | Błędy wykrywane po scaleniu → drugi weryfikator dla ryzyka WYSOKIEGO |
| Rozjazd zasad między narzędziami | Jedno źródło + import | Nowe narzędzie → krótkie zadanie testowe (SZABLONY, sekcja 4) |
| Za dużo ręcznego kopiowania | — | Tryb automatyczny, gdy narzędzie kierownika umie uruchamiać agentów |
