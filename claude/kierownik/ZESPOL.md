# ZESPÓŁ — state of this machine: model classes, roles, backup, limits

Shared by all projects on this machine. Filled in and updated by the lead (procedures: ZESPOL_PROCEDURY.md);
the owner may edit it by hand. The only package file with concrete model names. State only — no procedures.

Stan wypełnienia: NIEWYPEŁNIONY   (the lead changes it to: WYPEŁNIONY <data>)


## Model classes

SKILL.md, README.md and the templates speak of CLASSES — SZYBKI < STANDARDOWY < MOCNY < NAJMOCNIEJSZY. This table
says which Claude Code alias stands behind each class today. Aliases always point to the newest model of their
line, so a new release in the same line changes only the column „Wskazuje dziś na” (filled in from what the
owner reads in `/model`; information only — version names appear nowhere else).

| Klasa | Alias (`model:` in agent frontmatter and the `model` call parameter) | Wskazuje dziś na (stan na <data>) | Uwagi |
|---|---|---|---|
| NAJMOCNIEJSZY | `fable` | <np. Fable 5.1> | `/model` also has `best` (= strongest available), but the subagent and Agent tool docs don't list it — use `fable` |
| MOCNY | `opus` | <np. Opus 5.5> | the plan's default model; default effort of this line in Claude Code: medium |
| STANDARDOWY | `sonnet` | <np. Sonnet 5.5> | |
| SZYBKI | `haiku` | <np. Haiku 4.5> | doesn't support the effort field — calling `kier-analityk` with `model: haiku` unverified [?]; if it fails, stay with STANDARDOWY |


## Roles and effort

The model and effort actually in force are the `model:` and `effort:` fields in the frontmatter of
`~/.claude/agents/kier-*.md`; this table summarises them and must match — change one, change the other.
`model` can be overridden at any subagent call (aliases from the class table only; a full model ID works only in
frontmatter). `effort` cannot be changed at the call — need deeper work → change the class.

| Rola | Subagent | Klasa domyślna (`model:`) | `effort:` | Inna klasa przy wywołaniu |
|---|---|---|---|---|
| Kierownik | main thread `/kierownik` | MOCNY (`/model opus`) | session: model default; `/effort high` set by the owner when decisions are shallow | — |
| Analityk | `kier-analityk` | STANDARDOWY (`sonnet`) | medium | big repo, hard question → MOCNY; trivial → SZYBKI |
| Wykonawca | `kier-wykonawca` | STANDARDOWY (`sonnet`) | medium | hard, risky, after a failed round → MOCNY |
| Recenzent | `kier-recenzent` | MOCNY (`opus`) | medium | author in MOCNY (also the lead), task risk ŚREDNIE/WYSOKIE, stage goal → NAJMOCNIEJSZY |
| Architekt | `kier-architekt` | NAJMOCNIEJSZY (`fable`) | high | plan review: second, fresh instance in MOCNY |

Context safety net for the lead: `/autocompact 200k` (fixed by cost per turn, not by window size; the lead's
window: <…> per `/context` or `/model`, as of <data>; lower the threshold if the window is smaller).

Subagenci `kier-*` zainstalowani: [?]   (the lead checks at session start and writes TAK/NIE with the date)


## Backup and other-family review

| Narzędzie | Rodzina | Test dymny na tej maszynie | Odstępstwa od poleceń z ZESPOL_PROCEDURY.md, część C |
|---|---|---|---|
| Antigravity CLI (`agy`) | Google | [?] | |
| Codex CLI | OpenAI | [?] | |


## Limity

| System | Plan | Stan |
|---|---|---|
| Claude | Max | dostępny |
| Google / Antigravity | <…> | <dostępny / niedostępny do … / wyłączony przez właściciela> |
| OpenAI / Codex | <…> | <dostępny / niedostępny do … / wyłączony przez właściciela> |

Stan: `dostępny` | `niedostępny do <data godzina>` | `wyłączony przez właściciela`. The first two are written by
the lead (after a limit message or the owner's information); the third only by the owner — the lead neither tests
nor uses such a tool.


## Historia zmian
Entries in Polish (the owner reads and edits this file).
- <data> — <co zmieniono i dlaczego>
