# SZABLONY v12 — wspólny stan projektu i reguły Codex

Czytaj przy tworzeniu/naprawie plików, nie w każdym wznowieniu.
Wzory PROJEKT/TODO/karty pochodzą z Claude v10. Nie nadpisuj działających
odpowiedników, CLAUDE ani jego settings przy przejęciu przez Codex.

## 1. Reguły i zgodność narzędzi

AGENTS to wspólne reguły; stan i daty należą do PROJEKT/TODO. Codex
odczytuje AGENTS/AGENTS.override zgodnie z aktualnym klientem i katalogiem.
Nie rozwija importów `@plik`: istotne importy z CLAUDE otwieraj jawnie.
W zleceniach zawsze wskaż reguły właściwe dla obszaru. Objętość około
150 linii; najważniejsze na górze. Nie wkładaj skilla kierownika do
AGENTS wszystkich wykonawców. Definicje ról i uprawnienia nie zastępują
zasad projektu, a zasady ról (format raportu, sposób recenzji) są w rolach,
nie w AGENTS — AGENTS wczytuje się w każdej sesji i każdym agencie. Reguły dla wykonawcy nie zabraniają kierownikowi jego
zatwierdzonych czynności administracyjnych, testowania i integracji.

CLAUDE może pozostać importem AGENTS i różnicami dla Claude. Nie zakładaj
konkretnej wersji jego automatycznego odczytu. Dla zagnieżdżonych reguł
zachowaj istniejący proces, bez duplikowania wspólnych instrukcji.
Instrukcje nie są kontrolą dostępu: sandbox, ochrona gałęzi i CI chronią
rzeczy, których naruszenia nie wolno dopuścić. Nie instaluj hooków na zapas.

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
- Jako wykonawca nie edytuj docs/TODO.md, docs/PROJEKT.md ani kryteriów — prowadzi je kierownik.
- Nie osłabiaj, nie usuwaj i nie wyłączaj testów, żeby przeszły. Uzasadnioną zmianę testu opisz.
- Merge i zwykły push robi kierownik, nie wykonawca; przepisywanie historii wymaga osobnej zgody.
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
użyty (rzeczywiście użyty model) — to zapis zdarzenia, nie reguła.

```markdown
# TODO — <projekt>
Prowadzi kierownik. Agenci: wyłącznie odczyt.

## Stan (<data>)
Cel: <1 zdanie z PROJEKT.md>
Etap: E2 — <nazwa>: <obserwowalny cel etapu> (3/5 GOTOWE)
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


## 8. Konfiguracja Codex

Instalator z --register-agents dopisuje tylko brakujące tabele
`agents.kier-*` z `description` i `config_file` wskazującym właściwe role.
Zachowuje ustawienia modelu, uprawnień, MCP, limity i inne role.
Konflikt nazwy roli przerywa przed zmianą plików. Projektowy config może
wymagać zaufania repo w kliencie; installer nie wpisuje zaufania za właściciela.
Nowa sesja odświeża role. W clientach bez custom roles pozostaje helper CLI.
Nie dodawaj flag multi-agent z pamięci: sprawdź wersję i `codex features list`.
Nie zmieniaj ustawień zarządzanych przez platformę.

Effort i model to opcjonalne pola TOML ról, a nie model Claude z frontmatter.
Ustaw je zgodnie z rejestrem `~/.kierownik/ZESPOL.md` i dostępnymi modelami. Nie powielaj identyfikatorów
modeli w README/zleceniach jako stałej polityki; historyczny zapis faktycznie
użytego modelu w dowodach jest potrzebny.

Katalog procesu CLI określa `-C`, a nie samo `cd` w treści zlecenia.
Sandbox analityka read-only, wykonawcy workspace-write — stosowany przez run_agent.py (`-s`); natywna rola może
dziedziczyć sandbox kierownika, więc jej efektywny sandbox sprawdza test dymny. Recenzent potrzebuje
lokalnych zapisów runnerów testowych, więc workspace-write plus zakaz
zmian źródeł i kontrola HEAD/status/diff po przebiegu. Worktree samo nie
blokuje sieci ani dostępu do reszty maszyny. Braki dostępu rozwiąż wspieranym
mechanizmem klienta, bez wyłączania ochrony. Nie kopiuj `.env` ze źródła,
jeśli wystarczy przykład i bezpieczna konfiguracja testowa.

Testy z ograniczonym logiem muszą zachować kod runnera: Bash pipefail,
PowerShell zachowany LASTEXITCODE. Weryfikacja pustego zestawu nie dowodzi
funkcji. Niczego nie instaluj z wyłączoną kontrolą TLS/podpisów/checksum.

## 9. Przegląd końca etapu

- Komendy instalacji/testów/lintu rzeczywiście działają.
- Środowisko i koszty w AGENTS/PROJEKT zgodne z konfiguracją i użytymi usługami.
- PROJEKT opisuje obecny system, TODO aktualny plan/dowody/następny krok.
- AGENTS zwięzły, bez list zadań; CLAUDE zachowany, reguły nie są sprzeczne.
- AGENTS bez sekcji ról („Raport po zadaniu”, „Weryfikacja cudzej zmiany”) — od v11 są w rolach i zleceniach.
- Pułapki dopisane po faktycznych błędach, nieaktualne usunięte.
- Stare Zrobione dopisane do DONE, istotne dowody dostępne w repo.
- Własne worktree po udanym merge zabezpieczone i posprzątane; cudze zachowane.
- Nie obiecuj, że lokalny proces, ignorowane pliki albo sesja przejdą do nowej maszyny.

Źródło procesu: gałąź claude/eloquent-meitner-98b5px, commit c45c525,
kierownik/SZABLONY.md. Źródła techniczne:
https://developers.openai.com/codex/guides/agents-md
https://developers.openai.com/codex/multi-agent
https://github.com/openai/codex/blob/main/codex-rs/core/config.schema.json
https://github.com/openai/codex/blob/main/codex-rs/exec/src/cli.rs
