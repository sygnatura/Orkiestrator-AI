"""Import książek z CSV (kolumny: tytul, autor, rok)."""

import csv
from pathlib import Path

from biblioteka.model import Ksiazka


def z_csv(sciezka: Path, pierwsze_id: int) -> list[Ksiazka]:
    nowe = []
    with open(sciezka, encoding='utf-8', newline='') as plik:
        for numer, dane in enumerate(csv.DictReader(plik)):
            rok = dane.get('rok') or None
            nowe.append(Ksiazka(id=pierwsze_id + numer, tytul=dane['tytul'].strip(), autor=dane['autor'].strip(),
                                rok=int(rok) if rok else None))
    return nowe
