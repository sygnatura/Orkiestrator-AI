"""ISBN-13: normalizacja i cyfra kontrolna."""


def normalizuj_isbn(tekst: str) -> str:
    cyfry = tekst.replace('-', '').replace(' ', '')
    if len(cyfry) != 13 or not (cyfry.isascii() and cyfry.isdigit()):
        raise ValueError(f'ISBN musi mieć 13 cyfr: {tekst}')
    suma = sum(int(c) * (3 if i % 2 else 1) for i, c in enumerate(cyfry[:12]))
    if (10 - suma % 10) % 10 != int(cyfry[12]):
        raise ValueError(f'Błędna cyfra kontrolna ISBN: {tekst}')
    return cyfry
