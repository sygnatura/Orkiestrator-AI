# Kierownik projektu — Claude i Codex

**Zacznij tutaj.** Wybierz folder dla narzędzia, którego używasz:

| Folder | Co zawiera | Instrukcja |
|---|---|---|
| **`codex/`** | Kierownik v12 przystosowany do Codex; wywołanie `$kierownik` | [Instalacja i użycie](codex/README.md) |
| **`claude/`** | Kierownik v12 dla Claude Code; wywołanie `/kierownik` | [Instalacja i użycie](claude/README.md) |
| `archiwum/` | Starsze prompty v6, SDD i v7, zachowane do porównania | [Spis archiwum](archiwum/README.md) |

Obie wersje to v12 — zespół wielu dostawców ze wspólnym rejestrem `~/.kierownik/ZESPOL.md`
([claude/ANALIZA.md](claude/ANALIZA.md), decyzja 13) — zbudowana na v11: v10 z gałęzi **`claude/eloquent-meitner-98b5px`**,
commit [c45c525](https://github.com/sygnatura/Orkiestrator-AI/commit/c45c525445034b7859f66dda158e2226489db4b2),
po optymalizacji zużycia tokenów (instrukcje dla modeli po angielsku, komunikacja
i pliki projektu po polsku; uzasadnienie w [claude/ANALIZA.md](claude/ANALIZA.md),
decyzja 12). Oryginał v10 jest w historii Gita i na źródłowej gałęzi.
Starsze pliki z głównego katalogu zostały przeniesione do archiwum.

## Chcę używać Codex

Z głównego katalogu tego repozytorium, na maszynie z Codex i Pythonem 3.11+:

```bash
python3 codex/install.py --user --register-agents
```

Jeżeli wcześniej instalowałeś ten pakiet, dodaj `--upgrade`.
Następnie otwórz nową sesję Codex **w katalogu prowadzonego projektu** i wpisz:

```text
$kierownik
```

Installer kopiuje cały potrzebny zestaw. Nie musisz osobno instalować plików
z `skills/`, `roles/` ani `scripts/`. Szczegóły, PowerShell i instalacja tylko
dla jednego projektu są w [instrukcji Codex](codex/README.md).

## Chcę używać Claude Code

Przejdź do `claude/` i wykonaj polecenia z [instrukcji](claude/README.md#instalacja-raz-na-maszynę).
W prowadzonej sesji Claude Code użyj `/kierownik`.
Wzmianka o `archiwum/` w tej instrukcji odnosi się teraz do
[wspólnego archiwum w głównym katalogu](archiwum/README.md).

## Chcę kontynuować w Codex po Claude

Otwórz ten sam projekt z aktualnym stanem Gita i wpisz:

```text
$kierownik Przejmij projekt po kierowniku Claude i kontynuuj
z istniejących docs/PROJEKT.md, docs/TODO.md oraz Gita.
```

Stan pracy znajduje się **w prowadzonym projekcie**, przede wszystkim
w `docs/TODO.md`. To repozytorium zawiera narzędzia kierownika.
Przed przełączeniem najlepiej poprosić Claude o zapisanie checkpointu.
[Instrukcja przejęcia](codex/skills/kierownik/PRZEJECIE.md) opisuje również
zadania w toku i artefakty, które trzeba przenieść między maszynami.

## Gdzie są szczegóły techniczne

```text
README.md           punkt startowy
claude/             zestaw Claude v12
  kierownik/        skill, zlecenia, szablony i stan zespołu
  agents/           cztery role Claude
codex/              zestaw Codex v12
  install.py        instalator
  skills/kierownik/ skill i wszystkie jego zasoby
  docs/             analiza portu, wyniki walidacji i źródła
  tests/            testy instalatora i adaptera CLI
archiwum/           poprzednie wersje
```

Do zwykłego użycia wystarczy instrukcja wybranego narzędzia. Informacje
o architekturze i granicach sprawdzenia portu są w
[dokumentacji Codex](codex/docs/ANALIZA.md) oraz
[raporcie walidacji](codex/docs/VALIDATION.md).
