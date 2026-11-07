from _wspolne import TestCli


class T303(TestCli):
    def test_kolejka(self):
        self.assertEqual(self.linie('rezerwuj', '2', '--osoba', ' Ala '), ['Zarezerwowano: Ala, pozycja 1'])
        self.assertEqual(self.linie('rezerwuj', '2', '--osoba', 'Jan'), ['Zarezerwowano: Jan, pozycja 2'])
        self.assertEqual(self.linie('rezerwacje', '2'), ['1. Ala', '2. Jan'])
        self.assertEqual(self.linie('rezerwacje', '1'), [])

    def test_odmowy(self):
        self.linie('rezerwuj', '2', '--osoba', 'Ala')
        przed = self.stan_plikow()
        self.odmowa('rezerwuj', '2', '--osoba', 'Ala')
        self.odmowa('rezerwuj', '2', '--osoba', '   ')
        self.odmowa('rezerwuj', '99', '--osoba', 'Ala')
        self.odmowa('rezerwacje', '99')
        self.assertEqual(self.stan_plikow(), przed)
