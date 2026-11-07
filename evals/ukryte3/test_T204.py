import csv

from _wspolne import TestCli, ksiazka


class T204(TestCli):
    def test_dni_z_konfiguracji(self):
        self.zapisz_dane([ksiazka(1, 'Lalka', 'Bolesław Prus', 1890, 'Ola', '2024-02-25')])
        self.assertEqual(self.linie('przetrzymane', '--dzis', '2024-03-03'), [])
        self.konfiguracja('dni_przetrzymania = 5\n')
        self.assertEqual(self.linie('przetrzymane', '--dzis', '2024-03-03'), ['[1] Lalka — Ola, 7 dni'])
        self.assertEqual(self.linie('przetrzymane', '--dzis', '2024-03-03', '--dni', '7'), [])

    def test_katalog_eksportu_wzgledem_pliku_konfiguracji(self):
        plik = self.konfiguracja('katalog_eksportu = "wyniki"\n', self.katalog / 'ustawienia')
        self.linie('--konfiguracja', str(plik), 'eksport', 'k.csv')
        cel = self.katalog / 'ustawienia' / 'wyniki' / 'k.csv'
        with open(cel, encoding='utf-8', newline='') as zrodlo:
            self.assertEqual(len(list(csv.DictReader(zrodlo))), len(self.KSIAZKI))
        inny = self.katalog / 'inny'
        self.linie('--konfiguracja', str(plik), 'eksport', 'k.csv', '--katalog-eksportu', str(inny))
        self.assertTrue((inny / 'k.csv').is_file())
