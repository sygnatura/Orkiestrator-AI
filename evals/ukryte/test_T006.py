from _wspolne import TestCli


class T006(TestCli):
    def test_rok_po_autorze(self):
        linie = self.linie('lista')
        self.assertTrue(linie[0].startswith('Lalka — Bolesław Prus (1890)'), linie[0])
        self.assertTrue(linie[8].startswith('Zbrodnia i kara (przekład) — Fiodor Dostojewski'), linie[8])
        self.assertNotIn('(None)', linie[8])
        self.assertEqual(linie[8].rstrip(), 'Zbrodnia i kara (przekład) — Fiodor Dostojewski')
