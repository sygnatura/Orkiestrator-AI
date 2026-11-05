"""T-006 i T-007 zmieniają tę samą funkcję: po scaleniu obu linia ma rok i znacznik."""

from _wspolne import TestCli


class Kolizja(TestCli):
    def test_rok_i_znacznik_razem(self):
        linie = self.linie('lista')
        self.assertEqual(linie[0], 'Lalka — Bolesław Prus (1890)')
        self.assertEqual(linie[1], 'Przedwiośnie — Stefan Żeromski (1924) [wypożyczona]')
        self.assertEqual(linie[8], 'Zbrodnia i kara (przekład) — Fiodor Dostojewski')
