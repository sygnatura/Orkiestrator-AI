from pathlib import Path

from _wspolne import TestCli

AWARIA = '''
import os, sys
from pathlib import Path
from biblioteka.magazyn import wczytaj, zapisz
from biblioteka.model import Ksiazka
plik = Path(sys.argv[1])
ksiazki = wczytaj(plik)
if sys.argv[2] == 'serializacja':
    ksiazki.append(Ksiazka(id=99, tytul=object(), autor='x'))
else:
    ksiazki.append(Ksiazka(id=99, tytul='Nowa', autor='x'))
    def awaria(*a, **k):
        raise OSError('symulowana awaria')
    os.replace = awaria
try:
    zapisz(plik, ksiazki)
except Exception:
    print('wyjatek')
'''


class T106(TestCli):
    def pliki(self):
        return sorted(p.name for p in self.katalog.iterdir())

    def test_kopia_poprzedniej_wersji(self):
        self.linie('dodaj', '--tytul', 'Cyberiada', '--autor', 'Stanisław Lem', '--rok', '1965')
        bak = self.katalog / 'biblioteka.json.bak'
        self.assertEqual(bak.read_bytes(), self.przed)
        po_pierwszym = self.dane.read_bytes()
        self.linie('dodaj', '--tytul', 'Solaris', '--autor', 'Stanisław Lem', '--rok', '1961')
        self.assertEqual(bak.read_bytes(), po_pierwszym)
        self.assertEqual(self.pliki(), ['biblioteka.json', 'biblioteka.json.bak'])

    def test_awaria_serializacji(self):
        kod, wyjscie, bledy = self.python(AWARIA, str(self.dane), 'serializacja')
        self.assertIn('wyjatek', wyjscie, bledy)
        self.assertEqual(self.dane.read_bytes(), self.przed)
        self.assertTrue(set(self.pliki()) <= {'biblioteka.json', 'biblioteka.json.bak'}, self.pliki())

    def test_awaria_podmiany(self):
        kod, wyjscie, bledy = self.python(AWARIA, str(self.dane), 'replace')
        self.assertIn('wyjatek', wyjscie, bledy)
        self.assertEqual(self.dane.read_bytes(), self.przed)
        self.assertTrue(set(self.pliki()) <= {'biblioteka.json', 'biblioteka.json.bak'}, self.pliki())

    def test_nowy_plik_bez_bak(self):
        nowy = self.katalog / 'nowy' / 'katalog.json'
        nowy.parent.mkdir()
        kod, _, bledy = self.python(
            'import sys\nfrom pathlib import Path\nfrom biblioteka.magazyn import zapisz, wczytaj\n'
            'from biblioteka.model import Ksiazka\nzapisz(Path(sys.argv[1]), [Ksiazka(id=1, tytul="A", autor="B")])\n'
            'print(len(wczytaj(Path(sys.argv[1]))))', str(nowy))
        self.assertEqual(kod, 0, bledy)
        self.assertEqual(sorted(p.name for p in nowy.parent.iterdir()), ['katalog.json'])
