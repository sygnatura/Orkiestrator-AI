from _wspolne import TestCli


class T110(TestCli):
    def test_filtr_autora(self):
        self.assertEqual(self.linie('lista', '--autor', 'SIENK'), [
            '[4] Quo vadis — Henryk Sienkiewicz (1896) [wypożyczona]',
            '[5] Ogniem i mieczem — Henryk Sienkiewicz (1884)',
            '[6] Krzyżacy — Henryk Sienkiewicz (1900) [wypożyczona]'])
        self.assertEqual(len(self.linie('lista', '--autor', 'żerom')), 2)

    def test_brak_wynikow(self):
        kod, wyjscie, _ = self.uruchom('lista', '--autor', 'Tolkien')
        self.assertEqual((kod, wyjscie), (0, ''))
