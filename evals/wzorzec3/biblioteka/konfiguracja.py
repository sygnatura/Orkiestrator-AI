"""Plik konfiguracji TOML: domyślnie biblioteka.toml obok pliku danych."""

from dataclasses import dataclass
from pathlib import Path
import tomllib

DOMYSLNE = {'dni_przetrzymania': 30, 'format_daty': 'pl', 'katalog_eksportu': 'eksport'}


class BladKonfiguracji(ValueError):
    pass


@dataclass
class Konfiguracja:
    wartosci: dict
    zrodla: dict
    katalog: Path | None

    def __getitem__(self, klucz):
        return self.wartosci[klucz]

    def katalog_eksportu(self) -> Path:
        sciezka = Path(self.wartosci['katalog_eksportu'])
        if self.zrodla['katalog_eksportu'] == 'plik' and not sciezka.is_absolute():
            return self.katalog / sciezka
        return sciezka


def sprawdz(klucz: str, wartosc) -> None:
    if klucz == 'dni_przetrzymania' and not (type(wartosc) is int and wartosc >= 0):
        raise BladKonfiguracji(f'Klucz {klucz}: oczekiwana liczba całkowita ≥ 0, jest {wartosc!r}')
    if klucz == 'format_daty' and wartosc not in ('pl', 'iso'):
        raise BladKonfiguracji(f'Klucz {klucz}: oczekiwane "pl" albo "iso", jest {wartosc!r}')
    if klucz == 'katalog_eksportu' and not (isinstance(wartosc, str) and wartosc):
        raise BladKonfiguracji(f'Klucz {klucz}: oczekiwana niepusta ścieżka, jest {wartosc!r}')


def wczytaj_konfiguracje(sciezka_danych: Path, jawna: str | None) -> Konfiguracja:
    plik = Path(jawna) if jawna else Path(sciezka_danych).parent / 'biblioteka.toml'
    wartosci, zrodla = dict(DOMYSLNE), {klucz: 'domyślne' for klucz in DOMYSLNE}
    if not plik.is_file():
        if jawna:
            raise BladKonfiguracji(f'Brak pliku konfiguracji: {plik}')
        return Konfiguracja(wartosci, zrodla, None)
    try:
        dane = tomllib.loads(plik.read_text(encoding='utf-8'))
    except (tomllib.TOMLDecodeError, UnicodeDecodeError) as blad:
        raise BladKonfiguracji(f'Błędny plik konfiguracji {plik}: {blad}') from None
    for klucz, wartosc in dane.items():
        if klucz not in DOMYSLNE:
            raise BladKonfiguracji(f'Nieznany klucz konfiguracji: {klucz}')
        sprawdz(klucz, wartosc)
        wartosci[klucz], zrodla[klucz] = wartosc, 'plik'
    return Konfiguracja(wartosci, zrodla, plik.parent)
