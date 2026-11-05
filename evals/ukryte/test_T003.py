from _wspolne import TestCli


class T003(TestCli):
    def tytuly(self, autor):
        return [linia.split(' — ')[0] for linia in self.linie('szukaj', '--autor', autor)]

    def test_fragment_bez_wielkosci_liter(self):
        self.assertEqual(self.tytuly('żerom'), ['Przedwiośnie', 'Ludzie bezdomni'])
        self.assertEqual(self.tytuly('ŻEROMSKI'), ['Przedwiośnie', 'Ludzie bezdomni'])
        self.assertEqual(self.tytuly('sienk'), ['Quo vadis', 'Ogniem i mieczem'])

    def test_polskie_znaki_w_srodku(self):
        self.assertEqual(self.tytuly('WŁADYSŁAW'), ['Chłopi'])

    def test_brak_wynikow(self):
        kod, wyjscie, _ = self.uruchom('szukaj', '--autor', 'Szymborska')
        self.assertEqual(kod, 0)
        self.assertEqual(wyjscie, '')
