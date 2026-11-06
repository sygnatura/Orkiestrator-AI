"""Polecenia: lista, szukaj, dodaj, eksport, import."""

import argparse
from pathlib import Path
import sys

from biblioteka import __version__
from biblioteka.eksport import do_csv
from biblioteka.importer import z_csv
from biblioteka.magazyn import nastepne_id, wczytaj, zapisz
from biblioteka.model import Ksiazka
from biblioteka.wyszukiwanie import szukaj


class BladUzytkownika(Exception):
    """Błąd po stronie użytkownika: komunikat na stderr i kod wyjścia 2."""


def formatuj(ksiazka: Ksiazka) -> str:
    linia = f'[{ksiazka.id}] {ksiazka.tytul} — {ksiazka.autor}'
    if ksiazka.rok is not None:
        linia += f' ({ksiazka.rok})'
    if ksiazka.wypozyczona:
        linia += ' [wypożyczona]'
    return linia


def polecenie_lista(args, ksiazki: list[Ksiazka]) -> int:
    for ksiazka in ksiazki:
        print(formatuj(ksiazka))
    return 0


def polecenie_szukaj(args, ksiazki: list[Ksiazka]) -> int:
    if args.autor is None and args.tytul is None:
        raise BladUzytkownika('Podaj --autor albo --tytul.')
    for ksiazka in szukaj(ksiazki, autor=args.autor, tytul=args.tytul):
        print(formatuj(ksiazka))
    return 0


def polecenie_dodaj(args, ksiazki: list[Ksiazka]) -> int:
    tytul, autor = args.tytul.strip(), args.autor.strip()
    if not tytul or not autor:
        raise BladUzytkownika('Tytuł i autor nie mogą być puste.')
    nowa = Ksiazka(id=nastepne_id(ksiazki), tytul=tytul, autor=autor, rok=args.rok)
    zapisz(args.dane, [*ksiazki, nowa])
    print(f'Dodano: {formatuj(nowa)}')
    return 0


def plik_eksportu(katalog: Path, nazwa: str) -> Path:
    if not nazwa or nazwa in ('.', '..') or Path(nazwa).name != nazwa or Path(nazwa).is_absolute():
        raise BladUzytkownika(f'Nazwa pliku eksportu musi być samą nazwą pliku: {nazwa}')
    cel = katalog / nazwa
    if cel.is_symlink():
        raise BladUzytkownika(f'Plik eksportu jest dowiązaniem, odmawiam zapisu: {cel}')
    return cel


def polecenie_eksport(args, ksiazki: list[Ksiazka]) -> int:
    katalog = Path(args.katalog_eksportu)
    cel = plik_eksportu(katalog, args.nazwa)
    katalog.mkdir(parents=True, exist_ok=True)
    do_csv(ksiazki, cel)
    print(f'Zapisano {len(ksiazki)} pozycji: {cel}')
    return 0


def polecenie_import(args, ksiazki: list[Ksiazka]) -> int:
    try:
        nowe = z_csv(Path(args.plik), nastepne_id(ksiazki))
    except (OSError, KeyError, ValueError) as blad:
        raise BladUzytkownika(f'Nie można zaimportować {args.plik}: {blad}') from blad
    zapisz(args.dane, [*ksiazki, *nowe])
    print(f'Zaimportowano {len(nowe)} pozycji.')
    return 0


def parser() -> argparse.ArgumentParser:
    glowny = argparse.ArgumentParser(prog='biblioteka', description=__doc__)
    glowny.add_argument('--version', action='version', version=f'biblioteka {__version__}')
    glowny.add_argument('--dane', default='dane/biblioteka.json', help='plik katalogu (JSON)')
    polecenia = glowny.add_subparsers(dest='polecenie', required=True)

    lista = polecenia.add_parser('lista', help='wypisz książki w kolejności z pliku')
    lista.set_defaults(func=polecenie_lista)

    szukaj_ = polecenia.add_parser('szukaj', help='szukaj po autorze i/lub tytule (fragment, bez wielkości liter)')
    szukaj_.add_argument('--autor')
    szukaj_.add_argument('--tytul')
    szukaj_.set_defaults(func=polecenie_szukaj)

    dodaj = polecenia.add_parser('dodaj', help='dodaj książkę')
    dodaj.add_argument('--tytul', required=True)
    dodaj.add_argument('--autor', required=True)
    dodaj.add_argument('--rok', type=int)
    dodaj.set_defaults(func=polecenie_dodaj)

    eksport = polecenia.add_parser('eksport', help='zapisz katalog do CSV')
    eksport.add_argument('nazwa', help='nazwa pliku w katalogu eksportu')
    eksport.add_argument('--katalog-eksportu', default='eksport')
    eksport.set_defaults(func=polecenie_eksport)

    import_ = polecenia.add_parser('import', help='dopisz książki z CSV (kolumny tytul, autor, rok)')
    import_.add_argument('plik')
    import_.set_defaults(func=polecenie_import)
    return glowny


def main(argv=None) -> int:
    args = parser().parse_args(argv)
    for strumien in (sys.stdout, sys.stderr):
        if hasattr(strumien, 'reconfigure'):
            strumien.reconfigure(encoding='utf-8')
    args.dane = Path(args.dane)
    try:
        return args.func(args, wczytaj(args.dane))
    except BladUzytkownika as blad:
        print(blad, file=sys.stderr)
        return 2
