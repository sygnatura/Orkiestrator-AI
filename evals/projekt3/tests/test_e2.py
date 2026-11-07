"""Testy widoczne funkcji z etapu E2: ISBN, wypożyczenia, raport, lista z filtrami, statystyki, bezpieczny eksport."""

from contextlib import redirect_stderr, redirect_stdout
import csv
import io
import json
from pathlib import Path
import tempfile
import unittest

from biblioteka.cli import main

KSIAZKI = [
    {'id': 1, 'tytul': 'Lalka', 'autor': 'Bolesław Prus', 'rok': 1890, 'wypozyczona_przez': None,
     'data_wypozyczenia': None},
    {'id': 2, 'tytul': 'Przedwiośnie', 'autor': 'Stefan Żeromski', 'rok': 1924, 'wypozyczona_przez': 'Anna Nowak',
     'data_wypozyczenia': '2026-09-01'},
    {'id': 3, 'tytul': '=Zła formuła', 'autor': 'Ktoś', 'rok': 2001, 'wypozyczona_przez': None,
     'data_wypozyczenia': None, 'isbn': '9788324012343'},
]


class E2Test(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.katalog = Path(self.temp.name)
        self.dane = self.katalog / 'biblioteka.json'
        self.dane.write_text(json.dumps(KSIAZKI, ensure_ascii=False), encoding='utf-8')

    def uruchom(self, *argumenty):
        with redirect_stdout(io.StringIO()) as wyjscie, redirect_stderr(io.StringIO()) as bledy:
            kod = main(['--dane', str(self.dane), *argumenty])
        return kod, wyjscie.getvalue().splitlines(), bledy.getvalue()

    def test_szukaj_po_isbn(self):
        kod, linie, _ = self.uruchom('szukaj', '--isbn', '978-83-240-1234-3')
        self.assertEqual((kod, len(linie)), (0, 1))
        self.assertIn('Zła formuła', linie[0])

    def test_wypozycz_i_zwroc(self):
        kod, _, bledy = self.uruchom('wypozycz', '1', '--osoba', 'Ola', '--data', '2026-10-01')
        self.assertEqual(kod, 0, bledy)
        kod, _, bledy = self.uruchom('zwroc', '1')
        self.assertEqual(kod, 0, bledy)
        self.assertEqual(self.uruchom('zwroc', '1')[0], 2)

    def test_przetrzymane(self):
        kod, linie, _ = self.uruchom('przetrzymane', '--dzis', '2026-11-05')
        self.assertEqual((kod, linie), (0, ['[2] Przedwiośnie — Anna Nowak, 65 dni']))

    def test_lista_z_filtrami(self):
        kod, linie, _ = self.uruchom('lista', '--tylko-dostepne', '--sortuj', 'rok')
        self.assertEqual(linie, ['[1] Lalka — Bolesław Prus (1890)', '[3] =Zła formuła — Ktoś (2001)'])

    def test_statystyki(self):
        kod, linie, _ = self.uruchom('statystyki')
        self.assertEqual(kod, 0)
        self.assertEqual(linie[:2], ['Książek: 3', 'Wypożyczonych: 1 (33,3%)'])

    def test_eksport_neutralizuje_formuly(self):
        cel = self.katalog / 'eksport'
        self.assertEqual(self.uruchom('eksport', 'k.csv', '--katalog-eksportu', str(cel))[0], 0)
        with open(cel / 'k.csv', encoding='utf-8', newline='') as plik:
            wiersze = list(csv.DictReader(plik))
        self.assertEqual(wiersze[2]['tytul'], "'=Zła formuła")
        self.assertEqual(wiersze[2]['isbn'], '9788324012343')


if __name__ == '__main__':
    unittest.main()
