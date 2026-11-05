# Kierownik projektu — Claude i Codex

**Zacznij tutaj.** Wybierz folder dla narzędzia, którego używasz:

| Folder | Co zawiera | Instrukcja |
|---|---|---|
| **`codex/`** | Kierownik v13 przystosowany do Codex; wywołanie `$kierownik` | [Instalacja i użycie](codex/README.md) |
| **`claude/`** | Kierownik v13 dla Claude Code; wywołanie `/kierownik` | [Instalacja i użycie](claude/README.md) |
| `archiwum/` | Starsze prompty v6, SDD i v7, zachowane do porównania | [Spis archiwum](archiwum/README.md) |

Obie wersje to v13: mechanika gita w skrypcie `scripts/kier.py`, procedura konfliktów przy równoległej pracy,
wykonawca domyślnie w klasie MOCNY, zgoda na `agy` bez sandboxa pytana na każdej maszynie
([claude/ANALIZA.md](claude/ANALIZA.md), decyzja 14). Zbudowana na v12 — zespole wielu dostawców ze wspólnym
rejestrem `~/.kierownik/ZESPOL.md` (decyzja 13) — i na v11: v10 z gałęzi **`claude/eloquent-meitner-98b5px`**,
commit [c45c525](https://github.com/sygnatura/Orkiestrator-AI/commit/c45c525445034b7859f66dda158e2226489db4b2),
po optymalizacji zużycia tokenów (instrukcje dla modeli po angielsku, komunikacja
i pliki projektu po polsku; uzasadnienie w [claude/ANALIZA.md](claude/ANALIZA.md),
decyzja 12). Oryginał v10 jest w historii Gita i na źródłowej gałęzi.
Starsze pliki z głównego katalogu zostały przeniesione do archiwum.

## Instalacja i aktualizacja — jedno polecenie

Z głównego katalogu tego repozytorium (Python 3.11+, Linux, macOS i Windows):

```bash
python3 install.py --dry-run   # najpierw zobacz plan, nic się nie zmienia
python3 install.py             # instalacja albo aktualizacja
```

W PowerShell użyj `py install.py`. Instalator sam wykrywa Claude Code i Codex (`--claude` / `--codex`
wybiera jedno) i za każdym razem robi to samo, niezależnie od tego, którą wersję masz teraz:

- **Claude Code:** kopiuje skill do `~/.claude/skills/kierownik/` i agentów `kier-*` do `~/.claude/agents/`.
  Pliki z dowolnej wcześniejszej wersji (v8–v13, rozpoznawane po sumach kontrolnych
  w `install-history.json`) podmienia. Pliki, które zmieniłeś ręcznie, pokazuje i podmienia dopiero po
  Twojej zgodzie (albo z `--yes`). Pliki usunięte z pakietu kasuje. Wszystko, co nadpisuje lub kasuje,
  najpierw kopiuje do `~/.kierownik/backups/<data>/`. Puste po tym katalogi usuwa, a na koniec sprawdza, czy
  każdy plik pakietu jest na miejscu bajt w bajt.
- **Codex:** uruchamia `codex/install.py --user --register-agents --upgrade` (poprzednia instalacja
  ląduje w `~/.agents/backups/`).
- **Starsze wersje:** usuwa z kopią zapasową skill `architekt` z pierwszego portu Codex — w katalogu
  domowym i w projektach podanych przez `--project <ścieżka>` (tam też aktualizuje projektową instalację
  Codex, jeśli istnieje).
- **Nigdy nie rusza** Twojego stanu: starego `ZESPOL.md` w katalogu skilla, rejestru
  `~/.kierownik/ZESPOL.md` ani Twoich własnych agentów.

Przy pierwszym starcie po aktualizacji kierownik sam przeniesie stary `ZESPOL.md` do rejestru.

## Chcę używać Codex

Po `python3 install.py` otwórz nową sesję Codex **w katalogu prowadzonego projektu** i wpisz:

```text
$kierownik
```

Szczegóły i instalacja tylko dla jednego projektu są w [instrukcji Codex](codex/README.md).

## Chcę używać Claude Code

Po `python3 install.py` w prowadzonej sesji Claude Code użyj `/kierownik`
([instrukcja](claude/README.md)). Ręczne kopiowanie plików bez instalatora też jest tam opisane.
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
install.py          instalator i aktualizator obu wersji (+ install-history.json, tests/)
claude/             zestaw Claude v13
  kierownik/        skill, zlecenia, szablony i stan zespołu
  agents/           cztery role Claude
codex/              zestaw Codex v13
  install.py        instalator
  skills/kierownik/ skill i wszystkie jego zasoby
  docs/             analiza portu, wyniki walidacji i źródła
  tests/            testy instalatora i adaptera CLI
archiwum/           poprzednie wersje
.github/workflows/  CI: oba zestawy testów na Linuksie, Windows i macOS (Python 3.11 i 3.13)
evals/              evale: projekt testowy, ukryte testy, ocena przebiegów (evals/README.md)
```

Testy lokalnie: `python3 -m unittest discover -s tests` oraz `python3 -m unittest discover -s codex/tests`.
To samo uruchamia CI przy każdym PR i pushu do main.

Do zwykłego użycia wystarczy instrukcja wybranego narzędzia. Informacje
o architekturze i granicach sprawdzenia portu są w
[dokumentacji Codex](codex/docs/ANALIZA.md) oraz
[raporcie walidacji](codex/docs/VALIDATION.md).
