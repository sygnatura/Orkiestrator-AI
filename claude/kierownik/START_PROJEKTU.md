# START_PROJEKTU — taking over an existing project / starting a new one

Read by the lead (SKILL.md, section 1, step 3) when the project lacks `docs/PROJEKT.md` + `docs/TODO.md`.
Everything written for the owner and into project files is in Polish (SKILL.md, LANGUAGE).

## Takeover (goal: understand the project without asking the owner about what is in the repo)

1. Delete or rebuild nothing. Existing plan documents (ROADMAP, notes, checklists) are a source — move their
   content with a link, don't delete the originals. Keep the existing Git process and conventions.
2. Run 3 `kier-analityk` subagents in parallel (big repository → class MOCNY), each with a result of ≤ 60 lines,
   no code quotes; tell them why (you are building PROJEKT.md for future sessions):
   a. Goal and structure: what the program does and for whom (from README, code, UI/CLI), modules and their
      role, data flow from input to result, stack and versions.
   b. Running and tests: install, run, test and lint commands (from manifests, CI, scripts); which services are
      needed; what the tests call externally.
   c. Environment and costs: which LLMs/APIs the app and the tests call (local or paid, where configured),
      databases (test or real), sending, payments, secrets (variable names only, never values); state of the
      documentation and plans (what was declared done).
3. Write `docs/PROJEKT.md` (template in SZABLONY.md) from the results. Mark unknowns `[?]`.
4. Establish the actual state: run the tests (TEST RUNS, SKILL.md section 5) if point c shows they are safe; if
   they touch paid or real resources — ask. Record the result as the baseline in TODO.md.
5. Create or fix `AGENTS.md` and `CLAUDE.md` per SZABLONY.md (keep valuable content of existing files, remove
   duplicates and project state). Propose `.claude/settings.json` (SZABLONY.md, section 8): the list of allowed
   commands, if permissions would block the loop, and `worktree.baseRef: head`, so subagent worktrees start from
   your HEAD.
6. Plan: order from `kier-architekt` the stages to the goal and the first stage broken into small tasks with
   criteria, based on PROJEKT.md, the test result and existing tasks. Write it into a draft `docs/TODO.md`.
   Give the plan of a big or risky project to a second, fresh `kier-architekt` in class MOCNY for review
   (`model` parameter at the call; order C, question „recenzja planu”).
7. One message to the owner: a short picture of the project (5–8 lines), goal / MVP / what we don't do with
   your proposals, the first stage plan, questions with recommended answers.
   After acceptance: commit `docs(kierownik): przejęcie projektu` and start the loop.

## New project

1. At most 5 questions (goal, user, smallest useful version, constraints and costs, technology preferences),
   each with a proposed default answer.
2. `docs/PROJEKT.md` with the goal, MVP, „czego nie robimy” and the KEY ASSUMPTION (without which the project
   makes no sense, e.g. that the data can be fetched) + plan: stack with justification (ADR-0001), stages.
   The plan is prepared by `kier-architekt`; for a larger project a second, fresh `kier-architekt` in class MOCNY
   reviews it (order C, „recenzja planu”).
3. First stage = the thinnest end-to-end flow on real data that tests the key assumption. A working skeleton
   without a real function does not close the stage.
4. After the owner's acceptance: `git init -b main` (if there is no repository), scaffolding (structure,
   README.md, AGENTS.md, CLAUDE.md, .gitignore, .env.example, formatter, linter, one smoke test), first commit;
   the owner adds a remote if they want one. CI and other infrastructure are added when they become necessary.
