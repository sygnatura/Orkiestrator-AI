from _wspolne import TestCli, ksiazka


class T203(TestCli):
    def test_wypozycz_z_data_pl(self):
        self.linie('wypozycz', '1', '--osoba', 'Ola', '--data', '01.10.2026')
        self.assertEqual(self.ksiazki()[0]['data_wypozyczenia'], '2026-10-01')

    def test_przetrzymane_dzis_w_obu_formatach(self):
        self.zapisz_dane([ksiazka(1, 'Lalka', 'Bolesław Prus', 1890, 'Ola', '2024-02-01')])
        self.assertEqual(self.linie('przetrzymane', '--dzis', '03.03.2024'), ['[1] Lalka — Ola, 31 dni'])
        self.assertEqual(self.linie('przetrzymane', '--dzis', '2024-03-03'), ['[1] Lalka — Ola, 31 dni'])

    def test_bledne_daty(self):
        for zla in ('31.02.2026', '1.2.2026', '2026/10/01', '01-10-2026', '2026-13-01'):
            self.odmowa('wypozycz', '1', '--osoba', 'Ola', '--data', zla)
            self.odmowa('przetrzymane', '--dzis', zla)
