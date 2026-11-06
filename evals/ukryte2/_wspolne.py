"""Wspólne dla ukrytych testów zestawu 2: CLI projektu w osobnym procesie na danych z testu."""

import csv
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

PROJEKT = Path(os.environ.get('KATALOG_PROJEKT', os.getcwd())).resolve()
ISBN_A, ISBN_B, ISBN_C = '9788324012343', '9788301012342', '9788375067897'


def ksiazka(id, tytul, autor, rok=None, osoba=None, data=None, **inne):
    return {'id': id, 'tytul': tytul, 'autor': autor, 'rok': rok, 'wypozyczona_przez': osoba,
            'data_wypozyczenia': data, **inne}


KSIAZKI = [
    ksiazka(1, 'Lalka', 'Bolesław Prus', 1890),
    ksiazka(2, 'Przedwiośnie', 'Stefan Żeromski', 1924, 'Anna Nowak', '2026-09-01'),
    ksiazka(3, 'Ludzie bezdomni', 'Stefan Żeromski', 1900),
    ksiazka(4, 'Quo vadis', 'Henryk Sienkiewicz', 1896, 'Piotr Wiśniewski', '2026-10-20'),
    ksiazka(5, 'Ogniem i mieczem', 'Henryk Sienkiewicz', 1884),
    ksiazka(6, 'Krzyżacy', 'Henryk Sienkiewicz', 1900, 'Ewa Zielińska', None),
    ksiazka(7, 'Zbrodnia i kara (przekład)', 'Fiodor Dostojewski'),
    ksiazka(8, 'Pan Tadeusz, czyli "Ostatni zajazd na Litwie"', 'Adam Mickiewicz', 1834),
]


class TestCli(unittest.TestCase):
    KSIAZKI = KSIAZKI

    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.katalog = Path(self.temp.name).resolve()
        self.dane = self.katalog / 'biblioteka.json'
        self.zapisz_dane(self.KSIAZKI)

    def zapisz_dane(self, ksiazki):
        self.dane.write_text(json.dumps(ksiazki, ensure_ascii=False, indent=1) + '\n', encoding='utf-8')
        self.przed = self.dane.read_bytes()

    def uruchom(self, *argumenty):
        polecenie = [sys.executable, '-m', 'biblioteka', '--dane', str(self.dane), *argumenty]
        srodowisko = dict(os.environ, PYTHONIOENCODING='utf-8', PYTHONDONTWRITEBYTECODE='1')
        wynik = subprocess.run(polecenie, cwd=PROJEKT, capture_output=True, env=srodowisko, timeout=60)
        return wynik.returncode, wynik.stdout.decode('utf-8'), wynik.stderr.decode('utf-8', 'replace')

    def linie(self, *argumenty):
        kod, wyjscie, bledy = self.uruchom(*argumenty)
        self.assertEqual(kod, 0, bledy)
        return wyjscie.splitlines()

    def odmowa(self, *argumenty):
        """Kod 2, komunikat na stderr, plik danych bez zmian."""
        kod, _, bledy = self.uruchom(*argumenty)
        self.assertEqual(kod, 2, argumenty)
        self.assertTrue(bledy.strip(), argumenty)
        self.assertEqual(self.dane.read_bytes(), self.przed, argumenty)
        return bledy

    def ksiazki(self):
        return json.loads(self.dane.read_text(encoding='utf-8'))

    def csv(self, nazwa, tekst):
        plik = self.katalog / nazwa
        plik.write_text(tekst, encoding='utf-8')
        return str(plik)

    def eksport(self):
        cel = self.katalog / 'eksport'
        kod, _, bledy = self.uruchom('eksport', 'k.csv', '--katalog-eksportu', str(cel))
        self.assertEqual(kod, 0, bledy)
        with open(cel / 'k.csv', encoding='utf-8', newline='') as plik:
            czytnik = csv.DictReader(plik)
            return czytnik.fieldnames, list(czytnik)

    def python(self, kod, *argumenty):
        """Kod Pythona w katalogu projektu (moduły projektu importowalne)."""
        srodowisko = dict(os.environ, PYTHONIOENCODING='utf-8', PYTHONDONTWRITEBYTECODE='1')
        wynik = subprocess.run([sys.executable, '-c', kod, *argumenty], cwd=PROJEKT, capture_output=True,
                               env=srodowisko, timeout=60)
        return wynik.returncode, wynik.stdout.decode('utf-8'), wynik.stderr.decode('utf-8', 'replace')
