#!/usr/bin/env python3
"""Tworzy świeżą kopię projektu testowego evala poza tym repozytorium: repozytorium Git z jednym commitem
na `main` i opcjonalnie gołym remote obok (`<katalog>.remote.git`), żeby `kier.py merge --push` działało.
Ukryte testy (`evals/ukryte*/`) i wzorzec (`evals/wzorzec*/`) nigdy nie trafiają do kopii. `--zestaw 2`
kopiuje `evals/projekt2/` zamiast `evals/projekt/`."""

import argparse
from pathlib import Path
import shutil
import subprocess
import sys

EVALS = Path(__file__).resolve().parent
REPO = EVALS.parent


def git(*args: str, cwd: Path) -> str:
    return subprocess.run(['git', '-C', str(cwd), *args], check=True, capture_output=True, text=True,
                          encoding='utf-8').stdout.strip()


def przygotuj(katalog: Path, remote: bool, numer: int = 1) -> Path:
    katalog = katalog.resolve()
    if katalog == REPO or REPO in katalog.parents:
        raise SystemExit(f'Kopia musi być poza repozytorium {REPO} — inaczej agenci zobaczą ukryte testy.')
    if katalog.exists() and any(katalog.iterdir()):
        raise SystemExit(f'Katalog {katalog} istnieje i nie jest pusty — podaj nowy.')
    shutil.copytree(EVALS / ('projekt' if numer == 1 else f'projekt{numer}'), katalog, dirs_exist_ok=True, ignore=shutil.ignore_patterns('__pycache__', '*.pyc'))
    git('init', '-q', '-b', 'main', cwd=katalog)
    if subprocess.run(['git', '-C', str(katalog), 'config', 'user.name'], capture_output=True).returncode:
        git('config', 'user.name', 'Eval', cwd=katalog)
        git('config', 'user.email', 'eval@example.invalid', cwd=katalog)
    git('add', '.', cwd=katalog)
    git('commit', '-q', '-m', 'init: projekt testowy evala (stan wyjściowy)', cwd=katalog)
    if remote:
        gola = katalog.with_name(katalog.name + '.remote.git')
        subprocess.run(['git', 'init', '-q', '--bare', '-b', 'main', str(gola)], check=True)
        git('remote', 'add', 'origin', str(gola), cwd=katalog)
        git('push', '-q', '-u', 'origin', 'main', cwd=katalog)
        git('remote', 'set-head', 'origin', 'main', cwd=katalog)
    return katalog


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('katalog', type=Path, help='nowy katalog kopii, poza tym repozytorium')
    parser.add_argument('--remote', action='store_true', help='utwórz goły remote obok kopii')
    parser.add_argument('--zestaw', type=int, default=1, choices=(1, 2), help='zestaw zadań (1 albo 2)')
    args = parser.parse_args(argv)
    katalog = przygotuj(args.katalog, args.remote, args.zestaw)
    print(f'Gotowe: {katalog} (main @ {git("rev-parse", "--short", "HEAD", cwd=katalog)}).')
    print('Dalej: otwórz Claude Code w tym katalogu i uruchom konfigurację z evals/README.md, a po etapie:')
    print(f'  python3 {EVALS / "ocen.py"} {katalog} --zestaw {args.zestaw} --konfiguracja <A|B|C|D> --przebieg <N>')
    return 0


if __name__ == '__main__':
    sys.exit(main())
