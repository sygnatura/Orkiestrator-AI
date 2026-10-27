"""Installer/CLI adapter tests; fake CLI results are not model-behavior evidence."""

import sys

sys.dont_write_bytecode = True  # no __pycache__ inside the package directories the installers copy

from contextlib import redirect_stdout, redirect_stderr
import importlib.util
import io
from pathlib import Path
import subprocess
import tempfile
import tomllib
import unittest
from unittest.mock import patch

PACKAGE = Path(__file__).resolve().parents[1]
SKILL = PACKAGE / 'skills' / 'kierownik'


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


install = load('kierownik_install', PACKAGE / 'install.py')
runner = load('kierownik_runner', SKILL / 'scripts' / 'run_agent.py')


class ProjectTest(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix='kierownik-v10-')
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name).resolve()
        self.project = self.root / 'project with spaces'
        self.project.mkdir()
        self.git('init', '-q')
        self.git('config', 'user.name', 'Fixture')
        self.git('config', 'user.email', 'fixture@example.invalid')
        (self.project / 'tracked.txt').write_text('original\n')
        self.git('add', 'tracked.txt')
        self.git('commit', '-qm', 'fixture')

    def git(self, *args):
        return subprocess.check_output(['git', '-C', str(self.project), *args], stderr=subprocess.PIPE)

    def install(self, *args):
        with redirect_stdout(io.StringIO()):
            return install.main(['--project', str(self.project), *args])

    @property
    def target(self):
        return self.project / '.agents/skills/kierownik'


class InstallationTests(ProjectTest):
    def test_install_and_registration_preserve_existing_settings_and_claude(self):
        (self.project / 'CLAUDE.md').write_text('user rules\n')
        config = self.project / '.codex/config.toml'
        config.parent.mkdir()
        config.write_text('approval_policy = "on-request"\n[agents]\nmax_depth = 2\n')
        self.assertEqual(self.install('--register-agents'), 0)
        parsed = tomllib.loads(config.read_text())
        self.assertEqual(parsed['approval_policy'], 'on-request')
        self.assertEqual(parsed['agents']['max_depth'], 2)
        for role in install.ROLES:
            self.assertTrue(Path(parsed['agents'][role]['config_file']).is_file())
        self.assertEqual((self.project / 'CLAUDE.md').read_text(), 'user rules\n')

    def test_reinstall_retains_team_state_and_config_bytes(self):
        self.install('--register-agents')
        team = self.target / 'ZESPOL.md'
        team.write_text('Owner model mapping and limits\n')
        config = self.project / '.codex/config.toml'
        before = config.read_bytes()
        self.install('--register-agents')
        self.assertEqual(team.read_text(), 'Owner model mapping and limits\n')
        self.assertEqual(config.read_bytes(), before)

    def test_upgrade_backs_up_customizations_and_keeps_team(self):
        self.install()
        (self.target / 'ZESPOL.md').write_text('custom team\n')
        (self.target / 'SKILL.md').write_text('custom old skill\n')
        self.install('--upgrade')
        self.assertEqual((self.target / 'ZESPOL.md').read_text(), 'custom team\n')
        self.assertEqual((self.target / 'SKILL.md').read_bytes(), (SKILL / 'SKILL.md').read_bytes())
        backups = list((self.project / '.agents/backups').glob('*/kierownik/SKILL.md'))
        self.assertEqual(len(backups), 1)
        self.assertEqual(backups[0].read_text(), 'custom old skill\n')

    def test_collision_without_upgrade_does_not_replace(self):
        self.target.mkdir(parents=True)
        (self.target / 'SKILL.md').write_text('owner skill\n')
        with self.assertRaises(ValueError):
            self.install()
        self.assertEqual((self.target / 'SKILL.md').read_text(), 'owner skill\n')

    def test_native_role_collision_prevents_install_and_config_change(self):
        config = self.project / '.codex/config.toml'
        config.parent.mkdir()
        original = '[agents.kier-analityk]\nconfig_file = "owner-role.toml"\n'
        config.write_text(original)
        with self.assertRaises(ValueError):
            self.install('--register-agents')
        self.assertFalse(self.target.exists())
        self.assertEqual(config.read_text(), original)

    def test_symlink_does_not_write_outside_project(self):
        outside = self.root / 'outside'
        outside.mkdir()
        try:
            (self.project / '.agents').symlink_to(outside, target_is_directory=True)
        except OSError as error:  # Windows without the symlink privilege: nothing to test here
            self.skipTest(f'dowiązania niedostępne: {error}')
        with self.assertRaises(ValueError):
            self.install()
        self.assertEqual(list(outside.iterdir()), [])

    def test_non_git_project_is_rejected(self):
        invalid = self.root / 'non-git'
        invalid.mkdir()
        with self.assertRaises(ValueError):
            install.main(['--project', str(invalid)])
        self.assertFalse((invalid / '.agents').exists())

    def test_user_install_needs_no_project_and_keeps_other_skills(self):
        user = self.root / 'user'
        user.mkdir()
        other = user / '.agents/skills/other/SKILL.md'
        other.parent.mkdir(parents=True)
        other.write_text('other skill')
        with patch.object(Path, 'home', return_value=user), redirect_stdout(io.StringIO()):
            self.assertEqual(install.main(['--user', '--register-agents']), 0)
        self.assertTrue((user / '.agents/skills/kierownik/SKILL.md').is_file())
        self.assertEqual(other.read_text(), 'other skill')


class RunnerTests(ProjectTest):
    def setUp(self):
        super().setUp()
        self.prompt = self.root / 'order.md'
        self.literal = 'literal `not-a-command` $(not-a-command) and "$example"\n'
        self.prompt.write_text(self.literal)
        self.result = self.root / 'result.md'
        self.calls = []

    def run_role(self, role='kier-recenzent', code=0, make_report=True, mutate=None, extra=()):
        original_run = subprocess.run

        def fake(command, **kwargs):
            if command[0] != 'codex-test':
                return original_run(command, **kwargs)
            self.calls.append((command, kwargs))
            if mutate:
                mutate()
            if make_report:
                Path(command[command.index('-o') + 1]).write_text('fixture report\n')
            return subprocess.CompletedProcess(command, code)

        with patch.object(subprocess, 'run', side_effect=fake), redirect_stdout(io.StringIO()), redirect_stderr(io.StringIO()):
            return runner.main(['--role', role, '--cwd', str(self.project), '--prompt', str(self.prompt),
                                '--result', str(self.result), '--codex', 'codex-test', *extra])

    def test_fresh_cli_session_with_literal_stdin_and_correct_cwd(self):
        self.assertEqual(self.run_role(), 0)
        command, kwargs = self.calls[0]
        self.assertIn('exec', command)
        self.assertNotIn('resume', command)
        self.assertNotIn('shell', kwargs)
        self.assertEqual(command[command.index('-C') + 1], str(self.project))
        self.assertEqual(kwargs['input'], self.literal)
        self.assertIn('developer_instructions=', '\n'.join(command))
        self.assertEqual(command[command.index('-s') + 1], 'workspace-write')
        self.assertTrue(Path(str(self.result) + '.err').is_file())

    def test_exit_code_is_preserved(self):
        self.assertEqual(self.run_role(code=17), 17)

    def test_zero_exit_without_report_is_not_success(self):
        self.assertEqual(self.run_role(make_report=False), 4)

    def test_reviewer_source_change_invalidates_result(self):
        self.assertEqual(self.run_role(mutate=lambda: (self.project / 'tracked.txt').write_text('changed')), 3)

    def test_reviewer_commit_with_clean_status_invalidates_result(self):
        self.assertEqual(self.run_role(mutate=lambda: self.git('commit', '--allow-empty', '-qm', 'unexpected')), 3)

    def test_reviewer_change_to_existing_untracked_source_invalidates_result(self):
        source = self.project / 'untracked.txt'
        source.write_text('before')
        self.assertEqual(self.run_role(mutate=lambda: source.write_text('after')), 3)

    def test_reviewer_new_test_caches_are_allowed(self):
        def caches():
            (self.project / '.pytest_cache/v/cache').mkdir(parents=True)
            (self.project / '.pytest_cache/v/cache/lastfailed').write_text('{}')
            (self.project / 'pkg/__pycache__').mkdir(parents=True)
            (self.project / 'pkg/__pycache__/m.cpython-312.pyc').write_bytes(b'\0')
        self.assertEqual(self.run_role(mutate=caches), 0)

    def test_reviewer_adding_a_source_file_invalidates_result(self):
        self.assertEqual(self.run_role(mutate=lambda: (self.project / 'new_source.py').write_text('x = 1\n')), 3)

    def test_reviewer_deleting_existing_untracked_file_invalidates_result(self):
        source = self.project / 'untracked.txt'
        source.write_text('before')
        self.assertEqual(self.run_role(mutate=source.unlink), 3)

    def test_reviewer_caches_do_not_hide_tracked_change(self):
        def both():
            (self.project / '.pytest_cache').mkdir()
            (self.project / '.pytest_cache/x').write_text('c')
            (self.project / 'tracked.txt').write_text('changed')
        self.assertEqual(self.run_role(mutate=both), 3)

    def test_analyzer_source_change_invalidates_result(self):
        self.assertEqual(self.run_role(role='kier-analityk', mutate=lambda: (self.project / 'tracked.txt').write_text('changed')), 3)
        self.assertEqual(self.calls[0][0][self.calls[0][0].index('-s') + 1], 'read-only')

    def test_existing_result_is_preserved_and_cli_not_called(self):
        self.result.write_text('owner result\n')
        with self.assertRaises(SystemExit):
            self.run_role()
        self.assertEqual(self.result.read_text(), 'owner result\n')
        self.assertFalse(self.calls)

    def test_verified_model_and_effort_override_reach_cli(self):
        self.assertEqual(self.run_role(extra=('--model', 'fixture-model', '--effort', 'medium')), 0)
        command = self.calls[0][0]
        self.assertEqual(command[command.index('-m') + 1], 'fixture-model')
        self.assertIn('model_reasoning_effort="medium"', command)



if __name__ == '__main__':
    unittest.main()
