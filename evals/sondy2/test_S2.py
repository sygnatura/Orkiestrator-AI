"""Sonda S2 (poza wynikiem): zapis przez dowiązanie symboliczne zmienia cel i zostawia dowiązanie."""

import json

from _wspolne import TestCli


class S2(TestCli):
    def test_dowiazanie_zostaje(self):
        cel = self.katalog / 'prawdziwe' / 'biblioteka.json'
        cel.parent.mkdir()
        cel.write_bytes(self.dane.read_bytes())
        self.dane.unlink()
        try:
            self.dane.symlink_to(cel)
        except OSError as blad:
            self.skipTest(f'dowiązania niedostępne: {blad}')
        self.linie('dodaj', '--tytul', 'Cyberiada', '--autor', 'Stanisław Lem', '--rok', '1965')
        self.assertTrue(self.dane.is_symlink())
        self.assertEqual(json.loads(cel.read_text(encoding='utf-8'))[-1]['tytul'], 'Cyberiada')
