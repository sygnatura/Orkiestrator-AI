"""Testy widoczne: format pliku danych. Inne narzędzia domowe czytają ten plik, więc jego układ się nie zmienia."""

import json
from pathlib import Path
import tempfile
import unittest

from biblioteka.magazyn import nastepne_id, wczytaj, zapisz
from biblioteka.model import Ksiazka


class MagazynTest(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.plik = Path(self.temp.name) / 'biblioteka.json'

    def test_zapis_zachowuje_uklad_pliku(self):
        zapisz(self.plik, [Ksiazka(id=1, tytul='Lalka', autor='Bolesław Prus', rok=1890),
                           Ksiazka(id=2, tytul='Dziady', autor='Adam Mickiewicz', wypozyczona_przez='Ola',
                                   data_wypozyczenia='2026-10-01')])
        self.assertEqual(json.loads(self.plik.read_text(encoding='utf-8')), [
            {'id': 1, 'tytul': 'Lalka', 'autor': 'Bolesław Prus', 'rok': 1890, 'wypozyczona_przez': None,
             'data_wypozyczenia': None},
            {'id': 2, 'tytul': 'Dziady', 'autor': 'Adam Mickiewicz', 'rok': None, 'wypozyczona_przez': 'Ola',
             'data_wypozyczenia': '2026-10-01'},
        ])
        self.assertIn('Bolesław', self.plik.read_text(encoding='utf-8'))

    def test_odczyt_po_zapisie(self):
        ksiazki = [Ksiazka(id=3, tytul='Chłopi', autor='Władysław Reymont', rok=1904)]
        zapisz(self.plik, ksiazki)
        self.assertEqual(wczytaj(self.plik), ksiazki)

    def test_nastepne_id(self):
        self.assertEqual(nastepne_id([]), 1)
        self.assertEqual(nastepne_id([Ksiazka(id=4, tytul='a', autor='b'), Ksiazka(id=2, tytul='c', autor='d')]), 5)

    def test_dane_przykladowe_sie_wczytuja(self):
        ksiazki = wczytaj(Path(__file__).resolve().parents[1] / 'dane' / 'biblioteka.json')
        self.assertEqual(len(ksiazki), 20)
        self.assertTrue(any(k.rok is None for k in ksiazki))


if __name__ == '__main__':
    unittest.main()
