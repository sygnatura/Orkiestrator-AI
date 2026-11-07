import json

from _wspolne import ISBN_A, TestCli, ksiazka


class T401(TestCli):
    def v2(self, ksiazki, historia=(), rezerwacje=None):
        self.dane.write_text(json.dumps({'wersja': 2, 'ksiazki': ksiazki, 'historia': list(historia),
                                         'rezerwacje': rezerwacje or {}}, ensure_ascii=False), encoding='utf-8')
        self.przed = self.dane.read_bytes()

    def test_v2_czytany_i_zapisywany_bez_plikow_pobocznych(self):
        self.v2(self.KSIAZKI)
        self.assertEqual(len(self.linie('lista')), len(self.KSIAZKI))
        self.linie('rezerwuj', '2', '--osoba', 'Ala')
        self.linie('zwroc', '2', '--data', '2026-10-01')
        self.linie('wypozycz', '2', '--osoba', 'Ala', '--data', '2026-10-02')
        self.linie('dodaj', '--tytul', 'Nowa', '--autor', 'Ktoś', '--rok', '2000')
        dane = self.plik()
        self.assertEqual(sorted(dane), ['historia', 'ksiazki', 'rezerwacje', 'wersja'])
        self.assertEqual(dane['wersja'], 2)
        self.assertNotIn('isbn', dane['ksiazki'][-1])
        self.assertEqual(self.pliki(), ['biblioteka.json', 'biblioteka.json.bak'])
        self.assertEqual(self.linie('--format-daty', 'iso', 'historia', '2'),
                         ['2026-10-01 — zwrot — Anna Nowak', '2026-10-02 — wypożyczenie — Ala'])
        self.assertEqual(self.linie('rezerwacje', '2'), [])

    def test_v2_z_isbn_i_wyszukiwaniem(self):
        self.v2([ksiazka(1, 'Solaris', 'Stanisław Lem', 1961, isbn=ISBN_A)])
        self.assertEqual(self.linie('szukaj', '--isbn', ISBN_A), ['[1] Solaris — Stanisław Lem (1961)'])

    def test_stary_format_zostaje_stary(self):
        self.linie('wypozycz', '1', '--osoba', 'Ola', '--data', '2026-10-01')
        self.linie('rezerwuj', '1', '--osoba', 'Jan')
        self.assertIsInstance(self.plik(), list)

    def test_api_listy_bez_zmian(self):
        kod, wyjscie, bledy = self.python(
            'import sys\nfrom pathlib import Path\nfrom biblioteka.magazyn import wczytaj, zapisz\n'
            'p = Path(sys.argv[1]); k = wczytaj(p); zapisz(p, k); print(type(__import__("json").loads(p.read_text('
            'encoding="utf-8"))).__name__, len(wczytaj(p)))', str(self.dane))
        self.assertEqual((kod, wyjscie.split()), (0, ['list', str(len(self.KSIAZKI))]), bledy)
