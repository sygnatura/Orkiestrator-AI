"""Regresja: kluczowe zachowania z E2 działają po E3–E5, w starym formacie i w v2."""

import unicodedata

from _wspolne import ISBN_A, TestCli


class Regresja(TestCli):
    def sprawdz(self):
        self.assertEqual(len(self.linie('szukaj', '--autor', unicodedata.normalize('NFD', 'żerom'))), 2)
        self.linie('dodaj', '--tytul', '=Formuła', '--autor', 'Ktoś', '--rok', '2001', '--isbn', '978-83-240-1234-3')
        self.assertEqual(len(self.linie('szukaj', '--isbn', ISBN_A)), 1)
        _, wiersze = self.eksport()
        self.assertEqual((wiersze[-1]['tytul'], wiersze[-1]['isbn']), ("'=Formuła", ISBN_A))
        self.assertEqual(self.linie('lista', '--autor', 'sienk', '--tylko-dostepne', '--sortuj', 'rok'),
                         ['[5] Ogniem i mieczem — Henryk Sienkiewicz (1884)'])
        self.assertEqual(self.linie('przetrzymane', '--dzis', '2026-11-05', '--dni', '30'),
                         ['[2] Przedwiośnie — Anna Nowak, 65 dni', '[6] Krzyżacy — Ewa Zielińska, brak daty'])
        self.assertEqual(self.linie('statystyki')[:2], ['Książek: 9', 'Wypożyczonych: 3 (33,3%)'])
        self.assertNotIn('isbn', self.ksiazki()[0])

    def test_stary_format(self):
        self.sprawdz()

    def test_v2(self):
        if self.uruchom('migruj')[0] != 0:
            self.skipTest('brak migruj (E5) — regresja v2 nie dotyczy')
        self.sprawdz()
