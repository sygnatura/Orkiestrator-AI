from _wspolne import TestCli


class T104(TestCli):
    def test_szczegoly(self):
        linie = self.linie('lista', '--szczegoly')
        self.assertEqual(linie[:4], ['[1] Lalka — Bolesław Prus (1890)', '    dostępna',
                                     '[2] Przedwiośnie — Stefan Żeromski (1924) [wypożyczona]',
                                     '    wypożyczona przez: Anna Nowak, od 2026-09-01'])
        self.assertEqual(linie[10:12], ['[6] Krzyżacy — Henryk Sienkiewicz (1900) [wypożyczona]',
                                        '    wypożyczona przez: Ewa Zielińska, data nieznana'])
        self.assertEqual(len(linie), 2 * len(self.KSIAZKI))

    def test_bez_flagi_bez_zmian(self):
        linie = self.linie('lista')
        self.assertEqual(len(linie), len(self.KSIAZKI))
        self.assertEqual(linie[6], '[7] Zbrodnia i kara (przekład) — Fiodor Dostojewski')

    def test_formatuj_bez_zmian(self):
        kod, wyjscie, bledy = self.python(
            'from biblioteka.cli import formatuj\nfrom biblioteka.model import Ksiazka\n'
            "print(formatuj(Ksiazka(id=2, tytul='Dziady', autor='Adam Mickiewicz', rok=1823, wypozyczona_przez='X')))")
        self.assertEqual(kod, 0, bledy)
        self.assertEqual(wyjscie.strip(), '[2] Dziady — Adam Mickiewicz (1823) [wypożyczona]')
