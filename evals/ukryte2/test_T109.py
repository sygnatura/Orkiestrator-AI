from _wspolne import TestCli, ksiazka


class T109(TestCli):
    KSIAZKI = [ksiazka(1, 'Żywoty', 'zenon Ździebło', 1562), ksiazka(2, 'Lalka', 'Bolesław Prus', 1890),
               ksiazka(3, 'Łuk', 'Łucja Lis'), ksiazka(4, 'Ślub', 'Witold Gombrowicz', 1953),
               ksiazka(5, 'Solaris', 'Stanisław Lem', 1961), ksiazka(6, 'szewcy', 'Stanisław Ignacy Witkiewicz', 1934),
               ksiazka(7, 'Źdźbło', 'Ala Ćma', 1890), ksiazka(8, 'Zbrodnia', 'Fiodor Dostojewski'),
               ksiazka(9, 'Ludzie', 'Ćwierć Ąbc', 1900), ksiazka(10, 'Ćma', 'Celina Ab', 1890)]

    def ids(self, *argumenty):
        return [int(linia[1:linia.index(']')]) for linia in self.linie('lista', *argumenty)]

    def test_tytul_po_polsku(self):
        self.assertEqual(self.ids('--sortuj', 'tytul'), [10, 2, 9, 3, 5, 6, 4, 8, 7, 1])

    def test_autor_po_polsku(self):
        self.assertEqual(self.ids('--sortuj', 'autor'), [7, 2, 10, 9, 8, 3, 6, 5, 4, 1])

    def test_rok_bez_roku_na_koncu_stabilnie(self):
        self.assertEqual(self.ids('--sortuj', 'rok'), [1, 2, 7, 10, 9, 6, 4, 5, 3, 8])

    def test_zla_wartosc(self):
        self.odmowa('lista', '--sortuj', 'id')
