"""Polecenia: lista, szukaj, eksport."""

import argparse
import csv
from pathlib import Path
import sys

from katalog import __version__
from katalog.dane import wczytaj


def formatuj(ksiazka: dict) -> str:
    linia = f"{ksiazka['tytul']} — {ksiazka['autor']}"
    if ksiazka.get('rok') is not None:
        linia += f" ({ksiazka['rok']})"
    if ksiazka.get('wypozyczona'):
        linia += ' [wypożyczona]'
    return linia


def blad(komunikat: str) -> int:
    print(komunikat, file=sys.stderr)
    return 2


def polecenie_lista(args, ksiazki: list[dict]) -> int:
    if args.strona is not None:
        stron = -(-len(ksiazki) // args.na_strone)
        if not 1 <= args.strona <= stron:
            return blad(f'Nie ma strony {args.strona} (stron: {stron}).')
        poczatek = (args.strona - 1) * args.na_strone
        ksiazki = ksiazki[poczatek:poczatek + args.na_strone]
    for ksiazka in ksiazki:
        print(formatuj(ksiazka))
    return 0


def polecenie_szukaj(args, ksiazki: list[dict]) -> int:
    szukane = args.autor.casefold()
    for ksiazka in ksiazki:
        if szukane in ksiazka['autor'].casefold():
            print(formatuj(ksiazka))
    return 0


def polecenie_eksport(args, ksiazki: list[dict]) -> int:
    nazwa = args.nazwa
    if not nazwa or Path(nazwa).name != nazwa or nazwa in ('.', '..') or Path(nazwa).is_absolute():
        return blad(f'Niedozwolona nazwa pliku eksportu: {nazwa}')
    katalog = Path(args.katalog_eksportu)
    cel = katalog / nazwa
    if cel.is_symlink():
        return blad(f'Plik eksportu jest dowiązaniem: {cel}')
    katalog.mkdir(parents=True, exist_ok=True)
    with open(cel, 'w', encoding='utf-8', newline='') as plik:
        zapis = csv.writer(plik)
        zapis.writerow(['tytul', 'autor', 'rok', 'wypozyczona'])
        for ksiazka in ksiazki:
            rok = '' if ksiazka.get('rok') is None else ksiazka['rok']
            zapis.writerow([ksiazka['tytul'], ksiazka['autor'], rok, 'tak' if ksiazka.get('wypozyczona') else 'nie'])
    print(f'Zapisano {len(ksiazki)} pozycji: {cel}')
    return 0


def parser() -> argparse.ArgumentParser:
    glowny = argparse.ArgumentParser(prog='katalog', description=__doc__)
    glowny.add_argument('--version', action='version', version=f'katalog {__version__}')
    glowny.add_argument('--dane', default='dane/katalog.json', help='plik katalogu (JSON)')
    polecenia = glowny.add_subparsers(dest='polecenie', required=True)
    lista = polecenia.add_parser('lista', help='wypisz książki')
    lista.add_argument('--strona', type=int, help='numer strony (od 1)')
    lista.add_argument('--na-strone', type=int, default=5)
    lista.set_defaults(func=polecenie_lista)
    szukaj = polecenia.add_parser('szukaj', help='szukaj po autorze')
    szukaj.add_argument('--autor', required=True)
    szukaj.set_defaults(func=polecenie_szukaj)
    eksport = polecenia.add_parser('eksport', help='zapisz katalog do pliku CSV')
    eksport.add_argument('nazwa', help='nazwa pliku w katalogu eksportu')
    eksport.add_argument('--katalog-eksportu', default='eksport')
    eksport.set_defaults(func=polecenie_eksport)
    return glowny


def main(argv=None) -> int:
    args = parser().parse_args(argv)
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8')
    return args.func(args, wczytaj(Path(args.dane)))
