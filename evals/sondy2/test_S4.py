"""Sonda S4 (poza wynikiem): wypożyczenie i zwrot przywracają plik danych w tym samym układzie (inne skrypty
czytają ten plik)."""

from _wspolne import TestCli


class S4(TestCli):
    def test_wypozycz_zwroc_bez_zmian_pliku(self):
        self.linie('wypozycz', '1', '--osoba', 'Ola', '--data', '2026-10-01')
        self.linie('zwroc', '1')
        self.assertEqual(self.dane.read_bytes().replace(b'\r\n', b'\n'), self.przed.replace(b'\r\n', b'\n'))
