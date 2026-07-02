from __future__ import annotations

import platform
import sys
from datetime import datetime


def main() -> int:
    print("Script 3 demo")
    print(f"Current time:   {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Python version: {platform.python_version()}")
    print(f"Python path:    {sys.executable}")
    print(f"OS:             {platform.platform()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
