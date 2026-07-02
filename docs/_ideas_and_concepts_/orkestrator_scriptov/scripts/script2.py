from __future__ import annotations

import random


def main() -> int:
    number_a = random.randint(1, 100)
    number_b = random.randint(1, 100)
    result = number_a + number_b

    print(f"First random number:  {number_a}")
    print(f"Second random number: {number_b}")
    print(f"Sum:                  {result}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
