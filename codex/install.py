#!/usr/bin/env python3
"""Install the orchestration skills without replacing existing project files."""

import argparse
import filecmp
from pathlib import Path
import shutil
import subprocess


def identical(source: Path, target: Path) -> bool:
    source_files = {p.relative_to(source) for p in source.rglob('*') if p.is_file()}
    target_files = {p.relative_to(target) for p in target.rglob('*') if p.is_file()}
    if source_files != target_files or any(p.is_symlink() for p in target.rglob('*')):
        return False
    return all(filecmp.cmp(source / p, target / p, shallow=False) for p in source_files)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--project', type=Path, required=True, help='Existing project Git root')
    args = parser.parse_args()
    project = args.project.resolve()
    if not project.is_dir():
        parser.error('Katalog projektu nie istnieje.')
    result = subprocess.run(
        ['git', '-C', str(project), 'rev-parse', '--show-toplevel'],
        capture_output=True, text=True, check=False,
    )
    if result.returncode or Path(result.stdout.strip()).resolve() != project:
        parser.error('--project musi wskazywać katalog główny istniejącego repozytorium Git.')

    source_root = Path(__file__).resolve().parent / 'skills'
    destination = project / '.agents' / 'skills'
    for path in (project / '.agents', destination):
        if path.is_symlink() or (path.exists() and not path.is_dir()):
            parser.error(f'Nieobsługiwana ścieżka docelowa: {path}')

    pending = []
    for name in ('kierownik', 'architekt'):
        source, target = source_root / name, destination / name
        if not (source / 'SKILL.md').is_file():
            parser.error(f'Niekompletny pakiet: {source}')
        if target.is_symlink() or (target.exists() and not target.is_dir()):
            parser.error(f'Kolizja ścieżki: {target}')
        if target.exists():
            if not identical(source, target):
                parser.error(f'Istniejący skill różni się od pakietu; zachowano pliki: {target}')
        else:
            pending.append((source, target))

    destination.mkdir(parents=True, exist_ok=True)
    for source, target in pending:
        shutil.copytree(source, target)
        print(f'Zainstalowano: {target}')
    if not pending:
        print('Oba skills są już zainstalowane w identycznej wersji; bez zmian.')
    print('Otwórz nową sesję Codex w tym projekcie i wywołaj $kierownik.')


if __name__ == '__main__':
    main()
