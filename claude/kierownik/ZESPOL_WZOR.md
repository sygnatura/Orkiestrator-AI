# ZESPÓŁ — runner registry of this machine (shared by every lead host)

Registry v12, schemat 2. Template. The live file is `~/.kierownik/ZESPOL.md` (Windows: `%USERPROFILE%\.kierownik\ZESPOL.md`),
one per machine, read and written by the lead in Claude Code and in Codex alike, so a limit or a new subscription
recorded by one host is known to the other. Procedures: ZESPOL_PROCEDURY.md; running CLIs: URUCHAMIANIE_CLI.md. The
owner may edit it by hand; entries in Polish. The only file with concrete model names. State only — no procedures.

Stan wypełnienia: NIEWYPEŁNIONY   (the lead changes it to: WYPEŁNIONY <data>)

Stany (subscriptions and models): `dostępny` | `niedostępny do <data godzina>` (a reset time without one in the
message is an estimate: now + 5 h, written „(szacunek)”; a limit again right after it doubles the wait) |
`wymaga credits` (unavailable unless the owner agrees to pay) | `wyłączony przez właściciela` (set only by the owner or on the owner's explicit `zespół:`; the
lead neither tests nor uses it) | `NIEZNANY` (not checked yet — check before first use).


## Klasy

SZYBKI < STANDARDOWY < MOCNY < NAJMOCNIEJSZY — capability tiers comparable across providers. A model's class is
assigned by the lead from its capability and cost relative to the others and confirmed by the owner. Routing
(SKILL.md, section 7) names only classes and families, never tools — adding, dropping or replacing a subscription
changes only this file.


## Subskrypcje

Billing and limits: a limit or a cancelled plan usually hits a whole subscription; a single model can also be
limited (table below). Priorytet: 1 = spend first; the owner sets it (`zespół: oszczędzaj X` → higher number).

| Subskrypcja | Dostawca | Plan | Priorytet | Stan |
|---|---|---|---|---|
| claude | Anthropic | Max | 1 | dostępny |
| openai | OpenAI | <…> | 2 | NIEZNANY |
| google | Google | <…> | 2 | NIEZNANY |


## Modele

„Rodzina” belongs to the MODEL (who trained it), not to the tool or subscription — one CLI may offer models of
several families; independence of a review is judged by the model's family.

| Model / alias | Rodzina | Subskrypcja | Klasa | Stan | Uwagi |
|---|---|---|---|---|---|
| `fable` | Anthropic | claude | NAJMOCNIEJSZY | dostępny | `/model` also has `best`; subagent docs list only `fable` — use it |
| `opus` | Anthropic | claude | MOCNY | dostępny | default model of the plan; default effort of the line: medium |
| `sonnet` | Anthropic | claude | STANDARDOWY | dostępny | |
| `haiku` | Anthropic | claude | SZYBKI | dostępny | no effort field — `kier-analityk` with `model: haiku` unverified [?] |
| <model z `codex --help`> | OpenAI | openai | MOCNY | NIEZNANY | |
| <model z `agy --help`> | <rodzina modelu> | google | MOCNY | NIEZNANY | |

Claude aliases follow the newest model of their line; the version they point to is information only. Every order
names its model explicitly (SKILL.md, section 7), so changing a class mapping here is enough — agent and role-file
defaults are only fallbacks.


## Runnery

One row per way of getting work done. „Host”: the lead host the runner is used from — `Claude Code`, `Codex` or
`oba`. A lead uses only rows for its own host or `oba`; `subagenci` of its own host are its host runner (cheapest to
orchestrate). A runner is usable when its subscription and the chosen model are usable.

| ID | Subskrypcja | Typ | Host | Mechanizm / polecenie (zweryfikowane) | Test dymny |
|---|---|---|---|---|---|
| claude-sub | claude | subagenci `kier-*` | Claude Code | narzędzie Agent, `model: <alias>` | n/d |
| codex-cli | openai | CLI | Claude Code | <z URUCHAMIANIE_CLI.md po `--help`> | [?] |
| codex-sub | openai | role `kier-*` / run_agent.py | Codex | role TOML, `run_agent.py --model/--effort` | [?] |
| claude-cli | claude | CLI | Codex | <…> | [?] |
| agy-cli | google | CLI | oba | <…>; zgoda właściciela na tryb bez sandboxa (`--dangerously-skip-permissions`): BRAK — zapytaj przy konfiguracji (ZESPOL_PROCEDURY.md, A.4) | [?] |


## Host Claude Code — role i effort

The defaults in force are `model:`/`effort:` in `~/.claude/agents/kier-*.md`; this table must match them. Both can be
overridden per call (`model`: aliases; `effort`: Claude Code ≥ 2.1.292).

Claude Code: <wersja z `claude --version`>

| Rola | Subagent | Klasa domyślna | `effort:` |
|---|---|---|---|
| Kierownik | main thread `/kierownik` | MOCNY (`/model opus`) | session default; `/effort high` set by the owner |
| Analityk | `kier-analityk` | STANDARDOWY (`sonnet`) | medium |
| Wykonawca | `kier-wykonawca` | MOCNY (`opus`); STANDARDOWY (`sonnet`) per call for simple tasks | medium |
| Recenzent | `kier-recenzent` | MOCNY (`opus`) | high |
| Architekt | `kier-architekt` | MOCNY (`opus`); NAJMOCNIEJSZY per call (SKILL.md, section 7) | high |

Bezpiecznik kontekstu kierownika Claude: `/autocompact 200k` (by cost per turn, not by window size; Claude Code ≥ 2.1.221,
saved in user settings — every project).
Zgoda właściciela na `agy` bez sandboxa: BRAK (TAK/NIE <data> „(potwierdzona na tej maszynie: <hostname>)” — ZESPOL_PROCEDURY.md, A.4)
Subagenci `kier-*` zainstalowani: [?]; kier.py: [?]


## Host Codex — role i effort

Roles in `roles/kier-*.toml` inherit the Codex session model until `model` is set there; `run_agent.py --model
/--effort` override per order. Natywne role: NIEZWERYFIKOWANE; per-agent cwd: NIEZWERYFIKOWANE; kier.py: [?].

| Rola | Definicja | Klasa domyślna | Effort |
|---|---|---|---|
| Analityk | roles/kier-analityk.toml | STANDARDOWY | medium |
| Wykonawca | roles/kier-wykonawca.toml | MOCNY; STANDARDOWY per order for simple tasks | medium |
| Recenzent | roles/kier-recenzent.toml | MOCNY | high |
| Architekt | roles/kier-architekt.toml | MOCNY; NAJMOCNIEJSZY per order | high |


## Historia zmian
- <data> — <co zmieniono i dlaczego>
