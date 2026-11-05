"""Eksport katalogu do CSV."""

import csv
from pathlib import Path

from biblioteka.model import Ksiazka

KOLUMNY = ['id', 'tytul', 'autor', 'rok', 'wypozyczona_przez']


def wiersz(ksiazka: Ksiazka) -> list[str]:
    return [str(ksiazka.id), ksiazka.tytul, ksiazka.autor, '' if ksiazka.rok is None else str(ksiazka.rok),
            ksiazka.wypozyczona_przez or '']


def do_csv(ksiazki: list[Ksiazka], sciezka: Path) -> None:
    with open(sciezka, 'w', encoding='utf-8', newline='') as plik:
        zapis = csv.writer(plik)
        zapis.writerow(KOLUMNY)
        for ksiazka in ksiazki:
            zapis.writerow(wiersz(ksiazka))
