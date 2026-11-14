# Orkiestrator-AI — a "project lead" for AI coding agents

*Polska wersja: [README.pl.md](README.pl.md).*

Orkiestrator-AI is a set of instructions, role definitions and small Python tools that turn an AI coding assistant
(**Claude Code** or **OpenAI Codex**) into a *project lead* (Polish: *kierownik*). The lead plans a project in
stages, delegates each task to an executor agent working in an isolated Git worktree, has the result checked by an
independent reviewer in a fresh context, merges only verified work, and keeps the whole project state in plain
files in the repository, so a new session can pick up where the last one stopped.

It is not a standalone application or framework. It runs inside Claude Code (`/kierownik`) or Codex (`$kierownik`)
and uses their own subagents and CLIs. This repository also contains an evaluation harness that measures whether
the lead is worth its cost compared with a plain session. The honest answer so far: on the small projects tested,
it is not (see [Evaluation](#evaluation)).

## Why

Long AI-assisted projects tend to fail in predictable ways: the conversation becomes the only record of what was
decided, the context fills up and quality drops, the same model both writes and approves its own code, and
"tests pass" gets reported without anyone running them. The lead addresses these with a few rules:

- **State lives in the repo, not in the chat.** `docs/PROJEKT.md` (what the system is) and `docs/TODO.md` (goal,
  plan, what is in progress, what is verified, next step) are updated after every task. A new thread resumes from
  them.
- **Whoever writes code does not approve it.** Every change gets a review in a fresh context. Depending on risk,
  the reviewer is a model from another family (e.g. Codex reviewing Claude's work) or one capability class above
  the author.
- **Evidence over claims.** Merges run the project's own test command and are undone automatically if it fails.
- **Small, disposable threads.** The lead delegates reading and implementation so its own context stays short.

## How it works

```
 owner ──► /kierownik
             │  reads docs/PROJEKT.md, docs/TODO.md, ~/.kierownik/ZESPOL.md (registry of models/CLIs)
             ▼
        stage plan ──► mode for the stage: compact (fits one session) | full (task by task)
             │
             ├─► executor (kier-wykonawca, Opus by default) ── own Git worktree, branch task/T-NNN
             │        └─ report: commands run → results
             ├─► reviewer (kier-recenzent, fresh context) ── criteria + diff + regression checklist
             │        └─ verdict: ZALICZONE (pass) | DO POPRAWY (fix round) | ZABLOKOWANE (blocked)
             ├─► kier.py merge ── predict conflicts, merge --no-ff, run AGENTS.md tests, push, clean up
             │        └─ red tests → merge undone, task goes back to a fix round
             └─► checkpoint in docs/TODO.md ── the thread can end here without losing anything
```

Main parts:

- **The skill** (`claude/kierownik/SKILL.md`, `codex/skills/kierownik/SKILL.md`): the lead's operating rules.
  The work loop, autonomy limits (what it decides alone and what it asks the owner), routing by model *class*
  (`SZYBKI < STANDARDOWY < MOCNY < NAJMOCNIEJSZY`) and model *family* rather than tool name, verification, context
  and thread handoff, and fallback when a subscription hits its limit.
- **Order templates** (`ZLECENIA.md`): self-contained task orders for the executor, reviewer and analyst/architect.
  Agents never see the lead's conversation.
- **Role definitions**: four Claude Code subagents (`claude/agents/kier-*.md`) and matching Codex roles
  (`codex/skills/kierownik/roles/*.toml`): analyst, executor, reviewer, architect.
- **`kier.py`** (one file, Python standard library only, byte-identical in both packages): the deterministic Git
  mechanics. Subcommands: `env`, `worktree`, `ro-check`, `merge`, `cleanup`, `fix-round`, `sync`, `test`.
  - It refuses rather than guesses: it never force-pushes, deletes unmerged work or rewrites pushed history.
  - It checks that a merge would not overwrite ignored local files.
  - It predicts conflicts with `git merge-tree` before touching the working tree.
  - It reports through short `KEY: value` lines and documented exit codes, e.g. 1 = tests red and the merge was
    undone, 4 = conflict, 5 = push failed.
- **Model registry** (`~/.kierownik/ZESPOL.md`, one per machine, shared by both hosts): which providers and
  models are available, their class and current state (e.g. "out of quota until Friday"). A new or exhausted
  subscription changes only the registry, not the rules.
- **Two stage modes:**
  - *Compact* — added after the evaluations: for a stage that fits one executor session and needs no design
    decision. One executor implements all tasks (one commit per task), then one review of the whole stage runs in
    the strongest class.
  - *Full* — task by task, up to four executors in parallel, with a conflict procedure.
- **Installer** (`install.py`): installs and upgrades both packages. It recognises files from earlier releases by
  checksum (`install-history.json`), asks before replacing files the user edited, backs up everything it
  overwrites and verifies the result byte for byte.

## Repository layout

```
README.md, README.pl.md   this file (English) and the original Polish overview
install.py                installer/updater for both packages (+ install-history.json)
claude/                   Claude Code package: skill (kierownik/), subagents (agents/), design notes (ANALIZA.md)
codex/                    Codex package: skill, roles, installer, CLI adapter (run_agent.py), tests, port notes
evals/                    evaluation harness: test projects, hidden acceptance tests, probes, scoring, results
tests/                    tests of the installer, kier.py, package consistency and the eval harness
archiwum/                 earlier prompt versions (v6, v7, SDD), kept for comparison
.github/workflows/        CI
```

Most of the documentation and all owner-facing text is in **Polish**: the tool was built for a Polish-speaking
owner. Instructions addressed to models are in English to save tokens.

## Technology

- **Python, standard library only**, no dependencies: 3.9+ for the Claude part (installer, `kier.py`; the macOS
  system `python3` is enough), 3.11+ for the Codex part and the eval harness (they need `tomllib`).
- **Git ≥ 2.38** for conflict prediction (`git merge-tree --write-tree`). Older versions degrade to a plain merge
  attempt.
- **Claude Code** (skills, subagents with `isolation: worktree`; optional features need ≥ 2.1.221 and ≥ 2.1.292)
  and/or **Codex CLI**. Other CLIs (e.g. Google Antigravity) can be registered as extra runners.
- **GitHub Actions**: Linux, Windows and macOS × Python 3.11 and 3.13, plus the Claude part on the macOS system
  Python (3.9).

## Tests and CI

```bash
python3 -m unittest discover -s tests        # 73 tests: installer, kier.py, consistency, eval harness
python3 -m unittest discover -s codex/tests  # 22 tests: Codex installer and CLI adapter
```

- `tests/test_kier.py` drives `kier.py` against real temporary Git repositories. It covers worktree creation,
  merges with green and red tests (red merges are undone), conflict prediction, protection of ignored files and
  cleanup.
- `tests/test_install.py` covers fresh installs, upgrades from earlier releases, user-edited files, backups,
  removal of obsolete files and CRLF checkouts.
- `tests/test_spojnosc.py` keeps the Claude and Codex packages in step. It checks that shared files are identical,
  that protocol words, order fields and owner shortcuts appear in both, that every `kier.py` subcommand the prompts
  name exists, and that `SKILL.md` stays within its length limit.
- `tests/test_evals.py` checks the evaluation kit itself: an untouched test project fails every hidden test, the
  reference solution passes all of them, and the scoring and summary scripts work.

CI runs both suites on every pull request and every push to `main`.

## Evaluation

The question was whether the lead produces better results than a plain session, and at what cost. The harness is
in `evals/` (method and full write-up in Polish: [evals/README.md](evals/README.md); raw results:
[evals/WYNIKI.md](evals/WYNIKI.md), `evals/wyniki/*.json`).

**Method.**
- **Test projects:** each configuration gets the same small Python CLI project and an accepted stage plan.
- **Hidden acceptance tests:** the agents never see them; one test file per task.
- **Probes:** extra checks for defects that no task criterion mentions, such as file permissions after an atomic
  save, writing through a symlink, control characters in input, or performance on 20,000 records. Probes are
  reported separately from the task score.
- **Runs:** headless `claude -p` in a cloud container, with Claude Opus as the main model.
- **Cost:** API list price as reported by the CLI (`total_cost_usd`).

Configurations:
- **A** — plain session, no lead;
- **B** — lead, full mode, Opus executor;
- **D** — lead, full mode, Sonnet executor;
- **E** — lead, chooses its own mode (it chose compact).

The test sets:
- **Set 2:** 12 tasks with traps — a cross-cutting change, Unicode and date edge cases, two security tasks, a
  criterion that contradicts the existing tests, and four "independent" tasks that touch the same code.
- **Set 3:** 12 tasks across three stages, each run in a separate session. One session is killed mid-stage and a
  decision taken in an earlier stage must carry over.

| Set | Config | Runs | Tasks passed | Probes (avg) | Time (avg) | Cost (avg) |
|---|---|---|---|---|---|---|
| 2 | A — plain session | 2 | 12/12 | 3.5 / 6 | 6.9 min | $2.1 |
| 2 | B — lead, full mode, Opus executor | 2 | 12/12 | 4.5 / 6 | 19.1 min | $14.2 |
| 2 | D — lead, full mode, Sonnet executor | 2 | 12/12 | 3.0 / 6 | 17.9 min | $12.0 |
| 2 | E — lead, compact mode | 2 | 12/12 | 5.0 / 6 | 19.6 min | $4.9 |
| 3 | A — plain sessions (4 per run) | 2 | 12/12 | 6 / 6 | 11.1 min | $3.0* |
| 3 | E — lead (reviews on Claude Fable) | 2 | 12/12 | 6 / 6 | 35.8 min | $11.8* |

\* Excludes the cost of a killed session when the killed process could not report it, so A is understated.

**What the results say.**
- **Measured quality is the same.** Every configuration passed every hidden acceptance test in both sets. None
  weakened or rewrote existing tests. In set 2, every run flagged the contradictory criterion instead of silently
  working around it.
- **The lead is the slower and more expensive option.** In set 2, full mode cost about 6× a plain session; compact
  mode cost about a third of full mode (with an Opus reviewer). In set 3, the lead cost about 4× a plain session.
- **Plain sessions recovered across sessions.** After the interruption in set 3 they picked up the state from the
  code and Git history; the lead's resume procedure also worked.
- **Review catches some defects beyond the criteria, but only the kinds it is told to look for.**
  - With the regression checklist, compact mode passed all four probes in the categories the checklist names;
    plain sessions missed some of them.
  - No configuration caught the control-character probe, a category outside the list.
- **Opus vs Sonnet as executor:** Sonnet was only ~15% cheaper overall (most cost is the Opus lead and reviewers),
  with more fix rounds. The executor stays on Opus.

**Limitations.** 1–2 runs per configuration. Small projects (about 470–700 lines of code). Claude models only:
the Codex-as-reviewer configuration was not run. Costs are estimates at list price. The scenario the lead was
designed for has not been measured: a project too large to read in one session, with decisions that are not
visible in the code and several providers.

## Getting started

Requirements: Git, Claude Code and/or Codex, and Python 3.9+ (Claude Code) or 3.11+ (Codex).

```bash
git clone https://github.com/sygnatura/Orkiestrator-AI.git   # or download the ZIP
cd Orkiestrator-AI
python3 install.py --dry-run   # show the plan, change nothing
python3 install.py             # install or upgrade (Windows: py install.py)
```

Then open a session **in the project you want to run** and type `/kierownik` (Claude Code) or `$kierownik`
(Codex). On first start the lead sets up the model registry and asks a few questions. On an existing repository it
maps the project into `docs/PROJEKT.md` and `docs/TODO.md` and proposes a plan. Owner shortcuts while it works:
- `status`, `dalej` (continue), `stop`;
- `pomysł:` (idea), `zmiana:` (change of plan), `zespół:` (models or limits changed);
- `tryb: zwarty|pełny` (compact or full mode).

Per-host details: [claude/README.md](claude/README.md), [codex/README.md](codex/README.md) (Polish).

## Roadmap

Not done yet, in rough order of value:

1. **Evaluate where the lead should pay off:** a larger, longer project (beyond what one session can read) and the
   Codex-as-reviewer configuration on the owner's machine.
2. **Registry and routing in code** (`kier.py zespol/route/limit`) instead of rules in the prompt.
3. **Pull-request mode:** work through PRs and CI instead of merging to a local `main`.
4. **An English version of the owner-facing documentation.**

## How this was built with AI

This is a project about working with AI, built with AI. The author (Sebastian Jaśkiewicz) defined the goals,
used the tool on his own projects, reported problems and decided on direction and trade-offs. Most of the text and
code was written with Claude Code. Codex (another model family) reviewed the changes in several rounds. Its
blocking findings, mostly Git edge cases in `kier.py`, were fixed with regression tests that fail on the old code.
The evaluation harness and its conclusions were checked by an independent reviewer model before and after the
runs, which found and corrected a hidden test stricter than its criterion and several overstated numbers. The
design decisions and the reasons behind them are recorded in [claude/ANALIZA.md](claude/ANALIZA.md) (Polish).

## License

[MIT](LICENSE).
