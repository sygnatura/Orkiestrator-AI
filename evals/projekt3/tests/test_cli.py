"""Testy widoczne: zachowanie, które każde zadanie etapu E2 musi zachować."""

from contextlib import redirect_stderr, redirect_stdout
import csv
import io
import json
from pathlib import Path
import tempfile
import unittest

from biblioteka import __version__
from biblioteka.cli import formatuj, main
from biblioteka.model import Ksiazka

KSIAZKI = [
    {'id': 1, 'tytul': 'Lalka', 'autor': 'Bolesław Prus', 'rok': 1890, 'wypozyczona_przez': None,
     'data_wypozyczenia': None},
    {'id': 2, 'tytul': 'Przedwiośnie', 'autor': 'Stefan Żeromski', 'rok': 1924, 'wypozyczona_przez': 'Anna Nowak',
     'data_wypozyczenia': '2026-09-01'},
    {'id': 4, 'tytul': 'Solaris', 'autor': 'Stanisław Lem', 'rok': 1961, 'wypozyczona_przez': None,
     'data_wypozyczenia': None},
    {'id': 5, 'tytul': 'Zbrodnia i kara (przekład)', 'autor': 'Fiodor Dostojewski', 'rok': None,
     'wypozyczona_przez': None, 'data_wypozyczenia': None},
]


class CliTest(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.katalog = Path(self.temp.name)
        self.dane = self.katalog / 'biblioteka.json'
        self.dane.write_text(json.dumps(KSIAZKI, ensure_ascii=False), encoding='utf-8')

    def uruchom(self, *argumenty):
        with redirect_stdout(io.StringIO()) as wyjscie, redirect_stderr(io.StringIO()) as bledy:
            kod = main(['--dane', str(self.dane), *argumenty])
        return kod, wyjscie.getvalue(), bledy.getvalue()

    def ksiazki(self):
        return json.loads(self.dane.read_text(encoding='utf-8'))

    def test_version(self):
        with redirect_stdout(io.StringIO()) as wyjscie, self.assertRaises(SystemExit) as wyjscie_kod:
            main(['--version'])
        self.assertEqual(wyjscie_kod.exception.code, 0)
        self.assertEqual(wyjscie.getvalue().strip(), f'biblioteka {__version__}')

    def test_formatuj(self):
        self.assertEqual(formatuj(Ksiazka(id=1, tytul='Lalka', autor='Bolesław Prus', rok=1890)),
                         '[1] Lalka — Bolesław Prus (1890)')
        self.assertEqual(formatuj(Ksiazka(id=7, tytul='Dziady', autor='Adam Mickiewicz', wypozyczona_przez='Ola')),
                         '[7] Dziady — Adam Mickiewicz [wypożyczona]')

    def test_lista_jedna_linia_na_ksiazke_w_kolejnosci_z_pliku(self):
        kod, wyjscie, _ = self.uruchom('lista')
        self.assertEqual(kod, 0)
        self.assertEqual(wyjscie.splitlines(), ['[1] Lalka — Bolesław Prus (1890)',
                                                '[2] Przedwiośnie — Stefan Żeromski (1924) [wypożyczona]',
                                                '[4] Solaris — Stanisław Lem (1961)',
                                                '[5] Zbrodnia i kara (przekład) — Fiodor Dostojewski'])

    def test_szukaj_po_fragmencie_autora_i_tytulu(self):
        kod, wyjscie, _ = self.uruchom('szukaj', '--autor', 'LEM')
        self.assertEqual(kod, 0)
        self.assertEqual(wyjscie.splitlines(), ['[4] Solaris — Stanisław Lem (1961)'])
        kod, wyjscie, _ = self.uruchom('szukaj', '--tytul', 'kara')
        self.assertEqual(wyjscie.splitlines(), ['[5] Zbrodnia i kara (przekład) — Fiodor Dostojewski'])

    def test_szukaj_bez_kryterium_to_blad(self):
        kod, _, bledy = self.uruchom('szukaj')
        self.assertEqual(kod, 2)
        self.assertTrue(bledy.strip())

    def test_dodaj_nadaje_kolejne_id_i_zapisuje(self):
        kod, wyjscie, _ = self.uruchom('dodaj', '--tytul', 'Cyberiada', '--autor', 'Stanisław Lem', '--rok', '1965')
        self.assertEqual(kod, 0)
        self.assertIn('[6] Cyberiada', wyjscie)
        self.assertEqual(self.ksiazki()[-1]['tytul'], 'Cyberiada')
        self.assertEqual(self.ksiazki()[-1]['rok'], 1965)

    def test_dodaj_bez_roku(self):
        kod, _, bledy = self.uruchom('dodaj', '--tytul', 'Bajki', '--autor', 'Ignacy Krasicki')
        self.assertEqual(kod, 0, bledy)
        self.assertIsNone(self.ksiazki()[-1]['rok'])

    def test_import_dopisuje_ksiazki(self):
        plik = self.katalog / 'nowe.csv'
        plik.write_text('tytul,autor,rok\nDziady,Adam Mickiewicz,1823\nFraszki,Jan Kochanowski,\n', encoding='utf-8')
        kod, _, bledy = self.uruchom('import', str(plik))
        self.assertEqual(kod, 0, bledy)
        ksiazki = self.ksiazki()
        self.assertEqual([k['id'] for k in ksiazki[-2:]], [6, 7])
        self.assertEqual(ksiazki[-1]['tytul'], 'Fraszki')
        self.assertIsNone(ksiazki[-1]['rok'])

    def test_eksport_csv(self):
        cel = self.katalog / 'eksport'
        kod, _, bledy = self.uruchom('eksport', 'katalog.csv', '--katalog-eksportu', str(cel))
        self.assertEqual(kod, 0, bledy)
        with open(cel / 'katalog.csv', encoding='utf-8', newline='') as plik:
            czytnik = csv.DictReader(plik)
            wiersze = list(czytnik)
        self.assertEqual(czytnik.fieldnames[:5], ['id', 'tytul', 'autor', 'rok', 'wypozyczona_przez'])
        self.assertEqual(len(wiersze), len(KSIAZKI))
        self.assertEqual(wiersze[1]['wypozyczona_przez'], 'Anna Nowak')
        self.assertEqual(wiersze[3]['rok'], '')

    def test_eksport_odrzuca_sciezke(self):
        kod, _, bledy = self.uruchom('eksport', '../poza.csv', '--katalog-eksportu', str(self.katalog / 'eksport'))
        self.assertEqual(kod, 2)
        self.assertTrue(bledy.strip())
        self.assertFalse((self.katalog / 'poza.csv').exists())


if __name__ == '__main__':
    unittest.main()
