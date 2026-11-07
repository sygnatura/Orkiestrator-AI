"""Odczyt i zapis katalogu w pliku JSON (lista obiektów, UTF-8). Zapis atomowy z kopią poprzedniej wersji."""

import json
import os
from pathlib import Path
import shutil
import tempfile

from biblioteka.model import Ksiazka


def wczytaj(sciezka: Path) -> list[Ksiazka]:
    with open(sciezka, encoding='utf-8') as plik:
        return [Ksiazka.z_slownika(dane) for dane in json.load(plik)]


def zapisz(sciezka: Path, ksiazki: list[Ksiazka]) -> None:
    sciezka = Path(os.path.realpath(sciezka))  # zapis przez dowiązanie zmienia cel, dowiązanie zostaje
    tekst = json.dumps([k.do_slownika() for k in ksiazki], ensure_ascii=False, indent=1) + '\n'
    deskryptor, tymczasowy = tempfile.mkstemp(prefix=f'.{sciezka.name}.', suffix='.tmp', dir=sciezka.parent)
    try:
        if sciezka.exists():  # mkstemp tworzy plik 0600 — zachowaj uprawnienia pliku danych
            os.chmod(tymczasowy, sciezka.stat().st_mode & 0o777)
        with os.fdopen(deskryptor, 'w', encoding='utf-8') as plik:
            plik.write(tekst)
            plik.flush()
            os.fsync(plik.fileno())
        if sciezka.exists():
            shutil.copy2(sciezka, sciezka.with_name(sciezka.name + '.bak'))
        os.replace(tymczasowy, sciezka)
    except BaseException:
        Path(tymczasowy).unlink(missing_ok=True)
        raise


def nastepne_id(ksiazki: list[Ksiazka]) -> int:
    return max((k.id for k in ksiazki), default=0) + 1
