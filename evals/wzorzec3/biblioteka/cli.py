"""Polecenia: lista, szukaj, dodaj, eksport, import, wypozycz, zwroc, przetrzymane, statystyki, konfiguracja,
historia, rezerwuj, rezerwacje, migruj."""

import argparse
from datetime import date
from decimal import Decimal, ROUND_HALF_UP
from pathlib import Path
import sys

from biblioteka import __version__
from biblioteka.eksport import do_csv
from biblioteka.importer import z_csv
from biblioteka.isbn import normalizuj_isbn
from biblioteka.konfiguracja import BladKonfiguracji, wczytaj_konfiguracje
from biblioteka.magazyn import nastepne_id
from biblioteka.model import Ksiazka
from biblioteka.stan import BladWersji, migruj, wczytaj_stan, zapisz_stan
from biblioteka.walidacja import formatuj_date, sprawdz_date, sprawdz_rok, sprawdz_tekst
from biblioteka.wyszukiwanie import klucz_alfabetyczny, klucz_tekstu, nfc, pasuje, szukaj


class BladUzytkownika(Exception):
    """Błąd po stronie użytkownika: komunikat na stderr i kod wyjścia 2."""


def formatuj(ksiazka: Ksiazka) -> str:
    linia = f'[{ksiazka.id}] {ksiazka.tytul} — {ksiazka.autor}'
    if ksiazka.rok is not None:
        linia += f' ({ksiazka.rok})'
    if ksiazka.wypozyczona:
        linia += ' [wypożyczona]'
    return linia


def szczegoly(ksiazka: Ksiazka, format_daty: str = 'iso') -> str:
    if not ksiazka.wypozyczona:
        return '    dostępna'
    kiedy = f'od {formatuj_date(ksiazka.data_wypozyczenia, format_daty)}' if ksiazka.data_wypozyczenia else 'data nieznana'
    return f'    wypożyczona przez: {ksiazka.wypozyczona_przez}, {kiedy}'


def isbn_uzytkownika(tekst: str) -> str:
    try:
        return normalizuj_isbn(tekst)
    except ValueError as blad:
        raise BladUzytkownika(str(blad)) from None


def data_uzytkownika(tekst: str) -> date:
    try:
        return sprawdz_date(tekst)
    except ValueError as blad:
        raise BladUzytkownika(str(blad)) from None


def polecenie_lista(args, ksiazki: list[Ksiazka]) -> int:
    if args.autor is not None:
        ksiazki = [k for k in ksiazki if pasuje(k.autor, args.autor)]
    if args.tylko_dostepne:
        ksiazki = [k for k in ksiazki if not k.wypozyczona]
    if args.sortuj == 'rok':
        ksiazki = sorted(ksiazki, key=lambda k: (k.rok is None, k.rok or 0))
    elif args.sortuj:
        ksiazki = sorted(ksiazki, key=lambda k: klucz_alfabetyczny(getattr(k, args.sortuj)))
    for ksiazka in ksiazki:
        print(formatuj(ksiazka))
        if args.szczegoly:
            print(szczegoly(ksiazka, args.format_wyjscia))
    return 0


def polecenie_szukaj(args, ksiazki: list[Ksiazka]) -> int:
    if args.autor is None and args.tytul is None and args.isbn is None:
        raise BladUzytkownika('Podaj --autor, --tytul albo --isbn.')
    isbn = isbn_uzytkownika(args.isbn) if args.isbn is not None else None
    for ksiazka in szukaj(ksiazki, autor=args.autor, tytul=args.tytul, isbn=isbn):
        print(formatuj(ksiazka))
    return 0


def polecenie_dodaj(args, ksiazki: list[Ksiazka]) -> int:
    tytul, autor = nfc(args.tytul.strip()), nfc(args.autor.strip())
    if not tytul or not autor:
        raise BladUzytkownika('Tytuł i autor nie mogą być puste.')
    try:
        rok = sprawdz_rok(args.rok)
        sprawdz_tekst(tytul, 'tytuł'), sprawdz_tekst(autor, 'autor')
    except ValueError as blad:
        raise BladUzytkownika(str(blad)) from None
    isbn = isbn_uzytkownika(args.isbn) if args.isbn is not None else None
    nowa = Ksiazka(id=nastepne_id(ksiazki), tytul=tytul, autor=autor, rok=rok, isbn=isbn)
    zapisz_ksiazki(args, [*ksiazki, nowa])
    print(f'Dodano: {formatuj(nowa)}')
    return 0


def plik_eksportu(katalog: Path, nazwa: str) -> Path:
    if not nazwa or nazwa in ('.', '..') or Path(nazwa).name != nazwa or Path(nazwa).is_absolute():
        raise BladUzytkownika(f'Nazwa pliku eksportu musi być samą nazwą pliku: {nazwa}')
    cel = katalog / nazwa
    if cel.is_symlink():
        raise BladUzytkownika(f'Plik eksportu jest dowiązaniem, odmawiam zapisu: {cel}')
    return cel


def zapisz_ksiazki(args, ksiazki: list[Ksiazka], historia: bool = False, rezerwacje: bool = False) -> None:
    args.stan.ksiazki = ksiazki
    zapisz_stan(args.dane, args.stan, historia=historia, rezerwacje=rezerwacje)


def polecenie_eksport(args, ksiazki: list[Ksiazka]) -> int:
    katalog = Path(args.katalog_eksportu) if args.katalog_eksportu is not None else args.konf.katalog_eksportu()
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
    zapisz_ksiazki(args, [*ksiazki, *nowe])
    print(f'Zaimportowano {len(nowe)} pozycji.')
    return 0


def znajdz(ksiazki: list[Ksiazka], ident: int) -> Ksiazka:
    for ksiazka in ksiazki:
        if ksiazka.id == ident:
            return ksiazka
    raise BladUzytkownika(f'Nie ma książki o id {ident}.')


def polecenie_wypozycz(args, ksiazki: list[Ksiazka]) -> int:
    ksiazka = znajdz(ksiazki, args.id)
    osoba = args.osoba.strip()
    if not osoba:
        raise BladUzytkownika('Podaj osobę wypożyczającą.')
    kiedy = data_uzytkownika(args.data) if args.data is not None else date.today()
    if ksiazka.wypozyczona:
        raise BladUzytkownika(f'Książka jest już wypożyczona: {formatuj(ksiazka)}')
    kolejka = args.stan.rezerwacje.get(str(ksiazka.id), [])
    if kolejka and kolejka[0] != osoba:
        raise BladUzytkownika(f'Książka jest zarezerwowana; pierwsza w kolejce: {kolejka[0]}')
    if kolejka:
        kolejka.pop(0)
        if not kolejka:
            del args.stan.rezerwacje[str(ksiazka.id)]
    ksiazka.wypozyczona_przez, ksiazka.data_wypozyczenia = osoba, kiedy.isoformat()
    args.stan.historia.append({'id': ksiazka.id, 'typ': 'wypozyczenie', 'osoba': osoba, 'data': kiedy.isoformat()})
    zapisz_ksiazki(args, ksiazki, historia=True, rezerwacje=True)
    print(formatuj(ksiazka))
    return 0


def polecenie_zwroc(args, ksiazki: list[Ksiazka]) -> int:
    ksiazka = znajdz(ksiazki, args.id)
    if not ksiazka.wypozyczona:
        raise BladUzytkownika(f'Książka nie jest wypożyczona: {formatuj(ksiazka)}')
    kiedy = data_uzytkownika(args.data) if args.data is not None else date.today()
    if ksiazka.data_wypozyczenia and kiedy < date.fromisoformat(ksiazka.data_wypozyczenia):
        raise BladUzytkownika('Data zwrotu jest wcześniejsza niż data wypożyczenia.')
    args.stan.historia.append({'id': ksiazka.id, 'typ': 'zwrot', 'osoba': ksiazka.wypozyczona_przez,
                               'data': kiedy.isoformat()})
    ksiazka.wypozyczona_przez = ksiazka.data_wypozyczenia = None
    zapisz_ksiazki(args, ksiazki, historia=True)
    print(formatuj(ksiazka))
    kolejka = args.stan.rezerwacje.get(str(ksiazka.id))
    if kolejka:
        print(f'Zarezerwowana dla: {kolejka[0]}')
    return 0


def polecenie_historia(args, ksiazki: list[Ksiazka]) -> int:
    znajdz(ksiazki, args.id)
    zdarzenia = [z for z in args.stan.historia if z['id'] == args.id]
    nazwy = {'wypozyczenie': 'wypożyczenie', 'zwrot': 'zwrot'}
    for zdarzenie in sorted(zdarzenia, key=lambda z: z['data']):  # sort stabilny: równe daty w kolejności zapisu
        print(f"{formatuj_date(zdarzenie['data'], args.format_wyjscia)} — {nazwy[zdarzenie['typ']]} — {zdarzenie['osoba']}")
    return 0


def polecenie_rezerwuj(args, ksiazki: list[Ksiazka]) -> int:
    ksiazka = znajdz(ksiazki, args.id)
    osoba = args.osoba.strip()
    if not osoba:
        raise BladUzytkownika('Podaj osobę rezerwującą.')
    kolejka = args.stan.rezerwacje.setdefault(str(ksiazka.id), [])
    if osoba in kolejka:
        raise BladUzytkownika(f'{osoba} jest już w kolejce do tej książki.')
    kolejka.append(osoba)
    zapisz_ksiazki(args, ksiazki, rezerwacje=True)
    print(f'Zarezerwowano: {osoba}, pozycja {len(kolejka)}')
    return 0


def polecenie_rezerwacje(args, ksiazki: list[Ksiazka]) -> int:
    ksiazka = znajdz(ksiazki, args.id)
    for numer, osoba in enumerate(args.stan.rezerwacje.get(str(ksiazka.id), []), start=1):
        print(f'{numer}. {osoba}')
    return 0


def polecenie_konfiguracja(args, ksiazki: list[Ksiazka]) -> int:
    for klucz in sorted(args.konf.wartosci):
        print(f'{klucz} = {args.konf.wartosci[klucz]} ({args.konf.zrodla[klucz]})')
    return 0


def polecenie_migruj(args, ksiazki: list[Ksiazka]) -> int:
    if args.stan.wersja == 2:
        print('Plik jest już w wersji 2.')
        return 0
    migruj(args.dane, args.stan)
    rezerwacje = sum(len(kolejka) for kolejka in args.stan.rezerwacje.values())
    print(f'Zmigrowano do wersji 2: {len(ksiazki)} książek, {len(args.stan.historia)} zdarzeń, {rezerwacje} rezerwacji')
    return 0


def polecenie_przetrzymane(args, ksiazki: list[Ksiazka]) -> int:
    dzis = data_uzytkownika(args.dzis) if args.dzis is not None else date.today()
    if args.dni is None:
        args.dni = args.konf['dni_przetrzymania']
    if args.dni < 0:
        raise BladUzytkownika('Liczba dni nie może być ujemna.')
    przetrzymane, bez_daty = [], []
    for ksiazka in ksiazki:
        if not ksiazka.wypozyczona:
            continue
        if not ksiazka.data_wypozyczenia:
            bez_daty.append(ksiazka)
            continue
        dni = (dzis - date.fromisoformat(ksiazka.data_wypozyczenia)).days
        if dni > args.dni:
            przetrzymane.append((dni, ksiazka))
    for dni, ksiazka in sorted(przetrzymane, key=lambda para: (-para[0], para[1].id)):
        print(f'[{ksiazka.id}] {ksiazka.tytul} — {ksiazka.wypozyczona_przez}, {dni} dni')
    for ksiazka in bez_daty:
        print(f'[{ksiazka.id}] {ksiazka.tytul} — {ksiazka.wypozyczona_przez}, brak daty')
    return 0


def jedno_miejsce(licznik: int, mianownik: int) -> str:
    wartosc = (Decimal(licznik) / Decimal(mianownik)).quantize(Decimal('0.1'), rounding=ROUND_HALF_UP)
    return str(wartosc).replace('.', ',')


def polecenie_statystyki(args, ksiazki: list[Ksiazka]) -> int:
    wypozyczone = sum(k.wypozyczona for k in ksiazki)
    z_rokiem = [k for k in ksiazki if k.rok is not None]
    procent = jedno_miejsce(100 * wypozyczone, len(ksiazki)) if ksiazki else '0,0'
    print(f'Książek: {len(ksiazki)}')
    print(f'Wypożyczonych: {wypozyczone} ({procent}%)')
    print(f'Autorów: {len({klucz_tekstu(k.autor) for k in ksiazki})}')
    print(f"Średni rok wydania: {jedno_miejsce(sum(k.rok for k in z_rokiem), len(z_rokiem)) if z_rokiem else 'brak'}")
    najstarsza = min(z_rokiem, key=lambda k: (k.rok, k.id)) if z_rokiem else None
    print(f"Najstarsza: {formatuj(najstarsza) if najstarsza else 'brak'}")
    return 0


def parser() -> argparse.ArgumentParser:
    glowny = argparse.ArgumentParser(prog='biblioteka', description=__doc__)
    glowny.add_argument('--version', action='version', version=f'biblioteka {__version__}')
    glowny.add_argument('--dane', default='dane/biblioteka.json', help='plik katalogu (JSON)')
    glowny.add_argument('--konfiguracja', help='plik konfiguracji TOML (domyślnie biblioteka.toml obok danych)')
    glowny.add_argument('--format-daty', choices=('pl', 'iso'), help='format dat w wyjściu')
    polecenia = glowny.add_subparsers(dest='polecenie', required=True)

    lista = polecenia.add_parser('lista', help='wypisz książki w kolejności z pliku')
    lista.add_argument('--szczegoly', action='store_true', help='pokaż stan wypożyczenia')
    lista.add_argument('--sortuj', choices=('tytul', 'autor', 'rok'))
    lista.add_argument('--autor', help='tylko książki pasującego autora')
    lista.add_argument('--tylko-dostepne', action='store_true')
    lista.set_defaults(func=polecenie_lista)

    szukaj_ = polecenia.add_parser('szukaj', help='szukaj po autorze, tytule albo ISBN')
    szukaj_.add_argument('--autor')
    szukaj_.add_argument('--tytul')
    szukaj_.add_argument('--isbn')
    szukaj_.set_defaults(func=polecenie_szukaj)

    dodaj = polecenia.add_parser('dodaj', help='dodaj książkę')
    dodaj.add_argument('--tytul', required=True)
    dodaj.add_argument('--autor', required=True)
    dodaj.add_argument('--rok', type=int)
    dodaj.add_argument('--isbn')
    dodaj.set_defaults(func=polecenie_dodaj)

    eksport = polecenia.add_parser('eksport', help='zapisz katalog do CSV')
    eksport.add_argument('nazwa', help='nazwa pliku w katalogu eksportu')
    eksport.add_argument('--katalog-eksportu')
    eksport.set_defaults(func=polecenie_eksport)

    import_ = polecenia.add_parser('import', help='dopisz książki z CSV (kolumny tytul, autor, rok, isbn)')
    import_.add_argument('plik')
    import_.set_defaults(func=polecenie_import)

    wypozycz = polecenia.add_parser('wypozycz', help='zapisz wypożyczenie')
    wypozycz.add_argument('id', type=int)
    wypozycz.add_argument('--osoba', required=True)
    wypozycz.add_argument('--data', help='RRRR-MM-DD albo DD.MM.RRRR, domyślnie dziś')
    wypozycz.set_defaults(func=polecenie_wypozycz)

    zwroc = polecenia.add_parser('zwroc', help='zapisz zwrot')
    zwroc.add_argument('id', type=int)
    zwroc.add_argument('--data', help='RRRR-MM-DD albo DD.MM.RRRR, domyślnie dziś')
    zwroc.set_defaults(func=polecenie_zwroc)

    przetrzymane = polecenia.add_parser('przetrzymane', help='wypożyczone dłużej niż N dni')
    przetrzymane.add_argument('--dzis', help='RRRR-MM-DD, domyślnie dziś')
    przetrzymane.add_argument('--dni', type=int)
    przetrzymane.set_defaults(func=polecenie_przetrzymane)

    statystyki = polecenia.add_parser('statystyki', help='podsumowanie katalogu')
    statystyki.set_defaults(func=polecenie_statystyki)

    polecenia.add_parser('konfiguracja', help='ustawienia i ich źródła').set_defaults(func=polecenie_konfiguracja)
    historia = polecenia.add_parser('historia', help='historia wypożyczeń książki')
    historia.add_argument('id', type=int)
    historia.set_defaults(func=polecenie_historia)
    rezerwuj = polecenia.add_parser('rezerwuj', help='dopisz osobę do kolejki rezerwacji')
    rezerwuj.add_argument('id', type=int)
    rezerwuj.add_argument('--osoba', required=True)
    rezerwuj.set_defaults(func=polecenie_rezerwuj)
    rezerwacje = polecenia.add_parser('rezerwacje', help='kolejka rezerwacji książki')
    rezerwacje.add_argument('id', type=int)
    rezerwacje.set_defaults(func=polecenie_rezerwacje)
    polecenia.add_parser('migruj', help='przenieś plik danych do formatu v2').set_defaults(func=polecenie_migruj)
    return glowny


def main(argv=None) -> int:
    args = parser().parse_args(argv)
    for strumien in (sys.stdout, sys.stderr):
        if hasattr(strumien, 'reconfigure'):
            strumien.reconfigure(encoding='utf-8')
    args.dane = Path(args.dane)
    try:
        args.konf = wczytaj_konfiguracje(args.dane, args.konfiguracja)
        if args.format_daty is not None:
            args.konf.wartosci['format_daty'], args.konf.zrodla['format_daty'] = args.format_daty, 'argument'
        args.format_wyjscia = args.konf['format_daty']
        args.stan = wczytaj_stan(args.dane)
        return args.func(args, args.stan.ksiazki)
    except (BladUzytkownika, BladKonfiguracji, BladWersji) as blad:
        print(blad, file=sys.stderr)
        return 2
