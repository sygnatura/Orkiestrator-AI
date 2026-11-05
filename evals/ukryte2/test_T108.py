from datetime import date

from _wspolne import TestCli


class T108(TestCli):
    def test_wypozycz_i_zwroc(self):
        self.assertEqual(self.linie('wypozycz', '3', '--osoba', '  Jan Kowalski ', '--data', '2026-10-01'),
                         ['[3] Ludzie bezdomni — Stefan Żeromski (1900) [wypożyczona]'])
        k = self.ksiazki()[2]
        self.assertEqual((k['wypozyczona_przez'], k['data_wypozyczenia']), ('Jan Kowalski', '2026-10-01'))
        self.assertEqual(self.linie('zwroc', '3'), ['[3] Ludzie bezdomni — Stefan Żeromski (1900)'])
        k = self.ksiazki()[2]
        self.assertEqual((k['wypozyczona_przez'], k['data_wypozyczenia']), (None, None))

    def test_domyslna_data_dzisiejsza(self):
        self.linie('wypozycz', '1', '--osoba', 'Ola')
        self.assertEqual(self.ksiazki()[0]['data_wypozyczenia'], date.today().isoformat())

    def test_odmowy(self):
        self.odmowa('wypozycz', '99', '--osoba', 'Ola')
        self.odmowa('wypozycz', '1', '--osoba', '   ')
        self.odmowa('wypozycz', '1', '--osoba', 'Ola', '--data', '2026-13-01')
        self.odmowa('wypozycz', '2', '--osoba', 'Ola')
        self.odmowa('zwroc', '1')
        self.odmowa('zwroc', '99')
