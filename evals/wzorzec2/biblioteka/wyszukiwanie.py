"""Wyszukiwanie po autorze, tytule i ISBN; kolejność alfabetyczna po polsku."""

import unicodedata

from biblioteka.model import Ksiazka

ALFABET = 'aąbcćdeęfghijklłmnńoóprsśtuvwxyzźż'


def nfc(tekst: str) -> str:
    return unicodedata.normalize('NFC', tekst)


def klucz_tekstu(tekst: str) -> str:
    return nfc(nfc(tekst).casefold())


def pasuje(tekst: str, szukane: str) -> bool:
    return klucz_tekstu(szukane) in klucz_tekstu(tekst)


def klucz_alfabetyczny(tekst: str) -> tuple:
    return tuple((1, ALFABET.index(znak)) if znak in ALFABET else (0, ord(znak)) for znak in klucz_tekstu(tekst))


def szukaj(ksiazki: list[Ksiazka], autor: str | None = None, tytul: str | None = None,
           isbn: str | None = None) -> list[Ksiazka]:
    wynik = []
    for ksiazka in ksiazki:
        if autor is not None and not pasuje(ksiazka.autor, autor):
            continue
        if tytul is not None and not pasuje(ksiazka.tytul, tytul):
            continue
        if isbn is not None and ksiazka.isbn != isbn:
            continue
        wynik.append(ksiazka)
    return wynik
