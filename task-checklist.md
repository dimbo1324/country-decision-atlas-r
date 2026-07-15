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
      standalone, matching every other dev-tools script.
- [+] Wired into `full_check.py` Phase 3 as an unconditional
      `run_gate_step`, right after `mypy` — runs on every profile
      (quick/backend/frontend/full/ci), not just quick, since it's a
      cheap, fast, pure-Python check with no reason to gate it further.

## Implementation

- [ ] `scripts/dev_tools/i18n_parity_check.py`
- [ ] Register in `dev_tools_scripts_runner.py`
- [ ] Wire into `scripts/dev_tools/full_check.py` Phase 3
- [ ] Verify: intentionally break parity, confirm non-zero exit +
      readable diff; restore, confirm exit 0.

## Verification

- [ ] `python dev_tools_scripts_runner.py i18n-parity` — clean run.
- [ ] `python dev_tools_scripts_runner.py --profile quick` — includes
      the new step, passes.
- [ ] `python -m mypy scripts` / `python -m ruff check scripts` clean
      on the new script.

## Completion

- [ ] Commit(s)
- [ ] Merge to `main`, push — only once explicitly confirmed complete.
- [ ] Final report
