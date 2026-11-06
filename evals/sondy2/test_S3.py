"""Sonda S3 (poza wynikiem): kopia .bak prywatnego pliku danych nie jest szerzej czytelna niż on."""

import os
import stat
import unittest

from _wspolne import TestCli


@unittest.skipIf(os.name == 'nt', 'uprawnienia POSIX')
class S3(TestCli):
    def test_bak_nie_szerzej_czytelny(self):
        os.chmod(self.dane, 0o600)
        self.linie('dodaj', '--tytul', 'Cyberiada', '--autor', 'Stanisław Lem', '--rok', '1965')
        for plik in (p for p in self.katalog.iterdir() if p != self.dane):
            self.assertEqual(stat.S_IMODE(os.stat(plik).st_mode) & 0o077, 0, plik.name)
