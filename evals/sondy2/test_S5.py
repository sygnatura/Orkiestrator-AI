"""Sonda S5 (poza wynikiem, kategoria spoza listy regresji): wydajność na dużym katalogu (20 000 książek)."""

import time

from _wspolne import TestCli, ksiazka

LIMIT_S = 10


class S5(TestCli):
    KSIAZKI = [ksiazka(i, f'Tytuł {i:05d} ąęśź', f'Autor {i % 997} Żółć', 1500 + i % 500,
                       *(('Ola', '2026-01-01') if i % 7 == 0 else ())) for i in range(1, 20001)]

    def szybko(self, *argumenty):
        start = time.monotonic()
        self.linie(*argumenty)
        czas = time.monotonic() - start
        self.assertLess(czas, LIMIT_S, f'{argumenty}: {czas:.1f} s')

    def test_duzy_katalog(self):
        self.szybko('lista', '--sortuj', 'autor')
        self.szybko('szukaj', '--autor', 'autor 13 ')
        self.szybko('statystyki')
        self.szybko('dodaj', '--tytul', 'Nowa', '--autor', 'Ktoś', '--rok', '2000')
