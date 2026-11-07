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

    def copy(self, name, reference=False, numer=1):
        with redirect_stdout(io.StringIO()):
            path = przygotuj.przygotuj(self.root / name, remote=False, numer=numer)
        if reference:
            shutil.copytree(EVALS / ('wzorzec' if numer == 1 else f'wzorzec{numer}'), path, dirs_exist_ok=True)
            subprocess.run(['git', '-C', str(path), 'add', '-A'], check=True)
            subprocess.run(['git', '-C', str(path), 'commit', '-qm', 'wzorzec'], check=True)
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

    def test_set_2_untouched_fails_every_task_and_reference_passes_everything(self):
        tasks = ocen.zestaw(2)['zadania']
        self.assertEqual(len(tasks), 12)
        clean = ocen.ocen(self.copy('czysty2', numer=2), 2)
        self.assertTrue(clean['widoczne']['zaliczone'])
        self.assertFalse(any(clean['ukryte'].values()), clean['ukryte'])
        self.assertEqual(set(clean['ukryte']), set(tasks) | {'KOLIZJA'})
        self.assertIs(clean['zalozenie_zgloszone'], False)
        reference = ocen.ocen(self.copy('wzorzec2', reference=True, numer=2), 2)
        self.assertTrue(reference['widoczne']['zaliczone'])
        self.assertTrue(all(reference['ukryte'].values()), reference['ukryte'])
        self.assertEqual(reference['zadania_zaliczone'], 12)
        self.assertEqual((reference['oslabione_testy'], reference['zmienione_testy']), ([], []))
        self.assertEqual(sorted(reference['sondy']), ['S1', 'S2', 'S3', 'S4', 'S5', 'S6'])
        self.assertTrue(all(reference['sondy'].values()), reference['sondy'])
        self.assertEqual(ocen.ocen(self.copy('czysty1'))['sondy'], {})

    def test_probe_catches_a_replaced_symlink(self):
        try:
            (self.root / 'link').symlink_to(self.root)
        except OSError as error:
            self.skipTest(f'symlinks unavailable: {error}')
        path = self.copy('dowiazanie', reference=True, numer=2)
        store = path / 'biblioteka' / 'magazyn.py'
        store.write_text(store.read_text(encoding='utf-8').replace('Path(os.path.realpath(sciezka))', 'Path(sciezka)'),
                         encoding='utf-8')
        probes = ocen.testy_ukryte(path, 2, sondy=True)
        self.assertFalse(probes['S2'], probes)
        self.assertTrue(probes['S4'], probes)

    def test_set_3_untouched_fails_every_task_and_reference_passes_everything(self):
        tasks = ocen.zestaw(3)['zadania']
        self.assertEqual(len(tasks), 12)
        clean = ocen.ocen(self.copy('czysty3', numer=3), 3)
        self.assertTrue(clean['widoczne']['zaliczone'])
        self.assertFalse(any(clean['ukryte'][z] for z in tasks), clean['ukryte'])
        self.assertEqual(clean['dodatkowe'], {'CIAGLOSC': False, 'REGRESJA': True})
        self.assertIsNone(clean['kolizja_zaliczona'])
        reference = ocen.ocen(self.copy('wzorzec3', reference=True, numer=3), 3)
        self.assertTrue(reference['widoczne']['zaliczone'])
        self.assertTrue(all(reference['ukryte'].values()), reference['ukryte'])
        self.assertEqual((reference['oslabione_testy'], reference['zmienione_testy']), ([], []))

    def test_changed_visible_test_and_reported_assumption_are_detected(self):
        path = self.copy('zmieniony', numer=2)
        test = path / 'tests' / 'test_magazyn.py'
        test.write_text(test.read_text(encoding='utf-8').replace("'rok': 1890, 'wypozyczona_przez': None,",
                                                                 "'rok': 1890, 'isbn': None, 'wypozyczona_przez': None,"),
                        encoding='utf-8')
        with open(test, 'a', encoding='utf-8') as plik:
            plik.write('\n\ndef test_nowy_obok():\n    assert True\n')
        self.assertEqual(ocen.zmienione_testy(path, 2), ['zmieniona test_magazyn.py:MagazynTest.test_zapis_zachowuje_uklad_pliku'])
        self.assertIs(ocen.zalozenie_zgloszone(path, 2), False)
        subprocess.run(['git', '-C', str(path), 'commit', '-qam', 'feat(T-107): walidacja roku\n\n'
                        'Rok zostaje opcjonalny: kryterium sprzeczne z testami widocznymi.'], check=True)
        self.assertIs(ocen.zalozenie_zgloszone(path, 2), True)
        self.assertIsNone(ocen.zalozenie_zgloszone(path, 1))

    def test_preparation_keeps_hidden_material_out_and_refuses_the_repository(self):
        path = self.copy('kopia')
        self.assertEqual(subprocess.run(['git', '-C', str(path), 'rev-list', '--count', 'HEAD'], capture_output=True,
                                        text=True, check=True).stdout.strip(), '1')
        names = {p.name for p in path.rglob('*')}
        self.assertFalse(names & {'ukryte', 'wzorzec', '_wspolne.py', 'test_T001.py'})
        with redirect_stdout(io.StringIO()):
            path2 = przygotuj.przygotuj(self.root / 'kopia2', remote=False, numer=2)
        names2 = {p.name for p in path2.rglob('*')}
        self.assertIn('biblioteka', names2)
        with redirect_stdout(io.StringIO()):
            path3 = przygotuj.przygotuj(self.root / 'kopia3', remote=False, numer=3)
        self.assertFalse({p.name for p in path3.rglob('*')} & {'ukryte3', 'wzorzec3', 'test_T201.py', 'stan.py',
                                                               'konfiguracja.py', 'test_CIAGLOSC.py'})
        self.assertFalse(names2 & {'ukryte2', 'wzorzec2', 'sondy2', '_wspolne.py', 'test_T101.py', 'test_S1.py',
                                   'walidacja.py', 'isbn.py'})
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
        self.assertIn('B — kierownik, tylko Claude (z2: wykonawca Opus)', text)
        self.assertIn('7/7', text)


if __name__ == '__main__':
    unittest.main()
