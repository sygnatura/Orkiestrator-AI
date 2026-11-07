"""Stan CLI: książki, historia wypożyczeń i rezerwacje — w starym formacie (lista + pliki poboczne) albo v2."""

from dataclasses import dataclass
import json
import os
from pathlib import Path

from biblioteka.magazyn import zapisz_tekst
from biblioteka.model import Ksiazka


class BladWersji(ValueError):
    pass


@dataclass
class Stan:
    ksiazki: list[Ksiazka]
    historia: list[dict]
    rezerwacje: dict[str, list[str]]
    wersja: int


def pliki_poboczne(sciezka: Path) -> tuple[Path, Path]:
    rdzen = sciezka.name[:-5] if sciezka.name.endswith('.json') else sciezka.name
    return sciezka.with_name(rdzen + '.historia.json'), sciezka.with_name(rdzen + '.rezerwacje.json')


def json_z(plik: Path, domyslne):
    return json.loads(plik.read_text(encoding='utf-8')) if plik.is_file() else domyslne


def wczytaj_stan(sciezka: Path) -> Stan:
    sciezka = Path(sciezka)
    dane = json.loads(sciezka.read_text(encoding='utf-8'))
    if isinstance(dane, list):
        historia, rezerwacje = pliki_poboczne(sciezka)
        return Stan([Ksiazka.z_slownika(d) for d in dane], json_z(historia, []), json_z(rezerwacje, {}), 1)
    if isinstance(dane, dict) and dane.get('wersja') == 2:
        return Stan([Ksiazka.z_slownika(d) for d in dane.get('ksiazki', [])], list(dane.get('historia', [])),
                     dict(dane.get('rezerwacje', {})), 2)
    wersja = dane.get('wersja', 'brak') if isinstance(dane, dict) else type(dane).__name__
    raise BladWersji(f'Nieobsługiwana wersja pliku danych: {wersja} (obsługiwane: stary format i wersja 2)')


def tekst_json(dane) -> str:
    return json.dumps(dane, ensure_ascii=False, indent=1) + '\n'


def zapisz_stan(sciezka: Path, stan: Stan, historia: bool = False, rezerwacje: bool = False) -> None:
    """Zapis w formacie, w którym stan przeczytano; w starym formacie tylko pliki, które się zmieniły."""
    sciezka = Path(sciezka)
    ksiazki = [k.do_slownika() for k in stan.ksiazki]
    if stan.wersja == 2:
        zapisz_tekst(sciezka, tekst_json({'wersja': 2, 'ksiazki': ksiazki, 'historia': stan.historia,
                                          'rezerwacje': stan.rezerwacje}))
        return
    plik_historii, plik_rezerwacji = pliki_poboczne(sciezka)
    if historia:
        zapisz_tekst(plik_historii, tekst_json(stan.historia))
    if rezerwacje:
        zapisz_tekst(plik_rezerwacji, tekst_json(stan.rezerwacje))
    zapisz_tekst(sciezka, tekst_json(ksiazki))


def migruj(sciezka: Path, stan: Stan) -> None:
    stan.wersja = 2
    zapisz_stan(sciezka, stan)
    for plik in pliki_poboczne(Path(sciezka)):
        if plik.exists():
            os.replace(plik, plik.with_name(plik.name + '.v1.bak'))
