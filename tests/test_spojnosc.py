"""Drift guard: the Claude and Codex packages are maintained by hand, so the shared parts must stay in step."""

import sys

sys.dont_write_bytecode = True  # no __pycache__ inside the package directories the installers copy

import importlib.util
from pathlib import Path
import re
import unittest

REPO = Path(__file__).resolve().parents[1]
CLAUDE = REPO / 'claude' / 'kierownik'
CODEX = REPO / 'codex' / 'skills' / 'kierownik'
SHARED = ('ZESPOL_WZOR.md', 'ZESPOL_PROCEDURY.md', 'URUCHAMIANIE_CLI.md', 'scripts/kier.py')
PROTOCOL = ('TODO', 'W TOKU', 'DO SPRAWDZENIA', 'GOTOWE', 'ZABLOKOWANE', 'ZALICZONE', 'DO POPRAWY', 'BLOKUJĄCE',
            'OPCJONALNE', 'NIE SPRAWDZONO', 'przydział', 'ścieżka szybka', 'recenzja tą samą klasą',
            'Registry v12, schemat 2', 'KONFLIKT')
ORDER_FIELDS = ('ZADANIE', 'PO CO', 'PRZECZYTAJ', 'ŚRODOWISKO', 'ZAKRES', 'KRYTERIA', 'KONFLIKT', 'NIE',
                'RECENZJA', 'PYTANIE')
SHORTCUTS = ('status', 'dalej', 'pomysł:', 'zmiana:', 'zespół:', 'stop')
SKILL_LIMIT = 390


def read(path: Path) -> str:
    return path.read_text(encoding='utf-8')


class SharedFilesTest(unittest.TestCase):
    def test_shared_files_are_byte_identical(self):
        for name in SHARED:
            self.assertEqual((CLAUDE / name).read_bytes(), (CODEX / name).read_bytes(), name)

    def test_protocol_words_appear_in_both_skills(self):
        for skill in (CLAUDE / 'SKILL.md', CODEX / 'SKILL.md'):
            text = read(skill)
            for word in PROTOCOL:
                self.assertIn(word, text, f'{word} w {skill.relative_to(REPO)}')

    def test_order_fields_appear_in_both_templates(self):
        for orders in (CLAUDE / 'ZLECENIA.md', CODEX / 'ZLECENIA.md'):
            text = read(orders)
            for field in ORDER_FIELDS:
                self.assertRegex(text, rf'(?m)^\s*\[?{field}:', f'{field} w {orders.relative_to(REPO)}')

    def test_owner_shortcuts_appear_in_both_skills(self):
        for skill in (CLAUDE / 'SKILL.md', CODEX / 'SKILL.md'):
            text = read(skill)
            for shortcut in SHORTCUTS:
                self.assertIn(f'`{shortcut}', text, f'{shortcut} w {skill.relative_to(REPO)}')

    def test_every_kier_subcommand_named_in_the_prompts_exists(self):
        spec = importlib.util.spec_from_file_location('kierownik_kier_spojnosc', CLAUDE / 'scripts' / 'kier.py')
        kier = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(kier)
        actions = next(a for a in kier.parser()._actions if a.dest == 'cmd')
        known = set(actions.choices)
        files = [CLAUDE / 'SKILL.md', CODEX / 'SKILL.md', CLAUDE / 'URUCHAMIANIE_CLI.md', CLAUDE / 'ZLECENIA.md',
                 CLAUDE / 'ZESPOL_PROCEDURY.md']
        for path in files:
            for name in re.findall(r'(?:KIER|kier\.py) ([a-z][a-z-]+)', read(path)):
                self.assertIn(name, known, f'kier.py {name} w {path.relative_to(REPO)}')

    def test_no_stale_versions_in_codex_metadata(self):
        for path in (CODEX / 'agents' / 'openai.yaml', REPO / 'codex' / 'install.py'):
            self.assertNotRegex(read(path), r'v1[01]\b', str(path.relative_to(REPO)))

    def test_skill_stays_short(self):
        for skill in (CLAUDE / 'SKILL.md', CODEX / 'SKILL.md'):
            self.assertLessEqual(len(read(skill).splitlines()), SKILL_LIMIT, str(skill.relative_to(REPO)))

    def test_template_carries_no_pre_given_consent(self):
        self.assertNotIn('2026-10-18', read(CLAUDE / 'ZESPOL_WZOR.md'))
        self.assertIn('BRAK', read(CLAUDE / 'ZESPOL_WZOR.md'))


if __name__ == '__main__':
    unittest.main()
