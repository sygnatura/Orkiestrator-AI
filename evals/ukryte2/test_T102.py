import json
import unicodedata

from _wspolne import TestCli, ksiazka

nfd = lambda t: unicodedata.normalize('NFD', t)


class T102(TestCli):
    KSIAZKI = [ksiazka(1, nfd('Przedwiośnie'), nfd('Stefan Żeromski'), 1924),
               ksiazka(2, 'Ziele na kraterze', 'Melchior Wańkowicz', 1951),
               ksiazka(3, 'Lalka', 'Bolesław Prus', 1890)]

    def test_dane_nfd_zapytanie_nfc(self):
        self.assertEqual(self.linie('szukaj', '--autor', 'żerom')[0][:4], '[1] ')
        self.assertEqual(len(self.linie('szukaj', '--autor', 'ŻEROMSKI')), 1)
        self.assertEqual(len(self.linie('szukaj', '--tytul', 'wiośn')), 1)

    def test_dane_nfc_zapytanie_nfd(self):
        self.assertEqual(self.linie('szukaj', '--autor', nfd('Wańk')), ['[2] Ziele na kraterze — Melchior Wańkowicz (1951)'])
        self.assertEqual(self.linie('szukaj', '--autor', 'prus'), ['[3] Lalka — Bolesław Prus (1890)'])

    def test_dodaj_zapisuje_nfc(self):
        self.linie('dodaj', '--tytul', nfd('Śluby panieńskie'), '--autor', nfd('Aleksander Fredro'), '--rok', '1833')
        nowa = self.ksiazki()[-1]
        self.assertEqual(nowa['tytul'], 'Śluby panieńskie')
        self.assertTrue(unicodedata.is_normalized('NFC', nowa['tytul']))

    def test_import_zapisuje_nfc(self):
        self.linie('import', self.csv('n.csv', nfd('tytul,autor,rok\nŻywoty panów polskich,Mikołaj Rej,1562\n')))
        nowa = self.ksiazki()[-1]
        self.assertEqual((nowa['tytul'], nowa['autor']), ('Żywoty panów polskich', 'Mikołaj Rej'))
        self.assertIn('Żywoty', self.dane.read_text(encoding='utf-8'))
