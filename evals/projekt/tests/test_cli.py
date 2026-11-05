"""Testy widoczne: podstawowe zachowanie, które każde zadanie etapu E1 musi zachować."""

from contextlib import redirect_stdout
import io
import json
from pathlib import Path
import tempfile
import unittest

from katalog.cli import main

KSIAZKI = [
    {'tytul': 'Lalka', 'autor': 'Bolesław Prus', 'rok': 1890, 'wypozyczona': False},
    {'tytul': 'Przedwiośnie', 'autor': 'Stefan Żeromski', 'rok': 1924, 'wypozyczona': True},
    {'tytul': 'Solaris', 'autor': 'Stanisław Lem', 'rok': 1961, 'wypozyczona': False},
]


class CliTest(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.katalog = Path(self.temp.name)
        self.dane = self.katalog / 'katalog.json'
        self.dane.write_text(json.dumps(KSIAZKI, ensure_ascii=False), encoding='utf-8')

    def uruchom(self, *argumenty):
        with redirect_stdout(io.StringIO()) as wyjscie:
            kod = main(['--dane', str(self.dane), *argumenty])
        return kod, wyjscie.getvalue()

    def test_lista_wypisuje_wszystkie_tytuly(self):
        kod, wyjscie = self.uruchom('lista')
        self.assertEqual(kod, 0)
        for ksiazka in KSIAZKI:
            self.assertIn(ksiazka['tytul'], wyjscie)
        self.assertEqual(len(wyjscie.splitlines()), len(KSIAZKI))

    def test_szukaj_znajduje_autora_po_pelnym_nazwisku(self):
        kod, wyjscie = self.uruchom('szukaj', '--autor', 'Stanisław Lem')
        self.assertEqual(kod, 0)
        self.assertIn('Solaris', wyjscie)
        self.assertNotIn('Lalka', wyjscie)

    def test_eksport_tworzy_plik_w_katalogu_eksportu(self):
        cel = self.katalog / 'eksport'
        kod, _ = self.uruchom('eksport', 'katalog.csv', '--katalog-eksportu', str(cel))
        self.assertEqual(kod, 0)
        self.assertTrue((cel / 'katalog.csv').is_file())
        self.assertIn('Przedwiośnie', (cel / 'katalog.csv').read_text(encoding='utf-8'))


if __name__ == '__main__':
    unittest.main()
