from _wspolne import TestCli, ksiazka


class T112(TestCli):
    KSIAZKI = ([ksiazka(1, 'Dziady', 'Adam Mickiewicz', 1900, 'Ola', '2026-10-01'),
                ksiazka(2, 'Ballady', 'adam mickiewicz', 1901), ksiazka(3, 'Lalka', 'Bolesław Prus', 1900),
                ksiazka(4, 'Emancypantki', 'Bolesław Prus', 1900)]
               + [ksiazka(i, f'Tom {i}', 'Anonim') for i in range(5, 17)])

    def test_statystyki_z_zaokragleniem_polowek(self):
        self.assertEqual(self.linie('statystyki'), [
            'Książek: 16',
            'Wypożyczonych: 1 (6,3%)',
            'Autorów: 3',
            'Średni rok wydania: 1900,3',
            'Najstarsza: [1] Dziady — Adam Mickiewicz (1900) [wypożyczona]'])

    def test_pusty_katalog(self):
        self.zapisz_dane([])
        self.assertEqual(self.linie('statystyki'), [
            'Książek: 0', 'Wypożyczonych: 0 (0,0%)', 'Autorów: 0', 'Średni rok wydania: brak', 'Najstarsza: brak'])

    def test_bez_lat(self):
        self.zapisz_dane([ksiazka(1, 'A', 'B'), ksiazka(2, 'C', 'D', None, 'Ola', '2026-01-01')])
        self.assertEqual(self.linie('statystyki')[1:], [
            'Wypożyczonych: 1 (50,0%)', 'Autorów: 2', 'Średni rok wydania: brak', 'Najstarsza: brak'])
