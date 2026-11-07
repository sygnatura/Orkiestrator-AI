from datetime import date

from _wspolne import TestCli


class T301(TestCli):
    def test_zdarzenia_w_kolejnosci_dat(self):
        self.linie('wypozycz', '1', '--osoba', 'Ola', '--data', '2026-10-01')
        self.linie('zwroc', '1')
        self.linie('wypozycz', '1', '--osoba', 'Jan', '--data', '2026-09-01')
        dzis = date.today().isoformat()
        self.assertEqual(self.linie('--format-daty', 'iso', 'historia', '1'), [
            '2026-09-01 — wypożyczenie — Jan', '2026-10-01 — wypożyczenie — Ola', f'{dzis} — zwrot — Ola'])

    def test_rowne_daty_w_kolejnosci_zapisu(self):
        self.linie('wypozycz', '3', '--osoba', 'Ola', '--data', '2026-10-01')
        self.linie('zwroc', '3', '--data', '2026-10-01')
        self.linie('wypozycz', '3', '--osoba', 'Jan', '--data', '2026-10-01')
        self.assertEqual(self.linie('--format-daty', 'iso', 'historia', '3'), [
            '2026-10-01 — wypożyczenie — Ola', '2026-10-01 — zwrot — Ola', '2026-10-01 — wypożyczenie — Jan'])

    def test_nieudane_polecenie_nic_nie_zapisuje(self):
        self.uruchom('wypozycz', '2', '--osoba', 'Ola', '--data', '2026-10-01')
        self.uruchom('zwroc', '1')
        self.assertEqual(self.linie('historia', '2'), [])
        self.assertEqual(self.linie('historia', '1'), [])

    def test_nieznane_id(self):
        self.odmowa('historia', '99')
