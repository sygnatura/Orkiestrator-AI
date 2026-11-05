from _wspolne import PROJEKT, TestCli
import re


class T001(TestCli):
    def test_wersja(self):
        wersja = re.search(r"__version__\s*=\s*['\"]([^'\"]+)", (PROJEKT / 'katalog/__init__.py').read_text()).group(1)
        kod, wyjscie, _ = self.uruchom('--version', dane=False)
        self.assertEqual(kod, 0)
        self.assertEqual(wyjscie.strip(), f'katalog {wersja}')
