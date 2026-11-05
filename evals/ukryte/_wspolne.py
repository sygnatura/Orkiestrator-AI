"""Wspólne dla ukrytych testów: uruchomienie CLI projektu w osobnym procesie na danych z testu."""

import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

PROJEKT = Path(os.environ.get('KATALOG_PROJEKT', os.getcwd())).resolve()

KSIAZKI = [
    {'tytul': 'Lalka', 'autor': 'Bolesław Prus', 'rok': 1890, 'wypozyczona': False},
    {'tytul': 'Przedwiośnie', 'autor': 'Stefan Żeromski', 'rok': 1924, 'wypozyczona': True},
    {'tytul': 'Ludzie bezdomni', 'autor': 'Stefan Żeromski', 'rok': 1900, 'wypozyczona': False},
    {'tytul': 'Nad Niemnem', 'autor': 'Eliza Orzeszkowa', 'rok': 1888, 'wypozyczona': False},
    {'tytul': 'Quo vadis', 'autor': 'Henryk Sienkiewicz', 'rok': 1896, 'wypozyczona': True},
    {'tytul': 'Ogniem i mieczem', 'autor': 'Henryk Sienkiewicz', 'rok': 1884, 'wypozyczona': False},
    {'tytul': 'Chłopi', 'autor': 'Władysław Reymont', 'rok': 1904, 'wypozyczona': False},
    {'tytul': 'Pan Tadeusz, czyli "Ostatni zajazd na Litwie"', 'autor': 'Adam Mickiewicz', 'rok': 1834,
     'wypozyczona': False},
    {'tytul': 'Zbrodnia i kara (przekład)', 'autor': 'Fiodor Dostojewski', 'rok': None, 'wypozyczona': False},
]


class TestCli(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.katalog = Path(self.temp.name).resolve()
        self.dane = self.katalog / 'katalog.json'
        self.dane.write_text(json.dumps(KSIAZKI, ensure_ascii=False), encoding='utf-8')

    def uruchom(self, *argumenty, dane=True):
        polecenie = [sys.executable, '-m', 'katalog', *(['--dane', str(self.dane)] if dane else []), *argumenty]
        srodowisko = dict(os.environ, PYTHONIOENCODING='utf-8', PYTHONDONTWRITEBYTECODE='1')
        wynik = subprocess.run(polecenie, cwd=PROJEKT, capture_output=True, env=srodowisko, timeout=60)
        return wynik.returncode, wynik.stdout.decode('utf-8'), wynik.stderr.decode('utf-8', 'replace')

    def linie(self, *argumenty):
        kod, wyjscie, bledy = self.uruchom(*argumenty)
        self.assertEqual(kod, 0, bledy)
        return wyjscie.splitlines()
