from _wspolne import TestCli


class T305(TestCli):
    def test_zwrot_z_kolejka(self):
        self.linie('rezerwuj', '2', '--osoba', 'Ala')
        self.linie('rezerwuj', '2', '--osoba', 'Jan')
        linie = self.linie('zwroc', '2')
        self.assertEqual(linie, ['[2] Przedwiośnie — Stefan Żeromski (1924)', 'Zarezerwowana dla: Ala'])

    def test_zwrot_bez_kolejki(self):
        self.assertEqual(self.linie('zwroc', '2'), ['[2] Przedwiośnie — Stefan Żeromski (1924)'])
