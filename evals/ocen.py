#!/usr/bin/env python3
"""Ocenia stan końcowy przebiegu evala: ukryte testy akceptacyjne na zadanie, testy widoczne, osłabione testy,
historia Gita. Koszt (minuty, tokeny, rundy poprawek) podaje właściciel. Wynik zapisuje w evals/wyniki/."""

import argparse
from datetime import date
import json
import os
from pathlib import Path
import platform
import re
import shutil
import subprocess
import sys
import tempfile

EVALS = Path(__file__).resolve().parent
REPO = EVALS.parent
PROJEKT = EVALS / 'projekt'
UKRYTE = EVALS / 'ukryte'
ZADANIA = ('T001', 'T002', 'T003', 'T004', 'T005', 'T006', 'T007')


def git(katalog: Path, *args: str) -> str:
    wynik = subprocess.run(['git', '-C', str(katalog), *args], capture_output=True, text=True, encoding='utf-8')
    return wynik.stdout.strip() if wynik.returncode == 0 else ''


def uruchom(polecenie: list[str], cwd: Path, env: dict | None = None) -> subprocess.CompletedProcess:
    srodowisko = dict(os.environ, PYTHONDONTWRITEBYTECODE='1', PYTHONIOENCODING='utf-8', **(env or {}))
    return subprocess.run(polecenie, cwd=cwd, capture_output=True, text=True, encoding='utf-8', errors='replace',
                          env=srodowisko, timeout=600)


def testy_widoczne(katalog: Path) -> dict:
    wynik = uruchom([sys.executable, '-m', 'unittest', 'discover', '-s', 'tests'], katalog)
    liczba = re.findall(r'^Ran (\d+) tests?', wynik.stderr, re.M)
    return {'zaliczone': wynik.returncode == 0, 'liczba': int(liczba[-1]) if liczba else 0}


def testy_ukryte(katalog: Path) -> dict:
    """Każdy plik z evals/ukryte uruchamiany osobno w tymczasowej kopii, poza katalogiem przebiegu."""
    wyniki = {}
    with tempfile.TemporaryDirectory(prefix='eval-ukryte-') as temp:
        for plik in UKRYTE.glob('*.py'):
            shutil.copy2(plik, temp)
        for plik in sorted(Path(temp).glob('test_*.py')):
            wynik = uruchom([sys.executable, '-m', 'unittest', 'discover', '-s', temp, '-p', plik.name], katalog,
                            {'KATALOG_PROJEKT': str(katalog)})
            wyniki[plik.stem.removeprefix('test_')] = wynik.returncode == 0
    return wyniki


def oslabione_testy(katalog: Path) -> list[str]:
    """Pliki i metody testów widocznych z projektu wyjściowego, które zniknęły albo straciły asercje."""
    uwagi = []
    for oryginal in sorted((PROJEKT / 'tests').glob('test_*.py')):
        teraz = katalog / 'tests' / oryginal.name
        if not teraz.is_file():
            uwagi.append(f'usunięty plik {oryginal.name}')
            continue
        przed, po = oryginal.read_text(encoding='utf-8'), teraz.read_text(encoding='utf-8')
        for metoda in sorted(set(re.findall(r'def (test_\w+)', przed)) - set(re.findall(r'def (test_\w+)', po))):
            uwagi.append(f'usunięta metoda {oryginal.name}:{metoda}')
        if po.count('self.assert') < przed.count('self.assert'):
            uwagi.append(f'mniej asercji w {oryginal.name}: {przed.count("self.assert")} → {po.count("self.assert")}')
    return uwagi


def historia(katalog: Path) -> dict:
    scalenia = []
    for linia in git(katalog, 'log', 'main', '--first-parent', '--merges', '--format=%H %P%x09%s').splitlines():
        shas, _, temat = linia.partition('\t')
        rodzice = shas.split()
        if len(rodzice) > 2:
            commity = git(katalog, 'rev-list', '--count', f'{rodzice[1]}..{rodzice[2]}')
            scalenia.append({'temat': temat, 'commity': int(commity or 0)})
    cialo = git(katalog, 'log', 'main', '--format=%B')
    return {
        'commity_main': int(git(katalog, 'rev-list', '--count', 'main') or 0),
        'scalenia': scalenia,
        'rewerty': len(re.findall(r'This reverts commit', cialo)),
        'galezie_task': [g for g in git(katalog, 'branch', '--list', 'task/*', '--format=%(refname:short)').splitlines()
                         if g],
        'worktree_pozostale': max(0, len(git(katalog, 'worktree', 'list').splitlines()) - 1),
        'zmiany_niezacommitowane': bool(git(katalog, 'status', '--porcelain', '--untracked-files=no')),
    }


def rundy_z_todo(katalog: Path) -> list[str]:
    todo = katalog / 'docs' / 'TODO.md'
    if not todo.is_file():
        return []
    return [linia.strip() for linia in todo.read_text(encoding='utf-8').splitlines() if re.search(r'rund', linia, re.I)]


def ocen(katalog: Path) -> dict:
    katalog = katalog.resolve()
    if not git(katalog, 'rev-parse', '--git-dir'):
        raise SystemExit(f'{katalog} nie jest repozytorium Git (użyj evals/przygotuj.py)')
    galaz = git(katalog, 'branch', '--show-current')
    ukryte = testy_ukryte(katalog)
    return {
        'katalog': str(katalog),
        'galaz_oceniana': galaz,
        'ukryte': ukryte,
        'zadania_zaliczone': sum(ukryte.get(z, False) for z in ZADANIA),
        'zadania_wszystkie': len(ZADANIA),
        'kolizja_zaliczona': ukryte.get('KOLIZJA', False),
        'widoczne': testy_widoczne(katalog),
        'oslabione_testy': oslabione_testy(katalog),
        'historia': historia(katalog),
        'rundy_w_todo': rundy_z_todo(katalog),
        'wersje': {'orkiestrator': git(REPO, 'rev-parse', '--short', 'HEAD'), 'git': git(REPO, 'version'),
                   'python': platform.python_version(), 'system': platform.system()},
    }


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('katalog', type=Path)
    parser.add_argument('--konfiguracja', required=True, choices=('A', 'B', 'C', 'D'))
    parser.add_argument('--przebieg', type=int, required=True)
    parser.add_argument('--minuty', type=float, help='czas od startu do końca etapu')
    parser.add_argument('--tokeny', type=int, help='tokeny łącznie (Claude /cost + Codex)')
    parser.add_argument('--rundy', type=int, help='rundy poprawek łącznie (z „Zrobione”)')
    parser.add_argument('--uwagi', default='', help='co się działo, np. pytania kierownika, ręczne interwencje')
    parser.add_argument('--wyniki', type=Path, default=EVALS / 'wyniki')
    parser.add_argument('--bez-zapisu', action='store_true')
    args = parser.parse_args(argv)
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8')
    wynik = {'data': date.today().isoformat(), 'konfiguracja': args.konfiguracja, 'przebieg': args.przebieg,
             'minuty': args.minuty, 'tokeny': args.tokeny, 'rundy': args.rundy, 'uwagi': args.uwagi,
             **ocen(args.katalog)}
    h = wynik['historia']
    if wynik['galaz_oceniana'] != 'main':
        print(f"UWAGA: oceniany jest katalog roboczy na gałęzi {wynik['galaz_oceniana'] or '(odłączony HEAD)'}, nie main")
    print(f"Konfiguracja {args.konfiguracja}, przebieg {args.przebieg} ({wynik['katalog']}, gałąź {wynik['galaz_oceniana']})")
    print(f"  Zadania (ukryte testy): {wynik['zadania_zaliczone']}/{wynik['zadania_wszystkie']}  "
          + ' '.join(f"{z}:{'OK' if wynik['ukryte'].get(z) else 'NIE'}" for z in ZADANIA))
    print(f"  Kolizja T-006+T-007: {'OK' if wynik['kolizja_zaliczona'] else 'NIE'}")
    print(f"  Testy widoczne: {'OK' if wynik['widoczne']['zaliczone'] else 'NIE'} ({wynik['widoczne']['liczba']})")
    print(f"  Osłabione testy: {', '.join(wynik['oslabione_testy']) or 'brak'}")
    print(f"  Historia: commity {h['commity_main']}, scalenia {len(h['scalenia'])}, rewerty {h['rewerty']}, "
          f"gałęzie task/* {len(h['galezie_task'])}, worktree {h['worktree_pozostale']}, "
          f"zmiany niezacommitowane: {'tak' if h['zmiany_niezacommitowane'] else 'nie'}")
    if wynik['rundy_w_todo']:
        print('  Wzmianki o rundach w TODO.md (sprawdź --rundy):')
        for linia in wynik['rundy_w_todo'][:10]:
            print(f'    {linia}')
    if not args.bez_zapisu:
        args.wyniki.mkdir(parents=True, exist_ok=True)
        cel = args.wyniki / f"{wynik['data']}-{args.konfiguracja}-{args.przebieg}.json"
        cel.write_text(json.dumps(wynik, ensure_ascii=False, indent=1) + '\n', encoding='utf-8')
        print(f'Zapisano: {cel}')
    return 0


if __name__ == '__main__':
    sys.exit(main())
