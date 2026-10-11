# SZABLONY PROJEKTU — pliki instrukcji dla agentów i dokumenty zadań

Ten plik czyta orkiestrator przy zakładaniu lub naprawie plików projektu oraz wykonawca, któremu
zlecono ich przygotowanie. Nie wklejaj go do stałego kontekstu żadnego agenta.

Zawartość:
1. Zasady plików instrukcji (stan wytycznych OpenAI i Anthropic na 2026-10-03)
2. Wzór AGENTS.md
3. Wzór CLAUDE.md
4. Inne narzędzia (Antigravity / Gemini, Qwen przez Ollama, pozostałe)
5. Zagnieżdżone AGENTS.md (monorepo, moduły o innych zasadach)
6. Wzór docs/tasks/T-NNN.md (żywy plan zadania)
7. Wzór ADR
8. Lista kontrolna przeglądu plików instrukcji (koniec etapu)


## 1. Zasady plików instrukcji

### Jak narzędzia wczytują te pliki (fakty, które decydują o układzie)

Codex CLI (OpenAI):
- Wczytuje globalny `~/.codex/AGENTS.md`, a potem w każdym katalogu od korzenia repozytorium
  (wyznaczanego przez `.git`) do katalogu roboczego: `AGENTS.override.md`, a jeśli go brak —
  `AGENTS.md` (plus opcjonalne nazwy z `project_doc_fallback_filenames`). Najwyżej jeden plik
  na katalog; treści są łączone od korzenia w dół, więc plik bliżej katalogu roboczego jest
  czytany później i ma praktyczne pierwszeństwo.
- Nie schodzi poniżej katalogu roboczego: AGENTS.md w podkatalogu działa tylko wtedy, gdy Codex
  pracuje w tym podkatalogu.
- Łączny rozmiar jest domyślnie ograniczony do 32 KiB (`project_doc_max_bytes`); nadmiar jest
  po cichu obcinany. Ważne reguły muszą być na początku, a całość krótka.
- Nie rozwija importów `@plik` — cała potrzebna treść musi być w samym AGENTS.md.
- OpenAI zaleca: AGENTS.md jako trwałe wskazówki (polecenia, konwencje, weryfikacja); gdy agent
  drugi raz popełnia ten sam błąd — dopisać regułę; dla długich zadań — żywy plan wykonania
  (ExecPlan / PLANS.md) z sekcjami postępu, odkryć, decyzji i wyniku.

Claude Code (Anthropic):
- Od wersji 2.1.277 czyta AGENTS.md bezpośrednio, ALE tylko wtedy, gdy w katalogu roboczym ani
  wyżej nie ma CLAUDE.md, .claude/CLAUDE.md ani CLAUDE.local.md. Jeśli którykolwiek istnieje,
  domyślnie czyta tylko pliki CLAUDE.
- Zalecany sposób współdzielenia: CLAUDE.md z importem `@AGENTS.md` w pierwszej linii, a pod nim
  tylko instrukcje specyficzne dla Claude. Import nigdy nie powoduje podwójnego wczytania.
- Zdanie „przeczytaj AGENTS.md” jest słabe: Claude zobaczy plik tylko, jeśli sam zdecyduje się
  go otworzyć. Używaj importu `@AGENTS.md`.
- Dowiązanie symboliczne CLAUDE.md → AGENTS.md działa, ale nie na Windows (Git wypakuje je jako
  jednolinijkowy plik tekstowy) — przy PowerShell/Windows zawsze import.
- Zalecany rozmiar: poniżej 200 linii na plik. Dłuższe pliki obniżają przestrzeganie reguł;
  importy nie zmniejszają kosztu, bo ładują się na starcie.
- Treść: polecenia, których Claude nie zgadnie; styl odbiegający od domyślnego; testy;
  etykieta repozytorium (gałęzie, commity); decyzje architektoniczne; pułapki środowiska.
  Bez: rzeczy do odczytania z kodu, standardowych konwencji języka, szczegółowej dokumentacji API,
  informacji często zmiennych, tutoriali, opisów plik po pliku.
- Test każdej linii: „czy jej usunięcie spowoduje błąd agenta?” Jeśli nie — usuń.
- Instrukcje są kontekstem, nie wymuszeniem. Coś, co musi się wydarzyć zawsze, robi się hookiem
  (np. PreToolUse blokujący zapis do katalogu), uprawnieniami lub CI.
- Narzędzia kontrolne: `/context` (czy plik się wczytał), `/doctor prompt-audit` (sprzeczności,
  nieistniejące polecenia i ścieżki), `/init` (szkic na podstawie repozytorium).

### Wynikający z tego układ

    AGENTS.md          JEDYNE źródło zasad wspólnych dla wszystkich narzędzi (≤ ~150 linii, ≤ 12 KiB)
    CLAUDE.md          @AGENTS.md + krótka sekcja „Claude Code” (często pusta)
    <dir>/AGENTS.md    tylko gdy katalog ma naprawdę inne zasady (sekcja 5)
    pliki innych narzędzi  tylko jeśli narzędzie nie czyta AGENTS.md — minimalne odesłanie (sekcja 4)
    docs/TODO.md, docs/VISION.md, docs/tasks/  stan i plany — NIGDY w plikach instrukcji

Dlaczego tak:
- jedno źródło → brak rozjazdów między narzędziami;
- stan projektu poza plikami instrukcji → pliki instrukcji są stabilne, a stan nie jest
  wczytywany do każdej sesji niezależnie od potrzeby (oszczędność kontekstu);
- krótki plik → mieści się w limicie Codex i nie traci przestrzegania w Claude Code;
- zlecenie zawsze zawiera „PRZECZYTAJ: AGENTS.md” → działa także w narzędziach, które
  same niczego nie wczytują (Qwen przez Ollama).

### Czego nie robić
- Nie kopiować AGENTS.md do CLAUDE.md, GEMINI.md itd. (rozjedzie się po tygodniu).
- Nie wklejać promptu orkiestratora ani opisu całego workflow do AGENTS.md — agent wykonawczy
  potrzebuje tylko swojej części: polecenia, granice, Definition of Done, format raportu.
- Nie trzymać w AGENTS.md listy zadań, statusów, dat ani „aktualnego etapu”.
- Nie dodawać reguł „na zapas”. Reguła powstaje z obserwowanego błędu albo z twardej konwencji.
- Nie polegać na komentarzach HTML do ukrywania notatek: Claude Code je usuwa, Codex nie.


## 2. Wzór AGENTS.md

Wypełnij tylko to, co dotyczy projektu; puste pozycje usuń. Kolejność ma znaczenie:
najważniejsze na górze (obcinanie w Codex działa od końca).

```markdown
# <Projekt>

<Jedno zdanie: co to jest i dla kogo. Szczegóły: docs/VISION.md.>

## Polecenia
- Instalacja: `<…>`
- Uruchomienie: `<…>`
- Testy (całość): `<…>` | jeden test: `<…>`
- Lint / format: `<…>` / `<…>`
- Typy: `<…>`
<Wymagane zmienne środowiskowe: patrz .env.example. Wymagane usługi: <np. Postgres z docker compose up db>.>

## Struktura
- `<katalog>/` — <co tu jest; tylko najważniejsze katalogi>
- Decyzje architektoniczne: docs/decisions/ (ADR); obraz całości: docs/ARCHITECTURE.md

## Konwencje
- <tylko reguły odbiegające od domyślnych dla stosu, np. „błędy domenowe przez Result, nie wyjątki”>
- Commity: Conventional Commits z ID zadania, np. `feat(T-012): import faktur z CSV`.
- Gałęzie: `task/T-NNN-krotka-nazwa` od wskazanego sha; main zawsze działa.
- Zależności przypięte w lockfile.

## Granice
- Zmieniaj tylko to, czego dotyczy zadanie. Pomysły spoza zakresu wpisz w raporcie, nie wdrażaj.
- Najprostsze rozwiązanie spełniające kryteria. Bez interfejsów, warstw, flag i konfiguracji
  „na przyszłość”.
- Nie edytuj docs/TODO.md, docs/VISION.md ani kryteriów akceptacji (prowadzi je kierownik projektu).
- Nowa zależność tylko z uzasadnieniem w raporcie.
- Nie osłabiaj, nie usuwaj i nie wyłączaj testów, żeby przeszły. Uzasadnioną zmianę testu opisz.
- Bez merge, rebase, push, reset i usuwania gałęzi — robi to właściciel.
- Sekrety tylko w .env (poza Gitem); w repozytorium .env.example. Nie wypisuj wartości sekretów.
- Testy i skrypty tylko na danych testowych lub kopii. Zapis do prawdziwych danych lub usług
  zewnętrznych — wyłącznie gdy zlecenie wprost na to pozwala.
- Brak informacji: zapisz pytanie w raporcie zamiast zgadywać.

## Definition of Done
- Kryteria z zadania spełnione i pokazane dowodem (polecenie → wynik, scenariusz użycia).
- Testy i lint przechodzą; pominięte testy wymienione w raporcie.
- README / ARCHITECTURE / ADR zaktualizowane, jeśli zmieniło się zachowanie, uruchamianie
  lub architektura.
- Jeśli zadanie ma docs/tasks/T-NNN.md: zaktualizowane sekcje „Postęp”, „Odkrycia i decyzje”, „Wynik”.

## Raport po zadaniu (≤ 15 linii)
    T-NNN | gałąź | sha
    ZMIANY: 1–3 zdania; liczba plików
    TESTY: `<polecenie>` → exit <n>; passed/failed/skipped
    SCENARIUSZ: co uruchomiono jak użytkownik → wynik
    NIE SPRAWDZONO: …
    POZA ZAKRESEM: propozycje (niewdrożone)

## Weryfikacja cudzej zmiany
- Nie poprawiaj kodu i nie commituj. Sprawdź każde kryterium w działaniu, nie tylko w testach.
- Kod wyjścia 0 nie dowodzi kryterium: sprawdź pominięte testy i ostrzeżenia.
- BLOKUJĄCE są tylko: niespełnione kryterium, błąd, wyjście poza zakres, osłabiony test, zbędny kod
  „na przyszłość”, sekret. Resztę oznacz jako OPCJONALNE.

## Pułapki
- <nieoczywiste zachowania środowiska/projektu; dopisywane, gdy agent potknie się drugi raz>
```

Uwaga: sekcje „Raport” i „Weryfikacja” są celowo w AGENTS.md — dotyczą każdej sesji wykonawczej
w tym repozytorium, a dzięki temu zlecenia orkiestratora mogą być krótsze.


## 3. Wzór CLAUDE.md

Minimalny (najczęstszy przypadek):

```markdown
@AGENTS.md
```

Z różnicami dla Claude Code — tylko gdy są naprawdę potrzebne:

```markdown
@AGENTS.md

## Claude Code
- Przy kompaktowaniu zachowaj: ID zadania, gałąź i bazowy sha, kryteria akceptacji,
  listę zmienionych plików i polecenia testów.
- Szerokie przeszukiwanie kodu zlecaj subagentom, żeby nie zapełniać głównego kontekstu.
- <np. „Zmiany w src/billing/ zaczynaj w trybie planu.”>
```

Dlaczego zostawiać CLAUDE.md, choć Claude Code czyta AGENTS.md sam: część sesji nie wczytuje
AGENTS.md (starsze wersje, wyłączona obsługa, pierwsza sesja po aktualizacji), a dodanie przez
kogokolwiek CLAUDE.local.md wyłącza automatyczne czytanie AGENTS.md. Import działa zawsze
i nie dubluje treści. Osobiste preferencje → CLAUDE.local.md (w .gitignore) albo ~/.claude/CLAUDE.md.
Sprawdzenie: w nowej sesji `/context` → plik widoczny w „Memory files”.

Twarde reguły dla Claude Code (np. blokada zapisu do migracji, zakaz `git push`) ustaw jako
uprawnienia lub hook w `.claude/settings.json`, nie jako tekst.


## 4. Inne narzędzia

- Antigravity / Gemini: przed utworzeniem osobnego pliku sprawdź w dokumentacji używanej wersji,
  czy AGENTS.md jest wczytywany (nie zweryfikowano w ramach tego zestawu). Jeśli nie — utwórz
  plik reguł wymagany przez narzędzie z jedną treścią: odesłaniem do AGENTS.md (w narzędziach
  z importem `@AGENTS.md`, w pozostałych zdanie „Zasady projektu: AGENTS.md — przeczytaj przed
  pracą”) plus wyłącznie różnice narzędziowe. Alternatywnie skonfiguruj narzędzie, by czytało
  AGENTS.md jako plik kontekstu, jeśli to umożliwia.
- Qwen przez Ollama (lub inny model bez agenta plikowego): nic nie wczytuje się samo. Zlecenie
  zawsze zawiera „PRZECZYTAJ: AGENTS.md”, a jeśli model nie ma dostępu do plików — orkiestrator
  wkleja do zlecenia tylko potrzebne fragmenty (polecenia, granice, format raportu).
- Copilot, Cursor i inne: zasada ta sama — najpierw sprawdź, czy narzędzie czyta AGENTS.md;
  dopiero gdy nie, minimalny plik odsyłający.

Po dodaniu nowego narzędzia: jedno krótkie zadanie testowe („wypisz polecenie testów z zasad
projektu”) potwierdza, że agent widzi AGENTS.md.


## 5. Zagnieżdżone AGENTS.md

Twórz tylko wtedy, gdy katalog ma inne polecenia lub zasady (np. `frontend/` z innym stosem,
`services/payments/` ze ściślejszymi regułami). Zawiera wyłącznie różnice względem głównego pliku.
- Codex: działa, gdy agent pracuje w tym katalogu (uruchamiaj go tam albo wskaż katalog w zleceniu).
- Claude Code: plik z podkatalogu wczytuje się, gdy agent czyta pliki z tego podkatalogu
  (dla CLAUDE.md w podkatalogu analogicznie; reguły tylko dla Claude — `.claude/rules/` z `paths`).
- W zleceniu dla modułu dopisz „PRZECZYTAJ: AGENTS.md, <dir>/AGENTS.md”.


## 6. Wzór docs/tasks/T-NNN.md (żywy plan zadania)

Tylko dla zadań o ryzyku ŚREDNIM/WYSOKIM albo dłuższych niż jedna sesja. Zadania małe mają
kryteria bezpośrednio w TODO.md. Wzór jest uproszczoną wersją ExecPlan z OpenAI: dokument musi
wystarczyć, żeby nowa sesja bez żadnej historii mogła kontynuować pracę.

```markdown
# T-NNN — <tytuł>
Etap: E<n> | Ryzyko: ŚREDNIE/WYSOKIE | Specyfikacja: v1 (<data>, zatwierdził: właściciel)

## Cel
<Co użytkownik będzie mógł zrobić po zmianie, czego nie mógł wcześniej. 2–4 zdania.>

## Kontekst
<Pliki i moduły, których dotyczy; istniejące wzorce do naśladowania; definicje pojęć.
Wszystko, czego nowa sesja potrzebuje — bez odsyłania do rozmów.>

## Zakres
W ZAKRESIE: <…>
POZA ZAKRESEM: <…>

## Kryteria akceptacji (nie zmieniać po rozpoczęciu; nowa wersja tylko decyzją właściciela)
K1. <wejście / czynność → oczekiwany wynik; jak sprawdzić: `<polecenie>`>
K2. <scenariusz end-to-end tak, jak użyje tego użytkownik; dane: testowe/kopia>
K3. <przypadek negatywny lub regresja — gdy uzasadnia to ryzyko>

## Plan
1. <krok z rezultatem i poleceniem sprawdzającym>
2. <…>
<Dla niepewnych założeń: najpierw mały spike z kryterium „wykonalne / niewykonalne”.>

## Postęp (aktualizuje wykonawca przy każdym zatrzymaniu)
- [ ] <krok> 
- [x] <krok> (<data>, <sha>)

## Odkrycia i decyzje (aktualizuje wykonawca; krótko, z dowodem)
- <data> — <co odkryto / co postanowiono i dlaczego>

## Wynik
<Wykonawca: co dostarczono, czego nie, wnioski. Werdykt weryfikatora orkiestrator zapisuje w TODO.md.>

## Historia specyfikacji
- v1 <data> — utworzenie
```


## 7. Wzór ADR — docs/decisions/NNNN-tytul.md

Tylko decyzje trudne do odwrócenia (stos, baza, format danych, kontrakty zewnętrzne).

```markdown
# NNNN — <decyzja>
Status: proponowana | przyjęta | zastąpiona przez NNNN      Data: <…>

## Kontekst
<Jaki problem i jakie ograniczenia.>

## Decyzja
<Co wybieramy.>

## Rozważane alternatywy
- <wariant> — <dlaczego nie>

## Konsekwencje
<Co zyskujemy, co tracimy, co trzeba będzie zrobić.>
```


## 8. Lista kontrolna przeglądu plików instrukcji (koniec etapu lub po powtórzonym błędzie)

- [ ] Polecenia w AGENTS.md działają (weryfikator uruchomił je w ostatnim etapie).
- [ ] Brak stanu projektu, dat i list zadań w AGENTS.md / CLAUDE.md.
- [ ] AGENTS.md ≤ ~150 linii; łącznie z zagnieżdżonymi plikami na ścieżce < 32 KiB.
- [ ] CLAUDE.md zaczyna się od `@AGENTS.md` i nie powtarza jego treści.
- [ ] Pliki innych narzędzi tylko odsyłają; żaden nie zawiera kopii zasad.
- [ ] Brak sprzecznych reguł między plikami (w Claude Code: `/doctor prompt-audit`).
- [ ] Każda reguła przechodzi test „czy usunięcie spowoduje błąd agenta?”.
- [ ] Reguły, których łamanie było kosztowne, mają zabezpieczenie techniczne (uprawnienia, hook, CI).
- [ ] Nowe pułapki z ostatniego etapu dopisane; nieaktualne usunięte.


## Źródła (sprawdzone 2026-10-03)

- Anthropic, „How Claude remembers your project” (CLAUDE.md, AGENTS.md, importy, rozmiar):
  https://code.claude.com/docs/en/memory
- Anthropic, „Best practices for Claude Code” (co umieszczać w CLAUDE.md, kontekst, weryfikacja,
  recenzja w świeżym kontekście): https://code.claude.com/docs/en/best-practices
- Anthropic, „Effective harnesses for long-running agents” (plik postępu, lista funkcji, start sesji):
  https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents
- OpenAI, „Custom instructions with AGENTS.md”: https://developers.openai.com/codex/guides/agents-md
  (strona niedostępna z tego środowiska; zachowanie zweryfikowano w kodzie źródłowym Codex:
  https://github.com/openai/codex/blob/main/codex-rs/core/src/agents_md.rs)
- OpenAI, „Using PLANS.md for multi-hour problem solving” (ExecPlans):
  https://github.com/openai/openai-cookbook/blob/main/articles/codex_exec_plans.md
- OpenAI, „Codex best practices”: https://developers.openai.com/codex/learn/best-practices
