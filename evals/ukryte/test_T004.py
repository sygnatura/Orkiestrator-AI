import csv

from _wspolne import KSIAZKI, TestCli


class T004(TestCli):
    def test_csv(self):
        cel = self.katalog / 'eksport'
        kod, _, bledy = self.uruchom('eksport', 'katalog.csv', '--katalog-eksportu', str(cel))
        self.assertEqual(kod, 0, bledy)
        with open(cel / 'katalog.csv', encoding='utf-8', newline='') as plik:
            wiersze = list(csv.reader(plik))
        self.assertEqual(wiersze[0], ['tytul', 'autor', 'rok', 'wypozyczona'])
        self.assertEqual(len(wiersze), len(KSIAZKI) + 1)
        oczekiwane = [[k['tytul'], k['autor'], '' if k['rok'] is None else str(k['rok']),
                       'tak' if k['wypozyczona'] else 'nie'] for k in KSIAZKI]
        self.assertEqual(wiersze[1:], oczekiwane)
