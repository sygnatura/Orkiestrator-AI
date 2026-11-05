from _wspolne import TestCli


class T007(TestCli):
    def test_znacznik_na_koncu_tylko_dla_wypozyczonych(self):
        linie = self.linie('lista')
        self.assertTrue(linie[1].startswith('Przedwiośnie — Stefan Żeromski'), linie[1])
        self.assertTrue(linie[1].endswith(' [wypożyczona]'), linie[1])
        self.assertNotIn('[wypożyczona]', linie[0])

    def test_szukaj_uzywa_tego_samego_formatu(self):
        kod, wyjscie, bledy = self.uruchom('szukaj', '--autor', 'Henryk Sienkiewicz')
        self.assertEqual(kod, 0, bledy)
        self.assertTrue(wyjscie.splitlines()[0].endswith(' [wypożyczona]'))
