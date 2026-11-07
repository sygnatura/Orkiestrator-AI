from _wspolne import TestCli


class T304(TestCli):
    def test_tylko_pierwsza_osoba_z_kolejki(self):
        self.linie('rezerwuj', '1', '--osoba', 'Ala')
        self.linie('rezerwuj', '1', '--osoba', 'Ola')
        przed = self.stan_plikow()
        self.assertIn('Ala', self.odmowa('wypozycz', '1', '--osoba', 'Ola', '--data', '2026-10-01'))
        self.assertEqual(self.stan_plikow(), przed)
        self.linie('wypozycz', '1', '--osoba', ' Ala ', '--data', '2026-10-01')
        self.assertEqual(self.ksiazki()[0]['wypozyczona_przez'], 'Ala')
        self.assertEqual(self.linie('rezerwacje', '1'), ['1. Ola'])

    def test_bez_kolejki_bez_zmian(self):
        self.linie('wypozycz', '3', '--osoba', 'Kto', '--data', '2026-10-01')
        self.assertEqual(self.ksiazki()[2]['wypozyczona_przez'], 'Kto')
