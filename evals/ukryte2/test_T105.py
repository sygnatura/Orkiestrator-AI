from _wspolne import TestCli, ksiazka


class T105(TestCli):
    KSIAZKI = [ksiazka(1, '=HYPERLINK("http://zly.example","klik")', 'Autor', 2001),
               ksiazka(2, '+48 600 100 200', '-Anonim', 2002, '@osoba', '2026-10-01'),
               ksiazka(3, '\tTabulator', '\rPowrót', 2003),
               ksiazka(4, 'Zwykły, z przecinkiem i "cudzysłowem"', 'Jan Kowalski', 2004),
               ksiazka(5, 'Rok 1984 = przyszłość', 'George Orwell', 1949)]

    def test_neutralizacja(self):
        _, wiersze = self.eksport()
        self.assertEqual(wiersze[0]['tytul'], '\'=HYPERLINK("http://zly.example","klik")')
        self.assertEqual((wiersze[1]['tytul'], wiersze[1]['autor'], wiersze[1]['wypozyczona_przez']),
                         ("'+48 600 100 200", "'-Anonim", "'@osoba"))
        self.assertEqual((wiersze[2]['tytul'], wiersze[2]['autor']), ("'\tTabulator", "'\rPowrót"))

    def test_pozostale_bez_zmian(self):
        _, wiersze = self.eksport()
        self.assertEqual(wiersze[3]['tytul'], 'Zwykły, z przecinkiem i "cudzysłowem"')
        self.assertEqual(wiersze[4]['tytul'], 'Rok 1984 = przyszłość')
        self.assertEqual([w['id'] for w in wiersze], ['1', '2', '3', '4', '5'])
        self.assertEqual(wiersze[1]['rok'], '2002')
        self.assertEqual(wiersze[0]['wypozyczona_przez'], '')
        self.assertEqual(self.dane.read_bytes(), self.przed)
