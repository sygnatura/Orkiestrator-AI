# ANALIZA I DECYZJE (v8)

Do czytania, gdy chcesz zmieniać system. Do codziennej pracy niepotrzebne.


## 1. Czego oczekuje właściciel

Kierownika technicznego, któremu można powierzyć projekt: rozumie system, ma ciągłość między
sesjami bez tłumaczenia od nowa, sam deleguje i sprawdza pracę, scala zweryfikowane zmiany,
pyta tylko o decyzje właściciela, nie dryfuje, nie przeinżynierowuje — i nie rozdyma własnego
wątku, bo to najdroższy zasób (każde wczytanie zjada limit, a pełny kontekst pogarsza decyzje).


## 2. Lekcje z v6 / v7 (dlaczego tamte wersje zawodziły)

| Objaw w praktyce | Przyczyna w prompcie | Zmiana w v8 |
|---|---|---|
| Kierownik ma słabe pojęcie o projekcie, decyzje mylące | Zakaz czytania kodu i uruchamiania testów; w repo tylko cel (VISION) i lista zadań (TODO), brak opisu działania systemu | `docs/PROJEKT.md` — opis systemu budowany przez subagentów przy przejęciu i aktualizowany po każdym etapie; kierownik może czytać i uruchamiać wszystko |
| Pyta o zgodę na testy z „płatnym LLM”, choć projekt używa lokalnego | Brak faktów o środowisku + granice „pytaj, gdy może kosztować” bez obowiązku sprawdzenia | Sekcja „Środowisko i koszty” w PROJEKT.md i AGENTS.md; zasada „zanim zapytasz, sprawdź, czy ryzyko jest realne” |
| Nic nie może zrobić, o wszystko pyta | Granice oparte na nieufności (edytuje tylko TODO.md, uruchamia tylko odczyt, merge/push robi właściciel) | Autonomia według ryzyka: lista „robisz sam” / „pytasz”; scalanie i push zweryfikowanych zmian bez pytania |
| Nie wywołuje subagentów, właściciel kopiuje zlecenia | Model „właściciel jako kurier” | Kierownik sam uruchamia subagentów Claude i `codex exec` |
| Każdy nowy wątek = wklejanie 30 KB promptu | Prompt jako wklejka | Skill `/kierownik` instalowany raz; nowy wątek = `/clear` + `/kierownik` |
| Oszczędzanie kontekstu przez niewiedzę | „Czytaj tylko `git --stat`” | Oszczędzanie przez delegowanie: ciężkie czytanie robią subagenci, do kierownika wracają streszczenia |


## 3. Kluczowe decyzje v8

1. **Skill zamiast promptu.** `disable-model-invocation: true` sprawia, że opis skilla nie trafia
   do kontekstu innych sesji, a treść ładuje się tylko po `/kierownik`. Pliki pomocnicze
   (SZABLONY, ZESPOL) ładują się na żądanie. Format Agent Skills jest otwarty — w awaryjnym
   trybie inny agent może przeczytać SKILL.md jako zwykły plik.
2. **Dwa pliki stanu projektu**: PROJEKT.md (jak działa system — zmienia się wolno) i TODO.md
   (plan i stan — zmienia się po każdym zadaniu). VISION.md wchłonięty przez PROJEKT.md.
3. **Weryfikacja krzyżowa Claude ↔ Codex.** Dwie rodziny modeli wystarczą do niezależnej
   weryfikacji; Antigravity tylko jako trzecia opinia lub do zadań z przeglądarką, bo nie ma
   wywołania z terminala.
4. **Codex jako główny wykonawca implementacji**, bo kierownik i subagenci Claude dzielą limit;
   Claude zajmuje się planem, analizą i weryfikacją.
5. **Pięć statusów**: TODO, W TOKU, DO SPRAWDZENIA, GOTOWE, ZABLOKOWANE. Status „do scalenia”
   zniknął, bo kierownik scala sam zaraz po weryfikacji.
6. **Uwagi recenzenta BLOKUJĄCE vs OPCJONALNE** — tylko blokujące wracają do poprawy (Anthropic:
   recenzent zawsze coś znajdzie, gonienie wszystkiego prowadzi do przeinżynierowania).
7. **Punkt kontrolny po każdym zadaniu** (commit TODO.md) — wątek można zamknąć w dowolnej chwili.
8. **AGENTS.md jako jedyne źródło zasad, CLAUDE.md = `@AGENTS.md`** — zgodnie z aktualną
   dokumentacją obu firm (szczegóły: kierownik/SZABLONY.md, sekcja 1).


## 4. Czy to ma sens — uczciwa ocena

Ma sens, jeśli projekt trwa tygodnie i ma więcej niż kilka modułów. Rdzeń — stan i wiedza w plikach,
małe zadania z kryteriami, weryfikacja przez inny model, świeży kontekst zamiast długiego wątku —
to dokładnie to, co Anthropic i OpenAI opisują jako sprawdzone praktyki długiej pracy agentów.

Ograniczenia, o których trzeba wiedzieć:
- To nadal instrukcje dla modelu, nie program. Model może je łamać; dlatego ważne reguły mają
  zabezpieczenie techniczne (uprawnienia, ochrona gałęzi), a stan jest kontrolowalny w Gicie.
- Delegowanie do Codexa ma narzut (zlecenie, worktree, raport). Dla drobnych zmian kierownik
  robi je sam — inaczej system byłby wolniejszy niż zwykła sesja Claude Code.
- Dla małego projektu lub jednorazowej zmiany wystarczy zwykła sesja Claude Code z trybem planu;
  kierownik zaczyna się opłacać, gdy ciągłość między sesjami staje się problemem.
- Wywoływanie `codex exec` z wnętrza Claude Code wymaga, by Codex był zalogowany i działał
  nieinteraktywnie na tej maszynie — kierownik sprawdza to testem dymnym przy pierwszym uruchomieniu.
- Zestawu nie przetestowano jeszcze na prawdziwym projekcie. Zalecany pilot: jeden istniejący
  projekt, jeden etap; poprawki SKILL.md na podstawie tego, gdzie kierownik się pomylił.


## 5. Świadomie pominięte

Osobne prompty ról, PROJECT_WORKFLOW.md w repozytorium, pliki REPORT/REVIEW dla każdego zadania,
osobny PLAN.md, statusy DRAFT/READY/ACCEPTED, lista funkcji w JSON, lokalny model w zespole,
hooki „na wszelki wypadek”. Każdy z tych elementów można dodać, gdy pojawi się konkretny problem,
którego obecny układ nie rozwiązuje.


## 6. Źródła
Lista w kierownik/SZABLONY.md (sekcja „Źródła”). Poprzednia analiza (v7) z oceną materiałów
wejściowych: archiwum/ANALIZA_v7.md.
