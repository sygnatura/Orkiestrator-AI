"""Sonda S1 (poza wynikiem): zapis katalogu nie zmienia uprawnień pliku danych."""

import os
import stat
import unittest

from _wspolne import TestCli


@unittest.skipIf(os.name == 'nt', 'uprawnienia POSIX')
class S1(TestCli):
    def test_uprawnienia_pliku_danych_zostaja(self):
        os.chmod(self.dane, 0o640)
        self.linie('dodaj', '--tytul', 'Cyberiada', '--autor', 'Stanisław Lem', '--rok', '1965')
        self.assertEqual(stat.S_IMODE(os.stat(self.dane).st_mode), 0o640)
