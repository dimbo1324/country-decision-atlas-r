# Task: Stage 13 stream 5 — i18n key-parity script

Source: `task-checklist.md` handoff note from the Stage 13 polish stage —
"Написать скрипт сверки ключей `apps/web/src/messages/en.json` и
`ru.json` (падать при расхождении), подключить в quick-гейт."
Branch: `feat/frontend-stage13-i18n-parity` (fresh off `main`).

## Preparation

- [+] Confirmed `apps/web/src/messages/en.json` and `ru.json` are both
      currently in sync (same nested key set) — the script's baseline
      test case is "no diff, exit 0", not "immediately fails."
- [+] Confirmed no existing i18n lint/parity tooling exists anywhere in
      the repo (per Stage 13 Preparation research).
- [+] Read `scripts/dev_tools/sync_agents_md.py` as the house style
      reference for a standalone `dev_tools` script: `main(argv) -> int`,
      `--check` flag convention, `raise SystemExit(main())` entry point.
- [+] Read `scripts/dev_tools/full_check.py` Phase 3
      (`phase_static_quality`) to find where to hook the check — ruff/
      mypy/pytest run unconditionally before the `if self.profile ==
      "quick": ... return` branch, so a step placed there runs on every
      profile including quick, matching the ask.

## Design decisions

- [+] Script name: `scripts/dev_tools/i18n_parity_check.py`. Recursive
      flat-key diff (dot-path keys, e.g. `auth.loginSubmit`) between the
      two JSON files — reports every key present in one but missing in
      the other, on both sides, not just a boolean pass/fail.
- [+] `--check` is the only mode (no "fix" mode — there's no correct
      auto-generated value for a missing translation, unlike
      `sync-agents`'s regenerate-from-source-of-truth case). Running
      with no flags also runs the check; `--check` is accepted as an
      alias for consistency with `sync-agents` and CI clarity.
- [+] Registered in `dev_tools_scripts_runner.py`'s script registry
      (`ScriptInfo`) as `i18n-parity` so it's discoverable/runnable
      standalone, matching every other dev-tools script. **Placed at the
      end of `AVAILABLE_SCRIPTS`, not alongside `format-code`/
      `ship-main`** — an existing test
      (`test_interactive_help_browser_shows_manual_by_global_number`)
      hardcodes the interactive menu's global position of `ship-main`
      (types "3" expecting it), and inserting a new entry earlier in the
      list silently shifted that number and broke the test. Appending at
      the end preserves every existing script's position; fixed by
      moving the registration, not by touching the test.
- [+] Wired into `full_check.py` Phase 3 as an unconditional
      `run_gate_step`, right after `mypy` — runs on every profile
      (quick/backend/frontend/full/ci), not just quick, since it's a
      cheap, fast, pure-Python check with no reason to gate it further.

## Implementation

- [+] `scripts/dev_tools/i18n_parity_check.py` — recursive dot-path key
      diff between `en.json`/`ru.json`, exit 0 on match, exit 1 with a
      full listing of one-sided keys on mismatch, exit 2 on missing/
      malformed file.
- [+] Registered in `dev_tools_scripts_runner.py` as `i18n-parity`
      (aliases `i18n`, `messages-parity`), category `quality`.
- [+] Wired into `scripts/dev_tools/full_check.py` Phase 3, runs on
      every profile.
- [+] Verified: temporarily added an orphan key to `en.json`, confirmed
      exit 1 with a readable "Keys in en.json but missing from ru.json"
      listing; reverted (`git checkout --`), confirmed exit 0 again on
      the real files.
- [+] Found and fixed a real regression during verification, not by the
      task's ask: the first registration placement broke
      `test_interactive_help_browser_shows_manual_by_global_number` (see
      Design decisions) — caught by running the full pytest suite, not
      by typecheck/lint, both of which stayed green throughout.

## Verification

- [+] `python dev_tools_scripts_runner.py i18n-parity` — clean run
      ("i18n key parity OK: 59 keys match in en.json and ru.json.").
- [+] `python dev_tools_scripts_runner.py --profile quick` — includes
      the new step (`[OK] i18n key parity`), full gate clean except the
      pre-existing `arabic_reshaper` venv gap (`pytest
      (scripts/synthetic_data)`), same known baseline issue as every
      prior stage, not a regression.
- [+] `python -m mypy scripts dev_tools_scripts_runner.py` — clean.
- [+] `python -m ruff check` / `ruff format --check` on all 3 touched
      files — clean.
- [+] Full `pytest` suite (root `tests/`) — all passing, including the
      regression test that the placement fix restored.

## Completion

- [+] Commit(s)
- [ ] Merge to `main`, push — only once explicitly confirmed complete.
- [+] Final report — given in the chat response accompanying this
      checklist update.
