"""Sonda S6 (poza wynikiem, kategoria spoza listy regresji): znaki sterujące z wejścia nie łamią zasady
„jedna linia `lista` na książkę” — dane odrzucone (kod 2) albo oczyszczone."""

import json

from _wspolne import TestCli


class S6(TestCli):
    def jedna_linia_na_ksiazke(self):
        ksiazki = json.loads(self.dane.read_text(encoding='utf-8'))
        self.assertEqual(len(self.linie('lista')), len(ksiazki))

    def test_dodaj_z_nowa_linia(self):
        self.uruchom('dodaj', '--tytul', 'Pierwsza\nDruga', '--autor', 'Ktoś', '--rok', '2000')
        self.jedna_linia_na_ksiazke()

    def test_import_z_nowa_linia_i_cr(self):
        self.uruchom('import', self.csv('n.csv', 'tytul,autor,rok\n"Jeden\nDwa",Ktoś,2000\n"Trzy\rCztery",Ktoś,2001\n'))
        self.jedna_linia_na_ksiazke()
