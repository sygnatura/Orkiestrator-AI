"""Wyszukiwanie po autorze i tytule."""

from biblioteka.model import Ksiazka


def pasuje(tekst: str, szukane: str) -> bool:
    return szukane.casefold() in tekst.casefold()


def szukaj(ksiazki: list[Ksiazka], autor: str | None = None, tytul: str | None = None) -> list[Ksiazka]:
    wynik = []
    for ksiazka in ksiazki:
        if autor is not None and not pasuje(ksiazka.autor, autor):
            continue
        if tytul is not None and not pasuje(ksiazka.tytul, tytul):
            continue
        wynik.append(ksiazka)
    return wynik
