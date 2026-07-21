# Project Progress Tracking

Purpose: any assistant, in any session, with any model, can locate exactly
where the project is and where it is going — from files, not from memory.

## Where the truth lives

| Question | File |
|---|---|
| How do we work (process, gates, layers) | `docs/operations/working-standard.md` |
| What is built and how it is shaped | `docs/architecture/overview.md` |
| What is planned, in what order, what is DONE | `docs/product/roadmap.md` |
| What must never break | `docs/architecture/invariants.md` |
| Owner decisions and open questions | `docs/decisions/open-questions.md` |
| What the current/last task was | `task-checklist.md` (repo root) |
| What actually happened recently | `git log --oneline -10` |

## Orientation ritual — at the start of every task

1. `git status --short --branch` and `git log --oneline -10`.
2. Read the episode table in `roadmap.md` §1 and the `**Status.**`
   lines under each episode: episodes with a Status line are done; the first
   episode without one is next.
3. Read `task-checklist.md` to see what the previous task was and whether it
   finished cleanly.
4. Only then plan the new task.

## Update duties — when finishing work

- Completed an episode (or a significant slice): add/refresh the
  `**Status.**` line under that episode in `docs/product/roadmap.md`
  (what shipped: migration numbers, key modules, endpoints).
- Changed the system's shape (new domain, new service package, new
  operational job): update `docs/architecture/overview.md` in the
  matching section.
- Made or received an owner decision that constrains the future: it belongs
  in `docs/decisions/open-questions.md` / the plan header, not only in the chat.
- The episode order is binding: 1→2→3→4→5→6→7, then the visual tranche,
  then the integration tranche. Do not start a later episode before its
  dependencies without an explicit owner decision.

## Drift guard

If the plan, the current-state doc, and the code disagree, the code is the
fact, the plan is the intent — reconcile them in the same task or report the
mismatch explicitly. Never let the docs silently rot: stale docs are worse
than no docs.
