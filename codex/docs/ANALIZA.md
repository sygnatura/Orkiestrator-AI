# Port Claude v10 → Codex

Źródło: `claude/eloquent-meitner-98b5px` @ c45c525, a nie starsze prompty main.
Port zastępuje wcześniejszy codex/; pliki źródłowe nie są zmieniane.

## Zachowana metoda v10

Autonomia według ryzyka, małe taski, ciężka praca delegowana, krótkie
raporty, cztery role, klasy modeli, wybiórcza recenzja innej rodziny,
punkty kontrolne po tasku, testy po merge, E2E celu etapu, decyzja właściciela
o nowym etapie. Kierownik może czytać kod, testować, robić drobiazgi, uzupełniać
dokumentację i sam integrować/pushować zatwierdzone zmiany. Właściciel nie
jest domyślnym kurierem promptów. Brak dodatkowej rodziny/modelu nie blokuje
sam w sobie całego etapu: wyjątki są jawne, a kryteria nadal wymagają dowodów.

V10 celowo nie wymaga statusów SDD i osobnych plików raportów. Wspólne
PROJEKT/TODO/DONE/karty/ADR są formatem interoperacyjności, nie transkrypt
narzędzia. Dlatego przejęcie może zaczynać się od tego samego taska/werdyktu/
integracji; nie wymaga przywracania rozmowy Claude.

## Zmiany wymagane przez Codex

| Claude v10 | Codex |
|---|---|
| `/kierownik`, disable-model-invocation | `$kierownik`, policy.allow_implicit_invocation=false |
| CLAUDE_SKILL_DIR | Rzeczywista ścieżka skill; odsyłacze względne |
| agents/*.md, tools/model/effort frontmatter | roles/*.toml, developer_instructions, sandbox/model/reasoning_effort |
| Narzędzie Agent z modelem i isolation | Schemat rzeczywiście dostępnych narzędzi; helper exec gdy brak izolacji cwd |
| Automatyczny nowy worktree subagenta | Jawny lokalny worktree od bazy; istniejący katalog w kolejnej rundzie |
| worktree.baseRef i gałęzie worktree-* | Brak udawania tego ustawienia; kierownik podaje pełny SHA i katalog |
| Effort tylko w definicji Claude | Obsługiwany przez daną wersję Codex config/narzędzie; nie zakładamy ograniczenia Claude |
| Aliasy Claude na najnowszy model linii | Sprawdzone identyfikatory dostępne na koncie; bootstrap dziedziczy model |
| Automatyczne CLAUDE/import AGENTS | Jawne reguły AGENTS i reguły katalogu; importy Claude odczytywane ręcznie |
| /clear i /autocompact | Checkpoint i nowy wątek; bez obietnicy przeniesienia procesów |
| Równoległe worktree | Lokalnie do 4; cloud shared checkout kolejno, bez worktree bez żądania |
| Zapas Codex/Antigravity | Codex główny; Claude/Antigravity lub skonfigurowany zamiennik jako zapas |

Wszystkie pola ról sprawdzono względem publicznego schematu Codex.
Nie ma gwarancji, że każdy klient cloud udostępnia custom role/model override
albo że profile z dysku zastępują zarządzaną konfigurację platformy.
Dlatego API sprawdzamy na starcie i mamy świeże sesje CLI jako ścieżkę
wykonania; niedostępności CLI/natywnych narzędzi nie maskujemy fikcyjną delegacją.

## Różnice techniczne i granice

Worktree nie ogranicza dostępu do całej maszyny. Helper używa sandboxa
Codex i nie włącza flag bypass; noninteractive never oznacza odmowę eskalacji,
a nie automatyczne obejście uprawnień. Recenzent workspace-write jest potrzebny
do runnerów zapisujących wyniki; zakaz napraw źródeł i kontrola HEAD/status/
diff bronią odrębności recenzji. To nie pełna kontrola wszelkich efektów w
usługach zewnętrznych; zlecenie nadal ogranicza dane i operacje.

Przy kopiowaniu diagnostyki wymagamy rzeczywistego exit zamiast tail exit 0.
Nie usuwamy starych worktree/niescalonych gałęzi z nieznaną pracą jako
automatycznej czynności wznowienia. Nie modyfikujemy oryginalnej instalacji
Claude w imię ujednolicenia. Przyjęty proces Git i nadrzędne uprawnienia
pozostają obowiązujące, a publikacja w cloud jest raportowana tylko po dowodzie.

Obecne testy sprawdzają mechanikę instalacji/wywołań, nie poprawność wszystkich
decyzji modelu. Pilot: kopia projektu v10, aktywny task z Claude, jedna pętla
wykonanie→recenzja→integracja→checkpoint, nowa sesja Codex i powrót do Claude.
Przy błędzie reguły poprawia się z dowodu, nie rozbudowuje system na zapas.
