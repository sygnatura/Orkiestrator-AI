# Resuming the v11 lead — Claude ↔ Codex

## Shared sources

PROJEKT (how it works), TODO (goal/plan/state/evidence/next step), DONE, AGENTS, the existing CLAUDE, task files
`docs/tasks/T-NNN.md`, ADR and the real Git. Keep IDs/statuses and approvals. Don't create separate PROJEKT/TODO for
Codex, PLAN.md, PROJECT_WORKFLOW.md or REPORT/REVIEW as a condition of resuming. Keep existing equivalents/SDD with a
mapping, without a mechanical migration. v10 and v11 use the same statuses and files — no migration between them.

Team models/limits are the state of a given skill installation, not of the project. Don't overwrite
`~/.claude/skills/kierownik/ZESPOL.md`, the Claude agents or its settings during a takeover. You may read the explicit
metadata you need, but keep the Codex mapping in your own ZESPOL. Don't import sessions or secrets.

## Recovering the work

Read status/HEAD/branches/worktrees/diff and the current TODO. For the recorded SHAs check existence
(`git cat-file -t`) and integration (`merge-base --is-ancestor`). No ancestry after squash/cherry-pick doesn't prove
the change wasn't integrated: check the recorded target commit/evidence. Don't switch someone else's checkout or reset.

| Zapisany stan | Codex action |
|---|---|
| TODO z zaakceptowanego etapu | Start the executor; don't ask about the plan again |
| W TOKU, żywa sesja Claude lub los nieznany | Establish the fate of the existing order; no duplicate |
| W TOKU, niepełny commit lub niezapisane zmiany | Keep the work, continue this task/directory once authorship is clear |
| W TOKU, zmiana ukończona | Formal acceptance, own tests and a review of this version |
| DO SPRAWDZENIA, brak werdyktu | Collect the running review or start only the missing one |
| DO SPRAWDZENIA, właściwy ZALICZONE dla SHA | Integration and tests of this version; no reimplementation |
| DO POPRAWY jako werdykt | W TOKU, the BLOKUJĄCE remarks on the same branch |
| ZABLOKOWANE | Remove the concrete obstacle or collect the missing decision |
| Merge i pozytywne testy, TODO nieaktualny | Complete the checkpoint from the evidence |
| GOTOWE z dowodem | Keep the result, next task |
| GOTOWE bez dostępnego dowodu | Record the gap and check the area; don't roll back the whole stage |
| Sam merge bez dowodu zintegrowanej wersji | Check this version; don't announce GOTOWE |

Use existing `.claude/worktrees/` only after the previous executor finished and access is checked. Codex doesn't have
to delete them and create new ones. A `task/*` branch can be checked out in only one worktree; a detached reviewer
checkout solves the collision without switching the author's directory. A worktree on another machine isn't moved by
`git push`. A missing SHA/file in the cloud means the artefact is unavailable here, not permission to restart the task.
Recover the available commits, ask only for the missing work.

## Checkpoint and handoff

Update the existing TODO header, not a separate file. Record (in Polish):

```text
Cel / etap / zatwierdzony plan: <ścieżki i źródło decyzji>
Gałąź główna @ pełny SHA / ostatni zweryfikowany: <wersja + dowód>
W toku: <ID, status v10, gałąź, baza, ostatni commit, katalog/maszyna>
Lokalne zmiany: <autor/obszary/staging, bez sekretów>
Wykonawca: <narzędzie, faktyczny model/klasa, ID/los sesji, zlecenie/runda>
Recenzja: <oceniony SHA, świeży kontekst, werdykt, dowody, odstępstwa>
Integracja: <wersja, testy/scenariusz; czy stan/push wykonany>
Blokady / pytania / środowisko: <warunek i brakujące dane>
Ustalenia: <proces, mapowanie, zgody z odnośnikami, bez wartości sekretów>
Następny krok: <jedno konkretne działanie, task, rola, oczekiwany dowód>
```

Move important results into TODO/task files, because `.kierownik/` is local and ignored. Don't write a commit's own
SHA into that commit: give the checkpoint ID after the commit. Only a confirmed push makes commits available from
another machine.

Start prompt: `$kierownik Wznów z PROJEKT.md i TODO.md; zachowaj aktywne zlecenia i kontynuuj zapisany następny krok.`
Back in Claude, its `/kierownik` with the same files is enough. Recorded facts don't replace current permissions or an
acceptance left only in a chat.
