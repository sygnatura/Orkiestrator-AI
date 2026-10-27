#!/usr/bin/env python3
"""Git and test mechanics of the kierownik lead (Claude Code and Codex hosts; stdlib only, Python 3.11+).

The lead calls one subcommand per step and reads only the short `KLUCZ: wartość` lines; every git call is
logged to <repo>/.kierownik/log/kier.log. The script never forces, deletes unmerged work or rewrites pushed
history: what it refuses, the lead decides by hand.

Exit codes: 0 OK | 1 tests red (merge undone) | 2 usage/internal error | 3 refused, nothing changed |
4 conflict, aborted | 5 merged and green, but push failed | `test`: the command's own exit code.
"""

import argparse
from datetime import datetime
import os
from pathlib import Path
import platform
import re
import subprocess
import sys

EXCLUDES = ('.kierownik/', '.claude/worktrees/')
REPO: Path = Path.cwd()


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


def main_branch() -> str:
    head = git('symbolic-ref', '--short', 'refs/remotes/origin/HEAD', check=False)
    if head.returncode == 0 and head.stdout.strip():
        return head.stdout.strip().removeprefix('origin/')
    for name in ('main', 'master'):
        if ok('rev-parse', '--verify', '--quiet', f'refs/heads/{name}'):
            return name
    return text('branch', '--show-current') or 'main'


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
    existing = exclude.read_text(encoding='utf-8').splitlines() if exclude.is_file() else []
    missing = [line for line in EXCLUDES if line not in existing]
    if missing:
        exclude.parent.mkdir(parents=True, exist_ok=True)
        with exclude.open('a', encoding='utf-8') as handle:
            handle.write(''.join(line + '\n' for line in missing))
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


def run_test(name: str, command: list[str], cwd: Path, tail: int) -> int:
    log_path = REPO / '.kierownik' / 'log' / f'{name}.log'
    log_path.parent.mkdir(parents=True, exist_ok=True)
    shell = len(command) == 1
    with log_path.open('w', encoding='utf-8', errors='replace') as handle:
        code = subprocess.run(command[0] if shell else command, shell=shell, cwd=cwd, stdout=handle,
                              stderr=subprocess.STDOUT).returncode
    output = log_path.read_text(encoding='utf-8', errors='replace')
    counts = count_tests(output)
    out('TEST', f'{" ".join(command)} (katalog: {relative(cwd)})')
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
    new = [line[3:] for line in dirty(path) if line.startswith('??')]
    if new:
        shown = sorted({name.split('/')[0] for name in new})
        out('UWAGA', 'nowe nieśledzone (dozwolone): ' + ', '.join(shown[:5]) + (' …' if len(shown) > 5 else ''))
    if head != expected or changes:
        out('HEAD', f'{head[:9]} (oczekiwany {expected[:9]})')
        for line in changes[:10]:
            out('ZMIANA', line)
        raise Stop(3, 'ODMOWA', 'rola odczytu/recenzji zmieniła HEAD albo pliki śledzone — odrzuć jej wynik')
    return 0


def legacy_revert(main: str, branch: str) -> str | None:
    """A previous merge of this branch reverted on main and not restored yet → that revert's sha."""
    merges = [line.split() for line in text('rev-list', '--merges', '--first-parent', '--parents', main).splitlines()]
    earlier = [m[0] for m in merges if len(m) > 2 and ok('merge-base', '--is-ancestor', m[2], branch)]
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


def undo(before: str) -> None:
    if not ok('reset', '--keep', before):
        raise Stop(3, 'ODMOWA', f'nie udało się bezpiecznie cofnąć do {before[:9]} — main ma zmiany po testach; '
                   'sprawdź `git status` i cofnij scalenie ręcznie (`git revert -m 1`)')


def cmd_merge(args) -> int:
    main = main_branch()
    if text('branch', '--show-current') != main:
        raise Stop(3, 'ODMOWA', f'główny katalog nie jest na {main}')
    changes = dirty(REPO)
    if changes:
        raise Stop(3, 'ODMOWA', f'{main} ma niezacommitowane zmiany ({len(changes)}) — najpierw commit')
    branch = task_branch(args.task)
    before = text('rev-parse', 'HEAD')
    revert = legacy_revert(main, branch)
    if revert:
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
            undo(before)
        for name in files:
            out('KONFLIKT', name)
        out('DALEJ', f'kier.py sync {args.task}')
        raise Stop(4, 'KONFLIKT', f'{main} bez zmian')
    merge_sha = text('rev-parse', 'HEAD')
    out('MERGE', f'{merge_sha[:9]} {message}')
    if args.test:
        code = run_test(f'{args.task}-main', [args.test], REPO, args.tail)
        if code:
            undo(before)
            out('COFNIĘTO', f'{main} @ {before[:9]} (scalenie i testy czerwone — gałąź {branch} zostaje)')
            raise Stop(1, 'CZERWONE', 'zadanie wraca do W TOKU z obserwacjami z logu')
    else:
        out('UWAGA', 'bez --test: scalenie niezweryfikowane testami na main')
    if args.push and has_remote():
        if not ok('push', 'origin', main):
            raise Stop(5, 'BŁĄD', f'scalone i zielone, ale `git push origin {main}` się nie udał')
        out('PUSH', f'origin {main}')
    elif args.push:
        out('PUSH', 'pominięty — brak remote')
    if not args.no_cleanup:
        return cleanup(args.task, branch)
    return 0


def cleanup(task: str, branch: str | None) -> int:
    refused = False
    rec = REPO / '.kierownik' / 'wt' / f'{task}-rec'
    for tree in worktrees():
        if tree['typ'] == 'główny' or not (tree['branch'] == branch and branch or tree['path'] == rec):
            continue
        if git('worktree', 'remove', str(tree['path']), check=False).returncode:
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
        changes = dirty(tree['path'])
        if changes:
            raise Stop(3, 'ODMOWA', f'{relative(tree["path"])} ma niezapisaną pracę ({len(changes)} zmian) — '
                       'zabezpiecz ją commitem na gałęzi zadania')
        git('worktree', 'remove', str(tree['path']))
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
    command = [c for c in args.polecenie if c != '--'] if args.polecenie else []
    if not command:
        raise Stop(2, 'BŁĄD', 'podaj polecenie po `--`')
    return run_test(args.name, command, Path(args.cwd).resolve() if args.cwd else REPO, args.tail)


def parser() -> argparse.ArgumentParser:
    root = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    root.add_argument('--repo', type=Path, help='katalog repozytorium (domyślnie: główny worktree bieżącego)')
    sub = root.add_subparsers(dest='cmd', required=True)
    env = sub.add_parser('env', help='fakty startu sesji, fetch/fast-forward, worktree, gałęzie zadań, exclude')
    env.add_argument('--no-fetch', action='store_true')
    env.set_defaults(func=cmd_env)
    tree = sub.add_parser('worktree', help='katalog CLI w .kierownik/wt/: wykonawca, --rec, --ro')
    tree.add_argument('task', nargs='?')
    tree.add_argument('nazwa', nargs='?')
    tree.add_argument('--base')
    tree.add_argument('--rec', action='store_true', help='odłączony katalog recenzenta T-NNN-rec')
    tree.add_argument('--ro', metavar='ID', help='odłączony katalog odczytu <ID>-ro')
    tree.add_argument('--at', help='commit dla --ro (domyślnie main)')
    tree.set_defaults(func=cmd_worktree)
    check = sub.add_parser('ro-check', help='czy rola odczytu/recenzji niczego nie zmieniła')
    check.add_argument('katalog')
    check.add_argument('--sha', required=True)
    check.set_defaults(func=cmd_ro_check)
    merge = sub.add_parser('merge', help='scalenie --no-ff, testy na main, push, sprzątanie')
    merge.add_argument('task')
    merge.add_argument('--test', help='polecenie testów z AGENTS.md')
    merge.add_argument('--push', action='store_true')
    merge.add_argument('--opis')
    merge.add_argument('--no-cleanup', action='store_true')
    merge.add_argument('--tail', type=int, default=30)
    merge.set_defaults(func=cmd_merge)
    clean = sub.add_parser('cleanup', help='usuń worktree i gałęzie scalonego zadania (bez --force)')
    clean.add_argument('task')
    clean.set_defaults(func=cmd_cleanup)
    fix = sub.add_parser('fix-round', help='przygotuj rundę poprawek i podaj linię GAŁĄŹ')
    fix.add_argument('task')
    fix.set_defaults(func=cmd_fix_round)
    sync = sub.add_parser('sync', help='scal main do gałęzi zadania (po konflikcie)')
    sync.add_argument('task')
    sync.add_argument('--keep-conflict', action='store_true')
    sync.set_defaults(func=cmd_sync)
    test = sub.add_parser('test', help='uruchom testy z logiem, kodem wyjścia i liczbami')
    test.add_argument('--name', required=True)
    test.add_argument('--cwd')
    test.add_argument('--tail', type=int, default=30)
    test.add_argument('polecenie', nargs=argparse.REMAINDER)
    test.set_defaults(func=cmd_test)
    return root


def main(argv=None) -> int:
    global REPO
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, 'reconfigure'):
            stream.reconfigure(encoding='utf-8', errors='replace')
    args = parser().parse_args(argv)
    if args.cmd == 'worktree' and not args.ro and not args.task:
        parser().error('worktree: podaj T-NNN (albo --ro ID)')
    try:
        REPO = find_repo((args.repo or Path.cwd()).resolve())
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
