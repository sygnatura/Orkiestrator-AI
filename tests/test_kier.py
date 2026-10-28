"""Tests of scripts/kier.py — the lead's git and test mechanics — on temporary repositories with a bare remote."""

import sys

sys.dont_write_bytecode = True  # keep __pycache__ out of the package directory that the installers copy

from contextlib import redirect_stdout
import importlib.util
import io
from pathlib import Path
import subprocess
import tempfile
import unittest

REPO = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('kierownik_kier', REPO / 'claude/kierownik/scripts/kier.py')
kier = importlib.util.module_from_spec(spec)
spec.loader.exec_module(kier)

TEST = f'"{sys.executable}" check.py'
AGENTS = (f'# Fixture\n\n## Polecenia\n- Instalacja: `brak`\n- Testy: `{TEST}` | jeden test: `brak`\n'
          f'- Lint / format / typy: `"{sys.executable}" -c "print(42)"`\n')


class Fixture(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix='kier-')
        self.addCleanup(self.temp.cleanup)
        root = Path(self.temp.name).resolve()
        self.remote = root / 'remote.git'
        subprocess.run(['git', 'init', '-q', '--bare', '-b', 'main', str(self.remote)], check=True)
        self.repo = root / 'repo'
        self.repo.mkdir()
        self.git('init', '-q', '-b', 'main')
        self.git('config', 'user.name', 'Fixture')
        self.git('config', 'user.email', 'fixture@example.invalid')
        (self.repo / 'f.txt').write_text('a\nb\nc\n')
        (self.repo / 'check.py').write_text('import sys\nsys.exit(1 if "BAD" in open("f.txt").read() else 0)\n')
        (self.repo / 'AGENTS.md').write_text(AGENTS)
        (self.repo / '.gitignore').write_text('local.py\nprivate/\nprivate\nzażółć.py\ndist/\n', encoding='utf-8')
        self.git('add', '.')
        self.git('commit', '-qm', 'init')
        self.git('remote', 'add', 'origin', str(self.remote))
        self.git('push', '-q', '-u', 'origin', 'main')
        self.git('remote', 'set-head', 'origin', 'main')

    def git(self, *args, cwd=None):
        return subprocess.run(['git', '-C', str(cwd or self.repo), *args], check=True, capture_output=True,
                              text=True, encoding='utf-8').stdout.strip()

    def kier(self, *args):
        with redirect_stdout(io.StringIO()) as output:
            code = kier.main(['--repo', str(self.repo), *args])
        return code, output.getvalue()

    def task(self, task, name, old, new):
        code, output = self.kier('worktree', task, name)
        self.assertEqual(code, 0, output)
        path = self.repo / '.kierownik/wt' / task
        text = (path / 'f.txt').read_text().replace(old, new)
        (path / 'f.txt').write_text(text)
        self.git('commit', '-qam', f'feat({task}): {name}', cwd=path)
        return path

class KierTest(Fixture):
    def test_env_adds_excludes_and_removes_orphan_helper_branch(self):
        self.git('branch', 'worktree-gone')
        code, output = self.kier('env')
        self.assertEqual(code, 0, output)
        exclude = (self.repo / '.git/info/exclude').read_text()
        self.assertIn('.kierownik/', exclude)
        self.assertIn('.claude/worktrees/', exclude)
        self.assertIn('SIEROTA: worktree-gone — usunięta', output)
        self.assertNotIn('worktree-gone', self.git('branch'))

    def test_green_merge_pushes_and_cleans_up(self):
        self.task('T-001', 'alfa', 'a\n', 'A\n')
        code, output = self.kier('merge', 'T-001', '--push')
        self.assertEqual(code, 0, output)
        self.assertIn('WYNIK: OK', output)
        self.assertEqual(self.git('rev-parse', 'main'), self.git('rev-parse', 'origin/main'))
        self.assertNotIn('task/T-001', self.git('branch'))
        self.assertFalse((self.repo / '.kierownik/wt/T-001').exists())
        self.assertEqual(self.git('status', '--porcelain'), '')

    def test_conflict_aborts_and_leaves_main_unchanged(self):
        self.task('T-001', 'alfa', 'a\n', 'A1\n')
        self.task('T-002', 'beta', 'a\n', 'A2\n')
        self.assertEqual(self.kier('merge', 'T-001')[0], 0)
        before = self.git('rev-parse', 'HEAD')
        code, output = self.kier('merge', 'T-002')
        self.assertEqual(code, 4, output)
        self.assertIn('KONFLIKT: f.txt', output)
        self.assertEqual(self.git('rev-parse', 'HEAD'), before)
        self.assertEqual(self.git('status', '--porcelain'), '')
        code, output = self.kier('sync', 'T-002')
        self.assertEqual(code, 4, output)
        self.assertEqual(self.git('status', '--porcelain', cwd=self.repo / '.kierownik/wt/T-002'), '')

    def test_red_tests_undo_the_merge_and_keep_the_branch(self):
        self.task('T-003', 'zle', 'c\n', 'BAD\n')
        before = self.git('rev-parse', 'HEAD')
        code, output = self.kier('merge', 'T-003', '--push')
        self.assertEqual(code, 1, output)
        self.assertIn('WYNIK: CZERWONE', output)
        self.assertEqual(self.git('rev-parse', 'HEAD'), before)
        self.assertIn('task/T-003-zle', self.git('branch'))
        self.assertEqual(self.git('rev-parse', 'origin/main'), before)

    def test_merge_after_legacy_revert_brings_the_change_back(self):
        path = self.task('T-004', 'stare', 'a\n', 'A\n')
        self.git('merge', '--no-ff', '-qm', 'merge(T-004)', 'task/T-004-stare')
        self.git('revert', '--no-edit', '-m', '1', 'HEAD')
        (path / 'f.txt').write_text((path / 'f.txt').read_text().replace('b\n', 'B\n'))
        self.git('commit', '-qam', 'fix(T-004)', cwd=path)
        code, output = self.kier('merge', 'T-004')
        self.assertEqual(code, 0, output)
        self.assertIn('COFNIĘTO REWERT', output)
        self.assertEqual((self.repo / 'f.txt').read_text(), 'A\nB\nc\n')

    def test_dirty_main_is_refused(self):
        self.task('T-005', 'x', 'a\n', 'A\n')
        (self.repo / 'f.txt').write_text('local\n')
        code, output = self.kier('merge', 'T-005')
        self.assertEqual(code, 3, output)
        self.assertIn('WYNIK: ODMOWA', output)

    def test_fix_round_refuses_unsaved_work_and_frees_a_clean_claude_worktree(self):
        self.git('branch', 'task/T-006-y')
        claude = self.repo / '.claude/worktrees/agent-1'
        self.git('worktree', 'add', '-q', '-b', 'worktree-agent-1', str(claude))
        self.git('switch', '-q', 'task/T-006-y', cwd=claude)
        (claude / 'nowy.py').write_text('praca\n')
        code, output = self.kier('fix-round', 'T-006')
        self.assertEqual(code, 3, output)
        self.assertTrue(claude.exists())
        (claude / 'nowy.py').unlink()
        code, output = self.kier('fix-round', 'T-006')
        self.assertEqual(code, 0, output)
        self.assertFalse(claude.exists())
        self.assertNotIn('worktree-agent-1', self.git('branch'))
        self.assertIn('GAŁĄŹ: task/T-006-y (istnieje', output)

    def test_ro_check_allows_new_caches_but_not_tracked_changes(self):
        self.task('T-007', 'r', 'a\n', 'A\n')
        code, output = self.kier('worktree', '--rec', 'T-007')
        self.assertEqual(code, 0, output)
        rec = self.repo / '.kierownik/wt/T-007-rec'
        sha = self.git('rev-parse', 'task/T-007-r')
        (rec / '.pytest_cache').mkdir()
        (rec / '.pytest_cache/lastfailed').write_text('{}')
        code, output = self.kier('ro-check', str(rec), '--sha', sha)
        self.assertEqual(code, 0, output)
        self.assertIn('UWAGA: nowe pliki odtwarzalne (dozwolone): .pytest_cache', output)
        (rec / 'f.txt').write_text('zmiana\n')
        code, output = self.kier('ro-check', str(rec), '--sha', sha)
        self.assertEqual(code, 3, output)

    def test_test_command_keeps_exit_code_and_writes_log(self):
        (self.repo / 'AGENTS.md').write_text(AGENTS.replace(TEST, f'"{sys.executable}" -c "import sys; sys.exit(7)"'))
        self.git('commit', '-qam', 'docs: test kończy się kodem 7')
        code, output = self.kier('test', '--name', 'probe')
        self.assertEqual(code, 7)
        self.assertIn('exit: 7', output)
        self.assertTrue((self.repo / '.kierownik/log/probe.log').is_file())


class ReviewFindingsTest(Fixture):
    """Regressions for the scenarios of the v13 Codex review."""

    def add_file(self, task, name, relative, content):
        code, output = self.kier('worktree', task, name)
        self.assertEqual(code, 0, output)
        path = self.repo / '.kierownik/wt' / task
        (path / relative).parent.mkdir(parents=True, exist_ok=True)
        (path / relative).write_text(content)
        self.git('add', '-f', relative, cwd=path)
        self.git('commit', '-qm', f'feat({task}): {name}', cwd=path)
        return path

    def test_merge_refuses_to_overwrite_an_ignored_local_file(self):
        (self.repo / 'local.py').write_text('właściciela\n')
        self.add_file('T-008', 'local', 'local.py', 'z gałęzi\n')
        before = self.git('rev-parse', 'HEAD')
        code, output = self.kier('merge', 'T-008')
        self.assertEqual(code, 3, output)
        self.assertIn('local.py', output)
        self.assertEqual((self.repo / 'local.py').read_text(), 'właściciela\n')
        self.assertEqual(self.git('rev-parse', 'HEAD'), before)

    def test_cleanup_keeps_ignored_work_but_not_caches(self):
        path = self.task('T-009', 'p', 'a\n', 'A\n')
        (path / 'private').mkdir()
        (path / 'private/work.py').write_text('praca\n')
        (path / '__pycache__').mkdir()
        (path / '__pycache__/x.pyc').write_bytes(b'\0')
        code, output = self.kier('merge', 'T-009')
        self.assertEqual(code, 6, output)
        self.assertIn('private', output)
        self.assertTrue((path / 'private/work.py').is_file())
        (path / 'private/work.py').unlink()
        (path / 'private').rmdir()
        code, output = self.kier('cleanup', 'T-009')
        self.assertEqual(code, 0, output)
        self.assertFalse(path.exists())

    def test_test_takes_no_arbitrary_command(self):
        (self.repo / 'f.txt').write_text('niezacommitowane\n')
        with self.assertRaises(SystemExit):
            self.kier('test', '--name', 'proof', '--', 'git reset --hard HEAD')
        self.assertEqual((self.repo / 'f.txt').read_text(), 'niezacommitowane\n')
        code, output = self.kier('test', '--name', 'z-agents')
        self.assertEqual(code, 0, output)
        self.assertIn('check.py', output)

    def test_merge_refuses_when_an_ignored_file_stands_where_the_branch_adds_a_directory(self):
        (self.repo / 'private').write_text('plik właściciela\n')
        self.add_file('T-020', 'katalog', 'private/new_source.py', 'z gałęzi\n')
        code, output = self.kier('merge', 'T-020', '--no-cleanup')
        self.assertEqual(code, 3, output)
        self.assertEqual((self.repo / 'private').read_text(), 'plik właściciela\n')

    def test_merge_refuses_to_overwrite_an_ignored_file_with_a_polish_name(self):
        (self.repo / 'zażółć.py').write_text('właściciela\n', encoding='utf-8')
        self.add_file('T-022', 'pl', 'zażółć.py', 'z gałęzi\n')
        code, output = self.kier('merge', 'T-022', '--no-cleanup')
        self.assertEqual(code, 3, output)
        self.assertEqual((self.repo / 'zażółć.py').read_text(encoding='utf-8'), 'właściciela\n')

    def test_cleanup_keeps_untracked_work_in_a_build_directory(self):
        path = self.task('T-021', 'b', 'a\n', 'A\n')
        self.assertEqual(self.kier('merge', 'T-021', '--no-cleanup')[0], 0)
        (path / 'build').mkdir()
        (path / 'build/new_source.py').write_text('praca\n')
        code, output = self.kier('cleanup', 'T-021')
        self.assertEqual(code, 3, output)
        self.assertTrue((path / 'build/new_source.py').is_file())

    def test_cleanup_removes_ignored_output_and_untracked_caches(self):
        path = self.task('T-023', 'c', 'a\n', 'A\n')
        (path / 'dist').mkdir()
        (path / 'dist/app.whl').write_text('x')
        (path / 'pkg/__pycache__').mkdir(parents=True)
        (path / 'pkg/__pycache__/m.pyc').write_bytes(b'\0')
        code, output = self.kier('merge', 'T-023')
        self.assertEqual(code, 0, output)
        self.assertFalse(path.exists())

    def test_ro_check_rejects_a_source_file_in_a_build_directory(self):
        self.task('T-024', 'r', 'a\n', 'A\n')
        self.kier('worktree', '--rec', 'T-024')
        rec = self.repo / '.kierownik/wt/T-024-rec'
        (rec / 'build').mkdir()
        (rec / 'build/new_source.py').write_text('print(1)\n')
        code, output = self.kier('ro-check', str(rec), '--sha', self.git('rev-parse', 'task/T-024-r'))
        self.assertEqual(code, 3, output)

    def test_lint_line_of_the_agents_template_is_found(self):
        code, output = self.kier('test', '--name', 'lint', '--klucz', 'Lint')
        self.assertEqual(code, 0, output)
        self.assertIn('print(42)', output)

    def test_merge_without_test_line_in_agents_is_refused(self):
        (self.repo / 'AGENTS.md').write_text('# bez poleceń\n')
        self.git('commit', '-qam', 'docs: bez testów')
        self.task('T-010', 'x', 'a\n', 'A\n')
        before = self.git('rev-parse', 'HEAD')
        code, output = self.kier('merge', 'T-010')
        self.assertEqual(code, 3, output)
        self.assertEqual(self.git('rev-parse', 'HEAD'), before)

    def test_test_command_comes_from_main_not_from_the_task_branch(self):
        path = self.task('T-011', 'zle', 'c\n', 'BAD\n')
        (path / 'AGENTS.md').write_text(AGENTS.replace(TEST, 'exit 0'))
        self.git('commit', '-qam', 'feat(T-011): podmiana testów', cwd=path)
        code, output = self.kier('merge', 'T-011')
        self.assertEqual(code, 1, output)

    def test_unrelated_task_does_not_restore_someone_elses_revert(self):
        self.task('T-001', 'alfa', 'a\n', 'A\n')
        self.assertEqual(self.kier('merge', 'T-001')[0], 0)
        self.git('revert', '--no-edit', '-m', '1', 'HEAD')
        self.add_file('T-002', 'beta', 'g.txt', 'osobny plik\n')
        code, output = self.kier('merge', 'T-002')
        self.assertEqual(code, 0, output)
        self.assertNotIn('COFNIĘTO REWERT', output)
        self.assertEqual((self.repo / 'f.txt').read_text(), 'a\nb\nc\n')

    def test_tests_that_change_tracked_files_are_not_trusted(self):
        (self.repo / 'check.py').write_text('import sys\nopen("f.txt", "w").write("naprawione\\n")\nsys.exit(0)\n')
        self.git('commit', '-qam', 'test: modyfikuje f.txt')
        self.git('push', '-q', 'origin', 'main')
        self.task('T-012', 'zle', 'c\n', 'BAD\n')
        before = self.git('rev-parse', 'HEAD')
        code, output = self.kier('merge', 'T-012', '--push')
        self.assertEqual(code, 1, output)
        self.assertIn('STASH', output)
        self.assertEqual(self.git('rev-parse', 'HEAD'), before)
        self.assertEqual(self.git('rev-parse', 'origin/main'), before)
        self.assertEqual(self.git('status', '--porcelain'), '')
        self.assertIn('kier: zmiany testów T-012', self.git('stash', 'list'))

    def test_ro_check_rejects_a_new_source_file(self):
        self.task('T-013', 'r', 'a\n', 'A\n')
        self.kier('worktree', '--rec', 'T-013')
        rec = self.repo / '.kierownik/wt/T-013-rec'
        (rec / 'new_source.py').write_text('print(1)\n')
        code, output = self.kier('ro-check', str(rec), '--sha', self.git('rev-parse', 'task/T-013-r'))
        self.assertEqual(code, 3, output)
        self.assertIn('new_source.py', output)

    def test_unknown_main_branch_is_refused_unless_given(self):
        self.git('remote', 'remove', 'origin')
        self.git('branch', '-m', 'main', 'trunk')
        self.git('switch', '-q', '-c', 'feature')
        code, output = self.kier('env', '--no-fetch')
        self.assertEqual(code, 3, output)
        self.git('config', 'init.defaultBranch', 'nieistniejaca')
        code, output = self.kier('--main', 'trunk', 'env', '--no-fetch')
        self.assertEqual(code, 0, output)
        self.assertIn('MAIN: trunk', output)

    def test_exclude_without_final_newline_keeps_existing_rule(self):
        exclude = self.repo / '.git/info/exclude'
        exclude.write_text('private.txt')
        self.assertEqual(self.kier('env', '--no-fetch')[0], 0)
        self.assertIn('private.txt\n.kierownik/\n', exclude.read_text())

    def test_task_names_cannot_escape_the_worktree_directory(self):
        with self.assertRaises(SystemExit):
            self.kier('worktree', '../../poza', 'x')


class CountTests(unittest.TestCase):
    def test_known_runner_summaries(self):
        cases = {
            '===== 3 passed, 1 failed, 2 skipped in 0.12s =====': 'passed=3 failed=1 skipped=2',
            'Ran 5 tests in 0.1s\n\nFAILED (failures=1, skipped=1)': 'passed=3 failed=1 skipped=1',
            'Ran 4 tests in 0.1s\n\nOK': 'passed=4 failed=0 skipped=0',
            'Tests:       1 failed, 2 skipped, 9 passed, 12 total': 'passed=9 failed=1 skipped=2',
            'test result: ok. 7 passed; 0 failed; 1 ignored; 0 measured': 'passed=7 failed=0 skipped=1',
            'nothing here': 'nierozpoznane',
        }
        for text, expected in cases.items():
            self.assertEqual(kier.count_tests(text), expected, text)


if __name__ == '__main__':
    unittest.main()
