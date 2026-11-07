from _wspolne import TestCli


class T202(TestCli):
    def szczegol(self, *opcje):
        return self.linie(*opcje, 'lista', '--szczegoly')[3]

    def test_domyslny_format_ustalony_z_wlascicielem(self):
        self.assertEqual(self.szczegol(), '    wypożyczona przez: Anna Nowak, od 01.09.2026')

    def test_opcja_i_plik(self):
        self.assertEqual(self.szczegol('--format-daty', 'iso'), '    wypożyczona przez: Anna Nowak, od 2026-09-01')
        self.konfiguracja('format_daty = "iso"\n')
        self.assertEqual(self.szczegol(), '    wypożyczona przez: Anna Nowak, od 2026-09-01')
        self.assertEqual(self.szczegol('--format-daty', 'pl'), '    wypożyczona przez: Anna Nowak, od 01.09.2026')

    def test_plik_danych_w_iso(self):
        self.linie('--format-daty', 'pl', 'wypozycz', '1', '--osoba', 'Ola', '--data', '2026-10-01')
        self.assertEqual(self.ksiazki()[0]['data_wypozyczenia'], '2026-10-01')

    def test_zla_wartosc(self):
        self.odmowa('--format-daty', 'us', 'lista')
