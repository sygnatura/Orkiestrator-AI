"""Ciągłość między etapami: decyzje i ustawienia z E3 obowiązują w poleceniach z E4 i E5."""

from _wspolne import TestCli, ksiazka


class Ciaglosc(TestCli):
    def test_historia_w_formacie_ustalonym_w_E3(self):
        self.linie('wypozycz', '1', '--osoba', 'Ola', '--data', '2026-10-01')
        self.assertEqual(self.linie('historia', '1'), ['01.10.2026 — wypożyczenie — Ola'])

    def test_format_z_konfiguracji_w_historii(self):
        self.konfiguracja('format_daty = "iso"\n')
        self.linie('wypozycz', '1', '--osoba', 'Ola', '--data', '01.10.2026')
        self.assertEqual(self.linie('historia', '1'), ['2026-10-01 — wypożyczenie — Ola'])
        self.assertEqual(self.linie('lista', '--szczegoly')[1], '    wypożyczona przez: Ola, od 2026-10-01')

    def test_po_migracji_wszystko_dziala(self):
        self.zapisz_dane([ksiazka(1, 'Lalka', 'Bolesław Prus', 1890), ksiazka(2, 'Dziady', 'Adam Mickiewicz', 1823)])
        self.konfiguracja('dni_przetrzymania = 3\n')
        self.linie('rezerwuj', '1', '--osoba', 'Ala')
        self.linie('rezerwuj', '1', '--osoba', 'Jan')
        self.linie('migruj')
        self.odmowa('wypozycz', '1', '--osoba', 'Jan', '--data', '2026-10-01')
        self.linie('wypozycz', '1', '--osoba', 'Ala', '--data', '01.10.2026')
        self.assertEqual(self.linie('przetrzymane', '--dzis', '05.10.2026'), ['[1] Lalka — Ala, 4 dni'])
        self.assertEqual(self.linie('zwroc', '1', '--data', '2026-10-06')[1:], ['Zarezerwowana dla: Jan'])
        self.assertEqual(self.linie('historia', '1'), ['01.10.2026 — wypożyczenie — Ala', '06.10.2026 — zwrot — Ala'])
        self.assertEqual(self.plik()['wersja'], 2)
