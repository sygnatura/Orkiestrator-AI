"""Odczyt i zapis katalogu: lista słowników {tytul, autor, rok, wypozyczona} w pliku JSON (UTF-8)."""

import json
from pathlib import Path


def wczytaj(sciezka: Path) -> list[dict]:
    with open(sciezka, encoding='utf-8') as plik:
        return json.load(plik)


def zapisz(sciezka: Path, ksiazki: list[dict]) -> None:
    with open(sciezka, 'w', encoding='utf-8') as plik:
        json.dump(ksiazki, plik, ensure_ascii=False, indent=1)
        plik.write('\n')
