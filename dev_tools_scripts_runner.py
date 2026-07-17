"""Entry point only -- all business logic lives in
utils/dev_tools_scripts_runner/. Edit that package, not this file."""

import sys
from utils.dev_tools_scripts_runner import main


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
