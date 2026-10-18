# ZESPÓŁ — runner registry of this machine (shared by every lead host)

Template. The live file is `~/.kierownik/ZESPOL.md` (Windows: `%USERPROFILE%\.kierownik\ZESPOL.md`), one per
machine, read and written by the lead in Claude Code and in Codex alike, so a limit or a new subscription recorded
by one host is known to the other. Procedures: ZESPOL_PROCEDURY.md. The owner may edit it by hand; entries in
Polish. The only file with concrete model names. State only — no procedures.

Stan wypełnienia: NIEWYPEŁNIONY   (the lead changes it to: WYPEŁNIONY <data>)


## Klasy

SZYBKI < STANDARDOWY < MOCNY < NAJMOCNIEJSZY — capability tiers comparable across providers. A model's class is
assigned by the lead from its capability and cost relative to the others and confirmed by the owner (procedure B).
Routing (SKILL.md, section 7) names only classes and families, never tools — adding, dropping or replacing a
subscription changes only this file.


## Runnery

One row per way of getting work done. `host` = the lead's own subagents (cheapest to orchestrate, but the same
family as the lead); `CLI` = a non-interactive command run in a role directory. Priorytet: 1 = spend first; the
owner sets it (e.g. to save a subscription for later in the month).

| ID | Rodzina | Typ | Modele → klasy | Priorytet | Stan | Uwagi |
|---|---|---|---|---|---|---|
| claude-sub | Anthropic | host w Claude Code (`kier-*`) | `fable` NAJMOCNIEJSZY, `opus` MOCNY, `sonnet` STANDARDOWY, `haiku` SZYBKI | 1 | dostępny | aliases follow the newest model of each line |
| claude-cli | Anthropic | CLI (`claude -p`) — runner for a Codex host | as claude-sub | 1 | NIEZNANY | |
| codex-sub | OpenAI | host w Codex (role `kier-*`, run_agent.py) | <model> MOCNY, <model> STANDARDOWY | 1 | NIEZNANY | |
| codex-cli | OpenAI | CLI (`codex exec`) — runner for a Claude host | as codex-sub | 2 | NIEZNANY | sandbox `-s` |
| agy-cli | Google | CLI (`agy -p`) | <model> MOCNY | 2 | NIEZNANY | no sandbox — whole machine |

Stan: `dostępny` | `niedostępny do <data godzina>` | `niedostępny od <data godzina>` (reset time unknown — retry
after ~5 h or when the owner says so) | `wyłączony przez właściciela` | `NIEZNANY` (not smoke-tested yet). The lead
writes the first three after a limit message or the owner's information; `wyłączony przez właściciela` only the
owner — the lead neither tests nor uses such a runner. A new provider = a new row (procedure B).


## Polecenia CLI (zweryfikowane testem dymnym)

| Runner | Polecenie (zlecenie z pliku, wynik i stderr do plików) | Model / effort | Test dymny |
|---|---|---|---|
| codex-cli | <z ZESPOL_PROCEDURY.md, część C, po sprawdzeniu `--help`> | `-m <model>` | [?] |
| agy-cli | <…> | <flaga z `--help`> | [?] |
| claude-cli | <…> | `--model <alias>` | [?] |


## Host Claude Code — role i effort

The model and effort in force are `model:`/`effort:` in `~/.claude/agents/kier-*.md`; this table must match them.
`model` can be overridden per call (aliases only); `effort` only in the file.

| Rola | Subagent | Klasa domyślna | `effort:` |
|---|---|---|---|
| Kierownik | main thread `/kierownik` | MOCNY (`/model opus`) | session default; `/effort high` set by the owner |
| Analityk | `kier-analityk` | STANDARDOWY (`sonnet`) | medium |
| Wykonawca | `kier-wykonawca` | STANDARDOWY (`sonnet`) | medium |
| Recenzent | `kier-recenzent` | MOCNY (`opus`) | high |
| Architekt | `kier-architekt` | MOCNY (`opus`); NAJMOCNIEJSZY per call (SKILL.md, section 7) | high |

Bezpiecznik kontekstu kierownika Claude: `/autocompact 200k`. Subagenci `kier-*` zainstalowani: [?]


## Host Codex — role i effort

Roles in `roles/kier-*.toml` inherit the Codex session model until `model` is set there; `run_agent.py --model
/--effort` override per order. Natywne role: NIEZWERYFIKOWANE; per-agent cwd: NIEZWERYFIKOWANE.

| Rola | Definicja | Klasa domyślna | Effort |
|---|---|---|---|
| Analityk | roles/kier-analityk.toml | STANDARDOWY | medium |
| Wykonawca | roles/kier-wykonawca.toml | STANDARDOWY | medium |
| Recenzent | roles/kier-recenzent.toml | MOCNY | high |
| Architekt | roles/kier-architekt.toml | MOCNY; NAJMOCNIEJSZY per order | high |


## Historia zmian
- <data> — <co zmieniono i dlaczego>
