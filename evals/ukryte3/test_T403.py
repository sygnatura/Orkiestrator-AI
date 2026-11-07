import json

from _wspolne import TestCli


class T403(TestCli):
    def test_nieobslugiwana_wersja(self):
        for zawartosc in ({'wersja': 3, 'ksiazki': [], 'historia': [], 'rezerwacje': {}},
                          {'ksiazki': [], 'historia': [], 'rezerwacje': {}}, 'tekst', 42):
            self.dane.write_text(json.dumps(zawartosc), encoding='utf-8')
            self.przed = self.dane.read_bytes()
            for polecenie in (('lista',), ('dodaj', '--tytul', 'A', '--autor', 'B', '--rok', '2000'), ('migruj',)):
                self.assertIn('wersja', self.odmowa(*polecenie).lower(), zawartosc)
            self.assertEqual(self.pliki(), ['biblioteka.json'])
