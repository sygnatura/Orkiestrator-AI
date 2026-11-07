from _wspolne import TestCli


class T402(TestCli):
    def przygotuj_stary_stan(self):
        self.linie('wypozycz', '1', '--osoba', 'Ola', '--data', '2026-10-01')
        self.linie('zwroc', '1', '--data', '2026-10-03')
        self.linie('rezerwuj', '2', '--osoba', 'Ala')
        self.linie('rezerwuj', '2', '--osoba', 'Jan')
        self.linie('rezerwuj', '5', '--osoba', 'Ewa')

    def test_migracja(self):
        self.przygotuj_stary_stan()
        historia = self.linie('historia', '1')
        self.assertEqual(self.linie('migruj'), ['Zmigrowano do wersji 2: 8 książek, 2 zdarzeń, 3 rezerwacji'])
        dane = self.plik()
        self.assertEqual((sorted(dane), dane['wersja'], len(dane['ksiazki'])),
                         (['historia', 'ksiazki', 'rezerwacje', 'wersja'], 2, 8))
        nazwy = self.pliki()
        self.assertIn('biblioteka.historia.json.v1.bak', nazwy)
        self.assertIn('biblioteka.rezerwacje.json.v1.bak', nazwy)
        self.assertNotIn('biblioteka.historia.json', nazwy)
        self.assertNotIn('biblioteka.rezerwacje.json', nazwy)
        self.assertEqual(self.linie('historia', '1'), historia)
        self.assertEqual(self.linie('rezerwacje', '2'), ['1. Ala', '2. Jan'])

    def test_juz_v2(self):
        self.przygotuj_stary_stan()
        self.linie('migruj')
        przed = self.dane.read_bytes()
        self.assertEqual(self.linie('migruj'), ['Plik jest już w wersji 2.'])
        self.assertEqual(self.dane.read_bytes(), przed)

    def test_migracja_bez_plikow_pobocznych(self):
        self.assertEqual(self.linie('migruj'), ['Zmigrowano do wersji 2: 8 książek, 0 zdarzeń, 0 rezerwacji'])
        self.assertEqual(self.plik()['wersja'], 2)
