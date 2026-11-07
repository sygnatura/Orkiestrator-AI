#!/usr/bin/env python3
"""Zestawia wyniki przebiegów (evals/wyniki/*.json) w tabeli Markdown: każdy przebieg osobno i średnie
na konfigurację. Wynik w evals/WYNIKI.md."""

import argparse
import json
from pathlib import Path
import sys

EVALS = Path(__file__).resolve().parent
OPISY = {'A': 'sesja bez kierownika', 'B': 'kierownik, tylko Claude (z2: wykonawca Opus)', 'C': 'kierownik + Codex',
         'D': 'kierownik, wykonawca Sonnet', 'E': 'kierownik, tryb zwarty'}


def srednia(wartosci: list) -> str:
    liczby = [w for w in wartosci if w is not None]
    return f'{sum(liczby) / len(liczby):.1f}' if liczby else '—'


def tak_nie(wartosc) -> str:
    return '—' if wartosc is None else ('tak' if wartosc else 'nie')


def kontrole(wynik: dict) -> str:
    d = wynik.get('dodatkowe')
    return f'{sum(d.values())}/{len(d)}' if d else '—'


def sondy(wynik: dict) -> str:
    s = wynik.get('sondy')
    return f'{sum(s.values())}/{len(s)}' if s else '—'


def tabela(wyniki: list[dict]) -> str:
    wiersze = ['# Wyniki evali orkiestratora', '',
               '| Zestaw | Konf. | Przebieg | Data | Zadania | Kolizja | Kontrole | Sondy | Widoczne | Osłabione | Zmienione | Założenie | '
               'Rewerty | Commity | Minuty | Tokeny | Koszt USD | Rundy | Wersja |',
               '|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|']
    for w in sorted(wyniki, key=lambda w: (w.get('zestaw', 1), w['konfiguracja'], w['przebieg'], w['data'])):
        wiersze.append(
            f"| {w.get('zestaw', 1)} | {w['konfiguracja']} | {w['przebieg']} | {w['data']} | {w['zadania_zaliczone']}/{w['zadania_wszystkie']} | "
            f"{tak_nie(w['kolizja_zaliczona'])} | {kontrole(w)} | {sondy(w)} | {tak_nie(w['widoczne']['zaliczone'])} | "
            f"{len(w['oslabione_testy'])} | {len(w['zmienione_testy']) if 'zmienione_testy' in w else '—'} | {tak_nie(w.get('zalozenie_zgloszone'))} | "
            f"{w['historia']['rewerty']} | {w['historia']['commity_main']} | "
            f"{w['minuty'] if w['minuty'] is not None else '—'} | {w['tokeny'] if w['tokeny'] is not None else '—'} | "
            f"{w.get('koszt_usd') if w.get('koszt_usd') is not None else '—'} | "
            f"{w['rundy'] if w['rundy'] is not None else '—'} | {w['wersje']['orkiestrator']} |")
    wiersze += ['', '## Średnie na konfigurację', '',
                '| Zestaw | Konfiguracja | Przebiegów | Zadania | Kolizja (%) | Sondy | Minuty | Tokeny | Koszt USD | Rundy |',
                '|---|---|---|---|---|---|---|---|---|---|']
    for numer, konf in sorted({(w.get('zestaw', 1), w['konfiguracja']) for w in wyniki}):
        grupa = [w for w in wyniki if w['konfiguracja'] == konf and w.get('zestaw', 1) == numer]
        z_kolizja = [w['kolizja_zaliczona'] for w in grupa if w['kolizja_zaliczona'] is not None]
        kolizja = f'{100 * sum(z_kolizja) / len(z_kolizja):.0f}' if z_kolizja else '—'
        wiersze.append(f"| {numer} | {konf} — {OPISY.get(konf, '')} | {len(grupa)} | {srednia([w['zadania_zaliczone'] for w in grupa])} | "
                       f"{kolizja} | {srednia([sum(w['sondy'].values()) if w.get('sondy') else None for w in grupa])} | "
                       f"{srednia([w['minuty'] for w in grupa])} | {srednia([w['tokeny'] for w in grupa])} | "
                       f"{srednia([w.get('koszt_usd') for w in grupa])} | "
                       f"{srednia([w['rundy'] for w in grupa])} |")
    uwagi = [w for w in wyniki if w.get('uwagi')]
    if uwagi:
        wiersze += ['', '## Uwagi z przebiegów', '']
        wiersze += [f"- z{w.get('zestaw', 1)} {w['konfiguracja']}-{w['przebieg']}: {w['uwagi']}" for w in uwagi]
    return '\n'.join(wiersze) + '\n'


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--wyniki', type=Path, default=EVALS / 'wyniki')
    parser.add_argument('--cel', type=Path, default=EVALS / 'WYNIKI.md')
    args = parser.parse_args(argv)
    wyniki = [json.loads(p.read_text(encoding='utf-8')) for p in sorted(args.wyniki.glob('*.json'))]
    if not wyniki:
        raise SystemExit(f'Brak wyników w {args.wyniki} — najpierw evals/ocen.py.')
    tekst = tabela(wyniki)
    args.cel.write_text(tekst, encoding='utf-8')
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8')
    print(tekst)
    return 0


if __name__ == '__main__':
    sys.exit(main())
