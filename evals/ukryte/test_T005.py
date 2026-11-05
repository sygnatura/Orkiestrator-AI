import os

from _wspolne import TestCli


class T005(TestCli):
    def setUp(self):
        super().setUp()
        self.eksport = self.katalog / 'eksport'
        self.eksport.mkdir()

    def odmowa(self, nazwa):
        przed = sorted(p.name for p in self.katalog.rglob('*'))
        kod, _, bledy = self.uruchom('eksport', nazwa, '--katalog-eksportu', str(self.eksport))
        self.assertEqual(kod, 2, nazwa)
        self.assertTrue(bledy.strip(), nazwa)
        self.assertEqual(sorted(p.name for p in self.katalog.rglob('*')), przed, nazwa)

    def test_wyjscie_poza_katalog(self):
        self.odmowa('../poza.csv')
        self.odmowa(os.path.join('..', '..', 'poza.csv'))

    def test_sciezka_bezwzgledna(self):
        self.odmowa(str(self.katalog / 'bezwzgledna.csv'))

    def test_podkatalog(self):
        self.odmowa('podkatalog/plik.csv')

    def test_dowiazanie(self):
        cel = self.katalog / 'cel.txt'
        cel.write_text('nie ruszać\n', encoding='utf-8')
        try:
            (self.eksport / 'link.csv').symlink_to(cel)
        except OSError as blad:
            self.skipTest(f'dowiązania niedostępne: {blad}')
        self.odmowa('link.csv')
        self.assertEqual(cel.read_text(encoding='utf-8'), 'nie ruszać\n')

    def test_zwykla_nazwa_dziala(self):
        kod, _, bledy = self.uruchom('eksport', 'dobry.csv', '--katalog-eksportu', str(self.eksport))
        self.assertEqual(kod, 0, bledy)
        self.assertTrue((self.eksport / 'dobry.csv').is_file())
