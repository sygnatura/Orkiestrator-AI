from _wspolne import TestCli


class T302(TestCli):
    def test_data_zwrotu(self):
        self.linie('wypozycz', '1', '--osoba', 'Ola', '--data', '2026-10-01')
        self.linie('zwroc', '1', '--data', '05.10.2026')
        self.assertEqual(self.linie('--format-daty', 'iso', 'historia', '1')[-1], '2026-10-05 — zwrot — Ola')
        self.assertIsNone(self.ksiazki()[0]['wypozyczona_przez'])

    def test_zwrot_przed_wypozyczeniem(self):
        self.linie('wypozycz', '1', '--osoba', 'Ola', '--data', '2026-10-01')
        przed = self.stan_plikow()
        self.odmowa('zwroc', '1', '--data', '2026-09-30')
        self.odmowa('zwroc', '1', '--data', '31.09.2026')
        self.assertEqual(self.stan_plikow(), przed)
