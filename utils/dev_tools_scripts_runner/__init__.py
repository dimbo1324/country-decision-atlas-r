"""Dev-tools script orchestrator: business logic and infrastructure for
`dev_tools_scripts_runner.py` (the thin entry-point shim at the project
root, which never changes beyond importing and calling `main` from here).

Module map:
  models.py          Text/Category/ScriptInfo/Session -- pure data
  exceptions.py       RunnerError/ConfigValidationError/ScriptNotFoundError
  config_loader.py    ConfigLoader -- reads+validates config/*.json
  registry.py         ScriptRegistry -- queryable, read-only script catalog
  execution.py        ScriptRunner -- subprocess launch + arg prompting
  rendering.py        MenuRenderer -- all print_* output
  interactive.py       InteractiveShell -- the REPL loop
  main.py              CliApp + main(argv) -- argv dispatch, ties it together
  config/*.json        the hand-editable catalog (categories, cadences,
                        scripts, defaults) -- the actual data this whole
                        package operates on
"""

from __future__ import annotations

from .main import CliApp, main


__all__ = ["CliApp", "main"]
