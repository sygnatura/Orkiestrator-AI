"""Import książek z CSV (kolumny: tytul, autor, rok, opcjonalnie isbn). Całość albo nic."""

import csv
from pathlib import Path

from biblioteka.isbn import normalizuj_isbn
from biblioteka.model import Ksiazka
from biblioteka.walidacja import sprawdz_rok, sprawdz_tekst
from biblioteka.wyszukiwanie import nfc


def z_csv(sciezka: Path, pierwsze_id: int) -> list[Ksiazka]:
    nowe = []
    with open(sciezka, encoding='utf-8', newline='') as plik:
        czytnik = csv.DictReader(plik)
        for dane in czytnik:
            try:
                tytul, autor = nfc((dane.get('tytul') or '').strip()), nfc((dane.get('autor') or '').strip())
                if not tytul or not autor:
                    raise ValueError('brak tytułu albo autora')
                sprawdz_tekst(tytul, 'tytuł'), sprawdz_tekst(autor, 'autor')
                rok_tekst = (dane.get('rok') or '').strip()
                try:
                    rok = int(rok_tekst) if rok_tekst else None
                except ValueError:
                    raise ValueError(f'rok nie jest liczbą: {rok_tekst}') from None
                isbn_tekst = (dane.get('isbn') or '').strip()
                nowe.append(Ksiazka(id=pierwsze_id + len(nowe), tytul=tytul, autor=autor, rok=sprawdz_rok(rok),
                                    isbn=normalizuj_isbn(isbn_tekst) if isbn_tekst else None))
            except ValueError as blad:
                raise ValueError(f'wiersz {czytnik.line_num}: {blad}') from None
    return nowe
