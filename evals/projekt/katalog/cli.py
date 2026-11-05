"""Polecenia: lista, szukaj, eksport."""

import argparse
from pathlib import Path
import sys

from katalog.dane import wczytaj


def formatuj(ksiazka: dict) -> str:
    return f"{ksiazka['tytul']} — {ksiazka['autor']}"


def strona_listy(ksiazki: list[dict], strona: int, na_strone: int) -> list[dict]:
    poczatek = strona * na_strone
    return ksiazki[poczatek:poczatek + na_strone]


def polecenie_lista(args, ksiazki: list[dict]) -> int:
    if args.strona is not None:
        ksiazki = strona_listy(ksiazki, args.strona, args.na_strone)
    for ksiazka in ksiazki:
        print(formatuj(ksiazka))
    return 0


def polecenie_szukaj(args, ksiazki: list[dict]) -> int:
    for ksiazka in ksiazki:
        if ksiazka['autor'] == args.autor:
            print(formatuj(ksiazka))
    return 0


def polecenie_eksport(args, ksiazki: list[dict]) -> int:
    katalog = Path(args.katalog_eksportu)
    katalog.mkdir(parents=True, exist_ok=True)
    with open(katalog / args.nazwa, 'w', encoding='utf-8') as plik:
        for ksiazka in ksiazki:
            plik.write(f"{ksiazka['tytul']};{ksiazka['autor']}\n")
    print(f'Zapisano {len(ksiazki)} pozycji: {katalog / args.nazwa}')
    return 0


def parser() -> argparse.ArgumentParser:
    glowny = argparse.ArgumentParser(prog='katalog', description=__doc__)
    glowny.add_argument('--dane', default='dane/katalog.json', help='plik katalogu (JSON)')
    polecenia = glowny.add_subparsers(dest='polecenie', required=True)
    lista = polecenia.add_parser('lista', help='wypisz książki')
    lista.add_argument('--strona', type=int, help='numer strony (od 1)')
    lista.add_argument('--na-strone', type=int, default=5)
    lista.set_defaults(func=polecenie_lista)
    szukaj = polecenia.add_parser('szukaj', help='szukaj po autorze')
    szukaj.add_argument('--autor', required=True)
    szukaj.set_defaults(func=polecenie_szukaj)
    eksport = polecenia.add_parser('eksport', help='zapisz katalog do pliku')
    eksport.add_argument('nazwa', help='nazwa pliku w katalogu eksportu')
    eksport.add_argument('--katalog-eksportu', default='eksport')
    eksport.set_defaults(func=polecenie_eksport)
    return glowny


def main(argv=None) -> int:
    args = parser().parse_args(argv)
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8')
    return args.func(args, wczytaj(Path(args.dane)))
