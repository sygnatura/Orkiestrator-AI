from _wspolne import TestCli


class T201(TestCli):
    def test_domyslne(self):
        self.assertEqual(self.linie('konfiguracja'), ['dni_przetrzymania = 30 (domyślne)',
                                                     'format_daty = pl (domyślne)',
                                                     'katalog_eksportu = eksport (domyślne)'])

    def test_plik_obok_danych(self):
        self.konfiguracja('dni_przetrzymania = 10\nkatalog_eksportu = "exp"\n')
        self.assertEqual(self.linie('konfiguracja'), ['dni_przetrzymania = 10 (plik)', 'format_daty = pl (domyślne)',
                                                     'katalog_eksportu = exp (plik)'])

    def test_jawny_plik_i_argument(self):
        plik = self.konfiguracja('format_daty = "iso"\n', self.katalog / 'inny')
        self.assertEqual(self.linie('--konfiguracja', str(plik), 'konfiguracja')[1], 'format_daty = iso (plik)')
        self.assertEqual(self.linie('--konfiguracja', str(plik), '--format-daty', 'pl', 'konfiguracja')[1],
                         'format_daty = pl (argument)')
        self.odmowa('--konfiguracja', str(self.katalog / 'brak.toml'), 'konfiguracja')

    def test_bledy(self):
        for tekst, klucz in (('dni_przetrzymania = "10"\n', 'dni_przetrzymania'),
                             ('dni_przetrzymania = -1\n', 'dni_przetrzymania'),
                             ('dni_przetrzymania = true\n', 'dni_przetrzymania'),
                             ('format_daty = "us"\n', 'format_daty'),
                             ('kolor = "zielony"\n', 'kolor'),
                             ('katalog_eksportu = 5\n', 'katalog_eksportu')):
            self.konfiguracja(tekst)
            for polecenie in ('konfiguracja', 'lista'):
                self.assertIn(klucz, self.odmowa(polecenie), tekst)
        self.konfiguracja('to nie jest = = toml\n')
        self.odmowa('lista')
