from _wspolne import KSIAZKI, TestCli


class T002(TestCli):
    def tytuly(self, *argumenty):
        return [linia.split(' — ')[0] for linia in self.linie('lista', *argumenty)]

    def test_kolejne_strony(self):
        self.assertEqual(self.tytuly('--strona', '1'), [k['tytul'] for k in KSIAZKI[0:5]])
        self.assertEqual(self.tytuly('--strona', '2'), [k['tytul'] for k in KSIAZKI[5:9]])

    def test_wlasny_rozmiar_strony(self):
        self.assertEqual(self.tytuly('--strona', '3', '--na-strone', '4'), [KSIAZKI[8]['tytul']])

    def test_strona_poza_zakresem(self):
        for strona in ('0', '3', '-1'):
            kod, wyjscie, bledy = self.uruchom('lista', '--strona', strona)
            self.assertEqual(kod, 2, strona)
            self.assertEqual(wyjscie, '', strona)
            self.assertTrue(bledy.strip(), strona)

    def test_bez_strony_wszystko(self):
        self.assertEqual(len(self.linie('lista')), len(KSIAZKI))
