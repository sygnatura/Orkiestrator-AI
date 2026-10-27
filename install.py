#!/usr/bin/env python3
"""Instaluje i aktualizuje kierownika dla Claude Code i Codex (Python 3.11+).

Claude Code: ~/.claude/skills/kierownik/ i ~/.claude/agents/kier-*.md. Pliki niezmienione ręcznie są
podmieniane, zmienione ręcznie trafiają najpierw do kopii zapasowej, a pliki usunięte z pakietu znikają
(także z kopią). ZESPOL.md w katalogu skilla to stan maszyny i źródło migracji rejestru: nigdy nie jest
nadpisywany ani usuwany. Codex: codex/install.py --user --register-agents --upgrade (własne kopie
zapasowe w ~/.agents/backups/). Pozostałości starszych wersji (skill `architekt` z pierwszego portu
Codex) są usuwane z kopią. Uruchom z --dry-run, żeby zobaczyć plan bez zmian.
"""

import argparse
from dataclasses import dataclass
from datetime import datetime
import hashlib
import importlib.util
import json
from pathlib import Path
import shutil
import sys
from unittest.mock import patch

REPO = Path(__file__).resolve().parent
CLAUDE_SKILL_SRC = REPO / 'claude' / 'kierownik'
CLAUDE_AGENTS_SRC = REPO / 'claude' / 'agents'
CODEX_INSTALLER = REPO / 'codex' / 'install.py'
HISTORY = REPO / 'install-history.json'
MANIFEST = '.kierownik-install.json'
# Machine state kept in the skill directory by v10/v11; the lead migrates it into ~/.kierownik/ZESPOL.md.
PRESERVE = {'skill/ZESPOL.md'}
LEGACY_PREFIX = 'legacy-architekt/'


@dataclass
class Action:
    kind: str          # nowy | aktualizacja | zmieniony | usun | usun-zmieniony | usun-katalog
    target: Path
    source: Path | None = None
    note: str = ''

    @property
    def risky(self) -> bool:
        return self.kind in ('zmieniony', 'usun-zmieniony')


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_history() -> dict[str, set[str]]:
    data = json.loads(HISTORY.read_text(encoding='utf-8'))
    return {key: set(values) for key, values in data['pliki'].items()}


def packaged(path: Path) -> bool:
    return path.is_file() and '__pycache__' not in path.parts and path.suffix != '.pyc'


def package_files() -> dict[str, Path]:
    managed: dict[str, Path] = {}
    for src in sorted(CLAUDE_SKILL_SRC.rglob('*')):
        if packaged(src):
            managed['skill/' + src.relative_to(CLAUDE_SKILL_SRC).as_posix()] = src
    for src in sorted(CLAUDE_AGENTS_SRC.glob('*.md')):
        managed['agents/' + src.name] = src
    return managed


def record_release() -> int:
    """Maintainer step before a release: add the current package files to install-history.json."""
    data = json.loads(HISTORY.read_text(encoding='utf-8'))
    for key, src in package_files().items():
        values = set(data['pliki'].get(key, []))
        values.add(sha(src))
        data['pliki'][key] = sorted(values)
    data['pliki'] = dict(sorted(data['pliki'].items()))
    HISTORY.write_text(json.dumps(data, indent=1, ensure_ascii=False) + '\n', encoding='utf-8')
    print(f'Zapisano sumy bieżącej wersji w {HISTORY.name}.')
    return 0


def frontmatter(path: Path) -> list[str]:
    lines = path.read_text(encoding='utf-8').splitlines()
    return [line for line in lines[:12] if line.startswith(('model:', 'effort:', 'tools:'))]


def claude_targets(home: Path) -> tuple[Path, Path]:
    return home / '.claude' / 'skills' / 'kierownik', home / '.claude' / 'agents'


def target_for(key: str, skill_dir: Path, agents_dir: Path) -> Path:
    area, name = key.split('/', 1)
    return (skill_dir if area == 'skill' else agents_dir) / name


def plan_claude(home: Path, history: dict[str, set[str]]) -> tuple[list[Action], dict[str, str]]:
    skill_dir, agents_dir = claude_targets(home)
    manifest_path = skill_dir / MANIFEST
    manifest = json.loads(manifest_path.read_text(encoding='utf-8')) if manifest_path.is_file() else {}
    managed = package_files()
    actions = []
    for key, src in managed.items():
        dst = target_for(key, skill_dir, agents_dir)
        if dst.is_symlink():
            raise ValueError(f'Dowiązanie w miejscu docelowym: {dst}')
        if not dst.exists():
            actions.append(Action('nowy', dst, src))
        elif sha(dst) == sha(src):
            continue
        elif sha(dst) in history.get(key, set()) or manifest.get(key) == sha(dst):
            actions.append(Action('aktualizacja', dst, src))
        else:
            note = ''
            if key.startswith('agents/'):
                old, new = frontmatter(dst), frontmatter(src)
                if old != new:
                    note = f'Twoje ustawienia: {"; ".join(old)} → nowe: {"; ".join(new)}'
            actions.append(Action('zmieniony', dst, src, note))

    known_keys = {k for k in history if not k.startswith(LEGACY_PREFIX)} | set(manifest)
    for key in sorted(known_keys - set(managed) - PRESERVE):
        dst = target_for(key, skill_dir, agents_dir)
        if dst.is_file() and not dst.is_symlink():
            ours = sha(dst) in history.get(key, set()) or manifest.get(key) == sha(dst)
            actions.append(Action('usun' if ours else 'usun-zmieniony', dst, note='plik usunięty z pakietu'))
    return actions, {key: sha(src) for key, src in managed.items()}


def plan_legacy(home: Path, projects: list[Path], history: dict[str, set[str]]) -> list[Action]:
    actions = []
    for root in [home, *projects]:
        legacy = root / '.agents' / 'skills' / 'architekt'
        if not legacy.is_dir() or legacy.is_symlink():
            continue
        files = [p for p in legacy.rglob('*') if p.is_file()]
        ours = all(sha(p) in history.get(LEGACY_PREFIX + p.relative_to(legacy).as_posix(), set()) for p in files)
        note = 'skill z pierwszego portu Codex; v10+ używa roli kier-architekt'
        actions.append(Action('usun-katalog' if ours else 'usun-zmieniony', legacy, note=note))
    return actions


def describe(action: Action, home: Path) -> str:
    labels = {'nowy': 'nowy plik', 'aktualizacja': 'aktualizacja', 'zmieniony': 'aktualizacja PLIKU ZMIENIONEGO RĘCZNIE',
              'usun': 'usunięcie', 'usun-zmieniony': 'usunięcie ZMIENIONEGO RĘCZNIE', 'usun-katalog': 'usunięcie katalogu'}
    try:
        shown = '~/' + action.target.relative_to(home).as_posix()
    except ValueError:
        shown = str(action.target)
    line = f'  {labels[action.kind]:42} {shown}'
    return line + (f'\n      {action.note}' if action.note else '')


def backup(path: Path, home: Path, backup_root: Path) -> None:
    try:
        relative = path.relative_to(home)
    except ValueError:
        relative = Path('projekty') / path.relative_to(path.anchor)
    destination = backup_root / relative
    destination.parent.mkdir(parents=True, exist_ok=True)
    if path.is_dir():
        shutil.copytree(path, destination, dirs_exist_ok=True)
    else:
        shutil.copy2(path, destination)


def apply(actions: list[Action], home: Path, manifest: dict[str, str] | None) -> Path | None:
    backup_root = None
    for action in actions:
        if action.target.exists() and action.kind != 'nowy':
            if backup_root is None:
                backup_root = home / '.kierownik' / 'backups' / datetime.now().strftime('%Y%m%d-%H%M%S')
            backup(action.target, home, backup_root)
        if action.kind in ('nowy', 'aktualizacja', 'zmieniony'):
            action.target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(action.source, action.target)
        elif action.target.is_dir():
            shutil.rmtree(action.target)
        else:
            action.target.unlink()
            prune_empty(action.target.parent, home)
    if manifest is not None:
        skill_dir, _ = claude_targets(home)
        skill_dir.mkdir(parents=True, exist_ok=True)
        (skill_dir / MANIFEST).write_text(json.dumps(manifest, indent=1, sort_keys=True) + '\n', encoding='utf-8')
    return backup_root


def prune_empty(directory: Path, home: Path) -> None:
    """Remove directories emptied by a deletion (e.g. a dropped scripts/), never the skill or agents directory."""
    stops = set(claude_targets(home))
    while directory not in stops and directory.is_relative_to(claude_targets(home)[0]) and directory.is_dir() \
            and not any(directory.iterdir()):
        directory.rmdir()
        directory = directory.parent


def verify(home: Path) -> list[str]:
    """After installing: every package file is in place byte for byte."""
    skill_dir, agents_dir = claude_targets(home)
    wrong = []
    for key, src in package_files().items():
        dst = target_for(key, skill_dir, agents_dir)
        if not dst.is_file() or sha(dst) != sha(src):
            wrong.append(key)
    return wrong


def run_codex(home: Path, projects: list[Path]) -> None:
    spec = importlib.util.spec_from_file_location('kierownik_codex_install', CODEX_INSTALLER)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    runs = [['--user', '--register-agents', '--upgrade']]
    for project in projects:
        if (project / '.agents' / 'skills' / 'kierownik').is_dir():
            runs.append(['--project', str(project), '--register-agents', '--upgrade'])
    with patch.object(Path, 'home', return_value=home):
        for arguments in runs:
            print('Codex:', ' '.join(arguments))
            module.main(arguments)


def detect(home: Path, folder: str, command: str) -> bool:
    return (home / folder).is_dir() or shutil.which(command) is not None


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('--claude', action='store_true', help='Zainstaluj tylko wersję Claude Code')
    parser.add_argument('--codex', action='store_true', help='Zainstaluj tylko wersję Codex')
    parser.add_argument('--project', type=Path, action='append', default=[],
                        help='Projekt do sprawdzenia (projektowa instalacja Codex, stary skill architekt); można powtórzyć')
    parser.add_argument('--dry-run', action='store_true', help='Pokaż plan, niczego nie zmieniaj')
    parser.add_argument('--yes', action='store_true', help='Nie pytaj o zgodę na podmianę plików zmienionych ręcznie')
    parser.add_argument('--home', type=Path, default=None, help=argparse.SUPPRESS)
    parser.add_argument('--record-release', action='store_true',
                        help='Dla utrzymującego pakiet: dopisz sumy bieżących plików do install-history.json')
    args = parser.parse_args(argv)
    if args.record_release:
        return record_release()
    if sys.version_info < (3, 11):
        parser.error('Wymagany Python 3.11 lub nowszy.')
    home = (args.home or Path.home()).resolve()
    projects = [p.resolve() for p in args.project]
    do_claude = args.claude or (not args.codex and detect(home, '.claude', 'claude'))
    do_codex = args.codex or (not args.claude and detect(home, '.codex', 'codex'))
    if not (do_claude or do_codex):
        parser.error('Nie wykryto Claude Code ani Codex. Wskaż --claude i/lub --codex.')

    history = load_history()
    actions, manifest = plan_claude(home, history) if do_claude else ([], None)
    actions += plan_legacy(home, projects, history)

    print('Plan instalacji kierownika:')
    print(f'  Claude Code: {"tak" if do_claude else "pominięte"}; Codex: {"tak" if do_codex else "pominięte"}')
    for action in actions:
        print(describe(action, home))
    if do_claude and not actions:
        print('  Claude Code: wszystkie pliki aktualne.')
    if do_codex:
        print('  Codex: codex/install.py --user --register-agents --upgrade'
              + (' oraz projektowe instalacje z --project' if projects else ''))
    print('  Bez zmian: ZESPOL.md w katalogu skilla, rejestr ~/.kierownik/ZESPOL.md, inne pliki w ~/.claude/agents/.')
    if args.dry_run:
        print('Tryb --dry-run: nic nie zmieniono.')
        return 0

    risky = [a for a in actions if a.risky]
    if risky and not args.yes:
        if not sys.stdin.isatty():
            print('Są pliki zmienione ręcznie (wyżej). Uruchom ponownie z --yes, żeby je podmienić z kopią zapasową.')
            return 1
        if input('Podmienić/usunąć pliki zmienione ręcznie (kopia zapasowa zostanie zrobiona)? [t/N] ').strip().lower() not in ('t', 'tak', 'y', 'yes'):
            print('Przerwano; nic nie zmieniono.')
            return 1

    backup_root = apply(actions, home, manifest)
    if backup_root:
        print(f'Kopia zapasowa poprzednich plików: {backup_root}')
    if do_claude:
        wrong = verify(home)
        if wrong:
            print('Instalacja niepełna — pliki niezgodne z pakietem: ' + ', '.join(wrong), file=sys.stderr)
            return 2
        print(f'Sprawdzono: {len(package_files())} plików Claude Code zgodnych z pakietem.')
    if do_codex:
        try:
            run_codex(home, projects)
        except ValueError as error:
            print(f'Codex: {error}', file=sys.stderr)
            return 2
    changed = [a for a in actions if a.kind == 'zmieniony' and a.note]
    if changed:
        print('Zmieniałeś ustawienia agentów (wyżej). Model i effort wybiera kierownik z rejestru przy każdym '
              'zleceniu, więc zwykle nie trzeba ich przywracać. Od v13 wykonawca domyślnie pracuje na opus.')
    print('Gotowe. W projekcie uruchom /kierownik (Claude Code) albo $kierownik (Codex). Przy pierwszym starcie '
          'kierownik przeniesie stary ZESPOL.md do rejestru ~/.kierownik/ZESPOL.md i zapyta raz o zgodę na agy '
          'bez sandboxa. Aktualizacja w przyszłości: to samo polecenie (Windows: py install.py).')
    return 0


if __name__ == '__main__':
    try:
        raise SystemExit(main())
    except (OSError, ValueError) as error:
        print(f'Instalacja przerwana: {error}', file=sys.stderr)
        raise SystemExit(2)
