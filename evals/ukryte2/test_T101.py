from _wspolne import ISBN_A, ISBN_B, ISBN_C, TestCli


class T101(TestCli):
    def test_dodaj_z_isbn_zapisuje_same_cyfry(self):
        self.linie('dodaj', '--tytul', 'Solaris', '--autor', 'Stanisław Lem', '--rok', '1961',
                   '--isbn', '978-83-240-1234-3')
        self.assertEqual(self.ksiazki()[-1]['isbn'], ISBN_A)

    def test_dodaj_ze_spacjami(self):
        self.linie('dodaj', '--tytul', 'Solaris', '--autor', 'Stanisław Lem', '--rok', '1961',
                   '--isbn', '978 83 01 01234 2')
        self.assertEqual(self.ksiazki()[-1]['isbn'], ISBN_B)

    def test_bledny_isbn(self):
        for zly in ('9788324012344', '978832401234', '83-240-1234-5', '97883240123430', '978832401234X'):
            self.odmowa('dodaj', '--tytul', 'X', '--autor', 'Y', '--rok', '2000', '--isbn', zly)

    def test_bez_isbn_plik_jak_dotad(self):
        self.linie('dodaj', '--tytul', 'Cyberiada', '--autor', 'Stanisław Lem', '--rok', '1965')
        self.assertTrue(all('isbn' not in k for k in self.ksiazki()), self.ksiazki())

    def test_import_z_kolumna_isbn(self):
        plik = self.csv('n.csv', 'tytul,autor,rok,isbn\nSolaris,Stanisław Lem,1961,978-83-75-06789-7\n'
                                 'Cyberiada,Stanisław Lem,1965,\n')
        self.linie('import', plik)
        nowe = self.ksiazki()[-2:]
        self.assertEqual(nowe[0]['isbn'], ISBN_C)
        self.assertNotIn('isbn', nowe[1])

    def test_import_bez_kolumny_isbn(self):
        self.linie('import', self.csv('n.csv', 'tytul,autor,rok\nSolaris,Stanisław Lem,1961\n'))
        self.assertNotIn('isbn', self.ksiazki()[-1])

    def test_import_z_blednym_isbn_nic_nie_importuje(self):
        plik = self.csv('n.csv', f'tytul,autor,rok,isbn\nSolaris,Stanisław Lem,1961,{ISBN_C}\n'
                                 'Cyberiada,Stanisław Lem,1965,1234567890123\n')
        self.odmowa('import', plik)

    def test_eksport_kolumna_na_koncu(self):
        dane = [dict(k) for k in self.KSIAZKI]
        dane[0]['isbn'] = ISBN_A
        self.zapisz_dane(dane)
        kolumny, wiersze = self.eksport()
        self.assertEqual(kolumny, ['id', 'tytul', 'autor', 'rok', 'wypozyczona_przez', 'isbn'])
        self.assertEqual(wiersze[0]['isbn'], ISBN_A)
        self.assertEqual(wiersze[1]['isbn'], '')

    def test_szukaj_po_isbn(self):
        dane = [dict(k) for k in self.KSIAZKI]
        dane[2]['isbn'] = ISBN_B
        self.zapisz_dane(dane)
        self.assertEqual(self.linie('szukaj', '--isbn', '978-83-01-01234-2'), ['[3] Ludzie bezdomni — Stefan Żeromski (1900)'])
        self.assertEqual(self.linie('szukaj', '--isbn', ISBN_A), [])
