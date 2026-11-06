from datetime import date

from _wspolne import TestCli


class T107(TestCli):
    def dodaj(self, rok):
        return ('dodaj', '--tytul', 'Nowa', '--autor', 'Autor', '--rok', str(rok))

    def test_zakres_przy_dodawaniu(self):
        for rok in (1449, date.today().year + 1, 0, -1900):
            self.odmowa(*self.dodaj(rok))
        self.linie(*self.dodaj(1450))
        self.linie(*self.dodaj(date.today().year))
        self.assertEqual([k['rok'] for k in self.ksiazki()[-2:]], [1450, date.today().year])

    def test_import_spoza_zakresu_z_numerem_wiersza(self):
        plik = self.csv('n.csv', f'tytul,autor,rok\nA,B,1900\nC,D,{date.today().year + 5}\nE,F,1950\n')
        self.assertIn('wiersz 3', self.odmowa('import', plik))
        plik = self.csv('m.csv', 'tytul,autor,rok\nA,B,1900\nC,D,1901\nE,F,tysiąc\n')
        self.assertIn('wiersz 4', self.odmowa('import', plik))

    def test_ksiazki_bez_roku_dalej_dzialaja(self):
        self.assertIn('[7] Zbrodnia i kara (przekład) — Fiodor Dostojewski', self.linie('lista'))
