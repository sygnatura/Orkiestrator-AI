#!/usr/bin/env python3
"""Run one kierownik role in a fresh Codex CLI session without interpreting a shell prompt."""

import argparse
from fnmatch import fnmatch
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import tomllib

ROLES = ('kier-analityk', 'kier-wykonawca', 'kier-recenzent', 'kier-architekt')
# Tool-owned caches a review may leave behind; any other new unignored file is a change. Same as CACHE in kier.py.
CACHE = ('node_modules', '.venv', 'venv', '__pycache__', '*.pyc', '.pytest_cache', '.mypy_cache', '.ruff_cache', '.tox',
         '.coverage', '.coverage.*')


def regenerable(path: str) -> bool:
    return any(fnmatch(part, pattern) for part in path.split('/') for pattern in CACHE)


def git(cwd: Path, *args: str) -> bytes:
    return subprocess.check_output(['git', '-C', str(cwd), *args], stderr=subprocess.PIPE)


def snapshot(cwd: Path) -> tuple[tuple[bytes, bytes, bytes], dict[bytes, bytes]]:
    """HEAD, tracked state and pre-existing untracked files; new untracked files (test caches) don't count."""
    root = Path(os.fsdecode(git(cwd, 'rev-parse', '--show-toplevel')).strip())
    content = hashlib.sha256(git(cwd, 'diff', 'HEAD', '--binary') +
                             git(cwd, 'diff', '--cached', '--binary'))
    untracked = {}
    for name in git(root, 'ls-files', '--others', '--exclude-standard', '-z').split(b'\0'):
        if not name:
            continue
        path = root / os.fsdecode(name)
        data = os.fsencode(os.readlink(path)) if path.is_symlink() else path.read_bytes()
        untracked[name] = hashlib.sha256(data).digest()
    tracked = (
        git(cwd, 'rev-parse', 'HEAD'),
        git(cwd, 'status', '--porcelain=v1', '-z', '--untracked-files=no'),
        content.digest(),
    )
    return tracked, untracked


def changed(before, after) -> tuple[bool, list[str]]:
    """Return (sources changed, new recreatable paths). Pre-existing untracked files must stay as they were, and a
    new file counts as a change unless it is recreatable output (test caches, builds)."""
    (tracked_before, untracked_before), (tracked_after, untracked_after) = before, after
    new = sorted(os.fsdecode(name) for name in untracked_after.keys() - untracked_before.keys())
    altered = tracked_before != tracked_after or any(
        untracked_after.get(name) != digest for name, digest in untracked_before.items()) or not all(
        regenerable(path) for path in new)
    return altered, new


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--role', choices=ROLES, required=True)
    parser.add_argument('--cwd', type=Path, required=True)
    parser.add_argument('--prompt', type=Path, required=True)
    parser.add_argument('--result', type=Path, required=True)
    parser.add_argument('--model', help='Verified available model; otherwise inherit role/session')
    parser.add_argument('--effort', choices=('none', 'minimal', 'low', 'medium', 'high', 'xhigh'))
    parser.add_argument('--codex', default='codex', help='Codex executable path')
    args = parser.parse_args(argv)
    cwd, prompt, result = args.cwd.resolve(), args.prompt.resolve(), args.result.resolve()
    stderr_path = result.with_name(result.name + '.err')
    if not cwd.is_dir() or not prompt.is_file():
        parser.error('Katalog roli lub plik zlecenia nie istnieje.')
    if result.exists() or stderr_path.exists():
        parser.error('Plik wyniku lub stderr już istnieje; użyj nowego numeru rundy.')
    if result == prompt or stderr_path == prompt:
        parser.error('Wynik nie może zastępować zlecenia.')

    role_file = Path(__file__).resolve().parents[1] / 'roles' / (args.role + '.toml')
    role = tomllib.loads(role_file.read_text(encoding='utf-8'))
    command = [args.codex, '--ask-for-approval', 'never', 'exec', '-C', str(cwd),
               '-s', role['sandbox_mode'], '-o', str(result)]
    model = args.model or role.get('model')
    effort = args.effort or role.get('model_reasoning_effort')
    if model:
        command.extend(['-m', model])
    if effort:
        command.extend(['-c', 'model_reasoning_effort=' + json.dumps(effort)])
    command.extend(['-c', 'developer_instructions=' + json.dumps(role['developer_instructions'],
                                                               ensure_ascii=False), '-'])
    order = prompt.read_text(encoding='utf-8')
    before = snapshot(cwd) if args.role in ('kier-analityk', 'kier-recenzent') else None
    result.parent.mkdir(parents=True, exist_ok=True)
    with stderr_path.open('x', encoding='utf-8') as error_log:
        process = subprocess.run(command, input=order, text=True, stdout=subprocess.DEVNULL, stderr=error_log, check=False)
    if before is not None:
        altered, new = changed(before, snapshot(cwd))
        if altered:
            added = [path for path in new if not regenerable(path)]
            print('ODRZUCONO: rola odczytu/recenzji zmieniła HEAD, źródła, indeks, status'
                  + (' albo dodała pliki: ' + ', '.join(added[:5]) if added else '') + '.', file=sys.stderr)
            return process.returncode if process.returncode else 3
        if new:
            shown = sorted({path.split('/')[0] for path in new})
            print('UWAGA: nowe pliki odtwarzalne (dozwolone): ' + ', '.join(shown[:5])
                  + (' …' if len(shown) > 5 else ''), file=sys.stderr)
    if process.returncode:
        return process.returncode
    if not result.is_file() or not result.read_text(encoding='utf-8').strip():
        print('Brak niepustego raportu CLI; exit 0 nie jest potwierdzeniem wykonania.', file=sys.stderr)
        return 4
    print(f'Zakończono {args.role}; raport: {result}; stderr: {stderr_path}')
    return 0


if __name__ == '__main__':
    try:
        raise SystemExit(main())
    except (OSError, subprocess.CalledProcessError, tomllib.TOMLDecodeError) as error:
        print(f'Nie udało się wykonać roli: {error}', file=sys.stderr)
        raise SystemExit(2)
