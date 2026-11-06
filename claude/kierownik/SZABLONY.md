# SZABLONY — pliki projektu i zasady plików instrukcji

Czyta kierownik, gdy zakłada lub naprawia pliki projektu (oraz wykonawca, któremu to zlecono).
Szablony są po polsku, bo pliki projektu czyta właściciel.

1. Zasady AGENTS.md i CLAUDE.md (stan wytycznych OpenAI i Anthropic na 2026-10-06)
2. AGENTS.md
3. CLAUDE.md
4. docs/PROJEKT.md
5. docs/TODO.md
6. docs/tasks/T-NNN.md
7. ADR
8. .claude/settings.json (uprawnienia i ustawienia sesji kierownika)
9. Lista kontrolna przeglądu (koniec etapu)


## 1. Zasady AGENTS.md i CLAUDE.md

Jak wczytują je narzędzia:
- **Codex** łączy `AGENTS.md` z każdego katalogu od korzenia repozytorium (`.git`) do katalogu
  roboczego (w katalogu `AGENTS.override.md` ma pierwszeństwo przed `AGENTS.md`; plus globalny
  `~/.codex/AGENTS.md`). Nie schodzi poniżej katalogu roboczego. Łącznie domyślnie 32 KiB —
  nadmiar jest po cichu obcinany. Nie rozwija importów `@plik`.
- **Claude Code** czyta AGENTS.md sam (od v2.1.277) tylko wtedy, gdy w drzewie projektu nie ma CLAUDE.md,
  .claude/CLAUDE.md ani CLAUDE.local.md. Z CLAUDE.md czyta domyślnie tylko pliki CLAUDE.
  Zalecane: CLAUDE.md z importem `@AGENTS.md` (import nigdy nie wczytuje pliku dwa razy). Subagenci Claude
  Code dostają CLAUDE.md projektu automatycznie (także w worktree), więc przez import mają też AGENTS.md.
  Zdanie „przeczytaj AGENTS.md” jest słabe — Claude otworzy plik tylko, jeśli sam zdecyduje.
  Symlink zamiast importu nie działa poprawnie na Windows. Zalecany rozmiar < 200 linii na plik.
- **Antigravity (aplikacja i CLI `agy`)**: przed dodaniem osobnego pliku reguł sprawdź
  w dokumentacji używanej wersji, czy czyta AGENTS.md (np. krótkim zleceniem „wypisz polecenie
  testów z zasad projektu” bez wskazywania pliku). Jeśli nie — jego plik reguł zawiera tylko
  odesłanie do AGENTS.md i różnice narzędziowe. Zlecenia dla CLI i tak zawierają „PRZECZYTAJ: AGENTS.md”.

Wynikające zasady:
- AGENTS.md = jedyne źródło zasad wspólnych; CLAUDE.md = `@AGENTS.md` + krótka sekcja tylko dla
  Claude Code; pliki innych narzędzi tylko odsyłają. Nic nie jest kopiowane między plikami.
- Zasady ról (format raportu wykonawcy, sposób recenzji) nie należą do AGENTS.md: są w definicjach
  `kier-*` i w wierszach `[CLI]` zleceń. AGENTS.md wczytuje się w każdej sesji, także kierownika,
  więc każda linia roli w nim to koszt w każdym wywołaniu.
- Treść: polecenia, których agent nie zgadnie; środowisko i koszty; konwencje odbiegające od
  domyślnych; granice; Definition of Done. Bez: zasad ról (patrz niżej), rzeczy
  do wyczytania z kodu, standardowych konwencji języka, dokumentacji API, opisów plik po pliku,
  stanu projektu, planów i dat (te są w docs/TODO.md i docs/PROJEKT.md).
- Długość ≤ ~150 linii, najważniejsze na górze. Test każdej linii: „czy jej usunięcie spowoduje
  błąd agenta?”. Nie — usuń.
- Reguła powstaje z obserwowanego błędu (drugi raz ten sam) albo z twardej konwencji, nie „na zapas”.
- Instrukcje to wskazówki. Co musi być przestrzegane zawsze → uprawnienia, hook, CI.
- Katalog o innych zasadach (np. `frontend/` z innym stosem) → zagnieżdżony AGENTS.md tylko
  z różnicami. Codex użyje go, gdy pracuje w tym katalogu. Claude Code sam go nie wczyta (CLAUDE.md
  w drzewie wyłącza automatyczne czytanie AGENTS.md) — połóż obok `frontend/CLAUDE.md` z jedną linią
  `@AGENTS.md`; Claude Code dołączy go, gdy pracuje na plikach z tego katalogu.
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
- Testy: `<…>` | jeden test: `<…>`   (pierwsze polecenie w backtickach uruchamia `kier.py merge` i `kier.py test`)
- Lint / format / typy: `<…>`

## Środowisko i koszty
- LLM aplikacji: <np. lokalny serwer LLM pod http://localhost:<port> — darmowy, wolno używać w testach>
- Bazy: <np. testowa SQLite w tests/ — wolno; produkcyjna (zmienna DB_PROD_URL) — NIE dotykać>
- Usługi zewnętrzne: <np. wysyłka maili — w testach wyłącznie mock; płatne API X — tylko za zgodą właściciela>
- Sekrety: tylko w .env (poza Gitem), wzór w .env.example. Nie wypisuj wartości.
- Świeży worktree: <co trzeba zrobić, żeby testy ruszyły — np. `cp .env.example .env`, uruchomić usługę X>

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
- Nowe testy tylko tam, gdzie wymaga ich zadanie (kryteria, Definition of Done, konwencje wyżej).
  Jednorazowe skrypty sprawdzające trzymaj poza repozytorium i nie zamieniaj ich w stałe testy.
- Nie edytuj docs/TODO.md, docs/PROJEKT.md ani kryteriów zadania — prowadzi je kierownik.
- Nie osłabiaj, nie usuwaj i nie wyłączaj testów, żeby przeszły. Uzasadnioną zmianę testu opisz.
- Bez merge, push i przepisywania historii — robi to kierownik.
- Brak informacji: luka blokująca → zatrzymaj się i zapisz pytanie w raporcie; nieblokująca → przyjmij
  najprostsze założenie zgodne z kodem i zapisz je w raporcie.

## Definition of Done
- Kryteria spełnione i pokazane dowodem (polecenie → wynik, scenariusz użycia). Sprawdzenie, które nie
  wystartowało, albo sama kontrola składni nie są dowodem — takie przypadki w „NIE SPRAWDZONO”.
- Testy i lint przechodzą; pominięte testy wymienione w raporcie.
- README zaktualizowane, jeśli zmieniło się uruchamianie lub zachowanie widoczne dla użytkownika.
- Jeśli zadanie ma docs/tasks/T-NNN.md: zaktualizowane „Postęp”, „Odkrycia i decyzje”, „Wynik”.

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
co zweryfikowane, następny krok. W kolumnach „wyk.” / „rec.” wpisuj klasę modelu albo alias faktycznie
użyty (np. `sonnet`, `opus`) — to zapis zdarzenia, nie reguła.

```markdown
# TODO — <projekt>
Prowadzi kierownik. Agenci: wyłącznie odczyt.

## Stan (<data>)
Cel: <1 zdanie z PROJEKT.md>
Etap: E2 — <nazwa>: <obserwowalny cel etapu> (3/5 GOTOWE)
Tryb etapu: pełny | zwarty — <powód, np. „12 zadań, jeden moduł, bez decyzji projektowych”>
main @ <sha> | ostatni zweryfikowany: <sha> (<data>, <co potwierdzono>)
W toku: T-007 | W TOKU | kier-wykonawca (<klasa>) | task/T-007-import
        przydział rec.: autor sonnet/Anthropic, ryzyko NISKIE → MOCNY, inna rodzina → codex-cli <model>
Blokady: brak
Następny krok: <konkretnie: zadanie, wykonawca, czynność>
Ustalenia: <np. gałąź główna `master`, brak remote, odstępstwa od rejestru ~/.kierownik/ZESPOL.md, mapowanie plików (ROADMAP.md → TODO.md)>

## E2 — <nazwa>: <obserwowalny cel etapu>
- [ ] T-006 | DO SPRAWDZENIA | wyk. <klasa> → rec. <klasa> | <opis>
      Kryteria: <obserwowalne>; `<polecenie testu>`
- [ ] T-007 | W TOKU | wyk. <klasa> | <opis> (po T-006) | plan: docs/tasks/T-007.md
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
- [x] T-005 | <opis> | <sha scalenia> | zweryf.: <kto, klasa>, <data> |
      dowód: `<polecenie>` → <wynik>; scenariusz: <co zaobserwowano> | tokeny: wyk. <n>k, rec. <n>k
- [x] E1 zamknięty | <sha> | dowód E2E: <środowisko, dane, czynności, wynik>
```


## 6. docs/tasks/T-NNN.md (żywy plan zadania)

Tylko dla ryzyka ŚREDNIEGO/WYSOKIEGO albo zadania, którego nie da się pociąć na jednosesyjne kroki.
Uproszczony ExecPlan OpenAI: musi wystarczyć nowej sesji bez żadnej historii. Sekcje Cel–Plan pisze
architekt lub kierownik przed startem; Postęp, Odkrycia i decyzje, Wynik — wykonawca. Recenzent czyta
tylko Cel, Kontekst, Zakres i Kryteria.

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


## 8. .claude/settings.json (uprawnienia i ustawienia sesji kierownika)

Cel: Claude Code nie pyta o bezpieczne, powtarzalne polecenia, a niebezpieczne są zablokowane albo
pytają. Kolejność oceny reguł: deny → ask → allow. Wzorce dla Bash są prefiksowe i stanowią pas
bezpieczeństwa, nie pancerz (dają się obejść nietypową składnią) — prawdziwą ochroną main jest ochrona
gałęzi na GitHubie przed force push i usunięciem (nie „wymagaj pull requesta”: pętla scala lokalnie
i pcha main bezpośrednio). Polecenia testów dopasuj do projektu. Sprawdzenie: `/permissions`.

Opcjonalnie zapisz tu także model i effort kierownika — zastępują ręczne `/model` i `/effort` w każdej
sesji; wpis obowiązuje każdą sesję Claude Code w tym projekcie (gdy ma dotyczyć wszystkich projektów,
wpisz go w `~/.claude/settings.json`). Próg kompaktowania: `/autocompact 200k` (Claude Code ≥ 2.1.221)
zapisuje go w ustawieniach użytkownika i działa we wszystkich projektach; ten sam klucz to
`"autoCompactWindow": 200000` — opcjonalnie tutaj, gdy ma dotyczyć tylko tego projektu.

`CLAUDE_CODE_FORK_SUBAGENT: "0"` — wyłącza fork mode, który w sesji interaktywnej jest domyślnie włączony
i każdego subagenta uruchamia w tle. Bez tego kierownik nie może poczekać na raport ostatniego zlecenia, a wynik
przychodzi dopiero jako powiadomienie w późniejszej turze. Działa po ponownym uruchomieniu Claude Code.

`worktree.baseRef: head` — worktree subagenta (`isolation: worktree`) odgałęzia się od bieżącego HEAD
sesji, nie od `origin/HEAD`; bez tego klucza baza może nie zawierać niewypchniętych commitów kierownika.
Wykonawca i tak ustawia bazę jawnie przez sha ze zlecenia, więc ten klucz jest pasem bezpieczeństwa,
nie warunkiem działania.

```json
{
  "model": "opus",
  "worktree": { "baseRef": "head" },
  "env": { "CLAUDE_CODE_FORK_SUBAGENT": "0" },
  "permissions": {
    "allow": [
      "Bash(<polecenie testów> *)",
      "Bash(<polecenie lintu> *)",
      "Bash(codex exec *)",
      "Bash(git status)",
      "Bash(git status *)",
      "Bash(git log *)",
      "Bash(git diff *)",
      "Bash(git show *)",
      "Bash(git fetch)",
      "Bash(git fetch *)",
      "Bash(git pull --ff-only*)",
      "Bash(git rev-parse *)",
      "Bash(git symbolic-ref *)",
      "Bash(git remote -v)",
      "Bash(git remote *)",
      "Bash(git add *)",
      "Bash(git commit *)",
      "Bash(git switch *)",
      "Bash(python3 <bezwzględna ścieżka skilla>/scripts/kier.py *)",
      "Bash(git merge *)",
      "Bash(git revert *)",
      "Bash(git worktree *)",
      "Bash(git branch *)",
      "Bash(git push origin main)"
    ],
    "ask": [
      "Bash(agy *)",
      "Bash(git checkout -- *)",
      "Bash(git checkout .)",
      "Bash(git checkout -f*)",
      "Bash(git checkout --force*)",
      "Bash(git restore *)",
      "Bash(git switch -f*)",
      "Bash(git switch --discard-changes*)",
      "Bash(git worktree remove -f*)",
      "Bash(git push origin --delete *)",
      "Bash(git push origin -d *)",
      "Bash(git branch -D *)",
      "Bash(git worktree remove --force *)",
      "Bash(git worktree remove * --force*)"
    ],
    "deny": [
      "Bash(git push --force*)",
      "Bash(git push -f*)",
      "Bash(git push * --force*)",
      "Bash(git push * -f*)",
      "Bash(git push origin +*)",
      "Bash(git reset --hard*)",
      "Bash(git clean *)",
      "Bash(cat .env*)",
      "Bash(cat ./.env*)",
      "Bash(head .env*)",
      "Bash(tail .env*)",
      "Bash(printenv*)",
      "Bash(env)",
      "Read(./.env)",
      "Read(./.env.*)"
    ]
  }
}
```

Uwagi:
- `ask` odpowiada liście PYTASZ z SKILL.md, sekcja 6 (usuwanie gałęzi i worktree z niezapisaną pracą):
  pytanie, nie blokada. `git branch -d` i `git worktree remove` bez `--force` zostają w allow — Git sam
  odmawia przy niescalonej gałęzi albo plikach spoza commitów, więc rutynowe sprzątanie po scaleniu nie pyta.
- Allow dla push to dokładne polecenie `git push origin main` (dopasuj do nazwy gałęzi głównej), nie prefiks:
  każdy push z dodatkowymi flagami pyta. Wzorce `deny` z `*` w środku polecenia (np. `git push * --force*`)
  nie są potwierdzone w dokumentacji — po wklejeniu sprawdź w `/permissions`, czy `git push origin main --force`
  jest odrzucany. Forma `git push origin :<gałąź>` nie jest objęta: wzorzec kończący się
  na `:*` koliduje ze składnią prefiksu reguł i zablokowałby każdy push do origin — nie dodawaj go.
- Reguły `.env*` blokują też `.env.example` — jeśli przeszkadza, zawęź je. Reguły uprawnień działają
  osobno dla każdego narzędzia, a wzorce Bash są prefiksowe: `Read(./.env*)` nie zatrzymuje `cat .env`,
  stąd osobne wpisy Bash; `grep`/`sed` na .env, ścieżki bezwzględne i narzędzie Grep nadal nie są objęte.
  Gdy sekrety są krytyczne, dodaj hook PreToolUse odrzucający polecenia zawierające `.env`. Reguły deny
  obejmują także subagentów (ich pytania o uprawnienia trafiają do sesji głównej).
- `git checkout` nie jest w allow: wykonawcy używają `git switch`, a `git checkout -- .` / `git restore`
  kasują niezacommitowaną pracę. `agy` jest w ask, bo bez sandboxa ma dostęp do całej maszyny.
- `kier.py` (skrypt mechaniki gita kierownika) wpisz z bezwzględną ścieżką skilla, np.
  `~/.claude/skills/kierownik/scripts/kier.py` rozwinięte do pełnej ścieżki; `allowed-tools` skilla działa
  tylko w turze wywołania `/kierownik`, a kolejne tury („dalej”) potrzebują tej reguły. Reguła obejmuje cały
  skrypt, więc skrypt nie przyjmuje poleceń z wiersza poleceń: testy i lint uruchamia wyłącznie z linii
  `- Testy:` / `- Lint …:` w AGENTS.md scommitowanym na main (nie z gałęzi zadania). Zmiana tych linii jest
  więc zawsze commitem widocznym w historii. Skrypt nie używa `--force`, `reset --hard` ani `clean`. Reguły `ask` wygrywają z `allow` także między plikami ustawień.
- `"effortLevel": "high"` dopisz tylko wtedy, gdy właściciel chce wyższego effortu kierownika niż domyślny
  modelu (SKILL.md, sekcja 1, krok 6).
- Tryb auto w Claude Code (klasyfikator zamiast pytań): `"permissions": {"defaultMode": "auto"}` działa
  tylko w ustawieniach użytkownika (`~/.claude/settings.json`) albo z flagi CLI — w tym pliku projektu
  wartość `auto` jest ignorowana. Reguły `deny` działają także w trybie auto.
- Worktree subagenta to świeży checkout bez plików nieśledzonych. Jeśli testy potrzebują `.env`, dodaj
  w korzeniu projektu `.worktreeinclude` (składnia .gitignore) z nazwami plików do skopiowania do każdego
  nowego worktree — Claude Code skopiuje tylko te, które są jednocześnie ignorowane przez Git.


## 9. Lista kontrolna przeglądu (koniec etapu albo po powtórzonym błędzie)

- [ ] Polecenia w AGENTS.md działają (użyte w tym etapie).
- [ ] „Środowisko i koszty” zgodne ze stanem faktycznym (AGENTS.md i PROJEKT.md mówią to samo),
      łącznie z tym, co trzeba zrobić w świeżym worktree.
- [ ] Brak stanu, dat i list zadań w AGENTS.md / CLAUDE.md.
- [ ] AGENTS.md ≤ ~150 linii; łącznie z zagnieżdżonymi plikami < 32 KiB.
- [ ] AGENTS.md nie ma sekcji ról („Raport po zadaniu”, „Weryfikacja cudzej zmiany”) — od v11 są
      w definicjach `kier-*` i w wierszach `[CLI]` zleceń; jeśli są, usuń je.
- [ ] CLAUDE.md zaczyna się od `@AGENTS.md` i nie powtarza jego treści.
- [ ] Brak sprzecznych reguł (`/doctor prompt-audit`).
- [ ] Pułapki z tego etapu dopisane, nieaktualne usunięte.
- [ ] PROJEKT.md opisuje stan po etapie (moduły, przepływ, stan funkcjonalny).
- [ ] Brak osieroconych gałęzi `worktree-*` i worktree w `.claude/worktrees/` (`git worktree list`).


## Źródła (sprawdzone 2026-10-03/06)
- Anthropic — CLAUDE.md i AGENTS.md: https://code.claude.com/docs/en/memory
- Anthropic — Best practices for Claude Code: https://code.claude.com/docs/en/best-practices
- Anthropic — Skills: https://code.claude.com/docs/en/skills
- Anthropic — Subagents: https://code.claude.com/docs/en/sub-agents
- Anthropic — Worktrees (w tym izolacja subagentów): https://code.claude.com/docs/en/worktrees
- Anthropic — Model configuration (aliasy, effort): https://code.claude.com/docs/en/model-config
- Anthropic — Permissions: https://code.claude.com/docs/en/permissions
- Anthropic — Settings: https://code.claude.com/docs/en/settings
- Anthropic — Effective harnesses for long-running agents:
  https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents
- OpenAI — AGENTS.md: https://developers.openai.com/codex/guides/agents-md (zachowanie sprawdzone
  w kodzie: https://github.com/openai/codex/blob/main/codex-rs/core/src/agents_md.rs)
- OpenAI — Codex `exec` (flagi `-o`, `--json`, stdin): https://github.com/openai/codex/blob/main/codex-rs/exec/src/cli.rs
- OpenAI — ExecPlans: https://github.com/openai/openai-cookbook/blob/main/articles/codex_exec_plans.md
- OpenAI — Codex best practices: https://developers.openai.com/codex/learn/best-practices
