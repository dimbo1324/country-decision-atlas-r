# Developer Tools

Use `dev_tools_scripts_runner.py` from the repository root as the main entry
point.

## Common Commands

Format all supported code:

```powershell
python dev_tools_scripts_runner.py format-code
```

Run the fast local gate:

```powershell
python dev_tools_scripts_runner.py --profile quick
```

Run diagnostics only:

```powershell
python dev_tools_scripts_runner.py --doctor
```

Format, commit, verify, pull, and push `main`:

```powershell
python dev_tools_scripts_runner.py ship-main --message "type: explain the change"
```

## Scripts

- `full_check.py` — local quality gate and diagnostics.
- `format_code.py` — Ruff, Prettier, and gofmt formatting.
- `ship_main.py` — guided commit and push workflow for explicit main releases.

`ship_main.py` refuses to run outside `main`, runs the quick quality gate by
default, uses `git pull --ff-only origin main`, and stops on the first failing
step. After its own quick gate passes, it pushes with `--no-verify` to avoid
running the same pre-push gate twice. Direct `git push origin main` remains
protected by the pre-push hook.
