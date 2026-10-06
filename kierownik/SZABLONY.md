# SZABLONY — pliki projektu i zasady plików instrukcji

Czyta kierownik, gdy zakłada lub naprawia pliki projektu (oraz wykonawca, któremu to zlecono).

1. Zasady AGENTS.md i CLAUDE.md (stan wytycznych OpenAI i Anthropic na 2026-10-03)
2. AGENTS.md
3. CLAUDE.md
4. docs/PROJEKT.md
5. docs/TODO.md
6. docs/tasks/T-NNN.md
7. ADR
8. .claude/settings.json (uprawnienia dla pętli kierownika)
9. Lista kontrolna przeglądu (koniec etapu)


## 1. Zasady AGENTS.md i CLAUDE.md

Jak wczytują je narzędzia:
- **Codex** łączy `AGENTS.md` z każdego katalogu od korzenia repozytorium (`.git`) do katalogu
  roboczego (w katalogu `AGENTS.override.md` ma pierwszeństwo przed `AGENTS.md`; plus globalny
  `~/.codex/AGENTS.md`). Nie schodzi poniżej katalogu roboczego. Łącznie domyślnie 32 KiB —
  nadmiar jest po cichu obcinany. Nie rozwija importów `@plik`.
- **Claude Code** czyta AGENTS.md sam (od v2.1.277) tylko wtedy, gdy nie ma CLAUDE.md,
  .claude/CLAUDE.md ani CLAUDE.local.md. Z CLAUDE.md czyta domyślnie tylko pliki CLAUDE.
  Zalecane: CLAUDE.md z importem `@AGENTS.md` (import nigdy nie wczytuje pliku dwa razy).
  Zdanie „przeczytaj AGENTS.md” jest słabe — Claude otworzy plik tylko, jeśli sam zdecyduje.
  Symlink zamiast importu nie działa poprawnie na Windows. Zalecany rozmiar < 200 linii na plik.
- **Antigravity (aplikacja i CLI `agy`)**: przed dodaniem osobnego pliku reguł sprawdź
  w dokumentacji używanej wersji, czy czyta AGENTS.md (np. krótkim zleceniem „wypisz polecenie
  testów z zasad projektu” bez wskazywania pliku). Jeśli nie — jego plik reguł zawiera tylko
  odesłanie do AGENTS.md i różnice narzędziowe. Zlecenia i tak zawierają „PRZECZYTAJ: AGENTS.md”.

Wynikające zasady:
- AGENTS.md = jedyne źródło zasad wspólnych; CLAUDE.md = `@AGENTS.md` + krótka sekcja tylko dla
  Claude Code; pliki innych narzędzi tylko odsyłają. Nic nie jest kopiowane między plikami.
- Treść: polecenia, których agent nie zgadnie; środowisko i koszty; konwencje odbiegające od
  domyślnych; granice; Definition of Done; format raportu i zasady weryfikacji. Bez: rzeczy
  do wyczytania z kodu, standardowych konwencji języka, dokumentacji API, opisów plik po pliku,
  stanu projektu, planów i dat (te są w docs/TODO.md i docs/PROJEKT.md).
- Długość ≤ ~150 linii, najważniejsze na górze. Test każdej linii: „czy jej usunięcie spowoduje
  błąd agenta?”. Nie — usuń.
- Reguła powstaje z obserwowanego błędu (drugi raz ten sam) albo z twardej konwencji, nie „na zapas”.
- Instrukcje to wskazówki. Co musi być przestrzegane zawsze → uprawnienia, hook, CI.
- Katalog o innych zasadach (np. `frontend/` z innym stosem) → zagnieżdżony AGENTS.md tylko
  z różnicami. Codex użyje go, gdy pracuje w tym katalogu; Claude Code — gdy czyta z niego pliki.
- Kontrola: w Claude Code `/context` (czy plik się wczytał) i `/doctor prompt-audit`
  (sprzeczności, nieistniejące polecenia i ścieżki).


## 2. AGENTS.md

Puste pozycje usuń. Kolejność ma znaczenie (Codex obcina od końca).

```markdown
# <Projekt>

<Jedno zdanie: co to jest i dla kogo.> Opis systemu: docs/PROJEKT.md. Plan i stan: docs/TODO.md.

## Polecenia
- Instalacja: `<…>`
- Uruchomienie: `<…>`
- Testy: `<…>` | jeden test: `<…>`
- Lint / format / typy: `<…>`

## Środowisko i koszty
- LLM aplikacji: <np. lokalny serwer LLM pod http://localhost:<port> — darmowy, wolno używać w testach>
- Bazy: <np. testowa SQLite w tests/ — wolno; produkcyjna (zmienna DB_PROD_URL) — NIE dotykać>
- Usługi zewnętrzne: <np. wysyłka maili — w testach wyłącznie mock; płatne API X — tylko za zgodą właściciela>
- Sekrety: tylko w .env (poza Gitem), wzór w .env.example. Nie wypisuj wartości.

## Struktura
- `<katalog>/` — <rola; tylko najważniejsze katalogi>

## Konwencje
- <tylko reguły odbiegające od domyślnych dla stosu>
- Commity: Conventional Commits z ID zadania, np. `feat(T-012): import faktur z CSV`.
- Gałęzie zadań: `task/T-NNN-nazwa`; main zawsze działa.

## Granice
- Zmieniaj tylko to, czego dotyczy zadanie. Pomysły spoza zakresu wpisz w raporcie.
- Najprostsze rozwiązanie spełniające kryteria. Bez warstw, interfejsów, flag i konfiguracji
  „na przyszłość”.
- Nie edytuj docs/TODO.md, docs/PROJEKT.md ani kryteriów zadania — prowadzi je kierownik.
- Nie osłabiaj, nie usuwaj i nie wyłączaj testów, żeby przeszły. Uzasadnioną zmianę testu opisz.
- Bez merge, push i przepisywania historii — robi to kierownik.
- Brak informacji: zapisz pytanie w raporcie zamiast zgadywać.

## Definition of Done
- Kryteria spełnione i pokazane dowodem (polecenie → wynik, scenariusz użycia).
- Testy i lint przechodzą; pominięte testy wymienione w raporcie.
- README zaktualizowane, jeśli zmieniło się uruchamianie lub zachowanie widoczne dla użytkownika.
- Jeśli zadanie ma docs/tasks/T-NNN.md: zaktualizowane „Postęp”, „Odkrycia i decyzje”, „Wynik”.

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
- BLOKUJĄCE są tylko: niespełnione kryterium, błąd, wyjście poza zakres, osłabiony test, kod
  „na przyszłość”, sekret. Resztę oznacz jako OPCJONALNE.

## Pułapki
- <nieoczywiste zachowania; dopisywane, gdy agent potknie się drugi raz>
```


## 3. CLAUDE.md

Najczęściej wystarczy:

```markdown
@AGENTS.md
```

Z różnicami dla Claude Code (tylko gdy naprawdę potrzebne):

```markdown
@AGENTS.md

## Claude Code
- Przy kompaktowaniu zachowaj: ID zadania, gałąź i bazowy sha, kryteria, listę zmienionych plików,
  polecenia testów.
- <np. „Zmiany w src/billing/ zaczynaj w trybie planu.”>
```

Plik zostaje nawet, gdy jest jednolinijkowy: część sesji nie czyta AGENTS.md samodzielnie,
a dodanie CLAUDE.local.md wyłącza automatyczne czytanie AGENTS.md. Osobiste preferencje →
CLAUDE.local.md (w .gitignore) albo ~/.claude/CLAUDE.md.


## 4. docs/PROJEKT.md (wiedza o systemie, ≤ ~150 linii)

Pisze i aktualizuje kierownik. Ma pozwolić nowej sesji zrozumieć projekt w kilka minut.
Opisuje stan OBECNY; plany są w TODO.md.

```markdown
# <Projekt> — opis systemu
Aktualizacja: <data>, po etapie E<n> | main @ <sha>

## Cel
Problem: <jaki problem rozwiązuje>
Użytkownik: <kto i w jakiej sytuacji>
MVP: <co musi działać>
Kluczowe założenie: <bez czego projekt nie ma sensu; czy już potwierdzone i czym>
Czego NIE robimy: <lista>
Kryterium sukcesu: <po czym poznamy, że MVP spełnia cel>

## Jak działa
<5–15 linii: przepływ od wejścia do wyniku, w kolejności, z nazwami modułów.>

## Moduły
- `<katalog/moduł>` — <odpowiedzialność; kluczowy plik wejściowy>

## Uruchamianie i testy
<Polecenia są w AGENTS.md — tu tylko to, czego tam nie ma: wymagane usługi, dane przykładowe,
jak przejść główny scenariusz ręcznie.>

## Środowisko i koszty
- LLM: <lokalny / płatny; adres, model, gdzie konfiguracja>
- Dane: <testowe / kopie / produkcyjne — gdzie i co wolno>
- Usługi zewnętrzne: <co, czy płatne, czy są mocki>

## Stan funkcjonalny
- Działa (potwierdzone): <funkcja — dowód / sha>
- Częściowo / nie działa: <…>

## Decyzje i ograniczenia
- <decyzja trudna do odwrócenia — ADR NNNN>

## Pułapki
- <coś, o co łatwo się potknąć>
```


## 5. docs/TODO.md (plan rozwoju i stan, ≤ ~150 linii)

Prowadzi wyłącznie kierownik. Nagłówek odpowiada na pięć pytań: cel, plan, w toku,
co zweryfikowane, następny krok.

```markdown
# TODO — <projekt>
Prowadzi kierownik. Agenci: wyłącznie odczyt.

## Stan (<data>)
Cel: <1 zdanie z PROJEKT.md>
Etap: E2 — <nazwa>: <obserwowalny cel etapu> (3/5 GOTOWE)
main @ <sha> | ostatni zweryfikowany: <sha> (<data>, <co potwierdzono>)
W toku: T-007 | W TOKU | kier-wykonawca (Sonnet) | task/T-007-import
Blokady: brak
Następny krok: <konkretnie: zadanie, wykonawca, czynność>
Ustalenia: <np. odstępstwa od ZESPOL.md, mapowanie plików (ROADMAP.md → TODO.md)>

## E2 — <nazwa>: <obserwowalny cel etapu>
- [ ] T-006 | DO SPRAWDZENIA | wyk. Sonnet → rec. Opus | <opis>
      Kryteria: <obserwowalne>; `<polecenie testu>`
- [ ] T-007 | W TOKU | wyk. Opus | <opis> (po T-006) | plan: docs/tasks/T-007.md
      Kryteria: <…>
- [ ] T-008 | TODO | — | <opis> (po T-007)
      Kryteria: <…>

## Następne etapy
- E3 — <nazwa>: <cel> (hasłowo)

## Pytania do właściciela
- <pytanie> — rekomendacja: <…> (<data>)

## Pomysły (niezatwierdzone)
- <pomysł> (<źródło>, <data>) — <zgodność z celem>

## Zrobione (10 ostatnich; starsze w docs/DONE.md)
- [x] T-005 | <opis> | <sha scalenia> | zweryf.: <kto>, <data> |
      dowód: `<polecenie>` → <wynik>; scenariusz: <co zaobserwowano>
- [x] E1 zamknięty | <sha> | dowód E2E: <środowisko, dane, czynności, wynik>
```


## 6. docs/tasks/T-NNN.md (żywy plan zadania)

Tylko dla ryzyka ŚREDNIEGO/WYSOKIEGO albo pracy na więcej niż jedną sesję. Uproszczony ExecPlan
OpenAI: musi wystarczyć nowej sesji bez żadnej historii.

```markdown
# T-NNN — <tytuł>
Etap: E<n> | Ryzyko: ŚREDNIE/WYSOKIE | Kryteria: v1 (<data>)

## Cel
<Co użytkownik będzie mógł zrobić po zmianie. 2–4 zdania.>

## Kontekst
<Pliki i moduły, istniejące wzorce do naśladowania, definicje pojęć — bez odsyłania do rozmów.>

## Zakres
W ZAKRESIE: <…>
POZA ZAKRESEM: <…>

## Kryteria akceptacji (nie zmieniać w trakcie; nowa wersja tylko przez kierownika z adnotacją)
K1. <wejście / czynność → oczekiwany wynik; `<polecenie>`>
K2. <scenariusz end-to-end tak, jak użyje tego użytkownik>
K3. <przypadek negatywny / regresja — gdy uzasadnia to ryzyko>

## Plan
1. <krok z rezultatem i poleceniem sprawdzającym>
<Niepewne założenie → najpierw mały spike z kryterium „wykonalne / niewykonalne”.>

## Postęp (wykonawca, przy każdym zatrzymaniu)
- [ ] <krok>

## Odkrycia i decyzje (wykonawca, krótko, z dowodem)
- <data> — <co odkryto / postanowiono i dlaczego>

## Wynik
<Co dostarczono, czego nie, wnioski.>
```


## 7. ADR — docs/decisions/NNNN-tytul.md

Tylko decyzje trudne do odwrócenia (stos, baza, format danych, kontrakty zewnętrzne).

```markdown
# NNNN — <decyzja>
Status: proponowana | przyjęta | zastąpiona przez NNNN      Data: <…>
## Kontekst
## Decyzja
## Rozważane alternatywy
## Konsekwencje
```


## 8. .claude/settings.json (uprawnienia dla pętli kierownika)

Cel: Claude Code nie pyta o bezpieczne, powtarzalne polecenia, a niebezpieczne są zablokowane.
Kolejność oceny reguł: deny → ask → allow. Wzorce dla Bash to pas bezpieczeństwa, nie pancerz
(dają się obejść nietypową składnią) — prawdziwą ochroną main jest ochrona gałęzi na GitHubie.
Polecenia testów dopasuj do projektu. Sprawdzenie: `/permissions`.

```json
{
  "permissions": {
    "allow": [
      "Bash(<polecenie testów> *)",
      "Bash(<polecenie lintu> *)",
      "Bash(codex exec *)",
      "Bash(agy *)",
      "Bash(git add *)",
      "Bash(git commit *)",
      "Bash(git switch *)",
      "Bash(git checkout *)",
      "Bash(git merge *)",
      "Bash(git worktree *)",
      "Bash(git branch *)",
      "Bash(git revert *)",
      "Bash(git push origin *)"
    ],
    "deny": [
      "Bash(git push --force*)",
      "Bash(git push -f*)",
      "Bash(git push * --force*)",
      "Bash(git push * -f*)",
      "Bash(git reset --hard*)",
      "Bash(git clean *)",
      "Read(./.env)",
      "Read(./.env.*)"
    ]
  }
}
```

Uwaga: `Read(./.env.*)` blokuje też `.env.example` — jeśli przeszkadza, zawęź regułę.
Alternatywą jest tryb auto w Claude Code (klasyfikator zamiast pytań); reguły deny działają
także w nim.


## 9. Lista kontrolna przeglądu (koniec etapu albo po powtórzonym błędzie)

- [ ] Polecenia w AGENTS.md działają (użyte w tym etapie).
- [ ] „Środowisko i koszty” zgodne ze stanem faktycznym (AGENTS.md i PROJEKT.md mówią to samo).
- [ ] Brak stanu, dat i list zadań w AGENTS.md / CLAUDE.md.
- [ ] AGENTS.md ≤ ~150 linii; łącznie z zagnieżdżonymi plikami < 32 KiB.
- [ ] CLAUDE.md zaczyna się od `@AGENTS.md` i nie powtarza jego treści.
- [ ] Brak sprzecznych reguł (`/doctor prompt-audit`).
- [ ] Pułapki z tego etapu dopisane, nieaktualne usunięte.
- [ ] PROJEKT.md opisuje stan po etapie (moduły, przepływ, stan funkcjonalny).


## Źródła (sprawdzone 2026-10-03/04)
- Anthropic — CLAUDE.md i AGENTS.md: https://code.claude.com/docs/en/memory
- Anthropic — Best practices for Claude Code: https://code.claude.com/docs/en/best-practices
- Anthropic — Skills: https://code.claude.com/docs/en/skills
- Anthropic — Subagents: https://code.claude.com/docs/en/sub-agents
- Anthropic — Permissions: https://code.claude.com/docs/en/permissions
- Anthropic — Effective harnesses for long-running agents:
  https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents
- OpenAI — AGENTS.md: https://developers.openai.com/codex/guides/agents-md (zachowanie sprawdzone
  w kodzie: https://github.com/openai/codex/blob/main/codex-rs/core/src/agents_md.rs)
- OpenAI — ExecPlans: https://github.com/openai/openai-cookbook/blob/main/articles/codex_exec_plans.md
- OpenAI — Codex best practices: https://developers.openai.com/codex/learn/best-practices
