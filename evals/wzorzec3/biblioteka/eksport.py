"""Eksport katalogu do CSV, bezpieczny dla arkuszy (neutralizacja formuł)."""

import csv
from pathlib import Path

from biblioteka.model import Ksiazka

KOLUMNY = ['id', 'tytul', 'autor', 'rok', 'wypozyczona_przez', 'isbn']
POCZATKI_FORMUL = ('=', '+', '-', '@', '\t', '\r')


def bezpieczne(tekst: str) -> str:
    return "'" + tekst if tekst.startswith(POCZATKI_FORMUL) else tekst


def wiersz(ksiazka: Ksiazka) -> list[str]:
    return [str(ksiazka.id), bezpieczne(ksiazka.tytul), bezpieczne(ksiazka.autor),
            '' if ksiazka.rok is None else str(ksiazka.rok), bezpieczne(ksiazka.wypozyczona_przez or ''),
            ksiazka.isbn or '']


def do_csv(ksiazki: list[Ksiazka], sciezka: Path) -> None:
    with open(sciezka, 'w', encoding='utf-8', newline='') as plik:
        zapis = csv.writer(plik)
        zapis.writerow(KOLUMNY)
        for ksiazka in ksiazki:
            zapis.writerow(wiersz(ksiazka))
