#!/usr/bin/env python3
"""Zestawia wyniki przebiegów (evals/wyniki/*.json) w tabeli Markdown: każdy przebieg osobno i średnie
na konfigurację. Wynik w evals/WYNIKI.md."""

import argparse
import json
from pathlib import Path
import sys

EVALS = Path(__file__).resolve().parent
OPISY = {'A': 'sesja bez kierownika', 'B': 'kierownik, tylko Claude', 'C': 'kierownik + Codex',
         'D': 'kierownik, wykonawca Sonnet'}


def srednia(wartosci: list) -> str:
    liczby = [w for w in wartosci if w is not None]
    return f'{sum(liczby) / len(liczby):.1f}' if liczby else '—'


def tabela(wyniki: list[dict]) -> str:
    wiersze = ['# Wyniki evali orkiestratora', '',
               '| Konf. | Przebieg | Data | Zadania | Kolizja | Widoczne | Osłabione | Rewerty | Commity | Minuty | '
               'Tokeny | Rundy | Wersja |',
               '|---|---|---|---|---|---|---|---|---|---|---|---|---|']
    for w in sorted(wyniki, key=lambda w: (w['konfiguracja'], w['przebieg'], w['data'])):
        wiersze.append(
            f"| {w['konfiguracja']} | {w['przebieg']} | {w['data']} | {w['zadania_zaliczone']}/{w['zadania_wszystkie']} | "
            f"{'tak' if w['kolizja_zaliczona'] else 'nie'} | {'tak' if w['widoczne']['zaliczone'] else 'nie'} | "
            f"{len(w['oslabione_testy'])} | {w['historia']['rewerty']} | {w['historia']['commity_main']} | "
            f"{w['minuty'] if w['minuty'] is not None else '—'} | {w['tokeny'] if w['tokeny'] is not None else '—'} | "
            f"{w['rundy'] if w['rundy'] is not None else '—'} | {w['wersje']['orkiestrator']} |")
    wiersze += ['', '## Średnie na konfigurację', '',
                '| Konfiguracja | Przebiegów | Zadania | Kolizja (%) | Minuty | Tokeny | Rundy |', '|---|---|---|---|---|---|---|']
    for konf in sorted({w['konfiguracja'] for w in wyniki}):
        grupa = [w for w in wyniki if w['konfiguracja'] == konf]
        kolizja = 100 * sum(w['kolizja_zaliczona'] for w in grupa) / len(grupa)
        wiersze.append(f"| {konf} — {OPISY.get(konf, '')} | {len(grupa)} | {srednia([w['zadania_zaliczone'] for w in grupa])} | "
                       f"{kolizja:.0f} | {srednia([w['minuty'] for w in grupa])} | {srednia([w['tokeny'] for w in grupa])} | "
                       f"{srednia([w['rundy'] for w in grupa])} |")
    uwagi = [w for w in wyniki if w.get('uwagi')]
    if uwagi:
        wiersze += ['', '## Uwagi z przebiegów', '']
        wiersze += [f"- {w['konfiguracja']}-{w['przebieg']}: {w['uwagi']}" for w in uwagi]
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
