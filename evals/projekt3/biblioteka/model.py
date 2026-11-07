"""Model danych: książka w katalogu."""

from dataclasses import asdict, dataclass


@dataclass
class Ksiazka:
    id: int
    tytul: str
    autor: str
    rok: int | None = None
    wypozyczona_przez: str | None = None
    data_wypozyczenia: str | None = None  # ISO, np. 2026-10-01
    isbn: str | None = None  # 13 cyfr; w pliku tylko, gdy ustawiony

    @property
    def wypozyczona(self) -> bool:
        return self.wypozyczona_przez is not None

    @classmethod
    def z_slownika(cls, dane: dict) -> 'Ksiazka':
        return cls(id=int(dane['id']), tytul=dane['tytul'], autor=dane['autor'], rok=dane.get('rok'),
                   wypozyczona_przez=dane.get('wypozyczona_przez'),
                   data_wypozyczenia=dane.get('data_wypozyczenia'), isbn=dane.get('isbn'))

    def do_slownika(self) -> dict:
        dane = asdict(self)
        if dane['isbn'] is None:
            del dane['isbn']
        return dane
