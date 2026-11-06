"""Zadania zmieniające te same miejsca: po scaleniu wszystkie działają razem."""

import unicodedata

from _wspolne import ISBN_A, ISBN_C, TestCli, ksiazka


class Kolizja(TestCli):
    def test_lista_wszystkie_flagi_razem(self):
        self.assertEqual(self.linie('lista', '--autor', 'sienk', '--tylko-dostepne', '--sortuj', 'rok', '--szczegoly'),
                         ['[5] Ogniem i mieczem — Henryk Sienkiewicz (1884)', '    dostępna'])
        self.assertEqual(self.linie('lista', '--autor', 'żerom', '--sortuj', 'tytul', '--szczegoly'), [
            '[3] Ludzie bezdomni — Stefan Żeromski (1900)', '    dostępna',
            '[2] Przedwiośnie — Stefan Żeromski (1924) [wypożyczona]',
            '    wypożyczona przez: Anna Nowak, od 2026-09-01'])

    def test_eksport_isbn_i_neutralizacja(self):
        self.zapisz_dane([ksiazka(1, '=SUMA(A1)', '@autor', 2001, isbn=ISBN_A)])
        kolumny, wiersze = self.eksport()
        self.assertEqual(kolumny[-1], 'isbn')
        self.assertEqual((wiersze[0]['tytul'], wiersze[0]['autor'], wiersze[0]['isbn']),
                         ("'=SUMA(A1)", "'@autor", ISBN_A))

    def test_import_isbn_rok_nfc(self):
        nfd = unicodedata.normalize('NFD', 'Żywoty,Mikołaj Rej')
        self.linie('import', self.csv('a.csv', f'tytul,autor,rok,isbn\n{nfd},1562,{ISBN_C}\n'))
        nowa = self.ksiazki()[-1]
        self.assertEqual((nowa['tytul'], nowa['rok'], nowa['isbn']), ('Żywoty', 1562, ISBN_C))
        self.przed = self.dane.read_bytes()
        bledy = self.odmowa('import', self.csv('b.csv', f'tytul,autor,rok,isbn\nA,B,1900,{ISBN_A}\nC,D,1300,\n'))
        self.assertIn('wiersz 3', bledy)

    def test_wypozyczenie_w_statystykach_i_raporcie(self):
        self.linie('wypozycz', '1', '--osoba', 'Ola', '--data', '2026-01-01')
        self.assertEqual(self.linie('przetrzymane', '--dzis', '2026-03-01')[0], '[1] Lalka — Ola, 59 dni')
        self.assertEqual(self.linie('statystyki')[1], 'Wypożyczonych: 4 (50,0%)')
        self.assertTrue((self.katalog / 'biblioteka.json.bak').is_file())
