"""Tests of the eval kit: the hidden acceptance tests fail on the untouched project and pass on the reference
solution, preparation keeps hidden material out of the copy, scoring and the summary report what happened."""

import sys

sys.dont_write_bytecode = True  # no __pycache__ inside the eval project that preparation copies

from contextlib import redirect_stdout
import importlib.util
import io
import json
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest

EVALS = Path(__file__).resolve().parents[1] / 'evals'


def load(name):
    spec = importlib.util.spec_from_file_location(f'kierownik_eval_{name}', EVALS / f'{name}.py')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


przygotuj, ocen, zestaw = load('przygotuj'), load('ocen'), load('zestaw')


class EvalKitTest(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix='eval-')
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name).resolve()

    def copy(self, name, reference=False):
        with redirect_stdout(io.StringIO()):
            path = przygotuj.przygotuj(self.root / name, remote=False)
        if reference:
            shutil.copytree(EVALS / 'wzorzec', path, dirs_exist_ok=True)
            subprocess.run(['git', '-C', str(path), 'commit', '-qam', 'wzorzec'], check=True)
        return path

    def test_untouched_project_passes_visible_tests_and_fails_every_task(self):
        result = ocen.ocen(self.copy('czysty'))
        self.assertTrue(result['widoczne']['zaliczone'])
        self.assertEqual(result['zadania_zaliczone'], 0)
        self.assertFalse(any(result['ukryte'].values()), result['ukryte'])
        self.assertEqual(set(result['ukryte']), set(ocen.ZADANIA) | {'KOLIZJA'})

    def test_reference_solution_passes_everything(self):
        result = ocen.ocen(self.copy('wzorzec', reference=True))
        self.assertTrue(result['widoczne']['zaliczone'])
        self.assertTrue(all(result['ukryte'].values()), result['ukryte'])
        self.assertEqual(result['zadania_zaliczone'], len(ocen.ZADANIA))
        self.assertEqual(result['oslabione_testy'], [])

    def test_preparation_keeps_hidden_material_out_and_refuses_the_repository(self):
        path = self.copy('kopia')
        self.assertEqual(subprocess.run(['git', '-C', str(path), 'rev-list', '--count', 'HEAD'], capture_output=True,
                                        text=True, check=True).stdout.strip(), '1')
        names = {p.name for p in path.rglob('*')}
        self.assertFalse(names & {'ukryte', 'wzorzec', '_wspolne.py', 'test_T001.py'})
        with self.assertRaises(SystemExit):
            przygotuj.przygotuj(EVALS / 'nie-tutaj', remote=False)

    def test_weakened_visible_test_is_reported(self):
        path = self.copy('oslabiony')
        test = path / 'tests' / 'test_cli.py'
        text = test.read_text(encoding='utf-8').replace('def test_eksport_tworzy_plik_w_katalogu_eksportu',
                                                        'def _wylaczony')
        test.write_text(text, encoding='utf-8')
        self.assertTrue(any('test_eksport_tworzy_plik_w_katalogu_eksportu' in note
                            for note in ocen.oslabione_testy(path)))

    def test_summary_lists_runs_and_averages(self):
        results = self.root / 'wyniki'
        results.mkdir()
        base = ocen.ocen(self.copy('zestaw', reference=True))
        for konf, minutes in (('A', 10), ('B', 20)):
            data = dict(base, data='2026-11-05', konfiguracja=konf, przebieg=1, minuty=minutes, tokeny=None,
                        rundy=None, uwagi='')
            (results / f'{konf}.json').write_text(json.dumps(data, ensure_ascii=False), encoding='utf-8')
        target = self.root / 'WYNIKI.md'
        with redirect_stdout(io.StringIO()):
            zestaw.main(['--wyniki', str(results), '--cel', str(target)])
        text = target.read_text(encoding='utf-8')
        self.assertIn('| A | 1 |', text)
        self.assertIn('B — kierownik, tylko Claude', text)
        self.assertIn('7/7', text)


if __name__ == '__main__':
    unittest.main()
