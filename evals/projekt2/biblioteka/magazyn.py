"""Odczyt i zapis katalogu w pliku JSON (lista obiektów, UTF-8)."""

import json
from pathlib import Path

from biblioteka.model import Ksiazka


def wczytaj(sciezka: Path) -> list[Ksiazka]:
    with open(sciezka, encoding='utf-8') as plik:
        return [Ksiazka.z_slownika(dane) for dane in json.load(plik)]


def zapisz(sciezka: Path, ksiazki: list[Ksiazka]) -> None:
    with open(sciezka, 'w', encoding='utf-8') as plik:
        json.dump([k.do_slownika() for k in ksiazki], plik, ensure_ascii=False, indent=1)
        plik.write('\n')


def nastepne_id(ksiazki: list[Ksiazka]) -> int:
    return max((k.id for k in ksiazki), default=0) + 1
