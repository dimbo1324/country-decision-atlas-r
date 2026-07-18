# Task: Remove `apps/web-prototype` and its mentions

Owner request: delete `apps/web-prototype` entirely, plus every mention of
it across AI-agent settings and documentation. Branch `chore/remove-web-prototype`
off up-to-date `main`.

## Survey (done before editing)

- [+] Confirmed scope via git-tracked file count (61 files) and a
      case-insensitive repo-wide grep for "web-prototype" (excluding
      `node_modules`, `.git`, the file's own directory, `pnpm-lock.yaml`,
      and an unrelated sibling git worktree
      `.claude/worktrees/gallant-dubinsky-f97d5e` which is a separate
      checkout, not part of this repo's tracked tree). Found 9 files with
      real mentions: `pnpm-workspace.yaml`, `.claude/launch.json`,
      `README.md`, `apps/web/src/app/fonts.ts`,
      `apps/web/src/app/[locale]/decision/passports/[token]/page.tsx`,
      `packages/ui/.storybook/main.ts`, `packages/ui/src/tokens/theme.css`,
      and two `docs/_arch_` files. No hits in `.codex/`, `.claude/agents`,
      `.claude/skills`, `AGENTS.md`, `CLAUDE.md`, or `.ai/` — the only
      "AI-agent settings" reference was the `web-prototype` entry in
      `.claude/launch.json`.

## Implementation

- [+] `pnpm-workspace.yaml`: removed the `apps/web-prototype` package
      entry.
- [+] `.claude/launch.json`: removed the `web-prototype` dev-server
      config block. No `.codex` mirror existed for this file, so nothing
      to sync there.
- [+] `README.md`: removed the `apps/web-prototype` row from the
      repository map table.
- [+] `apps/web/src/app/fonts.ts`: reworded a comment that justified a
      font-fallback gap by comparing to `apps/web-prototype`'s behavior —
      now states the gap is an accepted limitation of the upstream font
      families directly, no dangling reference.
- [+] `apps/web/.../decision/passports/[token]/page.tsx`: reworded a
      comment describing `PassportCard.tsx`'s origin as "the
      web-prototype's mockup component" — dropped the historical
      attribution, kept the (still-accurate) description of what's reused
      and what isn't.
- [+] `packages/ui/.storybook/main.ts`: removed a comment sentence citing
      `apps/web-prototype`'s `vite.config.ts` as precedent for the same
      Tailwind Vite plugin registration — the remaining comment already
      explains why the plugin is needed on its own.
- [+] `packages/ui/src/tokens/theme.css`: this one needed a real edit, not
      just deletion — checked `packages/ui/.storybook/preview-head.html`
      first and confirmed Storybook loads the same font families via a
      Google Fonts `<link>`, i.e. Storybook has always been the *other*
      real consumer this comment was describing, `web-prototype` was just
      the named example. Swapped the reference to Storybook; the
      `--ui-font-*` indirection mechanism itself is untouched and its
      rationale still holds.
- [+] `docs/_arch_/01_Продукт/02_Текущее_состояние_системы.md`: removed
      the entire `### 7.4 Визуальный прототип` subsection (nothing in it
      was relevant once the prototype itself is gone) and renumbered
      `7.5 → 7.4` (confirmed no other doc references section numbers by
      digit, and no `### 7.x` sections exist past the old 7.5).
- [+] `docs/_arch_/02_План/01_План_реализации.md`: reworded the visual
      tranche's "prep already done" paragraph — item (1) now describes
      the prototype in past tense (served as a style/element donor, fully
      ported into `packages/ui` by the redesign waves, then removed)
      instead of pointing at a directory that no longer exists.
      Deliberately left item (2)'s existing `../FRONTEND_IMPLEMENTATION_PLAN.md`
      reference alone even though that file doesn't exist either — a
      separate, pre-existing staleness issue unrelated to this task, not
      mixed into this diff.
- [+] `git rm -r apps/web-prototype` — all 61 tracked files removed
      cleanly.
- [+] `pnpm install` to regenerate `pnpm-lock.yaml` for the 4 remaining
      workspace projects (was 5) — confirmed zero `web-prototype`
      references left in the lockfile.

## Verification

- [+] Repo-wide case-insensitive grep for "web-prototype" after all edits:
      only the one intentional historical mention left (in
      `01_План_реализации.md`, describing that it existed and was
      removed — not a dangling live reference).
- [+] `packages/ui` typecheck/lint clean.
- [+] `apps/web` typecheck/lint clean, `next build` clean (same 45
      routes, same worst-case 297 kB, well under the JS budget ceiling).
- [+] `pnpm format:check` clean.
- [+] `packages/ui` `storybook build` compiles clean (confirms the
      `main.ts`/`theme.css` edits didn't break the Storybook config or
      font loading).
- [+] No CI workflow (`.github/workflows/*`) referenced `web-prototype` —
      confirmed via grep, nothing to update there.

## Completion

- [+] Checklist filled (`+`/`-`).
- [+] Commit on `chore/remove-web-prototype`.
- [+] Final report.
