from _wspolne import TestCli, ksiazka


class T103(TestCli):
    KSIAZKI = [ksiazka(1, 'Lalka', 'Bolesław Prus', 1890, 'Ola', '2024-02-02'),
               ksiazka(2, 'Chłopi', 'Władysław Reymont', 1904, 'Jan', '2024-02-01'),
               ksiazka(3, 'Wesele', 'Stanisław Wyspiański', 1901, 'Ewa', None),
               ksiazka(4, 'Dziady', 'Adam Mickiewicz', 1823),
               ksiazka(5, 'Granica', 'Zofia Nałkowska', 1935, 'Piotr', '2024-01-02'),
               ksiazka(6, 'Solaris', 'Stanisław Lem', 1961, 'Ala', '2024-01-02'),
               ksiazka(7, 'Medaliony', 'Zofia Nałkowska', 1946, 'Kuba', None),
               ksiazka(8, 'Ferdydurke', 'Witold Gombrowicz', 1937, 'Iza', '2024-03-04')]

    def test_granica_30_dni_w_roku_przestepnym(self):
        self.assertEqual(self.linie('przetrzymane', '--dzis', '2024-03-03'), [
            '[5] Granica — Piotr, 61 dni',
            '[6] Solaris — Ala, 61 dni',
            '[2] Chłopi — Jan, 31 dni',
            '[3] Wesele — Ewa, brak daty',
            '[7] Medaliony — Kuba, brak daty',
        ])

    def test_wlasny_limit_dni(self):
        linie = self.linie('przetrzymane', '--dzis', '2024-03-03', '--dni', '0')
        self.assertIn('[1] Lalka — Ola, 30 dni', linie)
        self.assertNotIn('Ferdydurke', '\n'.join(linie))
        self.assertEqual(self.linie('przetrzymane', '--dzis', '2024-03-03', '--dni', '61')[:1],
                         ['[3] Wesele — Ewa, brak daty'])

    def test_brak_przetrzymanych(self):
        self.zapisz_dane([ksiazka(1, 'Lalka', 'Bolesław Prus', 1890, 'Ola', '2024-02-02'),
                          ksiazka(2, 'Dziady', 'Adam Mickiewicz', 1823)])
        kod, wyjscie, _ = self.uruchom('przetrzymane', '--dzis', '2024-02-10')
        self.assertEqual((kod, wyjscie), (0, ''))

    def test_bledne_parametry(self):
        for argumenty in (('--dzis', '2024-02-30'), ('--dzis', '3.03.2024'), ('--dni', '-1')):
            self.odmowa('przetrzymane', *argumenty)
