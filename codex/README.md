# Orkiestracja projektu w Codex

Pakiet przenosi role z `ORKIESTRATOR_PROJEKTU.md` (v6),
`ORKIESTRATOR_PROJEKTU_SDD.md`, `ARCHITEKT_PROJEKTU.md` i
`PROJECT_WORKFLOW.md` do skills Codex. Oryginały pozostają bez zmian.

Wyniki sprawdzenia pakietu i jego ograniczenia zapisano w
[VALIDATION.md](VALIDATION.md).

`kierownik` prowadzi kolejkę, przygotowuje zlecenia i odbiera dowody.
`architekt` przygotowuje plan i specyfikacje oraz diagnozuje problemy przekrojowe.
Wykonawca i weryfikator dostają osobne zlecenia; kierownik nie implementuje
ani nie recenzuje własnej pracy. Domyślnie właściciel uruchamia te sesje,
tak jak w oryginalnym v6. Dostępna jest także jawnie włączana delegacja
przez narzędzia agentów Codex, jeśli klient je udostępnia.

## Instalacja w repozytorium prowadzonego projektu

Wymagane: Python 3, Git i klient Codex obsługujący skills. Pakiet nie wymaga
zewnętrznych bibliotek, kluczy API ani zmiany konfiguracji modeli.

Z katalogu tego pakietu uruchom, podstawiając **repozytorium projektu**:

```bash
python3 install.py --project /sciezka/do/projektu
```

W PowerShell:

```powershell
py .\install.py --project 'C:\dev\projekt'
```

Instalator kopiuje dwa samowystarczalne foldery do
`<projekt>/.agents/skills/kierownik/` i `<projekt>/.agents/skills/architekt/`.
Nie zastępuje istniejących skills, `AGENTS.md`, `CLAUDE.md` ani dokumentacji
projektu. Powtórna instalacja identycznej wersji jest bez zmian; kolizja
przerywa instalację przed kopiowaniem. Aktualizację różniącej się wersji
wykonaj osobno po przejrzeniu różnic i zachowaniu swoich zmian.

Otwórz nową sesję Codex w **repozytorium projektu**, aby klient odświeżył
katalog skills. Wywołaj skill przez `$kierownik` (lub wybierz go w interfejsie
klienta). Przykładowy prompt:

```text
$kierownik
Przejmij projekt po kierowniku Claude. Odtwórz stan z istniejącej kolejki,
Git, planu oraz raportów i recenzji. Zachowaj proces i kontynuuj od ostatniego
potwierdzonego punktu. Domyślnie przygotowuj mi zlecenia do osobnych sesji.
```

Opcjonalnie można wskazać handoff lub rzeczywistą ścieżkę rejestru:

```text
$kierownik Kontynuuj według handoff w WORKBOARD.md; aktywne zadanie CDI-17.
```

Architekta wywołuj w osobnej sesji przez `$architekt`, przekazując zlecenie
kierownika. Pakiet przechowywany w `codex/skills/` jest materiałem do
instalacji; samo dodanie go do tego repo nie rejestruje skills w innym projekcie.

## Różnice względem Claude Code

| Obszar | Wersja Codex |
|---|---|
| Wejście w rolę | `SKILL.md` z nazwą i opisem; `$kierownik` / `$architekt` |
| Reguły projektu | Codex używa `AGENTS.md`; przy przejęciu czyta także istotne `CLAUDE.md` i wskazane w nim pliki. Nie zakłada obsługi importu `@AGENTS.md`. |
| Stan | Ta sama kolejka i te same ID, plan, TASK/VERIFY, REPORT/REVIEW i Git; bez odrębnej kolejki Codex |
| Starszy v6 | Zachowanie statusów `TODO`, `DO SPRAWDZENIA` i płaskich `docs/tasks/T-NNN.md`; żadnej automatycznej migracji do SDD |
| Delegacja | Ręczna domyślnie; natywna po autoryzacji i sprawdzeniu narzędzi klienta. Brak narzędzi oznacza gotowy prompt, nie pozorne uruchomienie. |
| Recenzja | Osobna sesja **i inny model niż autor**, najlepiej inna rodzina; subagent z tym samym modelem daje tylko dodatkowe sprawdzenie |
| Uprawnienia | Skill nie zmienia sandboxa ani zgód; ograniczenia klienta nadal obowiązują |
| Wznowienie | Odtworzenie stanu z plików i Git. `codex resume` dotyczy sesji Codex; nie importuje sesji Claude. |
| Cloud | Korzystanie z istniejącego checkoutu w izolowanym zadaniu; bez tworzenia worktree, chyba że właściciel tego zażąda |

Wywołanie `$kierownik` nie uruchamia lokalnego Claude, Qwen ani zewnętrznego
modelu. Dostępność sesji/modelu trzeba sprawdzić. Nie zapisujemy arbitralnych
identyfikatorów modeli, profili ani wymaganej flagi `multi_agent`: zależą od
wersji klienta i uprawnień konta. Prompt nie jest techniczną kontrolą dostępu.

## Przejęcie bez utraty punktu kontynuacji

Najlepiej przed zmianą narzędzia poprosić Claude o `/handoff` zapisany
w dotychczasowej kolejce. Codex może też przejąć projekt bez tego: odczyta
stan i wskaże tylko brakujący dowód lub decyzję. Nie przenosi ukrytej pamięci,
niezatwierdzonych ustaleń z czatu, nieobecnych plików, lokalnych gałęzi ani
żywych procesów z innej maszyny. Przenieś potrzebne artefakty lub udostępnij
checkout, w którym istnieją. Nie oznaczaj projektu jako ukończonego na podstawie
samego streszczenia rozmowy.

`status`, `gotowe T-NNN`, `pomysl` i `handoff` są poleceniami w treści
wiadomości do kierownika. Zapisy `/status` i `/handoff` zachowują znaczenie
z oryginałów, ale klient może przechwytywać ukośnik jako własną komendę;
wtedy napisz np. `$kierownik wykonaj handoff`.

Przed produkcyjnym użyciem sprawdź na kopii projektu: przejęcie aktywnego
ZLECONE bez ponownego zlecenia; odbiór raportu bez recenzji; odrzucenie recenzji
autora; brak potwierdzenia integracji; kontynuację po handoff. Oczekiwane
działania opisuje [procedura przejęcia](skills/kierownik/references/PRZEJECIE.md).

## Źródła techniczne i zakres sprawdzenia

- [Skills Codex](https://developers.openai.com/codex/skills)
- [Reguły AGENTS.md](https://developers.openai.com/codex/guides/agents-md)
- [Agenci Codex](https://developers.openai.com/codex/multi-agent)
- [Publiczny parser skills](https://github.com/openai/codex/blob/main/codex-rs/skills/src/parser.rs)

Rozpoznawanie skills można sprawdzić bez wywoływania modelu przez `skills/list`
w lokalnym app-server Codex. Takie sprawdzenie potwierdza format i wykrywanie
pakietu, ale nie dowodzi poprawnego prowadzenia rzeczywistego projektu przez
model. Pełna kontynuacja wymaga repozytorium projektu i jego dowodów.
