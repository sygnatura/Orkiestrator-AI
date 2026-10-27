#!/usr/bin/env python3
"""Run one kierownik role in a fresh Codex CLI session without interpreting a shell prompt."""

import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import tomllib

ROLES = ('kier-analityk', 'kier-wykonawca', 'kier-recenzent', 'kier-architekt')


def git(cwd: Path, *args: str) -> bytes:
    return subprocess.check_output(['git', '-C', str(cwd), *args], stderr=subprocess.PIPE)


def snapshot(cwd: Path) -> tuple[bytes, bytes, bytes]:
    root = Path(os.fsdecode(git(cwd, 'rev-parse', '--show-toplevel')).strip())
    content = hashlib.sha256(git(cwd, 'diff', 'HEAD', '--binary') +
                             git(cwd, 'diff', '--cached', '--binary'))
    for name in git(root, 'ls-files', '--others', '--exclude-standard', '-z').split(b'\0'):
        if not name:
            continue
        path = root / os.fsdecode(name)
        data = os.fsencode(os.readlink(path)) if path.is_symlink() else path.read_bytes()
        content.update(name + b'\0' + hashlib.sha256(data).digest())
    return (
        git(cwd, 'rev-parse', 'HEAD'),
        git(cwd, 'status', '--porcelain=v1', '-z'),
        content.digest(),
    )


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
    after = snapshot(cwd) if before is not None else None
    if before is not None and before != after:
        print('ODRZUCONO: rola odczytu/recenzji zmieniła HEAD, źródła, indeks lub status.',
              file=sys.stderr)
        return process.returncode if process.returncode else 3
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
