#!/usr/bin/env python3
"""Git and test mechanics of the kierownik lead (Claude Code and Codex hosts; stdlib only, Python 3.11+).

The lead calls one subcommand per step and reads only the short `KLUCZ: wartość` lines; every git call is
logged to <repo>/.kierownik/log/kier.log. The script never forces, deletes unmerged work or rewrites pushed
history: what it refuses, the lead decides by hand.

Test commands come only from the `- Testy:` / `- Lint:` lines of AGENTS.md as committed on main, never from the
command line, so a blanket permission for this script doesn't allow arbitrary commands.

Exit codes: 0 OK | 1 tests red or untrustworthy (merge undone) | 2 usage/internal error | 3 refused, nothing changed |
4 conflict, aborted | 5 merged and green, but push failed | 6 merged and pushed, cleanup incomplete |
`test`: the command's own exit code.
"""

import argparse
from datetime import datetime
from fnmatch import fnmatch
import os
from pathlib import Path
import platform
import re
import shutil
import subprocess
import sys

EXCLUDES = ('.kierownik/', '.claude/worktrees/')
# Files a test run or an install may leave behind and that can be recreated; anything else untracked is work.
# Keep identical to REGENERABLE in codex/skills/kierownik/scripts/run_agent.py (tests/test_spojnosc.py checks it).
REGENERABLE = ('node_modules', '.venv', 'venv', '__pycache__', '*.pyc', '.pytest_cache', '.mypy_cache', '.ruff_cache',
               '.tox', 'coverage', '.coverage', '.coverage.*', 'htmlcov', 'dist', 'build', 'target', '.next', '*.log')
NAME = re.compile(r'[A-Za-z0-9][A-Za-z0-9._-]*')
REPO: Path = Path.cwd()
MAIN: str | None = None


class Stop(Exception):
    def __init__(self, code: int, result: str, message: str = ''):
        super().__init__(message)
        self.code, self.result, self.message = code, result, message


def out(key: str, value) -> None:
    print(f'{key}: {value}')


def log(text: str) -> None:
    try:
        path = REPO / '.kierownik' / 'log' / 'kier.log'
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open('a', encoding='utf-8') as handle:
            handle.write(text.rstrip('\n') + '\n')
    except OSError:
        pass


def git(*args: str, cwd: Path | None = None, check: bool = True) -> subprocess.CompletedProcess:
    cwd = cwd or REPO
    process = subprocess.run(['git', '-C', str(cwd), *args], capture_output=True, text=True,
                             encoding='utf-8', errors='replace')
    log(f'{datetime.now():%Y-%m-%d %H:%M:%S} [{cwd}] git {" ".join(args)} -> {process.returncode}\n'
        + (process.stdout[-2000:] + process.stderr[-2000:]).strip())
    if check and process.returncode:
        raise Stop(2, 'BŁĄD', f'git {" ".join(args)}: {process.stderr.strip() or process.stdout.strip()}')
    return process


def text(*args: str, cwd: Path | None = None) -> str:
    return git(*args, cwd=cwd).stdout.strip()


def ok(*args: str, cwd: Path | None = None) -> bool:
    return git(*args, cwd=cwd, check=False).returncode == 0


def find_repo(start: Path) -> Path:
    common = subprocess.run(['git', '-C', str(start), 'rev-parse', '--path-format=absolute', '--git-common-dir'],
                            capture_output=True, text=True)
    if common.returncode:
        raise Stop(2, 'BŁĄD', f'{start} nie jest repozytorium Git')
    path = Path(common.stdout.strip())
    return path.parent if path.name == '.git' else path


def branch_exists(name: str) -> bool:
    return bool(name) and ok('rev-parse', '--verify', '--quiet', f'refs/heads/{name}')


def main_branch() -> str:
    if MAIN:
        if not branch_exists(MAIN):
            raise Stop(3, 'ODMOWA', f'gałąź główna {MAIN} (z --main) nie istnieje')
        return MAIN
    head = git('symbolic-ref', '--short', 'refs/remotes/origin/HEAD', check=False)
    if head.returncode == 0 and head.stdout.strip():
        return head.stdout.strip().removeprefix('origin/')
    configured = git('config', 'init.defaultBranch', check=False).stdout.strip()
    for name in ('main', 'master', configured):
        if branch_exists(name):
            return name
    raise Stop(3, 'ODMOWA', 'nie ustalono gałęzi głównej (brak origin/HEAD, main, master) — podaj --main <gałąź> '
               'i zapisz ją w TODO.md („Ustalenia”)')


def regenerable(entry: str, root: Path) -> bool:
    """A `git status` path (a directory ends with /) that only holds recreatable output."""
    parts = entry.rstrip('/').split('/')
    if any(fnmatch(part, pattern) for part in parts for pattern in REGENERABLE):
        return True
    example = root / '.env.example'
    return entry == '.env' and example.is_file() and (root / '.env').read_bytes() == example.read_bytes()


def leftovers(cwd: Path) -> list[str]:
    """Untracked or ignored entries that are someone's work, not recreatable output."""
    lines = git('status', '--porcelain=v1', '--ignored', cwd=cwd).stdout.splitlines()
    entries = [line[3:].strip('"') for line in lines if line[:2] in ('??', '!!')]
    return [entry for entry in entries if not regenerable(entry, cwd)]


def remove_worktree(path: Path) -> bool:
    """`git worktree remove` without --force; untracked recreatable output (which Git refuses on) goes first."""
    for line in git('status', '--porcelain=v1', cwd=path).stdout.splitlines():
        entry = line[3:].strip('"')
        if line.startswith('??') and regenerable(entry, path):
            target = path / entry.rstrip('/')
            shutil.rmtree(target) if target.is_dir() and not target.is_symlink() else target.unlink()
    return ok('worktree', 'remove', str(path))


def collisions(cwd: Path, base: str, incoming: str) -> list[str]:
    """Files `incoming` adds over `base` that already exist on disk (ignored files Git would silently overwrite)."""
    added = text('diff', '--name-only', '--no-renames', '--diff-filter=A', f'{base}...{incoming}', cwd=cwd).splitlines()
    return [name for name in added if os.path.lexists(cwd / name)]


def refuse_collisions(names: list[str], where: Path) -> None:
    if names:
        for name in names[:10]:
            out('ISTNIEJE', name)
        raise Stop(3, 'ODMOWA', f'scalenie nadpisałoby pliki istniejące w {relative(where)} (zwykle ignorowane, '
                   'np. lokalna konfiguracja) — przenieś je albo zabezpiecz i powtórz')


def agents_command(key: str, ref: str) -> str:
    """The `- <key>: `command`` line of AGENTS.md as committed at `ref`."""
    shown = git('show', f'{ref}:AGENTS.md', check=False)
    found = re.search(rf'(?mi)^\s*[-*]\s*{re.escape(key)}\b[^:\n]*:\s*`([^`]+)`', shown.stdout) if not shown.returncode else None
    if not found or '<' in found.group(1):
        raise Stop(3, 'ODMOWA', f'brak polecenia „- {key}: `…`” w AGENTS.md na {ref} — uzupełnij AGENTS.md, '
                   'scommituj na main i powtórz')
    return found.group(1)


def has_remote() -> bool:
    return 'origin' in text('remote').split()


def dirty(cwd: Path, untracked: bool = True) -> list[str]:
    args = ['status', '--porcelain=v1'] + ([] if untracked else ['--untracked-files=no'])
    return [line for line in git(*args, cwd=cwd).stdout.splitlines() if line]


def worktrees() -> list[dict]:
    items, current = [], {}
    for line in text('worktree', 'list', '--porcelain').splitlines() + ['']:
        if not line:
            if current:
                items.append(current)
            current = {}
            continue
        key, _, value = line.partition(' ')
        current[key] = value or True
    for item in items:
        path = Path(item['worktree'])
        item['path'] = path
        item['branch'] = item.get('branch', '').removeprefix('refs/heads/') if isinstance(item.get('branch'), str) else ''
        if path == REPO:
            item['typ'] = 'główny'
        elif path.parent == REPO / '.claude' / 'worktrees':
            item['typ'] = 'claude'
        elif path.parent == REPO / '.kierownik' / 'wt':
            item['typ'] = 'cli'
        else:
            item['typ'] = 'inny'
    return items


def task_branch(task: str, required: bool = True) -> str | None:
    names = [n for n in text('for-each-ref', '--format=%(refname:short)', f'refs/heads/task/{task}',
                             f'refs/heads/task/{task}-*').splitlines() if n]
    if len(names) == 1:
        return names[0]
    if not names and not required:
        return None
    raise Stop(3, 'ODMOWA', f'gałąź zadania {task}: ' + (', '.join(names) if names else 'brak'))


def ensure_exclude() -> list[str]:
    """Keep the lead's own directories (logs, CLI worktrees, Claude worktrees) out of `git status`."""
    exclude = Path(text('rev-parse', '--path-format=absolute', '--git-path', 'info/exclude'))
    content = exclude.read_text(encoding='utf-8') if exclude.is_file() else ''
    missing = [line for line in EXCLUDES if line not in content.splitlines()]
    if missing:
        exclude.parent.mkdir(parents=True, exist_ok=True)
        with exclude.open('a', encoding='utf-8') as handle:
            handle.write(('\n' if content and not content.endswith('\n') else '') + ''.join(f'{m}\n' for m in missing))
    return missing


def relative(path: Path) -> str:
    try:
        return path.relative_to(REPO).as_posix()
    except ValueError:
        return str(path)


# ---------------------------------------------------------------- test runs

COUNT_PATTERNS = (
    ('pytest', re.compile(r'^=+ .*\bin [\d.]+s.*=+$', re.M)),
    ('unittest', re.compile(r'^Ran (\d+) tests? in', re.M)),
    ('jest', re.compile(r'^Tests:\s+(.+)$', re.M)),
    ('cargo', re.compile(r'test result: \w+\. (\d+) passed; (\d+) failed; (\d+) ignored')),
)


def count_tests(output: str) -> str:
    def number(word: str, line: str) -> int:
        found = re.search(rf'(\d+) {word}', line)
        return int(found.group(1)) if found else 0

    lines = COUNT_PATTERNS[0][1].findall(output)
    if lines:
        line = lines[-1]
        return (f'passed={number("passed", line)} failed={number("failed", line) + number("errors?", line)} '
                f'skipped={number("skipped", line)}')
    ran = COUNT_PATTERNS[1][1].findall(output)
    if ran:
        tail = output[output.rfind('Ran '):]
        failed = sum(int(n) for n in re.findall(r'(?:failures|errors)=(\d+)', tail))
        skipped = sum(int(n) for n in re.findall(r'skipped=(\d+)', tail))
        return f'passed={int(ran[-1]) - failed - skipped} failed={failed} skipped={skipped}'
    jest = COUNT_PATTERNS[2][1].findall(output)
    if jest:
        line = jest[-1]
        return f'passed={number("passed", line)} failed={number("failed", line)} skipped={number("skipped", line)}'
    cargo = COUNT_PATTERNS[3][1].findall(output)
    if cargo:
        return 'passed={} failed={} skipped={}'.format(*(sum(int(c[i]) for c in cargo) for i in range(3)))
    go_ok, go_fail = len(re.findall(r'^ok\s', output, re.M)), len(re.findall(r'^(?:FAIL|--- FAIL)', output, re.M))
    if go_ok or go_fail:
        return f'pakiety ok={go_ok} fail={go_fail}'
    return 'nierozpoznane'


def run_test(name: str, command: str, cwd: Path, tail: int) -> int:
    log_path = REPO / '.kierownik' / 'log' / f'{name}.log'
    log_path.parent.mkdir(parents=True, exist_ok=True)
    with log_path.open('w', encoding='utf-8', errors='replace') as handle:
        code = subprocess.run(command, shell=True, cwd=cwd, stdout=handle, stderr=subprocess.STDOUT).returncode
    output = log_path.read_text(encoding='utf-8', errors='replace')
    counts = count_tests(output)
    out('TEST', f'{command} (katalog: {relative(cwd)})')
    out('LOG', relative(log_path))
    out('exit', code)
    out('LICZBY', counts)
    if re.search(r'passed=0 failed=0', counts):
        out('UWAGA', 'zero testów — wynik niczego nie dowodzi')
    print('--- koniec logu ---')
    print('\n'.join(output.splitlines()[-tail:]))
    print('---')
    return code


# ---------------------------------------------------------------- subcommands

def cmd_env(args) -> int:
    main = main_branch()
    current = text('branch', '--show-current')
    out('SYSTEM', f'{platform.system()} {platform.release()}; Python {platform.python_version()}')
    out('REPO', REPO)
    out('MAIN', main)
    out('GAŁĄŹ', current or '(odłączony HEAD)')
    changes = dirty(REPO)
    out('ZMIANY', len(changes))
    remote = has_remote()
    out('REMOTE', 'origin' if remote else 'brak (bez push)')
    if remote and not args.no_fetch:
        if not ok('fetch', '--quiet', 'origin'):
            out('FETCH', 'nieudany — stan zdalny nieznany')
        elif ok('rev-parse', '--verify', '--quiet', f'refs/remotes/origin/{main}'):
            ahead, behind = map(int, text('rev-list', '--left-right', '--count', f'{main}...origin/{main}').split())
            if ahead and behind:
                out('ROZBIEŻNOŚĆ', f'main +{ahead}/-{behind} wobec origin/{main} — sprawdź `git log --oneline '
                    f'{main}...origin/{main}`')
            elif behind and current == main and not dirty(REPO, untracked=False):
                git('merge', '--ff-only', f'origin/{main}')
                out('FAST-FORWARD', f'{behind} commitów, main @ {text("rev-parse", "--short", "HEAD")}')
            elif behind:
                out('W TYLE', f'{behind} commitów (bez fast-forward: nie na main albo zmiany lokalne)')
            elif ahead:
                out('NIEWYPCHNIĘTE', f'{ahead} commitów')
    out('HEAD', text('log', '--oneline', '-1'))
    trees = worktrees()
    for tree in trees:
        if tree['typ'] == 'główny':
            continue
        state = 'brak katalogu' if not tree['path'].is_dir() else (
            'zmiany' if dirty(tree['path']) else 'czysty')
        out('WORKTREE', f'{tree["typ"]} {relative(tree["path"])} '
            f'{tree["branch"] or "odłączony @ " + tree.get("HEAD", "")[:9]} ({state})')
    merged = set(text('branch', '--merged', main, '--format=%(refname:short)').splitlines())
    for name in text('for-each-ref', '--format=%(refname:short)', 'refs/heads/task/').splitlines():
        out('ZADANIE', f'{name} ({"scalona" if name in merged else "niescalona"})')
    claude_dirs = {tree['path'].name for tree in trees if tree['typ'] == 'claude'}
    for name in text('for-each-ref', '--format=%(refname:short)', 'refs/heads/worktree-*').splitlines():
        if name.removeprefix('worktree-') not in claude_dirs:
            removed = ok('branch', '-d', name)
            out('SIEROTA', f'{name} — {"usunięta" if removed else "zostawiona (niescalona)"}')
    return 0


def prepare_detached(path: Path, ref: str) -> None:
    sha = text('rev-parse', '--verify', ref + '^{commit}')
    if path.exists():
        if dirty(path, untracked=False):
            raise Stop(3, 'ODMOWA', f'{relative(path)} ma zmiany w plikach śledzonych')
        git('checkout', '--quiet', '--detach', sha, cwd=path)
    else:
        git('worktree', 'add', '--detach', str(path), sha)
    out('KATALOG', path)
    out('SHA', sha)


def cmd_worktree(args) -> int:
    base_dir = REPO / '.kierownik' / 'wt'
    if args.ro:
        prepare_detached(base_dir / f'{args.ro}-ro', args.at or main_branch())
        return 0
    if args.rec:
        branch = task_branch(args.task)
        prepare_detached(base_dir / f'{args.task}-rec', branch)
        out('GAŁĄŹ', branch)
        return 0
    path = base_dir / args.task
    existing = task_branch(args.task, required=False)
    branch = existing or f'task/{args.task}-{args.nazwa}' if args.nazwa else existing
    if not branch:
        raise Stop(2, 'BŁĄD', 'podaj nazwę zadania (nowa gałąź task/T-NNN-nazwa)')
    if path.exists():
        current = text('branch', '--show-current', cwd=path)
        if current != branch:
            raise Stop(3, 'ODMOWA', f'{relative(path)} jest na {current or "odłączonym HEAD"}, nie na {branch}')
    elif existing:
        git('worktree', 'add', str(path), branch)
    else:
        git('worktree', 'add', '-b', branch, str(path), args.base or main_branch())
    out('KATALOG', path)
    out('GAŁĄŹ', branch)
    out('SHA', text('rev-parse', 'HEAD', cwd=path))
    return 0


def cmd_ro_check(args) -> int:
    path = Path(args.katalog).resolve()
    head, expected = text('rev-parse', 'HEAD', cwd=path), text('rev-parse', '--verify', args.sha + '^{commit}')
    changes = dirty(path, untracked=False)
    new = [line[3:].strip('"') for line in dirty(path) if line.startswith('??')]
    added = [name for name in new if not regenerable(name, path)]
    if len(new) > len(added):
        out('UWAGA', 'nowe pliki odtwarzalne (dozwolone): ' + ', '.join(sorted(set(new) - set(added))[:5]))
    if head != expected or changes or added:
        out('HEAD', f'{head[:9]} (oczekiwany {expected[:9]})')
        for line in changes[:10]:
            out('ZMIANA', line)
        for name in added[:10]:
            out('NOWY PLIK', name)
        raise Stop(3, 'ODMOWA', 'rola odczytu/recenzji zmieniła HEAD, pliki śledzone albo dodała pliki — odrzuć '
                   'jej wynik')
    return 0


def legacy_revert(main: str, task: str, branch: str) -> str | None:
    """A previous merge of THIS task (subject `merge(T-NNN)`) reverted on main and not restored yet → the revert."""
    earlier = []
    for line in text('log', '--first-parent', '--merges', '--format=%H %P%x09%s', main).splitlines():
        shas, _, subject = line.partition('\t')
        parents = shas.split()
        if (len(parents) > 2 and subject.startswith(f'merge({task})')
                and ok('merge-base', '--is-ancestor', parents[2], branch)):
            earlier.append(parents[0])
    if not earlier:
        return None
    bodies = text('log', main, '--format=%H %b%x00').split('\0')
    reverts = {}
    for entry in bodies:
        entry = entry.strip()
        if entry:
            sha, _, body = entry.partition(' ')
            for target in re.findall(r'This reverts commit ([0-9a-f]{40})', body):
                reverts[target] = sha
    for merge in earlier:
        revert = reverts.get(merge)
        if revert and revert not in reverts:
            return revert
    return None


def undo(before: str, task: str) -> None:
    """Undo this run's own, unpushed commits on main; changes the tests made to tracked files go to a stash."""
    if dirty(REPO, untracked=False):
        git('stash', 'push', '-m', f'kier: zmiany testów {task}')
        out('STASH', text('stash', 'list', '-1') + ' (zmiany zrobione przez testy w plikach śledzonych)')
    if not ok('reset', '--keep', before):
        merged = text('rev-parse', '--short', 'HEAD')
        raise Stop(2, 'BŁĄD', f'main zostaje na {merged} (ze scaleniem, bez push) — nie udało się cofnąć do '
                   f'{before[:9]}; sprawdź `git status` i cofnij ręcznie')


def cmd_merge(args) -> int:
    main = main_branch()
    if text('branch', '--show-current') != main:
        raise Stop(3, 'ODMOWA', f'główny katalog nie jest na {main}')
    changes = dirty(REPO)
    if changes:
        raise Stop(3, 'ODMOWA', f'{main} ma niezacommitowane zmiany ({len(changes)}) — najpierw commit')
    branch = task_branch(args.task)
    before = text('rev-parse', 'HEAD')
    command = agents_command('Testy', before)
    refuse_collisions(collisions(REPO, before, branch), REPO)
    revert = legacy_revert(main, args.task, branch)
    if revert:
        refuse_collisions([n for n in text('diff', '--name-only', '--no-renames', '--diff-filter=D',
                                            f'{revert}^', revert).splitlines() if os.path.lexists(REPO / n)], REPO)
        restore = git('revert', '--no-edit', revert, check=False)
        if restore.returncode:
            git('revert', '--abort', check=False)
            raise Stop(4, 'KONFLIKT', f'przywrócenie wcześniejszego rewertu {revert[:9]} daje konflikt')
        out('COFNIĘTO REWERT', f'{revert[:9]} (inaczej poprzednie zmiany gałęzi by nie wróciły)')
    message = f'merge({args.task}): {args.opis or branch}'
    if git('merge', '--no-ff', '-m', message, branch, check=False).returncode:
        files = text('diff', '--name-only', '--diff-filter=U').splitlines()
        git('merge', '--abort', check=False)
        if revert:
            undo(before, args.task)
        for name in files:
            out('KONFLIKT', name)
        out('DALEJ', f'kier.py sync {args.task}')
        raise Stop(4, 'KONFLIKT', f'{main} bez zmian')
    merge_sha = text('rev-parse', 'HEAD')
    out('MERGE', f'{merge_sha[:9]} {message}')
    code = run_test(f'{args.task}-main', command, REPO, args.tail)
    touched = dirty(REPO, untracked=False)
    if code or touched:
        undo(before, args.task)
        out('COFNIĘTO', f'{main} @ {before[:9]} (bez push — gałąź {branch} zostaje)')
        reason = ('testy zmieniły pliki śledzone — wynik niewiarygodny' if touched else
                  'testy czerwone') + '; zadanie wraca do W TOKU z obserwacjami z logu'
        raise Stop(1, 'CZERWONE', reason)
    if args.push and has_remote():
        if not ok('push', 'origin', main):
            raise Stop(5, 'BŁĄD', f'scalone i zielone, ale `git push origin {main}` się nie udał')
        out('PUSH', f'origin {main}')
    elif args.push:
        out('PUSH', 'pominięty — brak remote')
    if not args.no_cleanup:
        try:
            return cleanup(args.task, branch)
        except Stop as stop:
            if stop.code == 3:
                raise Stop(6, 'SPRZĄTANIE NIEPEŁNE', 'scalone i wypchnięte; ' + stop.message) from None
            raise
    return 0


def cleanup(task: str, branch: str | None) -> int:
    refused = False
    rec = REPO / '.kierownik' / 'wt' / f'{task}-rec'
    for tree in worktrees():
        if tree['typ'] == 'główny' or not (tree['branch'] == branch and branch or tree['path'] == rec):
            continue
        work = leftovers(tree['path']) if tree['path'].is_dir() else []
        if work:
            refused = True
            out('ZOSTAWIONO', f'{relative(tree["path"])} — pliki poza commitami, które nie są odtwarzalne:')
            for entry in work[:10]:
                print('   ' + entry)
            continue
        if dirty(tree['path'], untracked=False) or not remove_worktree(tree['path']):
            refused = True
            out('ZOSTAWIONO', f'{relative(tree["path"])} — pliki poza commitami:')
            for line in dirty(tree['path'])[:10]:
                print('   ' + line)
        else:
            out('USUNIĘTO', relative(tree['path']))
        if tree['typ'] == 'claude':
            helper = f'worktree-{tree["path"].name}'
            if ok('rev-parse', '--verify', '--quiet', f'refs/heads/{helper}') and ok('branch', '-d', helper):
                out('USUNIĘTO', helper)
    if branch and not refused:
        if ok('branch', '-d', branch):
            out('USUNIĘTO', branch)
        else:
            refused = True
            out('ZOSTAWIONO', f'{branch} — niescalona z bieżącą gałęzią')
    git('worktree', 'prune', check=False)
    if refused:
        raise Stop(3, 'ODMOWA', 'część sprzątania odmówiona — sprawdź wyżej; --force tylko po wykluczeniu zapomnianej pracy')
    return 0


def cmd_cleanup(args) -> int:
    return cleanup(args.task, task_branch(args.task, required=False))


def cmd_fix_round(args) -> int:
    branch = task_branch(args.task)
    for tree in worktrees():
        if tree['branch'] != branch:
            continue
        if tree['typ'] == 'cli':
            out('KATALOG', f'{tree["path"]} (wykonawca CLI pracuje dalej w tym samym katalogu)')
            continue
        if tree['typ'] != 'claude':
            raise Stop(3, 'ODMOWA', f'{branch} jest wyewidencjonowana w {tree["path"]}')
        changes = dirty(tree['path'], untracked=False) + leftovers(tree['path'])
        if changes:
            raise Stop(3, 'ODMOWA', f'{relative(tree["path"])} ma niezapisaną pracę ({len(changes)} zmian) — '
                       'zabezpiecz ją commitem na gałęzi zadania')
        if not remove_worktree(tree['path']):
            raise Stop(3, 'ODMOWA', f'git nie usunął {relative(tree["path"])} — sprawdź `git -C <katalog> status`')
        out('USUNIĘTO', relative(tree['path']))
        helper = f'worktree-{tree["path"].name}'
        if ok('rev-parse', '--verify', '--quiet', f'refs/heads/{helper}') and ok('branch', '-d', helper):
            out('USUNIĘTO', helper)
    sha = text('rev-parse', '--short', branch)
    out('GAŁĄŹ', f'{branch} (istnieje, @ {sha}) — przełącz się na nią, nie twórz nowej')
    return 0


def cmd_sync(args) -> int:
    main, branch = main_branch(), task_branch(args.task)
    path = next((t['path'] for t in worktrees() if t['branch'] == branch), None)
    if path is None:
        path = REPO / '.kierownik' / 'wt' / args.task
        git('worktree', 'add', str(path), branch)
    if dirty(path, untracked=False):
        raise Stop(3, 'ODMOWA', f'{relative(path)} ma niezacommitowane zmiany')
    refuse_collisions(collisions(path, branch, main), path)
    out('KATALOG', path)
    merge = git('merge', '--no-ff', '-m', f'merge({args.task}): {main} do gałęzi zadania', main, cwd=path, check=False)
    if merge.returncode:
        files = text('diff', '--name-only', '--diff-filter=U', cwd=path).splitlines()
        for name in files:
            out('KONFLIKT', name)
        if args.keep_conflict:
            out('DALEJ', f'rozwiąż w {path}, `git add` + `git commit`, potem testy i `kier.py merge {args.task}`')
            raise Stop(4, 'KONFLIKT', 'konflikt zostawiony do rozwiązania')
        git('merge', '--abort', cwd=path, check=False)
        out('DALEJ', 'trywialny → `sync --keep-conflict`; inaczej `fix-round` i zlecenie A z linią KONFLIKT')
        raise Stop(4, 'KONFLIKT', 'przerwano, gałąź bez zmian')
    sha = text('rev-parse', 'HEAD', cwd=path)
    remerge = git('show', '--remerge-diff', '--format=', 'HEAD', cwd=path, check=False)
    size = 'n/d' if remerge.returncode else f'{len(remerge.stdout.splitlines())} linii'
    out('SHA', sha)
    out('ROZWIĄZANIE', f'git -C {path} show --remerge-diff HEAD ({size}; 0 = bez ręcznych zmian)')
    return 0


def cmd_test(args) -> int:
    command = agents_command(args.klucz, main_branch())
    return run_test(args.name, command, Path(args.cwd).resolve() if args.cwd else REPO, args.tail)


def name(value: str) -> str:
    if not NAME.fullmatch(value) or '..' in value:
        raise argparse.ArgumentTypeError(f'niedozwolona nazwa: {value!r} (litery, cyfry, . _ -)')
    return value


def parser() -> argparse.ArgumentParser:
    root = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    root.add_argument('--repo', type=Path, help='katalog repozytorium (domyślnie: główny worktree bieżącego)')
    root.add_argument('--main', type=name, help='gałąź główna, gdy nie wynika z origin/HEAD ani main/master')
    sub = root.add_subparsers(dest='cmd', required=True)
    env = sub.add_parser('env', help='fakty startu sesji, fetch/fast-forward, worktree, gałęzie zadań, exclude')
    env.add_argument('--no-fetch', action='store_true')
    env.set_defaults(func=cmd_env)
    tree = sub.add_parser('worktree', help='katalog CLI w .kierownik/wt/: wykonawca, --rec, --ro')
    tree.add_argument('task', nargs='?', type=name)
    tree.add_argument('nazwa', nargs='?', type=name)
    tree.add_argument('--base')
    tree.add_argument('--rec', action='store_true', help='odłączony katalog recenzenta T-NNN-rec')
    tree.add_argument('--ro', metavar='ID', type=name, help='odłączony katalog odczytu <ID>-ro')
    tree.add_argument('--at', help='commit dla --ro (domyślnie main)')
    tree.set_defaults(func=cmd_worktree)
    check = sub.add_parser('ro-check', help='czy rola odczytu/recenzji niczego nie zmieniła')
    check.add_argument('katalog')
    check.add_argument('--sha', required=True)
    check.set_defaults(func=cmd_ro_check)
    merge = sub.add_parser('merge', help='scalenie --no-ff, testy z AGENTS.md na main, push, sprzątanie')
    merge.add_argument('task', type=name)
    merge.add_argument('--push', action='store_true')
    merge.add_argument('--opis')
    merge.add_argument('--no-cleanup', action='store_true')
    merge.add_argument('--tail', type=int, default=30)
    merge.set_defaults(func=cmd_merge)
    clean = sub.add_parser('cleanup', help='usuń worktree i gałęzie scalonego zadania (bez --force)')
    clean.add_argument('task', type=name)
    clean.set_defaults(func=cmd_cleanup)
    fix = sub.add_parser('fix-round', help='przygotuj rundę poprawek i podaj linię GAŁĄŹ')
    fix.add_argument('task', type=name)
    fix.set_defaults(func=cmd_fix_round)
    sync = sub.add_parser('sync', help='scal main do gałęzi zadania (po konflikcie)')
    sync.add_argument('task', type=name)
    sync.add_argument('--keep-conflict', action='store_true')
    sync.set_defaults(func=cmd_sync)
    test = sub.add_parser('test', help='polecenie z AGENTS.md na main (Testy albo Lint) z logiem i liczbami')
    test.add_argument('--name', required=True, type=name)
    test.add_argument('--klucz', default='Testy', choices=('Testy', 'Lint'))
    test.add_argument('--cwd')
    test.add_argument('--tail', type=int, default=30)
    test.set_defaults(func=cmd_test)
    return root


def main(argv=None) -> int:
    global REPO, MAIN
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, 'reconfigure'):
            stream.reconfigure(encoding='utf-8', errors='replace')
    args = parser().parse_args(argv)
    if args.cmd == 'worktree' and not args.ro and not args.task:
        parser().error('worktree: podaj T-NNN (albo --ro ID)')
    try:
        REPO, MAIN = find_repo((args.repo or Path.cwd()).resolve()), args.main
        added = ensure_exclude()
        if added:
            out('EXCLUDE', 'dopisano ' + ', '.join(added))
        code = args.func(args)
    except Stop as stop:
        if stop.message:
            out('POWÓD', stop.message)
        out('WYNIK', stop.result)
        return stop.code
    if args.cmd != 'test':
        out('WYNIK', 'OK')
    return code


if __name__ == '__main__':
    raise SystemExit(main())
