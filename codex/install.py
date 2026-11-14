#!/usr/bin/env python3
"""Install/update the Codex kierownik skill; preserve machine state and existing configuration."""

import argparse
import json
from pathlib import Path
import shutil
import subprocess
import tempfile
import sys

if sys.version_info < (3, 11):  # tomllib; komunikat zamiast ModuleNotFoundError
    sys.exit('Kierownik dla Codex wymaga Pythona 3.11 lub nowszego (jest '
             + '.'.join(map(str, sys.version_info[:3])) + ').')

import tomllib  # noqa: E402

ROLES = ('kier-analityk', 'kier-wykonawca', 'kier-recenzent', 'kier-architekt')
DESCRIPTIONS = (
    'Odczyt i krótkie analizy projektu; bez zmian.',
    'Implementacja jednego zadania w katalogu wskazanym przez kierownika.',
    'Świeża niezależna recenzja kryteriów, diffu i działania; bez naprawiania.',
    'Plan, recenzja planu, specyfikacje i diagnozy; bez implementacji.',
)


def packaged(path: Path) -> bool:
    return path.is_file() and '__pycache__' not in path.parts and path.suffix != '.pyc'


def content(path: Path) -> bytes:
    """File bytes with CRLF normalised, so a Windows checkout is not mistaken for a changed skill."""
    data = path.read_bytes()
    return data.replace(b'\r\n', b'\n') if path.suffix in ('.md', '.py', '.toml', '.yaml', '.json') else data


def identical(source: Path, target: Path) -> bool:
    left = {p.relative_to(source): content(p) for p in source.rglob('*') if packaged(p)}
    right = {p.relative_to(target): content(p) for p in target.rglob('*') if packaged(p)}
    # ZESPOL is user-maintained machine state; never replace it on reinstall.
    left.pop(Path('ZESPOL.md'), None)
    right.pop(Path('ZESPOL.md'), None)
    return left == right


def config_addition(path: Path, skill: Path) -> str:
    original = path.read_text(encoding='utf-8') if path.exists() else ''
    config = tomllib.loads(original)
    agents = config.get('agents', {})
    if not isinstance(agents, dict):
        raise ValueError('Istniejąca konfiguracja agents nie jest tabelą TOML.')
    blocks = []
    for role, description in zip(ROLES, DESCRIPTIONS):
        role_path = (skill / 'roles' / (role + '.toml')).as_posix()
        existing = agents.get(role)
        if existing is not None:
            if not isinstance(existing, dict) or existing.get('config_file') != role_path:
                raise ValueError(f'Kolizja istniejącej konfiguracji roli {role}; zachowano config.toml.')
            continue
        blocks.append(f'[agents.{role}]\ndescription = {json.dumps(description, ensure_ascii=False)}\n'
                      f'config_file = {json.dumps(role_path, ensure_ascii=False)}\n')
    if not blocks:
        return original
    result = original.rstrip('\n') + '\n\n# Kierownik Codex — role\n' + '\n'.join(blocks)
    tomllib.loads(result)
    return result


def reject_symlink(path: Path) -> None:
    if path.is_symlink():
        raise ValueError(f'Dowiązanie w ścieżce docelowej: {path}')


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    location = parser.add_mutually_exclusive_group(required=True)
    location.add_argument('--project', type=Path, help='Existing project Git root')
    location.add_argument('--user', action='store_true', help='Install once in ~/.agents/skills')
    parser.add_argument('--register-agents', action='store_true', help='Add native roles to config.toml')
    parser.add_argument('--upgrade', action='store_true', help='Back up existing skill, retain ZESPOL, update')
    args = parser.parse_args(argv)
    source = Path(__file__).resolve().parent / 'skills' / 'kierownik'

    if args.project:
        root = args.project.resolve()
        result = subprocess.run(['git', '-C', str(root), 'rev-parse', '--show-toplevel'],
                                capture_output=True, text=True, check=False)
        if result.returncode or Path(result.stdout.strip()).resolve() != root:
            raise ValueError('--project musi wskazywać główny katalog istniejącego repozytorium Git.')
    else:
        root = Path.home()
    agents_root, config_root = root / '.agents', root / '.codex'
    skills = agents_root / 'skills'
    target = skills / 'kierownik'
    config_path = config_root / 'config.toml'
    for path in (agents_root, skills, target):
        reject_symlink(path)
        if path.exists() and not path.is_dir():
            raise ValueError(f'Kolizja z plikiem: {path}')
    if target.exists() and any(p.is_symlink() for p in target.rglob('*')):
        raise ValueError('Istniejący skill zawiera dowiązania; zachowano instalację.')
    if args.register_agents:
        reject_symlink(config_root)
        reject_symlink(config_path)
        if config_root.exists() and not config_root.is_dir():
            raise ValueError('Katalog .codex jest zajęty przez plik.')
        new_config = config_addition(config_path, target)
    else:
        new_config = None
    same = target.exists() and identical(source, target)
    if target.exists() and not same and not args.upgrade:
        raise ValueError('Istniejący skill różni się; do aktualizacji z kopią zapasową użyj --upgrade.')

    if not same:
        agents_root.mkdir(parents=True, exist_ok=True)
        with tempfile.TemporaryDirectory(prefix='kierownik-stage-', dir=agents_root) as stage_root:
            staged = Path(stage_root) / 'kierownik'
            shutil.copytree(source, staged, ignore=shutil.ignore_patterns('__pycache__', '*.pyc'))
            if target.exists() and (target / 'ZESPOL.md').is_file():
                shutil.copy2(target / 'ZESPOL.md', staged / 'ZESPOL.md')
            backup = None
            if target.exists():
                backup_root = agents_root / 'backups'
                reject_symlink(backup_root)
                backup_root.mkdir(exist_ok=True)
                archive = Path(tempfile.mkdtemp(prefix='kierownik-', dir=backup_root))
                backup = archive / 'kierownik'
                target.rename(backup)
            try:
                skills.mkdir(parents=True, exist_ok=True)
                staged.rename(target)
            except OSError:
                if backup is not None:
                    backup.rename(target)
                raise
            print(f'Zainstalowano: {target}')
            if backup is not None:
                print(f'Zachowano poprzedni skill i zmiany użytkownika: {backup}')
    else:
        print('Skill już zainstalowany; ZESPOL i pliki bez zmian.')

    if new_config is not None:
        old = config_path.read_text(encoding='utf-8') if config_path.exists() else None
        if new_config != old:
            config_root.mkdir(parents=True, exist_ok=True)
            with tempfile.NamedTemporaryFile(mode='w', encoding='utf-8', dir=config_root,
                                             prefix='kierownik-config-', delete=False) as output:
                output.write(new_config)
                temporary = Path(output.name)
            try:
                if config_path.exists():
                    temporary.chmod(config_path.stat().st_mode & 0o777)
                temporary.replace(config_path)
            finally:
                temporary.unlink(missing_ok=True)
            print(f'Dodano brakujące role bez zastępowania ustawień: {config_path}')
    print('Otwórz nową sesję Codex w projekcie i wywołaj $kierownik.')
    return 0


if __name__ == '__main__':
    try:
        raise SystemExit(main())
    except (OSError, ValueError) as error:
        print(f'Instalacja przerwana: {error}')
        raise SystemExit(2)
