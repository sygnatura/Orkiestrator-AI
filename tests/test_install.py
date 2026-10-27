"""Tests of the root installer: Claude files, history-based change detection, legacy cleanup, Codex hand-off."""

import sys

sys.dont_write_bytecode = True  # no __pycache__ inside the package directories the installers copy

from contextlib import redirect_stdout
import importlib.util
import io
import json
from pathlib import Path
import subprocess
import tempfile
import unittest

REPO = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('kierownik_root_install', REPO / 'install.py')
install = importlib.util.module_from_spec(spec)
spec.loader.exec_module(install)


class InstallerTest(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix='kierownik-root-')
        self.addCleanup(self.temp.cleanup)
        self.home = Path(self.temp.name)
        self.skill = self.home / '.claude/skills/kierownik'
        self.agents = self.home / '.claude/agents'

    def run_installer(self, *args):
        with redirect_stdout(io.StringIO()) as output:
            code = install.main(['--home', str(self.home), *args])
        return code, output.getvalue()

    def test_fresh_install_copies_package_and_manifest(self):
        code, _ = self.run_installer('--claude')
        self.assertEqual(code, 0)
        for src in install.package_files().values():
            if src.is_relative_to(REPO / 'claude/kierownik'):
                relative = src.relative_to(REPO / 'claude/kierownik')
                self.assertEqual((self.skill / relative).read_bytes(), src.read_bytes())
        self.assertTrue((self.skill / 'scripts/kier.py').is_file())
        for src in (REPO / 'claude/agents').glob('*.md'):
            self.assertEqual((self.agents / src.name).read_bytes(), src.read_bytes())
        self.assertTrue((self.skill / install.MANIFEST).is_file())
        code, output = self.run_installer('--claude')
        self.assertIn('wszystkie pliki aktualne', output)

    def test_old_release_is_updated_and_state_is_kept(self):
        self.skill.mkdir(parents=True)
        self.agents.mkdir(parents=True)
        old = subprocess.check_output(['git', '-C', str(REPO), 'show', '3a64c2a:claude/agents/kier-architekt.md'])
        (self.agents / 'kier-architekt.md').write_bytes(old)
        (self.skill / 'ZESPOL.md').write_text('Stan wypełnienia: WYPEŁNIONY\nmoje limity\n', encoding='utf-8')
        (self.agents / 'moj-agent.md').write_text('własny agent\n', encoding='utf-8')
        code, output = self.run_installer('--claude')
        self.assertEqual(code, 0)
        self.assertIn('aktualizacja', output)
        self.assertNotIn('ZMIENIONEGO', output)
        self.assertEqual((self.agents / 'kier-architekt.md').read_bytes(),
                         (REPO / 'claude/agents/kier-architekt.md').read_bytes())
        self.assertIn('moje limity', (self.skill / 'ZESPOL.md').read_text(encoding='utf-8'))
        self.assertEqual((self.agents / 'moj-agent.md').read_text(encoding='utf-8'), 'własny agent\n')
        backups = list((self.home / '.kierownik/backups').rglob('kier-architekt.md'))
        self.assertEqual(len(backups), 1)

    def test_user_modified_file_needs_consent_and_is_backed_up(self):
        self.run_installer('--claude')
        target = self.agents / 'kier-wykonawca.md'
        target.write_text(target.read_text(encoding='utf-8').replace('model: opus', 'model: fable'),
                          encoding='utf-8')
        code, output = self.run_installer('--claude')
        self.assertEqual(code, 1)
        self.assertIn('model: fable', output)
        self.assertIn('model: fable', target.read_text(encoding='utf-8'))
        code, _ = self.run_installer('--claude', '--yes')
        self.assertEqual(code, 0)
        self.assertEqual(target.read_bytes(), (REPO / 'claude/agents/kier-wykonawca.md').read_bytes())
        backup = next((self.home / '.kierownik/backups').rglob('kier-wykonawca.md'))
        self.assertIn('model: fable', backup.read_text(encoding='utf-8'))

    def test_file_removed_from_package_is_deleted_with_backup(self):
        self.run_installer('--claude')
        stale = self.skill / 'STARY.md'
        stale.write_text('z poprzedniej wersji\n', encoding='utf-8')
        manifest_path = self.skill / install.MANIFEST
        manifest = json.loads(manifest_path.read_text(encoding='utf-8'))
        manifest['skill/STARY.md'] = install.sha(stale)
        manifest_path.write_text(json.dumps(manifest), encoding='utf-8')
        code, output = self.run_installer('--claude')
        self.assertEqual(code, 0)
        self.assertIn('usunięcie', output)
        self.assertFalse(stale.exists())
        self.assertTrue(list((self.home / '.kierownik/backups').rglob('STARY.md')))

    def test_upgrade_from_v12_replaces_prompt_and_keeps_state(self):
        files = subprocess.check_output(['git', '-C', str(REPO), 'ls-tree', '-r', '--name-only', 'd87a48b',
                                         'claude/kierownik', 'claude/agents'], text=True).split()
        for name in files:
            data = subprocess.check_output(['git', '-C', str(REPO), 'show', f'd87a48b:{name}'])
            relative = Path(name).relative_to('claude')
            target = (self.skill / relative.relative_to('kierownik')) if relative.parts[0] == 'kierownik' \
                else self.agents / relative.name
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(data)
        (self.skill / 'ZESPOL.md').write_text('stary rejestr v11\n', encoding='utf-8')
        registry = self.home / '.kierownik/ZESPOL.md'
        registry.parent.mkdir(parents=True)
        registry.write_text('Registry v12, schemat 2\nmoje limity\n', encoding='utf-8')
        code, output = self.run_installer('--claude')
        self.assertEqual(code, 0, output)
        self.assertNotIn('ZMIENIONEGO', output)
        self.assertIn('nowy plik', output)
        self.assertIn('scripts/kier.py', output)
        self.assertIn('Sprawdzono', output)
        self.assertEqual((self.skill / 'ZESPOL.md').read_text(encoding='utf-8'), 'stary rejestr v11\n')
        self.assertEqual(registry.read_text(encoding='utf-8'), 'Registry v12, schemat 2\nmoje limity\n')
        self.assertNotIn('2026-10-18', (self.skill / 'ZESPOL_WZOR.md').read_text(encoding='utf-8'))
        self.assertIn('model: opus', (self.agents / 'kier-wykonawca.md').read_text(encoding='utf-8'))
        self.assertEqual(install.verify(self.home), [])
        code, output = self.run_installer('--claude')
        self.assertIn('wszystkie pliki aktualne', output)

    def test_crlf_install_from_windows_is_recognised_as_a_release(self):
        files = subprocess.check_output(['git', '-C', str(REPO), 'ls-tree', '-r', '--name-only', 'd87a48b',
                                         'claude/agents'], text=True).split()
        self.agents.mkdir(parents=True)
        for name in files:
            data = subprocess.check_output(['git', '-C', str(REPO), 'show', f'd87a48b:{name}'])
            (self.agents / Path(name).name).write_bytes(data.replace(b'\n', b'\r\n'))
        code, output = self.run_installer('--claude')
        self.assertEqual(code, 0, output)
        self.assertNotIn('ZMIENIONEGO', output)
        self.assertEqual(install.verify(self.home), [])

    def test_dropped_nested_file_is_deleted_and_its_empty_directory_removed(self):
        self.run_installer('--claude')
        stale = self.skill / 'narzedzia/stary.py'
        stale.parent.mkdir()
        stale.write_text('# z poprzedniej wersji\n', encoding='utf-8')
        manifest_path = self.skill / install.MANIFEST
        manifest = json.loads(manifest_path.read_text(encoding='utf-8'))
        manifest['skill/narzedzia/stary.py'] = install.sha(stale)
        manifest_path.write_text(json.dumps(manifest), encoding='utf-8')
        code, output = self.run_installer('--claude')
        self.assertEqual(code, 0, output)
        self.assertFalse(stale.parent.exists())
        self.assertTrue(self.skill.is_dir())
        self.assertTrue(list((self.home / '.kierownik/backups').rglob('stary.py')))

    def test_users_own_files_in_the_skill_directory_are_left_alone(self):
        self.run_installer('--claude')
        notes, script = self.skill / 'NOTATKI.md', self.skill / 'scripts/moj.py'
        notes.write_text('moje\n', encoding='utf-8')
        script.write_text('print(1)\n', encoding='utf-8')
        code, output = self.run_installer('--claude')
        self.assertEqual(code, 0, output)
        self.assertEqual(notes.read_text(encoding='utf-8'), 'moje\n')
        self.assertEqual(script.read_text(encoding='utf-8'), 'print(1)\n')

    def test_dry_run_changes_nothing(self):
        code, output = self.run_installer('--claude', '--dry-run')
        self.assertEqual(code, 0)
        self.assertIn('nowy plik', output)
        self.assertFalse(self.skill.exists())

    def test_legacy_architekt_skill_is_removed_from_project(self):
        project = self.home / 'projekt'
        legacy = project / '.agents/skills/architekt'
        for name in ('SKILL.md', 'agents/openai.yaml', 'references/WORKFLOW.md'):
            data = subprocess.check_output(['git', '-C', str(REPO), 'show', f'edf061c:codex/skills/architekt/{name}'])
            (legacy / name).parent.mkdir(parents=True, exist_ok=True)
            (legacy / name).write_bytes(data)
        code, output = self.run_installer('--claude', '--project', str(project))
        self.assertEqual(code, 0)
        self.assertIn('usunięcie katalogu', output)
        self.assertFalse(legacy.exists())

    def test_codex_part_installs_user_skill(self):
        code, _ = self.run_installer('--codex')
        self.assertEqual(code, 0)
        installed = self.home / '.agents/skills/kierownik'
        self.assertEqual((installed / 'SKILL.md').read_bytes(),
                         (REPO / 'codex/skills/kierownik/SKILL.md').read_bytes())
        self.assertTrue((self.home / '.codex/config.toml').is_file())
        self.assertEqual((installed / 'scripts/kier.py').read_bytes(), (REPO / 'claude/kierownik/scripts/kier.py').read_bytes())
        self.assertNotIn('v10', (self.home / '.codex/config.toml').read_text(encoding='utf-8'))
        self.assertFalse(self.skill.exists())


class HistoryTest(unittest.TestCase):
    def test_current_package_is_recorded_in_history(self):
        history = install.load_history()
        missing = [key for key, src in install.package_files().items() if install.sha(src) not in history.get(key, set())]
        self.assertEqual(missing, [], 'run: python3 install.py --record-release')


if __name__ == '__main__':
    unittest.main()
