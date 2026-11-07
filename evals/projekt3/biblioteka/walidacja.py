"""Walidacja pól wspólna dla CLI i importu."""

from datetime import date
import re
import unicodedata

ROK_MIN = 1450


def sprawdz_rok(rok: int | None) -> int | None:
    # Rok jest opcjonalny (decyzja właściciela w E2, kryteria T-107 v2); podany musi mieścić się w zakresie.
    if rok is not None and not ROK_MIN <= rok <= date.today().year:
        raise ValueError(f'rok spoza zakresu {ROK_MIN}–{date.today().year}: {rok}')
    return rok


def sprawdz_date(tekst: str) -> date:
    try:
        if not re.fullmatch(r'\d{4}-\d{2}-\d{2}', tekst):
            raise ValueError
        return date.fromisoformat(tekst)
    except ValueError:
        raise ValueError(f'niepoprawna data (RRRR-MM-DD): {tekst}') from None


def sprawdz_tekst(tekst: str, pole: str) -> str:
    """Znaki sterujące (np. nowa linia) złamałyby zasadę „jedna linia `lista` na książkę”."""
    if any(unicodedata.category(znak) == 'Cc' for znak in tekst):
        raise ValueError(f'{pole} zawiera znaki sterujące')
    return tekst
